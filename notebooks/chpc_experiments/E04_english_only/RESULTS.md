# E04_english_only — results

> ## SUPERSEDED AT CONVERGENCE — read this first
>
> Everything below is a **4,000-step** measurement, and its headline "the draft is worth
> **+0.0053**" does not survive convergence. At 12,000 steps:
>
> | | Token F1 |
> |---|---|
> | english **only** (`E04/conv12k`) | **0.8277** |
> | english **+ draft** (E19 seeds @12k, mean) | ~0.8291 |
> | **difference** | **+0.0014 — INSIDE the 0.0044 noise floor** |
>
> **At convergence the Bengali draft is worth nothing measurable.** The decision table's
> *"E04 ≈ E01 ⇒ the draft is redundant given English ⇒ ship english-only"* condition, which the
> 4k numbers just missed, **is met once both arms are run to convergence**.
>
> `E04/conv12k`: `best/` kept · hash `f9b288aa5b29f886` · 0.8277 / 0.8002 (E15 decoder),
> 0.8219 / 0.7949 (old decoder) · peak step 9,500 · 6.46 h · RTX PRO 4000 Blackwell, bf16 ·
> 640/512 · register হেলো 75.0 % / নাসেনিয়া 55.0 %, 100.0 tokens · truncation 0.25 % / 0.035 %.
>
> The "+0.0053" figure was quoted repeatedly across this project — including as the reason
> not to build E21. The direction of that argument survives (it is now *weaker*, not stronger:
> the draft matters even less), but the effect size was **4× too large** and compared a
> converged arm against a non-converged one.

**Ran 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL, bf16.** See `../_slurm/README.md`.

## VERDICT: **English alone beats our Bengali draft alone.** The draft is worth only +0.0053.

This is the most consequential Tier-1 result after E01, and it inverts an assumption the whole
project has carried since ALIGN-01.

| input | Token F1 | ROUGE-L | pred LB | src p95 tokens | hours |
|---|---|---|---|---|---|
| **english only** *(E04, 640/512)* | **0.7979** | 0.7667 | 0.8651 | 368 | **0.82** |
| draft only *(E05 @4,000, 768/512 — matched budget)* | 0.7807 | 0.7430 | 0.8579 | 234 | — |
| english + draft *(E01, 768/512)* | 0.8032 | 0.7719 | 0.8678 | 603 | 1.08 |

- **English alone − draft alone = +0.0172.** Four times the noise floor. **The English original is
  a better input than our own Bengali translation of it.**
- **E01 − E04 = +0.0053.** Just outside the 0.0044 noise floor: given English, the Bengali draft
  adds something, but barely — and it costs **64 % more source tokens** (p95 603 vs 368) and 32 %
  more wall clock to get it.

## Why this matters more than a 0.0053 gap

The pipeline has always been *English → (our Google translation) → model → organizers' register*.
E04 removes the middle hop entirely and loses almost nothing. Two things follow:

1. **The draft is not the carrier of the signal — it is a lossy re-encoding of it.** Its 0.7807
   against English's 0.7979 says our translation *destroys* information that the model could
   otherwise use. It survives in E01 only as a small residual.
2. **The project's translation-quality anxiety was aimed at the wrong target.** E17 spent a full
   experiment asking whether a better translator would raise the ceiling, and closed with "keep
   Google". E04 reframes that: the draft's *quality* matters less than expected because the draft
   itself is nearly redundant. **E21's draft-robustness arms and any future E17-style
   re-translation should be re-costed against this** — insurance on a component worth 0.0053 is
   cheap insurance to skip.

**What this does NOT say.** It does not mean "ship english-only". E01 is still the highest
non-`all_inputs` score, the gap is outside noise, and Phase 2 reproducibility favours the arm with
the best number. It means the draft is a **weak** contributor whose cost/benefit is now known.

## Checkpoints — keep every arm, including the losers

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `main` | `E04_english_only/main/best` | *(not uploaded)* | 0.7979 | 0.7667 | **3,750** | 0.82 | ckpt hash `4accfa4f6352ea38` · 247,577,856 params |

`main/submission.csv` written. **The cheapest strong arm in the program** — 49 min of H100 for
0.7979, against E07's 92 min for 0.8042.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `main` | 100.1 | 76.0 % | 53.7 % | 0.25 % / 0.035 % | bf16 | H100 NVL |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %. On target on all three — notable
because this model **never sees a single Bengali token of input** and still reproduces the
corpus register exactly. The register is learned entirely from the targets.

## Trajectory

| step | 250 | 500 | 750 | 1000 | 1250 | 1500 | 1750 | 2000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .5561 | .7234 | .7460 | .7582 | .7700 | .7763 | .7827 | .7845 |

| step | 2250 | 2500 | 2750 | 3000 | 3250 | 3500 | **3750** | 4000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .7857 | .7902 | .7909 | .7950 | .7957 | .7964 | **.7986** | .7971 |

Still climbing at the budget's end — five for five across the program.

## Verdict

- **What it must beat:** E01 (0.8032). Decision table: *"E04 ≈ E01 ⇒ the draft is redundant given
  English ⇒ ship english-only; halves input length."*
- **Result:** **0.0053 below E01 — just outside noise.** The decision table's "≈" is not quite
  met, so english-only does not automatically ship, but the draft's contribution is now bounded
  and small.
- **What it changes:**
  - **Do not spend further effort on draft quality.** The component is worth 0.0053.
  - **If input length ever becomes the constraint** — a longer-context experiment, a decoder with
    a tight window, an ensemble that must fit many members — `english_only` is the arm to fall back
    on: 61 % of E01's source length for 99.3 % of its score.
  - Keep for E14: it reads a *disjoint* field set from the draft-only arms, so its errors should be
    among the least correlated in the pool.
- **Row-level disagreement:** to be folded into the next `13_disagreement.py` pass.

## Anything surprising

**A model that never reads Bengali input still hits the reference register exactly** (`হেলো` 76.0 %
vs 76.4 %, `নাসেনিয়া` 53.7 % vs 50.0 %, length 100.1 vs ~100). The register is not being copied
from a Bengali draft at all — it is learned from the 101,737 targets. That is worth remembering
before assuming any future input combination needs a Bengali source to sound right.
