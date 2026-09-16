# E12 — Warm-start then transfer

**Tier 4 — DATA STRATEGY · Priority: MEDIUM**

## The question

> Does a **general Bengali medical warm-start** help before register transfer?

## Why it matters

Two-stage curriculum: 1 epoch on `data/warmstart_corpus/master_c_bengali.csv` (123,289 curated
Bengali medical dialogue rows), then the register-transfer task.

The hypothesis is that broader Bengali medical fluency helps the model produce in-domain phrasing it
would otherwise have to learn from the transfer data alone.

🔴 **The corpus is leak-safe and must stay that way.** Its hcm rows whose ids fall in the frozen
dev/test split were **removed** (6,000 rows) — they are a *second translation of answers we evaluate
on*, so training on them leaks the eval set. Verified: 0 dev-id overlap. See
`data/warmstart_corpus/SOURCES.md`.

### Optional: natively-Bengali additions worth evaluating

The corpus is **86% our own translation** of ChatDoctor, so it carries one translator's fingerprint
throughout. Natively-Bengali dialogue would add genuine variety — its only real advantage here.

| Candidate | Note |
|---|---|
| `Atanuc73/Bengali-Medical-Chatbot-Dataset` (HF) | Direct Bengali patient→doctor pairs. **Not yet in the repo** — the strongest native candidate. |
| `doctor_qa_bangla` | ✅ already inside the corpus (4,651 rows) — the only native source in it |
| `Shakil2448868/Bangla-medical-question-answering` | ⚠️ audited at **901 rows**, is itself a *translation* of another audited set, **no stated licence**, and the local copy is a **132-byte git-LFS stub** — never downloaded |

⚠️ **Before adding any of these, three checks:**
1. **Is the local file real, or an LFS pointer?** 18 of 35 files in `Data_Search_1` are stubs
   (trap #1). `ls -la` before believing a row count.
2. **§2.6.a** — publicly downloadable by any competitor, no gate, no cost. "No stated licence" is
   not the same as permissive; record the URL and terms.
3. **Re-run the dev/test exclusion** on anything you merge in. The leak guarantee above is only
   worth what your rebuild preserves.

**Expect little from this.** Warm-start data helps *fluency*, and the register-transfer task is
mostly copy-and-edit — it never had a fluency problem. Its real value is **Phase 2** (E16), where
clinical quality is judged rather than overlap.

## Configuration

| | |
|---|---|
| Model | `csebuetnlp/banglat5` |
| Data | `data/<winner of Tier 1>/` |
| Sequence | `--max-source-len 768 --max-target-len 512` |
| Batch | `--batch-size 32 --grad-accum 2` (effective 64) |
| LR | `1e-3` warmup 200, Adafactor (**re-tune in E06**) |
| Steps | 4000 · eval every 250 · `load_best_model_at_end` on **composite** |

## Command

```bash
python ../code/02_train_t5.py \
  --data-dir ../data/<winner of Tier 1> \
  --model csebuetnlp/banglat5 \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 \
  --batch-size 32 --grad-accum 2 --eval-batch-size 32 \
  --eval-subset 300 --eval-steps 250 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length \
  --seed 11 --epochs 2.516 --run-name E12_warmstart_then_transfer
```

Then decode and score:

```bash
python ../code/04_decode.py --ckpt runs/E12_warmstart_then_transfer/best --data-dir ../data/<winner of Tier 1> \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore --record dev.json

python ../code/04_decode.py --ckpt runs/E12_warmstart_then_transfer/best --data-dir ../data/<winner of Tier 1> \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --no-bertscore \
  --out submission.csv --record test.json
```

Raise `--batch-size` and lower `--grad-accum` together as VRAM allows — that is pure speed, not a
different experiment. Keep the effective batch at **32–64**.


## What it must beat

**The Tier-1 winner without warm-start.**

## How to read the result

| Result | Meaning |
|---|---|
| > baseline | ✅ Fluency transfer is real → also worth trying for Phase 2 clinical quality |
| ≈ baseline | The transfer task already teaches everything needed |
| < baseline | The warm-start shifted the model off-register — consistent with our measurement that off-register content is what this metric punishes |

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
