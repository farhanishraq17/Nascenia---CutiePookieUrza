# E01_add_english — results

> ## 🔴 THIS IS THE CHAMPION'S CONFIG, MEASURED AT 4,000 STEPS — read this first
>
> **E01's configuration is the configuration behind the #1 leaderboard entry.** Diffing
> `main/run.json` against `../E05_train_to_convergence/english_draft/run.json`, the two runs are
> identical on every field that defines the model — `csebuetnlp/banglat5` · `data/english_draft` ·
> 768/512 · effective batch 64 · lr 1e-3 · adafactor · label smoothing 0.0 · seed 11 · bf16 ·
> 101,737 train rows · H100 NVL. **The only two differences are `max_steps` (4,000 vs 30,000) and
> `early_stopping_patience` (5 vs 8).**
>
> So **0.8032 is not what this configuration scores. It is what it scores after 4,000 steps** — and
> `main/ckpt/checkpoint-4000/trainer_state.json` shows `best_global_step = 4000 = max_steps` with
> the early-stopping counter still at **0**. Training stopped because the budget ran out, not
> because the model stopped improving.
>
> | the same config, run to | Token F1 | ROUGE-L | measured in |
> |---|---|---|---|
> | 4,000 steps — **everything below in this file** | 0.8032 | 0.7719 | `main/dev.json` |
> | convergence, shipped decoder (beam 4, lp 1.0, min_new 80) | **0.8257** | 0.7968 | `../E05_train_to_convergence/english_draft/dev.json` |
> | convergence + E15 decoder (beam 8, lp 1.2, min_new 0) | **0.8328** | 0.8039 | `../E05_train_to_convergence/english_draft/dev_e15.json` |
>
> The converged run peaked at step **12,000** and early-stopped at **14,000** with patience 8
> exhausted (`english_draft/ckpt/checkpoint-14000/trainer_state.json`), 3.8 h on an H100 NVL, ckpt
> hash `6f9d4d6756032397`. **Public LB 0.89347, #1.** Full write-up: `../E05_train_to_convergence/RESULTS.md`.
>
> **The 4,000-step budget alone costs +0.0224 Token F1 — 5× the 0.0044 noise floor — at the same
> decoder.** Every number in this file is a lower bound, and any Δ taken between a number here and
> a longer-trained arm is inflated or deflated by roughly that much.
>
> ⚠️ **What changes and what survives.** Both of E01's headline Δs move at convergence, and — unlike
> E04, whose "+0.0053 for the draft" evaporated — **both move in E01's favour**:
>
> | claim | at 4,000 steps | at convergence |
> |---|---|---|
> | vs the 0.85030 incumbent (0.7724) | +0.0308 | **+0.0533** (0.8257 − 0.7724) |
> | English isolated vs draft-only, matched state | +0.0220 *(in-training evals: 0.8027 vs `E05/main` 0.7807 @4,000)* | **+0.0246** *(decoded, same decoder: 0.8257 vs `E05/main` 0.8011 at its 15,250-step peak)* |
>
> ⚠️ The short run is not simply the long run truncated — its LR schedule is compressed into 4,000
> steps, so it is *behind its own long-schedule twin at the same step*: in-training Token F1 at step
> 4,000 is **0.8027** here versus **0.8077** in `english_draft`. A 4,000-step measurement therefore
> understates the config twice over.

**Ran 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL, bf16.** See `../_slurm/README.md`.

## ✅ VERDICT: the English source adds real information. **+0.0308 Token F1 over the incumbent.**

Six times the 0.0044 noise floor, and it is the largest single-arm gain the project has
measured since ALIGN-01 itself.

| | Token F1 | ROUGE-L | pred LB |
|---|---|---|---|
| 🏆 incumbent — BanglaT5, draft only, 384/256 | 0.7724 | 0.7324 | 0.85030 *(actual)* |
| **E01 — BanglaT5, english + draft, 768/512** | **0.8032** | **0.7719** | **0.8678** |
| Δ | **+0.0308** | **+0.0395** | **+0.017** |

`LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L`

⚠️ **Two variables moved vs the incumbent, so use the matched control.** E01 changes the input
*and* raises the caps from 384/256 to 768/512. **E05** (`draft_only` at the same 768/512) isolates
the input, at a matched 4,000-step budget and the same in-training eval:

| | Token F1 @4,000 |
|---|---|
| E05 — draft only, 768/512 | 0.7807 |
| **E01 — english + draft, 768/512** | **0.8027** |
| **English alone** | **+0.0220** — 5× the noise floor |

So of the +0.0308 headline, **+0.0220 is the English source** and the rest is the larger caps.
`E18/banglat5` re-runs the incumbent's exact 384/256 recipe and lands 0.7768 (0.0001 from the
submitted model at its peak step), so the pipeline is not the source of either gain.

## Checkpoints — 🔴 keep every arm, including the losers

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `main` | ✅ `E01_add_english/main/best` | *(not uploaded yet)* | 0.8032 | 0.7719 | **4000 = the last step** | 1.08 | ckpt hash `b0c37448ebc6f1c9` · 247,577,856 params |

`main/submission.csv` (1,000 test rows) is written, so this arm is submittable without a retrain.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `main` | 100.3 | **75.3 %** | **52.3 %** | 1.62 % / 0.05 % | bf16 | H100 NVL |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %; draft 0.06 % / 0.00 %.
**Every one of the three lands on the references' rates, not the draft's** — the model learned
the register conversion rather than copying its input. Length is on target too (100.3 vs ~100).

## Trajectory — 🔴 it peaked at the last step. It had not converged.

| step | 250 | 500 | 750 | 1000 | 1250 | 1500 | 1750 | 2000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .6819 | .7430 | .7590 | .7706 | .7551 | .7811 | .7864 | .7894 |
| loss | .971 | .697 | .633 | .575 | .592 | .533 | .516 | .495 |

| step | 2250 | 2500 | 2750 | 3000 | 3250 | 3500 | 3750 | **4000** |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .7913 | .7938 | .7969 | .7992 | .8013 | .8021 | .8022 | **.8027** |
| loss | .488 | .478 | .461 | .455 | .452 | .449 | .445 | **.444** |

**Monotone to the end — no turnover, and loss falls with the metric the whole way.** The
question→answer task's "budget ~2,000 steps and stop" rule does not transfer here, exactly as
E05's premise argued. The last 1,000 steps still bought +0.0035, so the 4,000-step budget is a
cap, not a convergence point.

## Verdict

- **What it must beat:** incumbent 0.7724 / 0.7324
- **Result:** ✅ **+0.0308** — well outside noise
- **What it changes:** English is not redundant given the Bengali draft. The incumbent had to
  *invert our translation and re-apply theirs* from a noisy intermediate; the English original is
  the common ancestor of both translations and evidently carries signal the draft lost.
  → **E03** (question + english + draft) is worth running; it already is.
  → **E04** (english only) prices whether the draft is redundant *given* English.
  → Every downstream experiment that trains on "the winner of Tier 1" should point at
  `data/english_draft`, pending E03 and E05.
- **Row-level disagreement with the incumbent:** not yet — `13_disagreement.py` needs E05's
  `dev.json`, which is still training.

## Anything surprising

🔴 **A decode bug found here, fixed, and worth remembering.** `04_decode.py --max-source-len`
defaulted to **384** while this arm trained at **768**, so the first scoring pass fed the model a
third of its input and reported **0.7994** instead of 0.8032. Nothing crashed and the CSV was
well-formed — the same failure shape as the fp16 trap (#20). The default is now `None` and the cap
is read from the `run.json` beside the checkpoint; the sbatch template passes it explicitly as
well. **Any arm decoded before this fix is an underestimate**, worst for the long-input arms
(E03 at 1024, E07 at 1280).

⚠️ The step-1250 dip (0.7706 → 0.7551) is the only non-monotone point and it recovers fully by
1500. Worth noting only because a 5-eval early-stopping patience would survive it and a 1-eval
patience would not.
