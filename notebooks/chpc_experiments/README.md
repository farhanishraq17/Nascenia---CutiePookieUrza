> **Repo note.** This is `fine_tune_project/README.md` as written for the cluster run; its "Current state" header is historical. In this repo: `code/` → [`scripts/pipeline/`](../../scripts/pipeline/) · `_slurm/` → [`scripts/chpc_slurm/`](../../scripts/chpc_slurm/) (analysis reports in [`_analysis/`](_analysis/)) · `data/` → not uploaded, see [`datasets/experiment_inputs/`](../../datasets/experiment_inputs/README.md) · `reference_notebooks/` → byte-identical copies in [`notebooks/phase1_kaggle_training/`](../phase1_kaggle_training/) · `../PHASE_2_EXP/E25` → superseded by [`notebooks/phase2_specialist/`](../phase2_specialist/README.md). Each `E*/` folder keeps its spec, results, notebook template and small run records; checkpoints and prediction dumps are not in git. The shipped model is `E15_decode_sweep/ckptavg_peak5` (LB 0.89552) — see [`REPORT.md`](../../REPORT.md).

# High-GPU Fine-Tuning Program — Nascenia Bengali Medical Dialogue

Self-contained. **1.8 GB**: data, source corpora, code and **20 experiment specs**. Nothing outside
this folder is required.

