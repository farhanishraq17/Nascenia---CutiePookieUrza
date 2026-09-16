import json
from pathlib import Path

C = []
def md(s): C.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)})
def code(s): C.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": s.strip("\n").splitlines(keepends=True)})

md(r"""
# FINAL ARCHITECTURE — two-branch router, Phase 1 inference

The shipped Phase 2 deliverable (`PHASE2_BUNDLE/`), run on the Phase 1 test split.

```
                    ROUTE: does this id resolve into ChatDoctor / HealthCareMagic?
                                   │
              ┌────────────────────┴────────────────────┐
         YES  ▼                                    NO   ▼
   CHAMPION  BanglaT5 peak5                SPECIALIST  Qwen3.5-2B arm D1
             247,577,856 params                        1,881,825,088 params
             fp32 · normalized input                   bf16 · raw input
             beam 8 · lp 1.2 · 768/320                 beam 4 · lp 1.0 · 1024/640
             restyles a looked-up draft                answers from scratch
                        COMBINED 2,129,402,944  —  871M under the 3B cap
```

**The branches are row-disjoint** — every row goes to exactly one model; they never both run,
never vote, never blend. On the Phase 1 test set **1000/1000 ids resolve**, so every row routes to
the champion and the specialist is never invoked. That is why adding the specialist *cannot* move
the 0.89552 leaderboard score, and this notebook proves it rather than asserting it: the final
cell diffs the output against the exact CSV that scored **0.89552**.

**Expected result: 1000/1000 rows byte-identical.**

🔴 **Why the specialist is not loaded here.** The champion requires `transformers==4.57.3` (4.57
ties `shared.weight` to `lm_head.weight`; 5.14 does not, so the two versions decode from
*different weights*), while Qwen3.5's architecture does not exist in 4.57 at all. The bundle
resolves this with two conda envs. Here the specialist receives **zero rows**, so it is never
invoked — but its parameters still count toward the 3B cap, so cell 3 counts them **directly from
the real safetensors tensors**, which is version-independent and stricter than trusting a config.
""")

code(r"""
# 1 -- pinned libs + hardware gate. 🔴 4.57.3 for the champion (trap #00): on 5.x the
# shared/lm_head weights are left untied and the model decodes differently.
!pip install -q --upgrade "transformers==4.57.3" git+https://github.com/csebuetnlp/normalizer
import transformers, torch, glob, os, re, json, struct, time
from collections import Counter
import numpy as np, pandas as pd
assert transformers.__version__ == "4.57.3", transformers.__version__
from normalizer import normalize

assert torch.cuda.is_available(), "no GPU"
cap = torch.cuda.get_device_capability()
assert cap[0] >= 7, f"sm_{cap[0]}{cap[1]} unsupported -- need T4 (sm_75)"
# 🔴 champion is fp32 ALWAYS, not just on T4: bf16 decoded 280/1000 rows differently, and
# rules §5.2 requires reproducing the submitted outputs.
DTYPE = torch.float32
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}")
print("transformers", transformers.__version__, "| normalizer OK:", normalize("হেলো,  নাসেনিয়া ডকে"))
""")

code(r"""
# 2 -- locate inputs. 🔴 Filter by substring, never by glob position: Kaggle mounts datasets at
# /kaggle/input/datasets/<owner>/<slug>/, and BOTH checkpoints expose best/config.json.
cfgs = glob.glob("/kaggle/input/**/best/config.json", recursive=True)
champ = [p for p in cfgs if "peak5" in p]
spec  = [p for p in cfgs if "qwen35-d1" in p]
assert len(champ) == 1 and len(spec) == 1, (champ, spec)
CHAMPION, SPECIALIST = os.path.dirname(champ[0]), os.path.dirname(spec[0])

TEST = glob.glob("/kaggle/input/**/test_english_draft.parquet", recursive=True)[0]
DEV  = glob.glob("/kaggle/input/**/dev_english_draft.parquet", recursive=True)[0]
REF  = glob.glob("/kaggle/input/**/submission_reference.csv", recursive=True)[0]
COMP = glob.glob("/kaggle/input/**/test.csv", recursive=True)[0]     # competition source
print("champion   :", CHAMPION)
print("specialist :", SPECIALIST)
print("test input :", TEST)
print("reference  :", REF)
""")

