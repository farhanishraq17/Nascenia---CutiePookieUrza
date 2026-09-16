# E19_multiseed_ensemble — results

**13 arms, all landed.** Trained 2026-08-11 → 2026-08-14 on CHPC granite/notchpeak
(A800 40 GB, L40S, RTX A6000), bf16. See `../_slurm/README.md`.
Every number below was read from `*/run.json` and `*/dev*.json` on disk and re-derived from the
stored predictions against `../data/english_draft/dev.parquet` — all 25 recorded Token F1 values
reproduce to 4 decimals.

## 🔴 READ THIS BEFORE COMPARING ANY TWO NUMBERS IN THIS FILE

E19's arms are **not all scored on the same decoder.**

| record file | decoder |
|---|---|
| `dev_e15dec.json` | **E15 decoder** — beam 8, length_penalty 1.2, min_new_tokens 0, max_new_tokens 320 |
| `dev.json` | **OLD decoder** — beam 4, length_penalty 1.0, min_new_tokens 80, max_new_tokens 320 |
| `run.json` → `dev` | OLD decoder, written in-training on the 300-row eval subset |

Measured on identical weights across the 14 arms in this program that have both records, the E15
decoder is worth **+0.0074 mean (range +0.0056 … +0.0095)** — *larger than almost every effect
E19 measures, and larger than the 0.0044 noise floor.* **Never compare a `dev.json` number with a
`dev_e15dec.json` number.** The champion's own pair is 0.8257 (old) → **0.8328 (E15)**.

⚠️ `sched777` has **no E15-decoder record at all**. Its 0.8235 is an old-decoder number and cannot
be placed in the same column as `sched2468`/`sched31337`.

## 🔴 THE STRUCTURAL FACT: E19 contains TWO POPULATIONS, not thirteen seeds

Verified in every `run.json`. Everything else is identical — `csebuetnlp/banglat5`,
`../data/english_draft`, 768/512, lr 1e-3, adafactor, effective batch 64, 247,577,856 params.

| | **population A — "ten seeds"** | **population B — "the champion's schedule"** |
|---|---|---|
| arms | `seed7 11 21 23 42 99 314 555 1337 2024` | `sched777` `sched2468` `sched31337` |
| `max_steps` | **12,000** | **30,000** |
| `early_stopping_patience` | **5** | **8** |
| batch × accum *(`../_slurm/registry.py`)* | 32 × 2 | 8 × 8 |
| observed peak step | 8,250 – 11,500 | 11,750 / 14,500 / 12,000 |

**Population A never reaches the champion's convergence point.** The champion peaks at step 12,000;
patience 5 stopped **all ten** seeds before that — the latest peak in the population is 11,500, and
four peaked before step 9,500. The ten seeds are therefore not "the champion, reseeded" — they are
**the champion, stopped early, reseeded**. That single difference explains both results below.

## Checkpoints — 🔴 keep every arm, including the losers

🔴 **All 13 `best/` kept** (944 MB of weights each, verified on disk). None uploaded to Kaggle.

| Arm | `best/` | Token F1 **E15 dec** | Token F1 *old dec* | ROUGE-L | peak step | hours | ckpt hash (`run.json`) | GPU |
|---|---|---|---|---|---|---|---|---|
| `sched31337` | ✅ | **0.8332** | — | 0.8046 | **12,000** | 9.38 | `dbabe4d5a375177a` | L40S |
| `sched2468` | ✅ | **0.8331** | — | 0.8052 | **14,500** | 3.82 ⚠️ | `2e1e2172a36f30fd` | A800 |
| `seed11` | ✅ | 0.8319 | 0.8234 | 0.8031 | 9,750 | 5.87 | `94336739d00b6dd3` | A800 |
| `seed1337` | ✅ | 0.8317 | 0.8258 | 0.8032 | 11,500 | 6.39 | `08f777f9dddf196b` | A800 |
| `seed23` | ✅ | 0.8306 | 0.8221 | 0.8006 | 10,500 | 6.24 | `423cef2dc3176317` | A800 |
| `seed42` | ✅ | 0.8301 | 0.8245 | 0.8008 | 11,000 | 6.39 | `6f7b123614d8a759` | A800 |
| `seed2024` | ✅ | 0.8293 | 0.8227 | 0.8016 | 11,000 | 6.47 | `c3798305054e4185` | A800 |
| `seed21` | ✅ | 0.8286 | 0.8209 | 0.8002 | 8,250 | 5.14 | `0dec2fbb13196411` | A800 |
| `seed99` | ✅ | 0.8280 | 0.8204 | 0.7992 | 9,000 | 5.22 | `4bea1c9c5a75a061` | A800 |
| `seed314` | ✅ | 0.8272 | 0.8198 | 0.7987 | 9,500 | 5.57 | `1f885a5fd90c82f4` | A800 |
| `seed7` | ✅ | 0.8269 | 0.8195 | 0.7974 | 8,250 | 4.46 | `11a995ff168000ee` | A800 |
| `seed555` | ✅ | 0.8267 | 0.8200 | 0.7978 | 9,250 | 5.23 | `d1ba76607fccc0a6` | A800 |
| `sched777` | ✅ | **no record** | 0.8235 | 0.7937 *(old)* | 11,750 | 7.14 | `3e996d8bd4d93c88` | A800 |
| 🏆 *champion, for reference* | — | **0.8328** | 0.8257 | 0.8039 | 12,000 | 3.8 | `6f9d4d6756032397` | H100 NVL |

