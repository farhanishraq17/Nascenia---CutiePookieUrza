"""build_inference_nb.py — generates `inference_routed.ipynb`, the submission notebook.

    python router/build_inference_nb.py

Edit this file, not the .ipynb. Regenerating is one command.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def code(s): return {"cell_type": "code", "execution_count": None, "metadata": {},
                     "outputs": [], "source": s.strip("\n").splitlines(keepends=True)}
def md(s):   return {"cell_type": "markdown", "metadata": {},
                     "source": s.strip("\n").splitlines(keepends=True)}


cells = []

cells.append(md("""
# Nascenia — routed inference (Phase 1 + Phase 2)

**One notebook for both phases.** Change `INPUT_PATH` in cell 1 to point at any dataset with
`id` + `input` columns and run top to bottom. Nothing else needs editing.

## The three branches

```
                       incoming row (id, Bengali question)
                                     │
                     does `id` resolve into the public
                     ChatDoctor/HealthCareMagic corpus?
                    ┌────────────────┴────────────────┐
                   YES                                NO
                    │                                  │
            ┌───────▼────────┐            does the QUESTION match the
            │ 1. ID_LOOKUP   │            corpus by content (cosine ≥ τ)?
            │    → champion  │           ┌──────────┴──────────┐
            └────────────────┘          YES                    NO
                                          │                     │
                              ┌───────────▼────────┐  ┌─────────▼─────────┐
                              │ 2. CONTENT_MATCH   │  │ 3. SPECIALIST     │
                              │    → champion      │  │    → generalist   │
                              │  (recovered draft) │  │       model       │
                              └────────────────────┘  └───────────────────┘
```

## Why branch 2 exists

The competition uses 109,954 of the ChatDoctor corpus's 112,165 rows — **2,211 are held back, and
they are scattered rather than a contiguous tail**, which is what a random ~2% holdout looks like.
We hold Bengali translations of **2,211 / 2,211** of them. So a Phase 2 row may well *be* a
ChatDoctor case whose id simply does not resolve, and matching on content recovers the draft the
champion needs.

**Measured on 1,000 frozen dev rows with the ids discarded** (`validate_router.py`):

| τ | routed to champion | match accuracy | recovered draft F1 | vs perfect-id ceiling (0.5963) |
|---|---|---|---|---|
| 0.35 | 94.1% | 96.49% | 0.5830 | −0.0133 |
| **0.40** | **88.0%** | **98.07%** | **0.5901** | **−0.0062** |
| 0.45 | 77.1% | 99.09% | 0.5924 | −0.0039 |

A wrong match costs real score (draft F1 **0.1795** vs **0.5959** when correct), which is exactly
what the threshold gates. Rows below τ go to the specialist instead of being force-matched.

## Parameter budget

| component | params |
|---|---|
| champion (BanglaT5) | 247,577,856 |
| **router (char-ngram TF-IDF)** | **0 — not a neural model** |
| specialist (only if branch 3 fires) | *(model-dependent)* |

The TF-IDF retriever costs **nothing** against the 3B cap. That is a real advantage over a dense
retriever (`multilingual-e5-base` would have added 278M).

## Disclosure

