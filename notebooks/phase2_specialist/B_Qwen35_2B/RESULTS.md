# Qwen3.5-2B — RESULTS

**Model:** `Qwen/Qwen3.5-2B` (decoder-only) · exact params **1,881,825,088** · **Bar to beat: Token F1 0.1454**

**Ran 2026-08-19/21.** Effective batch **64** on every arm. bf16 throughout, `adafactor`, gradient
checkpointing on, LR **2e-5** except X5. Arms were spread over whatever hardware was free, so the
GPU column varies — that affects wall clock only, never the numbers.

> ### Read the `HELD-OUT` and `X7 VERIFY` columns, not `peak`
> `peak` is measured on `dev[0:300]` — **the same 300 rows the checkpoint was selected on.**
> `dev.parquet` in every data variant only *has* 300 rows (`build_data.py --dev-limit 300`), which
> is also why X7's mandatory disjoint verification had never been runnable. We built
> `dev[300:1300]` as `data/plain_devext/` + `data/rag_devext/` (leak-checked against all 118,912
> pool rows, self-retrieval asserted) and re-scored every checkpoint on it.
> **It changes the ranking.** Treat `peak` as an upper bound contaminated by selection.

## HEADLINE: the specialist works, and five arms are tied

Every trained arm clears the 0.1454 bar by **+0.10 to +0.12**. But the top five are separated by
**0.0033 on 1,000 held-out rows** — inside noise. Token F1 cannot pick a winner here; **register
can, and it separates them by a factor of five.**

## Scoreboard

| Arm | Data | peak | @step | final | **HELD-OUT** | **X7 VERIFY** | ckpt |
|---|---|---|---|---|---|---|---|
| X0 zero-shot | plain | — | — | 0.1575 | — | — | n/a |
| X1 few-shot k=4 | plain | — | — | *0.1224* | — | — | n/a |
| **X2 finetune** | plain | 0.2641 | 3000 | 0.2435 | **0.2630** | **0.2582** | done |
| X3 finetune+RAG | rag | 0.2482 | 6000 | 0.2482 | 0.2495 | — | done |
| **X4 ablation** | core_only | 0.2629 | 3000 | **0.2619** | **0.2643** | 0.2537 | done |
| X5 LR 1e-5 | plain | 0.2594 | 3500 | 0.2535 | 0.2610 | 0.2537 | done |
| X5 LR 5e-5 | plain | 0.2578 | 2500 | 0.2488 | 0.2488 | — | done |
| X6 RAG-at-inference | rag | — | — | 0.2443 | 0.2413 | — | n/a |
| X7 decode sweep | — | — | — | — | — | *see below* | n/a |
| **D1 + iCliniq** | core+7,321 | **0.2646** | 2500 | 0.2561 | 0.2625 | **0.2575** | done |
| D2 + GenMedGPT | core+5,200 | 0.2594 | 2000 | 0.2484 | 0.2558 | — | done |
| D3 + doctor_qa | core+4,651 | 0.2639 | 3000 | *(partial)* | 0.2621 | 0.2535 | done |
| X2 @ MAX_SRC 1536 | plain | 0.2536 | 3000 | 0.2484 | 0.2588 | 0.2511 | done |

**HELD-OUT** = `dev[300:1300]`, 1,000 rows, beams=4/lp=1.0. **X7 VERIFY** = each arm's own sweep
winner re-scored on a *second* disjoint slice, `devext[300:600]`.
**D3 is a partial run** — its allocation expired at step 3730/4500. Its peak (3000) and checkpoint
were already on disk and step 3500 had declined, so nothing was lost; `run.json` was rebuilt from
`trainer_state.json` and is flagged `partial: true`.

## X0 and X1: few-shot *hurts* this model

| Arm | Token F1 | ROUGE-L | tok | হেলো | নাসেনিয়া | trunc |
|---|---|---|---|---|---|---|
| X0 zero-shot | **0.1575** | 0.0878 | 190.3 | **0.0%** | 93.7% | 95.0% |
| X1 few-shot k=4 | *0.1224* | 0.0771 | 178.5 | 97.3% | 98.0% | 95.3% |

