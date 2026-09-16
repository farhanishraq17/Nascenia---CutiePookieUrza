# Two prompts for your teammate's Claude

Paste **Prompt 1** first and let it finish reading. Then paste **Prompt 2** to start work.

---

## PROMPT 1 — load the project context

```
You are joining an in-flight Kaggle competition project. Before doing anything, read the
following files in this order. Do not skim — these are the project's accumulated memory, and
several of them record corrections to earlier conclusions that are easy to re-make.

READ THESE, IN THIS ORDER:

1.  CLAUDE.md
    The single most important file. Project rules, repo layout, the measured findings that
    drive strategy, and 21 numbered "traps already hit" that cost real GPU-hours. Read every
    trap — most look like unrelated bugs and were one root cause.

2.  RULEBOOK/COMPETITION_RULES.md
    The competition rules. Note the ≤3B parameter cap at inference, the two-phase scoring, and
    §2.6.a (external data must be equally accessible to all participants).

3.  PLAN.md
    Phase 1 strategy, grounded in measurements. Pay attention to §5.3b (LIT-01) — a dataset
    ranked #1 for two days turned out to be synthetic and machine-translated.

4.  LOCAL_EXPERIMENTS.md
    Every run, including failures. This is where negative results live. Read ALIGN-01, MBR-01,
    E17-01, LIT-01, and BUG-01/02/03 carefully.

5.  PROGRESS.md
    The chronological journal — what happened, why, and what each result changed. Newest first.

6.  PREDICTIONS.md
    The dev↔leaderboard correlation table. The refined predictor lives here.

7.  FINE_TUNING_NOTEBOOKS/FINE_TUNING_LOG.md
    Master results table for every BanglaT5 run. Top level only — do NOT read the individual
    numbered run folders, they are per-run metadata and not needed.

8.  fine_tune_project/README.md
    The experiment program you will be running: 20 experiments in 4 parallel waves.

9.  fine_tune_project/RESULTS.md
    The cross-experiment scoreboard and, more importantly, the pairwise comparisons.

10. fine_tune_project/data/README.md
    What each prebuilt dataset is and which experiment uses it.

11. fine_tune_project/code/README.md
    The shared scripts and the two hard-won fixes they carry.

12. fine_tune_project/data/warmstart_corpus/SOURCES.md
    Provenance, licences, and the leak that was removed from that corpus.

13. fine_tune_project/E*/EXPERIMENT.md
    All 20. Each states its question, why it matters, the exact command, what it must beat, and
    how to read the outcome — including what a NEGATIVE result means.

SKIP: GPT-INSTRUCTIONS.md and GPT_DATASET_FIND.md (external strategy input, partly superseded).
SKIP: the numbered folders under FINE_TUNING_NOTEBOOKS/ and anything under DATA/.

WHEN YOU HAVE READ THEM, REPORT BACK WITH:

a) The task in two sentences — specifically what the model's input and output are. (Hint: it is
   not question answering. If you think it is, you have missed the single largest finding.)
b) The current leaderboard score, and the exact dev Token F1 / ROUGE-L behind it.
c) The three hard constraints that would invalidate a run if violated.
d) Which experiment you would run first and why.
e) Anything in these documents that looks internally inconsistent or stale — I would rather
   hear it now than have it silently acted on.

Do not start any training yet.
```

---

## PROMPT 2 — run the program

