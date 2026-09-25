# RESULTS — fill in as runs land

```
LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L        noise floor: 0.0044 Token F1
```

**Ignore any difference below 0.0044.** Judge on Token F1 / ROUGE-L, never the local composite.

---

## Where this ran

**CHPC granite `grn008` — 8 × H100 NVL, one GPU per arm, bf16.** ~20× a Kaggle T4: the 0.85030
recipe takes 69 min here instead of 472. Runner + every code change:
[`_slurm/README.md`](../../scripts/chpc_slurm/README.md). Live scoreboard: `python _slurm/collect.py`.

## Scoreboard — updated 2026-08-09

Numbers are dev-300, beam-4, the frozen seed-42 split. *(in flight)* = best eval so far, run
still going.

| Exp | Model | Input | Token F1 | ROUGE-L | pred LB | vs 0.7724 | peak step | hours | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| *incumbent* | BanglaT5 | draft | **0.7724** | **0.7324** | 0.8454 | — | 2,750 | 7.9 | **LB 0.85030 actual** |
| ~~E17~~ | *(4 translators)* | re-translated draft | — | — | — | — | — | done | **CLOSED — keep Google draft** |
| **E01** | BanglaT5 | **en + draft**, 768/512 | **0.8032** | **0.7719** | **0.8678** | **+0.0308** | **4,000 = last** | 1.1 | **English helps: +0.0220 vs matched E05** |
| **E02** | BanglaT5 | q + draft, 640/512 | 0.7734 | 0.7351 | 0.8512 | +0.0010 | 3,750 | 0.8 | **the question adds nothing** |
| E03 | BanglaT5 | q + en + draft, 1024/512 | **0.8035** | 0.7727 | 0.8681 | +0.0311 | 3,750 | 1.35 | +0.0003 over E01 → **ship the shorter input** |
| **E04** | BanglaT5 | **en only, 640/512** | **0.7979** | 0.7667 | 0.8651 | +0.0255 | 3,750 | **0.82** | **English alone > draft alone (+0.0172). Draft worth only +0.0053** |
| **E05** | BanglaT5 | draft, 768/512, 30k | **0.8011** | **0.7645** | **0.8658** | **+0.0287** | **15,250** | 2.87 | **convergence is 5.5× the incumbent's budget** |
| **E05b** | BanglaT5 | **en + draft, 30k** | *(queued)* | | | | | | **both confirmed gains combined** |
| E06a | BanglaT5 | en+draft @ **lr 3e-4** | 0.7772 | 0.7432 | 0.8540 | +0.0048 | 3,750 | 1.09 | −0.026 vs 1e-3 |
| E06b | BanglaT5 | en+draft @ **lr 1e-3** | **0.8032** | 0.7719 | 0.8678 | +0.0308 | 4,000 | 1.09 | **1e-3 transfers; bit-identical to E01 — see below** |
| E06c | BanglaT5 | en+draft @ **lr 3e-3** | *(in flight)* | | | | | | |
| E07 | BanglaT5 | all, 1280/768 | **0.8042** | 0.7733 | 0.8684 | +0.0318 | 3,250 | 1.54 | **+0.0007 over E03 — truncation CLOSED** |
| **E08** | mT5-base | draft, 640/640 | **0.7563** | 0.7168 | 0.8423 | −0.0161 | 3,750 | 1.5 | **below BanglaT5 — drop E09/E10** |
| E09 | mT5-base | en + draft | *(queued)* | | | | | | |
| E12 | BanglaT5 | warm-start → en+draft | *(queued)* | | | | | | two-stage |
| E13 | BanglaT5 | multi-task (transfer + Q→A) | *(queued)* | | | | | | |
| E14 | ensemble | — | | | | | | | needs E18/E19 |
| E15 | *best* | decoder sweep | | | | | | | needs a final ckpt |
| **E18a** | **Qwen3-1.7B** | draft — decoder | *(in flight)* | | | | | | |
| **E18b** | **Gemma-2-2B-IT** | draft — decoder | — | — | — | — | — | — | **HF 401 — gated, licence not accepted** |
| E18c | Qwen2.5-1.5B-Instruct | draft — decoder | *(in flight)* | | | | | | |
| E18d | Qwen3-0.6B | draft — decoder | *(in flight)* | | | | | | |
| E18e | Llama-3.2-1B-Instruct | draft — decoder | — | — | — | — | — | — | **HF 401 — gated, licence not accepted** |
| E18f | ai4bharat/IndicBART | draft — enc-dec | 0.4400 *(in flight)* | | | −0.33 | | | not competitive; kept for E14 |
| **E18g** | **BanglaT5, 384/256** | draft — *the zoo's control* | **0.7768** | 0.7389 | 0.8531 | +0.0044 | 3,750 | 1.2 | **replicates the incumbent to 0.0001 @2,750** |
| E19 | BanglaT5 ×10 seeds | *winner* — ensemble | | | | | | | budget waits on E05 |
| **E20a** | *Qwen3-235B teacher* | few-shot ceiling probe | | | | | — | ~2 h | gates E20b at >0.82 · **infra-gated, see below** |
| E20b | BanglaT5 | seq-KD from teacher | | | | | | | |
| **E21a** | BanglaT5 | real + back-translated drafts | | | | | | | |
| E21b | BanglaT5 | + pseudo-labelled unpaired | | | | | | | |
| E22a | *teacher* | k-NN in-context examples | | | | | — | | vs E20a random |
| E22b | BanglaT5 | + retrieved style exemplar | | | | | | | |
| E22c | *(Phase 2)* | RAG grounding | — | — | — | — | — | | judged by E16, not F1 |
| **E25** | **Bangla-AI-1.7B + RAG** | retrieved reference case + new question | *(queued)* | | n/a — Phase 2, not the LB | must beat **0.1454** (PHASE2-GEN-01 floor) | | | **moved to `../PHASE_2_EXP/E25_phase2_specialist/` — the model that actually answers, for Phase 2's private judging set** |

