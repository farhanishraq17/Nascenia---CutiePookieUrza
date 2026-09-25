# Fine-Tuning Log — all BanglaT5 runs

Every fine-tuning run, its exact configuration, and its measured result. One folder per run,
holding the notebook, the `.py` code it actually executed, and its results.

**Judge runs on Token F1 / ROUGE-L, never the local composite** — that composite is
mis-calibrated by ~0.118 because the organizers' BERTScore model is unknown. Predict the
leaderboard instead with:

```
LB ≈ 0.4672 + 0.3·TokenF1 + 0.2·ROUGE-L
```

Verified exactly against submission 1: `0.4672 + 0.3(0.2669) + 0.2(0.1564) = 0.5785` vs actual **0.57849**.

**Predictor refined 2026-08-06** after a second leaderboard anchor. BERTScore is *not* constant
across quality — it moved 0.9343 → 0.9442 between the constant string and the register-transfer
model. Use:

```
LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L
```

which fits **both** anchors to within 0.0001 (0.57857 vs 0.57849 · 0.85037 vs 0.85030). The older
`0.4672 + 0.3·F1 + 0.2·RL` under-predicts increasingly as quality rises — it cost 0.0049 on the
0.85030 submission. `pred LB` in the table below is still the *old* formula for runs recorded
before this date; treat it as a lower bound.

### Bars to beat

