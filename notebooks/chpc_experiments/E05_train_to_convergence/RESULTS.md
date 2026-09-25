# E05_train_to_convergence — results

**Ran 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL, bf16.** See `../_slurm/README.md`.

## ANSWER: the convergence point is **step 15,250** — 5.5× the incumbent's 2,750.

The incumbent stopped at 2,750 because a Kaggle session ran out, and the program has assumed ever
since that this was roughly the right budget. It was not.

| | Token F1 | ROUGE-L | pred LB | peak step |
|---|---|---|---|---|
| incumbent — same input, 384/256 | 0.7724 | 0.7324 | 0.85030 *(actual)* |  2,750 |
| **E05 — draft only, 768/512, run to convergence** | **0.8011** | **0.7645** | **0.8658** | **15,250** |
| Δ | **+0.0287** | **+0.0321** | **+0.016** | **5.5×** |

**+0.0287 from compute alone**, on the *weakest* input in the program. It ran 69 evals over
17,250 steps in **2.87 h** and early-stopped on patience 8. The decision table's top row —
*"still climbing at 10,000 ⇒ extend further; this task rewards compute more than anything else
tested"* — is the one that fired.

## Trajectory — this is the result, not the final number

| step | 250 | 1k | 2k | 3k | 4k | 5k | 6k | 7k | 8k |
|---|---|---|---|---|---|---|---|---|---|
| Token F1 | .6542 | .7473 | .7658 | .7756 | .7807 | .7836 | .7866 | .7914 | .7902 |
| loss | 1.115 | .708 | .623 | .564 | .544 | .529 | .511 | .503 | .497 |

| step | 9k | 10k | 11k | 12k | 13k | 14k | 15k | **15,250** | 16k | 17k | 17,250 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Token F1 | .7928 | .7911 | .7950 | .7968 | .7961 | .7982 | .7995 | **.8011** | .7988 | .8010 | .7977 |
| loss | .498 | .493 | .490 | .485 | .488 | .486 | .488 | **.488** | .497 | .489 | .488 |

Three things the shape says:

1. **Where the incumbent stopped (2,750) the curve is still steep.** Steps 2,750 → 8,000 buy
   +0.0146; 8,000 → 15,250 buy another +0.0109. **Two thirds of the run's gain came after the
   incumbent's budget ended.**
2. **It flattens but never turns over.** From ~12,000 the curve is noise-limited (.7961–.8011 over
   5,000 steps, a 0.005 band around the noise floor), and loss stops improving at ~.486–.490. It
   early-stopped because nothing beat 15,250 for 8 evals, not because it degraded.
3. **Loss and the metric agree here.** Both flatten together around step 12,000 — unlike the
   question→answer sweep, where one run's *lowest* loss coincided with its *worst* Token F1. That
   divergence was a property of that task, not of BanglaT5.

## Checkpoints — E05 is the exception: the trajectory checkpoints ARE the result

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `main` | `E05_train_to_convergence/main/best` | *(not uploaded)* | 0.8011 | 0.7645 | **15,250** | 2.87 | ckpt hash `7077b30bcc031165` · 247,577,856 params |

**69 intermediate checkpoints kept, 65 GB**, one every 250 steps — finer than the "every 2,000
steps" the README asks for, deliberately, because the 250-step grid is what located the peak. They
can be pruned to every 2,000 plus `best/` once the trajectory has been read; **do not prune before
E19 has chosen its budget from this curve.** `main/submission.csv` is written.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `main` | 99.6 | 75.0 % | 54.0 % | 0.0 % / 0.05 % | bf16 | H100 NVL |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %. On target. **Training 5.5× longer did
not push the model off-register** — the failure mode the "more epochs hurt" rule warned about does
not appear on this task.

## Verdict

- **What it must beat:** the incumbent's peak, 0.7724 / 0.7324 at step 2,750
- **Result:** **+0.0287**, peak at **15,250**
- **What it changes:**
  - **Every 4,000-step number in this program is a lower bound**, including E01's 0.8032 and
    E03/E07's 0.804. The whole Tier-1 table was measured at roughly a quarter of the productive
    budget.
  - **`E05/english_draft` — the same 30k budget on the Tier-1 winner — is the run that matters**,
    and it is in flight. It combines the two confirmed gains (+0.0220 English, +0.0287 compute).
    They will not simply add, but the ceiling for this program now sits above 0.81.
  - **E19's step budget is set: ~15,250** *(pending E05/english_draft, which may land elsewhere —
    the winner's convergence point is the one E19 should copy)*.
  - **Budget in steps, never epochs**, and set patience from the flattening point: the curve is
    noise-limited from ~12,000, so patience 8 × 250 steps was correctly sized. A patience of 3
    would have stopped at ~10,000 and cost 0.010.

