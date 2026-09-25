# E15 — Decoder sweep

**Tier 5 — ENSEMBLE & DECODING · Priority: HIGH (cheap)**

## The question

> Is **beam-4 / min_new 80 / lp 1.0** still the right decoder for the best model?

## Why it matters

Those settings were tuned when the model was **undershooting** on the question→answer task. The
current model reads a draft and knows the right length from it — measured mean output 98.7 tokens
against references at 100.2.

Two specific suspicions, both measured on dev:
- **`min_new_tokens 80` forces overshoot on 4.7%** of rows whose true answer is shorter than 80 tokens.
- **Beam width was never swept** above 4.

No training required — this runs against an existing checkpoint. Cheapest experiment here.

## Configuration

| | |
|---|---|
| Model | `<best checkpoint>` |
| Data | `data/<its dataset>/` |
| Sequence | `--max-source-len — --max-target-len —` |
| Batch | `--batch-size — --grad-accum —` (effective —) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |



## What it must beat

The best model's own beam-4 score.

## How to read the result

Sweep `num_beams ∈ {4, 8, 12}` × `length_penalty ∈ {0.6, 0.8, 1.0, 1.2}` ×
`min_new_tokens ∈ {0, 40, 60, 80}` on the same 300 dev rows.

Expect a **small but reliable** gain (~+0.003–0.01 LB). Only accept a winner that beats beam-4 by
more than the **0.0044** noise floor — and re-verify it on a second, disjoint dev subset before
shipping, since a 3-way sweep over 300 rows will find spurious winners.

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
