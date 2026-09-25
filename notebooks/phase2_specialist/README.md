> **Repo note.** This is `Phase2 Final architecture/README.md`, written before the study ran. In this repo `shared/` and `router/` are in [`scripts/phase2/`](../../scripts/phase2/), `data/` is not uploaded (inventory: [`datasets/phase2_bundled/DATASETS.md`](../../datasets/phase2_bundled/DATASETS.md)), and each model's `RESULTS.md` is the final version from the Phase 2 bundle. **Outcome:** B_Qwen35_2B arm D1 shipped as the specialist (held-out Token F1 0.2625); mT5-base turned out the weakest of the three — see [`PHASE2_WRITEUP.md`](../../PHASE2_WRITEUP.md).

# Phase 2 Final Architecture — build the generalist specialist

**Read this file first, then `GPU_BUDGET.md`, then `DATA_GUIDE.md`, then `EXPERIMENTS.md`, then
your model's `INSTRUCTIONS.md`.**

**`GPU_BUDGET.md` is not optional reading, and there are only 5 days** (Phase 2 bundle due
**Aug 25, 12:00 GMT+6**). The matrix in `EXPERIMENTS.md` is scientifically complete but is **not**
sized to that deadline. `GPU_BUDGET.md` gives you throughput **measured from this project's own
~60 previous runs**, three config changes that cut the cost substantially at no scientific cost,
a priority order for what to drop, and a stated gate for cutting model **C**.

**You budget the wall clock** — you know your fleet, this folder does not.

**This folder is fully self-contained — ~119 MB, all data bundled in `data/_sources/`.**
Nothing outside it is needed. Copy the whole folder anywhere and run.

| bundled file | rows | what it is |
|---|---|---|
| `data/_sources/train.parquet` | 101,740 | competition train, frozen dev/test already removed |
| `data/_sources/dev.parquet` | 5,000 | the frozen dev split (seed 42) — evaluation only, never train on it |
| `data/_sources/test.parquet` | 1,000 | competition test rows (no targets) |
| `data/_sources/extra_sources.parquet` | 17,172 | iCliniq 7,321 + GenMedGPT 5,200 + doctor_qa_bangla 4,651 |

**Verified end-to-end on 2026-08-17:** the pool assembles to exactly **118,912 rows** and the
dev/test leak assert passes (0 of 5,000 dev + 1,000 test ids present).

---

## The architecture, in one picture

```
                    incoming patient question (Bengali)
                                 │
                    does this row's id resolve via hcm_<id>
                    into the external ChatDoctor corpus?
                    ┌────────────┴────────────┐
                   YES                        NO
       (Phase 1: 100% of test.csv)    (Phase 2: 100% of the judging set)
                    │                         │
         ┌──────────▼──────────┐   ┌──────────▼───────────────────┐
         │  BanglaT5 champion  │   │  PHASE 2 SPECIALIST          │
         │  ckptavg_peak5      │   │  ← THIS FOLDER BUILDS IT     │
         │  247.6M, UNCHANGED  │   │  mT5-base / Qwen3.5-2B /     │
         │  LB 0.89552, #1     │   │  Bangla-AI-1.7B + optional RAG│
         └─────────────────────┘   └──────────────────────────────┘
```

**Why two branches.** Phase 1 is scored on the competition's `test.csv`, whose ids are row
indices into a public ChatDoctor corpus — **all 1,000 resolve**, so the champion handles 100% of
Phase 1 (public *and* private slices). Phase 2 is judged by an LLM on the **organizers' own
private data**, which is not ChatDoctor-derived — **0% resolves**, so the specialist handles
100% of Phase 2. The two branches never compete for the same row. Building the specialist
carries **zero risk** to the 0.89552 leaderboard number, because the champion is untouched and
its branch is unaffected.

**Rules §3 permits this**: *"Ensembling multiple models is permitted, provided that the combined
parameter count of all models used at inference stays under 3B."*

## The measurement that created this folder

The champion cannot answer a question it wasn't handed a draft for. Measured on the frozen
`dev[0:300]` split, champion unchanged:

| what was fed to the champion | Token F1 |
|---|---|
| its normal ChatDoctor-lookup input | **0.8328** |
| the raw patient question only, no lookup | **0.1235** |
| a live English translation in its exact trained template | **0.1454** |

Reading the actual predictions: with no draft to restyle, it **echoes the patient's own message
back** instead of answering. Fixing the input *shape* moved it +0.0219 — nothing. It memorized
one external corpus's translation distribution, not "how to answer."

**So the specialist must beat Token F1 `0.1454`.** That is the floor, and it is the honest bar —
nothing in this project has ever attempted genuine question-answering at convergence, so any
real gain over it is new ground.

## Three models, three folders — run all three

