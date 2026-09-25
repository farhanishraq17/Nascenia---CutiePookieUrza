# E13_multitask_qa — results

**`main` 2026-08-10 (4,000 steps); `conv12k` 2026-08-11 (12,000 steps, a800).**

## VERDICT: multi-task training costs 0.017 and buys robustness nobody needs yet.

Trained jointly on the transfer task + the competition's native question→answer task
(203,477 rows: 101,737 transfer + 101,740 Q→A), built by `code/11_build_stage_datasets.py`
with 0 dev/test id overlap asserted.

| | Token F1 | ROUGE-L | vs single-task at the same budget |
|---|---|---|---|
| single-task `english_draft` @12k *(E19 seed mean)* | ~0.8291 | ~0.797 | — |
| **E13/conv12k** | **0.8155** | 0.7853 | **−0.0136** |
| E13/main @4k | 0.8092 | 0.7786 | — |

**−0.0136 is 3× the noise floor.** Splitting capacity across two tasks measurably degrades the
one being scored.

## Checkpoints

| Arm | `best/` kept? | Token F1 | ROUGE-L | peak step | hours | ckpt hash |
|---|---|---|---|---|---|---|
| `main` | yes | 0.8092 | 0.7786 | 4,000 | 1.02 | — |
| `conv12k` | `E13_multitask_qa/conv12k/best` | 0.8155 | 0.7853 | 11,000 | 2.08 | `47caf859d1d480d7` |

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | precision | GPU |
|---|---|---|---|---|---|
| `conv12k` | 99.9 | 75.0 % | 54.0 % | bf16 | a800 |

On-register — this is a genuine capacity trade-off, not a broken run.

## Outstanding deliverable

EXPERIMENT.md requires **both** scores: the transfer score *and* the question→answer score,
the latter being the robustness insurance if the alignment route is ever closed off. Only the
transfer score is recorded. The Q→A number needs a decode against `../data/question_only`:

```bash
python ../code/04_decode.py --ckpt conv12k/best --data-dir ../data/question_only \
  --split dev --limit 300 --mode beam --num-beams 8 --length-penalty 1.2 \
  --min-new-tokens 0 --max-new-tokens 320 --no-bertscore --record conv12k/dev_qa.json
```

## Verdict

- **Result:** −0.0136 on the scored task.
- **What it changes:** multi-task is not free here. It remains defensible *only* as insurance
  against the alignment route being closed — and that insurance is unpriced until the Q→A
  number above is measured.