### Two results that change the plan

**1. Nothing has converged.** Four arms peaked at or within one eval of their **last** step, and
E05 is still climbing at 8,250. The "budget ~2,000 steps and stop" rule was a property of the
question→answer task and **does not transfer**. Every 4,000-step number in this table is a lower
bound.

**2. The Tier-1 winner is `english_draft`** — and the field ranking is now complete. Every
combination, at matched budget:

| input | Token F1 | what it says |
|---|---|---|
| all inputs, un-truncated *(E07)* | 0.8042 | truncation buys +0.0007 — **closed** |
| all inputs *(E03)* | 0.8035 | the question buys +0.0003 on top of E01 — **nothing** |
| **english + draft *(E01)*** | **0.8032** | **the winner** |
| **english only *(E04)*** | **0.7979** | the draft is worth only **+0.0053** |
| draft only *(E05 @4,000)* | 0.7807 | **English alone beats the draft alone by +0.0172** |
| question + draft *(E02)* | 0.7734 | the question is worth ~0 |

**3. The Bengali draft is the weak input, not the strong one.** English alone (0.7979) beats
our own translation of it (0.7807) by 4× the noise floor, and adding the draft to English recovers
only 0.0053. The pipeline's middle hop is a *lossy re-encoding*. This re-costs every
draft-quality question in the program — E17 closed by keeping Google, and E21's draft-robustness
arms are insurance on a component worth 0.0053.

### Blocked, not dropped

| | Why | To unblock |
|---|---|---|
| **E18b Gemma-2-2B-IT**, **E18e Llama-3.2-1B** | HF **401** — gated repos, licence not accepted by this account's token. Gemma-2-2B is the specific model LIT-01's *decoder beats enc-dec* finding rests on | accept both licences on huggingface.co, then `submit.py --arm … --force-blocked` |
| **E20a teacher** | `Qwen3-235B-A22B` is a ~440 GB download and needs all 8 GPUs at once. Probe script is written (`code/12_teacher_probe.py`, in-context examples asserted train-only) | decide: stage it via Qwen3-32B on one GPU first, or commit the node to the 235B |

Also record per run: **mean output tokens** (references ~100) · **`হেলো` opener %** (refs 76.4%) ·
**`নাসেনিয়া` %** (refs 50.0%) · **% truncated** (source and target) · precision actually used · GPU.

**And record where the checkpoint is.** Add a `ckpt` column as runs land — `best/` path on the
GPU box, and the Kaggle dataset slug once uploaded. A row with a score and no checkpoint is a
result that **cannot be submitted without retraining**, and that must be visible at a glance:

| Exp | Token F1 | ckpt (GPU box) | ckpt (Kaggle) |
|---|---|---|---|
| *incumbent* | 0.7724 | `_run_outputs/xfer/tashin/.../best` | `didhitinahid/nascenia-xfer-ckpt` |
| E05 | | | |

---

## The comparisons that actually answer the questions

A single score means little; these **pairs** each hold one variable fixed.

### Is the draft itself good enough? (E17 — run before anything else)

| | Token F1 vs target | verdict |
|---|---|---|
| **Claude Opus 5** (n=24) | **+0.0631** | wins — but no API here, not deployable |
| Codex GPT-5 (n=10) | +0.0253 | marginal, t=1.34 |
| *Google Translate — the draft we ship* | *baseline* | **kept** |
| NLLB-200 1.3B (n=200) | −0.0439 | dedicated MT loses |
| **Qwen3-14B** (n=200) | **−0.1255** | open-weights LLM loses hardest (t −20.4) |

