# Current Operating Instructions — Nascenia Bengali Medical Dialogue

This file is the concise, current briefing for work on this repository. It supersedes earlier guidance that treated conventional question-to-answer fine-tuning, external warm-starting, or MBR as the main path. Detailed evidence lives in [CLAUDE.md](CLAUDE.md), [LOCAL_EXPERIMENTS.md](LOCAL_EXPERIMENTS.md), [PREDICTIONS.md](PREDICTIONS.md), [PROGRESS.md](PROGRESS.md), and [fine_tune_project/README.md](notebooks/chpc_experiments/README.md).

## Objective and non-negotiable rules

Generate a Bengali doctor response from a patient prompt for the Nascenia AI Hackathon. The final system must be reproducible and genuinely model-generated.

- Submit exactly `id,output`, with one row for every test id.
- The inference total is **at most 3B parameters**, including adapters, retrievers, and every ensemble member. Verify the actual total in the Phase-2 environment; a model named “3B” is not automatically eligible.
- A constant response and a raw id-to-draft lookup are useful diagnostics only. Neither is an acceptable final system under the model-output and Phase-2 reproducibility requirements.
- Never train on the frozen 5,000-row dev split: `--seed 42 --dev-size 5000`.
- Do not submit anything without explicit user approval. Run the Kaggle notebook, validate it, then give the user the notebook link; do not call `kaggle competitions submit` with a CSV.
- Kaggle rules override conflicting local documents. The current submission schema is `id,output`.

## The winning formulation

The competition data is a Bengali translation of ChatDoctor / HealthCareMagic-100k, and the competition `id` preserves the source row index. The team's independently translated public corpus contains a matching `hcm_<id>` draft for all 1,000 test ids and 108,943 of 108,954 train ids.

The useful task is therefore **register transfer**, not ordinary medical QA:

```text
external Bengali draft of the source answer  →  competition-register Bengali answer
```

The incumbent is BanglaT5 seed 11, trained on aligned pairs and decoded with beam search. It achieved **Token F1 0.7724 / ROUGE-L 0.7324** on the comparable dev evaluation and **0.85030 public LB**. Seed 23 replicated at 0.7723 / 0.7332. This is the baseline every proposed change must beat.

The raw external draft plus brand/greeting cleanup scores 0.5984 / 0.5482; it is the information floor, not a shippable submission. The final model must learn the conversion to the competition’s distinctive register — especially its `হেলো` opener, brand usage, boilerplate, and output structure — without replacing the draft with an id lookup.

External-data disclosure is mandatory: include the official ChatDoctor URL, research-only restriction, translation model and prompt, row counts, deduplication rules, dataset hash, and stage-wise logs. The route is defensible because the source is public, free, and equally accessible, but organizers could still patch or rescore; do not conceal the provenance.

## How to evaluate

The project-local BERTScore setup is mis-calibrated. Select experiments primarily on **Token F1 and ROUGE-L**, not local composite or loss.

```text
Estimated public LB ≈ 0.4646 + 0.3098 × TokenF1 + 0.2 × ROUGE-L
```

This is an interpolation through the constant probe (0.57849 LB) and the register-transfer submission (0.85030 LB), not a guaranteed metric. It is useful for ordering candidates, while the frozen dev split remains the source of truth.

- Treat differences below **0.0044 Token F1** as noise.
- Always report the full trajectory, not only the final checkpoint. On the earlier QA task, loss and overlap diverged sharply; selecting the lowest loss chose bad checkpoints.
- Record mean output length, `হেলো` opener rate, brand rate, truncation rate, precision, parameter count, and row-level disagreement for ensemble candidates.
- Before producing a submission file, re-score a known dev subset and assert the recorded result. A valid CSV can still contain fp16 NaN garbage.

## Settled negative results — do not re-run casually

| Topic | Decision | Evidence |
| --- | --- | --- |
| Pooled MBR over the two transfer seeds | **Closed for register transfer** | 0.7677 / 0.7268, about 0.0027 LB below beam. The task is near-deterministic and the two seeds agree too closely. |
| Shipped decoder | **Beam 4** | `min_new_tokens=80`, `max_new_tokens=320`, `length_penalty=1.0`. |
| Conventional question-to-answer BanglaT5 | **Not the main track** | Best arm reached only 0.2576 / 0.1776; it is not competitive with transfer. |
| QA learning-rate search | **Closed for that task** | 1e-3 peaked; 3e-3 fell to 0.2390. Do not transfer this conclusion automatically to transfer. |
| Generic retrieval for Phase 1 | **Exclude** | TF-IDF retrieval lost to a constant; specific mismatched claims damage overlap. |
| NLP4Health-2025 as training data | **Exclude** | It is synthetic and machine-translated, not native real dialogue. Keep only its model-selection findings as weak prior evidence. |
| Medical books, MCQ/exam/reasoning/extractive data | **Exclude** | Wrong supervision shape and/or inadequate reuse evidence. |
| Encoder-only models in the generator | **Exclude** | BERT, XLM-R, and ModernBERT cannot generate the required response. |
| Qwen2.5-3B / Llama-3.2-3B | **Ineligible** | 3.09B and 3.21B total parameters, respectively. |

