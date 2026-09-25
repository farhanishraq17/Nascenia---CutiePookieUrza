# E23_data_filter — results

**Not in the original 20-experiment program.** Added 2026-08-12 as the last data lever with a
mechanism behind it, after every other lever had been measured and closed.

## The question

The training data was audited first (`_slurm/analysis/`): alignment is near-perfect (median
draft↔target Token F1 **0.604**, only **0.11 %** of pairs below 0.10), duplicates are 2.15 %,
degenerate targets 0.84 %. So there is no pool of noise to remove — **except** one thing with an
argument: **3,671 rows have targets under 40 words** against a ~100-word reference distribution.
Those teach the model to stop early, and since the shipped decoder now uses `min_new_tokens 0`
the model is free to act on it. Length calibration feeds the BERTScore term that the 0.89347
submission proved is live.

**Prediction recorded before running: inside the noise floor, and non-monotone.**

## Design — dose-response × paired seeds

A single filtered arm is unreadable: the expected effect (~0.005) is the size of the seed spread
E19 measured (0.8195–0.8258 across ten seeds). So:

- **dose** — filter at 20 / 40 / 60 words (0.8 % / 3.6 % / 6.1 % of rows). A real mechanism
  should be **monotone** in filter strength; noise will not be.
- **paired** — every arm has an unfiltered twin at the *same seed and batch split* among E19's
  ten (english_draft, bs 8×8, 12,000 steps), so each is a matched comparison.
- **factorial** — `len40` = short-filter only, `dedup` = duplicate-removal only, `clean` = both.

## Results — old decoder, matched against the ten unfiltered E19 seeds

| arm | rows dropped | seed | Token F1 | ROUGE-L | peak step |
|---|---|---|---|---|---|
| len20 | 0.8 % | 11 | 0.8205 | — | — |
| len40 | 3.6 % | 11 | 0.8232 | 0.7941 | 7,250 |
| len60 | 6.1 % | 11 | 0.8230 | — | — |
| clean | 5.1 % | 11 | 0.8236 | 0.7951 | 11,250 |
| len40_s23 | 3.6 % | 23 | 0.8224 | — | — |
| **unfiltered baseline (ten E19 seeds)** | — | — | **0.8195 – 0.8258** | | |

## VERDICT: no effect. The last data lever is closed.

**Every filtered arm falls inside the unfiltered seed range, and none exceeds the best
unfiltered seed (0.8258).** The dose curve is not monotone (−0.0012 / −0.0002 / −0.0007 for
0.8 % / 3.6 % / 6.1 %), and `len40` flips sign between seeds (−0.0002 at seed 11, +0.0001 at
seed 23). The pre-registered prediction was correct.

**A measurement error worth recording.** `clean` was first reported at **+0.0019** by
comparing its *in-training* eval against the champion's *decoded* score. Compared like-for-like
(both old-decoder decodes, same seed) it is **+0.0002**. Mixing measurement paths manufactured a
gain four times larger than the real one — the same failure mode as BUG-04.

## Checkpoints

Every arm keeps `best/` and a `submission.csv`. `clean` hash `837ea6aba2eab790`,
`len40` hash `74913520c158c573`. Datasets built by `code/11_build_stage_datasets.py`-style
filters, all TRAIN-only with 0 dev/test id overlap asserted at build time.

## What it changes

- **Data cleaning is not a lever on this task.** The corpus is already clean enough that
  removing its worst 0.8–6 % changes nothing measurable.
- It also **bounds E21**: if removing bad training rows does nothing, adding synthetic ones is
  unlikely to help either, which is consistent with E04's finding that the draft field itself is
  worth ~0.0014 at convergence.
