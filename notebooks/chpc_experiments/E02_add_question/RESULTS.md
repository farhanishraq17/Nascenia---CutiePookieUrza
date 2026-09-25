# E02_add_question — results

> ## A SECOND ARM EXISTS — `conv12k`, and it is NOT CONVERGED — read this first
>
> Everything from the dateline down is the **4,000-step** `main` arm. A 12,000-step `conv12k` arm
> ran on **2026-08-10** and is written up in its own section at the bottom of this file. Two things
> have to be read together:
>
> 1. **`conv12k` scores 0.7953 / 0.7599** (shipped decoder) against `main`'s 0.7734 / 0.7351 —
>    **+0.0219 from budget alone**, five times the 0.0044 noise floor. Most of the difference
>    between this file's arm and the arms it gets compared to was never about the input.
> 2. **`conv12k` never converged.** `conv12k/ckpt/checkpoint-12000/trainer_state.json` records
>    `global_step = 12000 = max_steps`, `best_model_checkpoint = conv12k/ckpt/checkpoint-11250`,
>    and an early-stopping counter of **3 of 8**. The run was cut off by its budget, not by its
>    own metric. Its two sibling conv12k arms **were** allowed to stop themselves: `E03/conv12k`
>    ended at 10,750 (best 8,750) and `E04/conv12k` at 11,500 (best 9,500), both with the counter
>    exhausted at 8/8.
>
> **`../_slurm/analysis/scoreboard.md` ranks E02/conv12k's 0.7953 in the same column as those
> genuinely-converged arms. It is not the same kind of number — it is a lower bound**, and the
> scoreboard's `peak step 11250` cell does not reveal it. Every Δ computed against E02/conv12k is
> therefore an **upper bound** on E02's deficit, not a measurement of it.
>
> The 4k verdict — *the patient question does not help* — **does survive at convergence**; the
> numbers are in "Does the 4k verdict survive?" at the end of this file. But no number quoted from
> `conv12k` should travel without the caveat above attached.

**`main` ran 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL, bf16;
`conv12k` ran 2026-08-10 on 1 × RTX PRO 4000 Blackwell, bf16.** See `../_slurm/README.md`.

## VERDICT: the patient question does NOT help. It is the weakest Tier-1 input tested.

| | Token F1 | ROUGE-L | pred LB |
|---|---|---|---|
| incumbent — draft only, 384/256 | 0.7724 | 0.7324 | 0.85030 *(actual)* |
| **E02 — question + draft, 640/512** | **0.7734** | **0.7351** | **0.8512** |
| E18/banglat5 — draft only, 384/256 *(this pipeline's replication)* | 0.7768 | 0.7389 | 0.8531 |
| **E01 — english + draft, 768/512** | **0.8032** | 0.7719 | 0.8678 |

**E02 − incumbent = +0.0010: inside the 0.0044 noise floor — no effect.**
**E02 − E01 = −0.0298: the question is worth nothing where English is worth a lot.**

Note E02 sits *below* the 384/256 draft-only replication (0.7768) despite reading strictly more
input at a larger cap. The gap is inside noise, but the direction is consistent: adding the
question is at best free and possibly a small distraction.

## Checkpoints — keep every arm, including the losers

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `main` | `E02_add_question/main/best` | *(not uploaded yet)* | 0.7734 | 0.7351 | **3750** | 0.84 | ckpt hash `930a70b38c3d0a8b` · 247,577,856 params |

**Kept deliberately even though it lost.** A model trained on a *different input field* is the
one member of the pool whose errors are not correlated with the others' — exactly what E14 needs
and cannot get from another seed. `main/submission.csv` is written.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `main` | 98.4 | **76.0 %** | **53.0 %** | 0.37 % / 0.05 % | bf16 | H100 NVL |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %; draft 0.06 % / 0.00 %.
The register is learned correctly — **this is not a broken run, it is a genuine negative.** The
model produces the right style, it simply has no extra information to convert.

## Trajectory

| step | 250 | 500 | 750 | 1000 | 1250 | 1500 | 1750 | 2000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .1087 | .6778 | .7167 | .7384 | .7480 | .7547 | .7597 | .7644 |
| loss | 3.113 | 1.012 | .871 | .754 | .714 | .688 | .671 | .646 |

| step | 2250 | 2500 | 2750 | 3000 | 3250 | 3500 | **3750** | 4000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .7658 | .7682 | .7686 | .7726 | .7734 | .7724 | **.7744** | .7741 |
| loss | .635 | .620 | .603 | .598 | .591 | .588 | **.584** | .583 |

Monotone, flattening after ~3,000. **Also no turnover** — three for three on that, across three
different input combinations. The step-250 value (0.1087) is warmup, not a result.

## Verdict

- **What it must beat:** incumbent 0.7724 / 0.7324, and E01
- **Result:** within noise of the incumbent, clearly below E01
- **What it changes:**
  - The 0.85030 model's one acknowledged blind spot — never reading the patient's question —
    **was not costing anything.** That is a real answer to a real open question.
  - **E03** (question + english + draft) is now expected to land at or just below E01: per the
    decision table, when one field dominates, *ship the shorter input*. E03 must beat E01 by
    >0.0044 to justify carrying a third field.
  - It does **not** follow that the question is uninformative in general — it is the only field
    the organizers guarantee at test time, so E13's multi-task arm (robustness insurance against
    the alignment route ever being closed off) keeps its rationale.

