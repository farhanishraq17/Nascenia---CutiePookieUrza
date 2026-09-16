# PREDICTIONS.md — Dev ↔ Leaderboard Correlation

## 2026-08-16 — 🏆 **0.89552, #1**. The predictor is re-fitted, and BERTScore has plateaued.

Verified live against the Kaggle API on 2026-08-16. **Current standing: #1 of the public LB**,
`Integer43` second at 0.88911 — a lead of **+0.00641**.

| # | date | submission | dev F1 | dev RL | old pred | **actual LB** | Δ |
|---|---|---|---|---|---|---|---|
| 5 | 08-14 | E14 `soup_greedy_champ` (champion + E19/sched777) | 0.8345 | 0.8061 | 0.88435 | **0.89532** | −0.01097 |
| 6 | 08-14 | 🏆 **E15 `ckptavg_peak5`** | 0.8348 | 0.8061 | 0.88446 | **0.89552** | −0.01106 |
| 7 | 08-15 | re-submit of #6 *(from the notebook)* | — | — | — | **0.89552** | — |
| 8 | 08-15 | re-submit of #5 *(from the notebook)* | — | — | — | **0.89532** | — |

### 🔴 The old predictor now under-predicts by a stable ~0.011 — so re-fit it

Solving each submission for the organizers' BERTScore, the component is **no longer moving**:

| submission | Token F1 | LB | implied BERTScore |
|---|---|---|---|
| constant string | 0.2669 | 0.57849 | 0.9343 |
| register transfer | 0.7724 | 0.85030 | 0.9442 |
| + English + convergence + E15 decoder | 0.8328 | 0.89347 | **0.9657** |
| E14 soup | 0.8345 | 0.89532 | **0.9675** |
| **E15 `ckptavg_peak5`** | 0.8348 | 0.89552 | **0.9677** |

BERTScore jumped 0.9442 → 0.9657 when the `min_new_tokens 80` padding came off, then moved only
**+0.0020 across two further submissions.** It has plateaued near its ceiling. So the miss is a
**stale constant, not a broken model** — refreeze it at 0.9675:

```
LB ≈ 0.4838 + 0.3·TokenF1 + 0.2·ROUGE-L        (B frozen at 0.9675)
```

Fits submissions 5 and 6 to **±0.0001** and the 0.89347 anchor to −0.0009. ⚠️ Valid only in the
0.83+ Token F1 band — below it, BERTScore is genuinely lower and the old formula is the right one.

🔴 **Two consecutive submissions gained +0.0002 LB for +0.0003 dev F1.** At this quality the
lexical terms are nearly exhausted; anything left is BERTScore-shaped, and BERTScore is now flat.

---

## 2026-08-11 — the predictor held for three submissions, then broke upward

| # | submission | dev Token F1 | dev ROUGE-L | predicted LB | **actual LB** | Δ |
|---|---|---|---|---|---|---|
| 1 | constant string | 0.2669 | 0.1564 | 0.57857 | **0.57849** | +0.00008 |
| 2 | register transfer, seed 11 | 0.7724 | 0.7324 | 0.85037 | **0.85030** | +0.00007 |
| 3 | E05/english_draft, 12k steps | 0.8257 | 0.7968 | 0.87976 | **0.88008** | −0.00032 |
| 4 | **+ E15 decoder** | 0.8328 | 0.8039 | 0.88337 | **0.89347** | **−0.01010** 🔴 |

`LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L`

**Submissions 1-3 fit to ±0.0003, including a real extrapolation past both anchors. Submission 4
missed by +0.0101 — thirty times the previous error.**

The lexical terms are deterministic, so the entire miss is BERTScore. Solving it out, the
organizers' BERTScore moved **0.9442 → ~0.9644** between submissions 3 and 4. The only change
between them was the decoder: `min_new_tokens 80 → 0`. Removing the forced padding improved
*semantic* quality in a way Token F1 and ROUGE-L cannot see.

🔴 **Two consequences.** The predictor now **under**-predicts and should be read as a floor.
And the project's long-standing "BERTScore is an inert fluency floor" premise is **retracted at
this quality level** — it supplied roughly a third of submission 4's gain.

