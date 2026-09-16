# E03_all_inputs — results

**Ran 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL, bf16.** See `../_slurm/README.md`.

## ➖ VERDICT: all three fields ≈ two fields. **The signals are not complementary — ship E01.**

| | Input | src p95 | Token F1 | ROUGE-L | pred LB |
|---|---|---|---|---|---|
| 🏆 incumbent | draft, 384/256 | — | 0.7724 | 0.7324 | 0.85030 *(actual)* |
| **E01** | **english + draft, 768/512** | 603 | **0.8027** | 0.7719 | 0.8676 |
| **E03** | **question + english + draft, 1024/512** | **734** | **0.8040** | 0.7727 | 0.8681 |
| E02 | question + draft, 640/512 | 387 | 0.7741 | 0.7361 | 0.8474 |

**E03 − max(E01, E02) = 0.8040 − 0.8027 = +0.0013.** Inside the 0.0044 noise floor.

Adding the patient question to `english + draft` buys **nothing** — which is the same answer E02
gave from the other direction (question + draft ≈ draft alone). Two independent measurements, one
conclusion: **the question carries no information this task can use.**

Per the decision table — *"E03 ≈ max(E01, E02) ⇒ one field dominates ⇒ ship the shorter input"* —
**the Tier-1 winner is `english_draft`**, and it wins on cost as well as parity: E01 trains in
**1.08 h** against E03's **1.35 h** (25 % cheaper) on a p95 source 131 tokens shorter.

## Checkpoints — 🔴 keep every arm, including the losers

| Arm | `best/` kept? | Kaggle dataset | Token F1 | ROUGE-L | peak step | hours | notes |
|---|---|---|---|---|---|---|---|
| `main` | ✅ `E03_all_inputs/main/best` | *(not uploaded)* | 0.8040 | 0.7727 | **3,750** | 1.35 | ckpt hash `7cd7aaa88baa8502` · 247,577,856 params |

`main/submission.csv` is written. Numerically this is the **highest-scoring arm in the program so
far** — it is not "the winner" only because E01 matches it inside noise with a shorter input, and
that tie is what the decision table resolves on cost.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `main` | 99.8 | 75.3 % | 53.0 % | 0.83 % / 0.05 % | bf16 | H100 NVL |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %. On target on all three.
Decoded at **max_source_len 1024**, the cap it trained at — verified in `dev.json`, and worth
stating because the earlier default of 384 would have fed this arm a *third* of its input
(see BUG-04 in `../../LOCAL_EXPERIMENTS.md`).

## Trajectory

| step | 250 | 500 | 750 | 1000 | 1250 | 1500 | 1750 | 2000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .6789 | .7433 | .7547 | .7705 | .7739 | .7843 | .7836 | .7906 |

| step | 2250 | 2500 | 2750 | 3000 | 3250 | 3500 | **3750** | 4000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .7899 | .7960 | .8000 | .7991 | .8027 | .8022 | **.8040** | .8026 |

Still climbing at the budget's end, like every other arm here. The last 1,000 steps bought
+0.0040 — about the noise floor, so E03 is closer to flat than E01 was, but neither has converged.

## Verdict

- **What it must beat:** incumbent 0.7724 / 0.7324, and `max(E01, E02)`
- **Result:** ✅ vs the incumbent (+0.0316) · ➖ vs E01 (+0.0013, within noise)
- **What it changes:**
  - **Tier 1 is settled: `english_draft`.** Downstream experiments (E05b, E06, E09, E12, E13,
    E19) all point there.
  - **E07's premise weakens further.** E07 re-runs *this* input at 1280/768; E03 already truncates
    only 0.83 % of sources, so E07 is testing a cap that binds on fewer than 1 row in 100.
  - Keep this checkpoint for E14: it reads a field no other member reads, so its errors have the
    best chance of being uncorrelated with E01's.
- **Row-level disagreement with the incumbent:** pending `13_disagreement.py`.

## Anything surprising

**The two "does field X help" questions gave consistent answers from opposite directions.**
E02 (question added to *draft*) → +0.0017. E03 (question added to *english + draft*) → +0.0013.
A field that is uninformative on its own and stays uninformative alongside a strong field is
about as clean a negative as this program can produce — no interaction effect hiding anywhere.

⚠️ E03 is the arm most exposed to BUG-04: at the old 384-token decode default it would have been
scored on roughly the first third of a 734-token p95 input. It was decoded after the fix, so the
number above is clean — but any all_inputs number produced before 2026-08-09 should be discarded
rather than compared.
