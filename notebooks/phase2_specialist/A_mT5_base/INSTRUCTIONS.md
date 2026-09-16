# A — `google/mt5-base` (580M, seq2seq)

**Run every arm in `../EXPERIMENTS.md`.** This file covers what is specific to mT5.

---

## Why this model is in the running, and why it might win outright

On this project's own model zoo (E18, measured on a different task — see the caveat in
`../README.md`), mT5-base scored **0.8017** — **higher than Qwen3.5-2B's 0.7835 while being 3.4×
smaller.** Its tokenizer needs **271 tokens** per Bengali answer versus Qwen3.5's 294 and
Qwen3-1.7B's 689.

It is also the **lowest-risk pipeline of the three**: seq2seq, same architecture family as the
champion, same trainer shape, none of the decoder-only footguns (no chat template, no prompt loss
masking, no left-padding trap). If it wins, the whole Phase 2 branch costs 580M params and leaves
~1.9B of headroom under the cap.

## 🔴 Three things specific to mT5 that will otherwise waste a day

**1. X0/X1 will produce garbage. That is correct.**
mT5-base is a *pure pretrained* span-corruption model with **no instruction tuning whatsoever**.
Zero-shot it will emit sentinel tokens (`<extra_id_0>`), empty strings, or fragments. Do not
debug this — record the number, note the failure mode, move to X2. A near-zero X0 for mT5 next to
a non-trivial X0 for models B/C is a *legitimate finding* about how much the fine-tune has to do,
not a broken setup.

**2. mT5 has a documented truncation problem on this exact corpus.**
When this project ran mT5-base on Bengali medical generation, it left **27.9% of answers cut off
mid-sentence** against the references' 6.8% — and a p95 output length of 123 tokens against the
references' 163. It systematically stops early.

**Watch `truncated_pct` and `mean_pred_tokens` in every eval**, not just Token F1. If truncation
is far above ~7%, the fix is *not* `min_new_tokens` (forcing length destroyed 0.0134 of score for
the champion). Try instead: raise `MAX_TGT`, check the target-length distribution in mT5's own
tokenizer, and confirm answers are not being truncated during *training* (a truncated training
target teaches the model to stop early — that is the actual root cause here).

**3. Learning rate is ~1e-3, not 2e-5.**
Seq2seq class. `2e-5` will barely move it and you will conclude the model is bad when it simply
never trained. This is the mirror of the decoder trap in folders B/C — **never carry an LR across
architecture classes.**

## Starting hyperparameters — yours to change

| Setting | Start | Why this value |
|---|---|---|
| `LR` | **1e-3** | Measured optimum for seq2seq on this corpus. Sweep 3e-4 / 1e-3 / 3e-3 in X5 |
| `OPTIM` | `adafactor` | T5's canonical optimizer; factors the second moment, so it needs far less memory than AdamW (~12 bytes/param) |
| `BATCH × ACCUM` | 4 × 16 | 🔴 product must be 64. mT5 is small — you can likely go 16×4 or 32×2 and train much faster |
| `MAX_SRC / MAX_TGT` | 1024 / 512 | 512 target is generous vs mT5's ~271 median. Raise `MAX_SRC` to 1536 for X3 if you see prompt truncation |
| `MAX_STEPS` | 20000 | Generous on purpose; early stopping finds the peak |
| `EVAL_STEPS` | 500 | Drop to 250 if evals are fast — a coarse grid straddles the peak |
| `GRAD_CKPT` | True | Turn **off** for mT5, it is small enough. ~20% faster |
| precision | bf16 on sm_80+ | 🔴 never fp16 — T5 goes NaN silently and still writes valid-looking output |

## Arm-by-arm

| Arm | Data | Expect | Watch for |
|---|---|---|---|
| **X0** | `plain` | Near-zero, sentinel tokens | Record the failure mode verbatim; do not debug |
| **X1** | `plain` | Still poor | Few-shot is prepended as plain text (no chat template) — inspect one built prompt |
| **X2** 🥇 | `plain` | The primary result | Truncation %, trajectory shape, peak step |
| **X3** | `rag` | vs X2 | 🔴 copy-margin. Also longer inputs — check prompt truncation |
| **X4** | `plain_core_only` | vs X2 | If within 0.0044, prefer the smaller dataset |
| **X5** | winner | 3 LRs, one decade apart | Stay in the seq2seq class |
| **D1** | `plain_core_plus_icliniq` | vs X4 | closest-register extra |
| **D2** | `plain_core_plus_genmedgpt` | vs X4 | 🔴 31-word median answers — watch `mean_pred_tokens` |
| **D3** | `plain_core_plus_doctor_qa_bangla` | vs X4 | the only natively-Bengali source in the project |

## 🔴 This model also carries the data decomposition (D1–D3) for all three

X4 only compares *all extras* against *none*. D1–D3 isolate each of the three extra sources, so
that a negative X4 can be attributed rather than guessed at. **They run here and nowhere else** —
data effects transfer across architectures, and running them on B and C too would cost 6 extra
training runs to answer a question that is not model-specific.

Run each at **X2's exact config** (same LR, batch, steps, seed), changing only `DATA`. Then fill in
the ladder table in `RESULTS.md` and **state the winning data variant there** — B and C will use it
for their own X2.

⚠️ All three extras open with `হেলো` **0.0%** of the time against the competition's **76.4%**. That
is the same off-register signature that got a 166k-row corpus excluded from this project earlier.
Expect small effects, judge against the 0.0044 noise floor, and if everything lands inside it,
**prefer the smaller dataset** — fewer external sources to disclose in the Phase 2 write-up.

## Do not

- Do not set `min_new_tokens > 0` to fix short output — treat the cause, not the symptom.
- Do not use `AutoModelForCausalLM` — mT5 is encoder-decoder.
- Do not carry the decoder LR (2e-5) from folders B/C.
- Do not skip X0 because "it obviously won't work" — it calibrates how much the fine-tune bought.

## Record in `RESULTS.md`

Everything in `../EXPERIMENTS.md`'s reporting table, and specifically for mT5: **`truncated_pct`
against the references' 6.8%** and mean output tokens against ~100. If mT5 wins on Token F1 but
truncates 25%+ of answers, say so loudly — an LLM judge scoring clinical completeness will punish
that far harder than Token F1 does, and Phase 2 is judged by an LLM, not by Token F1.
