# Scripts

All project code. Everything is plain Python (3.11–3.13) or bash; training and inference scripts need `torch`, `transformers==4.57.3` (BanglaT5) or `5.14.1` (Qwen3.5), `pandas`, `pyarrow`, `sentencepiece`, and the [csebuetnlp normalizer](https://github.com/csebuetnlp/normalizer). Scripts that must run in more than one place take their paths as arguments rather than deriving them from their own location.

| folder | what |
|---|---|
| [pipeline/](#pipeline) | **the canonical pipeline** — prep, training, decoding, metric, dataset builders, checkpoint averaging |
| [analysis/](#analysis) | early local analysis: baselines, BERTScore probe, constant optimiser, corpus curation |
| [kaggle/](#kaggle) | guarded push tool, the `nascenia-code` snapshot Kaggle notebooks attach, notebook generators |
| [chpc_slurm/](#chpc_slurm) | how the GPU program ran: arm registry, job submitter, pool runners, 100+ job scripts |
| [phase2/](#phase2) | Phase 2 study: data and index builders, notebook generator, router and its validators |
| [phase2_bundle/](#phase2_bundle) | the offline repro pack handed to the organizers |
| [e17_draft_quality/](#e17_draft_quality) | translator bake-off tools |

Quick check after installing:

```bash
python scripts/pipeline/metric.py --selftest     # LCS vs brute force on random pairs
python scripts/pipeline/02_train_t5.py --help     # must list --data-dir and --precision
python scripts/pipeline/04_decode.py --help       # must list --data-dir
```

---

## pipeline

The final versions, as used by the GPU program and the shipped champion (originally `fine_tune_project/code/`). Details and the two fixes that must never be "simplified" away: [pipeline/README.md](pipeline/README.md).

| script | what it does |
|---|---|
| [`metric.py`](pipeline/metric.py) | exact local re-implementation of the Phase 1 composite (Token F1, ROUGE-L via NumPy LCS, BERTScore). `--selftest` checks the LCS. **Rank runs on Token F1 / ROUGE-L** — the local BERTScore model differs from the organizers'. |
| [`01_prep.py`](pipeline/01_prep.py) | clean the competition data (brand fix, NFC, degenerate-row filter) and freeze the split: **`--seed 42 --dev-size 5000`, never anything else** |
| [`02_train_t5.py`](pipeline/02_train_t5.py) | seq2seq trainer (BanglaT5 / mT5 / IndicBART): Adafactor, step budgets, `--resume`, refuses to train on CPU, selects the best checkpoint on generated composite, never loss |
| [`03_train_causal.py`](pipeline/03_train_causal.py) | decoder-only counterpart (E18 zoo, Phase 2 specialist): chat template, prompt-masked loss |
| [`04_decode.py`](pipeline/04_decode.py) | beam / greedy / MBR decoding, sweeps, submission writer. fp32 by default with a finite-logits probe — fp16 T5 silently decodes garbage. |
| [`05_build_transfer.py`](pipeline/05_build_transfer.py) | the original register-transfer dataset (draft → target) |
| [`07_build_transfer_en.py`](pipeline/07_build_transfer_en.py) | English + draft → target (superseded by `09`, kept for provenance) |
| [`08_trim_mt5_vocab.py`](pipeline/08_trim_mt5_vocab.py) | trim mT5's 250k vocabulary to the ~23k tokens the corpus uses |
| [`09_build_inputs.py`](pipeline/09_build_inputs.py) | compose any input combination: `--fields q,en,bn` (the champion uses `en,bn`) |
| [`10_truncation_report.py`](pipeline/10_truncation_report.py) | how much each experiment's sequence cap cuts |
| [`11_build_stage_datasets.py`](pipeline/11_build_stage_datasets.py) | warm-start and multitask datasets (E12, E13) |
| [`12_teacher_probe.py`](pipeline/12_teacher_probe.py) | E20: can a large few-shot teacher do register transfer? |
| [`13_disagreement.py`](pipeline/13_disagreement.py) | the pairwise-disagreement gate that E14/E19 must pass before pooling |
| [`14_decode_sweep.py`](pipeline/14_decode_sweep.py) | E15 decoder sweep on a trained checkpoint |
| [`15_phase2_audit.py`](pipeline/15_phase2_audit.py) | E16: truncation, repetition and tautology rates vs the references |
| [`16_pool_mbr.py`](pipeline/16_pool_mbr.py) | consensus selection over existing prediction sets |
| [`17_model_soup.py`](pipeline/17_model_soup.py) | average checkpoint **weights** — produced the shipped `ckptavg_peak5` |
| [`18_backtranslate.py`](pipeline/18_backtranslate.py) | E21: a second draft for every training row |
| [`19_build_retrieval.py`](pipeline/19_build_retrieval.py) | E22: nearest-neighbour exemplars from train only |

## analysis

Local analysis scripts from the first days (originally `NOTEBOOKS/`). They expect the original working tree's `DATA/` layout — the `00_*` scripts hardcode its Windows paths — so adjust the paths before re-running them.

| script | what it does |
|---|---|
| [`00_eda_baselines.py`](analysis/00_eda_baselines.py) | constant / retrieval / random baselines on held-out rows → [`00_baseline_results.txt`](analysis/00_baseline_results.txt) |
| [`00_bertscore_probe.py`](analysis/00_bertscore_probe.py) | how much BERTScore separates good from bad answers (barely) |
| [`03_optimize_constant.py`](analysis/03_optimize_constant.py) | greedy token-overlap-optimal constant (CONST-OPT-01) → [`optimized_constant.json`](analysis/optimized_constant.json) |
| [`06_build_master_c.py`](analysis/06_build_master_c.py) | builds `MASTER_C_BENGALI` and `aligned_pairs.csv` with leak removal; asserts 100% dev/test coverage |
| [`08_lexical_gap.py`](analysis/08_lexical_gap.py) | LEX-01: where the champion loses Token F1, token by token |
| [`09_draft_leverage.py`](analysis/09_draft_leverage.py) | DRAFT-02: how much draft quality moves the champion |

## kaggle

| file | what |
|---|---|
| [`kpush.py`](kaggle/kpush.py) | **guarded `kaggle kernels push`** — refuses a GPU notebook that is not pinned to `NvidiaTeslaT4` and checks the kernel lands under the expected account. `python scripts/kaggle/kpush.py <kernel-dir> [account]` |
| [`build_ft_folders.py`](kaggle/build_ft_folders.py) | rebuilt the local per-run training folders from downloaded outputs |
| [`nascenia-code/`](kaggle/nascenia-code/) | snapshot of the Kaggle `nascenia-code` dataset that the Kaggle training and decode notebooks attach. Its `02_train_t5.py` / `04_decode.py` are earlier revisions of `pipeline/`: the 0.85030 run's copy differs from this one only in `logging_steps` and `dataloader_num_workers`, and `pipeline/` later added step budgets, `--resume`, the CPU refusal and more decoding options. `07_build_transfer_en.py` here is the mT5-oriented Kaggle variant. |
| [`notebook_builders/`](kaggle/notebook_builders/) | the generators behind notebooks that were written from Python (`build_nascenia-<kernel>.py` builds `nascenia-<kernel>.ipynb`). Each was run from its notebook's own folder, so output paths are relative to that folder. |

## chpc_slurm

How the GPU experiment program ran on the CHPC clusters granite and notchpeak (originally `fine_tune_project/_slurm/`). Read [chpc_slurm/README.md](chpc_slurm/README.md) first.

| file | what |
|---|---|
| [`registry.py`](chpc_slurm/registry.py) | every experiment arm as data (model, input, caps, budget) |
| [`submit.py`](chpc_slurm/submit.py) | turns registry entries into SLURM jobs, one GPU per arm |
| [`run_pool.sh`](chpc_slurm/run_pool.sh) · [`run_pool_multi.sh`](chpc_slurm/run_pool_multi.sh) | saturate the GPUs of allocations already held, from one shared work queue |
| [`collect.py`](chpc_slurm/collect.py) · [`final_analysis.sh`](chpc_slurm/final_analysis.sh) | scoreboard over every landed arm; all write-up numbers in parallel (reports in [`../notebooks/chpc_experiments/_analysis/`](../notebooks/chpc_experiments/_analysis/)) |
| `nasc-E*.sbatch` | one job per arm. [`nasc-E05-english_draft.sbatch`](chpc_slurm/nasc-E05-english_draft.sbatch) is the exact invocation that trained the champion. |
| `smoke*.sbatch` · `probe.sbatch` · `redecode*.sbatch` | pipeline smoke tests, GPU probe, re-decodes after BUG-04/06 |
| [`tasks/`](chpc_slurm/tasks/) · [`tasks_a800/`](chpc_slurm/tasks_a800/) | per-arm task scripts for the pool runners (convergence runs, seeds, soups, decoder sweeps, peak-5 composition and verification) |
| [`grn/`](chpc_slurm/grn/) · [`np/`](chpc_slurm/np/) · [`e24/`](chpc_slurm/e24/) | job scripts for the granite and notchpeak partitions and for E24 |
| [`watch/`](chpc_slurm/watch/) | queue and job watchers |

The job scripts keep the cluster's absolute paths (`/scratch/general/nfs1/<user>/…`), account and partition names. Change them before reusing anything.

## phase2

The Phase 2 study (originally `Phase2 Final architecture/`). Its specs and results are in [`../notebooks/phase2_specialist/`](../notebooks/phase2_specialist/README.md).

| file | what |
|---|---|
| [`shared/build_index.py`](phase2/shared/build_index.py) | step 1: the 118,912-row training pool and its `multilingual-e5-base` retrieval index, with dev/test leak asserts |
| [`shared/build_data.py`](phase2/shared/build_data.py) | step 2: every dataset variant — `plain`, `rag`, `plain_core_only`, `plain_core_plus_*` |
| [`shared/build_notebooks.py`](phase2/shared/build_notebooks.py) | generates `train.ipynb` + `inference.ipynb` for all three models |
| [`shared/evaluate.py`](phase2/shared/evaluate.py) · [`shared/metric.py`](phase2/shared/metric.py) | shared scoring harness (the metric is byte-identical to `pipeline/metric.py`, copied so the folder is self-contained) |
| [`router/router.py`](phase2/router/router.py) · [`router/router_4path.py`](phase2/router/router_4path.py) | router prototypes |
| [`router/build_inference_nb.py`](phase2/router/build_inference_nb.py) | generates the routed inference notebook |
| [`router/build_branch3_probe.py`](phase2/router/build_branch3_probe.py) | extracts the rows the retrieval branch would serve, for the branch-3 paired test |
| `router/validate_*.py` | router measurements. `validate_router.py` had no leak exclusion; `validate_router_leakfree.py` is the corrected re-measurement that retracted ROUTER-01 (see [router/README.md](phase2/router/README.md)). |

## phase2_bundle

The standalone repro pack delivered to the organizers (the Kaggle dataset `farhanishraqq/nascenia-phase2-repro-pack`, minus its lookup data and verification CSVs). See [phase2_bundle/README.md](phase2_bundle/README.md).

## e17_draft_quality

| file | what |
|---|---|
| [`run_local_models.py`](e17_draft_quality/run_local_models.py) | translate the E17 probe rows with a local open-weights model (NLLB, Qwen3) |
| [`score_all.py`](e17_draft_quality/score_all.py) | score every candidate translation against the competition target |
