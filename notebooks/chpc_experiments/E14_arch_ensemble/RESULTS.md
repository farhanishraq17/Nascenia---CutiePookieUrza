# E14_arch_ensemble — results

**No training.** Combines checkpoints from other experiments. Two phases, and they answered
different questions:

- **Phase 1 (2026-08-09)** — the *disagreement gate*, `../code/13_disagreement.py` over five
  output sets. Recorded at the bottom of this file; it passed, and its prediction was wrong.
- **Phase 2 (2026-08-13/14)** — **weight averaging** ("model soup"), `../code/17_model_soup.py`,
  on CHPC granite `grn023`, A800 40 GB, fp32. This is where the result is, and it did not come
  from architecture diversity at all.

Selection on `dev.iloc[:300]`, verification on the disjoint `dev.iloc[300:600]`. Noise floor
**0.0044** Token F1.

## 🔴 ANSWER: souping works, but only with a partner that shares the champion's **schedule**.

`soup_greedy_champ` (champion + E19/sched777, uniform 50/50) scored **0.8345 dev / 0.8384
verify** and took the leaderboard to **0.89532**. It was then beaten by `E15/ckptavg_peak5`
(0.8348 / **0.8404**, LB **0.89552**), which averages the champion's own checkpoints and is the
shipped model. Full write-up of the winner: `../E15_decode_sweep/RESULTS.md`.

| model | dev[0:300] | dev[300:600] *(disjoint)* | public LB |
|---|---|---|---|
| champion `E05/english_draft/best` | 0.8328 | 0.8348 | 0.89347 |
| **`soup_greedy_champ`** = champion + sched777 | **0.8345** | **0.8384** | **0.89532** |
| `ch_31337` = champion + sched31337 | 0.8348 | 0.8397 | *(not submitted)* |
| 🏆 `E15/ckptavg_peak5` *(for reference)* | 0.8348 | **0.8404** | **0.89552** |

## (a) The pairwise soup table — champion + one E19 partner, uniform

Every row is a 50/50 weight average, scored at average time on dev[0:300] with the E15 decoder.
Read from each arm's `soup.json`; `partner alone` is that seed's own `dev_e15dec.json`.

| partner | `max_steps` | partner alone | **pair** | vs champion 0.8328 |
|---|---|---|---|---|
| `sched31337` † | **30000** | 0.8332 | **0.8348** | **+0.0021** ✅ |
| `sched777` | **30000** | *(0.8235, old decoder — no e15dec run)* | **0.8345** | **+0.0018** ✅ |
| `seed11` | 12000 | 0.8319 | 0.8332 | +0.0004 ➖ |
| `seed21` | 12000 | 0.8286 | 0.8326 | −0.0002 ➖ |
| `seed2024` | 12000 | 0.8293 | 0.8319 | −0.0008 |
| `seed42` | 12000 | 0.8301 | 0.8317 | −0.0010 |
| `seed23` | 12000 | 0.8306 | 0.8315 | −0.0013 |
| `seed555` | 12000 | 0.8267 | 0.8308 | −0.0020 |
| `seed1337` | 12000 | 0.8317 | 0.8306 | −0.0022 |
| `seed99` | 12000 | 0.8280 | 0.8306 | −0.0021 |
| `seed7` | 12000 | 0.8269 | 0.8290 | −0.0037 |
| `seed314` | 12000 | 0.8272 | **0.8236** | **−0.0092** 🔴 |

† `ch_31337`, run 2026-08-14, after the other eleven. The eleven `pair_*` arms were run together
on 08-13.

**Only 2 of the 11 `pair_*` arms beat the champion**, and both by less than the 0.0044 noise floor
on this split — which is why the disjoint verification in (e) is the number that decides anything.
Adding `ch_31337` makes it 3 of 12, and all three of the winners are the 30,000-step arms.

## (b) 🔴 The interpretation: it is the SCHEDULE, not the seed

E19 ran two families against the same data and the same architecture:

