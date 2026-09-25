# E14 — Architecture-diverse ensemble

**Tier 5 — ENSEMBLE & DECODING · Priority: MEDIUM (gated)**

## The question

> Does an **architecture-diverse** ensemble work where a seed ensemble failed?

## Why it matters

Pooled MBR over two BanglaT5 seeds scored **−0.0027 LB** — it lost. Two reasons, both measured:
the task is near-deterministic (sampling adds noise where beam-4 is already near-optimal), and the
two seeds agreed to **0.0001**, giving the consensus selector nothing to choose between.

**Architecture diversity is the untested variable.** Models with different tokenizers and
pretraining objectives make genuinely different errors, which is the condition MBR actually needs.

Also try **logit-level ensembling** rather than candidate pooling — averaging next-token
distributions across models at each decoding step. Not implemented in `04_decode.py`; it needs a
shared vocabulary, so it works for BanglaT5 seeds but **not** across BanglaT5 and mT5.

## Configuration

| | |
|---|---|
| Model | `BanglaT5 + mT5 (+ mBART)` |
| Data | `data/<winner of Tier 1>/` |
| Sequence | `--max-source-len — --max-target-len —` |
| Batch | `--batch-size — --grad-accum —` (effective —) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |



## What it must beat

**The best single model.** MBR must clear it by more than the 0.0044 noise floor.

## How to read the result

Measure **row-level disagreement first** — if the members agree on >90% of rows, skip the
ensemble; there is nothing to pool. Only run MBR if disagreement is substantial.

Prior: MBR has already lost once here. Requires clear evidence, not a marginal gain.

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
