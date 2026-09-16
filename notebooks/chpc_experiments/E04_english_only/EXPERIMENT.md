# E04 — BanglaT5 + English only

**Tier 1 — INFORMATION · Priority: MEDIUM**

## The question

> Is our Bengali draft **redundant** once the model has the English?

## Why it matters

If the model can learn `English → competition Bengali` directly, our draft contributes nothing
except its own translation noise — and dropping it halves the input length.

This is the cleanest scientific version of the whole hypothesis: it removes the intermediate
translation entirely and asks the model to do what the organizers' pipeline did. It also tests
BanglaT5's weakest point — its Bengali-only vocabulary must now carry *English* input.

## Configuration

| | |
|---|---|
| Model | `csebuetnlp/banglat5` |
| Data | `data/english_only/` |
| Sequence | `--max-source-len 640 --max-target-len 512` |
| Batch | `--batch-size 32 --grad-accum 2` (effective 64) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |

## Command

```bash
python ../code/02_train_t5.py \
  --data-dir ../data/english_only \
  --model csebuetnlp/banglat5 \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 640 --max-target-len 512 \
  --batch-size 32 --grad-accum 2 --eval-batch-size 32 \
  --eval-subset 300 --eval-steps 250 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length \
  --seed 11 --epochs 2.516 --run-name E04_banglat5_english_only
```

Then decode and score:

```bash
python ../code/04_decode.py --ckpt runs/E04_banglat5_english_only/best --data-dir ../data/english_only \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore --record dev.json

python ../code/04_decode.py --ckpt runs/E04_banglat5_english_only/best --data-dir ../data/english_only \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore \
  --out submission.csv --record test.json
```

Raise `--batch-size` and lower `--grad-accum` together as VRAM allows — that is pure speed, not a
different experiment. Keep the effective batch at **32–64**.


## What it must beat

**E01 (english + draft)** and the incumbent 0.7724.

## How to read the result

| Result | Meaning |
|---|---|
| ≈ E01 | The draft is redundant → ship the shorter, faster input |
| < E01 | The draft carries real value; BanglaT5's English handling is the limit → **try E09 (mT5)** |
| > E01 | The draft was actively adding noise — a strong and surprising result worth double-checking |

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