| Reference | Token F1 | ROUGE-L | LB |
|---|---|---|---|
| **Register transfer, seed 11 — CURRENT #1** | **0.7724** | **0.7324** | **0.85030** *(actual)* |
| Draft + 3 regexes, no model (ALIGN-01) | 0.5984 | 0.5482 | 0.7564 |
| Constant string *(previous #1)* | 0.2669 | 0.1564 | 0.57849 *(actual)* |
| Frequency-only constant, no model (CONST-OPT-01) | 0.3519 | 0.1318 | — |
| Two real doctors, same question (CEILING-01) | 0.3557 | 0.2561 | ~0.63 |

**CEILING-01 is not a ceiling on this task.** It bounds a model that writes its *own* answer.
The register-transfer route reconstructs *the same* answer from a second translation, and beats it
by 0.42 Token F1. Quote it only for the question→answer strategy class.

---

## Results

Ranked by Token F1. All dev numbers are the 300-row subset with 4-beam search, as logged by the run.

| # | Run | Seed | lr | ep | eff-batch | extra | **Token F1** | ROUGE-L | dev loss | pred LB | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | **C-lr1e3** | 7 | **1e-3** | 2 | 64 | — | **0.2576** | **0.1776** | **2.016** | **0.5800** | done |
| 7 | **E-lr1e3-4ep** | 99 | **1e-3** | 4‡ | 64 | — | 0.2539 | **0.1787** | 2.067 | 0.5791 | done |
| 8 | **F-batch32** | 555 | 3e-4 | 2 | **32** | — | 0.2442 | 0.1746 | 2.220 | 0.5753 | done |
| 3 | **A-lr3e4** | 42 | 3e-4 | 2 | 64 | *reference arm* | 0.2365 | 0.1705 | 2.212 | 0.5722 | done |
| 6 | **D-smooth** | 2024 | 3e-4 | 2 | 64 | `label_smoothing 0.1` | 0.2360 | 0.1670 | 3.441* | 0.5714 | done |
| 2 | `1337seed` | 1337 | 3e-4 | 2 | 64 | — | 0.2321 | 0.1666 | 2.223 | 0.5701 | done |
| 1 | `0.42seed` (TRAIN-01) | 42 | **1e-4**, warmup 1000 | 2 | 64 | — | 0.2051 | 0.1433 | — | 0.5574 | done |
| 9 | **G-lr3e3** | 21 | **3e-3** | 2§ | 64 | — | 0.2390 | 0.1706 | 2.145 | 0.5730 | done — **LR optimum found** |
| 4 | **B-4epoch** | 1337 | 3e-4 | **4** | 64 | — | *cancelled* | | | — | cancelled, not re-queued |
| 10 | **XFER-s11** | 11 | 1e-3 | 2 | 64 | **register transfer** | **0.7724** | **0.7324** | **0.603** | **0.8454** | **LB 0.85030** |
| 11 | **XFER-s23** | 23 | 1e-3 | 2 | 64 | **register transfer** | **0.7723** | **0.7332** | 0.605 | 0.8455 | done — replicate |

\* D's loss is not comparable — label smoothing inflates the cross-entropy by construction.
† A completed in 377.9 min. Its best checkpoint is **step 3000 (epoch 1.89)** only because that
was the last eval before training ended at step 3180 — the run is finished, not truncated. Note it
was **still climbing** at its final eval, so at eff-batch 64 a 2-epoch budget (3,180 steps) ends
just short of convergence.
‡ E was configured for 4 epochs but stopped at **step 3,500 / epoch 2.20** after 480 min. That is
still decisive — see below — because its peak came at step 2,000 and it declined for 1,500 steps after.
§ G **early-stopped cleanly at step 1,500 / 3,180 (47%) with `exit 0`** after 212 min. It peaked at
step 750 and declined through three further evals, so early stopping cut it off — saving ~3.5 GPU-h.
A complete result, not a truncated one.

### LR TUNING IS CLOSED — 1e-3 is the optimum, and the curve turns over

| lr | eff-batch | peak Token F1 | **peak step** |
|---|---|---|---|
| 1e-4 *(+31% warmup)* | 64 | 0.2051 | — |
| 3e-4 | 64 | 0.2365 | *still climbing at 3,000* |
| 3e-4 | 32 | 0.2442 | ~3,000 |
| **1e-3** | 64 | **0.2576** | **2,000** |
| **3e-3** | 64 | **0.2390** ↓ | **750** |

**G is the first arm to come in *below* its predecessor.** The monotone rise 1e-4 → 3e-4 → 1e-3
**turns over at 3e-3**, so 1e-3 is a genuine maximum rather than a lower bound. The "try 1e-2 next"
branch is dead; there is no further LR arm worth a GPU slot.

**And the peak-moves-earlier law now has three clean points:** 3e-4 → beyond 3,000 · 1e-3 → 2,000 ·
3e-3 → **750**. Raising the LR pulls the peak earlier *and*, past the optimum, pulls it lower.

**Early stopping paid for itself here.** G reached its best at step 750 and was terminated at 1,500
instead of running to 3,180 — a wrong-LR arm cost 212 min instead of ~425.

**F's authoritative number is 0.2442, not 0.2444.** `run.json` records the *best checkpoint*
(step 3,000, chosen on composite); the trajectory's step-4,000 eval read 0.2444 on Token F1 alone
but lost on composite. Earlier notes quoting 0.2444 are off by 0.0002 — immaterial, but the
`run.json` value is the one to cite.

### XFER — the register-transfer task behaves completely differently from question→answer

`input = external Bengali draft` → `target = competition-register answer` (ALIGN-01). Same base
model, same LR, same batch — **+0.51 Token F1 over the best question→answer arm.**

| step | epoch | Token F1 | ROUGE-L | loss | tokens |
|---|---|---|---|---|---|
| 250 | 0.16 | 0.6546 | 0.6084 | 1.122 | 101.5 |
| 1000 | 0.63 | 0.7497 | 0.7085 | 0.716 | 96.8 |
| 2000 | 1.26 | 0.7673 | 0.7263 | 0.630 | 98.8 |
| **2750** | **1.73** | **0.7724** | **0.7324** | 0.603 | 98.7 | ← best |
| 3000 | 1.89 | 0.7700 | 0.7300 | **0.599** | 99.0 |

**This overturns the peak-then-decline law for this task class.** Every question→answer arm
showed Token F1 peaking then falling while loss kept improving. Here **loss and the metric move
together the whole way**, and the curve never turns over.

The divergence was never a property of the model or the learning rate — **it was a property of the
task.** When the model must invent content, training longer makes it more confidently specific, and
specific-but-wrong is exactly what the metric punishes. When the answer is recoverable from the
input, there is nothing to over-commit to.

**Practical consequence: the "budget ~2,000 steps and stop" rule (§3b) does NOT apply here.** XFER
was still improving at step 2,750; more training may genuinely help. Confirm before assuming either
rule transfers to a new task shape.

**Seed replication is excellent:** seed 11 → 0.7724, seed 23 → **0.7723** (Δ 0.0001). Two
independent runs landing that close is strong Phase 2 reproducibility evidence.

**It also killed the ensemble, as predicted.** Pooled MBR over both seeds scored **0.7677 /
0.7268 → pred LB 0.8478**, i.e. **−0.0027 below the better single model**. Two reasons, both stated
before the run: the task is near-deterministic (sampling at T=0.8 adds noise where beam-4 is already
near-optimal), and a consensus selector given candidates that agree to 0.0001 has nothing to select
on. **MBR and the beam/length sweep are closed** — beam-4 at `min_new 80 / max_new 320 / lp 1.0` is
the shipped decoder. Detail: **MBR-01** in LOCAL_EXPERIMENTS.md.

**Despite the 0.0001 dev gap, the two seeds share only 34/1000 test rows (3.4%).** Near-identical
aggregate scores do **not** mean near-identical outputs — worth remembering before treating two
checkpoints as interchangeable.

### Noise floor: differences below ~0.005 Token F1 are meaningless
Three runs share the identical config (lr 3e-4 · 2 ep · eff-batch 64), differing only in seed:

| run | seed | Token F1 |
|---|---|---|
| `1337seed` | 1337 | 0.2321 |
| D-smooth *(+ label smoothing)* | 2024 | 0.2360 |
| A-lr3e4 | 42 | 0.2365† |

**Spread 0.0044 across seeds — which entirely contains D's label-smoothing "effect" of +0.0039.**
Label smoothing does nothing. C's +0.013 over F and +0.026 over A are 3–6× the noise floor, so
the LR effect below is real.

Warmup is 200 steps everywhere except TRAIN-01. Shared by every run: `csebuetnlp/banglat5`
(247,577,856 params) · **`transformers==4.57.3`** · single T4 · fp32 · Adafactor · 384/256 ·
`--no-group-by-length` · csebuetnlp normalizer · **data-split seed 42 / dev-size 5000**
(identical dev set — the precondition for comparing any of them).

### C-lr1e3 is the first model to beat the constant string

```
C:        0.4672 + 0.3(0.2576) + 0.2(0.1776) = 0.5800
constant: 0.4672 + 0.3(0.2669) + 0.2(0.1564) = 0.57849
                                               ------- 
                                                +0.0015
```

It wins **despite still losing on Token F1** (0.2576 vs 0.2669). ROUGE-L carries it: **0.1776 vs
0.1564, +0.021**. The constant string's word overlap is near-optimal by construction, but its word
*order* matches nothing; a real model produces sequences, and ROUGE-L is the component that pays
for that. The margin is thin enough that it is not yet worth a submission on its own — but it
means the model track is no longer behind, and MBR decoding now starts from ahead rather than behind.

---

## What has been established

### 1. Pin `transformers==4.57.3` — this was the root cause of eight failed runs
Kaggle ships **5.0.0**, on which T5 training reports nonsensical loss (~163 vs ~10), inflates the
parameter count to 296.9M via untied embeddings, and stalls. Proof it was never the code:
`diff FINE_TUNING_NOTEBOOKS/*/nascenia-code/02_train_t5.py NOTEBOOKS/02_train_t5.py` → **no output**.
Byte-identical. Only the pin differed.

### 2. The LR schedule was worth +0.039 Token F1
TRAIN-01 ran `lr 1e-4 / warmup 1000` — 1000 warmup steps out of only 3,180, so **31% of training
was spent ramping the LR from zero**. Correcting to `lr 3e-4 / warmup 200` took Token F1 from
**0.2051 → 0.2444** (arm F). TRAIN-01's weak result was a bad schedule, not a ceiling.

### 3. Learning rate is the dominant knob, and the trend is monotone — REVISED
Four runs at the same 2 epochs / 64 effective batch now isolate the LR:

| lr | eff-batch | Token F1 | dev loss |
|---|---|---|---|
| 1e-4 *(+ 31% of training spent in warmup)* | 64 | 0.2051 | — |
| 3e-4 | 64 | 0.2321 | 2.223 |
| 3e-4 | **32** *(2× the update count)* | 0.2444 | 2.220 |
| **1e-3** | 64 | **0.2576** | **2.016** |

Strictly increasing, with **no sign of the top yet**, and loss falls in step with the metric — so
this is genuine learning, not the loss/metric divergence seen within a single run. Halving the
batch at fixed LR (F) buys +0.012, which is the same lever from the other side: **more effective
optimisation.** Nothing about the shape of these numbers says 1e-3 is the maximum.

**This supersedes the earlier "plateau at 0.244" reading**, twice over.

First, that plateau was a plateau **at that learning rate**, not a ceiling on the model — raising
the LR raised the level. Second, arm A shows **the axis is optimizer steps, not epochs**: A is
still climbing at epoch 1.89 where F was flat from epoch 0.94, but at equal *step* counts they
agree closely —

| step | A (eff-batch 64) | F (eff-batch 32) |
|---|---|---|
| 3000 | 0.2365 | 0.2442 |
| 4500 | — | 0.2396 |

F only *looked* like it converged after one epoch because at batch 32 an epoch is 3,180 steps.

### …and C's own trajectory shows the level is a *peak*, not a plateau

| step | epoch | Token F1 | ROUGE-L | loss | tokens |
|---|---|---|---|---|---|
| 500 | 0.31 | 0.2247 | 0.1673 | 2.391 | 83.9 |
| 1000 | 0.63 | 0.2358 | 0.1663 | 2.173 | 88.7 |
| 1500 | 0.94 | 0.2539 | 0.1763 | 2.079 | 99.1 |
| **2000** | **1.26** | **0.2576** | **0.1776** | 2.016 | 103.4 | ← best checkpoint |
| 2500 | 1.57 | 0.2533 | 0.1779 | 1.981 | 98.9 |
| 3000 | 1.89 | 0.2510 | 0.1763 | **1.964** | 102.4 |

**C peaks at step 2000 and then declines, while loss keeps falling to its lowest value.** The
loss/metric divergence is not a curiosity of one arm — it is the general shape, and at lr 1e-3 it
turns actively harmful rather than merely flat. Corrected statement:

> Token F1 tracks **optimizer updates × learning rate**, not epochs. Each LR rises to its own
> **peak** and then degrades while loss continues to improve. **A higher LR reaches a higher peak,
> sooner** — A (3e-4) was still climbing at step 3000, C (1e-3) topped out at 2000.

**This demotes arm E.** E is lr 1e-3 × 4 epochs = 6,360 steps — three times past the point where C
already started degrading. `load_best_model_at_end` will retain its best checkpoint, so **E should
land at or just under C, and its most likely value is as confirmation rather than improvement.**
The earlier note calling E "the only arm that can still move the number" was written before C's
trajectory was available and is superseded.

**It also changed arm G.** Since the peak moves earlier as LR rises, at 3e-3 it may fall between
two 500-step evals and never be checkpointed. G now evaluates **every 250 steps** — ~28 min of
extra eval on a ~6.5 h run, against the risk of never saving the best model.

### 3b. Arm E settles it — duration is dead, and the peak position is reproducible

E is C's learning rate run longer (seed 99, lr 1e-3, stopped at step 3,500 / epoch 2.20, 480 min):

| step | epoch | Token F1 | ROUGE-L | loss | tokens |
|---|---|---|---|---|---|
| 500 | 0.31 | 0.1572 | 0.1256 | 2.791 | 109.1 |
| 1000 | 0.63 | 0.2383 | 0.1718 | 2.310 | 83.1 |
| 1500 | 0.94 | 0.2434 | 0.1773 | 2.152 | 93.0 |
| **2000** | **1.26** | **0.2539** | **0.1787** | 2.067 | 101.2 | ← best checkpoint |
| 2500 | 1.57 | 0.2469 | 0.1726 | 2.011 | 100.5 |
| 3000 | 1.89 | 0.2434 | 0.1683 | 1.963 | 100.8 |
| 3500 | 2.20 | 0.2393 | 0.1695 | **1.932** | 102.9 |

**Two things are now confirmed rather than inferred:**

**① Extra duration buys nothing.** E 0.2539 vs C 0.2576 — a gap of **0.0037, inside the 0.0044
noise floor**. Two seeds at lr 1e-3 land in the same place regardless of how long they run. The
prediction made from C's trajectory ("E should land at or just under C — confirmation, not
improvement") holds exactly.

**② The peak position is a property of the learning rate, not of the seed.** C and E — different
seeds, different durations — both peak at **step 2,000**, and both decline monotonically after
while loss keeps falling to its minimum. E carries the decline 1,500 steps further than C did
(0.2539 → 0.2393), so past the peak the damage keeps accruing.

**Operationally this closes the epoch question.** At lr 1e-3 the useful budget is **~2,000 steps**,
not 2 epochs and certainly not 4. A run costs ~6.5 h; the part that matters is the first ~4 h. Any
future arm at this LR should budget **2,500 steps with eval every 250** and stop, freeing GPU hours
for a different question.

### 4. Label smoothing 0.1 (arm D): no effect, within seed noise
D 0.2360 vs its exact comparator `1337seed` 0.2321 — **+0.0039**, smaller than the seed spread we
are about to measure with arm A. No evidence of benefit. Do not spend another arm on it.

### 5. A fine-tuned model has now caught the constant string — on ROUGE-L, not Token F1
| | Token F1 | ROUGE-L | pred LB |
|---|---|---|---|
| TF-IDF retrieval (BASE-02) | 0.2047 | 0.1254 | 0.5537 |
| TRAIN-01 fine-tuned | 0.2051 | 0.1433 | 0.5574 |
| F-batch32 | 0.2444 | 0.1746 | 0.5754 |
| **Constant string** *(current #1)* | **0.2669** | 0.1564 | 0.57849 |
| **C-lr1e3** | 0.2576 | **0.1776** | **0.5800** |

TRAIN-01 landed **within 0.0004 of retrieval** — the same mechanism: both emit *specific* content,
the constant emits *generic* content, and specific-but-wrong loses more precision than it gains in
recall. That still holds on Token F1, where **no model has yet passed 0.2669**. What changed is
that ROUGE-L rewards ordered subsequences, which a constant cannot produce, and that component is
worth 0.2 of the score. The model wins the composite while still losing the bag-of-words.

**Remaining lever: MBR decoding**, which selects the candidate nearest the consensus of the model's
own samples — structurally biased toward the generic centre where the points are, i.e. aimed
squarely at the Token F1 gap that is still open. It now sits on a model worth decoding well.

### 6. Length is not the problem
Output length self-corrects during training (109 → 122 → 93 → 91 tokens), converging on the
~100-token reference without intervention. C runs longer at 103.4 tokens and scores highest, so
there is no length penalty to tune around.

### 7. `checkpoint_hash` in `run.json` is not a valid run identity — Phase 2 risk
`sha256_dir` ([`02_train_t5.py:102`](scripts/kaggle/nascenia-code/02_train_t5.py)) hashes **file names and sizes
only, never file contents.** Every BanglaT5 checkpoint therefore has the same layout and the same
hash. Observed collisions:

| Reported hash | Runs claiming it |
|---|---|
| `9e3126b85e78323a` | F (seed 555), D (seed 2024), `1337seed` — three *different* models |
| `498e2e7cbeb06445` | C (seed 7), and every 1,000-row `smoke` run |

C's real 393-minute checkpoint and a 2.6-minute smoke test report identical hashes. The field is
worthless as evidence and **must not be cited in the Phase 2 reproducibility bundle** — the
`run.json` config block plus the archived notebook are the real identity. Fix the function to hash
`f.read_bytes()` before any further runs; already-finished checkpoints must be re-hashed from the
downloaded weights.

---

## Folder contents

Each `N) Bangla-T5-*` folder holds:

| File | What it is |
|---|---|
| `*.ipynb` | the exact notebook that was pushed and run |
| `kernel-metadata.json` | Kaggle kernel config — account, inputs, GPU |
| `nascenia-code/*.py` | the `.py` files the run executed |
| `run.json` | final config + dev metrics + `checkpoint_hash` |
| `trainer_state_step*.json` | full eval trajectory (every 500 steps) |
| `prep_report.txt` | data-prep output, confirming an identical dev split |

**Checkpoints are not stored in the `N)` folders** — those hold metadata only. The weights live in
**`_run_outputs/`** (see below) and in each run's Kaggle output, attachable via `kernel_sources`.

**Do not copy `runs/smoke/` artifacts in.** The 1,000-row warmup writes its own `run.json` and
`checkpoint-63/trainer_state.json`; a naive glob copies them to the same destination names and
**silently replaces the real 400-minute record with a 2.6-minute one.** This already happened to
F's folder once and was caught by checking `run_name`/`seed` after the copy.

## Status of each folder — updated 2026-08-05

| Arm | Notebook | metadata | code | `run.json` | trajectory | prep report |
|---|---|---|---|---|---|---|
| **A** | yes | yes | run's own | genuine | steps 3000, 3180 | yes |
| B | yes | yes | from `NOTEBOOKS/` | **cancelled** — never ran to completion | no | no |
| **C** | yes | yes | run's own | genuine | steps 2000, 3180 | yes |
| D | yes | yes | from `NOTEBOOKS/` | *transcribed* | output not downloaded | no |
| **E** | yes | yes | run's own | genuine | steps 2000, 3500 | yes |
| **F** | yes | yes | run's own | genuine | steps 3000, 4500 | yes |
| **G** | yes | yes | run's own | genuine | step 1500 | yes |
| **XFER-s11** | yes | yes | run's own | genuine | steps 2750, 3180 | yes |
| **XFER-s23** | yes | yes | run's own | genuine | steps 3000, 3180 | yes |

**A, C, E and F are complete and verified** — each `run.json` was checked for `run_name`/`seed`
after copying, so none is a smoke-run substitution (see the warning above).

**Nine of eleven folders are complete and verified** — each `run.json` was checked for
`run_name`/`seed` after copying, so none is a smoke-run substitution (see the warning above).

**Two gaps remain:**
- **B** — **cancelled**, never completed, and deliberately not re-queued: arm E answered the
  duration question at a better learning rate. The folder keeps the notebook as a record of what
  was launched.
- **D** — the run finished but its ~2 GB output was never pulled. Its `run.json` is *transcribed*
  from the Kaggle log (carries a `_source` field saying so) and its `nascenia-code/` is a copy from
  `NOTEBOOKS/` rather than the run's own. Content is identical, but it is a reconstruction, not
  evidence. Fix with:

```bash
KAGGLE_API_TOKEN="$HOME/.kaggle/access_token.tashin" \
  kaggle kernels output tashintahir/nascenia-sweep-d-smooth -p _run_outputs/sweep/D
python KAGGLE_PUSH/build_ft_folders.py
```

---

## `_run_outputs/` — the downloaded weights (8.7 GB)

```
_run_outputs/
  sweep/{A,C,E,F,G}/runs/<run>/best/     the 5 question→answer arms
  xfer/tashin/runs/banglat5_xfer_seed11/best   THE 0.85030 MODEL — Phase 2 evidence
  xfer/salam/runs/banglat5_xfer_seed23/best    its seed replicate (0.7723)
```

**7 models, one `best/` per real run.** Each also keeps its `run.json` and the
`ckpt/checkpoint-*/trainer_state.json` eval trajectories (14 in total) — the weights around those
trajectories were pruned, the evidence was not.

**Pruned 2026-08-06: 31.55 GB** — 18.56 GB of 1,000-row smoke warmups and 12.99 GB of intermediate
`ckpt/checkpoint-*` weights superseded by `best/`. The prune asserted the 0.85030 model's file count
before and after.

**`xfer/tashin/runs/banglat5_xfer_seed11/best` must never be deleted** — Phase 2 requires
reproducing the leaderboard output from it. Mirrored on Kaggle as `didhitinahid/nascenia-xfer-ckpt`,
so two independent copies exist. The three question→answer arm checkpoints used for the earlier
submissions are also on Kaggle as `farhanishraqq/nascenia-ckpts`.