```
You have the project context. You are now running the experiment program in fine_tune_project/
on a machine with effectively unlimited GPUs. Phase 1 closes 2026-08-24.

THE JOB

Run the experiments in fine_tune_project/. Each folder has:
  EXPERIMENT.md  — the spec: question, what it must beat, how to read the result
  train.ipynb    — runnable; all config in cell 1; loops over that experiment's arms
  RESULTS.md     — the per-experiment record you must fill in
Four experiments train nothing and carry NO_TRAINING.md instead (E14, E15, E16, E17).

ORDER — waves, not a queue. README.md has the full plan.
  Wave 1, all in parallel: E05, E01, E02, E08   (E17 is already closed)
  Then waves 2-4, each gated on the previous wave's winner.

E05 is the single highest-value run: the current #1 model peaked at step 2,750 and was STILL
improving when a 12-hour limit stopped it. It has never been run to convergence.

YOU DECIDE THE HARDWARE SETTINGS. I DECIDE THE EXPERIMENT.

The configs in train.ipynb were tuned for a single 16GB T4 under a 12-hour limit. They are a
STARTING POINT, not a specification. Inspect the hardware you actually have and set the execution
strategy yourself — I have not seen your machine and my defaults will almost certainly waste it.

YOURS TO CHOOSE, from what the hardware supports:
  - per-device batch size and gradient accumulation (see the constraint below)
  - single-GPU vs DDP vs FSDP/DeepSpeed; how many GPUs per run
  - how many experiments/arms to run concurrently
  - attention implementation (flash-attn / SDPA), torch.compile, sequence packing
  - dataloader workers, pin_memory, eval batch size
  - gradient checkpointing — but only if you are genuinely memory-bound

MINE, AND NOT NEGOTIABLE — these define the experiment, not its speed:
  - EFFECTIVE batch size stays 64 (per_device x accum x num_gpus). This is what the current #1
    model used; change it and the result is not comparable to anything. HOW you reach 64 is
    entirely your call — 64x1 on one big GPU, or 8x1 across 8 GPUs, or anything in between.
  - Learning rate, sequence lengths, and step counts as given in each EXPERIMENT.md. These were
    measured, not guessed. (E06 sweeps LR — that IS the experiment.)
  - Evaluate every 250 steps. Do not coarsen this to save time: the metric peaks and then
    declines while loss keeps improving, and a coarse grid straddles the peak.

🔴 NEVER TRADE QUALITY FOR THROUGHPUT. If something does not fit or is slow, fix it with
HARDWARE, never by shrinking the experiment. Specifically, do NOT:
  - cut steps, or stop a run early because it "looks converged"
  - drop to fp16, or to 8-bit/4-bit, to fit memory
  - shorten sequence lengths to fit memory (truncation is information the model can never recover)
  - substitute LoRA/QLoRA for a full fine-tune
  - reduce eval frequency or the 300-row eval subset
  - skip arms, or drop an arm because its early numbers look bad
If you are memory-bound the answers are: more GPUs, smaller per-device batch with more
accumulation, gradient checkpointing, or activation offload. Not a cheaper experiment.

Tell me what you chose and why, and report the actual throughput. If a setting genuinely cannot
be met on your hardware, say so and stop — do not silently substitute a weaker one.

NON-NEGOTIABLES — violating any of these silently invalidates the result

1. KEEP EVERY ARM'S CHECKPOINT, including the ones that score badly.
   E18 has 7 bases, E19 has 10 seeds, E06 has 8 learning rates. Keep all of them. Size does not
   matter. A model that scores below the incumbent but DISAGREES with it usefully is exactly
   what the ensemble experiments need and cannot get from another seed.
   Each arm gets its own directory containing best/, run.json, trainer_state.json, dev.json.
   run.json must sit beside the weights — checkpoint_hash is not a run identity.

2. NEVER fp16. bf16 on sm_80+, fp32 below. T5 overflows to NaN in fp16 SILENTLY — it still
   prints a parameter count, still reports "decoded 300 rows", still writes a valid CSV, and
   scores ~0.0002. Gate on torch.cuda.get_device_capability()[0] >= 8, NOT on
   is_bf16_supported() — that returns True on a T4 via emulation.

3. NEVER change the data split. --seed 42 --dev-size 5000. Every number in this project rests
   on it. Change it and nothing is comparable to anything.

4. Select checkpoints on the composite metric, never on eval_loss. On one run the LOWEST loss
   coincided with the WORST Token F1 — early-stopping on loss would have picked the worst
   checkpoint in the run.

5. Judge on Token F1 and ROUGE-L, never the local composite (mis-calibrated by ~0.118).
   Predict the leaderboard with: LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L
   Ignore any difference below 0.0044 — that is the measured noise floor.

REPORTING — this is half the job

Record everything in each experiment's OWN RESULTS.md: per-arm scores, checkpoint locations,
full eval trajectories, the register read-out (হেলো opener % and নাসেনিয়া %), % truncated,
precision used, GPU, wall-clock. Then update the top-level RESULTS.md scoreboard.

Report the TRAJECTORY, not just the best number. Where a run peaks is often the finding — E05
exists entirely because the incumbent's trajectory showed it had not converged.

Report NEGATIVE results with the same care as positive ones. Every EXPERIMENT.md states what a
negative result means; several experiments are worth running precisely because a clean negative
closes a line of work. Do not quietly drop an arm that looked bad.

HOW TO WORK

- Read the EXPERIMENT.md before running anything, and follow its "how to read the result" table.
- If a result contradicts something in the project docs, say so explicitly rather than
  smoothing it over. Several documented claims have already been overturned by measurement.
- If a run fails, diagnose before re-running. Check the traps in CLAUDE.md first — most of the
  failures already hit in this project looked like novel bugs and were not.
- Tell me if an experiment's premise no longer holds given what earlier waves found. Do not run
  something just because it is in the list.

Start by profiling the environment and PROPOSING a plan before running anything:
  - GPU count, model, compute capability, VRAM, interconnect
  - transformers/torch versions; whether flash-attn is available
  - that fine_tune_project/data/ has all six input datasets
  - that python code/metric.py --selftest passes
  - your chosen per-device batch / accumulation / parallelism, and how it reaches effective 64
  - measured throughput from a short smoke run, and the resulting wall-clock estimate per wave
  - how many experiments you will run concurrently

Show me that plan, then begin Wave 1.
```

---

## Notes for you (not for the prompt)

**Prompt 1 ends with questions on purpose.** Items (a)–(e) are a comprehension check — if their
Claude answers "it's question answering," it has missed ALIGN-01 and everything downstream will be
wrong. Item (e) invites it to catch staleness rather than act on it.

**Prompt 2 leads with the checkpoint rule** because that is the one failure that cannot be repaired
later. Everything else can be re-measured; a deleted model has to be retrained on hardware you may
no longer have.

If your teammate only receives `fine_tune_project/` rather than the whole repo, drop items 1–7
from Prompt 1 and send them `CLAUDE.md`, `PLAN.md`, and `LOCAL_EXPERIMENTS.md` separately — those
three carry the findings the experiment specs assume you already know.