**CLOSED 2026-08-07.** Only frontier LLMs beat Google, and none of them are deployable at
107,737 rows. **The Google draft stays, and E05 (train longer) is where the remaining gain is.**
Qwen3-14B's output was verified fluent and correctly-sized — it lost on *synonym choice*, which is
the sharpest evidence yet that the metric rewards lexical coincidence with one translator rather
than translation quality.

### Does the English source add information? — YES, +0.0220

| pair | isolates | result |
|---|---|---|
| **E01 − E05 @ matched 768/512 and 4,000 steps** | English alone | **0.8027 − 0.7807 = +0.0220** 5× the noise floor |
| ~~E01 − incumbent~~ | *confounded* | +0.0308, but the incumbent also differs in sequence caps — **use the E05 pair** |
| **E09 − E08** | English, on mT5 | *(E09 queued)* |

The matched control matters here: E01 changes the input **and** raises the caps from 384/256 to
768/512. E05 at the same caps isolates the input, and English survives it at +0.0220.
E09 − E08 will say whether that is architecture-independent or a BanglaT5-tokenizer interaction.

### Does the patient question add information? — NO

| pair | isolates | result |
|---|---|---|
| **E02 − incumbent** | the question | **+0.0010 — inside the 0.0044 noise floor** |
| **E03 − max(E01, E02)** | are the signals complementary? | **0.8035 − 0.8032 = +0.0003 — no.** One field dominates ⇒ **ship the shorter input** |

The 0.85030 model's one acknowledged blind spot — never reading the patient's question — **was
not costing anything.** Note this does not make the question useless in general: it is the only
field the organizers guarantee at test time, which is E13's rationale.

### Is BanglaT5 the right carrier? — YES so far

| pair | isolates | result |
|---|---|---|
| **E08 − incumbent** | the model, identical input | **0.7563 − 0.7724 = −0.0161** mT5 loses |
| **E18f IndicBART − E18g BanglaT5** | the model, identical input *and* identical caps | **0.4400 − 0.7768 = −0.337** not competitive |
| **E18g − incumbent** | *the pipeline itself* | **+0.0001 @ step 2,750** replication |

mT5 needs **272 target tokens where BanglaT5 needs 145**. It starts behind and must win that back
before its multilingual pretraining pays. **If E08 ≪ 0.7724, skip E09–E10.**

### Had the incumbent converged? — NO. Convergence is step 15,250.

| | result |
|---|---|
| **E05 peak step** *(incumbent peaked at 2,750)* | **15,250 — 5.5× the incumbent's budget** |
| **E05 Token F1 − 0.7724** | **+0.0287** (0.8011 / 0.7645), from compute alone |

Trajectory: .7658 @2k · .7807 @4k · .7866 @6k · .7902 @8k · .7950 @11k · .7968 @12k ·
**.8011 @15,250** · early-stopped at 17,250 on patience 8. **Two thirds of the gain arrived after
the incumbent's budget ended.** It flattens from ~12k but never turns over, and loss flattens with
it — the loss/metric divergence seen on question→answer does not occur here.

**Every 4,000-step number in this program is therefore a lower bound**, including the entire
Tier-1 table.

**And compute on the weak input nearly equals information on the strong one:** E05 (draft only,
15,250 steps) 0.8011 vs E01 (english + draft, 4,000 steps) 0.8032 — a 0.0021 gap, inside noise.
`E05/english_draft` combines both and is in flight.

### Was lr 1e-3 still right? — YES (3e-3 arm still running)

| | Token F1 | |
|---|---|---|
| E06a lr 3e-4 | 0.7772 | −0.0260 |
| **E06b lr 1e-3** | **0.8032** | 1st |
| E06c lr 3e-3 | *(in flight)* | |

The LR measured on question→answer **transfers to register transfer**. No Tier-1 result needs
re-running.

**A free — and subtle — Phase-2 result fell out of this.** E06b is by construction the same
configuration as E01 (same data, seed, LR, caps, budget), run as a separate SLURM job on a
separate H100. Comparing the two:

| | |
|---|---|
| dev Token F1 | **0.803238 vs 0.803238** — equal to 6 dp |
| decoded predictions | **300 / 300 identical strings** |
| `checkpoint_hash` | `b0c37448ebc6f1c9` vs `c483d6b544bb0d50` — **DIFFERENT** |

**The outputs reproduce exactly; the weights do not.** Run-to-run nondeterminism in GPU reductions
perturbs the weights in low-order bits, and beam-4 decoding is insensitive to it.

**Consequence for Phase 2, and it cuts against the obvious approach: do not use
`checkpoint_hash` to prove a run was reproduced.** Trap #16 already retired the old hash for
hashing names rather than contents; the *fixed* content-hash still will not match across two
identical runs. **Reproduction evidence must be the decoded outputs** — which do match exactly —
i.e. the `run.json` config block plus `submission.csv`, never a weight hash.

