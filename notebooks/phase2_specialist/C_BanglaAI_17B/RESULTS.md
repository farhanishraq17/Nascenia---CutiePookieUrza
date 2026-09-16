# Bangla-AI-1.7B — RESULTS

**Model:** `swapnillo/Bangla-AI-1.7B` (decoder-only, Qwen3-1.7B base) · exact params
**1,720,574,976** (matches the documented count exactly) · **Bar to beat: Token F1 0.1454**

**Ran 2026-08-20/21.** Effective batch **64**, bf16, `adafactor`, gradient checkpointing on,
LR 2e-5. Caps set from **this model's own tokenizer**, measured before training — see below.

> ### 🔴 This model was scheduled to be CUT, and was run anyway
> GPU_BUDGET §4 nominates C as the first thing to drop, and its gate fired: both A and B cleared
> the bar with fluent Bengali. C ran because §4's own carve-out applied — *"When NOT to cut C:
> you have idle GPUs. The three-way comparison is strictly more informative — if it is free, run
> it."* Capacity freed up on 2026-08-20, so X2/X3/X4/X6/X7 were run on it. **Running it was
> worth it — but it should not be shipped over B D1.** C ties B on the 1,000-row held-out set and
> is much better behaved, yet drops twice as far as D1 on the second disjoint slice. Both halves
> of that matter; see the verdict.

## 🥇 HEADLINE: the "bad tokenizer" model is the best-behaved model in the bake-off

C was included to test whether Bengali instruction-tuning compensates for a 4.85× tokenizer
handicap. **The answer splits in two.** On *register* it wins outright: 12.8% un-terminated answers against
B's 27–71%, reference-matching length, and the smallest full pipeline of the three. On *score* it
ties B on the 1,000-row held-out set (0.2583 vs 0.2625, inside noise) but **does not hold that up
on a second disjoint slice** — 0.2486 against B D1's 0.2575. The tokenizer handicap did not stop
it competing; weaker generalization is what keeps it out of the bundle.

## Scoreboard

| Arm | Data | peak | @step | final | **HELD-OUT** | ckpt |
|---|---|---|---|---|---|---|
| **X0 zero-shot** | plain | — | — | **0.1524** | — | n/a |
| **X1 few-shot k=4** | plain | — | — | **0.1636** ✅ | — | n/a |
| **X2 finetune** 🥇 | plain | **0.2577** | 2500 | 0.2491 | **0.2583** | ☑ |
| X3 finetune+RAG | rag | 0.2525 | 2000 | *(partial)* | 0.2516 | ☑ |
| **X4 ablation** | core_only | 0.2574 | 1500 | 0.2528 | 0.2572 | ☑ |
| X5 LR sweep | — | *not run* | | | | — |
| X6 RAG-at-inference | rag | — | — | 0.2543 | — | n/a |
| X7 decode sweep | — | — | — | **0.2596** → **0.2486** *(disjoint)* | n/a |
| D1 / D2 / D3 | — | *not run* | | | | — |

**HELD-OUT** = `dev[300:1300]`, 1,000 rows no checkpoint was selected on (`data/plain_devext/`,
`data/rag_devext/`), beams=4/lp=1.0. **X5 was dropped** per GPU_BUDGET §2③. **D1–D3 were not run**
because their trigger — a clear A/B disagreement on the data question — turned out to be
unresolvable at this task's noise level (see `B_Qwen35_2B/RESULTS.md`); the condition could
neither be confirmed nor ruled out.
**X3 is a partial run**, stopped at step 2000/4500 by request to free its 8×A800 allocation; its
peak and checkpoint were already on disk, and `run.json` is flagged `partial: true`.

## 🔴 X0 reproduced — and C's central claim still fails

| Arm | Token F1 | ROUGE-L | tok | হেলো | নাসেনিয়া | trunc |
|---|---|---|---|---|---|---|
| X0 zero-shot | **0.1524** | 0.0967 | 174.4 | 0.7% | 8.0% | 85.7% |
| X1 few-shot k=4 | **0.1636** | 0.1090 | 158.1 | 14.0% | 60.7% | 61.3% |

**X0 reproduces the documented 0.1564 at 0.1524** — a 0.0040 gap, i.e. within noise, on different
hardware. The headline claim in INSTRUCTIONS.md is real: this model clears the 0.1454 bar with no
training at all.

**But INSTRUCTIONS.md set an explicit test and C fails it:** *"Should be the best X0 of the three
— this is its main advantage… If X0 is not **better than B's**, its instruction-tuning is not
helping and the case for this model largely collapses."* B's zero-shot is **0.1575**. C's is
**0.1524**. C loses. Its one distinguishing advantage does not exist.

**X1 is fixed, and it is the best few-shot result in the bake-off.** The documented X1 was
`0.0371` — a broken run where `max_length=3072` truncated the actual question away behind four
in-context examples. We measured the 4-shot block at **4,715 tokens** in this tokenizer and set
`MAX_SRC=6144`; X1 then came in at **0.1636**, above its own X0 *and* far above B's X1 (0.1224).
So the documented fix works exactly as described, and few-shot **helps C while hurting B** —
plausibly because instruction-tuning makes it better at using in-context examples.

