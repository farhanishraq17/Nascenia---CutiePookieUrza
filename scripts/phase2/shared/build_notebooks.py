"""build_notebooks.py — generates train.ipynb + inference.ipynb for all three models.

    python shared/build_notebooks.py

Edit THIS file rather than the generated .ipynb -- a notebook is a bad place to keep logic under
version control, and regenerating is one command. The generated notebooks are self-contained
(they import only `shared/evaluate.py`) so they can be run on any machine or uploaded to Kaggle.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODELS = [
    dict(folder="A_mT5_base", model="google/mt5-base", kind="seq2seq", short="mT5-base",
         params="~580M", lr="1e-3", optim="adafactor", d_arms=True,
         note="Seq2seq, same architecture family and trainer as the champion. Best measured "
              "Bengali score of the three despite being smallest. No instruction tuning at all, "
              "so X0/X1 will look terrible -- that is expected, not a bug."),
    dict(folder="B_Qwen35_2B", model="Qwen/Qwen3.5-2B", kind="causal", short="Qwen3.5-2B",
         params="~2B", lr="2e-5", optim="adamw_torch", d_arms=True,
         note="Decoder-only. 248k vocab -> 294 tokens/answer (2.07x BanglaT5). The strongest "
              "open decoder that fits the budget."),
    dict(folder="C_BanglaAI_17B", model="swapnillo/Bangla-AI-1.7B", kind="causal",
         short="Bangla-AI-1.7B", params="~1.7B", lr="2e-5", optim="adamw_torch",
         note="Decoder-only, already Bengali-instruction-tuned on 100K instructions. Merged "
              "standalone checkpoint -- load with AutoModelForCausalLM, NOT peft (it has no "
              "adapter_config.json). WARNING: its Qwen3-1.7B base has the WORST tokenizer of "
              "any decoder tested here -- 689 tokens/answer, a 4.85x handicap. Instruction "
              "tuning does not fix a tokenizer."),
]


def code(src): return {"cell_type": "code", "execution_count": None, "metadata": {},
                       "outputs": [], "source": src.strip("\n").splitlines(keepends=True)}
def md(src):   return {"cell_type": "markdown", "metadata": {},
                       "source": src.strip("\n").splitlines(keepends=True)}


def nb(cells):
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                        "name": "python3"},
                         "language_info": {"name": "python", "version": "3.11"}},
            "nbformat": 4, "nbformat_minor": 5}


# ============================== TRAIN NOTEBOOK ==============================
def train_nb(m):
    seq = m["kind"] == "seq2seq"
    is_D = m.get("d_arms", False)
    # D1/D2/D3 decompose X4's bundled "extras vs no extras" comparison. Run on A (seq2seq) and
    # B (decoder) so the two architectures CROSS-CHECK each other: agreement means the data
    # conclusion is solid and C inherits it; disagreement means data effects are
    # architecture-specific, which is itself a finding. See EXPERIMENTS.md.
    extra_arms = ("""
| `D1` | + iCliniq only | yes |
| `D2` | + GenMedGPT only — the length outlier | yes |
| `D3` | + doctor_qa_bangla only — native Bengali | yes |""" if is_D else "")
    extra_data = ('''
        "D1": "../data/plain_core_plus_icliniq",
        "D2": "../data/plain_core_plus_genmedgpt",
        "D3": "../data/plain_core_plus_doctor_qa_bangla",''' if is_D else "")
    arm_list = "X0 X1 X2 X3 X4 X5" + (" D1 D2 D3" if is_D else "")
    c = []

    c.append(md(f"""
# {m['short']} — Phase 2 specialist training

**Model:** `{m['model']}` ({m['params']}, {m['kind']})

{m['note']}

**Read `../EXPERIMENTS.md` before running.** Set `ARM` in cell 1 and run top to bottom, once per
arm. Every arm writes its own directory; nothing overwrites anything else.

