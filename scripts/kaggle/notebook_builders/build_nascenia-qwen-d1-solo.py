import json
from pathlib import Path

C = []
def md(s): C.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)})
def code(s): C.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": s.strip("\n").splitlines(keepends=True)})

md(r"""
# Qwen3.5-2B arm D1 — SOLO on the Phase 1 test split

**What this is:** the Phase 2 specialist, run **alone** on all 1,000 Phase 1 test rows, with the
champion and the id-lookup **completely removed**. Every row is answered from scratch from the
patient's raw Bengali question.

**Why:** D1 is the arm shipping in `PHASE2_BUNDLE`, and it has **never been leaderboard-tested**.
The earlier 0.57249 submission was arm **X2** (`data/plain`, all extras) — a different model on
different data. This puts a real LB composite under the model that actually ships.

**What it measures that dev cannot:** BERTScore. It is 50% of the composite and there is no
calibrated local harness for it (`metric.py`'s composite is mis-calibrated by ~0.118). Token F1
and ROUGE-L are already known from held-out dev (0.2625 / 0.1830).

⚠️ **Expect ~0.57–0.58, NOT a leaderboard threat.** The champion holds 0.89552 and is untouched by
this. Predicted here: `0.4646 + 0.3098·0.2625 + 0.2·0.1830 ≈ 0.582`, and that predictor ran ~0.01
high on the last specialist. This is a **diagnostic**, not a competitive entry.

## Fidelity to the shipped bundle

Decode config is copied from `scripts/bundle_decode.py`'s specialist branch, unchanged:

| | shipped bundle | here |
|---|---|---|
| transformers | 5.14.1 | **5.14.1** (Qwen3.5's `model_type` does not exist in 4.57.3) |
| input text | **raw** (no normalizer) | raw |
| decode | beam 4 · lp 1.0 · src 1024 · new 640 · min_new 0 | identical |
| prompt | chat template, Bengali system, `enable_thinking=False` | identical |
| padding | **left** | left |
| seed | `torch.manual_seed(42)` before each batch | identical |
| dtype | bf16 (H200) | 🔴 **fp32** — a T4 has no bf16 hardware (sm_75) |

🔴 **The dtype is the one deliberate deviation, and cell 5 gates on it.** Emulated bf16 on a T4 is
slower than fp32 and is not what anything was validated in (trap #8). fp32 was already shown to
reproduce this model faithfully: the RAG bolt-on run re-decoded the X2 checkpoint on a T4 in fp32
and scored **0.2648** against its recorded **0.2641** — inside the 0.0044 noise floor.
""")

code(r"""
# 1 -- pinned libs. 🔴 5.14.1, NOT the 4.57.3 pinned elsewhere in this project for T5/BanglaT5:
# transformers 4.57.3 does not recognize Qwen3.5's architecture at all. run_D1.json records the
# environment the checkpoint was actually trained in -- pin to THAT, never copy a pin across
# model families.
!pip install -q --upgrade "transformers==5.14.1" accelerate sentencepiece
import transformers, torch, glob, os, re, json, time
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd
assert transformers.__version__ == "5.14.1", transformers.__version__
assert torch.cuda.is_available(), "no GPU"
cap = torch.cuda.get_device_capability()
assert cap[0] >= 7, f"sm_{cap[0]}{cap[1]} unsupported -- need T4 (sm_75)"
# 🔴 gate on capability, NOT is_bf16_supported(): that returns True on a T4 via emulation.
BF16 = cap[0] >= 8
DTYPE = torch.bfloat16 if BF16 else torch.float32
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}  transformers {transformers.__version__}")
""")

code(r"""
# 2 -- locate inputs. 🔴 Filter by substring, never by glob position: Kaggle mounts datasets at
# /kaggle/input/datasets/<owner>/<slug>/, so anchoring the slug as a path segment silently
# matches nothing. Two checkpoints could also expose best/config.json -- disambiguate explicitly.
cfgs = glob.glob("/kaggle/input/**/best/config.json", recursive=True)
print("checkpoints visible:", cfgs)
d1 = [p for p in cfgs if "qwen35-d1" in p]
assert len(d1) == 1, f"expected exactly one D1 checkpoint, got {d1}"
CKPT = os.path.dirname(d1[0])

RUNJSON = glob.glob("/kaggle/input/**/run_D1.json", recursive=True)[0]
DEV  = glob.glob("/kaggle/input/**/nascenia-phase2-pool/dev.parquet", recursive=True)[0]
TEST = glob.glob("/kaggle/input/**/test.csv", recursive=True)[0]   # competition source
print("ckpt :", CKPT)
print("dev  :", DEV)
print("test :", TEST)

rec = json.load(open(RUNJSON))
assert rec["arm"] == "D1", rec["arm"]
REC_F1, REC_STEP = rec["best"]["token_f1"], rec["best"]["step"]
print(f"\nrecorded: arm {rec['arm']}  data {rec['data_dir']}  step {REC_STEP}  "
      f"Token F1 {REC_F1:.4f}  ({rec['train_rows']:,} train rows, {rec['precision']})")
""")

