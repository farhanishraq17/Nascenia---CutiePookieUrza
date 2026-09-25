# E19 — Ten-seed ensemble that actually fits the cap

**Tier 5 — ENSEMBLE · Priority: MEDIUM · unlocked by unlimited GPU**

## The question

> Pooled MBR over **two** seeds lost by −0.0027 LB. Is that a verdict on ensembling, or on
> **n=2**?

## Why it matters

The stated reason MBR failed is specific and quantified:

> *"a consensus selector given candidates that agree to 0.0001 has nothing to select on"*

Seed 11 scored 0.7724, seed 23 scored 0.7723. Two members, near-identical. But those same two
seeds **disagree on 96.6% of rows** — the agreement is in the *aggregate score*, not the *output*.
A consensus selector with ten voters is a materially different instrument from one with two.

**BanglaT5 is small enough that this fits.** 10 × 247.6M = **2.48B**, inside the 3B cap with
room to spare. This is the one place the cap is generous rather than binding, and it has never
been exploited.

Previously this needed 10 × 7.9 h = 79 GPU-hours sequentially. On a fleet the members train in
parallel and cost one wall-clock run.

## Configuration

| | |
|---|---|
| Model | `csebuetnlp/banglat5` × **10 seeds** |
| Seeds | 11, 23, 42, 99, 555, 1337, 2024, 7, 21, 314 |
| Data | The Tier-1 winner (`draft_only` if Tier 1 finds nothing) |
| Config | **Identical across members** — seed is the only variable |
| Steps | Whatever E05 establishes as the convergence point |

**Assert the total parameter count in the inference script**: `10 × 247,577,856 = 2,475,778,560`.
Note the count is **transformers-version dependent** — 296.9M each under transformers 5.x with
untied embeddings, which would be **2.97B** and dangerously close to the cap. Measure it in the
actual Phase 2 inference environment, not locally.

## Method — measure disagreement before pooling

**Step 1 — the gate.** Train the members, decode all ten with beam-4, and compute **pairwise
row-level disagreement**. If members agree on >90% of rows, **stop** — there is nothing to pool
and the remaining steps cannot help.

**Step 2 — combination, in increasing order of cost:**

| Method | Note |
|---|---|
| **Logit averaging** | Average next-token distributions at each decoding step. **Only works within a shared vocabulary — fine for 10 BanglaT5 seeds, impossible across architectures.** This is the method the two-seed test never tried, and the most likely winner. |
| **MBR over pooled candidates** | What lost at n=2. Re-test at n=10 with beam candidates, not sampled ones — sampling was a second confound in the original failure. |
| **Best-of-n by length prior** | Cheap heuristic: pick the candidate closest to the ~100-token reference mean. |

## What it must beat

**The best single member.** With ten seeds, "best single" is itself an optimistic pick — so also
compare against the **median** member to avoid crediting the ensemble for seed luck.

Require more than the **0.0044** noise floor.

## How to read the result

| Result | Meaning |
|---|---|
| Logit averaging > best single by >0.0044 | The two-seed failure was about **n**, not about ensembling. Ship it — it fits the cap. |
| Only MBR improves | Consistent with the earlier finding; the gain is from candidate volume |
| Nothing beats the best single | **Ensembling is closed on this task.** Two independent failures is enough — stop spending on it |
| Members agree >90% of rows | Seeds do not diversify a near-deterministic task. **E14's architecture diversity is the only remaining ensemble hope** |

**The prior here is negative.** MBR has already lost once. This is worth running because the
members are free on a fleet and logit averaging is genuinely untested — not because the odds are
good. Do not let it displace E05 or E17.

---

## Non-negotiables (every experiment)

- **bf16 on sm_80+, fp32 otherwise. NEVER fp16** — T5 goes NaN *silently*.
- **Never change the split**: `--seed 42 --dev-size 5000`. (Distinct from the *training* seed.)
- **Report Token F1 and ROUGE-L**, never the local composite.
- **Assert total params < 3B** in the inference script, measured in the Phase 2 environment.
- **Ignore differences below 0.0044.**
- **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.

Record in [`../RESULTS.md`](../RESULTS.md).