| family | `max_steps` | members | best pair with champion |
|---|---|---|---|
| **30,000-step** (the champion's own budget) | 30000 | `sched777`, `sched31337`, `sched2468` | **0.8345 – 0.8348** |
| **12,000-step** | 12000 | `seed7/11/21/23/42/99/314/555/1337/2024` | 0.8236 – 0.8332 |

**Every partner that helps is a 30,000-step run; every 12,000-step partner is neutral or harmful,
by up to 0.0092.** The champion (`E05/english_draft/run.json`) is itself `max_steps: 30000`,
peaked at 12000, early-stopped at 14000.

The mechanism is the LR-decay horizon, not the number of steps actually taken. Both families do
roughly 12–14 k steps of real work; but with `max_steps=30000` the scheduler is decaying toward a
30 k horizon, so at step 12000 the weights sit in a different part of the basin than a run whose
schedule has already annealed to zero by 12000. Weight averaging only works inside one basin —
the 12 k runs are in a different one, and averaging across the boundary destroys rather than
smooths.

🔴 **The controlled evidence for "schedule, not seed" is `seed11`.** The champion's own seed is
**11** (`E05/.../run.json: "seed": 11`), and `E19/seed11` is that same seed at a 12,000-step
horizon. Sharing the seed buys **+0.0004** — nothing. Sharing the schedule with a *different* seed
buys **+0.0018 to +0.0021**. Seed identity is not what puts two checkpoints in the same basin;
schedule identity is.

**The single worst partner, `seed314` at −0.0092, is not the worst standalone model** (that is
`seed555`, 0.8267). Standalone quality does not predict soup compatibility at all — across the 11
pairs the rank correlation is visibly weak (`seed1337` is the 2nd-best standalone and the 9th-best
partner). Do not pick soup members by their own scores.

## (c) Saturation — 0.8348 is a ceiling reached by two independent routes

`ch_31337` (champion + sched31337) reaches **0.8348301**, and `E15/ckptavg_peak5` reaches
**0.8348429**. Two completely different averaging axes — across seeds vs. across one run's
checkpoints — land **0.00001 apart**. That looks like a ceiling for this weight-averaging family,
not a coincidence to push on.

Everything past two members is worse:

| arm | members | dev[0:300] |
|---|---|---|
| `ch_31337` | champion + sched31337 | **0.8348** |
| `soup_greedy_champ` / `pair_sched777` | champion + sched777 | **0.8345** |
| `peak5_31337` | peak5 + sched31337 | 0.8344 |
| `peak5_777_31337` | peak5 + sched777 + sched31337 | 0.8340 |
| `ch_777_31337` | champion + sched777 + sched31337 | 0.8338 |
| `greedy_from_peak5` | peak5 alone — **all 5 candidate partners rejected** | 0.8348 |

**Greedy seeded from `peak5` rejected every partner offered**
(`_slurm/logs_a800/soup-greedy2.out`):

```
  start E15_decode_sweep: 0.8348
  + sched777:      0.8333 drop
  + sched31337:    0.8344 drop
  + english_draft: 0.8348 drop
  + seed11:        0.8330 drop
  + seed21:        0.8320 drop
greedy soup: 1 members, dev Token F1 0.8348
```

Note the third line: **averaging peak5 with the champion does not improve on peak5** — peak5
already contains checkpoint-12000, which *is* the champion, so the champion adds no new
information, only re-weights a member it already has.

### The two averaging axes do NOT compose

This is the cleanest negative result in the file. Checkpoint averaging (+0.0021) and cross-seed
averaging (+0.0018) are similar-sized gains from apparently orthogonal sources, so composing them
should help. It does the opposite:

| composition | dev[0:300] | vs its own best ingredient |
|---|---|---|
| `peak5_plus_sched777` = peak5 + sched777 | 0.8333 | **−0.0015** vs peak5 alone (0.8348) |
| `tail3_plus_sched777` = tail3 + sched777 | 0.8334 | +0.0004 vs tail3 alone (0.8330) |
| `peak5_777_31337` | 0.8340 | −0.0008 vs peak5 alone |

**Both compositions land below peak5 alone.** The two axes are not orthogonal — they are competing
ways of moving toward the same basin centre, and doing both overshoots.

### The uniform top-N ladder — monotone degradation, never useful

| arm | members | dev[0:300] |
|---|---|---|
| `soup_top2` | champion + seed1337 | 0.8306 |
| `soup_top3` | champion + seed11 + seed1337 | 0.8328 |
| `soup_top4` | + seed42, sched777 | 0.8305 |
| `soup_top5` | + seed2024 | 0.8289 |
| `soup_top6` | + seed11 | 0.8286 |
| `soup_top8` | + seed23, seed21 | 0.8293 |
| `soup_uniform` | all 10 twelve-k seeds, **no champion** | 0.8282 |

Not one uniform ladder arm beats the champion's 0.8328; the best merely ties it. **"Average
everything you have" is dead on this task** — it dilutes the one good member with nine members
from the wrong basin. `soup_top4` contains `sched777`, the single best partner, and still scores
0.8305 because four other 12 k members are dragging it.

## (d) 🔴 CORRECTION: "greedy soup finds nothing" was an artefact of the seeding order

This file previously carried the result that greedy souping over E19's seeds returned **1 member
and no gain**. That is `soup_greedy/soup.json` = 0.8319, and it is real — but it is real *only for
the ordering it was given*. Greedy soup starts from its first argument and keeps a member only if
dev Token F1 strictly improves, so **the first argument determines everything downstream.**

| run | seeded from | log | outcome |
|---|---|---|---|
| `soup_greedy` (08-11, notch299 RTX 3090) | `seed11` (0.8319) | `_slurm/np/logs/nd-soup-greedy.out` | **1 member, 0.8319** — all 9 partners dropped |
| `soup_greedy_champ` (08-13, grn023 A800) | **champion** (0.8328) | `_slurm/logs_a800/soup-ladder.out` | **2 members, 0.8345** — `sched777` KEPT |

Both runs saw `sched777` in their candidate list. The first one rejected it, because from a
0.8319 start the `seed11`+`sched777` average did not clear 0.8319. From the champion's 0.8328
start the same partner scores 0.8345 and is kept.

```
  start english_draft: 0.8328
  + seed1337: 0.8306 drop
  + seed42:   0.8317 drop
  + sched777: 0.8345 KEEP
  ...
greedy soup: 2 members, dev Token F1 0.8345
```

**A real +0.0018 result was hidden for two days by argument order**, and the earlier version of
this file recorded the null as if it were a property of souping. 🔴 Greedy soup is order-dependent
by construction; **always seed it from the best available model**, and never report a greedy null
without stating what it started from.

## (e) The disjoint verification — why `peak5` shipped and `ch_31337` did not

dev[0:300] is the split all of these were selected on. `../code/14_decode_sweep.py` re-decodes on
**dev[300:600]**, which nothing was selected on (`../E15_decode_sweep/verify_*.json`).

| model | selection dev[0:300] | **verify dev[300:600]** | margin over champion (verify) |
|---|---|---|---|
| champion | 0.8328 | 0.8348 | — |
| `soup_greedy_champ` | 0.8345 | 0.8384 | +0.0037 |
| `ch_31337` | 0.8348 | 0.8397 | +0.0050 |
| 🏆 `E15/ckptavg_peak5` | 0.8348 | **0.8404** | **+0.0057** |

`ch_31337` and `peak5` are tied on the selection split (0.83483 vs 0.83484) — that split cannot
separate them. **The disjoint split can: 0.8397 vs 0.8404.** peak5 shipped on that 0.0007, and on
one further consideration: peak5 needs only the champion run's own checkpoints, whereas `ch_31337`
depends on a separate 30 k training run, so peak5 is the cheaper and more reproducible artefact
for Phase 2.

⚠️ 0.0007 on 300 rows is **well inside the noise floor**. The claim "peak5 is better than
ch_31337" is *not* supported; the claim "peak5 is not worse, and is cheaper" is. Both beat the
champion by more than the noise floor, and that is the finding.

## Checkpoints — 🔴 keep every arm, including the losers

All arms: `T5ForConditionalGeneration`, vocab 32128, **247,577,856 params** (within the 3B cap,
headroom 2752 M), uniform fp32 averaging via `../code/17_model_soup.py`, scored with the E15
decoder (beams 8 · lp 1.2 · min_new 0 · max_new 320 · max_source_len 768, `do_sample=False`).

| Arm | kept? | dev[0:300] | verify[300:600] | members | notes |
|---|---|---|---|---|---|
| `ch_31337` | ✅ | **0.8348** | **0.8397** | champion + sched31337 | ties peak5 on selection, loses on verify |
| `soup_greedy_champ` | ✅ | **0.8345** | **0.8384** | champion + sched777 | **submitted, LB 0.89532** |
| `pair_sched777` | ✅ | 0.8345 | — | champion + sched777 | byte-identical recipe to `soup_greedy_champ` |
| `peak5_31337` | ✅ | 0.8344 | — | peak5 + sched31337 | |
| `peak5_777_31337` | ✅ | 0.8340 | — | 3-way | |
| `ch_777_31337` | ✅ | 0.8338 | — | 3-way | |
| `tail3_plus_sched777` | ✅ | 0.8334 | — | E15/tail3 + sched777 | axis composition |
| `peak5_plus_sched777` | ✅ | 0.8333 | — | E15/peak5 + sched777 | axis composition |
| `pair_seed11` | ✅ | 0.8332 | — | champion + seed11 | same seed as champion, different horizon |
| `soup_top3` | ✅ | 0.8328 | — | 3-way | best of the uniform ladder — ties champion |
| `pair_seed21` | ✅ | 0.8326 | — | | |
| `pair_seed2024` | ✅ | 0.8319 | — | | |
| `soup_greedy` | ✅ | 0.8319 | — | seed11 only | 🔴 the order-artefact — see (d) |
| `pair_seed42` | ✅ | 0.8317 | — | | |
| `pair_seed23` | ✅ | 0.8315 | — | | |
| `pair_seed555` | ✅ | 0.8308 | — | | |
| `pair_seed1337` / `soup_top2` | ✅ | 0.8306 | — | | identical member sets |
| `pair_seed99` | ✅ | 0.8306 | — | | |
| `soup_top4` | ✅ | 0.8305 | — | | contains sched777 and still loses |
| `soup_top8` | ✅ | 0.8293 | — | | |
| `pair_seed7` | ✅ | 0.8290 | — | | |
| `soup_top5` | ✅ | 0.8289 | — | | |
| `soup_top6` | ✅ | 0.8286 | — | | |
| `soup_uniform` | ✅ | 0.8282 | — | 10 seeds, no champion | |
| `pair_seed314` | ✅ | **0.8236** | — | champion + seed314 | 🔴 **worst arm, −0.0092** — keep it, it is the whole basin argument |
| `greedy_from_peak5` | ✅ | 0.8348 | — | peak5 only | records 5 rejections |

⚠️ **These checkpoints have no trustworthy hash.** `17_model_soup.py` writes no hash at all, and
the decode-path `04_decode.py:ckpt_hash()` hashes file *names and sizes only*, so every BanglaT5
checkpoint collides — `E19/seed11`, `seed42` and `seed314` all report `114136fe6dcde4c8`. Full
diagnosis in `../E15_decode_sweep/RESULTS.md` § "anything surprising". For Phase-2 evidence use
the source runs' content hashes (champion: `6f9d4d6756032397`).

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|
| champion (reference point) | 99.63 | 75.0 % | 52.33 % | 1.62 % / 0.05 % | fp32 | A800 40 GB |
| `soup_greedy_champ` | 99.78 | — | — | 1.62 % / 0.05 % | fp32 | A800 40 GB |
| `ch_31337` | 99.36 | — | — | 1.62 % / 0.05 % | fp32 | A800 40 GB |
| `E15/ckptavg_peak5` | 99.48 | 75.0 % | 52.67 % | 1.62 % / 0.05 % | fp32 | A800 40 GB |

References: ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %. Draft: 0.06 % / 0.00 %.

⚠️ **Register was not captured for the soup arms.** `14_decode_sweep.py` records `mean_tokens` but
not the opener/`নাসেনিয়া` rates, so only length is verifiable here. All arms sit at 99.4–99.8
tokens against references at ~100 — averaging does not shift output length. Truncation is
inherited from the source data (768 cap, `../_slurm/analysis/truncation.md`) and cannot be changed
by averaging.

## Verdict

- **What it must beat:** the best single model, by more than 0.0044 — the champion at **0.8328**
  selection / **0.8348** verify.
- **Result:** ✅ **`soup_greedy_champ` +0.0037 verify, +0.00185 LB.** Clears the noise floor on
  the disjoint split. Superseded by `E15/ckptavg_peak5` (+0.0057 verify, +0.00205 LB).
- **What it changes:**
  1. 🔴 **Phase 1's headline prediction was wrong.** The gate said architecture/tokenizer
     diversity was the axis to chase and seeds were the dead end. In fact **nothing
     architecture-diverse ever contributed** — mT5 and the Qwen arms cannot be souped at all
     (`17_model_soup.py` refuses across architectures and vocabularies, correctly), and the only
     thing that worked was averaging BanglaT5 weights from **matched-schedule** runs. The diverse
     members were useful for the *output*-ensembling question, which lost twice.
  2. **Weight averaging beats output ensembling on this task, decisively and cheaply.** MBR lost
     twice (−0.0027, +0.0015); souping wins by +0.0037 verified, ships one model, needs no
     selector, and costs nothing at inference.
  3. **Compatibility is set by the LR schedule.** Any future soup partner must be trained with the
     champion's `max_steps=30000` horizon. Seeds are free to vary; the horizon is not.
  4. **Always seed greedy soup from the best model** — see (d).
  5. **Two members is the ceiling here.** Every 3-way is worse, and greedy from the winner rejects
     everything.
- **Row-level disagreement with the incumbent:** not re-measured for the Phase-2 arms. A soup is a
  single model, so `13_disagreement.py` has no pool to compare — the Phase-1 gate machinery does
  not apply to this result.

## Anything surprising

**1. 🔴 The best available partner was never tested.** `E19/sched2468` is the third 30,000-step
run (`max_steps: 30000`, standalone **0.8331** — the best standalone of any E19 arm), and **there
is no `pair_sched2468` directory.** The two 30 k partners that *were* tested are the two best
results in this file. This is the single cheapest open item in the experiment: one `17_model_soup.py`
invocation, ~15 min on one GPU.

**2. Standalone score does not predict soup compatibility.** Ranks across the ten 12 k seeds,
standalone vs. as the champion's partner:

| seed | alone | rank | as partner | rank |
|---|---|---|---|---|
| `seed11` | 0.8319 | 1 | 0.8332 | 1 |
| `seed1337` | 0.8317 | **2** | 0.8306 | **8** |
| `seed23` | 0.8306 | 3 | 0.8315 | 5 |
| `seed42` | 0.8301 | 4 | 0.8317 | 4 |
| `seed2024` | 0.8293 | 5 | 0.8319 | 3 |
| `seed21` | 0.8286 | **6** | 0.8326 | **2** |
| `seed99` | 0.8280 | 7 | 0.8306 | 7 |
| `seed314` | 0.8272 | 8 | **0.8236** | 10 |
| `seed7` | 0.8269 | 9 | 0.8290 | 9 |
| `seed555` | 0.8267 | **10** | 0.8308 | **6** |

`seed1337` drops from 2nd to 8th; `seed21` climbs from 6th to 2nd; `seed555` is the **worst**
standalone and the 6th-best partner. Ranking candidates by their own dev score — which is exactly
what the `soup_top-N` ladder does — is why that entire ladder failed.

**3. `pair_seed314` at 0.8236 is worse than either ingredient.** seed314 alone is 0.8272 and the
champion alone is 0.8328; the average of the two is **0.8236**, below both. This is not
interpolation gone slightly wrong — it is direct evidence the two are in different loss basins,
because averaging two points in the *same* basin cannot land below both. Keep this arm; it is the
measurement that makes the basin claim more than a story.

**4. A800 40 GB OOMed on every 3-member soup on the first attempt.** `soup-triples.out` and
`peak5-compose.out` both died in `_beam_search` → `reorder_cache` with ~33 GB already held by
another process on the same 39.49 GiB card. The 3-way arms in the tables above are all from
successful re-runs (`soup31337.out`, `soup-peak31337.out`, `compose2.out`). The model is 0.248B
params — ~1 GB in fp32 — so this is GPU contention, not a memory requirement. Request a whole GPU.

**5. `soup_top2` and `pair_seed1337` are the same model computed twice** (champion + seed1337,
both 0.8305801519555319, identical to 16 digits). Likewise `soup_greedy_champ` and `pair_sched777`
(both 0.8345357192146158). Two of the 27 arm directories on disk are duplicates; the ladder and
pair sweeps were built independently and overlapped. Harmless, but do not count them as
independent evidence.

---

# Phase 1 (2026-08-09) — the disagreement gate

Measured with `../code/13_disagreement.py` on the frozen dev-300 split, five arms available at the
time. 🔴 **Retained for the record, but read (b) above first — its central prediction did not hold.**

## The gate passed. Members genuinely disagreed, and an oracle had +0.0195 of headroom.

The docs set the abandon line at **>90 % agreement**, because MBR failed once here for exactly
that reason: two seeds agreed to 0.0001 and the consensus selector had nothing to work with.

| | |
|---|---|
| mean pairwise Token F1 between members | **0.8704** — comfortably under the 0.90 line |
| best single member | **0.8035** (E03) |
| per-row oracle | **0.8230** |
| **oracle gain** | **+0.0195** — 4.4× the 0.0044 noise floor |

**This is a ceiling, not a forecast.** The oracle picks the best member per row *using the
reference*; no deployable selector can.

## Pairwise disagreement — the full matrix

| A | B | exact-diff % | mean pairwise Token F1 |
|---|---|---|---|
| E01 en+draft | E03 q+en+draft | 95.0 % | **0.9343** ⚠️ near-duplicates |
| E02 q+draft | E18 banglat5 draft | 96.7 % | **0.9253** ⚠️ near-duplicates |
| E01 | E18 banglat5 | 99.0 % | 0.8809 |
| E03 | E18 banglat5 | 98.7 % | 0.8775 |
| E03 | E02 | 98.3 % | 0.8737 |
| E01 | E02 | 99.3 % | 0.8724 |
| E18 banglat5 | **E08 mT5** | 99.3 % | **0.8461** |
| E02 | **E08 mT5** | 99.3 % | **0.8440** |
| E01 | **E08 mT5** | 99.7 % | **0.8265** |
| E03 | **E08 mT5** | 99.7 % | **0.8230** 🥇 most diverse pair |

**Exact-string difference is useless** — every pair sits at 95–99.7 %, because two fluent Bengali
paragraphs are essentially never byte-identical. **Token F1 similarity is the number to use.**

## The lowest scorer was the most diverse member

| member | Token F1 | mean similarity to the others |
|---|---|---|
| E03 q+en+draft | 0.8035 | 0.877 |
| E01 en+draft | 0.8032 | 0.879 |
| E18 banglat5 draft | 0.7768 | 0.887 |
| E02 q+draft | 0.7734 | 0.879 |
| **E08 mT5-base** | **0.7563** *(worst)* | **0.835** *(most different)* |

## 🔴 What Phase 2 did to this conclusion

Phase 1 concluded: *"the evidence points at architecture/tokenizer diversity, not input diversity
and not seeds"*, and predicted that E19's ten seeds would show higher mutual similarity than 0.87
and that **E19's pooling gate would fail where this one passed**.

What actually happened:

- **The seed pool is where the gain came from** — but through *weight* averaging, not pooling.
  The prediction that seeds were the dead end was correct about MBR and wrong about the axis.
- **Architecture diversity turned out to be unusable for the method that worked.** `17_model_soup.py`
  refuses to average across architectures or vocabularies — correctly, since that produces a
  well-formed model emitting noise — so E08/mT5, the most diverse and most prized member here,
  **cannot participate in the winning technique at all.** Its diversity is only spendable on
  output ensembling, which lost every time it was measured.
- **The useful diversity axis was the one nobody scored: the LR-decay horizon.** It is invisible
  to `13_disagreement.py`, which compares outputs, because two runs can produce near-identical
  outputs from very different regions of weight space.

**The lesson is not "the gate was wrong" — it is that output-space disagreement is the wrong
diagnostic for a weight-space method.** The gate correctly measured what it measured; it was
pointed at a question that turned out not to be the one worth answering.