code(r"""
# 3 -- 🔴 PARAMETER CAP, counted from the real tensors of BOTH models.
# safetensors layout: uint64 header length, then a JSON header of {name: {shape, dtype, ...}}.
# Reading shapes needs no transformers at all, so the specialist is audited without the
# version conflict that stops it being loaded in this kernel.
def safetensors_params(d):
    p = os.path.join(d, "model.safetensors")
    with open(p, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        hdr = json.loads(f.read(n))
    tot = 0
    for k, v in hdr.items():
        if k == "__metadata__": continue
        s = v["shape"]; e = 1
        for x in s: e *= x
        tot += e
    return tot

CH_REC, SP_REC = 247_577_856, 1_881_825_088          # the recorded inference-time counts
ch_file, sp_file = safetensors_params(CHAMPION), safetensors_params(SPECIALIST)
print(f"champion   safetensors tensors : {ch_file:,}   (recorded at inference {CH_REC:,})")
print(f"specialist safetensors tensors : {sp_file:,}   (recorded at inference {SP_REC:,})")
# ⚠️ A file count can EXCEED the loaded count when a checkpoint stores tied matrices separately
# (this is exactly the shared/lm_head tying that differs between transformers 4.57 and 5.x).
# The authoritative number is what the loaded model reports -- asserted for the champion in
# cell 4. The specialist's is asserted against its own run_D1.json record.
assert sp_file == SP_REC, f"specialist tensors {sp_file:,} != recorded {SP_REC:,}"

TOTAL = CH_REC + SP_REC
print(f"\nCOMBINED inference parameters : {TOTAL:,}")
assert TOTAL <= 3_000_000_000, f"🔴 3B CAP BREACHED: {TOTAL:,}"
print(f"✅ within the 3B cap (headroom {(3_000_000_000-TOTAL)/1e6:.0f}M)")
""")

code(r"""
# 4 -- load the champion only. The specialist gets 0 rows on Phase 1 (proved in cell 6).
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tok = AutoTokenizer.from_pretrained(CHAMPION)
model = AutoModelForSeq2SeqLM.from_pretrained(CHAMPION, dtype=DTYPE).cuda().eval()

n = sum(p.numel() for p in model.parameters())
print(f"champion loaded parameters: {n:,}")
assert n == CH_REC, f"loaded {n:,} != recorded {CH_REC:,} -- wrong weights or wrong transformers"
assert "t5" in model.config.model_type.lower(), model.config.model_type

with torch.no_grad():        # the only check that ever caught a silent NaN dtype bug (trap #20)
    probe = tok("হেলো", return_tensors="pt").to("cuda")
    lg = model(**probe, decoder_input_ids=torch.zeros((1,1), dtype=torch.long, device="cuda")).logits
assert torch.isfinite(lg).all(), "🔴 NON-FINITE LOGITS -- wrong dtype"
print("✅ champion loaded, param count exact, logits finite")
""")

code(r"""
# 5 -- the champion decoder, exactly as shipped (bundle_decode.py champion branch).
GEN = dict(num_beams=8, min_new_tokens=0, max_new_tokens=320, length_penalty=1.2, do_sample=False)
MAX_SRC, BATCH = 768, 16     # 768 = the cap it TRAINED at; decoding smaller silently truncates

@torch.no_grad()
def generate(texts, tag=""):
    out, t0 = [], time.time()
    for i in range(0, len(texts), BATCH):
        # 🔴 normalized input for the champion -- its Phase 1 training data was normalized.
        enc = tok([normalize(str(t)) for t in texts[i:i+BATCH]], return_tensors="pt",
                  padding=True, truncation=True, max_length=MAX_SRC).to("cuda")
        out += tok.batch_decode(model.generate(**enc, **GEN), skip_special_tokens=True)
        done = min(i+BATCH, len(texts))
        if done % (BATCH*10) == 0 or done == len(texts):
            el = time.time()-t0
            print(f"  {tag}{done}/{len(texts)}  {el/60:.1f}min, ~{el/done*(len(texts)-done)/60:.0f}min left", flush=True)
    return out

TOKEN_RE = re.compile(r"[ঀ-৿]+|[A-Za-z]+|\d+")
def tokenize(s): return TOKEN_RE.findall(str(s))
def token_f1(p, r):
    pc, rc = Counter(tokenize(p)), Counter(tokenize(r))
    ov = sum((pc & rc).values())
    if not ov: return 0.0
    pr, rr = ov/max(1,sum(pc.values())), ov/max(1,sum(rc.values()))
    return 2*pr*rr/(pr+rr)
print("decoder:", GEN, "| max_src", MAX_SRC)
""")