X1 lands **−0.035 below X0**. EXPERIMENTS.md's gate asks what to do if X1 ≫ X2; the opposite
happened, so the gate never fired. Note the mechanism: the four in-context examples teach the
*surface form* almost perfectly (হেলো 0.0% → 97.3%) while making the answer **worse**. The model
copies the register and stops reasoning. Both arms are ~190 tokens against a ~100-token reference
and 95% un-terminated, i.e. neither is a usable model — exactly what the fine-tune fixes.

Untrained, this model still beats the 0.1454 bar (0.1575). **It also beats C's zero-shot (0.1524)**,
which matters: C's entire case rested on owning the best X0.

## Data decomposition — and the A/B cross-check does NOT resolve

| Arm | Data | extra rows | HELD-OUT | mean tokens | vs X4 | verdict |
|---|---|---|---|---|---|---|
| **X4** *(baseline)* | competition only, 101,740 | 0 | **0.2643** | 110.4 | — | best F1, worst register |
| D1 + iCliniq | 109,061 | 7,321 | 0.2625 | 114.1 | −0.0018 | ~tied, best register of the leaders |
| D2 + GenMedGPT | 106,940 | 5,200 | 0.2558 | 114.8 | −0.0085 | weakest — the length outlier |
| D3 + doctor_qa_bangla | 106,391 | 4,651 | 0.2621 | 102.2 | −0.0022 | ~tied |
| X2 *(all extras)* | 118,912 | 17,172 | 0.2630 | 112.5 | −0.0013 | ~tied |

Every gap is **≤0.0085**. `mean_tokens` — the required diagnostic — shows no length collapse:
102–115 tokens against the references' ~100, and **D2, the arm carrying the 31-word GenMedGPT
answers, is not shortest** (114.8). So the doc's predicted mechanism does not appear, even though
D2 is the weakest arm.

### Cross-check against `A_mT5_base` — the honest answer is "unresolvable"

| held-out ranking | |
|---|---|
| **A (seq2seq)** | D1 0.2505 > D3 0.2499 > D2 0.2450 > X2 0.2426 > **X4 0.2382** |
| **B (decoder)** | **X4 0.2643** > X2 0.2630 > D1 0.2625 > D3 0.2621 > D2 0.2558 |

| | A | B | agree? |
|---|---|---|---|
| best data variant | D1 (+iCliniq) | X4 (core-only) | **no — exact opposite** |
| is core-only worst or best? | **worst** (0.2382) | **best** (0.2643) | **no** |
| does `genmedgpt` hurt? | no — D2 mid-field | weakest arm | weakly |
| does `doctor_qa_bangla` help? | yes, 2nd | 4th, ~tied | inconclusive |

**→ Verdict: the rankings invert, but every gap on both models is 0.008–0.012 — under the ~0.02
floor this task actually exhibits.** So this is **not** a clean "data effects are
architecture-specific" finding; it is a comparison the experiment lacks the power to resolve.
That matters procedurally: EXPERIMENTS.md makes a *disagreement* the trigger for running D1–D3 on
`C_BanglaAI_17B`, and that trigger cannot be evaluated. C's D arms were not run.

## Register read-out — the column that actually decides this model

| Arm | mean tokens | হেলো % | নাসেনিয়া % | **truncated %** | empty % |
|---|---|---|---|---|---|
| X2 | 112.5 | 81.2 | 85.3 | **60.0** | 0.0 |
| X3 | 151.2 | 80.3 | 86.6 | **93.0** | 0.0 |
| X4 | 110.4 | 84.1 | 84.9 | **70.8** | 0.0 |
| **X5 @1e-5** | 103.7 | 78.5 | 80.7 | **14.8** | 0.0 |
| X6 | 119.6 | 79.7 | 85.4 | 62.4 | 0.0 |
| **D1** | 114.1 | 78.5 | 85.4 | **27.3** | 0.0 |
| D2 | 114.8 | 81.2 | 84.9 | 32.0 | 0.0 |
| D3 | 102.2 | 86.8 | 82.8 | 63.7 | 0.0 |
| X2 @1536 | 129.9 | 82.1 | 83.8 | 54.4 | 0.0 |
| *references* | *~100* | *76.4* | *50.0* | ***6.8*** | — |

