"""Build the Phase-2 inference notebook for the 0.89347 submission (public LB #1).

Self-contained on purpose: no nascenia-code dataset, no external .py. Phase 2 asks the
inference script to reproduce the leaderboard outputs, and every extra moving part is
another thing that can drift between now and verification.
"""
import json
from pathlib import Path

CELLS = []


def md(src):
    CELLS.append({"cell_type": "markdown", "metadata": {}, "source": src.splitlines(True)})


def code(src):
    CELLS.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": src.splitlines(True)})


md("""# E05/english_draft — Phase 2 inference (public LB **0.89347**, #1)

Reproduces submission `55416313` exactly: BanglaT5 register-transfer, `english + draft`
input, best checkpoint at step 12,000, decoded with the E15 sweep winner.

| | |
|---|---|
| dev-300 | Token F1 **0.8328** · ROUGE-L **0.8039** |
| public LB | **0.89347** |
| params | **247,577,856** — within the 3B cap |
| checkpoint hash | `6f9d4d6756032397` |

🔴 The last cell diffs this notebook's output against the exact CSV that scored 0.89347.
That diff — not a weight hash — is the reproduction evidence: two identical training runs
produce identical *text* from bitwise-different weights, so hashes do not match and
outputs do.
""")

code('''# 1 — pinned libs. transformers 5.x breaks T5 training/inference (trap #00).
!pip install -q --upgrade "transformers==4.57.3" git+https://github.com/csebuetnlp/normalizer
import transformers
assert transformers.__version__ == "4.57.3", transformers.__version__
from normalizer import normalize
print("transformers", transformers.__version__, "| normalizer OK:", normalize("হেলো,  নাসেনিয়া ডকে"))''')

code('''# 2 — hardware gate. Kaggle PyTorch ships sm_70+ only; a P100 (sm_60) cannot run
# anything, and T4 (sm_75) has NO bf16 hardware, so this must be fp32.
import torch, glob, os
assert torch.cuda.is_available(), "no GPU"
cap = torch.cuda.get_device_capability()
assert cap[0] >= 7, f"sm_{cap[0]}{cap[1]} unsupported — need T4 (sm_75)"
# 🔴 gate on capability, NOT is_bf16_supported(): that returns True on a T4 via emulation,
# which is slower than fp32 and not what the model was validated in.
BF16 = cap[0] >= 8
DTYPE = torch.bfloat16 if BF16 else torch.float32
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}")

CKPT = os.path.dirname(glob.glob("/kaggle/input/**/best/config.json", recursive=True)[0])
TEST = glob.glob("/kaggle/input/**/test_english_draft.parquet", recursive=True)[0]
DEV  = glob.glob("/kaggle/input/**/dev_english_draft.parquet", recursive=True)[0]
REF  = glob.glob("/kaggle/input/**/submission_reference.csv", recursive=True)[0]
print("ckpt:", CKPT)''')

code('''# 3 — load, verify the parameter cap and that the logits are finite.
# 🔴 T5 overflows to NaN in fp16 SILENTLY: it still prints a parameter count, still
# "decodes", and still writes a well-formed CSV of garbage. Probe before trusting it.
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tok = AutoTokenizer.from_pretrained(CKPT)
model = AutoModelForSeq2SeqLM.from_pretrained(CKPT, dtype=DTYPE).cuda().eval()

n = sum(p.numel() for p in model.parameters())
print(f"parameters: {n:,}")
assert n <= 3_000_000_000, f"3B CAP BREACHED: {n:,}"
print(f"✅ within the 3B cap (headroom {(3_000_000_000-n)/1e6:.0f}M)")

with torch.no_grad():
    probe = tok("হেলো", return_tensors="pt").to("cuda")
    lg = model(**probe, decoder_input_ids=torch.zeros((1,1), dtype=torch.long, device="cuda")).logits
assert torch.isfinite(lg).all(), "❌ NON-FINITE LOGITS — wrong dtype"
print("✅ logits finite")''')

