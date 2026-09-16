# Environments — build them once, three ways

The pipeline needs **two** Python interpreters. They cannot be merged: `transformers` 4.57 ties
BanglaT5's `shared`/`lm_head` weights and 5.14 does not, so the two versions decode from
*different* weights. Rules §5.2 requires this bundle to reproduce the submitted leaderboard CSV,
and one shared environment would silently break that.

| branch | env | transformers | model |
|---|---|---|---|
| champion | `nascenia` | **4.57.3** | BanglaT5, 247,577,856 params |
| specialist | `nascenia_q35` | **5.14.1** | Qwen3.5-2B, 1,881,825,088 params |

Because the two branches are **row-disjoint** — an id either resolves into the lookup corpus or it
does not — running each in its own validated stack costs nothing.

---

## 🔴 The one thing that breaks a fresh install

`torch==2.8.0+cu128` **is not on plain PyPI.** A bare `pip install -r requirements_nascenia.txt`
fails on the first line. Every path below sets the PyTorch index for you:

```bash
export PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu128
```

`git` must also be installed — both envs pin the csebuetnlp normalizer as a `git+https`
requirement, and the champion branch refuses to run without it (omitting it left 16/1000 rows
differing from the scored CSV).

---

## Option 1 — Docker (recommended: nothing to resolve)

Both interpreters, pinned, verified at build time. From the **bundle root**:

```bash
docker build -t nascenia-phase2 -f env/Dockerfile .
```

```bash
docker run --rm --gpus all -v "$PWD:/bundle" nascenia-phase2 /bundle/scripts/run_bundle.sh /bundle/lookup/test.parquet /bundle/work/out.csv
```

The image sets `P2_ENV_CHAMPION` / `P2_ENV_SPECIALIST`, so nothing else needs passing. The base is
`python:3.11-slim`, **not** a CUDA image — torch 2.8.0+cu128 ships its whole CUDA 12.8 userspace as
the `nvidia-*-cu12` wheels already pinned in the requirements. Only the host NVIDIA driver matters
(**≥ 570** for cu128).

## Option 2 — one script, no Docker

```bash
./env/setup_envs.sh
```

Builds `./envs/nascenia` and `./envs/nascenia_q35` as plain venvs (the requirements files are pip
freezes, so venv reproduces them exactly), asserts both transformers versions, and prints the
`run_bundle.sh` invocation. Pass a different location as `./env/setup_envs.sh /path/to/envs`, or
point it at a specific interpreter with `P2_PYTHON=/usr/bin/python3.11`.

## Option 3 — by hand

```bash
python3.11 -m venv /path/to/nascenia && /path/to/nascenia/bin/pip install -r env/requirements_nascenia.txt
```

```bash
python3.11 -m venv /path/to/nascenia_q35 && /path/to/nascenia_q35/bin/pip install -r env/requirements_nascenia_q35.txt
```

Then run with `P2_ENV_CHAMPION=/path/to/nascenia P2_ENV_SPECIALIST=/path/to/nascenia_q35`.

---

## Verify before you spend GPU hours

```bash
./env/verify_envs.sh
```

Checks both interpreters, both transformers versions, the normalizer, the GPU and its bf16
capability, both weight directories with their **real** parameter counts read from the tensors
against the 3B cap, and the lookup corpus. Exit 0 means `scripts/run_bundle.sh` will run. It takes
about 30 seconds and replaces finding out three hours into a decode.

Requirements: Python **3.11** (envs frozen at 3.11.13), `git`, ~20 GB disk, NVIDIA driver ≥ 570.
