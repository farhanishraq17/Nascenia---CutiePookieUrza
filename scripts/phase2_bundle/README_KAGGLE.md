# Nascenia Phase 2 — repro pack

Supporting files for reproduction and verification. Companion to the inference notebook
`farhanishraqq/cpu-final-submission`.

## Where the weights are

**Not in this dataset**, deliberately — they ship as their own Kaggle datasets, attached directly
as inputs to the inference notebook so the model travels with the notebook rather than by link:

| model | params | dataset |
|---|---|---|
| champion BanglaT5 (peak5 checkpoint average) | 247,577,856 | `farhanishraqq/nascenia-peak5-checkpoint-average` |
| specialist Qwen3.5-2B (arm D1) | 1,881,825,088 | `farhanishraqq/nascenia-phase2-qwen35-d1` |
| **combined** | **2,129,402,944** | 871M under the 3B cap |

The notebook asserts that combined count from the real safetensors tensors on every run
(cell 3) — never from a model card.

Corpora used by the router, also attached to the notebook:
`farhanishraqq/nascenia-router-corpus` (id resolution) ·
`farhanishraqq/nascenia-aimc-lookup` (retrieval).

## What is here

```
WRITEUP.md        approach, base models, fine-tuning method, external-data disclosure
MANIFEST.md       bundle manifest + sha256 for every file
env/              the dependency/environment files
                  requirements_nascenia.txt      champion  (transformers 4.57.3)
                  requirements_nascenia_q35.txt  specialist(transformers 5.14.1)
                  Dockerfile · setup_envs.sh · verify_envs.sh · README.md
scripts/          run_bundle.sh · bundle_decode.py · swap_specialist.sh · audit_register.py
lookup/           id-resolution corpus for the standalone shell pipeline
verification/     bundle_phase1.csv  — 1000/1000 byte-identical to the scored submission
                  bundle_selftest.csv
docs/             per-model results, shipped arm run.json, specialist-swap procedure
```

## Two ways to reproduce

**1. The notebook (simplest).** Open `farhanishraqq/cpu-final-submission` and Run All. It is
already pointed at the Phase 1 test set and writes a `submission.csv` byte-identical to our
selected submission.

**2. The standalone shell bundle.** For running off Kaggle. Needs the weights from the two
datasets above placed under `weights/`, then:

```
./env/setup_envs.sh          # or: docker build -t nascenia-phase2 -f env/Dockerfile .
./env/verify_envs.sh         # ~30 s machine check, incl. real-tensor param count vs the 3B cap
P2_ENV_CHAMPION=<env> P2_ENV_SPECIALIST=<env> ./scripts/run_bundle.sh <test.parquet> <out.csv>
```

`torch==2.8.0+cu128` is not on plain PyPI. Every provided build path sets
`PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu128`. `git` is also required — both
environments pin the csebuetnlp normalizer as a `git+https` requirement.

Two transformers versions are required and isolated on purpose; `env/README.md` explains why.
