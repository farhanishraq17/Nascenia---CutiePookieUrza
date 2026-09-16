import json
from pathlib import Path

C = []
def md(s): C.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)})
def code(s): C.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": s.strip("\n").splitlines(keepends=True)})

md(r"""
# Draft-quality transfer test — Claude vs Google draft, 24 dev rows

**Question:** E17 measured Claude beats Google on *draft* Token F1 (+0.0631, t=5.88, n=24).
Does that survive through the champion into *final output*? Nobody has measured this — it is
the cheap 24-row test before committing to a full 1,000-row re-translation
(`fine_tune_project/E17_draft_quality/test1000_retranslate/`).

**Method:** all 24 rows already have a Claude translation (`claude_batches/`) AND happen to fall
inside the frozen dev split, so we have real organizers' targets. For each row, build TWO model
inputs — `english: {en}\nbangla: {google_draft}` and `english: {en}\nbangla: {claude_draft}` —
run both through the exact shipped champion (peak5, beam 8, lp 1.2), and score both against the
same true target. Paired, so the only thing that differs per row is which draft it saw.

This is a **paired n=24 test**, same statistical shape as the E17 measurement it's checking.
""")

code(r"""
# 1 — pinned libs. transformers 5.x breaks T5 training/inference (trap #00).
!pip install -q --upgrade "transformers==4.57.3" git+https://github.com/csebuetnlp/normalizer
import transformers
assert transformers.__version__ == "4.57.3", transformers.__version__
from normalizer import normalize
print("transformers", transformers.__version__, "| normalizer OK:", normalize("হেলো,  নাসেনিয়া ডকে"))
""")

code(r"""
# 2 — hardware gate. Kaggle PyTorch ships sm_70+ only; a P100 (sm_60) cannot run
# anything, and T4 (sm_75) has NO bf16 hardware, so this must be fp32.
import torch, glob, os
assert torch.cuda.is_available(), "no GPU"
cap = torch.cuda.get_device_capability()
assert cap[0] >= 7, f"sm_{cap[0]}{cap[1]} unsupported — need T4 (sm_75)"
BF16 = cap[0] >= 8
DTYPE = torch.bfloat16 if BF16 else torch.float32
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}")

CKPT = os.path.dirname(glob.glob("/kaggle/input/**/best/config.json", recursive=True)[0])
print("ckpt:", CKPT)
""")

code(r"""
# 3 — load, verify the parameter cap and that the logits are finite.
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tok = AutoTokenizer.from_pretrained(CKPT)
model = AutoModelForSeq2SeqLM.from_pretrained(CKPT, dtype=DTYPE).cuda().eval()

n = sum(p.numel() for p in model.parameters())
print(f"parameters: {n:,}")
assert n <= 3_000_000_000, f"3B CAP BREACHED: {n:,}"
print(f"OK within the 3B cap (headroom {(3_000_000_000-n)/1e6:.0f}M)")

with torch.no_grad():
    probe = tok("হেলো", return_tensors="pt").to("cuda")
    lg = model(**probe, decoder_input_ids=torch.zeros((1,1), dtype=torch.long, device="cuda")).logits
assert torch.isfinite(lg).all(), "NON-FINITE LOGITS -- wrong dtype"
print("logits finite")
""")

code(r"""
# 4 — the decoder. Identical to the shipped 0.89552 entry: beam 8, lp 1.2, min_new 0.
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
    return out
""")

code(r"""
# 5 — metric: Token F1 + ROUGE-L, same tokenizer/LCS as NOTEBOOKS/metric.py.
import re, numpy as np
from collections import Counter

def tokenize(s):
    return re.findall(r"[ঀ-৿]+|[A-Za-z]+|\d+", str(s))

def token_f1(p, r):
    pt, rt = Counter(tokenize(p)), Counter(tokenize(r))
    ov = sum((pt & rt).values())
    if not ov: return 0.0
    prec, rec = ov/max(1,sum(pt.values())), ov/max(1,sum(rt.values()))
    return 2*prec*rec/(prec+rec)

def _lcs_len(a, b):
    la, lb = len(a), len(b)
    if la == 0 or lb == 0: return 0
    if la > lb: a, b = b, a; la, lb = lb, la
    prev = np.zeros(lb+1, dtype=np.int32); cur = np.zeros(lb+1, dtype=np.int32)
    for i in range(la):
        cand = np.where(b == a[i], prev[:-1]+1, 0)
        np.maximum(cand, prev[1:], out=cur[1:]); cur[0] = 0
        np.maximum.accumulate(cur, out=cur)
        prev, cur = cur, prev
    return int(prev[lb])

def rouge_l(p, r):
    pt, rt = tokenize(p), tokenize(r)
    if not pt or not rt: return 0.0
    vocab = {}
    pa = np.fromiter((vocab.setdefault(t, len(vocab)) for t in pt), dtype=np.int32, count=len(pt))
    ra = np.fromiter((vocab.setdefault(t, len(vocab)) for t in rt), dtype=np.int32, count=len(rt))
    lcs = _lcs_len(pa, ra)
    if lcs == 0: return 0.0
    prec, rec = lcs/len(pt), lcs/len(rt)
    return 2*prec*rec/(prec+rec)

print("metric fns ready")
""")

