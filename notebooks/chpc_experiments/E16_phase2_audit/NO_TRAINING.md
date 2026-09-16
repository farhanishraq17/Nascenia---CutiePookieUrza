# E16_phase2_audit — no `train.ipynb`

This experiment does **no training — audits existing checkpoints for clinical quality.

🔴 **20% of the final score, LLM-judged on a different objective than Token F1.** Sample 100 test
outputs per candidate and check repetition loops, contradictions, unsafe advice, truncated
endings, wrong-language fragments. One arm already produced *"gastroenteritis can be caused by
gastroenteritis"* — free on Token F1, near-zero to a judge.