- **Row-level disagreement with the incumbent:** pending E05's `dev.json`; this arm is the most
  interesting one to measure, since a *different input field* is the likeliest source of
  genuinely uncorrelated errors.

## Anything surprising

The first eval (step 250) at Token F1 0.1087 with loss 3.11 is far worse than E01's 0.6819 at the
same step, and both use warmup 200. E02 simply starts from a harder place — a longer, noisier
input where the answer-bearing part (the draft) is now preceded by a question the model must
learn to ignore. It recovers by step 500 and never looks back.

This arm was decoded twice: once before the `04_decode.py --max-source-len` fix (which fed it
384 tokens instead of 640) and once after. The numbers above are the corrected pass. See
`../E01_add_english/RESULTS.md` for the bug.

---

# `conv12k` — the 12,000-step arm (2026-08-10)

**Ran 2026-08-10 on 1 × NVIDIA RTX PRO 4000 Blackwell, bf16, 422.9 min = 7.05 h.**

## It hit `max_steps`. Early stopping never fired. The number is a LOWER BOUND.

From `conv12k/ckpt/checkpoint-12000/trainer_state.json`, against the two conv12k arms it is
routinely ranked beside:

| | **E02/conv12k** | E03/conv12k | E04/conv12k |
|---|---|---|---|
| budget | `max_steps` 12,000 · 8 epochs · patience 8 | *identical* | *identical* |
| training stopped at step | **12,000 — `= max_steps`** | 10,750 | 11,500 |
| `best_model_checkpoint` | 11,250 | 8,750 | 9,500 |
| early-stopping counter at stop | **3 / 8** | 8 / 8 | 8 / 8 |
| epochs consumed (of the 8 allowed) | **7.55** | 6.76 | 7.23 |
| what ended the run | **the budget** | the metric | the metric |
| Token F1 (shipped decoder) | **0.7953** | 0.8246 | 0.8219 |

**E03 and E04 measured where their curves stopped improving. E02 measured where the clock ran
out.** Its best checkpoint is 750 steps from the wall; E03's is 2,000 steps back and E04's 2,000.

**Re-running this needs *two* caps lifted, not one.** At 1,590 optimizer steps per epoch, the
`num_train_epochs 8` cap binds at ~12,720 steps — only 720 past where `max_steps` stopped it.
Raising `max_steps` alone would buy under half an epoch. `E05/english_draft` and `E05/main` had
both caps set generously (30,000 steps / 19 epochs) and used 14,000 and 17,250 steps respectively.