code(r"""
# 3 -- load + param cap. The cap counts TOTAL params from the real tensors, never a model card.
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained(CKPT, trust_remote_code=True)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(CKPT, dtype=DTYPE, trust_remote_code=True).cuda().eval()

n = sum(p.numel() for p in model.parameters())
print(f"parameters: {n:,}")
assert n <= 3_000_000_000, f"3B CAP BREACHED: {n:,}"
assert n == rec["params"], f"loaded {n:,} != recorded {rec['params']:,} -- wrong checkpoint"
assert "qwen" in model.config.model_type.lower(), model.config.model_type
print(f"✅ {model.config.model_type}, matches run_D1.json, {(3_000_000_000-n)/1e6:.0f}M under the cap")
print("   (solo run -- the champion's 247,577,856 is NOT loaded here)")

with torch.no_grad():                    # the only check that ever caught a silent NaN dtype bug
    enc = tok("হেলো", return_tensors="pt").to("cuda")
    assert torch.isfinite(model(**enc).logits).all(), "🔴 NON-FINITE LOGITS -- wrong dtype"
print("✅ logits finite")
""")

code(r"""
# 4 -- the decoder, copied verbatim from bundle_decode.py's specialist branch.
BEAMS, LP, MAX_SRC, MAX_NEW, BS = 4, 1.0, 1024, 640, 8

SYSTEM = ("You are Nascenia Doc (নাসেনিয়া ডক), a professional doctor answering a patient in "
          "Bengali. Reply only in Bengali, with a greeting, clear medical guidance, and a "
          "polite closing.\n\n"
          "আপনি নাসেনিয়া ডক, একজন পেশাদার ডাক্তার। শুধুমাত্র বাংলায় সম্পূর্ণ, সহানুভূতিশীল "
          "উত্তর লিখুন।")

def prompt(q):
    # 🔴 RAW text -- no normalizer. build_data.py never normalized, so normalizing here would be
    # a train/test mismatch. (The champion branch is the opposite; do not cross them.)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": str(q)}]
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

@torch.no_grad()
def run(texts, tag=""):
    out, side = [], tok.padding_side
    tok.padding_side = "left"   # right padding inserts pads between prompt and continuation
    t0 = time.time()
    for i in range(0, len(texts), BS):
        enc = tok([prompt(t) for t in texts[i:i+BS]], return_tensors="pt", padding=True,
                  truncation=True, max_length=MAX_SRC, add_special_tokens=False).to("cuda")
        torch.manual_seed(42)
        g = model.generate(**enc, num_beams=BEAMS, length_penalty=LP, min_new_tokens=0,
                           max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.pad_token_id)
        g = g[:, enc["input_ids"].shape[1]:]                      # drop the prompt back off
        out += [re.sub(r"<think>.*?</think>", "", x, flags=re.S).strip()
                for x in tok.batch_decode(g, skip_special_tokens=True)]
        done = min(i+BS, len(texts))
        if done % (BS*10) == 0 or done == len(texts):
            el = time.time()-t0
            print(f"  {tag}{done}/{len(texts)}  {el/60:.1f}min elapsed, "
                  f"~{el/done*(len(texts)-done)/60:.0f}min left", flush=True)
    tok.padding_side = side
    return out

# metric, identical to shared/evaluate.py
TOKEN_RE = re.compile(r"[ঀ-৿]+|[A-Za-z]+|\d+")
def tokenize(s): return TOKEN_RE.findall(str(s))
def token_f1(p, r):
    pc, rc = Counter(tokenize(p)), Counter(tokenize(r))
    ov = sum((pc & rc).values())
    if not ov: return 0.0
    pr, re_ = ov/max(1,sum(pc.values())), ov/max(1,sum(rc.values()))
    return 2*pr*re_/(pr+re_)
print("decoder ready:", dict(beams=BEAMS, lp=LP, max_src=MAX_SRC, max_new=MAX_NEW, batch=BS))
""")

