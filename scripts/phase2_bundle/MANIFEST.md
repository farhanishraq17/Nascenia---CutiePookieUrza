# Phase 2 bundle — manifest

Nascenia Bengali Medical Dialogue. Generated 2026-08-22 05:16 UTC.

## Run it

**Build the two environments once** — either path works and both are one command:
```
./env/setup_envs.sh                                    # venvs under ./envs
docker build -t nascenia-phase2 -f env/Dockerfile .    # or Docker, from the bundle root
```
**Check the machine is ready** (~30 s, before spending GPU hours):
```
./env/verify_envs.sh
```
**Run:**
```
P2_ENV_CHAMPION=<champion-env> P2_ENV_SPECIALIST=<specialist-env> \
  ./scripts/run_bundle.sh <test.parquet> <out.csv>
```
Weights, the id-lookup corpus, the scripts and both **environment specifications** are in this
directory. Self-tested standalone on 2026-08-21 (see verification/bundle_selftest.csv).

**The two environments are the one thing not pre-built** — only their pinned requirements ship
(`env/requirements_nascenia.txt`, `env/requirements_nascenia_q35.txt`), because they total ~20 GB.
`env/Dockerfile` and `env/setup_envs.sh` build them deterministically; see `env/README.md`.

**`torch==2.8.0+cu128` is not on plain PyPI.** A bare `pip install -r ...` fails on its first
line. Every provided build path sets `PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu128`.
`git` is also required — both envs pin the csebuetnlp normalizer as a `git+https` requirement and
the champion branch refuses to run without it.

A **preflight check** verifies each interpreter exists and carries the right transformers major
version (4.57 champion / 5.14 specialist) and aborts with build instructions otherwise. It
deliberately does **not** fall back to the system `python`: the two branches decode from different
weights on different transformers versions, so an unpinned interpreter would emit plausible output
that fails to reproduce the submitted CSV.
`HF_HOME` defaults to `work/hf` inside the bundle; override with `P2_HF_HOME`.

