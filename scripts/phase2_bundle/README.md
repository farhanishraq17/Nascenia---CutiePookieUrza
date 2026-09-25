# Phase 2 repro pack

The standalone, off-Kaggle version of the Phase 2 pipeline, as delivered to the organizers in the Kaggle dataset `farhanishraqq/nascenia-phase2-repro-pack`. The organizer-facing description is [README_KAGGLE.md](README_KAGGLE.md); the write-up is `PHASE2_WRITEUP.md`.

| path | what |
|---|---|
| [`scripts/run_bundle.sh`](scripts/run_bundle.sh) | the inference entry point: `./scripts/run_bundle.sh <test.parquet> <out.csv>` — routes each row, runs each branch in its own environment, merges, and asserts the 3B cap from the real tensors |
| [`scripts/bundle_decode.py`](scripts/bundle_decode.py) | one branch of the pipeline (called once per branch) |
| [`scripts/audit_register.py`](scripts/audit_register.py) | judge-facing quality check: `হেলো`/brand rates, length, truncation |
| [`scripts/swap_specialist.sh`](scripts/swap_specialist.sh) · [`docs/SPECIALIST_SWAP.md`](docs/SPECIALIST_SWAP.md) | install a different specialist checkpoint without touching the champion |
| [`docs/shipped_arm_run.json`](docs/shipped_arm_run.json) | full config and trajectory of the shipped specialist (arm D1) |
| [`env/`](env/README.md) | `requirements_nascenia.txt` (champion, `transformers==4.57.3`), `requirements_nascenia_q35.txt` (specialist, `5.14.1`), `Dockerfile`, `setup_envs.sh`, `verify_envs.sh` |
| [`MANIFEST.md`](MANIFEST.md) | the bundle's file list with sha256 for every artifact |

**Not in this repo:**

- `weights/champion_banglat5_peak5/` → Kaggle `farhanishraqq/nascenia-peak5-checkpoint-average`
- `weights/specialist_qwen35_2b_D1/` → Kaggle `farhanishraqq/nascenia-phase2-qwen35-d1`
- `lookup/test.parquet` → the Phase 1 test rows in the champion's input format (data)
- `verification/bundle_phase1.csv` → identical to [`notebooks/phase1_submissions/08_peak5_inference_LB0.89552/data/submission_reference.csv`](../../notebooks/phase1_submissions/08_peak5_inference_LB0.89552/data/submission_reference.csv) (sha256 `45a7ee59…aa7e`)
- `docs/RESULTS_{A,B,C}_*.md` → [`notebooks/phase2_specialist/*/RESULTS.md`](../../notebooks/phase2_specialist/README.md)

Put `weights/` and `lookup/` next to `scripts/`, then follow [env/README.md](env/README.md): build the two environments, run `./env/verify_envs.sh`, and run the bundle. The bundle is the two-branch design (id resolves → champion, else specialist). The final Kaggle notebook added the retrieval branch and dataset-level id verification on top: [`notebooks/phase2_submissions/09_cpu_final_submission_FINAL/`](../../notebooks/phase2_submissions/09_cpu_final_submission_FINAL/).
