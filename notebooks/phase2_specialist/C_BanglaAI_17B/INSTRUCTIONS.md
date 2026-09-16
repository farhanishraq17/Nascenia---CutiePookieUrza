# C — `swapnillo/Bangla-AI-1.7B` (1.7B, decoder-only)

**Run every arm in `../EXPERIMENTS.md`.** This file covers what is specific to this model.

> 🔴 **CHECK `../GPU_BUDGET.md` §4 BEFORE STARTING THIS MODEL.**
> C is the **first thing to cut** if the schedule tightens — and there are only 5 days. The gate:
> **if either A or B clears Token F1 0.1454 by more than the 0.0044 noise floor with fluent
> on-topic Bengali, stop C and spend the time on the winner instead.**
> C's one distinguishing advantage — a strong *zero-shot* score, already measured at **0.1564** —
> is precisely the property that fine-tuning A or B overwrites. Do not run this model to
> completion out of symmetry.

---

## Why this model is in the running — and the honest case against it

**For:** it is the only candidate already **fine-tuned for Bengali instruction-following**
(LoRA on a 100K Bengali instruction dataset, merged into a standalone checkpoint). Of the three,
it should need the least work to produce fluent, well-formed Bengali replies, and its X0/X1
baselines should be the strongest.

**🔴 Against, and this is a real structural problem:** it is built on **Qwen3-1.7B**, whose
tokenizer measured **worst of every decoder this project tested — 689 tokens per Bengali answer,
a 4.85× handicap** versus BanglaT5's 142 and 2.3× worse than Qwen3.5-2B's 294. Its base scored
**0.7287**, the bottom of the zoo.

**Instruction tuning does not change the tokenizer.** That handicap survives any amount of
fine-tuning: every Bengali answer costs ~4.85× more sequence budget, which means shorter effective
context, slower training, slower inference, and more truncation risk at any given cap. This model
is here to test whether strong Bengali instruction-tuning can *compensate* for a bad tokenizer —
**do not assume it will.** A clean negative here is a genuinely useful result.

## ✅ X0 and X1 have ALREADY BEEN MEASURED for this model — real numbers, not estimates

Run on Kaggle T4, 2026-08-17, on the same `dev[0:300]` slice everything else uses.
**Exact parameter count: `1,720,574,976`.**

| arm | Token F1 | ROUGE-L | verdict |
|---|---|---|---|
| **X0 zero-shot** | **0.1564** | 0.1022 | 🥇 **Already beats the 0.1454 bar with NO training at all** |
| X1 few-shot (k=4) | 0.0371 | 0.0285 | 🔴 **Broken run, not a model property — see below** |

**X0 is the most encouraging single result in this whole comparison.** With zero fine-tuning it
clears the bar that the champion could not reach with *any* inference-time fix, and the outputs
are genuinely on-topic — it correctly picks up "scoliosis at T2-3", "blood pressure 113/80",
"mucus plug, third pregnancy" and answers *those*, rather than echoing the question back the way
the champion does. That is real answering behaviour and it is exactly what Phase 2 needs.

**You should still re-run X0 yourself** (different GPU, possibly different precision), but treat
a wildly different number as a setup problem rather than a new finding.

### 🔴 Why X1 collapsed — the trap that will bite you too if you reuse the probe's settings

Every few-shot prediction was **byte-identical across all 300 rows**, began mid-word
(`র শেষে ব্যথা কমে যায়)।`), and degenerated into `সার্ভিকাল সার্ভিকাল সার্ভিকাল…`.

The cause is **prompt truncation, not the model**. The probe used `max_length=3072` with 4
few-shot examples. At this tokenizer's **689 tokens per Bengali answer**, four examples alone are
~2,800 tokens before the system prompt — so the tokenizer truncated from the right and **cut off
the actual patient question entirely**. The model was left continuing a half-finished example.

**This is the single most likely way to waste a run on model C.** Before running X1:

```python
p = build_prompt(dv["input"].iloc[0], shots)
n = len(tok(p, add_special_tokens=False)["input_ids"])
print(f"few-shot prompt = {n} tokens vs MAX_SRC = {MAX_SRC}")
assert n < MAX_SRC, "🔴 the question is being truncated away — raise MAX_SRC or lower K_SHOT"
```

Fix by raising `MAX_SRC` (4096+) **or** lowering `K_SHOT` to 1–2. Do not accept a low X1 for this
model without checking this first.

## 🔴 Load it directly — it is NOT an adapter repo