ROUGE-L is quoted on the same decoder as the Token F1 beside it. All arms: 300-row frozen dev
subset, `--seed 42 --dev-size 5000`, normalizer on.
⚠️ `sched2468`'s 3.82 h is **not a run time** — see *Anything surprising*.

**Why the losers matter too:** measured here, and the answer for E19 is **they do not help** —
see the pooling gate below. That is the finding, not a reason to delete them. All 13 stay.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | precision | GPU |
|---|---|---|---|---|---|
| `seed7` | 99.5 | 75.0 | 53.3 | bf16 | A800 40 GB |
| `seed11` | 99.7 | 75.0 | 53.0 | bf16 | A800 40 GB |
| `seed21` | 99.2 | 75.0 | 53.0 | bf16 | A800 40 GB |
| `seed23` | 99.2 | 75.0 | 51.7 | bf16 | A800 40 GB |
| `seed42` | 99.4 | 75.0 | 52.3 | bf16 | A800 40 GB |
| `seed99` | 99.2 | 75.3 | 52.3 | bf16 | A800 40 GB |
| `seed314` | 99.1 | 75.0 | 52.7 | bf16 | A800 40 GB |
| `seed555` | 99.3 | 75.0 | 52.3 | bf16 | A800 40 GB |
| `seed1337` | 99.5 | 75.0 | 52.7 | bf16 | A800 40 GB |
| `seed2024` | 99.4 | 75.0 | 52.7 | bf16 | A800 40 GB |
| `sched777` *(old dec)* | 100.7 | 75.0 | 54.7 | bf16 | A800 40 GB |
| `sched2468` | 99.8 | 75.0 | 52.7 | bf16 | A800 40 GB |
| `sched31337` | 99.8 | 75.0 | 53.0 | bf16 | L40S |

References: ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %.
Near the *draft's* rates (0.06 % / 0.00 %) ⇒ the model copied its input. Near the references' ⇒ it
learned the conversion. **All 13 arms are on-register**, and the spread across them (52–55 % on
`নাসেনিয়া`) is smaller than the gap to the draft by two orders of magnitude. Register is
saturated on this task; it is not a lever any of these arms move.

Truncation is a property of the shared dataset, not of the arm: `english_draft` cuts
**1.60 % of sources at 768** and 0.03 % of targets at 512 (20,000-row sample, BanglaT5 tokenizer;
`../_slurm/truncation_report.json` records 1.62 / 0.05 on its own sample). Identical for all 13.

## Trajectory

In-training evals every 250 steps, **old decoder**, 300-row subset (this is what early stopping saw).

**The three 30k-schedule arms — the shape that matters:**

| step | 2k | 4k | 6k | 8k | 10k | 11k | 12k | 13k | 14k | 14.5k | 16k |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `sched777` | .7880 | .8006 | .8147 | .8161 | .8197 | .8211 | .8220 | .8238 | — | — | — |
| `sched2468` | .7881 | .8062 | .8132 | .8160 | .8200 | .8237 | .8227 | .8225 | .8228 | **.8260** | .8230 |
| `sched31337` | .7888 | .8064 | .8122 | .8166 | .8217 | .8242 | **.8280** | .8248 | .8264 | — | — |

