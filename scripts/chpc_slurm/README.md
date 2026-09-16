# `_slurm/` — running the program on CHPC granite

The program was written for "a machine with effectively unlimited GPUs". This is that machine,
and this directory is the whole of the adaptation: **one SLURM job per arm, one GPU per job.**

```bash
V=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python

$V registry.py                          # every arm as a table; asserts effective batch 64
$V submit.py --wave 1                   # submit a wave
$V submit.py --arm E18_model_zoo/qwen3_1p7b     # or single arms
$V submit.py --wave 2 --data-override english_draft   # resolve "winner of Tier 1" arms
$V collect.py                           # scoreboard across every arm that has landed
squeue -u $USER | grep nasc             # what is running
tail -f logs/nasc-E05-main-*.out        # one log per job
```

## 🔴 The node: grn008, and why that one

`grn008` is **8 × H100 NVL (94 GB), 64 CPUs, 764 GB RAM, and it was completely idle** — it sits in
the general `granite-gpu` partition, which the owner-node GPU survey never looks at.

```
-A kmarino -p granite-gpu --qos=granite-gpu-freecycle --nodelist=grn008 --gres=gpu:1
```

⚠️ **`granite-gpu-freecycle` is preemptible.** Every job carries `--requeue`, and
`02_train_t5.py --resume` restarts from the last 250-step checkpoint, so a preemption costs one
eval interval. The decoder trainer keeps only `best/`, so a preempted E18 decoder arm restarts
from zero — acceptable at 4,000 steps, worth knowing before you count on it.

**Jobs are never placed on a busy GPU.** A pending job is the correct outcome when the node is
full; widening the request to a node someone else is using is not.

## Hardware choices, and the one number that was not ours to choose

| | | |
|---|---|---|
| **Effective batch 64** | 🔴 fixed by the program | `registry.validate()` fails the submit if any arm's `bs × accum ≠ 64` |
| per-device batch × accum | ours | straight from each EXPERIMENT.md — 32×2 for BanglaT5 at 768/512, 16×4 for mT5, 8×8 for the long-sequence and decoder arms |
| precision | ours, constrained | H100 is sm_90 → **bf16**. 🔴 never fp16 |
| parallelism | ours | **1 GPU per arm, many arms at once.** These models are 0.25–1.7B; a second GPU per arm would buy less than a second arm does |
| eval grid | 🔴 fixed | every 250 steps, 300 dev rows, selection on composite |

**Measured throughput, one H100 NVL vs the Kaggle T4 the program was written against:**

| | T4 (fp32) | H100 NVL (bf16) | |
|---|---|---|---|
| BanglaT5 768/512, batch 32×2 | — | **2.2 it/s** | E05: 30k steps ≈ 4 h of compute |
| the 0.85030 run, 384/256, 8×8 | 0.11 it/s | ~5.3 it/s | **≈ 20× faster** |

Wall clock is now dominated by **evaluation**, not training: beam-4 generation over 300 dev rows
every 250 steps. That is deliberate — the metric peaks and then declines, and a coarser grid
straddles the peak.

## What each job does

1. `02_train_t5.py` (seq2seq) or `03_train_causal.py` (E18 decoder arms) → `<exp>/<arm>/best`,
   `run.json`, `ckpt/*/trainer_state.json`
2. `04_decode.py --split dev --limit 300` → `<exp>/<arm>/dev.json`
3. `04_decode.py --split test` → `<exp>/<arm>/submission.csv` + `test.json`

Step 3 matters: **an arm that returns only metrics has to be retrained before it can ever be
submitted**, because inference happens on Kaggle.

## Changes made to `code/` (additive — nothing was reinterpreted)

| File | Change | Why |
|---|---|---|
| `02_train_t5.py` | `--max-steps`, `--save-steps`, `--save-total-limit`, `--early-stopping-patience`, `--resume`, `--out` alias | Every EXPERIMENT.md states its budget in **steps**; the script only took `--epochs`, and the provided `train.ipynb` cells passed `--out`/`--max-steps`/`--save-steps`, which did not exist. `--resume` is what makes preemption cheap. |
| `02_train_t5.py` | `run.json` records `data_dir`, `max_steps`, `eval_steps`, `early_stopping_patience` | Seven experiments train on "the winner of Tier 1", so **which dataset a run saw is a result**, not a constant |
| `04_decode.py` | records the **register read-out** (`হেলো` opener %, `নাসেনিয়া` %) and the raw predictions | Both are required reporting; row-level predictions are what E14/E19 gate on and cannot be recovered later |
| `03_train_causal.py` | **new** — decoder-only trainer | `02_train_t5.py` is seq2seq-only, so E18's decoder-vs-encoder-decoder question was unanswerable without it |
| `10_truncation_report.py` | **new** | every EXPERIMENT.md asks for "% truncated" and nothing measured it |
| `11_build_stage_datasets.py` | **new** | E12's warm-start and E13's multitask corpora, with the dev/test leak check re-asserted rather than assumed |
| `12_teacher_probe.py` | **new** | E20 stage 1, few-shot, in-context examples asserted to come from train only |

## Environment

`/scratch/general/nfs1/u1592009/envs/nascenia` — a plain venv on the system `python3.11`,
because the scratch purge left `miniconda3`'s base interpreter unable to start.

```
torch 2.8.0+cu128 · transformers 4.57.3 (pinned, asserted) · datasets 4.8.5
sentencepiece · normalizer (csebuetnlp, from git) · pandas 3.0.5
```

`python code/metric.py --selftest` → ALL PASS (LCS verified against brute force).
