# E09_mt5_best_input — results

**`main` ran 2026-08-10 (4,000 steps); `conv12k` 2026-08-11 (12,000 steps, a800).**

## VERDICT: English helps mT5 too — but mT5 still loses. Both halves matter.

E09 exists for exactly one pair: `E09 − E08` isolates whether the English source helps
**independently of architecture**, or only through BanglaT5's tokenizer.

| | input | Token F1 | ROUGE-L |
|---|---|---|---|
| E08 mT5 | draft only | 0.7563 | 0.7168 |
| **E09 mT5** | **english + draft** | **0.7861** | 0.7517 |
| **E09/conv12k** | **english + draft, 12,000 steps** | **0.8017** | 0.7718 |

**E09 − E08 = +0.0298.** English helps mT5 *more* than it helps BanglaT5 (+0.0220). **The
English gain is architecture-independent** — it is information, not a tokenizer artifact. That
is the one conclusion only this experiment could produce.

But mT5 remains behind at every matched budget: **0.8017 vs BanglaT5's 0.8328** at convergence.

## Checkpoints — keep every arm

| Arm | `best/` kept? | Token F1 | ROUGE-L | peak step | hours | ckpt hash |
|---|---|---|---|---|---|---|
| `main` | `E09_mt5_best_input/main/best` | 0.7861 | 0.7517 | 3,750 | 1.96 | — |
| `conv12k` | `E09_mt5_best_input/conv12k/best` | **0.8017** | 0.7718 | **11,250** | 10.78 | `fffdb026a636143f` |

Both have `submission.csv`. `conv12k`: mT5-base, 582,401,280 params, 1024/640, effective batch
64, lr 1e-3, adafactor, seed 11, bf16, a800.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| `conv12k` | **93.2** | 75.0 % | 49.3 % | 0.95 % / **0.715 %** | bf16 | a800 |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %.
**93.2 tokens against a ~100-token reference** — mT5 under-generates, and it truncates
**14× more targets than BanglaT5** (0.715 % at a 640 cap vs 0.05 % at 512). That is the
tokenizer handicap (271 vs 142 tokens per answer) showing up in the output.

## Verdict

- **Result:** for the pair (English is architecture-independent) · for mT5 as a carrier
- **What it changes:** the decision table's *"E08 ≪ 0.7724 ⇒ drop E09"* would have discarded the
  only measurement that generalises the English finding. Running it anyway was correct.
- **E10 (trim mT5's vocab) is not worth running.** Trimming addresses parameter count; mT5
  already had 2.35× BanglaT5's parameters and lost. The deficit is fragmentation, not capacity.
- **Phase 2:** E08 leaves 27.9 % of answers cut off mid-sentence (references 6.8 %). mT5 is
  closed on **both** phases.
