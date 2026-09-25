# GPU_BUDGET — measured costs, and what to cut first

**⏱ You have 5 days.** Phase 2 bundle is due **Aug 25, 12:00 GMT+6**.

**This file does not tell you how to schedule your fleet — you know your hardware, I don't.**
What it gives you is the part you *can't* derive yourself: **throughput measured from this
project's own ~60 completed runs**, the relative cost structure between the three models, and a
priority order for what to drop when time runs short.

**Budget the wall clock yourself** from the rates in §1 and whatever GPUs you actually have.

---

## 1. Measured throughput — minutes per 1,000 training steps

Read out of the `run.json` files of previously completed arms in this project. Real numbers, same
codebase, same data.

| Model | GPU | src len | min / 1k steps | n runs |
|---|---|---|---|---|
| BanglaT5 (247M) | A800 40GB | 768 | **22.7** | 22 |
| BanglaT5 | H100 NVL | 768 | **14.4** | 13 |
| BanglaT5 | L40S | 768 | 26.2 | 4 |
| BanglaT5 | RTX A6000 | 768 | 35.6 | 3 |
| **mT5-base (580M)** — model **A** | **A800 40GB** | **1024** | **53.9** | 1 |
| mT5-base | H100 NVL | 640 | 26.0 | 2 |
| Gemma-2-2B | A800 40GB | 1536 | 314 | 1 |
| **Qwen3-1.7B** — model **C**'s base | **A800 40GB** | **2560** | **556** | 1 |
| **Qwen3.5-2B** — model **B** | **A800 40GB** | **1536** | **798** | 1 |

H100 NVL measured **~1.9× faster** than A800 on the same BanglaT5 config — scale accordingly if
your fleet differs.

### The one structural fact

**Decoders cost 15–35× more per step than BanglaT5, and ~15× more than mT5-base.**

Model **A is nearly free. B and C are where the entire budget goes.** Any scheduling decision you
make should start from that asymmetry.

---

## 2. Three config changes that cost nothing scientifically

Apply these before costing anything — they change the price substantially and give up no
information.

**① `MAX_SRC 2048` → `1024` on every arm except X3 (RAG).** **Biggest single saving.**
A plain patient question is ~77 words ≈ 400 tokens. Only the RAG arm carries a full reference case
and genuinely needs 2048. The global 2048 in the shipped notebooks was over-cautious. **Roughly
halves the cost of X2, X4 and D1–D3.**

**② `MAX_STEPS 20000` → `6000`, patience 8 → 6 — decoders only (B and C).**
The 20,000 budget comes from this project's E05 lesson, where the champion turned out to be
under-trained by 4.4×. **That lesson was BanglaT5 on register transfer and does not transfer
here**: the decoder arms in this project's own model zoo peaked at **2,750–3,500 out of 4,000**.
**Keep the generous budget on A** — it is seq2seq, it is cheap, and the E05 lesson genuinely
applies to that family.

**③ Drop X5 (the LR sweep, 3 runs) on B and C.** It re-derives a learning-rate class that this
project's E18 model zoo already established for these exact families. **Keep X5 on A** — cheap
there, and seq2seq LR was never swept on this task.

---

## 3. Priority order — what matters most, if not everything fits

Run top-down. Stop wherever your budget runs out.

| Priority | What | Why it ranks here |
|---|---|---|
| **1** | **X0 + X1 on all three** | Nearly free (decode only, ~20–40 min each). Catches a broken setup *before* you spend real GPU-hours on it |
| **2** | **X2 on A and B** | **This is the experiment.** Without it there is no Phase 2 model at all |
| **3** | **X3 on A and B** | Does RAG earn its 278M retriever? Decides the whole architecture |
| **4** | **X7 decode sweep on the winner** | No training. Historically the cheapest real gain on the board |
| **5** | X4 + D1–D3 on A | Cheap on mT5; answers the data question for everyone |
| **6** | X4 + D1–D3 on B | The A/B data cross-check. Valuable, but the most expensive way to buy it |
| **7** | Model C entirely | See the gate in §4 |

**Do not cut by shrinking runs instead of dropping arms.** A truncated X2 that never converged is
worse than no X2 — it produces a number that looks like a measurement and isn't. If you are out of
time, **drop whole arms and keep the rest honest.**

**Never cut X2 on both A and B.** At least one must complete or the deliverable does not exist.

---

## 4. CUT MODEL C IF A OR B LOOKS GOOD

**`C_BanglaAI_17B` is the first thing to drop.**

### The gate — evaluate as soon as A's and B's X2 arms land

> **If either A or B clears Token F1 `0.1454` by more than the `0.0044` noise floor and produces
> fluent, on-topic Bengali — stop model C.**

Spend the time on the winner instead: train it longer, run X7 properly with the disjoint
verification, or **build the combined routing inference script** — which is still unwritten and is
a hard requirement for the Phase 2 bundle. **Do not run C to completion out of symmetry.**

### Why C is the right one to cut

1. **Its tokenizer is structurally the worst of the three — 689 tokens per Bengali answer**, versus
   Qwen3.5-2B's 294 and mT5's 271. A **4.85× handicap** that instruction-tuning cannot fix. Its
   base scored **0.7287** in this project's model zoo — bottom of the field.
2. **Its one distinguishing advantage is a *zero-shot* advantage, and it is already measured.**
   X0 = **0.1564** (recorded in `C_BanglaAI_17B/RESULTS.md`) — genuinely good, already above the
   bar untrained. But that is exactly the property **fine-tuning A or B overwrites.** Once either
   is trained, C's head start is gone.
3. **It is the only model whose case rests on an untested assumption** — that Bengali
   instruction-tuning compensates for a bad tokenizer. A and B each have measured Bengali
   competence *and* a good tokenizer.

### When NOT to cut C

- **Both A and B come in under 0.1454.** Then C's strong zero-shot is the best signal you have and
  it becomes the primary track.
- **A and B disagree sharply on the D-arms.** That means data effects are architecture-specific,
  and a third architecture is worth measuring.
- **You have idle GPUs.** The three-way comparison is strictly more informative — if it is free,
  run it.

---

## 5. Sanity-check the rates early, against your own hardware

Two assumptions in §1 could be wrong in your favour or against it. **Both are cheap to check and
expensive to discover late.**

- **Sequence-length scaling is treated as linear here.** If attention dominates, the true cost is
  closer to quadratic and **the decoder numbers are under-estimates.**
  **After the first 500 steps of B's X2, compute `elapsed_min / 0.5` and compare it to what §1
  predicts for your GPU.** If it is materially worse, **cut model C immediately** rather than
  finding out three days in.
- **Early-stop step counts are inferred, not measured for this task.** Nothing has ever trained on
  RAG-shaped Bengali QA at convergence. The trajectory in each arm's `run.json` is the ground
  truth — **report it**, because it tells the next person what budget to set.

If your measured throughput diverges from §1 by more than ~30%, **say so and re-plan** rather than
pushing on with a schedule built on the wrong numbers.
