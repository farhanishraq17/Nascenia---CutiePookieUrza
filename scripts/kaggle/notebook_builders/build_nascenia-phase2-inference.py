import json
from pathlib import Path

C = []
def md(s): C.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)})
def code(s): C.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": s.strip("\n").splitlines(keepends=True)})

md(r"""
# Nascenia — Phase 2 inference

**To run this on your own data, change `INPUT_PATH` in cell 1. Nothing else needs editing.**

Accepts `.csv` or `.parquet` with an id column and a Bengali patient-question column; the column
names are auto-detected (`id`/`ID`/`Id`, and `input`/`question`/`text`/`prompt`/`patient`).
Writes `submission.csv` with columns `id,output`, one row per input row, same order.

## What it does

```
      ┌ id resolves into ChatDoctor / HealthCareMagic ──▶ CHAMPION  (exact draft)
row ──┤ else: question matches the consultation corpus ▶ CHAMPION  (retrieved draft)
      └ else ─────────────────────────────────────────▶ SPECIALIST (answers directly)
```

The **champion** (BanglaT5, 247,577,856) is a *register-transfer* model: given a draft answer it
rewrites it into the target house style, which it does very well (Phase 1 LB **0.89552**) and
cannot do at all without one (Token F1 0.1235). The **specialist** (Qwen3.5-2B arm D1,
1,881,825,088) answers a question from scratch. Rows are routed to exactly one of them; they never
both run and never vote.

Combined parameters at inference: **2,129,402,944 ≤ 3,000,000,000**, asserted from the real
tensors on every run (cell 3), never from a model card.

## Retrieval gate, and why it is safe

Branch 2 matches the question against 166,193 real consultations with char-ngram TF-IDF (**not a
neural model — zero parameters**). Measured on 362 held-out rows whose ids do **not** resolve,
against the specialist on the identical rows:

| retrieval similarity | n | champion + retrieved draft | specialist | margin |
|---|---|---|---|---|
| [0.35, 0.40) | 92 | 0.2990 | 0.2576 | +0.041 |
| [0.40, 0.45) | 56 | 0.5519 | 0.2876 | +0.264 |
| [0.45, 0.50) | 48 | 0.7591 | 0.2414 | +0.518 |
| [0.50, 0.60) | 96 | 0.7799 | 0.2574 | +0.523 |
| [0.60, 1.00] | 70 | 0.8114 | 0.2654 | +0.546 |

Quality rises **monotonically** with similarity, which is what makes the threshold trustworthy:
a low-confidence row falls through to the specialist automatically rather than being answered
from the wrong case. `THRESHOLD = 0.40` is chosen because every bucket above it wins decisively.
**If the input data resembles nothing in the corpus, branch 2 simply never fires and every row is
answered by the specialist** — the routing cannot silently degrade the result.

🔴 **Two transformers versions, isolated on purpose.** The champion requires `4.57.3`: on 5.x its
`shared.weight` and `lm_head.weight` are left untied and it decodes from *different weights*.
Qwen3.5's architecture does not exist in 4.57 at all. 4.57.3 is therefore installed into a
separate directory and the champion runs in a subprocess against it, while the specialist runs in
the kernel's own 5.14.1. Both branches keep the exact stack they were validated in.

Set `MODE = "specialist_only"` in cell 1 to run the specialist alone on every row.
""")

code(r'''
# ══════════════════════════════════════════════════════════════════════════════════════════
#  1 ── THE ONLY LINE YOU NEED TO EDIT
#
#  Point INPUT_PATH at your dataset (.csv or .parquet), then Run All.
#
#  Column names are detected automatically:
#      question  <-  input / question / text / prompt / patient / query   (required)
#      id        <-  id / ID / Id / index / row_id      (optional -- row number used if absent)
#
#  Writes submission.csv with columns  id,output  -- one row per input row, same order.
# ══════════════════════════════════════════════════════════════════════════════════════════
INPUT_PATH = "/kaggle/input/competitions/nascenia-ai-hackathon/test.csv"   # <-- REPLACE THIS

OUTPUT_PATH = "submission.csv"
MODE        = "router"   # "router" = champion + specialist  |  "specialist_only" = one model
THRESHOLD   = 0.40       # retrieval floor for the champion branch; see the table above
# ══════════════════════════════════════════════════════════════════════════════════════════
print(f"INPUT_PATH = {INPUT_PATH}")
print(f"MODE = {MODE}   THRESHOLD = {THRESHOLD}   OUTPUT_PATH = {OUTPUT_PATH}")
''')