`sched777` peaks at **11,750** and early-stopped at 13,750; `sched31337` at **12,000**, stopped at
14,000; `sched2468` at **14,500**, stopped at 16,250. All three curves are **flat, not turning
over** — the post-peak decline is 0.0012 / 0.0031 / 0.0016, every one of them inside the 0.0044
noise floor. This independently reproduces E05's finding that convergence for this configuration
is ~12,000 and that what follows is a plateau, not degradation.

**Population A, peak step and where patience cut it:**

| arm | seed7 | seed21 | seed99 | seed555 | seed314 | seed11 | seed23 | seed42 | seed2024 | seed1337 |
|---|---|---|---|---|---|---|---|---|---|---|
| peak step | 8,250 | 8,250 | 9,000 | 9,250 | 9,500 | 9,750 | 10,500 | 11,000 | 11,000 | 11,500 |
| last eval | 8,750 | 9,500 | 10,250 | 9,750 | 10,250 | 11,000 | 11,750 | 12,000 | 12,000 | 12,000 |

**Peak step largely predicts final score.** Across the ten seeds, peak step vs E15-decoder
Token F1 correlates at **r = 0.68 (Spearman 0.68)**, and the four arms that peaked at 10,500 or
later are four of the top five. It is not clean — `seed21` peaked earliest (8,250) yet finished
mid-pack at 0.8286 — so *how long a seed happened to survive patience 5* is the dominant variable
here, with residual seed noise on top. Nothing about the seeds themselves is being measured.

## Verdict

- **What it must beat:** `EXPERIMENT.md` — the pooling gate (mean pairwise Token F1 between members
  **< 0.90**, or ensembling is abandoned) and the champion's 0.8328.
- **Result:** ❌ **the pooling gate FAILS**, and ➖ **no single arm beats the champion**.

### 1. The pooling gate fails — exactly as E14 predicted

Measured over the ten seeds, E15 decoder, 45 pairs, on the frozen dev-300:

| | |
|---|---|
| **mean pairwise Token F1 between the ten seeds** | **0.9298** (min 0.9217, max 0.9388) |
| the abandon line in the docs | 0.90 |
| E14's five-member *architecture* pool, for contrast | 0.8704 |
| best single member | 0.8319 (`seed11`) |
| per-row oracle | 0.8595 |
| oracle gain | +0.0276 |

`../E14_arch_ensemble/RESULTS.md` closed with the prediction *"ten seeds of one architecture should
show higher mutual similarity than 0.87, and if they do, E19's pooling gate will fail where this
one passed."* **It is 0.9298. The prediction was correct and the gate is failed.**
Adding `sched2468` and `sched31337` and the champion barely moves it (0.9239 over 13 members).

⚠️ Note the tension worth carrying forward: agreement is *above* the abandon line while the oracle
headroom (+0.0276) is *larger* than E14's (+0.0195). High agreement does not mean low headroom —
it means the disagreements are concentrated in few rows, so a selector needs to be right on a
small, hard subset rather than broadly right. Read the gate as "seed pooling is the wrong source
of diversity", not as "there is nothing left".

### 2. Only the 30k-schedule arms are useful weight-averaging partners

The weight-averaging measurements live in `../E14_arch_ensemble/RESULTS.md` (arms
`pair_seed*`, `pair_sched777`, `ch_31337`, `soup_*`) and are not restated here. The E19-side
conclusion, from that experiment's `soup.json` records:

- **Champion + a 30k arm is the only combination that does not lose.** Both such pairs land above
  the champion; both gains are inside the noise floor, so the honest reading is *"the only
  partners that are not harmful"*, not *"a win"*.
- **Champion + a 12k seed hurts.** Nine of the ten pairs score at or below the champion, mean
  **−0.0022**, worst **−0.0092** (`seed314`); the single positive is +0.0004, a quarter of the
  noise floor. Uniform averaging of all ten seeds is −0.0046.
- **Mechanism, and it follows directly from the two populations:** weight averaging needs members
  in the same basin at the same stage of training. The 12k seeds were stopped 500–3,750 steps
  short of the champion's peak, so averaging the champion with one of them **drags it back down
  its own trajectory**. `sched777/2468/31337` ran the champion's 30,000-step budget with the
  champion's patience and peaked where the champion peaked — which is precisely why they are the
  only ones that compose with it.

**This is the reason the three `sched*` arms exist and the reason they were worth the GPU time.**
Population A produced thirteen checkpoints' worth of storage and no usable partner.

