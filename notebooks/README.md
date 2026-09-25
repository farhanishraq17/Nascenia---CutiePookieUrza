# Notebooks

Every notebook the project ran, grouped by phase and ordered in time. Kaggle notebooks sit next to their `kernel-metadata.json` (slug, GPU pin, attached datasets) and, where we downloaded them, the run log and small result JSONs. Kaggle kernels are **private**; model weights and data are not in git (see [../datasets/README.md](../datasets/README.md)).

The code these notebooks call lives in [../scripts/](../scripts/README.md). Kaggle notebooks attach it as the `nascenia-code` dataset ([snapshot](../scripts/kaggle/nascenia-code/)), and generated notebooks have their generator in [../scripts/kaggle/notebook_builders/](../scripts/kaggle/notebook_builders/).

| folder | what |
|---|---|
| [phase1_kaggle_training/](#phase1_kaggle_training) | single-T4 training runs: question→answer sweep, then register transfer |
| [phase1_submissions/](#phase1_submissions) | leaderboard submissions, 0.57849 → 0.89552 |
| [phase1_probes/](#phase1_probes) | decoding experiments, the ALIGN-01 probe, translator probes |
| [chpc_experiments/](#chpc_experiments) | the E01–E24 GPU program (specs, results, run records) |
| [phase2_specialist/](#phase2_specialist) | Phase 2 model study: which model can answer unseen questions |
| [phase2_submissions/](#phase2_submissions) | router notebooks, Phase 2 diagnostics, and the final organizer notebook |

---

## phase1_kaggle_training

Kaggle, single T4, fp32, `transformers==4.57.3`. Dev numbers are the 300-row subset, beam 4. Full table: [FINE_TUNING_LOG.md](../FINE_TUNING_LOG.md).

| folder | Kaggle kernel | run | Token F1 / ROUGE-L | notes |
|---|---|---|---|---|
| `01_banglat5_seed42` | `farhanishraqq/nascenia-banglat5-v2` | question→answer, lr 1e-4 (TRAIN-01) | 0.2051 / 0.1433 | first clean run, below the constant string |
| `02_banglat5_seed1337` | `didhitinahid/nascenia-banglat5-v2` | question→answer, lr 3e-4 | 0.2321 / 0.1666 | the pinned-transformers fix that made training work |
| `03_sweep_A_lr3e4` | `salam2026/nascenia-sweep-a-lr3e4` | lr 3e-4, reference arm | 0.2365 / 0.1705 | still climbing at step 3,000 |
| `04_sweep_B_4epoch` | `salam2026/nascenia-sweep-b-4epoch` | 4 epochs | — | cancelled |
| `05_sweep_C_lr1e3` | `tashintahir/nascenia-sweep-c-lr1e3` | **lr 1e-3** | **0.2576 / 0.1776** | best question→answer arm |
| `06_sweep_D_smooth` | `tashintahir/nascenia-sweep-d-smooth` | label smoothing 0.1 | 0.2360 / 0.1670 | inside the noise floor |
| `07_sweep_E_lr1e3_4ep` | `ishmamahmid/nascenia-sweep-e-lr1e3-4ep` | lr 1e-3, 4-epoch budget | 0.2539 / 0.1787 | same peak step as C → budget steps, not epochs |
| `08_sweep_F_batch32` | `ishmamahmid/nascenia-sweep-f-batch32` | effective batch 32 | 0.2442 / 0.1746 | |
| `09_sweep_G_lr3e3` | `ishmamahmid/nascenia-sweep-g-lr3e3` | lr 3e-3 | 0.2390 / 0.1706 | the LR curve turns over — LR tuning closed |
| `10_xfer_seed11_LB0.85030` | `tashintahir/nascenia-xfer-banglat5` | **register transfer**, draft → target | **0.7724 / 0.7324** | the 0.85030 model (`PROVEN_xfer_seed11` in older notes) |
| `11_xfer_seed23` | `salam2026/nascenia-xfer-banglat5` | register transfer, seed 23 | 0.7723 / 0.7332 | replicate — seeds agree to 0.0001 |
| `12_mt5_english_draft` | `fatkhato/nascenia-mt5-en` | mT5-base on english + draft | — | Kaggle-side mT5 attempt, with a runtime-projection guard |

Sweep and transfer folders also hold `run.json` (config + metrics), `trainer_state_step*.json` (the full eval trajectory) and `prep_report.txt`. Worker accounts that could not join the competition read the data from a private `nascenia-data` dataset.

## phase1_submissions

| folder | Kaggle kernel | public LB | what |
|---|---|---|---|
| `01_constant_probe_LB0.57849` | `farhanishraqq/nascenia-constant-probe` | **0.57849** | one hand-written boilerplate answer × 1,000 — a metric probe, never a candidate. Includes the scored `submission.csv` and log. |
| `02_submit_banglat5` | `farhanishraqq/nascenia-submit-banglat5` | — | first model-submission notebook (superseded) |
| `03_submit_qa_arms/{a-lr3e4,c-lr1e3,f-batch32}` | `farhanishraqq/nascenia-submit-*` | *pred.* 0.5722–0.5800 | decode the best question→answer checkpoints; dev re-scores reproduced training exactly |
| `04_xfer_seed11_LB0.85030` | `didhitinahid/nascenia-submit-xfer-s11` | **0.85030** | first register-transfer submission. Includes `submission.csv`, log, `dev.json`, `test_run.json`. |
| `05_xfer_seed23` | `didhitinahid/nascenia-submit-xfer-s23` | — | seed-23 replicate |
| `06_xfer_ensemble` | `didhitinahid/nascenia-submit-xfer-ensemble` | **0.85088** | pooled MBR over both seeds lost (−0.0027 pred.), so the notebook shipped seed-23 beam output. `d11/d23/dmbr.json` are the three measured decoders. |
| `07_e05_inference_LB0.89347` | `farhanishraqq/nascenia-e05-inference` | **0.89347** (and 0.88008 with the old decoder) | E05 `english_draft` checkpoint 12,000 + E15 decoder; the last cell diffs against the scored CSV |
| `08_peak5_inference_LB0.89552` | `farhanishraqq/nascenia-peak5-inference` | **0.89552** | the champion alone: `ckptavg_peak5`, beam 8 / lp 1.2. Archive of the champion with its own [README](phase1_submissions/08_peak5_inference_LB0.89552/README.md), draft write-up, base-run config, averaging record and the exact scored CSV (`data/submission_reference.csv`). |

The final *selected* submission (public 0.89552, private 0.89418) came from the Phase 2 router notebook (`phase2_submissions/09_…`), whose output is byte-identical to `08`.

## phase1_probes

| folder | Kaggle kernel | what | result |
|---|---|---|---|
| `01_mbr_decode` | `farhanishraqq/nascenia-mbr-decode` | minimum-Bayes-risk decoding on the question→answer model | superseded by MBR-01 on the transfer model (−0.0027 LB) |
| `02_decode_sweep` | — | beam × length-penalty × `min_new_tokens` sweep | early decoder settings |
| `03_hcm_align_probe` | `farhanishraqq/nascenia-hcm-align-probe` | **ALIGN-01**: look every test id up in our Bengali ChatDoctor translation | 1,000/1,000 resolve; the lookup is a probe, not a legal submission |
| `04_e17_indictrans2` | `farhanishraqq/nascenia-e17-indictrans2` | E17: NLLB-200 and IndicTrans2 as alternative draft translators | NLLB −0.0439 vs Google; IndicTrans2 blocked (gated repo). The inline HF token in this notebook is **redacted** here. |
| `05_e17_qwen3` | `farhanishraqq/nascenia-e17-qwen3` | E17: Qwen3-14B as translator | −0.1255 vs Google — fluent, but different synonyms |
| `06_transfer_test24` | `farhanishraqq/nascenia-transfer-test24` | XFER-TEST24: Claude-translated drafts through the champion | −0.0060 Token F1 (7 wins / 17 losses), so re-translating the test set was cancelled |

## chpc_experiments

The GPU experiment program (E01–E24) that ran on the CHPC clusters granite and notchpeak from 9 to 15 August and took the score from 0.85088 to 0.89552. Start with its [README](chpc_experiments/README.md) (the wave plan, as written for the cluster), [RESULTS.md](chpc_experiments/RESULTS.md) (cross-experiment scoreboard) and the root [REPORT.md](../REPORT.md). The analysis reports generated on the cluster are in [`_analysis/`](chpc_experiments/_analysis/).

Each `E*/` folder keeps its `EXPERIMENT.md` (question, bar to beat, how to read it), `RESULTS.md` (what happened), `train.ipynb` where one exists, and the small per-arm records (`run.json`, `soup.json`, `trainer_state.json`, sweep JSONs). Checkpoints and prediction dumps stayed on the cluster.

The `train.ipynb` files are **specification templates** written before the run. The arms were actually launched as SLURM jobs calling [`scripts/pipeline/`](../scripts/pipeline/) — the exact invocations are in [`scripts/chpc_slurm/`](../scripts/chpc_slurm/). In particular `E05_train_to_convergence/train.ipynb` has the wrong data dir and sequence lengths for the champion; use `scripts/chpc_slurm/nasc-E05-english_draft.sbatch`.

| experiment | question | outcome |
|---|---|---|
| [E01](chpc_experiments/E01_add_english/RESULTS.md) add English | does the English source help? | +0.0220 Token F1 (matched control) |
| [E02](chpc_experiments/E02_add_question/RESULTS.md) add question | does the patient question help? | +0.0010, noise |
| [E03](chpc_experiments/E03_all_inputs/RESULTS.md) all inputs | are the signals complementary? | +0.0003 over E01 — ship the shorter input |
| [E04](chpc_experiments/E04_english_only/RESULTS.md) English only | how much is the draft worth? | English alone beats draft alone by +0.0172; the draft adds +0.0053 |
| [E05](chpc_experiments/E05_train_to_convergence/RESULTS.md) convergence | had the incumbent converged? | no — peaks at 12,000 (english_draft) / 15,250 (draft) → the champion |
| [E06](chpc_experiments/E06_lr_retune/RESULTS.md) LR retune | is lr 1e-3 still right? | yes (3e-4 −0.026) |
| [E07](chpc_experiments/E07_no_truncation/RESULTS.md) no truncation | what did truncation cost? | +0.0007 — closed |
| [E08](chpc_experiments/E08_mt5_control/RESULTS.md) / [E09](chpc_experiments/E09_mt5_best_input/RESULTS.md) mT5 | is mT5 viable? | loses to BanglaT5; 27.9% truncated answers |
| [E12](chpc_experiments/E12_warmstart/RESULTS.md) warm-start | Bengali medical warm-start? | +0.0028 — closed |
| [E13](chpc_experiments/E13_multitask_qa/RESULTS.md) multitask | add question→answer as a second task? | −0.022 |
| [E14](chpc_experiments/E14_arch_ensemble/RESULTS.md) ensembles | output / weight ensembling | pooled MBR +0.0020 (noise); weight soup 0.89532 on LB |
| [E15](chpc_experiments/E15_decode_sweep/RESULTS.md) decoding | best decoder + checkpoint averaging | beam 8 / lp 1.2 / min_new 0 (+0.0134 LB); `ckptavg_peak5` = **0.89552** |
| [E16](chpc_experiments/E16_phase2_audit/RESULTS.md) Phase 2 audit | truncation, repetition, tautology vs references | champion matches the reference profile; clinical checks need a judge |
| [E17](chpc_experiments/E17_draft_quality/RESULTS.md) draft quality | is a better translator worth it? | closed — Google draft kept |
| [E18](chpc_experiments/E18_model_zoo/RESULTS.md) model zoo | do ≤3B decoders beat BanglaT5? | no — best decoder Gemma-2-2B 0.8068 vs 0.8328 (final numbers in REPORT.md §3) |
| [E19](chpc_experiments/E19_multiseed_ensemble/RESULTS.md) multi-seed | does a 10-seed ensemble help? | no — the all-seed soup is worse than the best seed |
| [E20](chpc_experiments/E20_teacher_ceiling/RESULTS.md) teacher | can a large teacher beat 0.7724? | no — Qwen3.5-9B few-shot 0.5841 |
| [E21](chpc_experiments/E21_synthetic_pairs/RESULTS.md) / [E22](chpc_experiments/E22_retrieval/RESULTS.md) / [E23](chpc_experiments/E23_data_filter/RESULTS.md) | synthetic pairs / retrieval exemplars / data filtering | see each RESULTS.md |
| E24 model size | decoder zoo on `english_draft` | stopped — 43–78 h per arm, and E18 had already answered it |

`E18_model_zoo/RESULTS.md` and `E16_phase2_audit/RESULTS.md` were frozen early; `REPORT.md` has the final zoo numbers. `E18_model_zoo/_INVALID_length_capped/` documents three arms invalidated by a generation-length cap (BUG-05).

## phase2_specialist

The Phase 2 model study. The champion cannot answer without a draft (Token F1 0.1235), and the organizers' judging data never resolves to one, so this study trained a second model on real question → answer pairs. Read its [README](phase2_specialist/README.md) → [GPU_BUDGET.md](phase2_specialist/GPU_BUDGET.md) → [DATA_GUIDE.md](phase2_specialist/DATA_GUIDE.md) → [EXPERIMENTS.md](phase2_specialist/EXPERIMENTS.md) (arms X0–X7, D1–D3). [HANDOFF_PROMPT.md](phase2_specialist/HANDOFF_PROMPT.md) is the self-contained prompt handed to the teammate's assistant that ran the study on the cluster.

| folder | model | params | best held-out Token F1 (n=1000) | verdict |
|---|---|---|---|---|
| [A_mT5_base](phase2_specialist/A_mT5_base/RESULTS.md) | google/mt5-base | 582,401,280 | 0.2533 (X3, + RAG) | weakest of the three |
| [B_Qwen35_2B](phase2_specialist/B_Qwen35_2B/RESULTS.md) | Qwen/Qwen3.5-2B | 1,881,825,088 | **0.2625 (D1)** | **shipped** |
| [C_BanglaAI_17B](phase2_specialist/C_BanglaAI_17B/RESULTS.md) | swapnillo/Bangla-AI-1.7B | ~1.7B | 0.2583 (X2) | tied on held-out, but drops twice as far on the disjoint slice |

Each folder has `INSTRUCTIONS.md`, `train.ipynb`, `inference.ipynb` and the final `RESULTS.md` (the filled-in version from the Phase 2 bundle). The notebooks are generated by [`scripts/phase2/shared/build_notebooks.py`](../scripts/phase2/shared/build_notebooks.py); the data and index builders and the router validators are in [`scripts/phase2/`](../scripts/phase2/).

## phase2_submissions

| folder | Kaggle kernel | what | result |
|---|---|---|---|
| `01_routed_inference` | `farhanishraqq/nascenia-routed-inference` | first routed notebook (id lookup → champion, else specialist) | 1000/1000 `ID_LOOKUP` on Phase 1 |
| `02_qwen_rag_bolton` | `farhanishraqq/nascenia-qwen-rag-bolton` | X6: retrieval bolted onto the specialist at inference | Token F1 0.2648 → 0.1828, copy-margin −0.0529 — it copies the retrieved case |
| `03_qwen_d1_solo` | `farhanishraqq/nascenia-qwen-d1-solo` | the shipped specialist alone on the Phase 1 test set, fp32 on T4 | dev 0.2675 vs 0.2646 recorded (bf16) — reproduces |
| `04_final_bundle_infer` | `farhanishraqq/nascenia-final-bundle-infer` | the two-branch bundle on Kaggle | 1000/1000 rows identical to the 0.89552 entry |
| `05_branch3_champ` / `06_branch3_qwen` | `farhanishraqq/nascenia-branch3-*` | paired test on 362 leak-free rows whose ids do not resolve | champion + ai-medical-chatbot draft **0.6257** · champion + ChatDoctor content-match 0.2094 · specialist 0.2616 |
| `07_phase2_inference` | `farhanishraqq/nascenia-phase2-inference` | first organizer-format notebook: 3-way router, one editable cell | 1000/1000 `ID_LOOKUP`, byte-identical output |
| `08_phase2_smoke` | `farhanishraqq/nascenia-phase2-smoke` | 60 disguised rows whose ids cannot resolve | 35% retrieval / 65% specialist, both `transformers` versions live in one run |
| **`09_cpu_final_submission_FINAL`** | **`farhanishraqq/cpu-final-submission`** | **the Phase 2 deliverable** — adds dataset-level id verification and the judges' how-to-run table | produced the selected submission; the three downloaded runs (`_output/`, `_output_v3/`, `_output_v4/` logs) all wrote the same CSV, sha256 `45a7ee59…aa7e` |

---

### Not included

- Superseded notebook copies: the first `train_banglat5*` notebooks (4 Aug), the earlier `sweep_runs/` pushes, the `xfer_train` template, and `fine_tune_project/reference_notebooks/` (byte-identical to folders above: `PROVEN_xfer_seed11` = `10_xfer_seed11`, `PROVEN_xfer_seed23` = `11_xfer_seed23`, `sweep_C`/`sweep_G` = `05`/`09`, `banglat5_v2_baseline` = `01`, `mt5_english_draft_kaggle` = `12`).
- Model weights, `dev*.json` / `test*.json` prediction dumps, per-arm `submission.csv` files, SLURM `.out` logs, and debug outputs.