> ### Current state
> **This header is stale — see `PROGRESS.md` for the real current state
> (0.89552, #1, shipped model is `E15_decode_sweep/ckptavg_peak5`).** Kept as historical context
> for the wave plan below, not as a live status line.
>
> **Public LB 0.85030 — #1** *(superseded)*, +0.272 over the previous leader.
> BanglaT5 reading our Bengali draft of the answer and rewriting it in the competition's register.
> **Token F1 0.7724 · ROUGE-L 0.7324.**
>
> ### E25 — the current top priority, and it's a different kind of experiment than E01–E24
> Every experiment below optimizes **Phase 1** (the champion, register transfer from a
> ChatDoctor-id lookup). **That mechanism resolves on 0% of Phase 2's judging data** — the
> organizers' own private set, never ChatDoctor-derived (confirmed by the organizers directly).
> **E25 moved out of this program** — it now lives at `../PHASE_2_EXP/E25_phase2_specialist/`,
> a separate root-level folder, since it optimizes a different objective (Phase 2) with a
> different model entirely. It builds a **second model** (`swapnillo/Bangla-AI-1.7B`, fine-tuned +
> RAG) specifically to answer novel Bengali questions the champion was never trained to handle.
> The champion's checkpoint and its 0.89552 leaderboard number are **untouched** by E25 — see
> `PHASE_2_EXP/E25_phase2_specialist/EXPERIMENT.md` and `LOCAL_EXPERIMENTS.md`'s `PHASE2-GEN-01` entry for
> why this exists and what was already ruled out.
>
> This program exists because **every remaining lever needs more GPU-time than Kaggle's 12-hour
> session allows.** Each experiment below was either blocked by that ceiling or compromised by it.
>
> Re-tiered for **unlimited GPU**: experiments run in four parallel waves, two capacity
> experiments were removed, and three the fleet newly unlocks were added (E18, E19, E20).

---

## The task, in one paragraph

The competition data is a Bengali translation of ChatDoctor/HealthCareMagic-100k, and **the
competition `id` is that corpus's row index**. So for every row:

```
competition target = f_B(English)      the organizers' translation  ← what we are scored on
our draft          = f_A(English)      our own translation
current model      : f_A(English) → f_B(English)
```

The model does **register transfer**, not question answering. Question→answer caps around Token F1
0.2576; this approach reaches 0.7724.

**Capacity is measurably not the bottleneck** — two BanglaT5 seeds landed at 0.7724 and 0.7723, a
gap of 0.0001. When two independent runs agree that closely, only more **information** or more
**training** can help. That is why wave 1 leads with information (E01, E02, E17) and training budget (E05).

---

## ▶ Run order — waves, not a queue

**You have unlimited GPUs, so this is not a serial list.** Each wave runs fully in parallel;
you only wait between waves because later experiments need earlier answers.

**What unlimited GPU does NOT change: the 3B cap.** Base + adapters + **every ensemble
member** must total ≤3B *at inference*. The fleet's real use is training many small models and
using large models as **teachers that never ship** (E20).

### Wave 1 — 5 in parallel, ~3 h. Most of the program's information for a fraction of its cost.

| | Question | Why it is in wave 1 |
|---|---|---|
| **E17** | Is the draft itself the bottleneck? | **No GPU.** Gates everything — a better draft invalidates every result measured against the old one |
| **E05** | Had the incumbent converged? | It peaked at 2,750 and was **still improving**. Pure GPU-time; the likeliest free win |
| **E01** | Does the English source help? | The incumbent never sees it |
| **E02** | Does the patient question help? | **The 0.85030 model never sees it.** Untested blind spot |
| **E08** | Is mT5 viable at all? | Control that decides whether E09 is worth running |

After wave 1 you know whether English helps, whether the question helps, whether mT5 is viable,
and where training actually converges.

### Wave 2 — needs wave 1's winner

| | Question |
|---|---|
| **E20** *(stage 1)* | Can a 235B teacher beat 0.7724 at all? Cheap, decisive, gates its own stage 2 |
| **E18** | **Model zoo** — sweep every viable ≤3B base in one parallel wave (Qwen3-1.7B · Gemma-2-2B · Qwen2.5-1.5B · Qwen3-0.6B · Llama-3.2-1B · IndicBART). Outside evidence says decoders beat encoder-decoders |
| **E06** | Was lr 1e-3 still right? Run **8 LRs in parallel**, not 3 sequentially |
| **E03** E04 | All-inputs / english-only, at the winning config |
| **E09** | mT5 at the winning input *(only if E08 was competitive)* |
| **E07** | What did truncation cost? |

### Wave 3 — data and combination

| | Question |
|---|---|
| **E20** *(stage 2)* | Sequence-level KD from the teacher *(only if stage 1 cleared 0.82)* |
| **E12** | Does a Bengali medical warm-start help? |
| **E13** | Does multi-task Q→A add robustness insurance? |
| **E21** | Can synthetic pairs be manufactured from unpaired corpora — and does draft variety buy E17 insurance? |
| E22 | **RAG** — arm A upgrades E20's teacher examples; arm C is the real prize and it is a **Phase 2** play |
| **E19** | Does a **10-seed** ensemble work where 2 seeds failed? 10×248M = 2.48B, fits the cap |
| **E14** | Does architecture diversity ensemble better than seed diversity? |

### Wave 4 — ship

| | Question |
|---|---|
| **E15** | Decoder sweep on the winner. No training; cheapest gain on the board |
| **E16** | **Phase 2 clinical audit — 20% of the final score, different objective** |
| **E22c** | RAG grounding for Phase 2 — judged by E16's audit, not by Token F1 |

### If you could run only three

**E05** (free score from compute) · **E17** (raises every ceiling) · **E20** (highest ceiling
of all, and stage 1 is two hours).

### Dependencies

```
E17 (no GPU) ─► if it WINS, rebuild all data and restart from wave 1
E05 ───────────► convergence point feeds every later run's step budget
E01 E02 ───────► E03 ─┐
E04 ──────────────────┼─► winning input feeds E06 E07 E09 E12 E13 E18 E19 E20
E08 ─► E09 ───────────┘
E20 stage 1 ─► stage 2, and ─► E21 arm C   (both gated at Token F1 > 0.82)
E17 ──────────► E21 arm A is the insurance policy for a draft-translator change
E18 (zoo) ───► E14 (needs a genuinely disagreeing member)
E22 arm A ───► upgrades E20 stage 1 (k-NN examples instead of random)
any checkpoint ─► E15, E16
```

### Removed — do not resurrect without new evidence

| Was | Why it is gone |
|---|---|
| mT5-large (trimmed) | Sized as a **capacity** experiment, but two BanglaT5 seeds agreeing to 0.0001 says capacity is not the bottleneck. E18's decoder is the better use of the slot. |
| mBART-50 | Its only real value was ensemble diversity, and **E18 supplies that better** — a decoder differs from BanglaT5 far more than another seq2seq does. |

---

## How long the program took — it RAN, 2026-08-09 → 08-15

**This section was an estimate. It is now a measurement.** The program executed on CHPC granite and
notchpeak across five VRAM tiers (H100 NVL, A800 40 GB, L40S, A6000, A40), one GPU per arm, bf16 —
**~60 arms over 7 calendar days**, ending at **LB 0.89552, #1**.

**The estimate was wrong in the direction that matters.** It projected ≈105 GPU-hours; the arms as
actually specified came to **≈164 GPU-hours across 45 arms**, and the real program ran more than
that once E19's thirteen seeds, E23 and E24 were added. The miss was **E18** — sized here as one
decoder hedge, it became a 7-base zoo costing 54.7 GPU-h on its own, a third of the program.

**Throughput, measured:** the 0.85030 recipe took **472 min on a Kaggle T4** and **69 min on an
H100 NVL** — **~20×**, not the ~6× assumed above. Wall clock became dominated by *evaluation*,
not training.

**Two lessons for anyone re-planning this:**
1. **Wall clock stopped scaling past ~8 GPUs**, because two single arms could not be split —
   E05 (30,000 sequential steps) and E18's `gemma-2-2b-it` (2.6B, ~10× BanglaT5's per-step cost).
