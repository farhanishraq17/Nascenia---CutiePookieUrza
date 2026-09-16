import json
from pathlib import Path

C = []
def md(s): C.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)})
def code(s): C.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": s.strip("\n").splitlines(keepends=True)})

md(r"""
# BRANCH-3 PROBE (champion arm) — is a broad-corpus draft worth routing to the champion?

The router's branch 3 would hand the champion a draft retrieved from **ai_medical_chatbot** when
the id does not resolve and ChatDoctor content-match fails. Draft-level numbers cannot settle
whether that is a good idea, because draft F1 measures the champion's *input*. Only **output** F1
decides the router.

These are the exact rows branch 3 claims at τ₂=0.35 (ai_medical_chatbot only — `given_train` and
`doctor_qa_bangla` are excluded because they have no English side and cannot form a champion
input at all). Their draft F1 is **0.3917**.

This notebook runs the champion on **two** inputs for each row:

| arm | draft source | what it tests |
|---|---|---|
| **A — aimc** | the ai_medical_chatbot match | branch 3 as designed |
| **B — cd_sub** | ChatDoctor's own *sub-threshold* match | simply lowering τ₁ instead |

A sister notebook runs **Qwen D1** on the same rows' raw questions (branch 4). Three-way compare
happens off-notebook.

**The bar:** branch 3 is only worth having if arm A beats Qwen on these rows. If Qwen wins,
those rows belong to the specialist and branch 3 stays disabled.

🔴 Champion config is the shipped one, unchanged: fp32, csebuetnlp-normalized, beam 8, lp 1.2,
768/320. Changing any of it would measure the decoder rather than the routing decision.
""")

code(r"""
# 1 -- pinned libs (champion needs 4.57.3; on 5.x shared/lm_head untie and it decodes differently)
!pip install -q --upgrade "transformers==4.57.3" git+https://github.com/csebuetnlp/normalizer
import transformers, torch, glob, os, re, json
from collections import Counter
import numpy as np, pandas as pd
assert transformers.__version__ == "4.57.3", transformers.__version__
from normalizer import normalize
assert torch.cuda.is_available()
cap = torch.cuda.get_device_capability(); assert cap[0] >= 7
DTYPE = torch.float32          # champion is fp32 always -- bf16 moved 280/1000 rows
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}")
""")

code(r"""
# 2 -- locate + load the champion
CK = [p for p in glob.glob("/kaggle/input/**/best/config.json", recursive=True) if "peak5" in p]
assert len(CK) == 1, CK
CKPT = os.path.dirname(CK[0])
PROBE = glob.glob("/kaggle/input/**/branch3_probe.parquet", recursive=True)[0]
print("ckpt :", CKPT); print("probe:", PROBE)

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tok = AutoTokenizer.from_pretrained(CKPT)
model = AutoModelForSeq2SeqLM.from_pretrained(CKPT, dtype=DTYPE).cuda().eval()
n = sum(p.numel() for p in model.parameters())
assert n == 247_577_856, f"{n:,} != 247,577,856 -- wrong checkpoint"
with torch.no_grad():
    lg = model(**tok("হেলো", return_tensors="pt").to("cuda"),
               decoder_input_ids=torch.zeros((1,1), dtype=torch.long, device="cuda")).logits
assert torch.isfinite(lg).all(), "NON-FINITE LOGITS"
print(f"champion {n:,} params, logits finite")
""")

code(r"""
# 3 -- decoder (shipped config) + metric
GEN = dict(num_beams=8, min_new_tokens=0, max_new_tokens=320, length_penalty=1.2, do_sample=False)
MAX_SRC, BATCH = 768, 8

@torch.no_grad()
def generate(texts):
    out = []
    for i in range(0, len(texts), BATCH):
        enc = tok([normalize(str(t)) for t in texts[i:i+BATCH]], return_tensors="pt",
                  padding=True, truncation=True, max_length=MAX_SRC).to("cuda")
        out += tok.batch_decode(model.generate(**enc, **GEN), skip_special_tokens=True)
        print(f"  {min(i+BATCH,len(texts))}/{len(texts)}", flush=True)
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
# 4 -- run both champion arms
df = pd.read_parquet(PROBE)
print(f"{len(df)} rows claimed by branch 3 at tau2=0.35\n")
tgt = df["target"].astype(str).tolist()

print("arm A -- champion fed the ai_medical_chatbot draft (branch 3 as designed)")
outA = generate(df["champion_in_aimc"].astype(str).tolist())
print("\narm B -- champion fed ChatDoctor's SUB-threshold draft (i.e. just lower tau1)")
outB = generate(df["champion_in_cd"].astype(str).tolist())

res = pd.DataFrame({
    "id": df["id"],
    "aimc_sim": df["aimc_sim"], "cd_sim": df["cd_sim"],
    "A_champ_aimc_f1": [token_f1(p, t) for p, t in zip(outA, tgt)],
    "A_champ_aimc_rl": [rouge_l(p, t) for p, t in zip(outA, tgt)],
    "B_champ_cd_f1":   [token_f1(p, t) for p, t in zip(outB, tgt)],
    "B_champ_cd_rl":   [rouge_l(p, t) for p, t in zip(outB, tgt)],
})
res["pred_A"] = outA
res["pred_B"] = outB
res.to_parquet("branch3_champion_arms.parquet", index=False)

print("\n" + "="*66)
print(f"arm A  champion + aimc draft : Token F1 {res['A_champ_aimc_f1'].mean():.4f}   ROUGE-L {res['A_champ_aimc_rl'].mean():.4f}")
print(f"arm B  champion + cd  draft  : Token F1 {res['B_champ_cd_f1'].mean():.4f}   ROUGE-L {res['B_champ_cd_rl'].mean():.4f}")
print("="*66)
print("\nQwen D1 on these same rows runs in nascenia-branch3-qwen; compare there.")
print("(reference: draft-level F1 was aimc 0.3917 vs ChatDoctor sub-threshold ~0.4769)")
""")

nb = {"cells": C, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
      "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
Path("nascenia-branch3-champ.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote nascenia-branch3-champ.ipynb ({len(C)} cells)")