| ARM | What it does | Trains? |
|---|---|---|
| `X0` | zero-shot baseline | no |
| `X1` | few-shot (k=4, train-split examples only) | no |
| `X2` | **fine-tune, plain** — the primary arm | yes |
| `X3` | **fine-tune + RAG** | yes |
| `X4` | data ablation (competition rows only) | yes |
| `X5` | LR sweep — set `LR` by hand, re-run | yes |{extra_arms}

**Bar to beat: Token F1 0.1454.** Noise floor 0.0044.

🔴 **Hyperparameters below are a STARTING POINT, not a specification.** Tune batch size,
accumulation, precision, sequence caps and parallelism to your GPU. The only two things fixed by
the experiment rather than by hardware: **effective batch must stay 64**, and **the learning-rate
class** ({m['lr']} for this architecture) — see `../README.md`.
"""))

    c.append(code(f"""
# 1 ── CONFIG — the only cell you normally edit
ARM       = "X2"                 # {arm_list}
MODEL     = "{m['model']}"
OUT_ROOT  = "runs"               # runs/<ARM>/best , runs/<ARM>/run.json

DATA = {{"X0": "../data/plain", "X1": "../data/plain", "X2": "../data/plain",
        "X3": "../data/rag",   "X4": "../data/plain_core_only",
        "X5": "../data/plain",{extra_data}
        }}[ARM]                          # X5: switch to ../data/rag if X3 won

# ---- yours to tune, per GPU -------------------------------------------------
BATCH, ACCUM = 4, 16             # 🔴 BATCH * ACCUM * n_gpu MUST equal 64
LR           = {m['lr']}                # 🔴 architecture-class LR — do not cross classes
OPTIM        = "{m['optim']}"
MAX_STEPS    = 20000             # generous on purpose; early stopping finds the real peak
EVAL_STEPS   = 500
PATIENCE     = 8
WARMUP       = 300
MAX_SRC, MAX_TGT = {'1024, 512' if seq else '2048, 640'}   # RAG inputs are long — see note below
EVAL_BATCH   = 8
EVAL_ROWS    = 300               # the frozen dev[0:300] selection slice
NUM_BEAMS    = 4
GRAD_CKPT    = True              # turn off if you have memory to spare (it is ~20% slower)
K_SHOT       = 4                 # X1 only
# -----------------------------------------------------------------------------
assert BATCH * ACCUM == 64, f"effective batch {{BATCH*ACCUM}} != 64 — see README"
print(f"ARM={{ARM}}  MODEL={{MODEL}}  DATA={{DATA}}  eff_batch={{BATCH*ACCUM}}")
"""))

    c.append(code("""
# 2 ── environment gate
!pip install -q --upgrade "transformers==4.57.3" accelerate sentencepiece
import transformers, torch, sys, json, time, random
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "../shared")
from evaluate import score_predictions, report

assert torch.cuda.is_available(), "❌ refusing to train on CPU — a silent CPU fallback here " \\
                                  "produces a run that would finish in about a month"
cap = torch.cuda.get_device_capability()
# 🔴 gate on capability, NOT is_bf16_supported() — that returns True on a T4 via emulation,
#    which is slower than fp32 and is not what anything was validated in.
BF16  = cap[0] >= 8
DTYPE = torch.bfloat16 if BF16 else torch.float32     # 🔴 never fp16: T5 goes NaN silently
print(f"{torch.cuda.get_device_name(0)}  sm_{cap[0]}{cap[1]}  ->  {DTYPE}")
print("transformers", transformers.__version__)
"""))

    c.append(code("""
# 3 ── data
tr = pd.read_parquet(f"{DATA}/train.parquet")
dv = pd.read_parquet(f"{DATA}/dev.parquet").iloc[:EVAL_ROWS].reset_index(drop=True)
print(f"train {len(tr):,}   dev {len(dv):,}")
print("\\n--- one training example (READ THIS, especially for X3) ---")
print("INPUT :", str(tr['input'].iloc[0])[:600])
print("OUTPUT:", str(tr['output'].iloc[0])[:300])
# 🔴 For X3, confirm by eye that the 'অনুরূপ কেস' reference is a DIFFERENT case than the
#    question being asked. If the reference IS the answer, retrieval leaked and every X3
#    number is meaningless.
"""))

    if seq:
        c.append(code("""