**`truncated %` spans 14.8 → 93.0 across arms whose Token F1 spans 0.015.** The F1 leaders X4 and
X2 fail to close a sentence on 60–71% of answers, against a reference rate of 6.8%. X5 @1e-5 is at
14.8% and D1 at 27.3% for the same F1. Since Phase 2 is judged by an LLM on *"tone, completeness,
clarity as a doctor's response"*, this is the axis that should decide the pick — not F1.

Every arm over-uses the brand name (~80–86% vs the references' 50%). No language drift and no
`<think>` leakage was observed on any arm (`enable_thinking=False` plus defensive stripping).

## RAG copy-check — RAG loses for this architecture, twice over

| Arm | Token F1 | overlap w/ TRUE target | overlap w/ SHOWN reference | **margin** |
|---|---|---|---|---|
| X3 (trained in) | 0.2495 | 0.2495 | 0.2221 | **+0.0274** answering |
| X6 (bolted on) | 0.2413 | 0.2413 | 0.2701 | **−0.0288** **copying** |

Two separate findings, and they point the same way:

- **X6 has a negative margin — it is copying the retrieved example, not answering.** Per
  EXPERIMENTS.md that arm has *failed regardless of its Token F1*. RAG cannot be bolted onto a
  plain-trained checkpoint here.
- **X3 does answer** (+0.0274) but still **loses to plain X2** on held-out (0.2495 vs 0.2630), and
  it is the worst-behaved arm in the table: 151 tokens and 93% un-terminated. Its curve was also
  still climbing at 6000 (0.2478 → 0.2480 → 0.2482), i.e. under-trained — but at ~0.0002 per 500
  steps it would need tens of thousands more steps to close 0.0135.

**→ RAG did not earn its 278M retriever on this model.** It loses trained-in and fails the
copy-check bolted-on. (Model A reached the opposite conclusion — its X3 was its best arm — so this
is architecture-specific and stated as such.)

## X7 decode sweep — a null, and the sweep itself is a trap

Swept `beams ∈ {4,8}` × `lp ∈ {1.0,1.2,1.5}`, `min_new_tokens=0`, selecting on `devext[0:300]`
and re-verifying on the disjoint `devext[300:600]`.

| arm | sweep "best" (n=300) | **disjoint VERIFY** | drop |
|---|---|---|---|
| X4 | 0.2752 | 0.2537 | **−0.0215** |
| D1 | 0.2713 | **0.2575** | −0.0138 |
| X5 @1e-5 | 0.2687 | 0.2537 | −0.0150 |
| X2 | — | 0.2582 | — |
| D3 | — | 0.2535 | — |
| X2 @1536 | — | 0.2511 | — |

Two results. **`beams=4` beats `beams=8` consistently by ~0.005–0.013 on every arm** — the one
reliable decode finding. And **`length_penalty` does nothing**: winners differ by ≤0.0013, which
is why the "best" lp varies arbitrarily between arms.

**Every sweep winner collapsed 0.014–0.022 on the disjoint slice.** This is exactly the
spurious-winner effect EXPERIMENTS.md demands the re-verification for, measured here for the first
time on this task. **Discard the 0.27x numbers.** It also contradicts GPU_BUDGET.md §3, which
ranks X7 as *"historically the cheapest real gain on the board"* — on this task it gains nothing.

## X5 — the LR sweep vindicates the *low* end, on register not on F1

| LR | peak | HELD-OUT | truncated % |
|---|---|---|---|
| **1e-5** | 0.2594 | 0.2610 | **14.8%** |
| 2e-5 *(default, = X2)* | **0.2641** | **0.2630** | 60.0% |
| 5e-5 | 0.2578 | 0.2488 | **94.8%** |

A clean inverted-U on F1 with the shipped default at the top — so the LR *class* in
INSTRUCTIONS.md is confirmed, and 2e-5 is genuinely the right value within it.

But the register column tells a different story, and it is monotonic in LR: **14.8% → 60.0% →
94.8% truncation as the learning rate rises**. 1e-5 costs 0.0020 of Token F1 (noise) and cuts
un-terminated answers **4×**; 5e-5 is worse on both axes and is the second-worst-behaved arm in
the whole study.

GPU_BUDGET §2③ recommended dropping X5 on decoders as re-deriving a known LR class. On F1 alone
that was right — the sweep confirms the default. It would have missed the register finding
entirely, which is the more useful of the two. Reported as a contradiction.

## MAX_SRC 1536 — a measured negative that overturns our own hypothesis

At `MAX_SRC=1024`, **26.1% of training rows lose prompt tokens**: `train_ddp.py` packs prompt *and*
answer into one budget for a causal model, and p95 combined is 1,348 tokens (prompt+system p95
823, answer p95 687). GPU_BUDGET §2① sized 1024 off the question alone (~400 tok), which is only
correct for the seq2seq model. Raising to 1536 drops truncated rows to 2.1%.

**It made the model worse.** Same data, same 6000 steps, only the cap changed:

| | peak | HELD-OUT | X7 VERIFY | tok | trunc |
|---|---|---|---|---|---|
| X2 @1024 | **0.2641** | **0.2630** | **0.2582** | 112.5 | 60.0% |
| X2 @1536 | 0.2536 | 0.2588 | 0.2511 | 129.9 | 54.4% |

−0.0105 peak, −0.0042 held-out, −0.0071 verify, and 17 tokens more verbose. The prompt truncation
was real and measured, and fixing it did not help — so it was not what was limiting the model.
Stated plainly because it contradicts the hypothesis we ran the arm to test.

## Trajectories

```
X2        500:0.2174 1000:0.2324 1500:0.2338 2000:0.2429 2500:0.2578 3000:0.2641 3500:0.2569 4000:0.2463 4500:0.2408 5000:0.2395 5500:0.2417 6000:0.2435
X3        500:0.2059 1000:0.2244 1500:0.2330 2000:0.2393 2500:0.2432 3000:0.2451 3500:0.2439 4000:0.2450 4500:0.2458 5000:0.2478 5500:0.2480 6000:0.2482
X4        500:0.2581 1000:0.2368 1500:0.2570 2000:0.2566 2500:0.2527 3000:0.2630 3500:0.2582 4000:0.2607 4500:0.2567 5000:0.2585 5500:0.2625 6000:0.2619
X5 1e-5   500:0.1950 1000:0.2267 1500:0.2383 2000:0.2499 2500:0.2591 3000:0.2590 3500:0.2594 4000:0.2573 4500:0.2535
D1        500:0.2227 1000:0.2397 1500:0.2469 2000:0.2532 2500:0.2646 3000:0.2576 3500:0.2558 4000:0.2539 4500:0.2561
D2        500:0.2006 1000:0.2394 1500:0.2507 2000:0.2594 2500:0.2478 3000:0.2481 3500:0.2484
D3        500:0.1744 1000:0.2427 1500:0.2626 2000:0.2596 2500:0.2607 3000:0.2639 3500:0.2610          (partial, stopped 3730)
X2@1536   500:0.2326 1000:0.2361 1500:0.2371 2000:0.2498 2500:0.2448 3000:0.2536 3500:0.2477 4000:0.2470 4500:0.2500 5000:0.2489 5500:0.2496 6000:0.2484
```

**Where these peak is itself the finding.** Every arm peaks at **2000–3500** and then decays or
flatlines — X2 loses 0.021 from step 3000 to 6000. GPU_BUDGET §2② predicted 2,750–3,500 from this
project's own model zoo and was **exactly right**; the 20,000-step budget inherited from the
BanglaT5 E05 lesson would have wasted ~5× the compute. The one exception is **X4, which is flat
from 3000 to 6000 (0.2630→0.2619)** — the only arm whose final ≈ peak, i.e. genuinely converged
rather than caught at a bounce.

## Environment actually used

| | |
|---|---|
| GPU / count | varied per arm: 8×A800 40G (X2, X3), 2×H200 (X4), 1×H200 (D1), 2×L40S (D3), 2×A100 80G (D2), 2×H200 NVL (X5) |
| precision | **bf16** (`torch.bfloat16`), never fp16 — gated on `get_device_capability()[0] >= 8` |
| optimizer | `adafactor` |
| BATCH × ACCUM × ranks | always **= 64** (e.g. 1×8×8, 4×8×2, 4×16×1) |
| MAX_SRC / MAX_TGT | 1024 / 640 (X3 & X6: 2048; X1: 4096; the cap arm: 1536) |
| measured p95 target length in this tokenizer | **687 tokens** (median 397) — so `MAX_TGT=640` truncates >5% of answers; 704+ would be correct |
| LR / warmup / schedule | 2e-5 (X5: 1e-5, 5e-5) / 300 / cosine, seed 42 |
| grad checkpointing | on |
| exact param count | **1,881,825,088** |
| torch / transformers | 2.8.0+cu128 / 5.14.1 |
| peak VRAM | ~22 GB/rank at BATCH=1 (A800 40G); ~30 GB at BATCH=4 (H200) |

**Throughput note:** every B arm ran **~4× slower than model C on identical hardware** (33 s/it
vs 7.6 s/it on 2×A100) because `flash-linear-attention`/`causal-conv1d` are not installed, so
Qwen3.5's Gated DeltaNet falls back to a torch implementation. Installing them is the single
largest speedup available for any future work on this model.

## Verdict

- **Best arm: D1 (+iCliniq).** Not because it leads Token F1 — five arms tie there — but because
  it is the only arm that is simultaneously top-tier on F1 (0.2625 held-out, 0.2575 on the
  disjoint verify, the best of any arm on that slice), best-in-class on ROUGE-L among the leaders
  (0.1830), and keeps un-terminated answers to 27.3% where X4 and X2 sit at 60–71%.
- **Runner-up: X5 @1e-5** if the judge's tone/completeness axis is weighted above F1 — 14.8%
  truncation, closest of any arm to the reference distribution, at a cost of 0.0015 F1.
- **Does it clear 0.1454?** Yes, by **+0.117** on held-out data (0.2625 vs 0.1454) — 27× the
  stated noise floor, and it holds up on two independent disjoint slices.
- **Did RAG earn its 278M retriever?** **No.** X3 loses to plain by 0.0135 held-out; X6 copies
  (margin −0.0288) and has failed by EXPERIMENTS.md's own criterion.
- **Contradictions with the documentation**, stated plainly:
  1. **X7 is a null**, not "the cheapest real gain" (GPU_BUDGET §3) — and its winners are
     selection artifacts that lose 0.014–0.022 on a disjoint slice.
  2. **`MAX_SRC=1024` truncates 26.1% of training rows** (GPU_BUDGET §2① sized it for seq2seq),
     **but raising it to 1536 made the model worse.** Both halves are contradictions.
  3. **Dropping X5 on decoders (§2③) would have hidden a 4× register improvement** at 1e-5.
  4. **The A/B data cross-check is unresolvable**, so the trigger for running C's D-arms cannot be
     evaluated — the design assumed this comparison would be decisive.
  5. **Few-shot hurts this model** (X1 0.1224 < X0 0.1575), and it does so by teaching register
     while degrading content.