code(r"""
# 5 -- 🔴 KNOWN-GOOD GATE. Runs BEFORE the test split, so a broken load fails in ~45 min
# instead of after 3 hours of generating a well-formed CSV of garbage (trap #20).
# dev[0:300] is the exact slice D1's checkpoint was selected on -> directly comparable to
# run_D1.json's recorded 0.2646.
dev = pd.read_parquet(DEV).iloc[:300].reset_index(drop=True)
print(f"gate: dev[0:300], recorded Token F1 {REC_F1:.4f} (bf16/H200); this run is fp32/T4\n")
dev_preds = run(dev["input"].astype(str).tolist(), tag="dev ")
f1 = sum(token_f1(p, r) for p, r in zip(dev_preds, dev["output"].astype(str))) / len(dev)
delta = f1 - REC_F1
print(f"\ndev[0:300] Token F1 = {f1:.4f}   recorded {REC_F1:.4f}   delta {delta:+.4f}")
assert f1 > 0.22, f"🔴 {f1:.4f} is far below the recorded {REC_F1:.4f} -- DO NOT SUBMIT THIS"
print("✅ within noise of the recorded value" if abs(delta) <= 0.0044 else
      "⚠️  outside the 0.0044 noise floor -- fp32-vs-bf16 drift, readable but note it")
""")

code(r"""
# 6 -- the test split, solo. No lookup, no champion, no retrieval: raw question -> answer.
test = pd.read_csv(TEST, dtype={"id": str})
assert len(test) == 1000, len(test)
print(f"test: {len(test)} rows, cols {list(test.columns)}")
preds = run(test["input"].astype(str).tolist(), tag="test ")
""")

code(r"""
# 7 -- submission.csv (id,output per the Data tab) + a register read-out.
sub = pd.DataFrame({"id": test["id"], "output": preds})
assert len(sub) == 1000 and list(sub.columns) == ["id", "output"]
assert not sub["id"].duplicated().any(), "duplicate ids"
assert not (sub["output"].str.strip() == "").any(), "empty predictions"
sub.to_csv("submission.csv", index=False)

toks = [len(tokenize(p)) for p in preds]
helo = 100.0*sum(str(p).strip().startswith("হেলো") for p in preds)/len(preds)
trunc = 100.0*sum(bool(str(p).strip()) and str(p).strip()[-1] not in "।?!." for p in preds)/len(preds)
print(f"✅ submission.csv  {sub.shape}")
print(f"\nregister read-out (references: ~100 tokens · হেলো 76.4% · un-terminated 6.8%)")
print(f"  mean tokens   {np.mean(toks):7.1f}")
print(f"  হেলো opener   {helo:7.1f}%")
print(f"  un-terminated {trunc:7.1f}%   (D1 recorded 27.3% on held-out)")

json.dump({"arm": "D1_solo", "ckpt": CKPT, "params": int(n), "dtype": str(DTYPE),
           "decode": dict(beams=BEAMS, lp=LP, max_src=MAX_SRC, max_new=MAX_NEW),
           "dev300_token_f1": f1, "recorded_dev300_token_f1": REC_F1,
           "mean_tokens": float(np.mean(toks)), "helo_pct": helo, "unterminated_pct": trunc},
          open("d1_solo_result.json", "w"), indent=2, ensure_ascii=False)
sub.head(3)
""")

code(r"""
# 8 -- what to expect from the leaderboard, so the number is read correctly.
print("="*70)
print("This is the SPECIALIST ALONE. The champion (0.89552) is not involved.")
print()
print(f"  dev[0:300] Token F1 (this run) : {f1:.4f}")
print(f"  held-out Token F1 / ROUGE-L    : 0.2625 / 0.1830   (n=1000, from the bundle)")
print(f"  predicted LB composite         : ~{0.4646 + 0.3098*0.2625 + 0.2*0.1830:.3f}")
print(f"  arm X2 actually scored         : 0.57249   (different arm, different data)")
print()
print("A result near ~0.57-0.58 is the EXPECTED outcome and confirms the specialist is")
print("working as designed -- it answers from scratch, where the champion's lookup gives it")
print("0.1235. It does not compete with 0.89552 and is not meant to.")
print()
print("The genuinely NEW information is BERTScore, which is 50% of the composite and has no")
print("calibrated local harness. Back it out as:  B = (LB - 0.3*F1 - 0.2*RL) / 0.5")
print("="*70)
""")

nb = {"cells": C, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
      "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
Path("nascenia-qwen-d1-solo.ipynb").write_text(
    json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote nascenia-qwen-d1-solo.ipynb  ({len(C)} cells)")