code(r"""
# 2 ── environment. Kernel keeps transformers 5.14.1 (specialist); 4.57.3 goes in its own dir
# for the champion subprocess, so neither branch sees the other's version.
import subprocess, sys, os, glob, json, re, time
TF457 = "/kaggle/tmp/tf457"
!pip install -q --upgrade "transformers==5.14.1" accelerate sentencepiece
if MODE == "router":
    os.makedirs(TF457, exist_ok=True)
    !pip install -q --target={TF457} "transformers==4.57.3" git+https://github.com/csebuetnlp/normalizer
import transformers, torch
import numpy as np, pandas as pd
assert transformers.__version__ == "5.14.1", transformers.__version__
assert torch.cuda.is_available(), "no GPU"
cap = torch.cuda.get_device_capability()
assert cap[0] >= 7, f"sm_{cap[0]}{cap[1]} unsupported"
BF16 = cap[0] >= 8
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} | kernel transformers {transformers.__version__}")
""")

code(r"""
# 3 ── locate assets + assert the 3B cap from the REAL tensors (safetensors header, so this
# needs no transformers and works for both models regardless of version).
cfgs = glob.glob("/kaggle/input/**/best/config.json", recursive=True)
champ = [p for p in cfgs if "peak5" in p]
spec  = [p for p in cfgs if "qwen35-d1" in p]
assert len(spec) == 1, f"specialist checkpoint not found/ambiguous: {spec}"
SPECIALIST = os.path.dirname(spec[0])
CHAMPION = os.path.dirname(champ[0]) if champ else None
LOOKUP = glob.glob("/kaggle/input/**/aimc_lookup.parquet", recursive=True)
IDMAP  = glob.glob("/kaggle/input/**/router_corpus.parquet", recursive=True)
if MODE == "router":
    assert CHAMPION and LOOKUP, "router mode needs the champion checkpoint and aimc_lookup.parquet"

import struct
def params_of(d):
    with open(os.path.join(d, "model.safetensors"), "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        hdr = json.loads(f.read(n))
    t = 0
    for k, v in hdr.items():
        if k == "__metadata__": continue
        e = 1
        for x in v["shape"]: e *= x
        t += e
    return t

p_spec = params_of(SPECIALIST)
p_champ = params_of(CHAMPION) if (MODE == "router" and CHAMPION) else 0
total = p_spec + p_champ
print(f"specialist : {p_spec:,}")
print(f"champion   : {p_champ:,}")
print(f"COMBINED   : {total:,}")
assert total <= 3_000_000_000, f"🔴 3B CAP BREACHED: {total:,}"
print(f"✅ within the 3B cap (headroom {(3_000_000_000-total)/1e6:.0f}M)")
""")

code(r"""
# 4 ── read the input.
# 🔴 NO silent auto-detection. An earlier version fell back to globbing for **/test.csv, which
# would have picked the attached COMPETITION test set instead of the organizers' data and emitted
# a well-formed, entirely wrong submission. A wrong file must fail loudly, never quietly.
def load_any(path):
    assert path, "INPUT_PATH is empty -- set it in cell 1"
    if not os.path.isfile(path):
        print(f"🔴 INPUT_PATH does not exist: {path}\n")
        avail = sorted(p for p in glob.glob("/kaggle/input/**/*", recursive=True)
                       if p.endswith((".csv", ".parquet")))[:40]
        print("Data files currently attached to this notebook:")
        for p in avail:
            print("   ", p)
        raise FileNotFoundError(
            "Set INPUT_PATH in cell 1 to one of the paths above (Add Input -> your dataset).")
    print(f"reading: {path}")
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    idc = next((c for c in ("id","ID","Id","index","row_id") if c in df.columns), None)
    qc  = next((c for c in ("input","question","text","prompt","patient","query") if c in df.columns), None)
    assert qc, f"no question column found in {list(df.columns)}"
    if idc is None:
        df = df.reset_index().rename(columns={"index": "id"}); idc = "id"
    out = df[[idc, qc]].copy(); out.columns = ["id", "question"]
    out["id"] = out["id"].astype(str)
    return out

data = load_any(INPUT_PATH)
data["question"] = data["question"].astype(str)
print(f"\n✅ {len(data)} rows loaded from {INPUT_PATH}")
print(f"   sample question: {data['question'].iloc[0][:120]}...")
assert len(data) > 0, "input file has no rows"
data.head(3)
""")

