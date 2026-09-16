# A — `google/mt5-base` (580M, seq2seq) — RESULTS

**Ran 2026-08-16/17 on 8 × A800 40GB, DDP via torchrun, bf16.** Effective batch **64** on every
arm (`per_device 4 × accum 2 × 8 ranks`). Exact params **582,401,280**.

## 🥇 HEADLINE: the specialist works. Every trained arm clears the bar by ~0.10.

The bar was **0.1454** — the best any inference-time fix achieved on the frozen champion, which
without a draft echoes the patient's message back (0.1235). mT5-base fine-tuned on real
question→answer pairs lands at **0.24–0.26**, i.e. **+0.10, more than 20× the stated noise floor.**
The premise this folder was built on is confirmed: the champion could not answer because it was
only ever trained to restyle, and a model trained on the actual task can.

## Every arm

Both columns matter — see the stability section for why the peak alone is misleading.

| arm | data | rows | **peak F1** | peak step | **final F1** | ROUGE-L | tokens | হেলো | trunc | min |
|---|---|---|---|---|---|---|---|---|---|---|
| **X3 RAG** 🥇 | `rag` | 118,912 | **0.2566** | 11,500 | **0.2537** | 0.1782 | 95.8 | 86.7% | 5.7% | 342 |
| **X4 core-only** | `plain_core_only` | 101,740 | 0.2547 | 5,000 | 0.2452 | 0.1817 | 94.1 | 84.7% | 8.7% | 134 |
| D2 +genmedgpt | core+5,200 | 106,940 | 0.2536 | 3,500 | 0.2504 | 0.1782 | 94.7 | 71.7% | 11.0% | 109 |
| D3 +doctor_qa | core+4,651 | 106,391 | 0.2537 | 5,000 | 0.2399 | 0.1781 | 98.8 | 84.0% | 11.7% | 133 |
| X2 plain | all extras | 118,912 | 0.2475 | 2,500 | 0.2414 | 0.1715 | 91.7 | 77.7% | 7.3% | 99 |
| D1 +icliniq | core+7,321 | 109,061 | 0.2538 | 3,500 | 0.2339 | 0.1553 | 104.2 | **2.0%** 🔴 | 0.0% | 95 |
| X5 lr 3e-4 | `plain` | 118,912 | 0.2488 | 8,000 | 0.2327 | 0.1719 | 96.4 | 84.0% | 16.3% | 181 |
| X5 lr 3e-3 | `plain` | 118,912 | 0.2398 | 2,500 | **0.1492** 🔴 | 0.1592 | 130.6 | 2.7% | **61.7%** | 90 |
| *references* | | | | | | | *~100* | *76.4%* | *6.8%* | |

X0 (zero-shot) and X1 (few-shot) produced the documented near-gibberish — mT5-base is a pure
span-corruption model with no instruction tuning. Recorded and not debugged, as instructed.

## 🔴 The trajectories are unstable — do not trust a single peak

This is the most important methodological finding here, and it changes how every number above
should be read.

D1's register opener oscillates **all-or-nothing** between consecutive evals:

| step | 500 | 1,000 | 1,500 | 2,000 | 2,500 | 3,000 | 3,500 | 4,000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .1233 | .2370 | .2207 | .2446 | .2454 | .2435 | **.2538** | **.0858** |
| হেলো % | 100 | 100 | 20.3 | 0.7 | 0.0 | 0.0 | 100 | 0.0 |

**Token F1 falls 0.2538 → 0.0858 in 500 steps.** A metric that moves 0.15 between evals means
the documented **0.0044 noise floor does not transfer to this task** — it was derived on stable
register-transfer runs. On Phase 2 QA, treat anything under **~0.02** as unresolved.

Concretely: the three D arms' *peaks* span 0.0002 (0.2538/0.2536/0.2537 — implausibly tight),
while their *finals* span 0.0165. The peaks are noise-selected maxima off a bouncing curve. **The
final column is the more honest comparator**, and this write-up ranks on it.

## Verdicts

**X4 vs X2 — the extra 17k rows do not help.** Peak 0.2547 vs 0.2475, final 0.2452 vs 0.2414;
`plain_core_only` wins on both with **25% less data**. Ship the smaller set: faster, and fewer
external sources to disclose.

**D1/D2/D3 — no single extra source is the culprit, contradicting the doc's prediction.** The
guide named GenMedGPT's 31-word answers as the prime suspect if X4 went negative. It is not:
D2 (+genmedgpt) has the **best final of the three** (0.2504). The individually-neutral pattern
with a mildly negative bundle is the "all three ≈ X4" branch of the decision table ⇒ **ship
`plain_core_only`**. ⚠️ Individually neutral yet collectively −0.007 is a genuine oddity; at this
task's real noise level it is not resolvable with the runs available.

**D1 ended off-register and its Token F1 hides it.** 2.0% হেলো against the references' 76.4%,
100% নাসেনিয়া against 50%, 0.0% truncation. A respectable-looking 0.2339 from a model that is
not producing the house style — exactly why the guide demands register read-outs alongside F1.

**X5 — the default LR is right.** 3e-4 (0.2488 peak) ≈ 1e-3 (0.2475), inside noise. 3e-3 is
**broken**: final 0.1492 with 61.7% truncation and 2.7% হেলো — the divergence signature, at the
top of the seq2seq class rather than across it. Keep **1e-3**.

**X3 RAG — the best arm, but it has not earned its retriever.** Best final (0.2537, +0.0085 over
X4) *and* the most stable (lowest truncation 5.7%, smallest peak→final drop). But:
- it costs **342 min vs 134** and **+278M retriever params**;
- 🔴 **the copy-margin is thin: 0.018.** Overlap with the true target 0.2537 vs overlap with the
  *retrieved example it was shown* 0.2352. The prediction is nearly as similar to the example as
  to the right answer. Medical Bengali shares heavy boilerplate, so this is not proof of copying
  — but it is not a clean pass either, and the guide is explicit that this outranks the headline.

**Recommendation for model A: ship X4 (`plain_core_only`, lr 1e-3).** It gets within 0.0085 of
the best arm at 40% of the cost and 0% of the retriever, and its gain over the bar (+0.10) dwarfs
the X3–X4 gap. Revisit X3 only if the copy-margin can be shown to be benign.

## The budget doc's step guidance was wrong for this family

GPU_BUDGET §2② says to keep the generous 20,000-step budget on A because the E05
"under-trained by 4.4×" lesson applies to seq2seq. **It does not apply here.** X2 peaked at
**step 2,500**; four of six arms peaked at ≤5,000; every arm early-stopped far short of 20,000.
mT5 on Bengali QA converges fast. Budget **~6,000 steps with patience 6** for this family on this
task — the same numbers the doc reserved for decoders.

## Also contradicting the docs

**mT5's truncation problem did not reproduce.** INSTRUCTIONS.md warned of 27.9% truncated answers
from a previous mT5 run on this corpus. Measured here: **5.7–11.7%** against the references' 6.8%
— on target. The one arm that blew past it (X5 lr 3e-3, 61.7%) did so because the run diverged,
not because of the tokenizer.

## Checkpoints — every arm kept

`A_mT5_base/runs/<ARM>/best` with `run.json` beside the weights, plus
`runs_lr3e4/X5` and `runs_lr3e3/X5`. All bf16, A800, `transformers 4.57.3`, `torch 2.8.0+cu128`.

⚠️ **`run.json` under-reports `effective_batch` as 8.** The notebook computes `BATCH × ACCUM` and
ignores world size; the true global batch was **4 × 2 × 8 = 64** on every arm and is comparable
across them. The recorded field is wrong, not the training.
