# E14_arch_ensemble — no `train.ipynb`

This experiment does **no training — combines checkpoints from **E18** (architecture diversity) and
**E19** (seed diversity). Point it at those `best/` directories.

🔴 **Measure row-level disagreement between members FIRST.** If they agree on >90% of rows there
is nothing to pool — MBR already lost once here for exactly that reason.
