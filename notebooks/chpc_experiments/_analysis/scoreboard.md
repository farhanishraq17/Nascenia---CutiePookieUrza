
### Converged arms — early-stopped, or given ≥ 12,000 steps

| Exp | Arm | Model | Input | Token F1 | ROUGE-L | pred LB | vs 0.7724 | budget | peak step | হেলো% | নাসেনিয়া% | tokens | hours | ckpt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E19 | seed1337 | banglat5 | english_draft | **0.8258** | 0.7974 | 0.8799 | beats incumbent +0.0534 | 12000† | 11500 | 75.0 | 52.3 | 100.2 | 6.39 | yes |
| E05 | english_draft | banglat5 | english_draft | **0.8257** | 0.7968 | 0.8798 | beats incumbent +0.0533 | 30000 | 12000 | 75.0 | 53.3 | 100.7 | 3.8 | yes |
| E03 | conv12k | banglat5 | all_inputs | **0.8246** | 0.7964 | 0.8793 | beats incumbent +0.0522 | 12000 | 8750 | 75.0 | 52.7 | 100.4 | 10.28 | yes |
| E19 | seed42 | banglat5 | english_draft | **0.8245** | 0.7949 | 0.8790 | beats incumbent +0.0521 | 12000† | 11000 | 75.0 | 53.7 | 100.2 | 6.39 | yes |
| E07 | conv12k | banglat5 | all_inputs | **0.8245** | 0.7967 | 0.8794 | beats incumbent +0.0521 | 12000† | 11000 | 75.0 | 53.3 | 100.2 | 23.66 | yes |
| E21 | A1 | banglat5 | english_draft_a1 | **0.8242** | 0.7951 | 0.8790 | beats incumbent +0.0518 | 12000† | 10750 | 75.0 | 54.3 | 100.4 | 6.91 | yes |
| E23 | clean | banglat5 | english_draft_clean | **0.8236** | 0.7951 | 0.8788 | beats incumbent +0.0512 | 12000† | 11250 | 75.0 | 52.7 | 100.4 | 6.54 | yes |
| E19 | sched777 | banglat5 | english_draft | **0.8235** | 0.7937 | 0.8785 | beats incumbent +0.0511 | 30000 | 11750 | 75.0 | 54.7 | 100.7 | 7.14 | yes |
| E19 | seed11 | banglat5 | english_draft | **0.8234** | 0.7949 | 0.8787 | beats incumbent +0.0510 | 12000 | 9750 | 75.0 | 53.0 | 100.8 | 5.87 | yes |
| E23 | len40 | banglat5 | english_draft_len40 | **0.8232** | 0.7941 | 0.8784 | beats incumbent +0.0508 | 12000 | 7250 | 75.0 | 53.0 | 100.2 | 5.07 | yes |
| E23 | len60 | banglat5 | english_draft_len60 | **0.8230** | 0.7946 | 0.8785 | beats incumbent +0.0506 | 12000† | 11250 | 75.0 | 53.0 | 100.9 | 6.48 | yes |
| E19 | seed2024 | banglat5 | english_draft | **0.8227** | 0.7953 | 0.8785 | beats incumbent +0.0503 | 12000† | 10750 | 75.0 | 54.0 | 100.2 | 6.47 | yes |
| E22 | B | banglat5 | english_draft_rag | **0.8227** | 0.7940 | 0.8783 | beats incumbent +0.0503 | 12000† | 12000 | 75.0 | 54.3 | 100.7 | 8.01 | yes |
| E23 | len40_s23 | banglat5 | english_draft_len40 | **0.8224** | 0.7939 | 0.8782 | beats incumbent +0.0500 | 12000† | 10750 | 75.0 | 53.3 | 100.6 | 6.54 | yes |
| E19 | seed23 | banglat5 | english_draft | **0.8221** | 0.7924 | 0.8777 | beats incumbent +0.0497 | 12000 | 10500 | 75.0 | 52.0 | 100.5 | 6.24 | yes |
| E04 | conv12k | banglat5 | english_only | **0.8219** | 0.7949 | 0.8782 | beats incumbent +0.0495 | 12000 | 9500 | 75.0 | 55.0 | 100.0 | 6.46 | yes |
| E19 | seed21 | banglat5 | english_draft | **0.8209** | 0.7925 | 0.8774 | beats incumbent +0.0485 | 12000 | 8250 | 75.0 | 52.7 | 100.1 | 5.14 | yes |
| E21 | A2 | banglat5 | english_draft_a2 | **0.8207** | 0.7912 | 0.8771 | beats incumbent +0.0483 | 12000† | 11500 | 75.0 | 53.0 | 100.9 | 0.5 | yes |
| E23 | len20 | banglat5 | english_draft_len20 | **0.8205** | 0.7915 | 0.8771 | beats incumbent +0.0481 | 12000 | 8750 | 75.0 | 53.3 | 100.1 | 5.91 | yes |
| E19 | seed99 | banglat5 | english_draft | **0.8204** | 0.7920 | 0.8772 | beats incumbent +0.0480 | 12000 | 9000 | 75.3 | 53.7 | 100.4 | 5.22 | yes |
| E19 | seed555 | banglat5 | english_draft | **0.8200** | 0.7924 | 0.8771 | beats incumbent +0.0476 | 12000 | 8500 | 75.0 | 52.3 | 100.3 | 5.23 | yes |
| E19 | seed314 | banglat5 | english_draft | **0.8198** | 0.7921 | 0.8770 | beats incumbent +0.0474 | 12000 | 9000 | 75.0 | 53.0 | 100.2 | 5.57 | yes |
| E19 | seed7 | banglat5 | english_draft | **0.8195** | 0.7910 | 0.8767 | beats incumbent +0.0471 | 12000 | 7500 | 75.0 | 55.0 | 100.8 | 4.46 | yes |
| E06 | conv12k-lr3e-3 | banglat5 | english_draft | **0.8189** | 0.7907 | 0.8764 | beats incumbent +0.0465 | 12000† | 11750 | 75.0 | 53.7 | 100.4 | 3.67 | yes |
| E12 | conv12k | banglat5 | english_draft | **0.8106** | 0.7797 | 0.8717 | beats incumbent +0.0382 | 12000† | 11500 | 75.0 | 54.0 | 100.3 | 4.53 | yes |
| E13 | conv12k | banglat5 | multitask_english_draft | **0.8092** | 0.7786 | 0.8710 | beats incumbent +0.0368 | 12000† | 11000 | 75.0 | 54.0 | 99.9 | 2.08 | yes |
| E05 | main | banglat5 | draft_only | **0.8011** | 0.7649 | 0.8658 | beats incumbent +0.0287 | 30000 | 15250 | 75.0 | 54.0 | 99.6 | 2.87 | yes |
| E09 | conv12k | mt5-base | english_draft | **0.8000** | 0.7702 | 0.8665 | beats incumbent +0.0276 | 12000† | 11250 | 75.0 | 49.3 | 93.2 | 10.78 | yes |
| E02 | conv12k | banglat5 | question_draft | **0.7953** | 0.7599 | 0.8630 | beats incumbent +0.0229 | 12000† | 11250 | 75.3 | 53.0 | 99.5 | 7.05 | yes |
| E18 | indicbart | IndicBART | draft_only | **0.4527** | 0.4090 | 0.6867 | below incumbent -0.3197 | 4000 | 2500 | 75.3 | 40.0 | 48.6 | 0.58 | yes |