## Register read-out — where this model wins outright

| Arm | mean tokens | হেলো % | নাসেনিয়া % | **truncated %** | empty % |
|---|---|---|---|---|---|
| **X2** | 103.8 | 77.1 | 81.1 | **12.8** ✅ | 0.0 |
| X3 | 106.3 | 75.0 | 82.3 | 17.2 | 0.0 |
| **X4** | 102.0 | 76.7 | 56.7 | **16.2** ✅ | 0.0 |
| X6 | 111.8 | — | — | 13.3 | 0.0 |
| *references* | *~100* | *76.4* | *50.0* | ***6.8*** | — |
| *(B's best arms, for contrast)* | *110–115* | *78–84* | *85* | ***27–71*** 🔴 | *0.0* |

This is the strongest result in this file. **C X2 sits at 103.8 tokens against a 100-token
reference and 77.1% হেলো against 76.4%** — essentially on the reference distribution — and
truncates at 12.8% where B's F1 leaders truncate at 60–71%. **X4 is also the only arm in the entire
bake-off to get নাসেনিয়া nearly right** (56.7% vs the references' 50.0%); every B arm over-uses it
at ~85%. Phase 2 is judged on *"tone, completeness, clarity as a doctor's response"*, and on that
axis C is the best model here by a wide margin.

## 🔴 RAG copy-check — C copies even with retrieval TRAINED IN

| Arm | Token F1 | overlap w/ TRUE target | overlap w/ SHOWN reference | **margin** |
|---|---|---|---|---|
| X3 (trained in) | 0.2516 | 0.2516 | 0.2717 | **−0.0201** 🔴 **copying** |
| X6 (bolted on) | 0.2543 | 0.2543 | 0.2787 | **−0.0244** 🔴 **copying** |

**Both RAG arms have negative margins.** Per EXPERIMENTS.md both have failed regardless of score.
This is worse than B, where at least the trained-in arm answered (+0.0274) and only the bolted-on
one copied. Note X6 (0.2543) even *out-scores* X3 (0.2516) — so on this model, training retrieval
in bought nothing at all, and the higher-scoring arm is the one copying hardest.

**→ RAG did not earn its 278M retriever on this model either.** All three models now agree that
retrieval cannot be bolted on; C and B further agree it should not be trained in for a decoder.

## X7 decode sweep

On X2's checkpoint, `dev[0:300]`, `min_new_tokens=0`:

| beams | lp | Token F1 | tok | trunc |
|---|---|---|---|---|
| 4 | **1.5** | **0.2596** | 108.4 | 13.7% |
| 4 | 1.2 | 0.2594 | 107.6 | 14.7% |
| 4 | 1.0 | 0.2579 | 104.4 | 14.0% |
| 8 | 1.5 | 0.2524 | 112.7 | 15.7% |
| 8 | 1.2 | 0.2496 | 107.3 | 16.3% |
| 8 | 1.0 | 0.2446 | 100.9 | 17.3% |

**`beams=4` beats `beams=8` by 0.007–0.013** — the same direction as A and B, and the one decode
finding that reproduces across all three models. `length_penalty` moves 0.0017 across its whole
range, i.e. nothing. 🔴 **The held-out re-verification has now landed, and it is the worst news in this file.**
Selecting on `devext[0:300]` and re-scoring the winner on the disjoint `devext[300:600]`:

| arm | sweep winner | **disjoint VERIFY** | drop |
|---|---|---|---|
| C X2 | 0.2596 (b4/lp1.5) | **0.2486** | −0.0110 |
| C X4 | — (b4/lp1.5) | **0.2455** | — |

C's arms lose **0.0096–0.0116** going from the 1,000-row held-out set to the second disjoint
slice, roughly **twice** B D1's drop (0.2625 → 0.2575, −0.0050). On that slice C X2 sits **0.0089
below B D1** — the widest the two have been separated on any measurement. See the revised verdict.

## X4 vs X2 — the extra 17k rows are neutral here

Held-out **0.2572 (core-only) vs 0.2583 (all extras)** — a 0.0011 gap, far inside noise.
Per EXPERIMENTS.md's rule ("if the difference is under 0.0044, prefer the smaller dataset"),
**ship `plain_core_only`** for this model: 101,740 rows instead of 118,912, 25% less data, fewer
external sources to disclose, and it trained to its peak in 1,500 steps versus X2's 2,500.

## Trajectories

```
X2   500:0.1892 1000:0.2323 1500:0.2301 2000:0.2569 2500:0.2577 3000:0.2525 3500:0.2491 4000:0.2450 4500:0.2491
X3   500:0.1920 1000:0.2411 1500:0.2466 2000:0.2525                                 (partial, stopped at 2000)
X4   500:0.2328 1000:0.2484 1500:0.2574 2000:0.2567 2500:0.2522 3000:0.2514 3500:0.2460 4000:0.2552 4500:0.2528
```

**X4 peaks at 1,500 steps** — the earliest peak of any arm in the bake-off, and it is still within
0.002 of that peak at 4,500, i.e. stable rather than bouncing. X2 peaks at 2,500 and decays.
X3 was still climbing when stopped (0.2411 → 0.2466 → 0.2525) but decelerating hard, and at
+0.0055 per 500 steps it was not on track to reach X2's 0.2583.

## Environment actually used

| | |
|---|---|
| GPU / count | X2: 1×H200 140G · X4: 2×A100 80G · X3: 8×A800 40G · X6/X7: 4×RTX PRO 6000 Blackwell |
| precision (must not be fp16) | **bf16** (`torch.bfloat16`), gated on `get_device_capability()[0] >= 8` |
| optimizer | `adafactor` |
| BATCH × ACCUM (must be 64) | **= 64** (4×16×1 on H200, 2×16×2 on A100, 1×8×8 on A800) |
| MAX_SRC / MAX_TGT | **2560 / 1280** (X1: 6144; X3: 4608) |
| **measured p95 target length in this tokenizer** | **1,149 tokens** (median 651, max 1,482) |
| LR / warmup / schedule | 2e-5 / 300 / cosine, seed 42 |
| exact param count | **1,720,574,976** |
| peak VRAM | ~123 GB at BATCH=4 (H200); ~23 GB/rank at BATCH=1 (A800) |
| torch / transformers | 2.8.0+cu128 / 5.14.1 |
| combined pipeline | 247,577,856 (champion) + 1,720,574,976 = **1,968,152,832** — 1.03B under the 3B cap |

🔴 **The documented `MAX_TGT=640` starting value would have been a silent disaster.** The p95
target in this tokenizer is **1,149 tokens** — the shipped default would have cut off more than 5%
of answers and the score would have measured the cap, not the model. This is precisely the failure
INSTRUCTIONS.md warns "already invalidated three arms in this project's model zoo." We ran the
length check first and set 1280.

## Verdict

- **Best arm: X2 (plain), decoded at beams=4.** Held-out **0.2583**; X4 is statistically identical
  (0.2572) and cheaper, so **X4 is the better ship** if the 0.0011 is treated as the noise it is.
- **Does it clear 0.1454?** Yes, by **+0.113** — 26× the stated noise floor.
- **Did RAG earn its 278M retriever?** **No** — both RAG arms copy the retrieved example (margins
  −0.0201 and −0.0244) and have failed by EXPERIMENTS.md's criterion.
- **Was cutting C the right call?** **Partly — and the disjoint slice is what decides it.** On
  the 1,000-row held-out set C X2 (0.2583) is within 0.0042 of B D1 (0.2625), i.e. tied, with less
  than half the truncation. But on the *second* disjoint slice C falls to **0.2486** against D1's
  **0.2575** — a 0.0089 gap, and C drops about twice as far as D1 does between the two slices.
  **So C's score does not hold up on data it was not selected on, and B D1 remains the pick.**
  What survives is narrower but still real: C is the best-behaved model in the bake-off
  (12.8% truncation, reference-matching length, নাসেনিয়া nearly right) and its pipeline is 161M
  parameters smaller. Running it was worth it — the gate's cost premise was wrong (below) — but
  it should not be shipped over D1.
- **Contradictions with the documentation**, stated plainly:
  1. **C is ~2× cheaper than costed.** GPU_BUDGET §1 lists its base at 556 min/1k steps on an
     A800; measured **127 min/1k on 2×A100**. §5 asks for exactly this to be reported when it
     diverges by >30%. The cost premise behind "cut C first" was too pessimistic.
  2. **C's tokenizer handicap is real but smaller than stated** — 1,149 p95 target tokens vs
     Qwen3.5-2B's 687, i.e. **1.67×**, not the documented 4.85×/2.3×. And it did not translate
     into worse output: C's answers land closer to the reference length than any B arm's.
  3. **The claim that C should own the best X0 is false** — B's zero-shot beats it (0.1575 vs
     0.1524). By INSTRUCTIONS.md's own test the case for C "largely collapses" — yet C finished
     level with B on score and ahead on register. **The stated rationale for including C was
     wrong, and the model was worth including anyway.**
  4. **Instruction-tuning helps few-shot, not zero-shot.** C's X1 (0.1636) is the best
     zero/few-shot number in the bake-off and beats its own X0, while B's X1 *hurts* (0.1224 vs
     0.1575). That is the real signature of its instruction-tuning, and no document predicted it.
  5. **97% of this model's wall clock was evaluation, not training** — 135 min per generation eval
     (8750/7604/8029 s) versus 2.5 h of total training for X3. The tokenizer handicap shows up as
     *eval* cost, which no budget in these documents accounts for.
