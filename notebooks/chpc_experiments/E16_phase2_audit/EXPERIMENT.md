# E16 — Phase 2 clinical quality audit

**Tier 6 — PHASE 2 (20% of final score) · Priority: 🥇 HIGHEST (different objective)**

## The question

> Is the winning model **clinically good**, not just lexically overlapping?

## Why it matters

**Phase 1 is 80% of the final score; Phase 2 is 20% and judged by an LLM on clinical accuracy —
a completely different objective from token overlap.** Nothing in this project has optimised for it.

The good news: our output is a reconstruction of *real doctor answers*, so it should judge well.
The risk is concrete and already observed — one arm's output degenerated into
*"gastroenteritis can be caused by gastroenteritis"*. That is **free on Token F1** (repeated
in-vocabulary tokens boost recall) and **near-zero to a clinical judge**.

There is a real tension here: the decoder settings that maximise overlap may be the ones that
produce repetition. A model that scores 0.86 on Phase 1 and fails Phase 2 can lose to one that
scores 0.85 and passes.

## Configuration

| | |
|---|---|
| Model | `<best checkpoint>` |
| Data | `data/warmstart_corpus/` |
| Sequence | `--max-source-len — --max-target-len —` |
| Batch | `--batch-size — --grad-accum —` (effective —) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |



## What it must beat

Not a leaderboard comparison — a **qualitative audit**.

## How to read the result

1. Sample **100 test outputs** and check for: repetition loops, contradictions, unsafe advice,
   truncated endings, wrong-language fragments.
2. Measure repetition rate mechanically (repeated 4-grams within a response) across candidate models.
3. If the Phase-1 winner is materially worse clinically than the runner-up, **that is a real
   trade-off to escalate** — 20% of the final score is worth more than a 0.005 Phase-1 gap.
4. Draft the Phase 2 bundle: `inference.py`, pinned `requirements.txt` (**`transformers==4.57.3`**),
   parameter-count assertion, checkpoint hosting, and the **mandatory external-data disclosure**.

## 🔵 This is the ONE place extra medical data genuinely earns its slot

Everywhere else in this program, more Bengali medical dialogue optimises a track we measured as 3×
worse (question→answer caps at Token F1 **0.2576**; register transfer reaches **0.7724**). Phase 2 is
the exception: it is **LLM-judged on clinical accuracy**, where overlap is irrelevant and answer
quality is the whole score.

| Candidate | Why here specifically |
|---|---|
| **`Atanuc73/Bengali-Medical-Chatbot-Dataset`** (HF) | Native Bengali patient→doctor pairs — **zero translation fingerprint**, which matters for judged quality where it did not for overlap. **Not yet in the repo.** |
| `doctor_qa_bangla` (4,651) | Already in `warmstart_corpus`; the only native source in it |
| `ChatDoctor-GenMedGPT-5k` | ✅ already have it (5,200 rows) — dense, curated clinical dialogue |

⚠️ **Check before use:** is the local file real or a **git-LFS stub** (18 of 35 in `Data_Search_1`
are stubs)? Is it §2.6.a-accessible with a stated licence? Does merging it preserve the dev/test
exclusion?

**A model fine-tuned for Phase 2 need not be the Phase 1 submission.** They are scored separately —
80/20 — so the clinically-better model can serve Phase 2 while the overlap-optimal one holds the
leaderboard, provided the write-up is honest about which produced which.

## ❌ Explicitly ruled out for this task — do not spend time re-checking

| Dataset | Reason (measured) |
|---|---|
| `omi-health/medical-dialogue-to-soap-summary` | SOAP summarisation — the same shape as `mts_dialog`, which we measured and excluded: clinical note in, doctor's *opening line* out. Inverse of our task. |
| `badhanamitroy/bangla-disease-symptom` | Same shape as `disease_db` (796 rows, excluded): structured symptom/drug bullet lists, not doctor replies. The "vocabulary dictionary" use does not apply — **BanglaT5's tokenizer is already Bengali-native**, so there is no vocabulary gap. |
| `nahidstaq/bangla-llm-data` (800k general Bengali) | Premised on starting from Qwen-2.5-3B or Llama-3.2-3B — **both breach the 3B cap** (3.09B, 3.21B, verified on the model cards). BanglaT5 is Bengali-pretrained, so catastrophic forgetting of Bengali grammar is not our failure mode. |

---

## Non-negotiables (every experiment)

- **`transformers==4.57.3`** — other versions do not train this pipeline correctly. Assert it.
- **bf16 on sm_80+, fp32 otherwise. 🔴 NEVER fp16** — T5 goes NaN *silently* and still writes a
  well-formed CSV of garbage.
- **Never change the split**: `--seed 42 --dev-size 5000`. Every number in this project rests on it.
- **Select on composite, never `eval_loss`** — they move in opposite directions on some tasks; one
  run's lowest loss coincided with its *worst* Token F1.
- **Report Token F1 and ROUGE-L**, never the local composite (mis-calibrated by ~0.118).
  Predict the leaderboard with `LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L`.
- **Report the register read-out**: `হেলো` opener rate (references 76.4%, draft 0.06%) and
  `নাসেনিয়া` rate (references 50.0%, draft 0.00%). Near the draft's rates ⇒ the model copied its
  input; near the references' ⇒ it learned the conversion.
- **Verify no truncation** — report the % of examples exceeding the source and target caps.

Record everything in [`../RESULTS.md`](../RESULTS.md).

- 🔴 **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.
