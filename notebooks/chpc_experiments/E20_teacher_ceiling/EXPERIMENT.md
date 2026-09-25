# E20 — Large-teacher ceiling probe, then distillation

**Tier 4 — DATA · Priority: HIGHEST CEILING · unlocked by unlimited GPU**

## The question

> A model far over the 3B cap **cannot be submitted** — but it can *teach*. First: can a
> 235B model do register transfer better than our 248M one at all? Only if yes is there
> anything to distill.

## Why it matters

Every other experiment tunes a small model. This is the only one that asks whether a
**fundamentally more capable model** has headroom our student could inherit — and the cap does
not block it, because **the teacher never ships.** Only the ≤3B student is submitted.

**But the premise is genuinely uncertain, and that is why this is staged.** Register transfer is
*idiosyncratic*: the task is matching one particular translator's fingerprint, not producing good
Bengali. A 235B model has no way to know that fingerprint zero-shot. Our 248M student learned it
from 101,737 examples — which is exactly the kind of thing fine-tuning does better than scale.

So a plausible outcome is that **the teacher loses to the student**, and the distillation stage
never runs. That result is worth having in two hours.

## Stage 1 — the ceiling probe (cheap, decisive, gates everything below)

Run the teacher **few-shot** on 300 dev rows. No training.

| | |
|---|---|
| Teacher | `Qwen/Qwen3-235B-A22B` (or whatever wins E17) |
| Prompt | 20 in-context `(draft → target)` pairs drawn **only from train**, then the dev draft |
| Decoding | greedy, `enable_thinking=False` |
| Cost | a few GPU-hours, no training |

**The in-context examples must come from `train` only.** Drawing them from dev leaks the
evaluation set and the number becomes meaningless. This is the same trap that removed 6,000 rows
from `warmstart_corpus`.

### Stage-1 gate

| Teacher Token F1 | Meaning | Next |
|---|---|---|
| **> 0.82** | Real headroom above the student's 0.7724 | **Run Stage 2** |
| 0.77 – 0.82 | Marginal — distillation would chase a thin margin | Judgment call; prefer E05 |
| **< 0.7724** | **Scale does not substitute for fine-tuning on a fingerprint-matching task.** | **Stop. Do not run Stage 2.** Record it — it is a genuinely useful negative that closes the whole "bigger teacher" line |

## Stage 2 — sequence-level KD (only if Stage 1 clears 0.82)

Teacher generates register-transfer outputs on the **101,737 train inputs**; the student trains on
those instead of, or mixed with, gold.

**Why train on teacher output when gold targets already exist?** Sequence-level KD often beats
gold for a small student: the teacher's output distribution is more *self-consistent* than human
gold, so a low-capacity student fits it with less of its budget spent on irreducible noise. It is
a real technique with a real mechanism — not a hedge.

Run three arms, identical apart from the target:

| Arm | Student target |
|---|---|
| **A** *(control)* | gold only — this is the incumbent |
| **B** | teacher output only |
| **C** | 50/50 gold + teacher |

Student: BanglaT5, or the E18 decoder if it won. Everything else matches the Tier-1 winner's
config so the target is the only variable.

## What it must beat

**Stage 1:** the student's **0.7724** — the teacher must clear it to be worth distilling.
**Stage 2:** arm **A** (gold-only), which reproduces the incumbent.

## How to read the result

| Pattern | Conclusion |
|---|---|
| B or C > A by >0.0044 | Distillation works. **The teacher never ships — cap satisfied**, only the student is submitted |
| C > B | Gold carries signal the teacher loses; keep the mix |
| A ≥ B and A ≥ C | Gold is already the better target. Close the line; the earlier ceiling probe told you why |

## Disclosure

Teacher-generated training data is **external data processed by an external model**. Rules §2.6.a
requires disclosing it: model name and version, the exact prompt, the in-context example policy,
row counts, and the date. Record these as you go — reconstructing them for the Phase 2 write-up
afterwards is far harder.

Also confirm the teacher's licence permits using its outputs to train another model. Some model
licences restrict exactly this; check before Stage 2, not after.

---

## Non-negotiables (every experiment)

- **bf16 on sm_80+, fp32 otherwise. NEVER fp16** — T5 goes NaN *silently*.
- **Never change the split**: `--seed 42 --dev-size 5000`.
- **In-context examples from `train` only** — never dev or test.
- **Report Token F1 and ROUGE-L**, never the local composite.
- **Ignore differences below 0.0044.**
- **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.

Record in [`../RESULTS.md`](../RESULTS.md).