**Honest bound on what is missing.** The in-training curve is flat over the last third:
0.7926 at step 8,000 → 0.7957 at the 11,250 peak, **+0.0031 across 3,250 steps — inside the
0.0044 noise floor.** The residual is probably small. But "probably small" is an estimate, and
this arm is currently being ranked against arms whose residual was *measured* to be zero.

## Checkpoints — keep every arm, including the losers

| Arm | `best/` kept? | Token F1 | ROUGE-L | pred LB | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `conv12k` | `E02_add_question/conv12k/best` | **0.7953** | 0.7599 | 0.8630 | **11,250** *(of a run cut off at 12,000)* | 7.05 | ckpt hash `b4bacffb770ea0ee` · 247,577,856 params |

**Config** (`conv12k/run.json`): `csebuetnlp/banglat5` · `../data/question_draft` · **640/512** ·
effective batch 64 · lr 1e-3 · adafactor · label smoothing 0.0 · seed 11 · eval every 250 ·
patience 8 · `max_steps` 12,000 · 8 epochs · torch 2.8.0+cu128.
**Hardware:** 1 × NVIDIA RTX PRO 4000 Blackwell, bf16, 422.9 min.

`conv12k/submission.csv` and `conv12k/submission_e15.csv` (1,000 test rows each) are both written,
so this arm is submittable under either decoder without a retrain.

Quote the hash from `run.json`, not from `dev.json`. The `checkpoint_hashes` field inside the
decode records is **not** a weights identifier — `5b96a2389190d5e5` appears in **27 different
decode records** across the program (E01/main, E02, E03, E04, E05/main, E06, E07, E18, E23 …),
and a second value, `114136fe6dcde4c8`, covers 26 more. Two arms sharing it are not the same model.

## Decoder

| decoder | Token F1 | ROUGE-L | mean output tokens | record |
|---|---|---|---|---|
| shipped — beam 4, lp 1.0, `min_new_tokens` 80 | 0.7953 | 0.7599 | 99.5 | `conv12k/dev.json` |
| **E15 — beam 8, lp 1.2, `min_new_tokens` 0** | **0.8023** | **0.7670** | 98.4 | `conv12k/dev_e15dec.json` |

Same weights, **+0.0070 Token F1 from decoding alone** — the same free gain E15 found on the
champion. (`pred LB` above uses the shipped-decoder row only: the
`LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L` fit is not calibrated for E15 decoding — on the
champion it predicts 0.8834 against an actual 0.89347.)

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `conv12k` (dev, 300 rows) | 99.5 | **75.3 %** | **53.0 %** | 0.37 % / 0.05 % | bf16 | RTX PRO 4000 Blackwell |
| `conv12k` (test, 1,000 rows) | — | 76.0 % | 50.4 % | — | bf16 | RTX PRO 4000 Blackwell |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %; draft 0.06 % / 0.00 %.
Truncation from `../_slurm/analysis/truncation.md` (`question_draft` at 640: src p95 387, max 1509).
**On register on every axis, and the 1,000-row test split lands closer to the references than the
300-row dev split does.** Three times the training budget changed the score and left the style
untouched — the register was already fully learned at 4,000 steps. As at 4k: **a genuine negative,
not a broken run.**

## Trajectory — flat, then cut off

In-training eval (300-row subset), every 1,000 steps plus the peak:

| step | 1000 | 2000 | 3000 | 4000 | 5000 | 6000 |
|---|---|---|---|---|---|---|
| Token F1 | .7480 | .7668 | .7726 | .7807 | .7832 | .7875 |
| loss | .715 | .622 | .579 | .554 | .533 | .518 |