# 4 ── model + tokenizer (seq2seq)
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
tok   = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL, dtype=DTYPE).cuda()

n = sum(p.numel() for p in model.parameters())
print(f"parameters: {n:,}")
assert n <= 3_000_000_000, f"3B CAP BREACHED: {n:,}"
print(f"✅ within cap. Combined with champion (247,577,856) + retriever (~278M): "
      f"{(n + 247_577_856 + 278_000_000)/1e9:.2f}B")
"""))
        c.append(code("""
# 5 ── tokenized dataset (seq2seq: labels are just the target ids)
from torch.utils.data import Dataset

class S2S(Dataset):
    def __init__(self, df):
        self.src = df["input"].astype(str).tolist()
        self.tgt = df["output"].astype(str).tolist()
    def __len__(self): return len(self.src)
    def __getitem__(self, i):
        x = tok(self.src[i], truncation=True, max_length=MAX_SRC)
        y = tok(text_target=self.tgt[i], truncation=True, max_length=MAX_TGT)
        x["labels"] = y["input_ids"]
        return x

from transformers import DataCollatorForSeq2Seq
collate = DataCollatorForSeq2Seq(tok, model=model, padding=True, label_pad_token_id=-100)

@torch.no_grad()
def generate(texts, num_beams=NUM_BEAMS, max_new=MAX_TGT, length_penalty=1.0):
    model.eval(); out = []
    for i in range(0, len(texts), EVAL_BATCH):
        enc = tok([str(t) for t in texts[i:i+EVAL_BATCH]], return_tensors="pt",
                  padding=True, truncation=True, max_length=MAX_SRC).to("cuda")
        g = model.generate(**enc, num_beams=num_beams, max_new_tokens=max_new,
                           min_new_tokens=0, length_penalty=length_penalty, do_sample=False)
        out += tok.batch_decode(g, skip_special_tokens=True)
    model.train(); return out
"""))
    else:
        c.append(code("""
# 4 ── model + tokenizer (decoder-only)
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=DTYPE,
                                             trust_remote_code=True).cuda()

n = sum(p.numel() for p in model.parameters())
print(f"parameters: {n:,}")
assert n <= 3_000_000_000, f"3B CAP BREACHED: {n:,}"
print(f"✅ within cap. Combined with champion (247,577,856) + retriever (~278M): "
      f"{(n + 247_577_856 + 278_000_000)/1e9:.2f}B")

SYSTEM = ("You are Nascenia Doc (নাসেনিয়া ডক), a professional doctor answering a patient in "
          "Bengali. Reply only in Bengali, with a greeting, clear medical guidance, and a "
          "polite closing.\\n\\n"
          "আপনি নাসেনিয়া ডক, একজন পেশাদার ডাক্তার। শুধুমাত্র বাংলায় সম্পূর্ণ, সহানুভূতিশীল "
          "উত্তর লিখুন।")

def build_prompt(question, shots=()):
    msgs = [{"role": "system", "content": SYSTEM}]
    for q, a in shots:                       # X1 few-shot; empty everywhere else
        msgs += [{"role": "user", "content": str(q)},
                 {"role": "assistant", "content": str(a)}]
    msgs.append({"role": "user", "content": str(question)})
    try:   # Qwen3: thinking blocks would have to be stripped from every prediction
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
"""))
        c.append(code("""
# 5 ── tokenized dataset (decoder: prompt+answer concatenated, loss MASKED on the prompt)
from torch.utils.data import Dataset
eos = tok.eos_token or ""

class Causal(Dataset):
    def __init__(self, df):
        self.src = df["input"].astype(str).tolist()
        self.tgt = df["output"].astype(str).tolist()
    def __len__(self): return len(self.src)
    def __getitem__(self, i):
        p = tok(build_prompt(self.src[i]), add_special_tokens=False)["input_ids"]
        a = tok(self.tgt[i] + eos, add_special_tokens=False)["input_ids"]
        # 🔴 Truncate the PROMPT, never the answer — losing answer tokens teaches the model
        #    to stop early, and the score then measures the truncation, not the model.
        room = MAX_SRC - len(a)
        if room < 16:
            a, room = a[:MAX_SRC - 16], 16
        p = p[-room:]
        return {"input_ids": p + a, "labels": [-100]*len(p) + list(a)}

