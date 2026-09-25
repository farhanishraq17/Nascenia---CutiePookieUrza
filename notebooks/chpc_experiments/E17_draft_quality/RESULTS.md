# E17_draft_quality — results

Fill this in as arms land. **This file is the per-experiment record**; `../RESULTS.md` is only the
cross-experiment scoreboard. Anything surprising goes here, not there.

_CLOSED — no checkpoints, translator outputs only_

## Checkpoints — keep every arm, including the losers

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `—` | pending | | | | | | |

**Why the losers matter too:** a model that scores *below* the incumbent but **disagrees with it
usefully** is exactly what E14/E19 need and cannot get from another seed. MBR failed once because
two members agreed to 0.0001. Do not delete an arm because its number looked bad.

## Per-arm read-out

Record for every arm, not just the winner:

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `—` | | | | | | |

References: ~100 tokens · `হেলো` 76.4% · `নাসেনিয়া` 50.0%.
Near the *draft's* rates (0.06% / 0.00%) ⇒ the model copied its input. Near the references' ⇒ it
learned the conversion.

## Trajectory

Paste each arm's eval trajectory (step · Token F1 · ROUGE-L · loss). **Where a run peaks is often
the finding** — E05 exists only because the incumbent's trajectory showed it had not converged.

## Verdict

- **What it must beat:** see `EXPERIMENT.md`
- **Result:** / within noise (<0.0044) /
- **What it changes:**
- **Row-level disagreement with the incumbent:** _(report even when the score loses)_

## Anything surprising

_Failures, crashes, OOMs, config changes forced by hardware, anything that would mislead a reader
of the numbers alone. Negative results belong here — they stop the same dead end being walked twice._