Do not interpret the MBR result as a universal claim: it was measured only on the register-transfer task. An architecture-diverse ensemble remains an experiment, not an assumption.

## Immediate priority: improve the draft before retraining

E17 changed the next step. The Google-translated draft used by the incumbent is not the closest available reconstruction of the organizers’ target register.

| Translator | Evaluation | Result |
| --- | --- | --- |
| Google Translate | current draft | baseline, 0.5984 Token F1 on the aligned dev measurement |
| Claude Opus 5 | 24-row probe | 0.6865; +0.0631 vs paired Google |
| Codex / GPT-5 | 10-row probe | 0.6483; +0.0253 vs paired Google |
| NLLB-200 1.3B | 200-row probe | 0.5480; −0.0439 vs paired Google |

Dedicated MT is closed; the target’s fingerprint appears more LLM-like. The next practical decision is whether a scalable, permitted open-weights LLM translator (the current plan names a Qwen3-14B probe) clears Google sufficiently to regenerate all aligned drafts. Do not rebuild all data from a tiny or unpaired result. If a replacement wins decisively on a sufficiently representative aligned probe, rebuild every input set and restart Wave 1; the draft is an input to every later experiment.

## High-GPU program and gates

Use [fine_tune_project/README.md](notebooks/chpc_experiments/README.md) as the self-contained execution plan and copy a notebook from [fine_tune_project/reference_notebooks](notebooks/phase1_kaggle_training/) rather than rebuilding the proven recipe. On high-GPU hardware, run independent experiments in parallel, but respect their information dependencies.

1. **Wave 1 after E17:** E05 (convergence), E01 (English + draft), E02 (question + draft), and E08 (mT5 control). They identify whether more source information or more training helps.
2. **Wave 2:** run E03/E04 with the Wave-1 input winner; E06 retunes transfer learning rate, E07 measures truncation, and E09 is allowed only if E08 is competitive. E18 is the model-zoo hedge: Qwen3-1.7B, Gemma-2-2B-IT, Qwen2.5-1.5B, Qwen3-0.6B, Llama-3.2-1B, and IndicBART. Decoder-only models are promising prior art, not established winners here.
3. **Wave 3:** E12 warm-start, E13 multi-task, E19 ten-seed ensemble, E14 architecture ensemble, E21 synthetic-pair robustness, and E20 teacher ceiling/distillation. E20 stage 2 is gated: a teacher must first exceed **0.82 Token F1**. Synthetic augmentation may vary the *draft/input* only; targets must remain genuine competition-register text, and it must exclude dev/test ids.
4. **Wave 4:** E15 decoding sweep, E16 Phase-2 clinical audit, and Phase-2-only retrieval grounding. For any ensemble, measure useful row-level disagreement first. Ten BanglaT5 members may fit only if measured model sizes keep the total below 3B.

For each experiment, write `run.json`, best-checkpoint trajectory, dev/test decode records, and notes in its own `fine_tune_project/E*/` directory. Update `fine_tune_project/RESULTS.md` with the pairwise comparison that the experiment was designed to answer.

## Runtime and reproducibility requirements

- Pin and assert **`transformers==4.57.3`**. Newer Kaggle defaults caused broken T5 training, abnormal losses, and embedding changes.
- BanglaT5 on a T4 uses **fp32**. Use bf16 only on sm_80+ hardware. **Never use fp16**: T5 can silently produce NaN logits and a plausible-looking but invalid CSV.
- The proven Kaggle-scale transfer recipe used BanglaT5, Adafactor, lr 1e-3, warmup 200, effective batch 64, 384/256 limits, eval every 250, and a best-checkpoint selection. Treat it as the baseline, not as a universal optimum.
- A GPU Kaggle notebook must specify `"machine_shape": "NvidiaTeslaT4"`; use `KAGGLE_PUSH/kpush.py`, then verify the returned metadata. Keep a runtime capability gate.
- Hosted scripts must accept explicit data paths; do not derive data locations from `__file__`.
- Filter `runs/smoke/` when collecting artifacts. Historical checkpoint hashes written before the content-hashing fix are not valid identities; cite the archived notebook and `run.json` configuration instead.
- Store all development in `.py`; use `.ipynb` only for the final Kaggle inference workflow.

## Project-memory maintenance

Treat documentation as part of every experimental task.

- Add every completed, failed, and negative experiment to [LOCAL_EXPERIMENTS.md](LOCAL_EXPERIMENTS.md), with hypothesis, config, checkpoint identity, all metric components, decoding, and verdict.
- After any notebook submission/run, update both [PROGRESS.md](PROGRESS.md) and [PREDICTIONS.md](PREDICTIONS.md), including the dev-to-LB delta.
- Archive every scored notebook and its exact output under `NOTEBOOKS/(score)_(notebook_name)/`; never overwrite an archive.
- Update [PLAN.md](PLAN.md) whenever a measured result changes the strategy.

When documents conflict, prefer the newest measured entry in `PROGRESS.md` or `LOCAL_EXPERIMENTS.md`, then the detailed experiment specification, over historical narrative.