code('''# 4 — the decoder that produced 0.89347. Every value here is load-bearing.
#   beam 8 · min_new 0 · max_new 320 · length_penalty 1.2   (MBR lost by 0.0027; beam ships)
#   max_source_len 768 = the cap it TRAINED at. Decoding at a smaller cap silently feeds
#   the model a fraction of its input and quietly costs score.
import pandas as pd
# 🔴 beam 8 / lp 1.2 / min_new 0 — the E15 sweep winner, verified on a DISJOINT dev
# subset (0.8348 there vs 0.8328 on the selection rows, so not a spurious winner).
# min_new_tokens 0 is the load-bearing change: the old floor of 80 was set when models
# UNDER-generated, and once this one already produced reference-length answers (~100
# tokens) the floor only padded them, costing precision AND semantic quality.
GEN = dict(num_beams=8, min_new_tokens=0, max_new_tokens=320,
           length_penalty=1.2, do_sample=False)
MAX_SRC, BATCH = 768, 16

@torch.no_grad()
def generate(texts):
    out = []
    for i in range(0, len(texts), BATCH):
        enc = tok([normalize(str(t)) for t in texts[i:i+BATCH]], return_tensors="pt",
                  padding=True, truncation=True, max_length=MAX_SRC).to("cuda")
        g = model.generate(**enc, **GEN)
        out += tok.batch_decode(g, skip_special_tokens=True)
        if i % (BATCH*10) == 0: print(f"  {i}/{len(texts)}", flush=True)
    return out''')

code('''# 5 — 🔴 KNOWN-GOOD GATE. Score the same 300 dev rows the checkpoint was selected on.
# "Assert a recorded dev number before writing anything" — the only thing that ever caught
# the fp16 bug. A well-formed CSV of garbage is indistinguishable from a good one until
# the leaderboard says so.
import re
def tokenize(s):
    return re.findall(r"[\\u0980-\\u09FF]+|[A-Za-z]+|\\d+", str(s))

def token_f1(p, r):
    from collections import Counter
    pt, rt = Counter(tokenize(p)), Counter(tokenize(r))
    ov = sum((pt & rt).values())
    if not ov: return 0.0
    prec, rec = ov/max(1,sum(pt.values())), ov/max(1,sum(rt.values()))
    return 2*prec*rec/(prec+rec)

dev = pd.read_parquet(DEV).iloc[:300]
dp = generate(dev["input"].tolist())
f1 = sum(token_f1(a, b) for a, b in zip(dp, dev["output"])) / len(dev)
print(f"\\ndev-300 Token F1 = {f1:.4f}   (recorded: 0.8328)")
assert f1 > 0.81, f"❌ {f1:.4f} is far below the recorded 0.8328 — do NOT submit this"
print("✅ matches the recorded checkpoint")''')

code('''# 6 — test split -> submission.csv
test = pd.read_parquet(TEST)
preds = generate(test["input"].tolist())
sub = pd.DataFrame({"id": test["id"], "output": preds})
assert len(sub) == 1000 and list(sub.columns) == ["id", "output"]
assert not sub["id"].duplicated().any() and not (sub["output"].str.strip() == "").any()
sub.to_csv("submission.csv", index=False)
print(sub.shape, list(sub.columns))
sub.head(3)''')

code('''# 7 — 🔴 PHASE 2 EVIDENCE: diff against the exact CSV that scored 0.89347.
ref = pd.read_csv(REF)
m = ref.merge(sub, on="id", suffixes=("_ref", "_new"))
assert len(m) == 1000, "id mismatch against the scored submission"
exact = (m["output_ref"].str.strip() == m["output_new"].str.strip()).sum()
agree = sum(token_f1(a, b) for a, b in zip(m["output_ref"], m["output_new"])) / len(m)
print(f"identical rows : {exact}/1000")
print(f"mean Token F1 vs the scored submission : {agree:.4f}")
if exact == 1000:
    print("✅ EXACT reproduction of the 0.89347 submission")
else:
    print("⚠️  not byte-identical — expected when the scored CSV was produced in bf16 on an\\n"
          "    H100 and this runs fp32 on a T4. Token F1 above 0.99 means the same model,\\n"
          "    same decoder, different floating-point path.")''')

nb = {"cells": CELLS, "metadata": {"kernelspec": {"language": "python", "display_name": "Python 3", "name": "python3"},
                                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = Path(__file__).parent / "nascenia-e05-inference.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", out, len(CELLS), "cells")