### 3. No arm beats the champion

`sched31337` 0.8332 and `sched2468` 0.8331 sit **+0.0005 / +0.0003** above the champion's 0.8328
on the same decoder — an eighth of the noise floor. The ten seeds span **0.8267 – 0.8319**
(mean 0.8291, sd 0.0019); the best of ten is **0.0008 below** the champion.

- **What it changes:** the champion's 0.8328 is confirmed as a **real level, not a lucky draw** —
  it is at the top of a 13-sample distribution whose sd is 0.0019, and the two arms that matched
  its schedule matched its score. **Training-seed σ on this task is ≈ 0.002 Token F1**, well under
  the 0.0044 noise floor; a 0.005 effect is roughly 2.5 σ of seed noise, so single-arm claims below
  that size cannot be read.
- **Row-level disagreement with the champion (E15 decoder, dev-300):** 0.9127 – 0.9232 Token F1
  agreement across all 12 arms with an E15 record. The *strongest* arms are not the most similar —
  `sched2468` (0.9133) and `sched31337` (0.9157) agree with the champion *less* than `seed1337`
  (0.9232) or `seed2024` (0.9229) do, while scoring higher. Output diversity and weight-space
  compatibility are different axes here, and it is the second one that paid.

## Anything surprising

**1. `sched2468`'s recorded 3.82 h is a fragment, not a run time.** It trained across three jobs on
two GPU types: `_slurm/np/logs/E19-sched2468.out` (A6000, to ~step 8,250) → `re-sched2468.out`
(A6000, `resume: checkpoint-8250`) → `_slurm/logs_a800/sched2468.out` (A800, `resume:
checkpoint-9000`, the segment that wrote `run.json`). An earlier A800 attempt
(`_slurm/logs/nasc-E19-sched2468.out`) produced zero evals. `run.json`'s `train_minutes: 229.2` and
`gpu: A800` describe **only the final segment**. Do not use it in any cost table.
`sched31337` (9.38 h, single job on grn010/L40S) is the only clean 30k timing.

**2. `sched777` was never re-decoded on the E15 decoder.** Ten seeds and two sched arms have
`dev_e15dec.json`; `sched777` has only `dev.json`. Its 0.8235 is ~0.007 lower *for decoder reasons
alone*, and a reader scanning one column will read it as the worst arm in E19 when it is not
measured. Fixing this is one 6-minute decode.

**3. `sched31337` — the top-scoring arm in E19 — has no `test.json` and no `submission.csv`.**
It cannot be submitted or fed to a test-split ensemble without a decode pass. Every other arm has
one. (Only `seed11` and `seed1337` have `submission_e15.csv`, i.e. test predictions on the shipped
decoder.)

**4. 🔴 The `checkpoint_hashes` field inside every `dev*.json` / `test*.json` is not a weight
fingerprint and must not be used as one.** `code/04_decode.py:ckpt_hash()` hashes only *file names
and sizes*; `code/02_train_t5.py:sha256_dir()` hashes *contents*. The fix was applied to the
training script — its docstring even records the incident (*"three different sweep arms reported
the identical hash 9e3126b85e78323a"*) — and **not** to the decoder. The consequence is visible in
this repo right now: twelve of E19's thirteen arms, plus `E21/A2` and the E14 soups, all report
`114136fe6dcde4c8`, while `E05/main`, `E21/A1` and `E22/B` all report `5b96a2389190d5e5`. These are
collisions across unrelated weights. **Use `run.json`'s `checkpoint_hash`** (all 13 are distinct)
— which is what `EXPERIMENT.md` means by *"`checkpoint_hash` is not a run identity"*.

**5. The ten seeds cost 57.0 GPU-hours and bought a negative result.** They were commissioned
to supply ensemble diversity; they supplied 0.9298 agreement, a failed pooling gate, and ten
weight-averaging partners that all hurt. What they *did* buy is the measurement that makes every
other single-arm claim in this program readable: **seed sd = 0.0019**, ten samples, one
configuration. That number was not available before and it is why the 0.0044 floor is defensible.

**6. `seed42`'s decoder delta is the smallest in the program (+0.0056) and `A2`'s the largest
(+0.0095).** The E15 decoder's benefit is not uniform across weights, so "+0.007" is a mean and
not a constant that can be added to an unmeasured arm — which is the second reason `sched777`
should be re-decoded rather than adjusted on paper.
