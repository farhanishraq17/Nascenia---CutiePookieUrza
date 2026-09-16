# E08 — mT5-base control (draft only)

**Tier 3 — MODEL / ARCHITECTURE · Priority: HIGH (control)**

## The question

> Is mT5 **competitive at all** on this task, given its tokenizer handicap?

## Why it matters

**Without this control, every mT5 result is uninterpretable.** If mT5 with English beats 0.7724
you cannot tell whether the English helped or mT5 is simply the better model. This gives mT5 exactly
the incumbent's input, isolating the model.

It also directly measures the handicap. Both real tokenizers on the same text:

| | source tokens | **target tokens** |
|---|---|---|
| BanglaT5 | 364 | **145** |
| mT5 | 443 | **272** |

**mT5 needs 88% more tokens for identical Bengali output**, where generation quality lives. Its 250k
multilingual vocab fragments Bengali far worse than BanglaT5's native 32k. mT5 starts behind and must
win that back before multilingual pretraining pays off.

## Configuration

| | |
|---|---|
| Model | `google/mt5-base` |
| Data | `data/draft_only/` |
| Sequence | `--max-source-len 640 --max-target-len 640` |
| Batch | `--batch-size 16 --grad-accum 4` (effective 64) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |

## Command

```bash
python ../code/02_train_t5.py \
  --data-dir ../data/draft_only \
  --model google/mt5-base \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 640 --max-target-len 640 \
  --batch-size 16 --grad-accum 4 --eval-batch-size 16 \
  --eval-subset 300 --eval-steps 250 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length \
  --seed 11 --epochs 2.516 --run-name E08_mt5base_draft_only
```

Then decode and score:

```bash
python ../code/04_decode.py --ckpt runs/E08_mt5base_draft_only/best --data-dir ../data/draft_only \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore --record dev.json

python ../code/04_decode.py --ckpt runs/E08_mt5base_draft_only/best --data-dir ../data/draft_only \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore \
  --out submission.csv --record test.json
```

Raise `--batch-size` and lower `--grad-accum` together as VRAM allows — that is pure speed, not a
different experiment. Keep the effective batch at **32–64**.


### ⚠️ Outside evidence already points down (LIT-01)

In the NLP4Health-2025 shared task — same <3B cap, Indic medical dialogue — **mT5 came last on
every metric**: mT5-base scored 0.78 / 0.55 / 0.13 against Gemma2-2B's 0.93 / 0.70 / 0.88. The
overview concludes decoder-only models *"significantly outperform encoder-decoder architectures
(mT5)"*.

That does **not** replace this run: their task is summarisation/extraction, ours is register
transfer, and BanglaT5 (also encoder-decoder) currently holds our #1. But it raises the prior that
E08 comes in low — so **treat the E09 gate as strict**, and do not queue E09 before E08 reports.

## What it must beat

**The incumbent on identical input: Token F1 **0.7724** · ROUGE-L **0.7324** · public LB **0.85030**.**

## How to read the result

| Result | Meaning |
|---|---|
| ≈ 0.7724 | mT5 overcame the tokenizer handicap → **E09/E10 are worth running** |
| ≪ 0.7724 | mT5 is the wrong carrier for Bengali output → **skip E09 and E10 entirely** |

This single run decides whether Tier 3 continues.

---

## Non-negotiables (every experiment)

- **`transformers==4.57.3`** — other versions do not train this pipeline correctly. Assert it.
- **bf16 on sm_80+, fp32 otherwise. 🔴 NEVER fp16** — T5 goes NaN *silently* and still writes a
  well-formed CSV of garbage.
- **Never change the split**: `--seed 42 --dev-size 5000`. Every number in this project rests on it.
- **Select on composite, never `eval_loss`** — they move in opposite directions on some tasks; one
  run's lowest loss coincided with its *worst* Token F1.
- **Report Token F1 and ROUGE-L**, never the local composite (mis-calibrated by ~0.118).
  Predict the leaderboard with `LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L`.
- **Report the register read-out**: `হেলো` opener rate (references 76.4%, draft 0.06%) and
  `নাসেনিয়া` rate (references 50.0%, draft 0.00%). Near the draft's rates ⇒ the model copied its
  input; near the references' ⇒ it learned the conversion.
- **Verify no truncation** — report the % of examples exceeding the source and target caps.

Record everything in [`../RESULTS.md`](../RESULTS.md).

- 🔴 **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.