E06b is therefore not an independent datapoint and must not be counted as one.

---

## Decision table

| Pattern | Conclusion | Do next |
|---|---|---|
| E05 peaks ≫ 2,750 | Free score was being left on the table | Re-run every Tier-1 winner at the longer budget |
| E01 > 0.7724 and E02 > 0.7724 | Both signals help | E03; ship its winner |
| E03 ≈ max(E01, E02) | One field dominates | Ship the **shorter** input — faster, same score |
| E04 ≈ E01 | The draft is redundant given English | Ship english-only; halves input length |
| E08 ≪ 0.7724 | mT5 cannot carry Bengali output | **Drop E09**; the tokenizer verdict is in |
| E06 winner ≠ 1e-3 | The LR did not transfer across tasks | Re-run Tier 1 at the new LR |
| E14/E19 members agree >90% of rows | Nothing to ensemble | Skip — MBR already lost once here |
| E20 stage-1 teacher < 0.7724 | Scale ≠ fingerprint matching | **Stop; skip stage 2.** A real negative — closes the teacher line |
| E18 loses but disagrees a lot | Architecture is not better, but IS different | Keep it purely as an E14 ensemble member |
| E16 finds repetition in the winner | Phase-1 gain may cost Phase-2 score | Escalate — 20% of final beats a 0.005 Phase-1 gap |

---

## Before trusting any number

1. **Frozen split intact?** `--seed 42 --dev-size 5000`. If that changed, nothing is comparable.
2. **`transformers==4.57.3`?**
3. **Precision bf16 or fp32 — never fp16?** fp16 T5 goes NaN silently.
4. **No truncation?** Report the measured %. A weak score from a truncated input measures the
   truncation, not the hypothesis.
5. **Best checkpoint, selected on composite — not the last, not on loss?**
6. **Difference > 0.0044?** Below that it is noise.

---

## Notes per experiment

### E17 — Re-translation probe
_(one row per translator: model+version, prompt, Token F1, ROUGE-L, n rows, cost)_

### E01 — BanglaT5 + English + draft
_(trajectory, wall-clock, anything surprising)_

### E02 — BanglaT5 + question + draft

### E03 — BanglaT5 + all inputs

### E04 — BanglaT5 + English only

### E05 — Train to convergence
_(the full eval trajectory matters more than the final number)_

### E06 — LR re-tune

### E07 — No truncation
_(report % truncated in E03 vs here)_

### E08 — mT5-base control

### E09 — mT5-base at the winning input

### E18 — Model zoo
_(one row per base. Record total params and assert < 3B. **Report tokens-per-answer for each
tokenizer** — BanglaT5 needs 145 where mT5 needs 272, and that ratio is the mechanism the
NLP4Health paper credits for Gemma's win. Report row-level disagreement with the incumbent for
EVERY model even when the score loses — a usefully-disagreeing model is what E14 needs and cannot
get from another seed.)_
Decoders need **lr 1e-5–5e-5**, not BanglaT5's 1e-3. Carrying 1e-3 across diverges and looks
like a bad model.

### E22 — Retrieval
_(arm A: k-NN vs random in-context examples for E20's frozen teacher — index TRAIN ONLY.
arm B: expected flat; report the score split by retrieval similarity, a low-similarity-tail gain
is the only real outcome. arm C: Phase 2 grounding — judged by E16's audit.)_
If a retriever ships, its params (e5-base = 278M) count toward the 3B cap.

### E19 — Ten-seed ensemble
_(report pairwise row disagreement FIRST; 10 × 247.6M = 2.48B — re-measure params in the
Phase 2 environment, where untied embeddings would make it 2.97B)_

### E21 — Synthetic pairs
_(target side must ALWAYS be genuine organizers' text — synthesizing the target teaches the
wrong register. Augment TRAIN ONLY; assert 0 dev/test ids. Score each arm against BOTH the Google
draft and a held-out alternative draft — draft-robustness is the point, not just headline F1)_

### E20 — Teacher ceiling, then distillation
_(stage 1: teacher few-shot Token F1 vs 0.7724 — STOP if below. In-context examples from
train only. Stage 2: arms A gold / B teacher / C 50-50)_

### E12 — Warm-start then transfer

### E13 — Multi-task
_(report BOTH the transfer score and the question→answer score)_

### E14 — Architecture ensemble
_(report row-level disagreement between members FIRST)_

### E15 — Decoder sweep
_(re-verify any winner on a second disjoint dev subset — a 3-way sweep over 300 rows finds spurious winners)_

### E16 — Phase 2 clinical audit
_(repetition rate, unsafe advice, truncated endings — across the top candidates)_