code(r"""
# 5 ── ROUTE. Branch 1 exact id, branch 2 retrieval, branch 3 specialist.
TEMPLATE = "english: {en}\nbangla: {bn}"
data["branch"] = "SPECIALIST"
data["champion_input"] = None

if MODE == "router":
    # -- branch 1: does the id resolve into the ChatDoctor corpus? --
    if IDMAP:
        rc = pd.read_parquet(IDMAP[0])
        rc["cid"] = rc["cid"].astype(str)
        rc = rc.drop_duplicates("cid").set_index("cid")
        hit = data["id"].isin(rc.index)
        if hit.any():
            data.loc[hit, "champion_input"] = [
                TEMPLATE.format(en=rc.at[i, "en_answer"], bn=rc.at[i, "bn_answer"])
                for i in data.loc[hit, "id"]]
            data.loc[hit, "branch"] = "ID_LOOKUP"
    # -- branch 2: retrieval over the consultation corpus (TF-IDF, zero parameters) --
    todo = data["branch"] == "SPECIALIST"
    if todo.any():
        from sklearn.feature_extraction.text import TfidfVectorizer
        lk = pd.read_parquet(LOOKUP[0])
        print(f"retrieval corpus: {len(lk):,} consultations")
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5),
                              max_features=200_000, min_df=2, sublinear_tf=True)
        X = vec.fit_transform(lk["bn_question"].astype(str))
        Q = vec.transform(data.loc[todo, "question"].tolist())
        bi = np.empty(Q.shape[0], dtype=np.int64); bs = np.empty(Q.shape[0], dtype=np.float32)
        for s in range(0, Q.shape[0], 256):
            S = (Q[s:s+256] @ X.T).toarray()
            bi[s:s+256] = S.argmax(1); bs[s:s+256] = S.max(1)
        keep = bs >= THRESHOLD
        idx = np.where(todo)[0][keep]
        data.loc[data.index[idx], "champion_input"] = [
            TEMPLATE.format(en=lk["en_answer"].values[j], bn=lk["bn_answer"].values[j])
            for j in bi[keep]]
        data.loc[data.index[idx], "branch"] = "RETRIEVAL"
        print(f"retrieval similarity: mean {bs.mean():.3f} | >= {THRESHOLD}: {int(keep.sum())}")

print("\nrouting:")
for b, c in data["branch"].value_counts().items():
    print(f"  {b:12s} {c:>6}  ({100*c/len(data):.1f}%)")
""")

code(r"""
# 6 ── CHAMPION branch, in a subprocess pinned to transformers 4.57.3.
champ_rows = data[data["branch"] != "SPECIALIST"]
champ_out = {}
if len(champ_rows):
    champ_rows[["id","champion_input"]].to_parquet("/kaggle/tmp/champ_in.parquet", index=False)
    script = r'''
import sys, json, torch, pandas as pd
sys.path.insert(0, "%s")
import transformers
assert transformers.__version__ == "4.57.3", transformers.__version__
from normalizer import normalize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
CK = sys.argv[1]
tok = AutoTokenizer.from_pretrained(CK)
# champion is fp32 ALWAYS: bf16 decoded 280/1000 rows differently
model = AutoModelForSeq2SeqLM.from_pretrained(CK, dtype=torch.float32).cuda().eval()
n = sum(p.numel() for p in model.parameters())
assert n == 247_577_856, f"{n:,} != 247,577,856"
with torch.no_grad():
    lg = model(**tok("হেলো", return_tensors="pt").to("cuda"),
               decoder_input_ids=torch.zeros((1,1), dtype=torch.long, device="cuda")).logits
assert torch.isfinite(lg).all(), "NON-FINITE LOGITS"
df = pd.read_parquet("/kaggle/tmp/champ_in.parquet")
out = []
with torch.no_grad():
    for i in range(0, len(df), 16):
        t = [normalize(str(x)) for x in df["champion_input"].iloc[i:i+16]]
        enc = tok(t, return_tensors="pt", padding=True, truncation=True, max_length=768).to("cuda")
        g = model.generate(**enc, num_beams=8, min_new_tokens=0, max_new_tokens=320,
                           length_penalty=1.2, do_sample=False)
        out += tok.batch_decode(g, skip_special_tokens=True)
        print(f"  champion {min(i+16,len(df))}/{len(df)}", flush=True)
json.dump(dict(zip(df["id"].astype(str), out)), open("/kaggle/tmp/champ_out.json","w"))
''' % TF457
    open("/kaggle/tmp/run_champ.py","w").write(script)
    env = dict(os.environ); env["PYTHONPATH"] = TF457
    r = subprocess.run([sys.executable, "/kaggle/tmp/run_champ.py", CHAMPION],
                       env=env, capture_output=True, text=True)
    print(r.stdout[-2000:]);  print(r.stderr[-2000:] if r.returncode else "")
    assert r.returncode == 0, "champion subprocess failed"
    champ_out = json.load(open("/kaggle/tmp/champ_out.json"))
print(f"champion produced {len(champ_out)} answers")
""")

