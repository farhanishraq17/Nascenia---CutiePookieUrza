# B — `Qwen/Qwen3.5-2B` (2B, decoder-only)

**Run every arm in `../EXPERIMENTS.md`.** This file covers what is specific to Qwen3.5-2B.

---

## Why this model is in the running

It is the **strongest open decoder that fits the budget**. On this project's model zoo it scored
**0.7835** — behind mT5-base (0.8017) but well ahead of every Qwen3/Qwen2.5 variant (0.7287–0.7363),
and the reason is measurable: its **248k vocabulary needs 294 tokens** per Bengali answer versus
Qwen3-1.7B's **689** (a 4.85× handicap). Qwen3.5 beats Qwen3 at every matched step *exactly* as
that token-efficiency gap predicts.

It is also the real test of a question mT5 cannot answer: **does raw scale and broader pretraining
help at genuine question-answering**, as opposed to the restyling task the zoo actually measured?
Phase 2 is judged on clinical quality by an LLM, which is closer to reasoning than to lexical
overlap — a bigger, better-pretrained model may have headroom there that a 580M seq2seq does not.

## 🔴 Four decoder-only traps, all of which have bitten this project before

**1. Learning rate ≈ 2e-5, roughly 50× lower than seq2seq.**
Carrying mT5's `1e-3` onto a decoder **diverges**, and the run reads as *"this model is bad"* when
it is actually *"this run was broken."* This exact mistake is documented in the repo. Never cross
the class boundary.

**2. LEFT padding for generation — right padding fails silently.**
Right-padding inserts pad tokens between the prompt and the continuation, and the model produces
**fluent-looking garbage** that decodes cleanly and scores like a bad model. The notebook handles
this (`tok.padding_side = "left"` inside `generate`, restored after). If you rewrite the decode
loop, keep it.

**3. Loss must be masked on the prompt.**
Only answer tokens should train. The notebook sets `labels = [-100]*len(prompt) + answer_ids`. If
you change the data pipeline, preserve that — training on the prompt teaches the model to generate
questions.

**4. `enable_thinking=False`.**
Qwen3-family models wrap output in `<think>…</think>` blocks by default. This is not a reasoning
task and those blocks burn tokens and must be stripped from every prediction. The notebook passes
the flag *and* strips defensively (`strip_think`) — keep both, since the flag is silently ignored
on some template versions.

## Starting hyperparameters — yours to change

| Setting | Start | Why this value |
|---|---|---|
| `LR` | **2e-5** | Decoder class. Sweep 1e-5 / 2e-5 / 5e-5 in X5 — **never 1e-3** |
| `OPTIM` | `adamw_torch` | ⚠️ AdamW keeps fp32 m+v ≈ **12 bytes/param** — for 2B that is ~24 GB of optimizer state alone, before weights, gradients or activations. On a 24 GB card **switch to `adafactor`**, which factors the second moment and fits. This is not an exotic choice; it is what the champion trained with |
| `BATCH × ACCUM` | 4 × 16 | 🔴 product must be 64. Lower `BATCH` / raise `ACCUM` if you OOM — the product is what matters |
| `MAX_SRC / MAX_TGT` | 2048 / 640 | Generous because RAG inputs carry a full reference case **and** the question, at 294 tokens per answer. Check the actual p95 in *this* tokenizer before lowering |
| `GRAD_CKPT` | True | Keep on for a 2B model unless you have plenty of headroom |
| `EVAL_BATCH` | 8 | Beam-4 generation over 300 rows is the slow part of every eval; lower if you OOM during eval rather than training |
| precision | bf16 on sm_80+ | 🔴 never fp16 |

**Memory is the constraint that will actually bite here**, being the largest of the three. If you
are tight: `adafactor` first, then gradient checkpointing, then smaller `BATCH` with proportionally
larger `ACCUM`, then a shorter `MAX_SRC` **only if you have verified you are not truncating
inputs** (truncation is information the model can never recover — check before trading it away).

## Arm-by-arm

| Arm | Data | Expect | Watch for |
|---|---|---|---|
| **X0** | `plain` | Non-trivial — it is instruction-capable out of the box | Is it answering in Bengali, or drifting to English/Chinese? Record it |
| **X1** | `plain` | Better than X0 | 🔴 If X1 ≫ X2, the fine-tune is broken (LR / masking / padding) — stop and diagnose |
| **X2** 🥇 | `plain` | The primary result | Trajectory shape, peak step, `<think>` leakage |
| **X3** | `rag` | vs X2 | 🔴 copy-margin — a large model is *more* prone to parroting a supplied example |
| **X4** | `plain_core_only` | vs X2 | If within 0.0044, prefer the smaller dataset |
| **X5** | winner | 1e-5 / 2e-5 / 5e-5 | Stay in the decoder class |
| **D1** | `plain_core_plus_icliniq` | vs X4 | closest-register extra |
| **D2** | `plain_core_plus_genmedgpt` | vs X4 | 🔴 31-word median answers — watch `mean_pred_tokens` |
| **D3** | `plain_core_plus_doctor_qa_bangla` | vs X4 | the only natively-Bengali source in the project |

## 🔴 This model runs the data decomposition too — as the decoder half of a cross-check

X4 only compares *all extras* against *none*. D1–D3 isolate each of the three extra sources so a
negative X4 can be attributed rather than guessed at.

**`A_mT5_base` runs the same three arms.** That is deliberate: A is seq2seq, B is decoder-only, and
running the data decomposition on both turns it into a **cross-check**:

| A and B... | Conclusion |
|---|---|
| **agree** on which sources help | The data verdict is solid and architecture-independent — **C inherits it**, no need to re-run there |
| **disagree** | 🔴 Data effects *are* architecture-specific — a real finding. Say so explicitly, and C should then run D1–D3 as well before its X2 is trusted |

Run each at **X2's exact config** (same LR, batch, steps, seed), changing only `DATA`. Record the
result in `RESULTS.md`'s decomposition table, then compare against A's.

⚠️ There is a specific reason a decoder might diverge from mT5 here: all three extras are much
shorter than the competition data (GenMedGPT's median answer is **31 words** against **93**), and
this model's tokenizer spends **294 tokens per Bengali answer**. Length-distribution effects can
land differently on a decoder trained with prompt-masked loss than on a seq2seq. **Watch
`mean_pred_tokens` on every D arm**, not just Token F1 — that is where the mechanism shows up.

⚠️ All three extras open with `হেলো` **0.0%** of the time against the competition's **76.4%** — the
same off-register signature that got a 166k-row corpus excluded from this project earlier. Expect
small effects, judge against the 0.0044 noise floor, and if everything lands inside it, **prefer
the smaller dataset**.

## Do not

- Do not use `1e-3` (that is the seq2seq LR from folder A).
- Do not right-pad during generation.
- Do not train loss on the prompt tokens.
- Do not ship `<think>` blocks into `submission.csv` — check a few raw outputs before writing.
- Do not quantize to fit memory — quantization reduces memory, **not parameter count**, and a
  quantized 2B is still 2B for cap purposes. Use `adafactor` / accumulation instead.

## Record in `RESULTS.md`

Everything in `../EXPERIMENTS.md`'s table, plus specifically: **language drift** (any non-Bengali
output), **`<think>` leakage rate**, the optimizer you actually used, and peak VRAM. The next
person needs to know whether this fits their card before they plan around it.