def collate(batch):
    n_max = max(len(b["input_ids"]) for b in batch); pad = tok.pad_token_id
    out = {"input_ids": [], "attention_mask": [], "labels": []}
    for b in batch:                                    # right-pad for TRAINING only
        k = n_max - len(b["input_ids"])
        out["input_ids"].append(b["input_ids"] + [pad]*k)
        out["attention_mask"].append([1]*len(b["input_ids"]) + [0]*k)
        out["labels"].append(b["labels"] + [-100]*k)
    return {k: torch.tensor(v, dtype=torch.long) for k, v in out.items()}

@torch.no_grad()
def generate(texts, num_beams=NUM_BEAMS, max_new=MAX_TGT, length_penalty=1.0, shots=()):
    # 🔴 LEFT-pad for generation. Right padding inserts pad tokens between the prompt and the
    #    continuation and yields fluent-looking garbage — a silent failure that reads as a
    #    bad model rather than a broken decode.
    model.eval(); side = tok.padding_side; tok.padding_side = "left"; out = []
    for i in range(0, len(texts), EVAL_BATCH):
        prompts = [build_prompt(t, shots) for t in texts[i:i+EVAL_BATCH]]
        enc = tok(prompts, return_tensors="pt", padding=True, truncation=True,
                  max_length=MAX_SRC, add_special_tokens=False).to("cuda")
        g = model.generate(**enc, num_beams=num_beams, max_new_tokens=max_new,
                           min_new_tokens=0, length_penalty=length_penalty,
                           do_sample=False, pad_token_id=tok.pad_token_id)
        out += tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    tok.padding_side = side; model.train(); return out
"""))

    fewshot_block = ("""
    # mT5 has no chat template, so few-shot examples are prepended as plain text.
    q_texts = dv["input"].tolist()
    if ARM == "X1":
        prefix = "".join(f"রোগী: {q}\\nডাক্তার: {a}\\n\\n" for q, a in shots)
        q_texts = [prefix + "রোগী: " + str(q) + "\\nডাক্তার:" for q in q_texts]
    preds = [strip_think(p) for p in generate(q_texts)]
""" if seq else """
    preds = [strip_think(p) for p in generate(dv["input"].tolist(), shots=shots)]
""")
    c.append(code("""
# 6 ── X0 / X1 — no-training baselines. Stops here for those arms.
import re
def strip_think(t): return re.sub(r"<think>.*?</think>", "", str(t), flags=re.S).strip()

if ARM in ("X0", "X1"):
    shots = ()
    if ARM == "X1":
        # 🔴 examples from TRAIN only — drawing them from dev leaks the eval set.
        rng = random.Random(42)
        picks = rng.sample(range(len(tr)), K_SHOT)
        shots = [(tr["input"].iloc[i], tr["output"].iloc[i]) for i in picks]
        print(f"few-shot example row ids: {[str(tr['id'].iloc[i]) for i in picks]}")
""" + fewshot_block + """
    refs  = dv["output"].tolist()
    res   = score_predictions(preds, refs,
                              ref_examples=dv["ref_output"].tolist() if "ref_output" in dv else None)
    txt = report(res, arm=ARM, model=MODEL)
    Path(OUT_ROOT, ARM).mkdir(parents=True, exist_ok=True)
    Path(OUT_ROOT, ARM, "report.txt").write_text(txt, encoding="utf-8")
    json.dump({k: v for k, v in res.items() if k != "per_row_f1"},
              open(f"{OUT_ROOT}/{ARM}/result.json", "w"), indent=2)
    print("\\n--- 3 sample predictions ---")
    for i in range(3):
        print("Q :", str(dv['input'].iloc[i])[:150]); print("P :", preds[i][:250])
        print("R :", str(refs[i])[:150]); print("-"*60)
    print("\\n🛑 X0/X1 complete — do NOT run the training cells below for these arms.")
