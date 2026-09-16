# E15_decode_sweep — results

**No training — averages and decodes existing checkpoints.** Two phases:
the original decoder sweep (2026-08-10, `sweep.json` / `sweep2.json`), and the
**checkpoint-averaging** phase (2026-08-13/14, CHPC granite `grn023`, A800 40 GB, fp32),
which is where the result is. Selection on `dev.iloc[:300]`, verification on the disjoint
`dev.iloc[300:600]`. Noise floor **0.0044** Token F1.

## 🔴 ANSWER: `ckptavg_peak5` is the shipped model. Public LB **0.89552, #1**.

Averaging the champion run's **own** five checkpoints around its peak beats the champion itself,
beats the cross-seed soup, and is the current leaderboard entry.

| model | dev[0:300] | dev[300:600] *(disjoint)* | public LB |
|---|---|---|---|
| 🏆 champion `E05/english_draft/best` | 0.8328 | 0.8348 | 0.89347 |
| `E14/soup_greedy_champ` — champion + E19/sched777 | 0.8345 | 0.8384 | 0.89532 |
| 🏆🏆 **`ckptavg_peak5`** — champion's own ckpts 11500–12500 | **0.8348** | **0.8404** | **0.89552** |
| Δ peak5 − champion | **+0.0021** | **+0.0057** | **+0.00205** |

Same architecture, same 247,577,856 params, same decoder, **zero extra training**. The gain came
from re-using checkpoints that were already on disk.

---

## (a) The checkpoint-averaging table

Every arm is a **uniform** average of checkpoints from the single champion run
(`E05_train_to_convergence/english_draft/ckpt/`), scored by `../code/17_model_soup.py` at
average time on dev[0:300] with the E15 decoder. Read straight from each arm's `soup.json`.

| arm | member steps | n | dev Token F1 | vs champion |
|---|---|---|---|---|
| *(champion, single ckpt 12000)* | 12000 | 1 | 0.8328 | — |
| `ckptavg_tail2` | 11750, 12000 | 2 | 0.8344 | +0.0016 |
| `ckptavg_tail3` | 11500–12000 | 3 | 0.8330 | +0.0003 |
| `ckptavg_tail4` | 11250–12000 | 4 | 0.8340 | +0.0012 |
| `ckptavg_tail5` | 11000–12000 | 5 | 0.8337 | +0.0009 |
| `ckptavg_tail7` | 10500–12000 | 7 | 0.8323 | **−0.0005** |
| `ckptavg_peak3` | 11750, 12000, 12250 | 3 | **0.8349** | **+0.0022** |
| 🏆 **`ckptavg_peak5`** | 11500, 11750, 12000, 12250, 12500 | 5 | **0.8348** | **+0.0021** |
| `ckptavg_peak7` | 11250–12750 | 7 | 0.8341 | +0.0014 |
| `ckptavg_peak9` | 11000–13000 | 9 | 0.8336 | +0.0008 |
| `ckptavg_wide12` | 9500–14000 (12, coarse) | 12 | 0.8333 | +0.0006 |

Full precision for the two that matter: peak3 **0.834931**, peak5 **0.834843** — a gap of
**0.00009**, 2 % of the noise floor. See "anything surprising".

### 🔴 The structural point: peak-CENTRED beats tail-centred

`tail-N` = the last N checkpoints, **ending at** the best one (12000).
`peak-N` = N checkpoints **centred on** the best one.

At matched N the centred window wins every time, and the gap is not small:

| n | tail (ends at peak) | peak (centred on peak) | Δ |
|---|---|---|---|
| 3 | 0.8330 | **0.8349** | **+0.0019** |
| 5 | 0.8337 | **0.8348** | **+0.0011** |
| 7 | 0.8323 | **0.8341** | **+0.0018** |

**This is the opposite of the standard recipe.** The textbook move is "average the last N
checkpoints", and here the last-N family is the *loser* — `tail7` is the only averaging arm that
scores **below** the champion. Averaging pulls the model toward the centre of mass of its members,
so a window anchored at the peak drags it backwards into the still-improving region; a window
centred on the peak has that pull cancel.

The operational consequence is the awkward one: **you cannot build `peak5` unless you train past
the peak.** Its right half (12250, 12500) exists only because early stopping ran patience 8 × 250
= 2000 steps beyond the best checkpoint before halting at 14000. A run that stopped *at* its best
checkpoint can only ever build tail-N — the family that does not work. Keep the post-peak
checkpoints.

## (b) 🔴 The disjoint verification — this is the evidence that matters

dev[0:300] is the split every one of these arms was **selected** on, so its ranking is
contaminated by selection. `../code/14_decode_sweep.py` re-decodes on **dev[300:600]**, which
nothing was selected on. Read from `verify_*.json`.

