# E18 — The ≤3B model zoo: sweep every viable base

**Tier 3 — MODEL · Priority: HIGHEST · unlocked by unlimited GPU**

## The question

> **Everything we have ever shipped is encoder-decoder, and BanglaT5 at 248M carries the entire
> 0.85030 result.** Is that the right base — or the only one we tried?

## Why a sweep, not a single model

With a fleet, these all train in **one parallel wave**. Every model here is small; the whole zoo
costs less wall-clock than E05 alone. **There is no reason to pick a favourite in advance** — run
them all on identical data and let the numbers choose.

### Outside evidence that this matters (LIT-01)

The **NLP4Health-2025 shared task** ran the *same* <3B cap on Indic medical dialogue:

| Team | Model | Summ BERTScore | QA F1 | KnV F1 |
|---|---|---|---|---|
| C-DAC | **Gemma2-2B + LoRA** | **0.93** | 0.70 | 0.88 |
| Zaid | Qwen-1.5B + pipeline | 0.83 | 0.67 | 0.72 |
| Samvad | mT5 / Sarvam (RAG) | 0.81 | **0.78** | — |
| KV | **Qwen3-1.7B + QLoRA** | 0.80 | 0.65 | **0.93** |
| Moutushi Roy | **mT5-base** | 0.78 | 0.55 | 0.13 |

> *"decoder-only models (Qwen, Gemma) **significantly outperform encoder-decoder architectures
> (mT5)**"* — and Gemma's edge is credited to **superior tokenizer support for Indic scripts**.

Their task is summarisation/extraction from multi-turn dialogue; ours is register transfer on
single answers. **The tokenizer argument transfers cleanly** (it is about script, not task shape);
the architecture argument is suggestive only. That is exactly why we sweep instead of assuming.

---

## The zoo

All on `data/draft_only/` first — **identical to the incumbent's input**, so this isolates the base
model and nothing else. The Tier-1 winner input comes after.

### Decoders (the untested architecture)

| Model | Params | Why it is here |
|---|---|---|
| **`Qwen/Qwen3-1.7B`** | 1.7B | Qwen3 covers **119 languages incl. Bengali**; **Team KV used this exact model**. Leaves 1.3B of cap for ensembling |
| **`google/gemma-2-2b-it`** | 2.6B | Best zero-shot generation in the paper, best fine-tuned summarisation. Fits the cap **alone** — no room to ensemble |
| `Qwen/Qwen2.5-1.5B-Instruct` | 1.54B | The ≤2.5B hedge CLAUDE.md named and never ran. Qwen2.5's language list does **not** feature Bengali — expect it below Qwen3 |
| `Qwen/Qwen3-0.6B` | 0.6B | Cheapest Qwen3. If it holds up, **ensemble 4 of them** under the cap |
| `meta-llama/Llama-3.2-1B-Instruct` | 1.24B | Weakest in the paper (QA F1 0.43). Cheap control that anchors the low end |

### Encoder-decoders (the family we already ship)

| Model | Params | Why it is here |
|---|---|---|
| `csebuetnlp/banglat5` | 248M | **The incumbent.** Every number is measured against it |
| `ai4bharat/IndicBART` | 244M | Indic-native seq2seq — the closest architectural sibling to BanglaT5 we have not tried |
| `google/mt5-base` | 580M | Already **E08**; do not duplicate — reuse that result |

**Do not run `google/mt5-large`.** Removed from the program: it was a *capacity* experiment, and
two BanglaT5 seeds agreeing to 0.0001 says capacity is not the bottleneck.

**Verify total params from each model card before training, and assert in the inference script.**
Every model this project checked with "-3B" in its name exceeded the cap — Qwen2.5-3B is 3.09B,
Llama-3.2-3B is 3.21B. The cap counts **total** params, not non-embedding.

---

## Configuration

Identical across the zoo except where architecture forces a change.

| | Encoder-decoder | Decoder-only |
|---|---|---|
| Data | `data/draft_only/` | same |
| Precision | **bf16** sm_80+ · never fp16 | same |
| Sequence | 384 src / 256 tgt *(incumbent)* | 1024 total |
| Effective batch | 64 | 64 |
| **LR** | **1e-3** *(measured optimum)* | **1e-5 – 5e-5** |
| Steps | 4,000, eval every 250 | same |

**The LR difference is not optional.** Decoder LLM fine-tuning wants roughly **50× lower** LR
than BanglaT5's 1e-3. Carrying 1e-3 across will diverge, and you will misread a broken run as a
bad model.

**Full fine-tune, not LoRA.** A fleet makes LoRA unnecessary, and adapters count toward the cap
anyway.

**Decoders: format as instruction-following and mask the loss on the prompt** so only answer
tokens train:

```
<|im_start|>user
Rewrite this Bengali draft in the target register.

{draft}<|im_end|>
<|im_start|>assistant
{target}<|im_end|>
```

**Qwen3: set `enable_thinking=False`.** Register transfer is not a reasoning task; thinking
wraps output in `<think>` blocks you would have to strip, and burns tokens.

## What it must beat

**The incumbent: Token F1 0.7724 · ROUGE-L 0.7324 · LB 0.85030.**

## How to read the result

| Pattern | Meaning | Next |
|---|---|---|
| A decoder > 0.7724 | The whole project has been the wrong architecture | That base becomes the primary track; re-run Tier 1 on it |
| Gemma wins but only just | 2.6B beats 248M by a little | Weigh carefully — **Gemma leaves no ensemble headroom**, BanglaT5 leaves room for 10 |
| All ≈ 0.7724 | Base model is not the lever | Consistent with everything else. Value shifts to **ensemble diversity** (E14/E19) |
| All < 0.7724 | BanglaT5's Bengali-native tokenizer beats scale | Strong, useful finding — closes the model question for good |

**Report row-level disagreement with the incumbent for every model, regardless of score.** MBR
failed because two BanglaT5 seeds agreed to 0.0001 and left the consensus selector nothing to work
with. **A model that scores slightly worse but disagrees usefully is still valuable** — it is
exactly what E14 needs and cannot get from another seed.

**Also report tokens-per-answer for each tokenizer.** BanglaT5 needs 145 target tokens where mT5
needs 272. That ratio predicts both cost and quality, and it is the mechanism the paper credits for
Gemma's win.

---

## Non-negotiables (every experiment)

- **bf16 on sm_80+, fp32 otherwise. NEVER fp16** — T5 goes NaN *silently*.
- **Never change the split**: `--seed 42 --dev-size 5000`.
- **Assert total params < 3B** in the inference script, measured in the Phase 2 environment.
- **Report Token F1 and ROUGE-L**, never the local composite.
  `LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L`.
- **Report the register read-out**: `হেলো` opener rate (refs 76.4%) · `নাসেনিয়া` rate (refs 50.0%).
- **Ignore differences below 0.0044.**
- **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.

Record in [`../RESULTS.md`](../RESULTS.md).