"""))

    c.append(code(f"""
# 7 ── training arms (X2 X3 X4 X5). Selection is on the COMPOSITE metric, never eval_loss.
from transformers import TrainingArguments, Trainer, TrainerCallback

run_dir = Path(OUT_ROOT, ARM); run_dir.mkdir(parents=True, exist_ok=True)
history, best = [], {{"token_f1": -1.0, "step": -1}}
dev_refs = dv["output"].tolist()
dev_ref_ex = dv["ref_output"].tolist() if "ref_output" in dv else None

class GenEval(TrainerCallback):
    \"\"\"Generation-based eval + best-checkpoint selection + early stopping.

    🔴 Selection is on Token F1, NOT eval_loss. On one run in this project the LOWEST loss
    coincided with the WORST Token F1 — early stopping on loss would have picked the single
    worst checkpoint of the run.\"\"\"
    def __init__(self): self.bad = 0
    def on_step_end(self, args, state, control, model=None, **kw):
        if state.global_step == 0 or state.global_step % EVAL_STEPS: return control
        t0 = time.time()
        preds = [strip_think(p) for p in generate(dv["input"].tolist())]
        r = score_predictions(preds, dev_refs, ref_examples=dev_ref_ex)
        rec = {{"step": state.global_step, "token_f1": round(r["token_f1"], 5),
               "rouge_l": round(r["rouge_l"], 5),
               "mean_tokens": round(r["mean_pred_tokens"], 1),
               "helo_pct": round(r["helo_opener_pct"], 1),
               "secs": round(time.time()-t0, 1)}}
        if "copy_margin" in r: rec["copy_margin"] = round(r["copy_margin"], 4)
        history.append(rec); print("  [eval]", rec, flush=True)
        (run_dir/"trainer_state.json").write_text(
            json.dumps({{"history": history, "best": best}}, indent=2))
        if r["token_f1"] > best["token_f1"]:
            best.update(token_f1=r["token_f1"], rouge_l=r["rouge_l"], step=state.global_step)
            model.save_pretrained(run_dir/"best", safe_serialization=True)
            tok.save_pretrained(run_dir/"best"); self.bad = 0
            print(f"         ✅ new best -> {{run_dir/'best'}}", flush=True)
        else:
            self.bad += 1
            if self.bad >= PATIENCE:
                print("         early stop"); control.should_training_stop = True
        return control

targs = TrainingArguments(
    output_dir=str(run_dir/"ckpt"), max_steps=MAX_STEPS, learning_rate=LR,
    warmup_steps=WARMUP, per_device_train_batch_size=BATCH,
    gradient_accumulation_steps=ACCUM, bf16=BF16, fp16=False,   # 🔴 never fp16
    optim=OPTIM, logging_steps=50, save_strategy="no", report_to=[],
    gradient_checkpointing=GRAD_CKPT, lr_scheduler_type="cosine", seed=42,
    dataloader_num_workers=2,
)
ds = {'S2S' if seq else 'Causal'}(tr)
trainer = Trainer(model=model, args=targs, train_dataset=ds,
                  data_collator=collate, callbacks=[GenEval()])
print(f"training {{len(ds):,}} rows, up to {{MAX_STEPS:,}} steps")
"""))

    c.append(code("""
# 8 ── train
t0 = time.time(); trainer.train(); mins = (time.time()-t0)/60
print(f"\\ndone in {mins:.1f} min — best Token F1 {best['token_f1']:.4f} @ step {best['step']}")
"""))

    c.append(code("""
# 9 ── final scoring + run.json
res = score_predictions([strip_think(p) for p in generate(dv["input"].tolist())],
                        dev_refs, ref_examples=dev_ref_ex)