2. **Schedule was never the constraint; it was the estimate's own scope.** Adding one experiment
   (E18) cost more than three waves of the original plan.

**E24 did not finish** — seven arms re-running the decoder zoo on the winning `english_draft`
input produced **zero evals** before being stopped; `gemma2_2b_ed` was running at 23.5 s/it, a
78-hour job. Given E18 already showed every decoder losing to BanglaT5 by ≥0.026, it is not worth
resuming.

**Phase 1 closes Aug 24, 00:00 GMT+6 · Phase 2 bundle due Aug 25, 12:00.** Training is done; the
remaining calendar belongs to **Phase 2 packaging**, exactly as this section originally warned.

## `reference_notebooks/` — the recipes that produced these numbers

Working Kaggle notebooks, kept as reference implementations. **Copy these rather than rebuilding** —
they carry every trap fix the hard way.

| Notebook | What it is |
|---|---|
| **`PROVEN_xfer_seed11_LB0.85030.ipynb`** | **The exact notebook behind the 0.85030 submission.** The recipe every experiment here modifies. |
| `PROVEN_xfer_seed23.ipynb` | Its seed replicate — landed 0.7723 vs 0.7724 |
| `sweep_C_lr1e3_best_qa_arm.ipynb` | Best question→answer arm; where lr 1e-3 was established |
| `sweep_G_lr3e3_LR_ceiling.ipynb` | The arm that turned the LR curve over |
| `mt5_english_draft_kaggle.ipynb` | mT5 on Kaggle — includes the runtime-projection guard |
| `banglat5_v2_baseline.ipynb` | Earliest clean baseline |

They target Kaggle (T4, 12 h). On a big GPU, **raise `--batch-size`, lower `--grad-accum`, raise the
sequence limits, and drop the step caps** — those were all ceiling workarounds, not choices.

## Environment

```bash
pip install "transformers==4.57.3" torch pandas pyarrow sentencepiece protobuf
pip install git+https://github.com/csebuetnlp/normalizer     # required by BanglaT5's model card
python -c "import transformers; assert transformers.__version__=='4.57.3'"
python code/metric.py --selftest        # verifies LCS against brute force
```

### Non-negotiables

| | |
|---|---|
| **`transformers==4.57.3`** | Other versions do not train this pipeline correctly — 5.0.0 reports loss ~163 instead of ~10 and silently unties embeddings. Cost ~10 GPU-hours before it was found. **Assert the version.** |
| **bf16 on sm_80+, fp32 below. NEVER fp16** | T5 overflows to NaN in fp16 and fails **silently** — prints a parameter count, reports "decoded 300 rows", writes a well-formed CSV of garbage. Gate on `get_device_capability()[0] >= 8`, **not** `is_bf16_supported()` (returns `True` on a T4 via emulation). |
| **`--seed 42 --dev-size 5000`** | The frozen split. Every number in this project rests on it. Changing it makes results incomparable to everything. |
| **Select on composite, never `eval_loss`** | They move in opposite directions on some tasks — one run's *lowest loss* coincided with its *worst* Token F1. |
| **Assert a known-good number before writing a submission** | The only thing that caught the fp16 bug. A well-formed CSV of garbage is indistinguishable from a good one until the leaderboard says so. |