### Budget-capped probes — ranked separately, NOT against the block above

Each of these ran out of steps at a budget below 12,000 and was still climbing when it stopped. Every score here is a LOWER BOUND: E05/main gained +0.0205 Token F1 between step 4,000 and its peak at 15,250. Do not compare a row here with a row above — re-run the arm at 12,000 first.

| Exp | Arm | Model | Input | Token F1 | ROUGE-L | pred LB | vs 0.7724 | budget | peak step | হেলো% | নাসেনিয়া% | tokens | hours | ckpt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E12 | main | best | english_draft | **0.8060** | 0.7753 | 0.8693 | Δ+0.0336 — lower bound, stopped at the 4000-step cap | 4000† | 4000 | 75.0 | 53.3 | 100.0 | 1.08 | yes |
| E07 | main | banglat5 | all_inputs | **0.8042** | 0.7733 | 0.8684 | Δ+0.0318 — lower bound, stopped at the 4000-step cap | 4000† | 3250 | 76.3 | 53.3 | 100.1 | 1.54 | yes |
| E06 | lr3e-3 | banglat5 | english_draft | **0.8040** | 0.7720 | 0.8681 | Δ+0.0316 — lower bound, stopped at the 4000-step cap | 4000† | 4000 | 75.0 | 53.3 | 100.5 | 1.09 | yes |
| E03 | main | banglat5 | all_inputs | **0.8035** | 0.7727 | 0.8681 | Δ+0.0311 — lower bound, stopped at the 4000-step cap | 4000† | 3750 | 75.3 | 53.0 | 99.8 | 1.35 | yes |
| E01 | main | banglat5 | english_draft | **0.8032** | 0.7719 | 0.8678 | Δ+0.0308 — lower bound, stopped at the 4000-step cap | 4000† | 4000 | 75.3 | 52.3 | 100.3 | 1.08 | yes |
| E06 | lr1e-3 | banglat5 | english_draft | **0.8032** | 0.7719 | 0.8678 | Δ+0.0308 — lower bound, stopped at the 4000-step cap | 4000† | 4000 | 75.3 | 52.3 | 100.3 | 1.09 | yes |
| E04 | main | banglat5 | english_only | **0.7979** | 0.7667 | 0.8651 | Δ+0.0255 — lower bound, stopped at the 4000-step cap | 4000† | 3750 | 76.0 | 53.7 | 100.1 | 0.82 | yes |
| E13 | main | banglat5 | multitask_english_draft | **0.7899** | 0.7571 | 0.8607 | Δ+0.0175 — lower bound, stopped at the 4000-step cap | 4000† | 4000 | 76.0 | 54.3 | 99.9 | 1.02 | yes |
| E09 | main | mt5-base | english_draft | **0.7861** | 0.7517 | 0.8585 | Δ+0.0137 — lower bound, stopped at the 4000-step cap | 4000† | 3750 | 75.3 | 50.7 | 93.0 | 1.96 | yes |
| E06 | lr3e-4 | banglat5 | english_draft | **0.7772** | 0.7432 | 0.8540 | Δ+0.0048 — lower bound, stopped at the 4000-step cap | 4000† | 3750 | 75.7 | 55.3 | 100.0 | 1.09 | yes |
| E18 | banglat5 | banglat5 | draft_only | **0.7768** | 0.7389 | 0.8530 | Δ+0.0044 — lower bound, stopped at the 4000-step cap | 4000† | 3750 | 76.3 | 53.0 | 98.9 | 1.15 | yes |
| E02 | main | banglat5 | question_draft | **0.7734** | 0.7351 | 0.8512 | Δ+0.0010 — lower bound, stopped at the 4000-step cap | 4000† | 3750 | 76.0 | 53.0 | 98.4 | 0.84 | yes |
| E08 | main | mt5-base | draft_only | **0.7563** | 0.7168 | 0.8423 | Δ-0.0161 — lower bound, stopped at the 4000-step cap | 4000† | 3750 | 75.7 | 51.3 | 92.1 | 1.5 | yes |

incumbent Token F1 0.7724 · ROUGE-L 0.7324 · LB 0.85030 · noise floor 0.0044 · convergence budget 12000
† = the run reached its step budget, so early stopping never fired and even this score is a lower bound.
references: হেলো opener 76.4% · নাসেনিয়া 50.0%   |   draft: 0.06% · 0.00%