txt = report(res, arm=ARM, model=MODEL)
(run_dir/"report.txt").write_text(txt, encoding="utf-8")
json.dump({
    "arm": ARM, "model": MODEL, "data_dir": DATA, "params": int(n),
    "train_rows": int(len(tr)), "lr": LR, "optim": OPTIM,
    "effective_batch": BATCH*ACCUM, "max_src": MAX_SRC, "max_tgt": MAX_TGT,
    "max_steps": MAX_STEPS, "eval_steps": EVAL_STEPS, "patience": PATIENCE,
    "precision": str(DTYPE), "gpu": torch.cuda.get_device_name(0),
    "train_minutes": round(mins, 1), "best": best, "trajectory": history,
    "final": {k: v for k, v in res.items() if k != "per_row_f1"},
    "versions": {"torch": torch.__version__, "transformers": transformers.__version__},
}, open(run_dir/"run.json", "w"), indent=2, ensure_ascii=False)
print(f"\\n✅ checkpoint {run_dir/'best'}\\n✅ record     {run_dir/'run.json'}")
assert (run_dir/"best").exists(), "🔴 NO CHECKPOINT — this arm cannot be submitted without a retrain"
"""))

    c.append(md("""
## Before moving on — record in `RESULTS.md`

Copy the printed report block, plus the **full trajectory** from `run.json` (not just the best
number — where it peaks is itself a finding), the peak step, wall-clock, and the checkpoint path.

**If this arm lost, record it anyway with the same care.** A clean negative closes a line of work;
a missing row means someone re-runs it in three days.

**For X3, the copy-margin matters more than Token F1.** Negative margin = the model is copying the
retrieved example instead of answering, and the arm has failed even if the score looks fine.
"""))
    return nb(c)


# ============================== INFERENCE NOTEBOOK ==============================
def infer_nb(m):
    seq = m["kind"] == "seq2seq"
    cls = "AutoModelForSeq2SeqLM" if seq else "AutoModelForCausalLM"
    c = []

    c.append(md(f"""
# {m['short']} — inference, decode sweep (X7), RAG-at-inference (X6)

Run **after** training. Loads one checkpoint and:
1. asserts the parameter cap and that logits are finite,
2. **X6** — feeds RAG-formatted inputs to a plain-trained checkpoint (does RAG need training in?),
3. **X7** — sweeps beams × length_penalty, then **re-verifies the winner on a disjoint dev slice**,
4. decodes the 1,000 competition test rows to `submission.csv`.

🔴 **A well-formed CSV of garbage is indistinguishable from a good one until the leaderboard says
so.** This notebook asserts a known-good dev number *before* writing anything — that assert is the
only thing that has ever caught a silent decode failure in this project.
"""))

    c.append(code(f"""
# 1 ── config
CKPT      = "runs/X2/best"        # the arm you are decoding
DATA      = "../data/plain"       # ../data/rag for an X3 checkpoint, or for X6
DEV_ROWS  = 300                   # selection slice
VERIFY    = (300, 600)            # 🔴 disjoint slice — nothing was selected on these rows
EVAL_BATCH = 8
MAX_SRC, MAX_NEW = {'1024, 512' if seq else '2048, 640'}
EXPECTED_DEV_F1 = None            # 🔴 SET THIS from the arm's run.json before decoding test
"""))

    c.append(code(f"""
# 2 ── env + load
!pip install -q --upgrade "transformers==4.57.3" accelerate sentencepiece
import torch, sys, json, re
import pandas as pd
from pathlib import Path
from transformers import {cls}, AutoTokenizer
sys.path.insert(0, "../shared")
from evaluate import score_predictions, report

cap  = torch.cuda.get_device_capability()
DTYPE = torch.bfloat16 if cap[0] >= 8 else torch.float32     # 🔴 never fp16
tok   = AutoTokenizer.from_pretrained(CKPT{'' if seq else ', trust_remote_code=True'})
{'' if seq else 'if tok.pad_token is None: tok.pad_token = tok.eos_token'}
model = {cls}.from_pretrained(CKPT, dtype=DTYPE{'' if seq else ', trust_remote_code=True'}).cuda().eval()

n = sum(p.numel() for p in model.parameters())
print(f"parameters: {{n:,}}")
assert n <= 3_000_000_000, f"3B CAP BREACHED: {{n:,}}"
TOTAL = n + 247_577_856 + 278_000_000     # + champion + retriever
print(f"✅ specialist within cap. Full pipeline: {{TOTAL:,}} ({{TOTAL/1e9:.2f}}B)")
assert TOTAL <= 3_000_000_000, f"🔴 PIPELINE OVER 3B: {{TOTAL:,}} — drop the retriever or shrink"