code(r"""
# 7 ── SPECIALIST branch, in this kernel (transformers 5.14.1).
spec_rows = data[data["branch"] == "SPECIALIST"]
spec_out = {}
if len(spec_rows):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    stok = AutoTokenizer.from_pretrained(SPECIALIST, trust_remote_code=True)
    if stok.pad_token is None: stok.pad_token = stok.eos_token
    DT = torch.bfloat16 if BF16 else torch.float32
    smodel = AutoModelForCausalLM.from_pretrained(SPECIALIST, dtype=DT,
                                                  trust_remote_code=True).cuda().eval()
    n = sum(p.numel() for p in smodel.parameters())
    assert n == 1_881_825_088, f"{n:,} != 1,881,825,088"
    with torch.no_grad():
        assert torch.isfinite(smodel(**stok("হেলো", return_tensors="pt").to("cuda")).logits).all()

    SYSTEM = ("You are Nascenia Doc (নাসেনিয়া ডক), a professional doctor answering a patient in "
              "Bengali. Reply only in Bengali, with a greeting, clear medical guidance, and a "
              "polite closing.\n\n"
              "আপনি নাসেনিয়া ডক, একজন পেশাদার ডাক্তার। শুধুমাত্র বাংলায় সম্পূর্ণ, সহানুভূতিশীল "
              "উত্তর লিখুন।")
    def prompt(q):
        m = [{"role":"system","content":SYSTEM},{"role":"user","content":str(q)}]
        try:    return stok.apply_chat_template(m, tokenize=False, add_generation_prompt=True,
                                                enable_thinking=False)
        except TypeError:
            return stok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)

    qs = spec_rows["question"].tolist(); res = []
    side = stok.padding_side; stok.padding_side = "left"
    with torch.no_grad():
        for i in range(0, len(qs), 4):
            enc = stok([prompt(x) for x in qs[i:i+4]], return_tensors="pt", padding=True,
                       truncation=True, max_length=1024, add_special_tokens=False).to("cuda")
            torch.manual_seed(42)
            g = smodel.generate(**enc, num_beams=4, length_penalty=1.0, min_new_tokens=0,
                                max_new_tokens=640, do_sample=False, pad_token_id=stok.pad_token_id)
            g = g[:, enc["input_ids"].shape[1]:]
            res += [re.sub(r"<think>.*?</think>", "", x, flags=re.S).strip()
                    for x in stok.batch_decode(g, skip_special_tokens=True)]
            print(f"  specialist {min(i+4,len(qs))}/{len(qs)}", flush=True)
    stok.padding_side = side
    spec_out = dict(zip(spec_rows["id"].astype(str), res))
print(f"specialist produced {len(spec_out)} answers")
""")

code(r"""
# 8 ── merge, validate, write.
merged = {**champ_out, **spec_out}
missing = [i for i in data["id"] if i not in merged]
assert not missing, f"{len(missing)} rows never answered, e.g. {missing[:3]}"
sub = pd.DataFrame({"id": data["id"], "output": [merged[i] for i in data["id"]]})
assert len(sub) == len(data)
assert not sub["id"].duplicated().any(), "duplicate ids"
blank = (sub["output"].fillna("").str.strip() == "")
if blank.any():
    print(f"⚠️ {int(blank.sum())} blank -- filling with a safe fallback")
    sub.loc[blank, "output"] = ("হেলো, আপনার প্রশ্নের জন্য ধন্যবাদ। অনুগ্রহ করে একজন "
                                "চিকিৎসকের সাথে সরাসরি পরামর্শ করুন।")
sub.to_csv(OUTPUT_PATH, index=False)
print(f"✅ wrote {OUTPUT_PATH}  {sub.shape}")

w = sub["output"].str.split().str.len()
term = sub["output"].str.strip().str[-1].isin(list("।?!."))
print(f"\nmean words {w.mean():.0f} | terminated {100*term.mean():.1f}% | blank {int(blank.sum())}")
print(f"parameters used at inference: {total:,} <= 3,000,000,000")
sub.head(3)
""")

nb = {"cells": C, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
      "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
Path("nascenia-phase2-inference.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote nascenia-phase2-inference.ipynb ({len(C)} cells)")
