# E15_decode_sweep — no `train.ipynb`

This experiment does **no training — sweeps decoder settings against an existing checkpoint.
Record **which** checkpoint in `RESULTS.md`.

Sweep `num_beams {4,8,12}` x `length_penalty {0.6,0.8,1.0,1.2}` x `min_new_tokens {0,40,60,80}`
via `../code/04_decode.py`. Re-verify any winner on a **second disjoint dev subset** — a 3-way
sweep over 300 rows will find spurious winners.