with torch.no_grad():   # 🔴 T5 in the wrong dtype emits NaN and still "decodes" cleanly
    probe = tok("হেলো", return_tensors="pt").to("cuda")
    lg = model(**probe{', decoder_input_ids=torch.zeros((1,1),dtype=torch.long,device="cuda")' if seq else ''}).logits
assert torch.isfinite(lg).all(), "❌ NON-FINITE LOGITS — wrong dtype"
print("✅ logits finite")
"""))

    if seq:
        c.append(code("""
# 3 ── decoder
@torch.no_grad()
def generate(texts, num_beams=4, length_penalty=1.0, max_new=MAX_NEW):
    out = []
    for i in range(0, len(texts), EVAL_BATCH):
        enc = tok([str(t) for t in texts[i:i+EVAL_BATCH]], return_tensors="pt",
                  padding=True, truncation=True, max_length=MAX_SRC).to("cuda")
        g = model.generate(**enc, num_beams=num_beams, max_new_tokens=max_new,
                           min_new_tokens=0, length_penalty=length_penalty, do_sample=False)
        out += tok.batch_decode(g, skip_special_tokens=True)
    return out
"""))
    else:
        c.append(code("""
# 3 ── decoder (LEFT padding — right padding silently produces garbage)
SYSTEM = ("You are Nascenia Doc (নাসেনিয়া ডক), a professional doctor answering a patient in "
          "Bengali. Reply only in Bengali, with a greeting, clear medical guidance, and a "
          "polite closing.\\n\\n"
          "আপনি নাসেনিয়া ডক, একজন পেশাদার ডাক্তার। শুধুমাত্র বাংলায় সম্পূর্ণ, সহানুভূতিশীল "
          "উত্তর লিখুন।")

def build_prompt(q):
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": str(q)}]
    try:    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                           enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

def strip_think(t): return re.sub(r"<think>.*?</think>", "", str(t), flags=re.S).strip()

@torch.no_grad()
def generate(texts, num_beams=4, length_penalty=1.0, max_new=MAX_NEW):
    side = tok.padding_side; tok.padding_side = "left"; out = []
    for i in range(0, len(texts), EVAL_BATCH):
        enc = tok([build_prompt(t) for t in texts[i:i+EVAL_BATCH]], return_tensors="pt",
                  padding=True, truncation=True, max_length=MAX_SRC,
                  add_special_tokens=False).to("cuda")
        g = model.generate(**enc, num_beams=num_beams, max_new_tokens=max_new,
                           min_new_tokens=0, length_penalty=length_penalty,
                           do_sample=False, pad_token_id=tok.pad_token_id)
        out += [strip_think(x) for x in
                tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)]
    tok.padding_side = side; return out
"""))

    c.append(code("""
# 4 ── X6: does RAG need to be trained in, or can it be bolted on?
#     Point CKPT at an X2 (plain-trained) checkpoint and DATA at ../data/rag, then run this.
RUN_X6 = False
if RUN_X6:
    rag_dev = pd.read_parquet("../data/rag/dev.parquet").iloc[:DEV_ROWS]
    p = generate(rag_dev["input"].tolist())
    r = score_predictions(p, rag_dev["output"].tolist(),
                          ref_examples=rag_dev["ref_output"].tolist())
    report(r, arm="X6 RAG-at-inference-only", model=CKPT)
    print("compare against: X2 (same ckpt, plain input) and X3 (RAG trained in).")
    print("≈X3 -> RAG needs no training.  ≪X3 -> it must be trained in.  ≪X2 -> it actively hurts.")
"""))

    c.append(code("""
# 5 ── X7: decode sweep on the selection slice
dv = pd.read_parquet(f"{DATA}/dev.parquet")
sel = dv.iloc[:DEV_ROWS]
refs = sel["output"].tolist()
ref_ex = sel["ref_output"].tolist() if "ref_output" in sel else None