| step | 7000 | 8000 | 9000 | 10000 | 11000 | **11250** | 12000 |
|---|---|---|---|---|---|---|---|
| Token F1 | .7902 | .7926 | .7899 | .7936 | .7921 | **.7957** | .7935 |
| loss | .516 | .510 | .508 | .502 | .500 | **.500** | .500 |

**Still no turnover** — the same finding the 4k arm reported, now over 3× the budget. Eval loss
sits between 0.4996 and 0.5005 for every eval from step 10,750 to the end, which is why the patience
counter had only reached 3: the metric kept ticking up by noise-sized amounts and kept resetting it.
That is exactly the regime in which a step cap silently substitutes for a convergence criterion.

## Does the 4k verdict survive? — yes

All rows below are decoded dev, 300 rows, shipped decoder (beam 4, lp 1.0, min_new 80):

| arm | input | Token F1 | ROUGE-L | converged? |
|---|---|---|---|---|
| `E05/english_draft` | english + draft | **0.8257** | 0.7968 | early-stopped 14,000, peak 12,000 |
| `E03/conv12k` | question + english + draft | 0.8246 | 0.7964 | early-stopped 10,750, peak 8,750 |
| `E04/conv12k` | english only | 0.8219 | 0.7949 | early-stopped 11,500, peak 9,500 |
| `E05/main` | **draft only** | **0.8011** | 0.7649 | early-stopped 17,250, peak 15,250 |
| **`E02/conv12k`** | **question + draft** | **0.7953** | 0.7599 | **NO — hit `max_steps` 12,000** |

- **vs English, the claim is unchanged.** question+draft − english+draft was **−0.0298 at 4,000
  steps**; at convergence it is **−0.0304** (0.7953 vs 0.8257), and **−0.0305** under the E15
  decoder (0.8023 vs 0.8328). A ~0.030 gap that does not move across a 3× budget change is the
  most robust thing in this file.
- **vs the matched draft-only control, the "small distraction" reading gets its first support —
  but it is confounded.** question+draft − draft_only at convergence is **−0.0058** (0.7953 vs
  `E05/main` 0.8011), just outside the 0.0044 floor, where at 4k the file could only say "inside
  noise". **Do not promote this to a finding.** `E05/main` was given 30,000 steps / 19 epochs
  and used 15,250; E02/conv12k was capped at 12,000 / 8 epochs. The comparison is exactly the
  program's known 4k-vs-convergence bug in miniature, one budget tier up. **−0.0058 is an upper
  bound on the question's cost.** The defensible statement remains the 4k one: *the question is
  worth nothing measurable, and is certainly not worth its tokens.*
- **vs the 0.85030 incumbent:** +0.0229 (0.7953 vs 0.7724) — which is the budget, not the input.
  Compare `E05/main`'s +0.0287 on strictly less input.

## Verdict

- **Result:** the 4k conclusion stands. Three times the compute moved question+draft from
  0.7734 to 0.7953 and left it **0.030 behind english+draft**, the same distance as before.
- **What it changes:**
  - **The scoreboard entry needs an asterisk.** `E02 | conv12k | 0.7953` is a lower bound sitting
    in a column of converged numbers. Fixing it means either re-running with `max_steps` **and**
    `num_train_epochs` lifted, or annotating the row — not silently comparing it.
  - **Nothing else needs re-deciding.** The question was already ruled out on the E01/E03 axis,
    and this arm's gap to English is stable at convergence, so the Tier-1 decision
    (`english_draft`) is untouched no matter which way the ~0.003 of missing budget falls.
  - Still worth keeping for E14: it is the only pool member that reads the patient question, so
    its errors remain the least correlated available — and the E15-decoder weights (0.8023) are
    what that pool should use.
- **Cost note:** 7.05 h on a Blackwell card for +0.0219, against E04/conv12k's 6.46 h for a
  number 0.0266 higher on a *shorter* input. This is the most expensive way the program has found
  to buy the second-lowest converged score.