The model card's usage example shows `PeftModel.from_pretrained(base, ...)`, which is **wrong for
this repo as published**. Verified 2026-08-17: the repo's file listing is
`config.json` + `model.safetensors` + its own `chat_template.jinja` + tokenizer files, and it has
**no `adapter_config.json`** — a PEFT load fails with a 404 on exactly that file. (This already
cost one failed run in this project.)

```python
# correct
model = AutoModelForCausalLM.from_pretrained("swapnillo/Bangla-AI-1.7B",
                                             trust_remote_code=True, dtype=DTYPE)
# WRONG — 404s on adapter_config.json
# model = PeftModel.from_pretrained(base_model, "swapnillo/Bangla-AI-1.7B")
```

The notebook already does this correctly. No `peft` dependency is needed.

## The other decoder traps — identical to folder B

All four apply here without modification, so read **`../B_Qwen35_2B/INSTRUCTIONS.md`** for the
detail:
1. **LR ≈ 2e-5**, never the seq2seq `1e-3`.
2. **LEFT padding** for generation — right padding produces fluent garbage.
3. **Loss masked on the prompt.**
4. **`enable_thinking=False`** + defensive `<think>` stripping (Qwen3 lineage).

## Starting hyperparameters — yours to change

| Setting | Start | Why this value |
|---|---|---|
| `LR` | **2e-5** | Decoder class. Sweep 1e-5 / 2e-5 / 5e-5 in X5. ⚠️ Consider the *lower* end — this model is already instruction-tuned, so a high LR risks overwriting the Bengali capability that is its whole reason for inclusion |
| `OPTIM` | `adamw_torch` | ~12 bytes/param ≈ 20 GB of optimizer state for 1.7B. On a 24 GB card **switch to `adafactor`** |
| `BATCH × ACCUM` | 4 × 16 | 🔴 product must be 64 |
| `MAX_SRC / MAX_TGT` | 2048 / **640** | 🔴 **The most important setting for this model.** At 689 tokens/answer, a cap tuned for another tokenizer silently truncates answers and the score then measures the cap, not the model. **Measure the real p95 target length in THIS tokenizer before training** — see the check below |
| `GRAD_CKPT` | True | Keep on |
| precision | bf16 on sm_80+ | 🔴 never fp16 |

### 🔴 Run this length check before X2, it takes one minute

```python
lens = sorted(len(tok(str(r), add_special_tokens=False)["input_ids"])
              for r in dv["output"].tolist())
p95, med = lens[int(0.95*len(lens))], lens[len(lens)//2]
print(f"target length in THIS tokenizer: median {med}, p95 {p95}")
assert MAX_TGT >= p95, f"MAX_TGT {MAX_TGT} < p95 {p95} — answers will be cut off on 5%+ of rows"
```

This exact failure already invalidated three arms in this project's model zoo — a cap carried over
from BanglaT5 capped a Qwen model at ~46 words against a ~100-word reference, and the run scored
~0.48 while looking completely healthy. **If the assert fires, raise `MAX_TGT`, do not lower the
bar.**

## Arm-by-arm

| Arm | Data | Expect | Watch for |
|---|---|---|---|
| **X0** | `plain` | 🥇 Should be the **best X0 of the three** — this is its main advantage | If X0 is *not* better than B's, its instruction-tuning is not helping and the case for this model largely collapses |
| **X1** | `plain` | Better still | 🔴 If X1 ≫ X2, the fine-tune is broken — diagnose before trusting X2 |
| **X2** 🥇 | `plain` | The primary result | Does fine-tuning *improve* on X0/X1, or overwrite the instruction-tuning and make it worse? Both are real outcomes |
| **X3** | `rag` | vs X2 | 🔴 copy-margin. Also the longest inputs of any arm at 4.85× tokens — verify no prompt truncation |
| **X4** | `plain_core_only` | vs X2 | If within 0.0044, prefer the smaller dataset |
| **X5** | winner | 1e-5 / 2e-5 / 5e-5 | Try the low end first — see the LR note above |

## Do not

- Do not load it with `peft` / `PeftModel`.
- Do not use `1e-3`.
- Do not carry `MAX_TGT` from folder A or B — this tokenizer is 2.3–4.9× hungrier.
- Do not quantize to fit memory (quantization does not reduce parameter count for cap purposes).

## Record in `RESULTS.md`

Everything in `../EXPERIMENTS.md`'s table, plus specifically:
- **measured median / p95 target length in this tokenizer** (the number that justifies `MAX_TGT`),
- **X0 vs X2 delta** — the direct measure of whether fine-tuning helped or hurt a model that was
  already instruction-tuned,
- **X0 compared against folder B's X0** — the cleanest test of whether Bengali instruction-tuning
  actually beats a better tokenizer.
