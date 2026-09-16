import json
from pathlib import Path

C = []
def md(s): C.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)})
def code(s): C.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": s.strip("\n").splitlines(keepends=True)})

md(r"""
# BRANCH-3 PROBE (specialist arm) — Qwen D1 on the rows branch 3 wants to claim

Sister to `nascenia-branch3-champ`. Same rows, same targets; this one answers them the way the
router would if branch 3 did **not** exist — the raw question straight to the Phase 2 specialist.

**This is the bar branch 3 must clear.** If Qwen wins here, those rows belong to the specialist
and branch 3 stays disabled regardless of how good its draft looked.

🔴 Separate notebook, not a separate cell, because the two models cannot share a kernel: the
champion requires `transformers==4.57.3` and Qwen3.5's architecture does not exist in that
version. This is the same reason the shipped bundle uses two conda envs.

Specialist config is the shipped one: bf16→fp32 on T4, **raw** text (no normalizer), beam 4,
lp 1.0, 1024/640, `enable_thinking=False`.
""")

code(r"""
# 1 -- pinned libs. 🔴 5.14.1 here, NOT the 4.57.3 pinned for the champion elsewhere.
!pip install -q --upgrade "transformers==5.14.1" accelerate sentencepiece
import transformers, torch, glob, os, re, json
from collections import Counter
import numpy as np, pandas as pd
assert transformers.__version__ == "5.14.1", transformers.__version__
assert torch.cuda.is_available()
cap = torch.cuda.get_device_capability(); assert cap[0] >= 7
BF16 = cap[0] >= 8
DTYPE = torch.bfloat16 if BF16 else torch.float32   # T4 has no bf16 hardware -> fp32
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}")
""")

code(r"""
# 2 -- load the D1 specialist
CK = [p for p in glob.glob("/kaggle/input/**/best/config.json", recursive=True) if "qwen35-d1" in p]
assert len(CK) == 1, CK
CKPT = os.path.dirname(CK[0])
PROBE = glob.glob("/kaggle/input/**/branch3_probe.parquet", recursive=True)[0]
print("ckpt :", CKPT); print("probe:", PROBE)

from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained(CKPT, trust_remote_code=True)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(CKPT, dtype=DTYPE, trust_remote_code=True).cuda().eval()
n = sum(p.numel() for p in model.parameters())
assert n == 1_881_825_088, f"{n:,} != 1,881,825,088 -- wrong checkpoint"
with torch.no_grad():
    assert torch.isfinite(model(**tok("হেলো", return_tensors="pt").to("cuda")).logits).all()
print(f"specialist {n:,} params, logits finite")
""")

code(r"""
# 3 -- shipped specialist decoder + metric
SYSTEM = ("You are Nascenia Doc (নাসেনিয়া ডক), a professional doctor answering a patient in "
          "Bengali. Reply only in Bengali, with a greeting, clear medical guidance, and a "
          "polite closing.\n\n"
          "আপনি নাসেনিয়া ডক, একজন পেশাদার ডাক্তার। শুধুমাত্র বাংলায় সম্পূর্ণ, সহানুভূতিশীল "
          "উত্তর লিখুন।")
BEAMS, LP, MAX_SRC, MAX_NEW, BS = 4, 1.0, 1024, 640, 4

def prompt(q):
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": str(q)}]
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

@torch.no_grad()
def generate(texts):
    side = tok.padding_side; tok.padding_side = "left"; out = []
    for i in range(0, len(texts), BS):
        enc = tok([prompt(t) for t in texts[i:i+BS]], return_tensors="pt", padding=True,
                  truncation=True, max_length=MAX_SRC, add_special_tokens=False).to("cuda")
        torch.manual_seed(42)
        g = model.generate(**enc, num_beams=BEAMS, length_penalty=LP, min_new_tokens=0,
                           max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.pad_token_id)
        g = g[:, enc["input_ids"].shape[1]:]
        out += [re.sub(r"<think>.*?</think>", "", x, flags=re.S).strip()
                for x in tok.batch_decode(g, skip_special_tokens=True)]
        print(f"  {min(i+BS,len(texts))}/{len(texts)}", flush=True)
    tok.padding_side = side
    return out

TOK = re.compile(r"[ঀ-৿]+|[A-Za-z]+|\d+")
def tk(s): return TOK.findall(str(s))
def token_f1(p, r):
    a, b = Counter(tk(p)), Counter(tk(r))
    ov = sum((a & b).values())
    if not ov: return 0.0
    pr, rc = ov/max(1,sum(a.values())), ov/max(1,sum(b.values()))
    return 2*pr*rc/(pr+rc)
def _lcs(a, b):
    if not a or not b: return 0
    prev = [0]*(len(b)+1)
    for x in a:
        cur = [0]*(len(b)+1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j-1]+1 if x == y else max(prev[j], cur[j-1])
        prev = cur
    return prev[-1]
def rouge_l(p, r):
    x, y = tk(p), tk(r)
    if not x or not y: return 0.0
    l = _lcs(x, y)
    if not l: return 0.0
    pr, rc = l/len(x), l/len(y)
    return 2*pr*rc/(pr+rc)
""")

code(r"""
# 4 -- Qwen on the raw questions (branch 4)
df = pd.read_parquet(PROBE)
print(f"{len(df)} rows\n")
tgt = df["target"].astype(str).tolist()
outQ = generate(df["question"].astype(str).tolist())

res = pd.DataFrame({
    "id": df["id"],
    "C_qwen_f1": [token_f1(p, t) for p, t in zip(outQ, tgt)],
    "C_qwen_rl": [rouge_l(p, t) for p, t in zip(outQ, tgt)],
    "pred_C": outQ,
})
res.to_parquet("branch3_qwen_arm.parquet", index=False)
print("\n" + "="*66)
print(f"arm C  Qwen D1 on the raw question : Token F1 {res['C_qwen_f1'].mean():.4f}   ROUGE-L {res['C_qwen_rl'].mean():.4f}")
print("="*66)
print("\nCompare against nascenia-branch3-champ arms A (aimc draft) and B (cd sub-threshold draft).")
print("If C wins, branch 3 stays disabled and these rows belong to the specialist.")
""")

nb = {"cells": C, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
      "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
Path("nascenia-branch3-qwen.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote nascenia-branch3-qwen.ipynb ({len(C)} cells)")
