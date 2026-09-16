> **Repo note.** This folder mirrors the local `FINAL SUBMISSION_DRAFT/` archive. `model_checkpoint/best/` (the weights) is the Kaggle dataset `farhanishraqq/nascenia-peak5-checkpoint-average`; `training/` lives in [`scripts/pipeline/`](../../../scripts/pipeline/) (`02_train_t5.py`, `17_model_soup.py`, `metric.py`) and [`scripts/chpc_slurm/nasc-E05-english_draft.sbatch`](../../../scripts/chpc_slurm/nasc-E05-english_draft.sbatch); `inference/build_nb.py` is [`scripts/kaggle/notebook_builders/build_nascenia-peak5-inference.py`](../../../scripts/kaggle/notebook_builders/build_nascenia-peak5-inference.py); `WRITEUP.md` is kept as `WRITEUP_DRAFT.md`; the `data/*.parquet` inputs are not uploaded. The TODO list at the bottom was completed by the Phase 2 bundle ([`PHASE2_WRITEUP.md`](../../../PHASE2_WRITEUP.md)), and the specialist that shipped is Qwen3.5-2B, not Bangla-AI-1.7B.

# FINAL SUBMISSION_DRAFT

**Status: early archive, not final.** This folder collects the real, verified artifacts behind
the current champion (public LB **0.89552**, #1) into one self-contained place, ahead of
actually assembling the Phase 2 submission. Started 2026-08-17 — see `PROGRESS.md` in the repo
root for the day's full context.

**This is the Phase 1 specialist only.** Per the routing architecture (BanglaT5 for
ChatDoctor-resolving rows, the Bangla-AI-1.7B specialist + RAG for everything else — see
`PHASE_2_EXP/`), this folder covers the deterministic branch. The Phase 2 specialist isn't
trained yet and will be added here once it lands.

## What's in here, and what each thing actually is

```
model_checkpoint/
  best/                    the real weights — csebuetnlp/banglat5, 247,577,856 params, bf16
                            trained. This is `ckptavg_peak5`: a uniform average of 5 checkpoints
                            (steps 11500-12500) from ONE training run, not an ensemble.
  checkpoint_average.json  which 5 checkpoints were averaged, and the dev score at averaging time
  base_run.json            the underlying training run's exact config (seed 11, lr 1e-3,
                            768/512 sequence, effective batch 64, adafactor, bf16, H100 NVL)

training/
  02_train_t5.py                   the trainer — this IS the training script (Rules §5.1 item 1
                                    doesn't require a notebook for training, only for inference —
                                    see the note below)
  nasc-E05-english_draft.sbatch    the exact SLURM invocation that produced the base checkpoint.
                                    🔴 There is no training NOTEBOOK for this model — it was
                                    trained on CHPC via this script directly, verified to match
                                    base_run.json exactly. A stale, wrong-config .ipynb template
                                    exists elsewhere in the repo (fine_tune_project/
                                    E05_train_to_convergence/train.ipynb) — do NOT use it, it
                                    has the wrong data dir and sequence lengths.
  17_model_soup.py                 the checkpoint-averaging script that turned the base
                                    checkpoint into ckptavg_peak5 (peak-centred averaging beat
                                    the single best checkpoint and every cross-seed alternative —
                                    see fine_tune_project/E15_decode_sweep/RESULTS.md)
  metric.py                        Token F1 / ROUGE-L, exact implementation used everywhere in
                                    this project — needed to reproduce the reported dev numbers

inference/
  nascenia-peak5-inference.ipynb   the REAL inference notebook. Pushed, run, status COMPLETE on
                                    Kaggle (farhanishraqq/nascenia-peak5-inference). This is what
                                    actually produced the scored 0.89552 submission.
  build_nb.py                      generates the notebook above from source — edit this, not the
                                    .ipynb directly, if changes are needed
  kernel-metadata.json             T4, machine_shape pinned (CLAUDE.md's "no T4, no push" rule)

data/
  dev_english_draft.parquet        the frozen dev split (seed 42, 5,000 rows) in the model's
                                    trained input format — needed to reproduce the dev numbers
  test_english_draft.parquet       the actual 1,000 competition test rows, same format — this is
                                    what the inference notebook decodes
  submission_reference.csv         the exact CSV that scored 0.89552 — the inference notebook
                                    diffs its own fresh output against this as reproduction
                                    evidence (NOT a weight hash — see the note below)

requirements.txt                  pinned deps
```

## 🔴 Two things every reader of this folder should know before trusting it

**1. Reproduction evidence is the decoded outputs, not a weight hash.** Two identical training
runs on this project produced 300/300 identical predictions but *different* `checkpoint_hash`
values — floating-point non-determinism in GPU reductions perturbs weights in low-order bits
without changing what they generate. `submission_reference.csv` + the notebook's own diff-against-it
cell (cell 9) is the real evidence; don't ask for or expect a matching hash.

**2. There is no training notebook, by design, not by omission.** Phase 2 rules require a
"training script" — that's satisfied by `02_train_t5.py` + `nasc-E05-english_draft.sbatch`.
Only the *inference* side is required to be a Kaggle notebook (confirmed from the organizer
clarification captured in this project's chat history). If a training notebook turns out to be
wanted anyway, it needs to be built fresh from the real config — do not adapt the stale
template.

## What's still missing from this folder (TODO before it's actually submittable)

- [ ] **WRITEUP.md is a draft**, not final — needs a pass once the Phase 2 specialist (E25) is
  trained, since the final write-up should describe the whole pipeline, not just the champion.
- [ ] **The Phase 2 specialist** (`swapnillo/Bangla-AI-1.7B` + retrieval) — not trained yet,
  will be added here once `PHASE_2_EXP/E25_phase2_specialist/` produces a checkpoint.
- [ ] **A single combined inference script** implementing the actual routing logic (id-lookup
  hit → this checkpoint; miss → the Phase 2 specialist) — the notebook here only covers the
  hit path, since that's all that existed until E25.
- [ ] Organizer invite to the (currently private) Kaggle notebook — per their stated process,
  this happens after judging starts, not before.
