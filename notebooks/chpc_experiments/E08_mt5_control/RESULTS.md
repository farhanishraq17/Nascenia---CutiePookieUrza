# E08_mt5_control — results

**Ran 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL, bf16.** See `../_slurm/README.md`.

## ❌ VERDICT: mT5 is not competitive. **Skip E09–E10.** The tokenizer verdict holds.

Identical input to the incumbent (`draft_only`), so this isolates the model.

| | Model | Params | Token F1 | ROUGE-L | pred LB |
|---|---|---|---|---|---|
| 🏆 incumbent — BanglaT5 @384/256 | banglat5 | 247.6 M | **0.7724** | 0.7324 | 0.85030 *(actual)* |
| `E18/banglat5` — same recipe, this pipeline | banglat5 | 247.6 M | **0.7768** | 0.7389 | 0.8531 |
| **E08 — mT5-base @640/640** | **mt5-base** | **582.4 M** | **0.7563** | 0.7168 | 0.8423 |

**E08 − incumbent = −0.0161** · **E08 − E18/banglat5 = −0.0205**, both far outside the 0.0044
noise floor. mT5 loses while carrying **2.35× the parameters** and a **larger sequence budget**
(640/640 vs 384/256). The decision table's "E08 ≪ 0.7724 ⇒ drop E09" condition is met.

⚠️ **E09 was queued before this landed** (mT5 on the Tier-1 winner, `english_draft`). Left running
on purpose: it is the second half of the `E09 − E08` pair, which is the only thing that can say
whether English helps *independently of architecture* or only through BanglaT5's tokenizer. That
is a different question from "should mT5 ship", which this arm has already answered with no.

## Checkpoints — 🔴 keep every arm, including the losers

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `main` | ✅ `E08_mt5_control/main/best` | *(not uploaded)* | 0.7563 | 0.7168 | **3,750** | 1.50 | ckpt hash `0845d190d7cbcdd3` · 582,401,280 params |

🔴 Kept despite losing. It is the only **non-BanglaT5 encoder-decoder that still works** (unlike
IndicBART at 0.44), so it is a credible E14 ensemble member: different pretraining, different
vocabulary, genuinely different errors. `main/submission.csv` is written.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `main` | **92.1** | 75.7 % | 51.3 % | 0.95 % / **0.715 %** | bf16 | H100 NVL |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %.
**The register is learned correctly — this is a genuine model deficit, not a broken run.**
Two details point at the same cause:
- **92.1 mean output tokens vs the references' ~100** — the shortest output of any healthy arm
  (BanglaT5 arms land 98.9–100.5). Short output costs recall directly.
- **0.715 % of targets truncated at a 640 cap**, versus BanglaT5's 0.05 % at **512**. mT5 needs
  more tokens to say the same Bengali, so it both truncates more and generates less.

## Trajectory

| step | 250 | 500 | 750 | 1000 | 1250 | 1500 | 1750 | 2000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .6758 | .7006 | .7103 | .7168 | .7269 | .7325 | .7344 | .7434 |

| step | 2250 | 2500 | 2750 | 3000 | 3250 | 3500 | **3750** | 4000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .7440 | .7454 | .7507 | .7515 | .7512 | .7538 | **.7558** | .7549 |

Still climbing at 4,000 — same as every other arm in this program. **But it is climbing from
behind and the gap is not closing**: at every step from 1,000 onward it trails
`E18/banglat5` by 0.02–0.03, and both curves flatten together. Extending the budget would not
change the ranking.

## Verdict

- **What it must beat:** incumbent 0.7724 / 0.7324
- **Result:** ❌ **−0.0161**
- **What it changes:**
  - **The measured tokenizer handicap is confirmed as a real score deficit**, not just a token
    count. mT5 needs 88 % more tokens for the same Bengali output; here it also truncates 14×
    more targets at a larger cap and generates 8 tokens short of the reference length.
  - **E10 (trim mT5's vocab to the ~23k tokens this corpus uses) is not worth running on this
    evidence.** Trimming addresses parameter count, not the fragmentation that is costing the
    score — mT5 already had 2.35× the parameters and still lost.
  - E09 stays, but only as the architecture-independence half of `E09 − E08`.
- **Row-level disagreement with the incumbent:** pending — `13_disagreement.py` against
  `E18/banglat5/dev.json`. This is the interesting pairing: a *different pretraining corpus and
  vocabulary* is a better source of uncorrelated errors than another seed.

## Anything surprising

Nothing broke. The interest is that mT5's deficit shows up in the **data** before training: the
truncation audit (`code/10_truncation_report.py`) predicted it from token counts alone, and the
trained model's output length confirmed it. Worth remembering as a cheap pre-screen — a tokenizer
that needs 88 % more tokens for the target language can be ruled out before a GPU is booked.
