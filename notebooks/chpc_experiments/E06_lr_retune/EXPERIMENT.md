# E06 — Re-tune the learning rate

**Tier 2 — TRAINING REGIME · Priority: HIGH**

## The question

> **lr 1e-3 was tuned on a different task.** Is it still optimal here?

## Why it matters

Our LR sweep (seven arms) was run on **question→answer**, and 1e-3 won there:

| lr | peak Token F1 | peak step |
|---|---|---|
| 1e-4 | 0.2051 | — |
| 3e-4 | 0.2365 | still climbing @3,000 |
| **1e-3** | **0.2576** | **2,000** |
| 3e-3 | 0.2390 ↓ | 750 |

But that task had loss and metric **diverging**, and this one has them **moving together**. The
optimisation landscape is demonstrably different, so the optimum may be too. Carrying 1e-3 over is a
reasonable prior — not a measured fact — and it has never been checked.

Three runs, identical except LR. Cheap on a fast GPU, and it gates every other experiment's config.

## Configuration

| | |
|---|---|
| Model | `csebuetnlp/banglat5` |
| Data | `data/<winner of Tier 1>/` |
| Sequence | `--max-source-len 768 --max-target-len 512` |
| Batch | `--batch-size 32 --grad-accum 2` (effective 64) |
| LR | `1e-3` warmup 200, Adafactor (**this is the variable**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |

## Command

```bash
python ../code/02_train_t5.py \
  --data-dir ../data/<winner of Tier 1> \
  --model csebuetnlp/banglat5 \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 \
  --batch-size 32 --grad-accum 2 --eval-batch-size 32 \
  --eval-subset 300 --eval-steps 250 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length \
  --seed 11 --epochs 2.516 --run-name E06_lr_retune
```

Then decode and score:

```bash
python ../code/04_decode.py --ckpt runs/E06_lr_retune/best --data-dir ../data/<winner of Tier 1> \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore --record dev.json

python ../code/04_decode.py --ckpt runs/E06_lr_retune/best --data-dir ../data/<winner of Tier 1> \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore \
  --out submission.csv --record test.json
```

Raise `--batch-size` and lower `--grad-accum` together as VRAM allows — that is pure speed, not a
different experiment. Keep the effective batch at **32–64**.


## What it must beat

Each other, and the incumbent 0.7724.

## How to read the result

Run **3e-4 · 1e-3 · 3e-3**, each 4,000 steps, eval every 250.

If the winner is not 1e-3, **re-run the Tier-1 winner at the new LR before drawing conclusions** —
every Tier-1 number would have been measured at a suboptimal setting. Watch whether the
peak-then-decline shape appears at high LR here; if it does, this task is less different from
question→answer than E05 assumes.

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