_data24 = json.load(open(Path(__file__).parent / "data24.json", encoding="utf-8"))
code(
    "# 6 -- the 24-row dataset: id, english (ChatDoctor answer), google_draft (our Bengali\n"
    "# translation of that answer, i.e. what the champion trains on), claude_draft (Claude Opus 5\n"
    "# translation of the same English, from E17's claude_batches/), target (organizers' true\n"
    "# answer for this id, from the frozen dev split -- these 24 ids all resolve into dev).\n"
    "DATA24 = " + repr(_data24) + "\n"
    "print(f\"{len(DATA24)} rows loaded\")\n"
    "assert len(DATA24) == 24\n"
    "\n"
    "TEMPLATE = \"english: {en}\\nbangla: {bn}\"\n"
    "google_inputs = [TEMPLATE.format(en=r[\"english\"], bn=r[\"google_draft\"]) for r in DATA24]\n"
    "claude_inputs = [TEMPLATE.format(en=r[\"english\"], bn=r[\"claude_draft\"]) for r in DATA24]\n"
    "targets = [r[\"target\"] for r in DATA24]\n"
)

code(r"""
# 7 — generate both arms and score, paired per row.
import pandas as pd

google_out = generate(google_inputs)
claude_out = generate(claude_inputs)

rows = []
for r, go, co, tgt in zip(DATA24, google_out, claude_out, targets):
    rows.append({
        "id": r["id"],
        "google_f1": token_f1(go, tgt), "claude_f1": token_f1(co, tgt),
        "google_rl": rouge_l(go, tgt),  "claude_rl": rouge_l(co, tgt),
    })
res = pd.DataFrame(rows)
res["delta_f1"] = res["claude_f1"] - res["google_f1"]
res["delta_rl"] = res["claude_rl"] - res["google_rl"]
res
""")

code(r"""
# 8 — aggregate + paired significance (paired t-test, same shape as the E17 draft-level test).
from scipy import stats

mean_g_f1, mean_c_f1 = res["google_f1"].mean(), res["claude_f1"].mean()
mean_g_rl, mean_c_rl = res["google_rl"].mean(), res["claude_rl"].mean()

t_f1, p_f1 = stats.ttest_rel(res["claude_f1"], res["google_f1"])
t_rl, p_rl = stats.ttest_rel(res["claude_rl"], res["google_rl"])

print("=== FINAL OUTPUT (after the champion), n=24, paired ===")
print(f"Token F1  google={mean_g_f1:.4f}  claude={mean_c_f1:.4f}  delta={mean_c_f1-mean_g_f1:+.4f}  t={t_f1:.2f}  p={p_f1:.4f}")
print(f"ROUGE-L   google={mean_g_rl:.4f}  claude={mean_c_rl:.4f}  delta={mean_c_rl-mean_g_rl:+.4f}  t={t_rl:.2f}  p={p_rl:.4f}")
print()
print("wins/losses/ties (Token F1):", (res["delta_f1"]>0).sum(), "/", (res["delta_f1"]<0).sum(), "/", (res["delta_f1"]==0).sum())
print()
print("=== for reference, E17's DRAFT-level result on these same rows ===")
print("Token F1  google vs claude draft:  delta=+0.0631  t=5.88  (measured pre-champion)")
print()
composite_delta = 0.3098*(mean_c_f1-mean_g_f1) + 0.2*(mean_c_rl-mean_g_rl)
print(f"implied LB composite delta (0.3098*dF1 + 0.2*dRL, BERTScore term ignored): {composite_delta:+.4f}")
""")

nb = {"cells": C, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
      "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}

Path("nascenia-transfer-test24.ipynb").write_text(
    json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote nascenia-transfer-test24.ipynb  ({len(C)} cells)")