rows = []
for beams in (4, 8):
    for lp in (1.0, 1.2, 1.5):
        r = score_predictions(generate(sel["input"].tolist(), beams, lp), refs, ref_examples=ref_ex)
        rows.append({"beams": beams, "lp": lp, "token_f1": round(r["token_f1"], 4),
                     "rouge_l": round(r["rouge_l"], 4),
                     "tokens": round(r["mean_pred_tokens"], 1)})
        print(rows[-1], flush=True)
sweep = pd.DataFrame(rows).sort_values("token_f1", ascending=False)
print("\\n", sweep.to_string(index=False))
BEST_BEAMS, BEST_LP = int(sweep.iloc[0]["beams"]), float(sweep.iloc[0]["lp"])
print(f"\\nwinner: beams={BEST_BEAMS} lp={BEST_LP}")
"""))

    c.append(code("""
# 6 ── 🔴 verify the winner on the DISJOINT slice. A 6-config sweep over 300 rows finds
#      spurious winners; this is how the champion's own decoder was confirmed before shipping.
ver = dv.iloc[VERIFY[0]:VERIFY[1]]
if len(ver):
    rv = score_predictions(generate(ver["input"].tolist(), BEST_BEAMS, BEST_LP),
                           ver["output"].tolist(),
                           ref_examples=ver["ref_output"].tolist() if "ref_output" in ver else None)
    report(rv, arm=f"X7 verify beams={BEST_BEAMS} lp={BEST_LP}", model=CKPT)
    print("A winner that holds up here is real. One that collapses was sweep noise.")
else:
    print("⚠️ dev split has no rows in the verify range — rebuild dev with more rows to verify.")
"""))

    c.append(code("""
# 7 ── 🔴 KNOWN-GOOD GATE, then decode test
assert EXPECTED_DEV_F1 is not None, "🔴 set EXPECTED_DEV_F1 from the arm's run.json first"
got = score_predictions(generate(sel["input"].tolist(), BEST_BEAMS, BEST_LP), refs)["token_f1"]
print(f"dev[0:{DEV_ROWS}] Token F1 = {got:.4f}   (recorded {EXPECTED_DEV_F1:.4f})")
assert got > EXPECTED_DEV_F1 - 0.02, (
    f"❌ {got:.4f} is far below the recorded {EXPECTED_DEV_F1:.4f} — DO NOT write a submission. "
    "Something about this load/decode differs from training.")
print("✅ matches the recorded number — safe to decode test")

test = pd.read_parquet(f"{DATA}/test.parquet")
preds = generate(test["input"].tolist(), BEST_BEAMS, BEST_LP)
sub = pd.DataFrame({"id": test["id"], "output": preds})
assert len(sub) == 1000 and list(sub.columns) == ["id", "output"]
assert not sub["id"].duplicated().any(), "duplicate ids"
assert not (sub["output"].str.strip() == "").any(), "empty predictions"
sub.to_csv("submission.csv", index=False)
print(sub.shape); sub.head(3)
"""))

    c.append(md("""
## Deliverables

- `submission.csv` — 1,000 rows, `id,output`
- the decode sweep table + the **disjoint verification** number (not just the selection number)
- winning `beams` / `length_penalty`, recorded in `RESULTS.md`
- X6's verdict if you ran it

🔴 **This notebook covers the Phase 2 specialist branch only.** The full submission also needs the
champion's branch for ChatDoctor-resolving ids — see `../../FINAL SUBMISSION_DRAFT/`. The combined
routing script is still to be written, and needs both halves finalised first.
"""))
    return nb(c)


def main():
    for m in MODELS:
        d = ROOT / m["folder"]; d.mkdir(parents=True, exist_ok=True)
        for name, builder in (("train.ipynb", train_nb), ("inference.ipynb", infer_nb)):
            (d / name).write_text(json.dumps(builder(m), ensure_ascii=False, indent=1),
                                  encoding="utf-8")
            print(f"wrote {m['folder']}/{name}")


if __name__ == "__main__":
    raise SystemExit(main())