---

## Scoring

**Judge on Token F1 and ROUGE-L, never the local composite** — it is mis-calibrated by ~0.118
because the organizers' BERTScore model is unknown.

```
LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L
```

Calibrated on two real submissions 0.5 of Token F1 apart; fits both to **±0.0001**.

**Reference points**

| | Token F1 | ROUGE-L | LB |
|---|---|---|---|
| **incumbent** — BanglaT5, draft only | **0.7724** | **0.7324** | **0.85030** |
| draft + 3 regexes, no model | 0.5984 | 0.5482 | 0.7564 |
| best question→answer fine-tune | 0.2576 | 0.1776 | 0.5800 |
| constant string (previous #1) | 0.2669 | 0.1564 | 0.57849 |
| **noise floor** | **0.0044** | — | — |

**Ignore any difference below 0.0044 Token F1.**

### The register read-out — report it for every run

| | references | our draft |
|---|---|---|
| outputs opening `হেলো` | **76.4%** | 0.06% |
| outputs containing `নাসেনিয়া` | **50.0%** | 0.00% |

Near the draft's rates ⇒ the model copied its input. Near the references' ⇒ it learned the
conversion. This is the sharpest single diagnostic available.

---

## Things already settled — do not re-litigate

| Finding | Evidence |
|---|---|
| **LR 1e-3 optimum** *(on question→answer)* | 7 arms; the curve turns over at 3e-3. Never re-tuned for **this** task — that is **E06**. |
| **Label smoothing does nothing** | +0.0039, inside a 0.0044 noise floor |
| **MBR loses** | −0.0027 LB vs beam-4. Near-deterministic task; two seeds agreed to 0.0001. **E14** tests only the untested variable: architecture diversity. |
| **More epochs hurt on question→answer** | Every arm peaked then declined. **Does NOT transfer** — this task never turned over. That is **E05**. |
| **Retrieval < a constant string** | 0.2047 vs 0.2669 — specific-but-wrong costs more precision than it gains recall |
| **BanglaT5 tokenises this better than mT5** | 364/145 vs 443/272 tokens. mT5 needs **88% more tokens for the same Bengali output**. |
| **Only 9.2% of mT5's vocab is used** | 22,991 of 250,100 → trimming takes mT5-large 1.23B → ~785M (**E10**) |

---

## Reporting back — EVERY arm's checkpoint, in its own folder

**Metrics alone are not a result.** Inference happens on a different machine (Kaggle), so an
experiment that returns only numbers must be **retrained from scratch** before it can ever be
submitted.

### Keep every arm, not just the winner

Several experiments run many models — E18 sweeps 7 bases, E19 trains 10 seeds, E06 runs 8 learning
rates, E21 has 5 arms. **Keep the checkpoint for all of them, including the ones that score badly.**

**Size is not a consideration. Losing arms are not disposable:**

- A model that scores *below* the incumbent but **disagrees with it usefully** is exactly what
  E14/E19 need — and cannot get from another seed. Pooled MBR failed once precisely because two
  members agreed to 0.0001.
- "Which arm won" is only known after scoring. Deleting as you go throws away the answer to a
  question that has not been asked yet.
- Re-running one arm to recover it costs more than storing all of them.

### Folder layout — one directory per arm

```
E18_model_zoo/
    EXPERIMENT.md              the spec (what to run, what to beat)
    train.ipynb                RUNNABLE — config in cell 1, trains every arm, asserts
                                  no checkpoint is missing before it finishes
    RESULTS.md                 the per-experiment record — fill this in
    banglat5/
        best/                  THE MODEL — config.json · model.safetensors ·
                                  tokenizer files · generation_config.json
        run.json               config + dev metrics — MUST sit beside the weights
        trainer_state.json     full eval trajectory
        dev.json  test.json    decode records
    qwen3_1p7b/    best/ run.json trainer_state.json dev.json …
    gemma_2_2b_it/ best/ run.json trainer_state.json dev.json …
    qwen25_1p5b/   …
    qwen3_0p6b/    …
    llama32_1b/    …
    indicbart/     …
```

Single-arm experiments use one `main/` directory, same contents. **Every experiment folder already contains:**

| File | |
|---|---|
| `EXPERIMENT.md` | the question, why it matters, what to beat, how to read the outcome |
| **`train.ipynb`** | **runnable** — all config in cell 1, loops over every arm, writes `best/` + `run.json` + `dev.json` per arm, and **asserts no checkpoint is missing** before it exits |

**The batch/accum defaults in `train.ipynb` were tuned for one 16 GB T4 — change them.**
**Effective batch must stay 64** (`BATCH × ACCUM × N_GPU`, asserted in cell 1): that is what the
0.85030 model used, and changing it makes the result incomparable. *How* you reach 64 is entirely
a hardware decision. Everything else about execution — parallelism, attention kernel, workers,
`torch.compile` — is yours to choose.

**Never trade quality for throughput.** If you are memory-bound the answers are more GPUs, a
smaller per-device batch with higher accumulation, or gradient checkpointing — **never** fp16,
quantisation, LoRA in place of a full fine-tune, shorter sequences, fewer steps, or a coarser
eval grid.
| `RESULTS.md` | the per-experiment record, with this experiment's arms pre-listed |

Four experiments train nothing (**E14** ensembling · **E15** decode sweep · **E16** Phase-2 audit ·
**E17** closed) and carry a `NO_TRAINING.md` explaining what to run instead.

Do not put per-experiment detail only in the top-level scoreboard.

**E05 is the exception on intermediate checkpoints.** Its whole purpose is finding where the
curve turns over, so **keep a checkpoint every 2,000 steps** there — the trajectory checkpoints
*are* the result, not scaffolding.

### The two records, and what goes where

| File | Holds |
|---|---|
| `<experiment>/RESULTS.md` | **Everything about this experiment** — per-arm scores, checkpoint locations, trajectories, register read-out, failures, surprises |
| `RESULTS.md` *(top level)* | Only the cross-experiment scoreboard and the **pairwise comparisons** that answer the program's questions |

### Still not worth keeping

| Delete | Why |
|---|---|
| `runs/smoke/**` | 1,000-row pipeline warmups. Pure waste |
| optimizer / scheduler / RNG state | Not needed for inference |
| intermediate `ckpt/checkpoint-*/` **weights** — *except in E05* | Superseded by that arm's `best/`. **Keep every `trainer_state.json`** — a few KB, and it is the trajectory evidence |

**`runs/smoke/` shadows the real run's filenames.** It writes its own `run.json` and
`checkpoint-63/trainer_state.json`. A glob like `runs/*/run.json` flattened into one destination
**silently replaces a 400-minute record with a 2.6-minute one.** Filter `smoke` explicitly and
verify `run_name`/`seed` after any copy.

### Returning them — Kaggle Datasets, because inference runs there

One dataset per experiment keeps things under control and lets an inference notebook attach only
what it needs:

```bash
mkdir -p ckpt_upload && cp -r E18_model_zoo/*/  ckpt_upload/     # every arm
find ckpt_upload -name 'optimizer.pt' -o -name 'scheduler.pt' -o -name 'rng_state*' | xargs rm -f

cat > ckpt_upload/dataset-metadata.json <<'EOF'
{ "title": "nascenia-e18-model-zoo", "id": "<kaggle-user>/nascenia-e18-model-zoo",
  "licenses": [{"name": "CC-BY-NC-SA-4.0"}] }
EOF

cd ckpt_upload && kaggle datasets create -p . -r zip
# updates later:  kaggle datasets version -p . -m "added indicbart arm"
```

Licence is **CC-BY-NC-SA-4.0**, inherited from BanglaT5. `-r zip` matters at this size.
Record the dataset slug in that experiment's `RESULTS.md` checkpoint table.

**`run.json` must ship inside the same folder as the weights.** `checkpoint_hash` is not a run
identity — ours hashed file *names and sizes*, so three different models reported the same hash and
a 393-minute run collided with a 2.6-minute smoke test. **The `run.json` config block beside the
weights is the only reliable link between a checkpoint and the number it scored.**

**The model behind any submitted score is mandatory Phase 2 evidence and must never be deleted** —
Phase 2 requires reproducing the leaderboard outputs from the checkpoint.

**Report the trajectory, not just the best number.** Where a run peaks is often the finding —
E05 exists entirely because the incumbent's trajectory showed it had not converged.
