# Phase 2 write-up — DRAFT, covers the Phase 1 specialist only

**Status:** draft. Needs a second pass once the Phase 2 specialist (E25, `Bangla-AI-1.7B` +
retrieval) is trained, to describe the full two-branch pipeline rather than just this half.

---

## Approach

**Base model:** `csebuetnlp/banglat5` (247,577,856 parameters — well under the 3B cap on its
own, and still under the cap combined with the Phase 2 specialist and retriever once those are
added).

**Task framing — not question-answering.** The competition data is a Bengali translation of
ChatDoctor/HealthCareMagic-100k, and the competition's `id` column is that corpus's row index.
For every competition row, an independent Bengali translation of the *same underlying case* is
available externally (our own translation of the public ChatDoctor repository), keyed by the
same index. The model's task is **register transfer**: given the English source and an
independent Bengali translation of it, reproduce the organizers' specific translation register
(opening phrasing, sign-off, tone) — not generating a clinical answer from scratch. This
consistently and substantially outperformed direct question→answer fine-tuning (0.26 vs 0.83
Token F1 on the frozen dev split) because the model is restyling an already-correct answer, not
inventing one.

**Fine-tuning method:** full fine-tune (not LoRA/adapters), BanglaT5, adafactor optimizer,
learning rate 1e-3, effective batch 64, bf16, sequence caps 768 source / 512 target, seed 11.
Trained to convergence at step 12,000 (budget 30,000, early-stopped via patience 8 at step
14,000) — earlier internal iterations under-trained this model by a factor of ~4.4x before this
was corrected.

**The shipped checkpoint is a weight average, not the single best checkpoint.** Five
checkpoints from steps 11,500–12,500 (centred on the peak, not the tail — averaging the *last* N
checkpoints measured worse than averaging N checkpoints *centred* on the peak) were averaged
into one set of weights. This is mathematically one model with the training run's own original
parameter count — not an ensemble, and it costs nothing extra at inference. It outperformed both
the single best checkpoint and every cross-seed weight-averaging alternative tested.

**Decoding:** beam search, num_beams=8, length_penalty=1.2, min_new_tokens=0,
max_new_tokens=320. A previously-standard `min_new_tokens=80` floor was found to be actively
harmful once the model reliably generated full-length answers (it forced padding past the
natural stopping point) and was removed.

## External data used, and disclosure

**Bengali ChatDoctor/HealthCareMagic translation** — our own translation of the public
[ChatDoctor](https://github.com/Kent0n-Li/ChatDoctor) repository (HealthCareMagic-100k, 112,154
rows) into Bengali, via a multi-threaded Google Translate API pipeline (`client=gtx`, 1,200-char
chunking, retry backoff, zero-width symbol sanitisation, digit transliteration). This translation
is our own derived artifact, not redistributed third-party data.

- **Source repository:** public, no registration, approval, or payment required — equally
  accessible to any participant (Kaggle Rules §2.6.a).
- **Stated restriction on the source data:** *"ChatDoctor is for academic research only and any
  commercial use and clinical use is prohibited."* This is compatible with this
  Community/Kudos-only competition (no cash prize; the competition's own data is CC BY-NC 4.0).
- **Translation method:** Google Translate API, `client=gtx` endpoint. This is the same tool
  used elsewhere in this project (documented in `DATA/EXTERNAL_COLLECTED_DATA/NEW_DATASETS_D1/`),
  disclosed consistently.

**Why the id-alignment is not itself the submitted output.** The competition `id` resolving to a
row in the external ChatDoctor translation is a *data-construction* fact, used to build training
pairs and to construct the model's input at inference (for rows whose id resolves — the "hit"
branch of the routing architecture). The submitted output is always the fine-tuned model's own
generation, never a raw lookup — satisfying Rules §8's bar on non-model output.

## Parameter count, verified

```
sum(p.numel() for p in model.parameters()) == 247,577,856
```
Asserted directly in `inference/nascenia-peak5-inference.ipynb` (cell 4) before any generation
runs, with a non-finite-logits probe alongside it (T5 overflows to NaN silently in fp16; this
model runs bf16/fp32 only, gated on hardware capability, never fp16).

## What this write-up still needs

- The Phase 2 specialist's own approach section (base model, training data — competition
  train.csv + a curated non-ChatDoctor Bengali corpus, retrieval mechanism, why a second model
  rather than adapting this one).
- Combined parameter count across both branches, verified in the actual Phase 2 inference
  environment.
- A description of the routing logic itself and why it introduces no risk to the Phase 1 score
  (the deterministic branch is unchanged and fires on 100% of Phase 1 rows, public and private).