| model | selection dev[0:300] | **verify dev[300:600]** | Δ verify − selection | margin over champion (verify) |
|---|---|---|---|---|
| champion `english_draft/best` | 0.8328 | 0.8348 | +0.0020 | — |
| `E14/soup_greedy_champ` | 0.8345 | 0.8384 | +0.0039 | +0.0037 |
| `E14/ch_31337` | 0.8348 | 0.8397 | +0.0049 | +0.0050 |
| 🏆 **`ckptavg_peak5`** | **0.8348** | **0.8404** | **+0.0056** | **+0.0057** |

**peak5's margin grows on held-out rows: +0.0021 on the split it was chosen on, +0.0057 on the
split it was not.** That is the shape a real effect has. A selection artefact shrinks or reverses
when the split changes; this one nearly triples. It is also the only number here that clears the
0.0044 noise floor on its own.

Note every model gains ~+0.002 going from A to B — rows [300:600] are simply slightly easier — so
the honest quantity is the *margin* column, not the raw verify score.

## (c) The extended decoder sweep is CLOSED

Re-swept on the champion, `num_beams ∈ {4, 8, 12, 16}` × `length_penalty ∈ {1.0, 1.2, 1.4, 1.6,
1.8, 2.0, 2.4, 2.8, 3.2}` = **36 configs**, `min_new_tokens 0`, `max_new_tokens 320`
(`sweep2_champ_b{4,8,12,16}.json`). 16 of them were re-verified on dev[300:600].

| | beams | lp | dev[0:300] | dev[300:600] |
|---|---|---|---|---|
| **shipped** | 8 | 1.2 | 0.832754 | 0.834751 |
| best on the selection split | 4 | 1.8 | 0.833069 | 0.834030 |
| best on the verify split | 16 | 1.6 | 0.832728 | **0.834990** |

- On the **beams-8 grid**, the verify-based re-rank re-picked the shipped `lp 1.2` exactly:
  the sweep log ends `best swept config: 0.8328 (Δ +0.0000) ➖ inside the 0.0044 noise floor —
  keep the shipped decoder`.
- Across **all 36**, the largest honest gain available is **+0.00024** (b16/lp1.6 on the verify
  split) — **5 % of the noise floor**. The selection split prefers lp 1.8 by +0.00032, and that
  preference does not survive the split change: wherever both were verified (beams 8), lp 1.8
  lands at 0.8340 against lp 1.2's 0.8348.
- Beam width is flat from 4 to 16 (spread **0.0010** across the whole 36-config grid) and
  `length_penalty` is flat from 1.0 to 3.2 (spread **0.0007** at beams 8).

**Verdict: stop sweeping this decoder.** Three sweeps — 48-config beams×lp×min_new on 08-10
(`sweep.json`), 40-config beams×lp×max_new on 08-10 (`sweep2.json`), 36-config beams×lp on 08-13
(`sweep2_champ_b*.json`), **124 configs total** — have all landed on beam 8 / lp 1.2 / min_new 0 /
max_new 320 / max_source_len 768, and the residual headroom is an order of magnitude under the
noise floor.

### `max_new_tokens` — inert **above 320**, not inert below it

From `sweep2.json`, all ten (beams, lp) pairs:

| max_new_tokens | dev Token F1 (b8/lp1.2) | mean pred tokens |
|---|---|---|
| 192 | 0.8243 | 96.3 |
| 256 | 0.8316 | 99.2 |
| **320** | **0.832754** | 99.63 |
| 448 | **0.832754** | 99.63 |

320 and 448 are **bit-identical to 16 significant figures** for every configuration tested, so
nothing is bought by raising the cap. But 256 costs **−0.0011** and 192 costs **−0.0085**, so the
cap is *not* free to lower.

🔴 **Correction to the reason usually given for this.** The claim that "nothing this model emits
exceeds ~100 tokens" is false. 100 is the *mean* — measured max prediction is **226 words on dev**
and **271 on test** (`ckptavg_peak5/{dev_e15dec,test}.json`). The distribution has a real tail;
320 clears it and 256 clips it. The setting is safe because it sits above the tail, not because
the tail does not exist.

## Checkpoints — 🔴 keep every arm, including the losers

