# Prompt to paste into your friend's Claude

Everything below the line is self-contained — it does not need any context from the conversation
that produced this folder.

---

```
You are running a three-way model bake-off for the Phase 2 half of a Kaggle competition
(Nascenia Bengali Medical Dialogue). Everything you need is in the folder
"Phase2 Final architecture/". Read these, in this order, before running anything:

  1. README.md        — the routing architecture, the bar to beat, the non-negotiables
  2. GPU_BUDGET.md    — READ BEFORE LAUNCHING. 5 days left, and the full matrix is not sized to
                        it. Measured per-step rates from this project's own runs, three config
                        changes that cut cost at no scientific cost, a priority order for what to
                        drop, and the gate for cutting model C. You do the scheduling.
  3. DATA_GUIDE.md    — every dataset, verified row counts, what to use and what to avoid
  4. EXPERIMENTS.md   — the 8-arm experiment matrix (X0-X7), identical for all three models
  5. <your model>/INSTRUCTIONS.md — model-specific traps and starting hyperparameters

THE SHORT VERSION

The competition scores in two phases. Phase 1 (80%) is already won and is NOT your problem — a
BanglaT5 model holds #1 at 0.89552 by exploiting a deterministic id-lookup into a public corpus.
Do not touch it.

Phase 2 (20%) is judged by an LLM on the organizers' OWN private data, where that lookup resolves
on exactly 0% of rows. Measured: fed a novel question with no lookup, the champion echoes the
patient's message back instead of answering — Token F1 0.1235, and no inference-time fix gets past
0.1454. So Phase 2 needs a second, separate model that can actually answer. That is what you are
building.

YOUR JOB

Train and evaluate three candidate models, run every arm for each, and tell me which wins:

  A_mT5_base/       google/mt5-base        580M, seq2seq
  B_Qwen35_2B/      Qwen/Qwen3.5-2B        2B,   decoder
  C_BanglaAI_17B/   swapnillo/Bangla-AI-1.7B 1.7B, decoder

Each folder has train.ipynb, inference.ipynb, INSTRUCTIONS.md and an empty RESULTS.md to fill in.
The three are independent — run them in parallel if you have the GPUs.

The folder is fully self-contained (~119 MB) — all data is bundled in data/_sources/ and
verified. You do not need to download anything or point at any other directory.

ORDER  (run from the folder root; no arguments needed)

  1. python shared/build_index.py    # once, shared, ~1 GPU-hour. Assembles a 118,912-row pool
                                     # and asserts 0 frozen dev/test ids are in it.
  2. python shared/build_data.py     # once, shared. Writes plain / rag / plain_core_only.
  3. READ 5 ROWS of data/rag/train.parquet BY HAND and confirm the retrieved reference case is a
     DIFFERENT case from the question being asked. There is an assert for this, but an assert
     cannot catch a subtly wrong template and your eyes can. If the reference IS the answer,
     stop — every RAG number would be meaningless.
  4. per model: train.ipynb (set ARM in cell 1, run once per arm), then inference.ipynb
     - all three models run arms X0-X7
     - A_mT5_base AND B_Qwen35_2B also run D1/D2/D3, which decompose the data question (X4 only
       compares "all extras" vs "none" and cannot say WHICH source helped). Running them on one
       seq2seq and one decoder makes it a cross-check: if A and B agree, the data verdict is
       architecture-independent and C inherits it. If they DISAGREE, that is itself a finding --
       say so, and run D1/D2/D3 on C too before trusting its X2.
     - do the D arms early: the winning data variant is what C should use for its X2.
  5. fill in each RESULTS.md

HYPERPARAMETERS ARE YOURS

Batch size, accumulation, precision, sequence caps, gradient checkpointing, optimizer, parallelism
— all yours, tuned to whatever GPU you actually have. Each INSTRUCTIONS.md gives a starting point
and explains WHY each value is where it is so you can move it intelligently.

Only two things are fixed, because they define the experiment rather than its speed:
  - effective batch = 64 (per_device x accum x n_gpu). Everything in this project is comparable
    at 64; change it and nothing lines up.
  - the learning-rate CLASS: ~1e-3 for seq2seq (model A), ~2e-5 for decoders (B, C). Crossing
    these diverges the run and it reads as "bad model" when it is a broken run. Sweeping WITHIN
    a class is arm X5 and is encouraged.

If something genuinely cannot be met on your hardware, say so and stop — do not silently
substitute a weaker version.

NON-NEGOTIABLE

  - NEVER fp16. bf16 on sm_80+, fp32 below. T5 overflows to NaN silently — it still prints a
    parameter count, still "decodes", still writes a valid CSV of garbage. Gate on
    torch.cuda.get_device_capability()[0] >= 8, NOT is_bf16_supported() (True on a T4 via
    emulation).
  - NEVER change the frozen split (seed 42, 5,000 dev rows).
  - KEEP EVERY ARM'S CHECKPOINT, including the losers. A row with a score and no checkpoint is a
    result that cannot be submitted without a full retrain.
  - Judge on Token F1 and ROUGE-L, never the local composite (mis-calibrated by ~0.118). Ignore
    any difference below 0.0044 — that is the measured noise floor.
  - Do not touch, retrain, or re-average the existing champion checkpoint.

BUDGET — YOU HAVE 5 DAYS. Phase 2 bundle is due Aug 25, 12:00 GMT+6.

Decoders cost 15-35x more per step than the seq2seq model, measured from this project's own ~60
previous runs. Model A (mT5) is nearly free; B and C are where the entire budget goes.

GPU_BUDGET.md has the measured per-step rates, three config changes that cut cost at no scientific
cost, and a priority order for what to drop. YOU decide the actual schedule and how much fits --
you know your fleet, the folder does not. Tell me what you decided to run and what you dropped.

THE ONE GATE TO WATCH: as soon as A's and B's X2 arms land, check them. If EITHER clears Token
F1 0.1454 by more than the 0.0044 noise floor and produces fluent on-topic Bengali, STOP model C
and spend that time on the winner instead -- training it longer, running its decode sweep properly,
or building the combined routing inference script, which is still unwritten and is a hard
requirement for the Phase 2 bundle. Do not run C to completion out of symmetry.

If your measured throughput diverges from GPU_BUDGET.md's rates by more than ~30%, say so and
re-plan rather than pushing on with a schedule built on the wrong numbers.

WHAT I NEED BACK

  1. All three RESULTS.md, filled in — including arms that lost, with the same care.
  2. Every checkpoint, one directory per arm, run.json beside the weights. Private Kaggle
     datasets are fine if they are large.
  3. A one-paragraph recommendation: which model, which arm, and why — including whether RAG
     earned the 278M parameters its retriever costs.
  4. For the RAG arms specifically: the copy-margin. If a model scores well but is copying the
     retrieved example instead of answering, that arm has failed regardless of Token F1, and I
     need to know.

REPORTING STYLE

Report the trajectory, not just the best number — where a run peaks is often the finding. This
project's own champion was under-trained by a factor of 4.4 and nobody noticed until the full
curve was plotted.

If a result contradicts something in these documents, say so explicitly rather than smoothing it
over. Several documented claims here have already been overturned by measurement; a contradiction
is a finding, not a mistake.

Anything in the specs that looks wrong to you — say so before running it. The sequence caps and
batch sizes are starting points sized without access to your hardware.
```