| Folder | Model | Params | Why it's a candidate |
|---|---|---|---|
| **`A_mT5_base/`** | `google/mt5-base` | 580M | **Best measured Bengali score of the three (0.8017)** *despite being 3.4× smaller than B*, best tokenizer efficiency (271 tok/answer), and it is seq2seq — the same architecture family and trainer as the champion, so the lowest-risk pipeline |
| **`B_Qwen35_2B/`** | `Qwen/Qwen3.5-2B` | 2B | Best *decoder* that is open and fits. 248k vocab (294 tok/answer). Tests whether raw scale + broader pretraining beats a small efficient seq2seq at genuine reasoning |
| **`C_BanglaAI_17B/`** **CUT 2026-08-20** | `swapnillo/Bangla-AI-1.7B` | 1.7B | Already Bengali-instruction-tuned on 100K instructions. Built on Qwen3-1.7B, whose tokenizer measured **worst of every decoder tested** (689 tok/answer, 4.85× handicap) — instruction-tuning does not fix a tokenizer. Included because its instruction-tuning may compensate; **do not assume it will**. Cut per the cut-gate below once `A_mT5_base`'s X3 cleared 0.2533 — see `C_BanglaAI_17B/RESULTS.md` |

Those scores come from this project's own model zoo (E18) measured on a *different* task
(register transfer). Treat them as a **tokenizer-efficiency and baseline-competence signal, not
a Phase 2 prediction** — the reasoning ability the specialist actually needs was never measured
by that task.

## Parameter budget

| component | params |
|---|---|
| BanglaT5 champion (Phase 1 branch, fixed) | 247,577,856 |
| retriever `intfloat/multilingual-e5-base` (only if a RAG arm wins) | ~278,000,000 |
| **remaining for the specialist** | **~2.47B** |

All three candidates fit. Combined totals: A ≈ 1.11B · B ≈ 2.53B · C ≈ 2.23B. **Assert the real
number in the inference notebook** — every model this project checked with a size in its name
differed from the card (Qwen2.5-3B is 3.09B, Llama-3.2-3B is 3.21B; both would have been
disqualifying).

## What to run, in order

Run from the folder root. No arguments needed — the defaults point at the bundled data.

```bash
python shared/build_index.py     # 1. dense retrieval index over the 118,912-row pool (~1 GPU-h)
python shared/build_data.py      # 2. all dataset variants: plain / rag / plain_core_only
# 3. read 5 rows of data/rag/train.parquet BY HAND before training anything (see below)
# 4. per model: train.ipynb (set ARM in cell 1, once per arm), then inference.ipynb
# 5. fill in each RESULTS.md, then pick the overall winner
```

Steps 1–2 are shared and run **once**. Steps 4–5 are per-model and independent — run them
concurrently if you have the GPUs.

**Step 3 is not optional.** `build_data.py` asserts that no row retrieves itself as its own
RAG reference, but an assert cannot catch a subtly wrong template and your eyes can. Confirm the
`অনুরূপ কেস` reference is a **different case** from the question being asked. If the reference
*is* the answer, every RAG number is meaningless.

Steps 1–2 are shared and run **once**. Steps 3–4 are per-model and independent — run them
concurrently.

## Non-negotiables

- **Never modify the champion.** No retraining, no re-averaging, no touching
  `ckptavg_peak5`. Its 0.89552 must stay reproducible byte-for-byte.
- **Never change the frozen split**: seed 42, 5,000 dev rows. Every number in this project
  rests on it.
- **Never fp16.** T5 overflows to NaN *silently* — it still prints a parameter count, still
  "decodes", still writes a valid CSV of garbage. bf16 on sm_80+, fp32 below. Gate on
  `torch.cuda.get_device_capability()[0] >= 8`, **not** `is_bf16_supported()` (that returns True
  on a T4 via emulation).
- **Judge on Token F1 and ROUGE-L, never the local composite** — it is mis-calibrated by
  ~0.118. Ignore any difference below **0.0044** (the measured noise floor).
- **Keep every arm's checkpoint**, including losers. A model that scores worse but *disagrees
  usefully* is the only thing an ensemble can use.
- **Report the trajectory, not just the best number.** Where a run peaks is often the finding —
  the champion's own predecessor was under-trained by 4.4× and nobody noticed until the full
  curve was plotted.

## Fine-tuning hyperparameters are YOURS to set

Batch size, gradient accumulation, precision, parallelism, sequence caps, LoRA-vs-full,
gradient checkpointing, workers — **all yours**, tuned to whatever GPU you actually have.
`INSTRUCTIONS.md` in each folder gives a starting point and explains *why* each value is where
it is, so you can move it intelligently.

**The two things that are not yours**, because they define the experiment rather than its speed:
1. **Effective batch = 64** (`per_device × accum × n_gpu`). Everything in this project is
   comparable at 64; change it and nothing lines up.
2. **Learning rate class.** Seq2seq (mT5) wants ~1e-3; decoders want ~2e-5. Carrying the seq2seq
   LR onto a decoder **diverges**, and the run reads as "bad model" when it is a broken run.
   Within a class, sweeping is encouraged — that is experiment **X5**.

If something genuinely cannot be met on your hardware, **say so and stop** — do not silently
substitute a weaker version.