| Arm | kept? | Token F1 | ROUGE-L | source steps | notes |
|---|---|---|---|---|---|
| 🏆 `ckptavg_peak5` | ✅ **SHIPPED** | **0.8348** | 0.8061 | 11500–12500 | `submission.csv` + `test.json` written |
| `ckptavg_peak3` | ✅ | 0.8349 | — | 11750–12250 | ⚠️ never verified on dev[300:600] |
| `ckptavg_peak7` | ✅ | 0.8341 | — | 11250–12750 | |
| `ckptavg_peak9` | ✅ | 0.8336 | — | 11000–13000 | |
| `ckptavg_tail2` | ✅ | 0.8344 | — | 11750–12000 | |
| `ckptavg_tail3` | ✅ | 0.8330 | — | 11500–12000 | also feeds `E14/tail3_plus_sched777` |
| `ckptavg_tail4` | ✅ | 0.8340 | — | 11250–12000 | |
| `ckptavg_tail5` | ✅ | 0.8337 | — | 11000–12000 | |
| `ckptavg_tail7` | ✅ | 0.8323 | — | 10500–12000 | 🔴 **the only arm below the champion** — keep it, it is what proves the tail recipe fails |
| `ckptavg_wide12` | ✅ | 0.8333 | — | 9500–14000 | coarse 500-step grid |

Shared by all ten:

| | |
|---|---|
| params | **247,577,856** (0.248B) — within the 3B cap, headroom 2752 M |
| architecture | `T5ForConditionalGeneration`, vocab 32128 (BanglaT5) |
| source run | `E05_train_to_convergence/english_draft` · seed 11 · lr 1e-3 adafactor · eff. batch 64 · 768/512 · max_steps 30000, patience 8 · **peak 12000**, stopped 14000 |
| decoder | beams 8 · length_penalty 1.2 · min_new_tokens 0 · max_new_tokens 320 · max_source_len 768 · greedy (`do_sample=False`) |
| averaging | uniform, fp32, `../code/17_model_soup.py` |
| hardware | granite `grn023`, A800 40 GB, fp32 · ~2–4 min per dev-300 decode, 8.7 min for test-1000 |
| shipped hash | `161f3b7b0ac89309` as recorded in `ckptavg_peak5/test.json` — ⚠️ **not reproducible, see below** |

**Weights-vs-decode gate passed:** the standalone re-decode of `peak5` reproduces the average-time
score to `delta +3.33e-16` (`_slurm/logs_a800/peak5-test.out`) — the model written to disk is the
model that was scored.

## Per-arm read-out

| Arm | split | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | % truncated (src/tgt) | precision | GPU |
|---|---|---|---|---|---|---|---|
| champion (reference point) | dev[0:300] | 99.63 | 75.0 % | 52.33 % | 1.62 % / 0.05 % | fp32 | A800 40 GB |
| 🏆 `ckptavg_peak5` | dev[0:300] | 99.48 | 75.0 % | 52.67 % | 1.62 % / 0.05 % | fp32 | A800 40 GB |
| 🏆 `ckptavg_peak5` | **test (1000)** | 99.9 | **76.2 %** | **50.6 %** | 1.62 % / 0.05 % | fp32 | A800 40 GB |
| `E14/soup_greedy_champ` | dev[0:300] | 99.78 | — | — | 1.62 % / 0.05 % | fp32 | A800 40 GB |
| `E14/ch_31337` | dev[0:300] | 99.36 | — | — | 1.62 % / 0.05 % | fp32 | A800 40 GB |

References: ~100 tokens · `হেলো` **76.4 %** · `নাসেনিয়া` **50.0 %**. Draft: 0.06 % / 0.00 %.

**On the 1000-row test split peak5 lands at 76.2 % / 50.6 % against references at 76.4 % / 50.0 %
— the closest register match this program has recorded.** Weight averaging did not blur the
register; if anything it sharpened it (the champion sits at 52.3 % `নাসেনিয়া` on dev, peak5 at
50.6 % on test). Nowhere near the draft's 0.06 % / 0.00 %, so the model is converting, not copying.

Truncation is **inherited unchanged** from the source run — same data, same 768 cap
(`_slurm/analysis/truncation.md`: english_draft p95 603, max 1851). Averaging cannot change it.

## Trajectory — where the averaging window comes from

The champion's own eval curve (`E05/.../ckpt/checkpoint-14000/trainer_state.json`, eval every 250):

| step | 11000 | 11250 | 11500 | 11750 | **12000** | 12250 | 12500 | 12750 | 13000 | 13500 | 14000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Token F1 | .8233 | .8227 | .8219 | .8232 | **.8268** | .8239 | .8240 | .8252 | .8240 | .8231 | .8235 |
| loss | .3772 | .3798 | .3779 | .3813 | **.3734** | .3705 | .3719 | .3794 | .3790 | .3769 | .3752 |

`best_model_checkpoint = checkpoint-12000`, `best_metric` (composite) `0.87475`. The post-peak
region 12250–14000 is a **plateau — maximum decline 0.0037 (at 13500), inside the 0.0044 noise
floor**. That is exactly why averaging over it works: those checkpoints are not worse models, they
are equally-good models with decorrelated errors, and 12250/12500 are the two the shipped model
needs.

