# E07_no_truncation — results

Fill this in as arms land. **This file is the per-experiment record**; `../RESULTS.md` is only the
cross-experiment scoreboard. Anything surprising goes here, not there.

_single arm — 1280/768_

## Measured before the run: truncation was already nearly zero, so E07's ceiling is small

`code/10_truncation_report.py`, 20,000 sampled train rows per dataset, each dataset's **own**
training caps, csebuetnlp normalizer applied, tokenizer counts (not words):

| dataset | tokenizer | src cap | **% src cut** | src p95 | src max | tgt cap | **% tgt cut** | tgt p95 | tgt max |
|---|---|---|---|---|---|---|---|---|---|
| draft_only | banglat5 | 768 | **0.0 %** | 234 | 698 | 512 | **0.05 %** | 237 | 623 |
| english_draft | banglat5 | 768 | **1.62 %** | 603 | 1851 | 512 | **0.05 %** | 237 | 623 |
| question_draft | banglat5 | 640 | **0.37 %** | 387 | 1509 | 512 | **0.05 %** | 237 | 623 |
| **all_inputs** *(what E07 un-truncates)* | banglat5 | 1024 | **0.83 %** | 734 | 1925 | 512 | **0.05 %** | 237 | 623 |
| english_only | banglat5 | 640 | **0.25 %** | 368 | 1046 | 512 | **0.035 %** | 236 | 665 |
| question_only | banglat5 | 768 | **0.015 %** | 202 | 969 | 512 | **0.035 %** | 236 | 665 |
| draft_only | **mt5-base** | 640 | **0.95 %** | 455 | 1409 | 640 | **0.715 %** | 448 | 1217 |

**E07 raises the cap for 0.83 % of rows on the source side and 0.05 % on the target side.**
Even if every one of those rows were fixed perfectly, the headroom is a fraction of the 0.0044
noise floor. **Predict within noise, and read a positive result with suspicion** — at this
truncation rate a >0.0044 gain is more likely to be seed noise than recovered information.

The run is still worth having as the *measurement* that closes the question, but it should not
be treated as a live lever, and no other experiment's result should be discounted as
"truncation-limited".

Two things this also settles for the rest of the program:
- **The 512-token target cap costs nothing** (0.05 % of rows) — target length is not the
  constraint anywhere, on any input combination.
- **mT5 truncates ~14× more of its targets than BanglaT5** at a *larger* cap (0.715 % at 640 vs
  0.05 % at 512). Small in absolute terms, but it is the tokenizer handicap E08 exists to price,
  showing up in the data before a single step is trained.

## RESULT: prediction confirmed. **+0.0007 over E03 — inside noise. The question is closed.**

**Ran 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL, bf16.**

| | Input | caps | Token F1 | ROUGE-L | pred LB | hours |
|---|---|---|---|---|---|---|
| E03 | all inputs | 1024/512 | 0.8035 | 0.7727 | 0.8681 | 1.35 |
| **E07** | **all inputs** | **1280/768** | **0.8042** | **0.7733** | **0.8684** | **1.54** |
| Δ | *(un-truncating)* | | **+0.0007** | +0.0006 | | **+14 %** cost |

The pre-registered prediction above — *"predict within noise, and read a positive result with
suspicion"* — holds exactly. Raising the caps for 0.83 % of source rows and 0.05 % of target rows
bought 0.0007, one sixth of the noise floor, for 14 % more wall clock.

**Truncation is not a lever on this task and no result elsewhere in the program should be
discounted as "truncation-limited".** That is the value of this arm: it converts an untested
assumption into a measured zero.

## Checkpoints — keep every arm, including the losers

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `main` | `E07_no_truncation/main/best` | *(not uploaded)* | 0.8042 | 0.7733 | **3,250** | 1.54 | ckpt hash `6d05bc7a0fea3b27` · 247,577,856 params |

**Why the losers matter too:** a model that scores *below* the incumbent but **disagrees with it
usefully** is exactly what E14/E19 need and cannot get from another seed. MBR failed once because
two members agreed to 0.0001. Do not delete an arm because its number looked bad.

## Per-arm read-out

Record for every arm, not just the winner:

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `main` | 100.1 | 76.3 % | 53.3 % | **0 % / 0 %** *(that is the experiment)* | bf16 | H100 NVL |

References: ~100 tokens · `হেলো` 76.4% · `নাসেনিয়া` 50.0%.
Near the *draft's* rates (0.06% / 0.00%) ⇒ the model copied its input. Near the references' ⇒ it
learned the conversion.

## Trajectory

| step | 250 | 500 | 750 | 1000 | 1250 | 1500 | 1750 | 2000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .6540 | .7405 | .7575 | .7724 | .7780 | .7852 | .7877 | .7937 |

| step | 2250 | 2500 | 2750 | 3000 | **3250** | 3500 | 3750 | 4000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .7937 | .7976 | .8010 | .7990 | **.8039** | .8016 | .8020 | .8022 |

Flat from ~3,250 within noise — the flattest curve of any arm here, which is consistent with
un-truncated inputs simply having nothing more to give.

## Verdict

- **What it must beat:** E03 (0.8035), the same input at 1024/512
- **Result:** **+0.0007 — within noise.** The pre-registered prediction was correct.
- **What it changes:**
  - **Truncation is closed as a lever.** No experiment in this program is truncation-limited,
    and no future arm needs caps above its dataset's own.
  - The 512-token **target** cap is confirmed free across every BanglaT5 arm (0.05 % of rows).
  - Practical consequence: prefer the *smaller* cap that fits, since E07 cost 14 % more wall clock
    for nothing. `english_only` at 640 is the extreme version of the same point.
- **Row-level disagreement with the incumbent:** to be folded into the next `13_disagreement.py`
  pass — expected to be low, since E07 and E03 differ only by a cap that binds on <1 % of rows.

## Anything surprising

_Failures, crashes, OOMs, config changes forced by hardware, anything that would mislead a reader
of the numbers alone. Negative results belong here — they stop the same dead end being walked twice._