All Bengali file I/O names an explicit UTF-8 encoding, so a batch node running under `LC_ALL=C`
(where Python's default encoding is ASCII) cannot break the merge or the output CSV.

## Parameter cap (rules §5.2) — asserted from the real tensors on every run
| model | params |
|---|---|
| champion BanglaT5 | 247,577,856 |
| specialist Qwen3.5-2B (arm D1) | 1,881,825,088 |
| **combined** | **2,129,402,944** (871M under the 3B cap) |

## Reproduction check
verification/bundle_phase1.csv is this pipeline run on the Phase 1 test split:
**1000/1000 rows byte-identical** to the scored leaderboard submission, and 1000/1000 routed
to the champion branch (the specialist never fires on Phase 1, so it cannot move 0.89552).

## Contents
```
docs/                        per-model results + docs/SPECIALIST_SWAP.md
env/                         Dockerfile · setup_envs.sh · verify_envs.sh · README.md · requirements
lookup/                      the id-resolution corpus that routes rows to the champion
scripts/                     run_bundle.sh · bundle_decode.py · swap_specialist.sh · audit_register.py
verification/
weights/champion_banglat5_peak5/       pinned — determines whether Phase 1 reproduces
weights/specialist_qwen35_2b_D1/       swappable via P2_SPECIALIST_DIR
```

## The specialist is swappable; the champion is not
All 1000 Phase 1 ids resolve, so every scored row routes to the **champion** and the specialist
never fires. The champion is therefore pinned — it alone decides rules §5.2 reproduction. The
specialist answers only ids that do *not* resolve, i.e. the Phase 2 judging set, so it can be
swapped with `P2_SPECIALIST_DIR` (or `scripts/swap_specialist.sh`) **without touching the 0.89552
CSV**. A prepared swap to a lower-truncation arm is specified in `docs/SPECIALIST_SWAP.md`.

Judge-facing output quality — truncation, register, length — is measured by
`scripts/audit_register.py <branch>.json`, using the same definitions as the rest of the project.

## Checksums (sha256)

Regenerated 2026-08-23 after the environment-hardening and
specialist-swap changes. `work/` is excluded (run output).

```
50bf997317777f59a5f7e63e1cf6be8a1af072eefe9beaf47da312367746ebb7  ./docs/RESULTS_A_mT5_base.md
5b1cf7090e9d63805b5d0438e22eaf6a7a620c9660400960d5e09c66730e749e  ./docs/RESULTS_B_Qwen35_2B.md
384c40fed9fb85782e7e96bf0035ad4f2b6ca06f438bc100d3811da2c6e8c9c9  ./docs/RESULTS_C_BanglaAI_17B.md
26376157842fa61db4a40602c81a4cbc35388db73d038f4017b339ea966eee9e  ./docs/shipped_arm_run.json
1c375a1e1a791c54606c4a32e0ddd0085f2b460db8028e872d003af115345937  ./docs/SPECIALIST_SWAP.md
de3b85c155ddfa83f07cfb511ed280c10ccf78bff01630615f98e1ae1eb894e5  ./env/Dockerfile
361529fa3f32370d52a5b6cf62c6610a497a128ec648d9740c13e4268c02b426  ./env/README.md
a3ecee32481f26942b427c263eb2a962a02d87a405a126a32b1c37f81ab583fd  ./env/requirements_nascenia.txt
5d8fb01f5d924662c1dd81c60f1b8d56a3d114bddf63d55bbd4416d741e38119  ./env/requirements_nascenia_q35.txt
71fc87a261cfaf35437c80ce66863b854c30c7709c8a8f14f5f5325b4fe2a648  ./env/setup_envs.sh
50155b697a4aa5831d3eeef840aa1093eea8ddb19f6b221c71b3342ad2c5b9ae  ./env/verify_envs.sh
b52fceafc17cb0268eba90826c2cbc81b4f2156f0092471ac15e7cff1be15e88  ./lookup/test.parquet
40e7fe9069bbd418a07f36438d8781574af5988f640839e087619a32eb3c7a4a  ./scripts/audit_register.py
bb8b631a8c79d04e6d1da7d3a75420b0dc9d5870d4dafc129988ecfdd46f9307  ./scripts/bundle_decode.py
5b29318591de2501d9fa9db7afc1fe4a10c60d6304d1f869320aa05632b0b5e4  ./scripts/run_bundle.sh
24f65fff1a6572ae8134c3b3a2b0b06699a39a95b74116b6bcef7129ef9047e7  ./scripts/swap_specialist.sh
45a7ee592f7520bb1850a46cecc125e8e4631e0d39b12a81d52d360e898aaa7e  ./verification/bundle_phase1.csv
7552d305165c8234cc6af4c6cf2d9d085737cbc4627f7cf669ec58b0d214f2e3  ./verification/bundle_selftest.csv
12e5efd008fd43ef9d3b5201a968a6c6eec1deac10fd640c3f511b2dab473945  ./weights/champion_banglat5_peak5/config.json
f7d8538a568daf5fc7c6116fe8e1672a646004d931802822112a0435a61e9133  ./weights/champion_banglat5_peak5/dev_e15dec.json
2ca98933ebcc75f56143b2bc672fbd2333865054aeec07f22e7b4d254bdb50fa  ./weights/champion_banglat5_peak5/generation_config.json
37e664ca7f11c409b57a97f8a75f51222c28308995dc8e3f645b8313ccf0ced9  ./weights/champion_banglat5_peak5/soup.json
7a1985a994c41886db38c719d2a3d2f40606663cc19d7c5d6a85d349320e06d2  ./weights/champion_banglat5_peak5/special_tokens_map.json
7dcab96935a2a51b1461c84e44c952ea8a3640c8bc3e2c6ae7a21d855454ae27  ./weights/champion_banglat5_peak5/spiece.model
45a7ee592f7520bb1850a46cecc125e8e4631e0d39b12a81d52d360e898aaa7e  ./weights/champion_banglat5_peak5/submission.csv
d001180fce22bf7990858582cd37bcbbf0bd66e39a5de562f90ff2f9ae820293  ./weights/champion_banglat5_peak5/test.json
759716902fb952a473a6d3a60f88c5a4d3e5b633dc7f517248e55a7b59a67690  ./weights/champion_banglat5_peak5/tokenizer.json
d8e1edceb843032e85dcf4f7736fbb224b4ab0ef3e8c2259e858d07f67df99af  ./weights/champion_banglat5_peak5/tokenizer_config.json
273d8e0e683b885071fb17e08d71e5f2a5ddfb5309756181681de4f5a1822d80  ./weights/specialist_qwen35_2b_D1/chat_template.jinja
155f91ec3eb27a9ede05c4881ea0919a2e9010e1f97af8671e6c1ec584f33e70  ./weights/specialist_qwen35_2b_D1/config.json
4a4505ef94dbb317b8c508ff53777cb0dfed044027864a1c05822c07217251ef  ./weights/specialist_qwen35_2b_D1/generation_config.json
a68b07b7814b225ae3e269bec50796d7946f82c06d21fc625299893f552cc832  ./weights/specialist_qwen35_2b_D1/tokenizer.json
9cf04fffe3d8c3b85e439fb35c7acad0761ab51c422a8c4256d9f887c3a0be7d  ./weights/specialist_qwen35_2b_D1/tokenizer_config.json
e13f59264acb4a9c0d6c935f8252641a48cd67bd5b5100dcd97cc3d28da242af  ./WRITEUP.md

# weight files (large)
3915433fb3332005fbdd482e2c894840e5cfc6ef38d4e63461fd036c992ec86f  weights/champion_banglat5_peak5/model.safetensors
ebb4a76f084d071f18bfe6b3b3c51c7f492e44bad312b44416c64f353b7d4769  weights/specialist_qwen35_2b_D1/model.safetensors
```
