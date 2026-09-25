# E09 — mT5-base + best input

**Tier 3 — MODEL / ARCHITECTURE · Priority: MEDIUM (gated by E08)**

## The question

> Does mT5's **multilingual pretraining** handle the English better than BanglaT5 does?

## Why it matters

BanglaT5 must process English through a Bengali-only vocabulary; mT5 was pretrained on 101
languages and should genuinely understand it better. That is mT5's one real advantage here, and this
run is where it would show up.

**Gated on E08.** If mT5 cannot match the incumbent on identical input, this run cannot separate
"English helps" from "mT5 differs" either.

## Configuration

| | |
|---|---|
| Model | `google/mt5-base` |
| Data | `data/<winner of Tier 1>/` |
| Sequence | `--max-source-len 1024 --max-target-len 640` |
| Batch | `--batch-size 16 --grad-accum 4` (effective 64) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |

## Command

```bash
python ../code/02_train_t5.py \
  --data-dir ../data/<winner of Tier 1> \
  --model google/mt5-base \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 1024 --max-target-len 640 \
  --batch-size 16 --grad-accum 4 --eval-batch-size 16 \
  --eval-subset 300 --eval-steps 250 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length \
  --seed 11 --epochs 2.516 --run-name E09_mt5base_best_input
```

Then decode and score:

```bash
python ../code/04_decode.py --ckpt runs/E09_mt5base_best_input/best --data-dir ../data/<winner of Tier 1> \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore --record dev.json

python ../code/04_decode.py --ckpt runs/E09_mt5base_best_input/best --data-dir ../data/<winner of Tier 1> \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore \
  --out submission.csv --record test.json
```

Raise `--batch-size` and lower `--grad-accum` together as VRAM allows — that is pure speed, not a
different experiment. Keep the effective batch at **32–64**.


## What it must beat

**E08** (English contribution within mT5) and **E01** (same input, different model).

## How to read the result

The pair that matters is **E09 − E08** vs **E01 − incumbent**: both measure the English
contribution, each holding its own model fixed.

| Pattern | Meaning |
|---|---|
| Both positive | English genuinely adds information, independent of architecture |
| Only E09 − E08 positive | English only helps a model that can actually read it → mT5 earns its place |
| Only E01 − incumbent positive | The gain is BanglaT5-specific; mT5's tokenizer cost outweighs its comprehension |

---

## Non-negotiables (every experiment)

- **`transformers==4.57.3`** — other versions do not train this pipeline correctly. Assert it.
- **bf16 on sm_80+, fp32 otherwise. NEVER fp16** — T5 goes NaN *silently* and still writes a
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

- **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.