## Anything surprising

**Compute on the weak input nearly matches information on the strong one.** E05 (draft only, 15,250
steps) = 0.8011; E01 (english + draft, 4,000 steps) = 0.8032. A 0.0021 gap — inside noise. The
project has spent its effort on *what the model reads*, and it turns out **how long it trains buys
almost the same thing.** Neither had been run to convergence before today, so the two levers had
never been compared on equal footing.

**Cost note for anyone repeating this:** the peak arrived at 2.87 h of H100 time. On the Kaggle
T4 this run would have taken **roughly 57 hours** — 4.75 twelve-hour sessions. The experiment was
not skipped out of oversight; it was genuinely unreachable on the original hardware.

---

# `english_draft` — THE CHAMPION. Public LB **0.89347, #1**.

This arm is the model behind the leaderboard entry and is **mandatory Phase 2 evidence**.
It was missing from this file entirely until 2026-08-13.

| | Token F1 | ROUGE-L | public LB |
|---|---|---|---|
| shipped decoder (beam 4, lp 1.0, min_new 80) | 0.8257 | 0.7968 | **0.88008** |
| **+ E15 decoder (beam 8, lp 1.2, min_new 0)** | **0.8328** | **0.8039** | **0.89347** |

Same weights for both rows — only decoding differs. That +0.0134 of leaderboard came from
deleting a stale `min_new_tokens 80` floor, and ~0.010 of it was **BERTScore**, which this
project had assumed was inert (see ../../PREDICTIONS.md for the retraction).

## Checkpoint

| | |
|---|---|
| path | `E05_train_to_convergence/english_draft/best` |
| checkpoint hash | `6f9d4d6756032397` |
| params | 247,577,856 — within the 3B cap |
| config | english_draft · 768/512 · effective batch 64 (32×2) · lr 1e-3 · adafactor · seed 11 |
| budget | max 30,000, patience 8 · **peak step 12,000** · early-stopped at 14,000 |
| hardware | H100 NVL, bf16, **3.8 h** |
| Kaggle | dataset `farhanishraqq/nascenia-e05-english-draft` · notebook `farhanishraqq/nascenia-e05-inference` |

**Phase-2 reproduction verified: the notebook regenerates the scored CSV 1000/1000 byte-exact**
on a T4 in fp32, despite the original being produced in bf16 on an H100.

## Per-arm read-out

| mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|
| 100.7 | 75.0 % | 53.3 % | **1.62 % / 0.05 %** | bf16 | H100 NVL |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %. On target on all three.
Note the truncation figure is **not** 0.0 % like the `main` arm — english_draft cuts 1.62 %
of sources at 768 (p95 603, max 1851). Measured in `_slurm/analysis/truncation.md`.

## Trajectory — plateau, not turnover

| step | 2,000 | 4,000 | 6,000 | 8,000 | 10,000 | **12,000** | 14,000 |
|---|---|---|---|---|---|---|---|
| Token F1 | .7906 | .8077 | .8172 | .8161 | .8219 | **.8268** | .8235 |

**Correction to this file's earlier claim.** The peak is at 12,000 with 8 further evals
after it, so the best checkpoint is *not* the last one. But the maximum decline after the peak
is **0.0037 — inside the 0.0044 noise floor**, so this is a plateau that early stopping cut,
**not** the loss/metric divergence seen on the old question→answer task. The "no turnover"
language elsewhere in this program should be read as "no *harmful* turnover".

## Verdict

- **Convergence for this input is step 12,000**, not the 15,250 measured on `draft_only`.
  The "E19's budget is set: ~15,250" line earlier in this file is **superseded** — E19 in
  fact ran at 12,000, which was correct.
- Combining the two confirmed gains (English +0.0220, convergence +0.0287) did not simply add:
  the champion sits at 0.8328 against a draft-only-at-convergence 0.8011.
- Verified independently: `E19/sched777`, given the same 30,000-step headroom, also peaked at
  **11,750** — so 12,000 is a property of the configuration, not of this seed.