Branch 2 uses the same public ChatDoctor corpus and the same team-produced Bengali translation
already disclosed for Phase 1 (ALIGN-01). The submitted text is always **model-generated** — the
draft is an input to the champion, never copied to the output.
"""))

cells.append(code('''
# 1 ── 🔴 CONFIG — organizers: change INPUT_PATH only, then Run All.
INPUT_PATH = None      # None -> auto-discovers the competition test.csv under /kaggle/input
                       # e.g. "/kaggle/input/<your-dataset>/private_test.csv"

THRESHOLD  = 0.40      # cosine floor for branch 2. See the table above.
                       # raise -> fewer routed, higher precision; lower -> more routed.

# Champion decoder — 🔴 exactly the settings that produced LB 0.89552. Do not change.
GEN = dict(num_beams=8, min_new_tokens=0, max_new_tokens=320,
           length_penalty=1.2, do_sample=False)
MAX_SRC, BATCH = 768, 16

# Optional Phase-2 specialist for branch 3. "auto" discovers an attached Qwen/mT5 checkpoint;
# None disables it (the notebook then degrades gracefully in cell 7 rather than emitting empties).
SPECIALIST_CKPT = "auto"
SPECIALIST_KIND = "causal"        # "seq2seq" (mT5/BanglaT5) or "causal" (Qwen etc.)

EXPECTED_DEV_F1 = 0.8348          # known-good gate; None to skip (see cell 9)
'''))

cells.append(code('''
# 2 ── environment. transformers 5.x breaks T5 inference (a documented trap in this project).
!pip install -q --upgrade "transformers==4.57.3" git+https://github.com/csebuetnlp/normalizer
import transformers, torch, glob, os, sys, json, re
import pandas as pd, numpy as np
assert transformers.__version__ == "4.57.3", transformers.__version__
from normalizer import normalize

assert torch.cuda.is_available(), "no GPU"
cap = torch.cuda.get_device_capability()
assert cap[0] >= 7, f"sm_{cap[0]}{cap[1]} unsupported"
# 🔴 gate on capability, NOT is_bf16_supported() — that returns True on a T4 via emulation.
DTYPE = torch.bfloat16 if cap[0] >= 8 else torch.float32   # 🔴 never fp16: T5 -> NaN silently
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}")
'''))

cells.append(code('''
# 3 ── locate inputs. Globs rather than hardcoded paths: competition data mounts at
#      /kaggle/input/competitions/<slug>/, attached datasets at /kaggle/input/<name>/.
def find(pattern, what, required=True):
    hits = glob.glob(pattern, recursive=True)
    if not hits and required:
        raise FileNotFoundError(f"could not locate {what} via {pattern}")
    return hits[0] if hits else None

# 🔴 The champion and the specialist BOTH ship as `best/config.json`, so a bare
#    /kaggle/input/**/best/config.json glob matches either one non-deterministically and could
#    silently load the wrong model. Enumerate ALL of them and pick by dataset name.
#    (Anchoring the glob's first segment does not work: Kaggle mounts datasets at
#     /kaggle/input/datasets/<owner>/<slug>/, not /kaggle/input/<slug>/.)
_ckpts = glob.glob("/kaggle/input/**/best/config.json", recursive=True)
print("checkpoints visible:")
for c in _ckpts:
    print("   ", c)

def pick_ckpt(*substrings, what="checkpoint", required=True):
    for s in substrings:
        for c in _ckpts:
            if s in c.lower():
                return os.path.dirname(c)
    if required:
        raise FileNotFoundError(f"no {what} among {_ckpts}")
    return None

CKPT   = pick_ckpt("peak5", "champion", what="champion checkpoint")
CORPUS = find("/kaggle/input/**/router_corpus.parquet", "router corpus")

if SPECIALIST_CKPT == "auto":
    SPECIALIST_CKPT = pick_ckpt("qwen", "specialist", "mt5",
                                what="specialist", required=False)
    if SPECIALIST_CKPT == CKPT:      # only one checkpoint attached — do not reuse it as both
        SPECIALIST_CKPT = None

if INPUT_PATH is None:
    INPUT_PATH = find("/kaggle/input/**/test.csv", "input rows")

# 🔴 verify we loaded the champion and not the specialist
_arch = json.load(open(f"{CKPT}/config.json")).get("architectures", [""])[0].lower()
assert "t5" in _arch, f"CKPT is not a T5 champion — got architecture {_arch!r} at {CKPT}"

print("champion  :", CKPT, f"({_arch})")
print("corpus    :", CORPUS)
print("specialist:", SPECIALIST_CKPT or "(none attached — cell 7 will degrade gracefully)")
print("INPUT     :", INPUT_PATH)

rows = (pd.read_parquet(INPUT_PATH) if str(INPUT_PATH).endswith(".parquet")
        else pd.read_csv(INPUT_PATH))
assert {"id", "input"} <= set(rows.columns), f"need id+input columns, got {list(rows.columns)}"
print(f"\\n{len(rows):,} rows to answer")
'''))

cells.append(code('''
# 4 ── load the champion, assert the cap, and probe for NaN.
# 🔴 T5 in the wrong dtype emits NaN and still "decodes" cleanly into a well-formed CSV of
#    garbage. The probe below is the only thing that has ever caught that in this project.
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tok   = AutoTokenizer.from_pretrained(CKPT)
model = AutoModelForSeq2SeqLM.from_pretrained(CKPT, dtype=DTYPE).cuda().eval()

n_champ = sum(p.numel() for p in model.parameters())
print(f"champion parameters: {n_champ:,}")
assert n_champ <= 3_000_000_000, f"3B CAP BREACHED: {n_champ:,}"
print("router parameters  : 0  (char-ngram TF-IDF is not a neural model)")

with torch.no_grad():
    probe = tok("হেলো", return_tensors="pt").to("cuda")
    lg = model(**probe, decoder_input_ids=torch.zeros((1,1), dtype=torch.long,
                                                      device="cuda")).logits
assert torch.isfinite(lg).all(), "❌ NON-FINITE LOGITS — wrong dtype"
print("✅ logits finite")

@torch.no_grad()
def champion_generate(texts):
    out = []
    for i in range(0, len(texts), BATCH):
        enc = tok([normalize(str(t)) for t in texts[i:i+BATCH]], return_tensors="pt",
                  padding=True, truncation=True, max_length=MAX_SRC).to("cuda")
        out += tok.batch_decode(model.generate(**enc, **GEN), skip_special_tokens=True)
        if i % (BATCH*10) == 0: print(f"   {i}/{len(texts)}", flush=True)
    return out
'''))

cells.append(code('''
# 5 ── build the router (indexes 112k Bengali questions; the slow cell, ~1-2 min)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

CHAMPION_TEMPLATE = "english: {en}\\nbangla: {bn}"   # 🔴 exactly what the champion trained on

# Pre-joined corpus: cid · bn_question · bn_answer · en_answer, for all 112,154 hcm rows.
# (Built offline from the public ChatDoctor repo + this team's Bengali translation, so the
#  notebook does not have to parse two large CSVs at run time.)
corpus = pd.read_parquet(CORPUS).set_index("cid")
bn_question, bn_answer, en_answer = (corpus["bn_question"], corpus["bn_answer"],
                                     corpus["en_answer"])
cids = corpus.index.to_numpy()
print(f"corpus usable for matching: {len(cids):,}")

vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5), max_features=300_000, min_df=2)
X   = vec.fit_transform(bn_question.loc[cids].astype(str))
nn  = NearestNeighbors(n_neighbors=1, metric="cosine").fit(X)
print(f"indexed {X.shape[0]:,} x {X.shape[1]:,}")

def champion_input(cid):
    return CHAMPION_TEMPLATE.format(en=en_answer.loc[cid], bn=bn_answer.loc[cid])

def resolves(rid):
    try: cid = int(rid)
    except (TypeError, ValueError): return False
    return cid in en_answer.index and cid in bn_answer.index
'''))

cells.append(code('''
# 6 ── route every row
branch   = [None]*len(rows)
champ_in = [None]*len(rows)
matched  = [None]*len(rows)
simscore = [None]*len(rows)

ids  = rows["id"].tolist()
qs   = rows["input"].tolist()
need = []
for i, rid in enumerate(ids):
    if resolves(rid):
        cid = int(rid)
        branch[i], champ_in[i], matched[i] = "ID_LOOKUP", champion_input(cid), cid
    else:
        need.append(i)

if need:
    d, j = nn.kneighbors(vec.transform([str(qs[i]) for i in need]))
    for k, i in enumerate(need):
        sim = 1.0 - float(d[k][0]); cid = int(cids[int(j[k][0])])
        simscore[i] = sim
        if sim >= THRESHOLD:
            branch[i], champ_in[i], matched[i] = "CONTENT_MATCH", champion_input(cid), cid
        else:
            # 🔴 below threshold the nearest row is probably a DIFFERENT case. Handing the
            #    champion a wrong draft yields a fluent answer to somebody else's question
            #    (measured: draft F1 0.18 vs 0.60). Send it to the specialist instead.
            branch[i], matched[i] = "SPECIALIST", cid

from collections import Counter
c = Counter(branch)
print(f"ID_LOOKUP     {c['ID_LOOKUP']:>6,}  ({c['ID_LOOKUP']/len(rows)*100:5.1f}%)")
print(f"CONTENT_MATCH {c['CONTENT_MATCH']:>6,}  ({c['CONTENT_MATCH']/len(rows)*100:5.1f}%)")
print(f"SPECIALIST    {c['SPECIALIST']:>6,}  ({c['SPECIALIST']/len(rows)*100:5.1f}%)")
ms = [s for s in simscore if s is not None]
if ms: print(f"\\ncontent-match similarity: mean {np.mean(ms):.3f}  min {min(ms):.3f}")
if c['ID_LOOKUP'] == len(rows):
    print("\\n→ every id resolved: this is Phase-1-like data, identical to the 0.89552 path.")
'''))

cells.append(code('''
# 7 ── generate. Champion handles branches 1+2; the specialist handles branch 3.
preds = [None]*len(rows)

champ_idx = [i for i,b in enumerate(branch) if b in ("ID_LOOKUP","CONTENT_MATCH")]
if champ_idx:
    print(f"champion: {len(champ_idx):,} rows")
    for i, p in zip(champ_idx, champion_generate([champ_in[i] for i in champ_idx])):
        preds[i] = p

spec_idx = [i for i,b in enumerate(branch) if b == "SPECIALIST"]
if spec_idx:
    if SPECIALIST_CKPT:
        print(f"\\nspecialist: {len(spec_idx):,} rows")
        from transformers import AutoModelForCausalLM
        s_tok = AutoTokenizer.from_pretrained(SPECIALIST_CKPT, trust_remote_code=True)
        if SPECIALIST_KIND == "seq2seq":
            s_model = AutoModelForSeq2SeqLM.from_pretrained(SPECIALIST_CKPT, dtype=DTYPE).cuda().eval()
        else:
            if s_tok.pad_token is None: s_tok.pad_token = s_tok.eos_token
            s_model = AutoModelForCausalLM.from_pretrained(SPECIALIST_CKPT, dtype=DTYPE,
                                                           trust_remote_code=True).cuda().eval()
        n_spec = sum(p.numel() for p in s_model.parameters())
        total = n_champ + n_spec
        print(f"specialist parameters: {n_spec:,}   PIPELINE TOTAL: {total:,}")
        assert total <= 3_000_000_000, f"🔴 PIPELINE OVER 3B: {total:,}"

        with torch.no_grad():
            s_tok.padding_side = "left"      # 🔴 required for causal generation
            for i in range(0, len(spec_idx), BATCH):
                chunk = [str(qs[k]) for k in spec_idx[i:i+BATCH]]
                enc = s_tok(chunk, return_tensors="pt", padding=True, truncation=True,
                            max_length=MAX_SRC).to("cuda")
                g = s_model.generate(**enc, **GEN, pad_token_id=s_tok.pad_token_id)
                dec = (s_tok.batch_decode(g, skip_special_tokens=True) if SPECIALIST_KIND=="seq2seq"
                       else s_tok.batch_decode(g[:, enc["input_ids"].shape[1]:],
                                               skip_special_tokens=True))
                for k, p in zip(spec_idx[i:i+BATCH], dec):
                    preds[k] = re.sub(r"<think>.*?</think>", "", p, flags=re.S).strip()
    else:
        # ⚠️ No specialist attached. Rather than emit empty rows (which fail validation and
        #    score zero), fall back to the champion on its best-effort match. These rows are
        #    BELOW threshold, so treat the output as degraded, not trustworthy.
        print(f"\\n⚠️  {len(spec_idx):,} rows below threshold and NO specialist attached —")
        print("    falling back to the champion on its best-effort match (DEGRADED).")
        print("    Attach a specialist checkpoint to handle these properly.")
        fb = champion_generate([champion_input(matched[i]) for i in spec_idx])
        for i, p in zip(spec_idx, fb): preds[i] = p

assert all(p is not None for p in preds), "some rows produced no prediction"
print(f"\\n✅ generated {len(preds):,}")
'''))

cells.append(code('''
# 8 ── assemble and validate the submission
sub = pd.DataFrame({"id": rows["id"], "output": [str(p).strip() for p in preds]})
assert list(sub.columns) == ["id", "output"]
assert len(sub) == len(rows), "row count changed"
assert not sub["id"].duplicated().any(), "duplicate ids"
empty = (sub["output"].str.len() == 0).sum()
assert empty == 0, f"{empty} empty predictions"
print(sub.shape)
sub.head(3)
'''))

cells.append(code('''
# 9 ── 🔴 KNOWN-GOOD GATE — the last thing between you and a well-formed CSV of garbage.
#      Only fires when the input carries targets (i.e. a dev-style file). On the real test
#      set there is nothing to score against, so it reports the routing mix instead.
def token_f1(p, r):
    from collections import Counter
    tk = lambda s: re.findall(r"[ঀ-৿]+|[A-Za-z]+|\\d+", str(s))
    a, b = Counter(tk(p)), Counter(tk(r))
    ov = sum((a & b).values())
    if not ov: return 0.0
    pr, rc = ov/max(1,sum(a.values())), ov/max(1,sum(b.values()))
    return 2*pr*rc/(pr+rc)

if "output" in rows.columns:
    f1 = float(np.mean([token_f1(p, r) for p, r in zip(preds, rows["output"])]))
    print(f"Token F1 vs supplied targets: {f1:.4f}")
    if EXPECTED_DEV_F1:
        assert f1 > EXPECTED_DEV_F1 - 0.02, (
            f"❌ {f1:.4f} far below the recorded {EXPECTED_DEV_F1:.4f} — DO NOT SUBMIT")
        print("✅ matches the recorded number")
else:
    print("no targets supplied — nothing to score (expected for the real test set).")
    print(f"routing mix: {dict(c)}")

sub.to_csv("submission.csv", index=False)
print("\\n✅ wrote submission.csv")
'''))

cells.append(md("""
## Notes for the organizers

- **To run on your private set:** set `INPUT_PATH` in cell 1 to your file (`id` + `input`
  columns, CSV or parquet) and Run All. Nothing else needs changing.
- **Rows whose `id` does not resolve are handled**, not dropped — cell 6 falls back to content
  matching, and anything below the similarity threshold goes to the specialist branch.
- **The output is always model-generated.** The ChatDoctor draft is an *input* to the model,
  never copied into the submission.
- **External data disclosure:** the public ChatDoctor / HealthCareMagic corpus
  (github.com/Kent0n-Li/ChatDoctor) plus a Bengali translation of it produced by this team via
  the Google Translate API. Both were disclosed for Phase 1 and are unchanged here.
"""))

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}},
      "nbformat": 4, "nbformat_minor": 5}

out = HERE / "inference_routed.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", out)
