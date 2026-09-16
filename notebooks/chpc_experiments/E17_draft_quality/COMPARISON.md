# E17 retranslation comparison

## Batch 001 — 10-row early probe

This comparison uses the first 10 rows of `PROBE_200_dev.csv`, identified by the
same `hcm_id` values in both translator outputs. It is an early diagnostic, not
the E17 verdict; the planned decision set is 200–1,000 rows.

| Translator | Token F1 | ROUGE-L | Token F1 vs Google | ROUGE-L vs Google | Token-F1 wins vs Google |
| --- | ---: | ---: | ---: | ---: | ---: |
| Google Translate draft | 0.6230 | 0.5595 | — | — | — |
| **Claude** | **0.6947** | **0.6336** | **+0.0717** | **+0.0741** | **10/10** |
| Codex | 0.6483 | 0.6087 | +0.0253 | +0.0491 | 6/10 |

Directly comparing the two LLM translations:

| Comparison | Token-F1 difference | ROUGE-L difference | Token-F1 row wins |
| --- | ---: | ---: | ---: |
| **Claude − Codex** | **+0.0464** | **+0.0250** | **7/10 Claude** |

### Paired Token-F1 statistics

| Comparison | Mean difference | SD | SE | t statistic |
| --- | ---: | ---: | ---: | ---: |
| Claude − Google | +0.0717 | 0.0517 | 0.0163 | 4.38 |
| Codex − Google | +0.0253 | 0.0595 | 0.0188 | 1.34 |
| Claude − Codex | +0.0464 | 0.0676 | 0.0214 | 2.17 |

The t statistics are descriptive only. With `n=10`, neither normality nor a
stable population estimate should be assumed.

## Per-row Token F1

| `hcm_id` | Google | Claude | Codex | Best |
| ---: | ---: | ---: | ---: | --- |
| 2464 | 0.4968 | 0.5350 | **0.5621** | Codex |
| 92052 | 0.6937 | 0.7101 | **0.7286** | Codex |
| 52420 | 0.6570 | **0.7071** | 0.6861 | Claude |
| 101941 | 0.6172 | **0.6848** | 0.6747 | Claude |
| 10398 | 0.5657 | 0.6943 | **0.7225** | Codex |
| 92474 | 0.6907 | **0.7009** | 0.6316 | Claude |
| 101645 | 0.5325 | **0.6928** | 0.5241 | Claude |
| 29139 | 0.6350 | **0.6667** | 0.6204 | Claude |
| 80410 | 0.6995 | **0.8213** | 0.7059 | Claude |
| 7647 | 0.6421 | **0.7340** | 0.6268 | Claude |

## Register-contamination check

| Translator | Starts with target-specific `হেলো` | Contains `নাসেনিয়া` |
| --- | ---: | ---: |
| Google Translate | 0/10 | 0/10 |
| Claude | 0/10 | 0/10 |
| Codex | 0/10 | 0/10 |

All three comparisons are free of the two known target-register shortcuts. The
scores measure translation choices rather than injected Nascenia styling.

## Interpretation

Claude's early gain is reproduced exactly from the saved file and is the
strongest result: `+0.0717` Token F1 with all 10 rows beating Google. Codex also
beats Google on the aggregate metrics, but the Token-F1 gain is only `+0.0253`,
with four rows losing. On this small batch, Codex therefore does **not** reproduce
Claude's translation quality closely enough to assume it is an equivalent
production translator.

The next honest decision point is still the 200-row paired probe. Do not project
either result to all 107,737 rows from this table alone.

## Experimental caveat

The Codex batch was not perfectly blind. During the initial repository audit,
Codex inspected part of Claude's `batch_001.py` before producing its own file.
The Codex translations were subsequently written from the English source, but
the exposure means this should be treated as a practical comparison rather than
a rigorously blinded model evaluation. A clean 200-row comparison should use
unseen rows or be generated before either model can inspect the other's output.

## Files and method

- Source: `PROBE_200_dev.csv`, first 10 rows.
- Claude predictions: `claude_batches/batch_001.csv`.
- Codex predictions: `codex_batches/batch_001.csv`.
- Google predictions and references: `aligned_pairs.csv`, joined by `comp_id`.
- Metric implementation: `NOTEBOOKS/metric.py`, default punctuation-stripping
  multiset Token F1 and ROUGE-L F1.
- Codex translator: GPT-5-based Codex desktop session; the exact serving snapshot
  is not exposed by the client.
- Translation policy: faithful and plain; sentence order retained; no added
  greeting, Nascenia branding, medical advice, or sign-off; source corruptions
  preserved rather than repaired.
- Date: 2026-08-07 (Asia/Dhaka).

