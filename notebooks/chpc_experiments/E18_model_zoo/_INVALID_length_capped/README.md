# INVALID — these three runs measured a generation cap, not a model

First pass of E18's decoder arms, 2026-08-09. **Do not cite these numbers.**

| arm | Token F1 | mean output |
|---|---|---|
| qwen3_1p7b | 0.4797 | 45.5 words |
| qwen25_1p5b | 0.4795 | 45.8 words |
| qwen3_0p6b | 0.4820 | 45.1 words |

Three models spanning 3x in parameters landed within **0.0025** of each other, all producing
**~45 words against a ~100-word reference**. That uniformity is the tell: it is not capacity.

**Cause.** Generation caps are in SUBWORD tokens and the subword cost of one Bengali answer is
tokenizer-dependent — measured on this corpus, **BanglaT5 needs ~142 tokens per answer, Qwen
needs ~689** (p95 1,149). EXPERIMENT.md's "1024 total" and the `--max-new-tokens 320` carried
over from the BanglaT5 arms therefore capped Qwen output at **~46 metric words**, and `max_len
1024` was shredding the prompt to fit the answer. The score measured the cap.

Nothing crashed; the runs looked healthy for six hours each and wrote plausible numbers — the
same failure shape as the fp16 trap (#20).

**Fix.** `max_len 2560 · min_new 200 · max_new 1280` — the *same experiment* expressed in each
tokenizer's units — plus a length guard in `03_train_causal.py` that now asserts
`max_new_tokens >= p95 target length` and refuses to start otherwise.

Kept only as evidence of the failure mode. The valid arms are one level up.