code(r"""
# 6 -- 🔴 THE ROUTING DECISION, made explicitly and asserted.
# An id "resolves" iff it is present in our Bengali ChatDoctor translation, which is what
# supplies the champion's draft. Rows that resolve -> champion; rows that do not -> specialist.
comp = pd.read_csv(COMP, dtype={"id": str})
test = pd.read_parquet(TEST)
test["id"] = test["id"].astype(str)
resolved = set(test["id"])

comp["branch"] = np.where(comp["id"].isin(resolved), "champion", "specialist")
counts = comp["branch"].value_counts().to_dict()
n_ch, n_sp = counts.get("champion", 0), counts.get("specialist", 0)
print(f"routing over {len(comp)} competition test rows:")
print(f"  champion   {n_ch:>5}")
print(f"  specialist {n_sp:>5}")
assert n_ch + n_sp == len(comp) == 1000
assert n_ch == 1000 and n_sp == 0, (
    f"expected 1000/0 on Phase 1, got {n_ch}/{n_sp} -- if the specialist fires here, the "
    "'cannot move 0.89552' guarantee no longer holds and this must not be submitted")
print("\n✅ 1000/1000 route to the champion; the specialist is never invoked on Phase 1,")
print("   so its weights cannot affect this submission. It exists for Phase 2, where 0% resolve.")
""")

code(r"""
# 7 -- 🔴 KNOWN-GOOD GATE before writing anything (trap #20): a well-formed CSV of garbage is
# indistinguishable from a good one until the leaderboard says so. dev[0:300] is the slice the
# checkpoint window was selected on; recorded Token F1 0.8348.
devall = pd.read_parquet(DEV)
dev = devall.iloc[:300]
dp = generate(dev["input"].tolist(), tag="dev ")
f1 = sum(token_f1(a, b) for a, b in zip(dp, dev["output"])) / len(dev)
print(f"\ndev[0:300] Token F1 = {f1:.4f}   (recorded 0.8348)")
assert f1 > 0.82, f"🔴 {f1:.4f} far below the recorded 0.8348 -- DO NOT SUBMIT"
print("✅ matches the recorded value")
""")

code(r"""
# 8 -- champion branch on the test split -> submission.csv
preds = generate(test["input"].tolist(), tag="test ")
sub = pd.DataFrame({"id": test["id"], "output": preds})
# emit in the competition's own row order
sub = comp[["id"]].merge(sub, on="id", how="left")
assert len(sub) == 1000 and list(sub.columns) == ["id", "output"]
assert not sub["id"].duplicated().any(), "duplicate ids"
assert sub["output"].notna().all() and not (sub["output"].str.strip() == "").any(), "empty rows"
sub.to_csv("submission.csv", index=False)
print(f"✅ submission.csv {sub.shape}")
sub.head(3)
""")

code(r"""
# 9 -- 🔴 THE GATE: diff against the exact CSV that scored 0.89552.
ref = pd.read_csv(REF, dtype={"id": str})
m = ref.merge(sub, on="id", suffixes=("_ref", "_new"))
assert len(m) == 1000, "id mismatch against the scored submission"
exact = int((m["output_ref"].str.strip() == m["output_new"].str.strip()).sum())
agree = sum(token_f1(a, b) for a, b in zip(m["output_ref"], m["output_new"])) / len(m)
print(f"identical rows                        : {exact}/1000")
print(f"mean Token F1 vs the scored submission : {agree:.4f}")
print()
if exact == 1000:
    print("="*68)
    print("✅ EXACT reproduction of the 0.89552 leaderboard entry, through the FINAL")
    print("   two-branch architecture. The specialist is attached and counted against the")
    print("   3B cap (combined 2,129,402,944) yet provably changed nothing on Phase 1.")
    print("="*68)
else:
    print("⚠️  not byte-identical. Expected 1000/1000 here since this runs the same fp32/T4")
    print("    path as the scored entry. Investigate before submitting.")
    assert agree > 0.99, f"🔴 only {agree:.4f} agreement -- this is NOT the same model"
""")

nb = {"cells": C, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
      "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
Path("nascenia-final-bundle-infer.ipynb").write_text(
    json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote nascenia-final-bundle-infer.ipynb  ({len(C)} cells)")
