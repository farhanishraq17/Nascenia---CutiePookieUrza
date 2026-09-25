# E13 — Multi-task: Q→A + transfer

**Tier 4 — DATA STRATEGY · Priority: MEDIUM**

## The question

> Does training **question→answer jointly** with register transfer help either task?

## Why it matters

Train on both objectives at once, mixing `data/question_only` (the competition's actual task) with
the transfer data.

Two reasons it might pay:
1. **Robustness.** If the alignment route is ever closed off — the organizers patch the test set, or
   rescore — a model that can also answer from the question alone still works. That is genuine
   insurance on a 0.85 score built on an id alignment.
2. **Regularisation.** The auxiliary task may prevent over-fitting to the copy-and-edit shortcut.

Cost: the question→answer task caps around Token F1 0.2576, so mixing risks *dragging down* transfer
performance. Use a low auxiliary weight (~10–20% of batches) and measure both tasks separately.

## Configuration

| | |
|---|---|
| Model | `csebuetnlp/banglat5` |
| Data | `data/question_only + <winner>/` |
| Sequence | `--max-source-len 768 --max-target-len 512` |
| Batch | `--batch-size 32 --grad-accum 2` (effective 64) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |

## Command

```bash
python ../code/02_train_t5.py \
  --data-dir ../data/question_only + <winner> \
  --model csebuetnlp/banglat5 \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 \
  --batch-size 32 --grad-accum 2 --eval-batch-size 32 \
  --eval-subset 300 --eval-steps 250 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length \
  --seed 11 --epochs 2.516 --run-name E13_multitask
```

Then decode and score:

```bash
python ../code/04_decode.py --ckpt runs/E13_multitask/best --data-dir ../data/question_only + <winner> \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore --record dev.json

python ../code/04_decode.py --ckpt runs/E13_multitask/best --data-dir ../data/question_only + <winner> \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore \
  --out submission.csv --record test.json
```

Raise `--batch-size` and lower `--grad-accum` together as VRAM allows — that is pure speed, not a
different experiment. Keep the effective batch at **32–64**.


## What it must beat

**The Tier-1 winner** on transfer, and **0.2576** on question→answer.

## How to read the result

Report **both** scores. The interesting outcome is transfer holding steady while
question→answer improves — that is free insurance. If transfer degrades measurably, drop it:
the primary score matters more than the hedge.

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
