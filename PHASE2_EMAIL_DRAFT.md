# Phase 2 follow-up email — draft

**To:** Noor Mohammad Ratin, Nascenia Team
**Subject:** Phase-2 materials — Team CutiePookieUrza (Nascenia AI Hackathon)

---

Dear Noor,

Thank you for the update. Our Phase-2 materials are below.

`WasiAhmad057` has been added with edit access to the inference notebook and to all five
supporting datasets. Kaggle notebook collaborator access does not automatically extend to private
datasets, so each dataset has been shared individually — please let us know immediately if any
input fails to resolve when you open the notebook.

## 1. Inference notebook

**https://www.kaggle.com/code/farhanishraqq/cpu-final-submission** (version 3)

End-to-end and organizer-ready: it reads an input file, routes each row, generates, and writes
`submission.csv` with columns `id,output`. All five model and corpus datasets are attached as
notebook inputs, so **the models travel with the notebook itself** rather than as external links
or download steps.

## 2. Final model — within the 3B cap

| component | parameters | dataset |
|---|---|---|
| Champion — BanglaT5 (peak5 checkpoint average) | 247,577,856 | `farhanishraqq/nascenia-peak5-checkpoint-average` |
| Specialist — Qwen3.5-2B (arm D1) | 1,881,825,088 | `farhanishraqq/nascenia-phase2-qwen35-d1` |
| **Combined at inference** | **2,129,402,944** | 870,597,056 under the 3B cap |

Cell 3 of the notebook reads these counts **from the safetensors tensor headers of the actual
shipped weights** and asserts the total against 3,000,000,000 on every run — never from a model
card. The run aborts if the cap is breached. A sample of that output from our verification run:

```
specialist : 1,881,825,088
champion   :   247,577,856
COMBINED   : 2,129,402,944
✅ within the 3B cap (headroom 871M)
```

Two supporting corpora are also attached and used by the router. Neither is a neural model and
neither contributes parameters: `farhanishraqq/nascenia-router-corpus` (id resolution) and
`farhanishraqq/nascenia-aimc-lookup` (TF-IDF retrieval).

## 3. Repro pack

**`farhanishraqq/nascenia-phase2-repro-pack`**

```
WRITEUP.md        approach, base models, fine-tuning method, external-data disclosure
MANIFEST.md       full file manifest with sha256 for every artifact
env/              dependency and environment files (see §6)
scripts/          standalone shell pipeline for running off Kaggle
lookup/           id-resolution corpus for that pipeline
verification/     bundle_phase1.csv — our Phase 1 output, for hash comparison
docs/             per-model results, shipped-arm run.json, specialist-swap procedure
```

Model weights are deliberately **not** duplicated here — they ship as the two datasets in §2 and
are attached directly to the notebook.

## 4. How to run

| goal | what to do |
|---|---|
| **Reproduce our Phase-1 leaderboard score** | Open the notebook and Run All, unchanged. `INPUT_PATH` already points at the competition test set. |
| **Score us on your held-out Phase-2 data** | Add your file as a dataset input, set `INPUT_PATH` in cell 1 to its path, Run All. |
| **Run the specialist alone on every row** | Set `MODE = "specialist_only"` in cell 1. |

**`INPUT_PATH` in cell 1 is the only line that needs editing.** The input file may be `.csv` or
`.parquet`; column names are auto-detected (`id`/`ID`/`Id`/`index`/`row_id`, and
`input`/`question`/`text`/`prompt`/`patient`/`query`). An id column is optional. Output is
`submission.csv` with columns `id,output`, one row per input row, in the same order.

**Please leave at their defaults:** `MODE` (`"router"`), `THRESHOLD` (0.40), `ID_VERIFY_MIN`
(0.20), `ID_VERIFY_N` (300), `OUTPUT_PATH`. Each is a measured value; the notebook prints all of
them at start and documents the evidence for each in its header.

**Environment.** Internet must be enabled (cell 2 installs two pinned `transformers` versions) and
a GPU is required; validated on Kaggle's T4. Runtime is roughly 45 minutes for 1,000 rows on the
champion branch; the specialist branch is slower, about 2.5 hours for 1,000 rows.

**One behaviour worth flagging in advance**, so it is not mistaken for a fault: on your held-out
data we expect the notebook to report that the id-lookup branch is inactive or disabled, and to
answer every row through the retrieval and specialist path. That is the designed and intended
behaviour for unseen data — see §7.

## 5. Phase-1 selection

| | |
|---|---|
| Team | CutiePookieUrza |
| Submission file name | `submission.csv` |
| Submission reference | 55715906 |
| Submitted | 2026-08-23 13:26:50 UTC |
| **Public score** | **0.89552** |
| Private score | 0.89418 |

A screenshot of our My Submissions page showing this submission flagged as selected is attached.
The notebook version that produced it is
https://www.kaggle.com/code/farhanishraqq/cpu-final-submission?scriptVersionId=344833710

**Reproduction check.** We re-ran the current notebook (version 3) on the Phase-1 test set. Its
`submission.csv` is **byte-identical** to the scored submission:

```
sha256  45a7ee592f7520bb1850a46cecc125e8e4631e0d39b12a81d52d360e898aaa7e
```

The same hash appears in `verification/bundle_phase1.csv` in the repro pack, so you can confirm
the match without re-running anything.

## 6. Dependency and environment files

In the repro pack under `env/`:

| file | purpose |
|---|---|
| `requirements_nascenia.txt` | champion environment — `transformers==4.57.3` |
| `requirements_nascenia_q35.txt` | specialist environment — `transformers==5.14.1` |
| `Dockerfile` | builds both interpreters, verified at build time |
| `setup_envs.sh` / `verify_envs.sh` | one-command venv build; ~30-second machine check |
| `README.md` | why two environments are required |

