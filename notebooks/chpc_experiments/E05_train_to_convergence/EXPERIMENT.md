# E05 — Train to convergence

**Tier 2 — TRAINING REGIME · Priority: 🥇 HIGHEST**

## The question

> **The incumbent never converged.** How far does this task actually go?

## Why it matters

This is the single most likely source of free score, and it is purely a GPU-time question.

The 0.85030 model was **still improving when its budget ran out**:

| step | Token F1 | loss |
|---|---|---|
| 1000 | 0.7497 | 0.716 |
| 2000 | 0.7673 | 0.630 |
| **2750** | **0.7724** | 0.603 |
| 3000 | 0.7700 | 0.599 |

Loss and metric rose **together** the whole way — no turnover. On the question→answer task every arm
peaked then declined, so we adopted a "budget ~2,000 steps and stop" rule. **That rule does not
transfer here**: the divergence was a property of the *task* (a model inventing content becomes
confidently wrong), not of the model. When the answer is recoverable from the input there is nothing
to over-commit to.

Kaggle's 12-hour ceiling is the only reason this was not answered already.

## Configuration

| | |
|---|---|
| Model | `csebuetnlp/banglat5` |
| Data | `data/<winner of Tier 1>/` |
| Sequence | `--max-source-len 768 --max-target-len 512` |
| Batch | `--batch-size 32 --grad-accum 2` (effective 64) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 10000 · eval every 250 · `load_best_model_at_end` on **composite** |

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
  --seed 11 --epochs 6.291 --run-name E05_train_to_convergence
```

Then decode and score:

```bash
python ../code/04_decode.py --ckpt runs/E05_train_to_convergence/best --data-dir ../data/<winner of Tier 1> \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore --record dev.json

python ../code/04_decode.py --ckpt runs/E05_train_to_convergence/best --data-dir ../data/<winner of Tier 1> \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore \
  --out submission.csv --record test.json
```

Raise `--batch-size` and lower `--grad-accum` together as VRAM allows — that is pure speed, not a
different experiment. Keep the effective batch at **32–64**.


## What it must beat

**The incumbent's peak: Token F1 **0.7724** · ROUGE-L **0.7324** · public LB **0.85030** at step 2,750.**

## How to read the result

Run **10,000 steps** with eval every 250 and early stopping (patience 5). Then report the
**full trajectory**, not just the best number — where it peaks is the finding.

| Peak at | Meaning |
|---|---|
| ~3,000 | The incumbent was essentially converged; look elsewhere for gains |
| 5,000–8,000 | ✅ Free score was being left on the table — re-run every Tier-1 winner at this budget |
| still climbing at 10,000 | Extend further; this task rewards compute more than anything else tested |

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