🔴 Note the peak5 window (11500–12500) contains the **lowest eval in the entire 11000–14000
plateau** (11500, .8219) and still wins. Do not select averaging members by their individual scores — `peak3`, which excludes
11500, gains only 0.00009 for doing so.

## Verdict

- **What it must beat:** the best model's own decoder score — the champion at **0.8328**.
- **Result:** ✅ **+0.0021** on the selection split, **+0.0057** on the disjoint split,
  **+0.00205** on the public leaderboard. Clears the 0.0044 noise floor on held-out rows.
- **What it changes:**
  1. 🔴 **The decoder question is closed.** 124 configs across three sweeps; residual headroom
     +0.00024, i.e. 5 % of the noise floor. Any further decoder work on this model is wasted.
  2. 🔴 **The averaging question is open, and it is where the gains are.** Checkpoint averaging
     over one run bought more (+0.0057 verified) than the entire cross-seed soup programme in E14
     (+0.0037), at zero training cost.
  3. **"Average the last N checkpoints" is the wrong recipe on this task** — invert it to
     "average N checkpoints *centred* on the peak", and budget patience so the run continues past
     its peak by at least half the window.
  4. **Never prune post-peak checkpoints.** The shipped model is 40 % composed of checkpoints that
     early stopping classified as failures to improve.
- **Row-level disagreement with the incumbent:** not measured for the averaging arms. A soup is
  one model, not a pool, so `13_disagreement.py` has nothing to compare — the E14 gate does not
  apply here. ⚠️ This means the +0.0057 is **not** decomposable into "which rows got better"
  without a re-decode; that analysis was not run.

## Anything surprising

**1. 🔴 `peak3` scores higher than the model that shipped, and was never verified.**
peak3 = 0.834931 vs peak5 = 0.834843 on dev[0:300] — peak3 wins by **0.00009**, 2 % of the noise
floor. peak5 shipped because it is the arm that was carried through the disjoint verification
(0.8404) and the test decode; peak3 has a `soup.json` and nothing else. The choice was made on
*evidence available*, not on the selection score, and that is the right call — but the file should
not pretend peak5 led the selection split. It did not. Verifying peak3 on dev[300:600] is the one
cheap open item left in this experiment.

**2. 🔴 The recorded checkpoint hashes do not identify the weights.** `04_decode.py:ckpt_hash()`
hashes only **file names and sizes**, not contents:

```python
h.update(f.name.encode()); h.update(str(f.stat().st_size).encode())
```

Two consequences, both reproduced:
- **It collides across genuinely different models.** `E19/seed11/best`, `E19/seed42/best` and
  `E19/seed314/best` all hash to `114136fe6dcde4c8` — every BanglaT5 checkpoint has identical file
  names and sizes. This is the *exact* collision `02_train_t5.py:sha256_dir()` documents having
  already fixed once ("three different sweep arms reported the identical hash `9e3126b85e78323a`")
  — the fix went into the training path only, never into the decode path.
- **It changes as the directory accumulates outputs.** peak5 records `c1b64f64ba94e921` in
  `dev_e15dec.json` and `161f3b7b0ac89309` in `test.json` — same directory, same unmodified
  `model.safetensors`, one job. `rglob` picks up `.json` files, so writing the dev run-record
  changed the hash before the test pass ran. Recomputing today gives `fa466f2dd87c2ff5`, because
  `test.json` and `submission.csv` now exist too.

⚠️ **The shipped model's recorded hash `161f3b7b0ac89309` cannot be recomputed from the directory
as it stands.** For Phase-2 evidence use the content hash from `02_train_t5.py:sha256_dir()`
instead — the champion's is `6f9d4d6756032397` (`E05/.../run.json`). The averaged arms have no
content hash at all; `17_model_soup.py` does not write one.

**3. A800 40 GB OOMs on 3-member soups and on beams ≥ 12, but only when the node is shared.**
`soup-triples`, `peak5-compose` and the first `sw-champ-b12` all died with
`torch.OutOfMemoryError` during `_beam_search` → `reorder_cache`, each time reporting ~33 GB
already held by *another* process on the same 39.49 GiB card. All three succeeded on re-run
(`compose2.out`, `sweep2_champ_b12.json`). The failure is contention, not model size — 0.248B
params in fp32 is ~1 GB. Anyone repeating this should request a whole GPU or set
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.

**4. The dev→LB correspondence held unusually well here.** peak5 beat the champion by +0.0021 on
dev[0:300] and by +0.00205 on the public leaderboard. Given this program's history of dev gains
evaporating on the LB, that is worth recording — though with n = 2 submissions it is a
coincidence until it repeats.