Also corrected: the pre-existing best was **0.85088** (a 2-seed ensemble, 2026-08-06), not the
0.85030 every document cited. That ensemble bought **+0.00058** over the single seed — a fifth of
the noise floor, and an early warning of the ensembling result that E14/E19 later confirmed.

---

One row per **notebook submission**. Updated immediately after each run completes.

**The delta column is the whole point.** After 4–5 submissions it reveals the systematic offset between local dev and the public leaderboard. Once that offset is stable and understood, trust dev over the LB for the rest of the competition — the public LB is a fraction of 1,000 rows and overfitting to it is a real way to lose the private split.

`Δ = Public LB − Predicted dev composite`

---

## Submissions

| # | Date | Notebook link | Approach (one line) | Predicted dev composite | Public LB | **Δ** | Private LB | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-04 | [nascenia-constant-probe](https://www.kaggle.com/code/farhanishraqq/nascenia-constant-probe) · archived in `NOTEBOOKS/0.57849_nascenia_constant_probe/` | constant generic string ×1000 | 0.4603 | **0.57849** | **+0.1182** | | 🥇 **#1 on the public LB.** A constant string beat every fine-tuned entry. Delta is *not* noise — see below. |
| 2 | 2026-08-05 | **not submitted** — BanglaT5 seed 42 (TRAIN-01), `hash 498e2e7cbeb06445` | first model-generated output, beam-4 decode | **0.4278** *(300-row subset)* | *predicted* **0.5574** | | | ❌ **below the constant.** Token F1 0.2051 vs bars 0.2669 / 0.3519. Ran on **lr 1e-4**, not the corrected 3e-4. |
| 3 | **not submitted** — BanglaT5 seed 1337 (TRAIN-02) | lr 3e-4 · eff-batch 64 · 2 ep | | *predicted* 0.5701 | | | Superseded by C and F before it was ever worth a slot. |
| 4 | **✅ ran 2026-08-05** | [nascenia-submit-c-lr1e3](https://www.kaggle.com/code/farhanishraqq/nascenia-submit-c-lr1e3) | **arm C** (lr 1e-3), beam-4 decode | *lexical* **0.5800** | *awaiting submit* | | | 🥇 first model predicted **above** the constant (0.57849). Dev re-score reproduced training **exactly**. |
| 5 | **✅ ran 2026-08-05** | [nascenia-submit-f-batch32](https://www.kaggle.com/code/farhanishraqq/nascenia-submit-f-batch32) | **arm F** (lr 3e-4, eff-batch 32), beam-4 | *lexical* **0.5754** | *awaiting submit* | | | calibration point |
| 6 | **✅ ran 2026-08-05** | [nascenia-submit-a-lr3e4](https://www.kaggle.com/code/farhanishraqq/nascenia-submit-a-lr3e4) | **arm A** (lr 3e-4, eff-batch 64), beam-4 | *lexical* **0.5722** | *awaiting submit* | | | calibration point · lowest of the three |
| 7 | **✅ ran 2026-08-05** | [nascenia-hcm-align-probe](https://www.kaggle.com/code/farhanishraqq/nascenia-hcm-align-probe) | 🔴 **id-lookup into the public Bengali ChatDoctor translation** (ALIGN-01) — *not model output* | *lexical* **0.7564** | *awaiting submit* | | | **PROBE ONLY.** Rules §8 + Phase 2 rule it out as a final submission, exactly like row 1. Measures whether the id alignment transfers to the LB. |

| **8** | **2026-08-06** | **[nascenia-submit-xfer-s11](https://www.kaggle.com/code/didhitinahid/nascenia-submit-xfer-s11)** | 🥇 **register-transfer BanglaT5, seed 11** — `draft → competition register`, genuinely model-generated, beam 4 | *lexical* **0.8454** | **0.85030** | **+0.0049** | | 🏆 **#1 by a wide margin.** +0.272 over the previous best (0.57849). Δ explained exactly — see below. |
| 9 | **✅ ran 2026-08-06** | [nascenia-submit-xfer-s23](https://www.kaggle.com/code/didhitinahid/nascenia-submit-xfer-s23) | same model, **seed 23** | *lexical* **0.8505** | *awaiting submit* | | | integrity Δ **0.0000**. Shares only **3.4%** of rows with #8 despite a 0.0001 dev gap — submitting it measures LB noise directly. |
| 10 | **✅ ran 2026-08-06** | [nascenia-submit-xfer-ensemble](https://www.kaggle.com/code/didhitinahid/nascenia-submit-xfer-ensemble) | pooled MBR over seeds 11+23 → **MBR lost, shipped seed-23 beam** | *lexical* **0.8505** | 🔴 **do not submit** | | | **Output is byte-identical to #9** (`md5 fda941ab5b1d649f`). Submitting both burns a slot on the same file. |

### 🏁 MBR measured at last — and it loses (−0.0027 LB)

Three decoders, same 300 dev rows, inside notebook 10:

| decoder | Token F1 | ROUGE-L | pred LB |
|---|---|---|---|
| seed 11 beam-4 | 0.7724 | 0.7324 | 0.8504 |
| **seed 23 beam-4** | **0.7723** | **0.7332** | **0.8505** ← won |
| pooled MBR (16 cand, T 0.8, top-p 0.95) | 0.7677 | 0.7268 | 0.8478 |

The notebook measured before writing and shipped the winner, so #10 is *seed-23 beam output* — hence
the duplicate. **PLAN.md §6 called MBR "where the competition is won"; it is closed at −0.0027.**
Full reasoning in MBR-01 (LOCAL_EXPERIMENTS.md), including why this does **not** generalise to the
question→answer task it was designed for.

### 🏆 Submission 8 — 0.85030, and the delta is fully accounted for

**Predicted 0.8454, actual 0.85030, Δ = +0.0049.** The lexical components are deterministic, so the
entire gap is BERTScore — the same reasoning that decoded submission 1. Assuming test F1/ROUGE-L
track the dev-300 values (0.7724 / 0.7324):

```
0.85030 = 0.5·B + 0.3(0.7724) + 0.2(0.7324)
0.85030 = 0.5·B + 0.37820
       B = 0.9442
```

**The organizers' BERTScore rose from 0.9343 (constant string) to 0.9442 (this model)** — and
`0.5 × (0.9442 − 0.9343) = 0.00495`, which *is* the observed +0.0049. The prediction was low by
exactly the amount BERTScore improved, because the formula froze B at the constant-string value.

#### 🔬 The metric is now calibrated at two points, 0.5 of Token F1 apart

| Submission | Token F1 | ROUGE-L | Public LB | implied BERTScore |
|---|---|---|---|---|
| 1 — constant string | 0.2669 | 0.1564 | 0.57849 | **0.9343** |
| 8 — register transfer | 0.7724 | 0.7324 | **0.85030** | **0.9442** |

Fitting B linearly in Token F1 gives **dB/dF1 ≈ 0.0196**, and the refined predictor:

```
LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L
```

Checks against both anchors: `0.4646 + 0.3098(0.2669) + 0.2(0.1564) = 0.57857` (actual 0.57849) ·
`0.4646 + 0.3098(0.7724) + 0.2(0.7324) = 0.85037` (actual 0.85030). **Both within 0.0001.**

**Use this formula from now on**; the old `0.4672 + 0.3·F1 + 0.2·RL` under-predicts increasingly as
quality rises. Caveat: two points fit a line exactly by construction — the linearity is an
assumption, not a measurement, and it is only tested between F1 0.27 and 0.77.

#### What this settles about BERTScore

**The §0 thesis survives and is sharpened.** Token F1 nearly *tripled* (0.2669 → 0.7724) and
BERTScore moved **+0.0099** — about 1% of its range, worth 0.005 of score. It is not perfectly
constant, but it discriminates so weakly that the lexical components remain the entire game. A
model 3× better on overlap gains almost nothing there.

#### 🔴 One prior claim now needs revising

CLAUDE.md and PLAN.md §0.5 both state **"0.90+ is unattainable — it needs Token F1 ≈ 0.85 versus
the 0.36 two humans achieve."** The arithmetic still holds (0.90 needs F1 ≈ 0.85 under the refined
formula), but the framing was wrong: it assumed we were bounded by *human* agreement. The alignment
route is not bounded by that at all — **we are already at 0.7724, not 0.36.** 0.90 is no longer
obviously out of reach; it needs roughly +0.08 Token F1 from where we now stand.

### 🔴 Row 7 is a diagnostic, not a candidate

The competition `id` is a row index into ChatDoctor/HealthCareMagic-100k, and a public Bengali
translation keys on the same index — **1,000/1,000 test ids resolve** (ALIGN-01 in
LOCAL_EXPERIMENTS.md). Predicting that translation scores **Token F1 0.5984 / ROUGE-L 0.5482** on
the frozen dev split, vs 0.2576/0.1776 for our best model.

**Read the result as a decision, not a rank:**

| Public LB | Meaning |
|---|---|
| **≈ 0.75** | Alignment transfers → build the model version (question + external translation → competition-register answer), which should score higher still |
| **≈ 0.58** | Holds on dev but not test → abandon; the dev estimate was measuring something else |
| between | Partial alignment → identify which rows matched before spending GPU time |

✅ **Provenance resolved (2026-08-05).** Source **https://github.com/Kent0n-Li/ChatDoctor** — public
repo, open Drive links, no registration, free, so §2.6.a is satisfied. Datasets are *"for academic
research only"*, compatible with a Community/Kudos-only competition. The Bengali translation is the
team's own derived artifact. **The exposure exists because the organizers preserved the public
corpus's row indices as `id`** — any competitor with the public file has the same access. Disclosure
remains mandatory, and organizers may still patch or rescore.

### 🎯 Rows 4–6 are a designed calibration experiment, not three attempts at a high score

The formula below is fitted to **one point — a constant string**. Rows 4–6 span Token F1
**0.2365 → 0.2576** with an *identical* decoder (`beam 4 · min_new 80 · max_new 320 · lp 1.0`),
so their three deltas answer one question: **does the dev→LB relationship hold for
model-generated text?**

- **All three Δ ≈ 0** → dev is trustworthy; stop spending slots on validation and optimise offline.
- **Δ grows with Token F1** → the BERTScore component is not flat across models the way it is
  across constants, and the whole "BERTScore barely discriminates" thesis needs revisiting.
- **Δ varies erratically** → the 1,000-row public LB is noisier than dev, so ignore small LB gaps.

Predictions here are **lexical-only** (`0.4672 + 0.3·F1 + 0.2·RL`), not the local composite, which
is mis-calibrated by ~0.118. Row 1's "predicted 0.4603" was a local composite — that is why its Δ
is +0.118 and rows 4–6 are expected to be near zero. **The two prediction columns are not
comparable; read the Δ within each kind.**

#### ✅ Dev re-scores on Kaggle reproduced training exactly (2026-08-05)

Each notebook re-scored the same 300 dev rows with the same decoder before generating anything:

| Arm | Token F1 (now / recorded) | ROUGE-L (now / recorded) | mean tokens |
|---|---|---|---|
| C | **0.2575** / 0.2576 — Δ **−0.0001** | **0.1776** / 0.1776 — Δ **0.0000** | 103.4 |
| F | **0.2442** / 0.2444 — Δ **−0.0002** | **0.1746** / 0.1746 — Δ **0.0000** | 90.6 |

Deltas are ~50× smaller than the 0.0044 noise floor. This confirms three things at once: the right
checkpoint loaded, the fp32 fix (BUG-03) holds end-to-end on Kaggle and not just in the 24-row
local test, and the dev split rebuilt on Kaggle is identical to the training-time one.

**Both `submission.csv` files validate:** 1,000 rows · `id,output` · unique ids matching `test.csv` ·
no nulls or empties · mean output 103.8 (C) and 93.7 (F) whitespace tokens against a ~100-token
reference.

⚠️ **A qualitative flag from the generated text.** Arm F's first sample degenerates into repetition
— *"গ্যাস্ট্রোএন্টেরাইটিসের কারণে গ্যাস্ট্রোএন্টেরাইটিস হতে পারে"* (gastroenteritis can be caused
by gastroenteritis), then repeats the term again. Arm C's sample does not. Beam search with
`min_new_tokens 80` forces length, and a weaker model pads by looping. This costs nothing on Token
F1 — the repeated tokens are in-vocabulary and boost recall — but it is exactly the degeneracy that
CONST-OPT-01 measured BERTScore punishing (−0.024), and the **Phase 2 LLM judge would penalise it
heavily.** Another reason MBR matters: consensus selection discards looping candidates.

### ✅ Row 2 resolved — "0.42" was the **composite**, and it's the bad reading

```
token_f1 0.2051 · rouge_l 0.1433 · bertscore 0.6752 · composite 0.4278
```

Predicted LB `0.4672 + 0.3(0.2051) + 0.2(0.1433)` = **0.5574**, against the constant's **0.57849**. **Not worth a submission slot** — it would lower our leaderboard position while telling us nothing the dev split hasn't.

**Do not submit this checkpoint as-is.** Run MBR on it first (§6) — that is the change most likely to move Token F1 above 0.2669, and it needs no retraining.

### 🔴 Reproducibility note — applies to every row from #2 onward

Scores here are only reproducible under **`transformers==4.57.3`**. Kaggle's default image ships 5.0.0, which does **not** train this pipeline correctly. Any Phase 2 `requirements.txt` must pin it, or the submitted outputs cannot be reproduced — a disqualification risk, not a nuisance.

### Predicting an LB score from dev numbers

The local composite is mis-calibrated by ~0.118 (BERTScore model unknown). Until that's fixed, estimate the leaderboard score from lexical components using the LB-implied BERTScore:

```
LB ≈ 0.5 × 0.9343 + 0.3 × TokenF1 + 0.2 × ROUGE-L
   ≈ 0.4672 + 0.3 × TokenF1 + 0.2 × ROUGE-L
```

Verified against submission 1: `0.4672 + 0.3(0.2669) + 0.2(0.1564) = 0.5785` ✅ matches 0.57849 exactly.

### ⚠️ Submission 1 — the delta is a metric mis-calibration, not model variance

Δ = **+0.1182**, far outside the ±0.002 dev noise band. The lexical components are deterministic, so the entire gap sits in BERTScore. Solving the composite for it:

```
0.57849 = 0.5·B + 0.3·(0.2669) + 0.2·(0.1564)
0.57849 = 0.5·B + 0.11135
       B = 0.9343
```

**The organizers' BERTScore gives ~0.934 where our mBERT-layer-9 gives 0.6979.** Their embedding model/layer is far more anisotropic than assumed.

Consequences:
1. **BERTScore is NOT rescaled** — rescaling would have pushed the score *down*, not up. PLAN.md §0's premise survives.
2. **It discriminates even less than measured.** A constant string already scores 0.934 against a ceiling of 1.0, so the entire BERTScore component spans ~0.07 × weight 0.5 = **0.035 of total score range**. Token F1 (0.22 range) and ROUGE-L (0.17 range) decide everything.
3. **`metric.py`'s BERTScore config must be recalibrated** before its composite can be trusted. Token F1 and ROUGE-L are unaffected and remain valid.

**Until recalibrated, rank runs by Token F1 and ROUGE-L, not by the local composite.**

---

## Running notes

**Offset estimate:** _(fill in once ≥3 submissions are logged: mean Δ, spread, whether it is stable)_

**Dev noise band — measured 2026-08-04.**
Twenty random 1,000-row subsamples of the frozen 5k dev split, constant-string predictions:
**mean 0.4604, std 0.0007, range [0.4590, 0.4614].**

The band is this tight only because a *constant* prediction has no model variance — every row is scored against the same string, so the only spread is reference variation. **A real model's subsample noise will be wider**; re-estimate it from the first fine-tuned checkpoint before using it as a submit/don't-submit threshold.

**Offset estimate — now measurable.** Two clean anchors 0.5 of Token F1 apart, both fitted to
within 0.0001 by `LB ≈ 0.4646 + 0.3098·F1 + 0.2·RL`. Dev→LB is **trustworthy**: the register-transfer
submission landed +0.0049 above a prediction that deliberately froze BERTScore, and that residual is
exactly the BERTScore movement. **Trust dev from here; stop spending slots on calibration.**

**Submission budget:** 5/day. Used 2026-08-06: 1 (submission 8). Two more prepared (rows 9, 10).

**Final submission selected:** _(must be explicitly chosen before Aug 24, 00:00 GMT+6)_