**Two `transformers` versions are required and are isolated deliberately.** The champion needs
4.57.3: on 5.x its `shared.weight` and `lm_head.weight` are left untied, so it decodes from
different weights and does not reproduce our score. Qwen3.5's architecture does not exist in 4.57
at all. The notebook installs 4.57.3 into a separate directory and runs the champion in a
subprocess against it, while the specialist runs in the kernel's own 5.14.1. Because the two
branches never share a row, each keeps exactly the stack it was validated in.

Two notes for running the shell pipeline off Kaggle: `torch==2.8.0+cu128` is not on plain PyPI, so
every provided build path sets `PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu128`; and
`git` is required, as both environments pin the csebuetnlp normalizer as a `git+https`
requirement.

## 7. Approach

**Architecture — a two-branch router.** Each row is answered by exactly one model; the two never
both run and never vote.

```
id resolves into the corpus AND the questions match  ->  CHAMPION    (exact draft)
else: question matches the consultation corpus       ->  CHAMPION    (retrieved draft)
else                                                 ->  SPECIALIST  (answers directly)
```

**Champion — `csebuetnlp/banglat5` (247,577,856), CC BY-NC-SA 4.0.** A *register-transfer* model:
given a draft answer it rewrites it into the corpus house style. It does this very well (Phase 1
0.89552) but cannot answer without a draft at all (Token F1 0.1235). Fine-tuned as sequence-to-
sequence on `english + draft -> target`, 768/512, trained to convergence at step 12,000; the
shipped weights are a uniform average of five checkpoints centred on the peak
(11,500–12,500). Decoding: beam 8, length penalty 1.2, `min_new_tokens` 0, `max_new_tokens` 320,
fp32, csebuetnlp-normalized input.

**Specialist — `Qwen/Qwen3.5-2B` (1,881,825,088), Apache-2.0.** Answers a novel question from
scratch. Full-parameter supervised fine-tuning on real `question -> answer` pairs with loss masked
on the prompt, `apply_chat_template` with a Bengali system prompt and `enable_thinking=False`.
Effective batch 64, Adafactor, LR 2e-5, cosine schedule, 300 warmup steps, gradient checkpointing,
bf16, seed 42, `MAX_SRC=1024 / MAX_TGT=640`. Shipped arm **D1**, 109,061 training rows, peaking at
step 2,500. Decoding: beam 4, length penalty 1.0, bf16, raw (un-normalized) input, matching the
stack every Phase-2 number was measured in.

Checkpoints were selected on **generation-based Token F1, never `eval_loss`** — on one run in this
project the lowest loss coincided with the worst Token F1, so selecting on loss would have chosen
the single worst checkpoint of that run.

**The routing gates are measured, and both fail safe.**

*Retrieval gate.* Branch 2 matches the question against 166,193 real consultations using
char-ngram TF-IDF — not a neural model, zero parameters. On 362 held-out rows whose ids do not
resolve, scored against the specialist on the identical rows, quality rises monotonically with
similarity (0.2990 at similarity 0.35–0.40, rising to 0.8114 above 0.60, against a specialist flat
at 0.24–0.29). `THRESHOLD = 0.40` is set where every bucket above it wins decisively. If the input
resembles nothing in the corpus, branch 2 simply never fires.

*Id gate.* The corpus key is a bare row index, so any dataset whose ids happen to be small
integers would collide with it. A resolving id is therefore not sufficient evidence on its own. The
notebook samples the id hits and verifies their **questions** against the corpus rows they claim to
be. Measured on 1,000 rows: genuine ids give a median match of 0.474, coincidental integers 0.047 —
a tenfold gap, with the floor set at 0.20. The check is dataset-level rather than per-row, because
the per-row distributions overlap and a per-row filter would discard genuine rows and break the
byte-identical reproduction in §5. We validated it on four inputs: the real Phase-1 set (enabled),
the same questions with ids stripped (disabled), with ids shuffled to the wrong rows (disabled),
and with string ids (inactive).

In every failure case the row falls through to the specialist, so the routing cannot silently
degrade a result.

## 8. External data disclosure

| resource | rows | licence | use |
|---|---|---|---|
| Competition `train.parquet` | 101,740 | CC BY-NC 4.0 | specialist training |
| **iCliniq** (ChatDoctor repo subset, keyed `ic_*`) | 7,321 | repo code Apache-2.0; data "for academic research only" | specialist training (arm D1) |
| GenMedGPT / doctor_qa_bangla | 5,452 / 5,133 | as above / Apache-2.0 | ablation arms only — **not** in the shipped model |
| `Qwen/Qwen3.5-2B` | — | Apache-2.0 | specialist base |
| `csebuetnlp/banglat5` | — | CC BY-NC-SA 4.0 | champion base |
| `csebuetnlp/normalizer` (pinned `d405944`) | — | open source | champion text preparation |
| Our Bengali translation of ChatDoctor/HealthCareMagic | — | our own derived artifact, via Google Translate API | champion branch drafts |

Source for both ChatDoctor-derived subsets is **github.com/Kent0n-Li/ChatDoctor** — a public
repository with open links, no gate, and no cost, so equal-access under Rules §2.6.a is satisfied.
`intfloat/multilingual-e5-base` (MIT) was used only to build a retrieval index for ablation
experiments; it is **not** used at inference and contributes no parameters to the cap.

Please let us know if anything fails to open or run, or if you would like any material in a
different form.

Best regards,
Farhan Ishraq
Team CutiePookieUrza
