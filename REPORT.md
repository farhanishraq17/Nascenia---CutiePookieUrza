# Nascenia Bengali Medical Dialogue — Experiment Program Report

> ⏩ **Snapshot of 2026-08-11 — superseded on 08-14, kept as written.** The program continued for
> three more days: cross-seed weight souping reached **0.89532**, then averaging the champion run's
> **own** peak-centred checkpoints reached **0.89552**, which is the current #1 entry and the
> shipped model (`fine_tune_project/E15_decode_sweep/ckptavg_peak5/`). §7's "ship the champion" now
> means that average, not `E05/english_draft/best`. §4's reproduction gap was addressed by
> re-submitting from the notebook itself on 08-15.
> Current state: [PROGRESS.md](PROGRESS.md) · [PREDICTIONS.md](PREDICTIONS.md) ·
> `fine_tune_project/E15_decode_sweep/RESULTS.md`.

**2026-08-11** · CHPC granite + notchpeak · ~40 arms trained across 5 VRAM tiers
**Public leaderboard: 0.89347 — #1**, up from 0.85088 at the start of this program.

Numbers are dev-300, beam-8/lp-1.2/min_new-0, on the frozen seed-42 / 5,000-row split.
Judge on **Token F1 / ROUGE-L** — the local composite is mis-calibrated by ~0.118.

---

## 1. Result

| submission | public LB | |
|---|---|---|
| constant string (day 1) | 0.57849 | |
| register-transfer, 2,750 steps | 0.85030 | the model this program inherited |
| + 2-seed ensemble | 0.85088 | the actual bar when this program started |
| **E05/english_draft, 12,000 steps** | **0.88008** | +0.02920 |
| **+ E15 decoder (beam 8, lp 1.2, min_new 0)** | **0.89347** | **+0.01339** |
| | **total +0.04259** | |

Two changes produced all of it: **read the English source**, and **train 4.4× longer**. A third
— removing a stale decoder setting — produced the last third of the gain for free.

**Champion:** `E05_train_to_convergence/english_draft/best` · BanglaT5 · 247,577,856 params ·
hash `6f9d4d6756032397`. Phase-2 artifacts are on Kaggle (dataset + T4-verified notebook).

---

## 2. The five findings that matter

### 2.1 🔴 The incumbent had not converged — by a factor of 4.4

It stopped at step 2,750 because a Kaggle session ran out. Run properly, `draft_only` peaks at
**15,250** and `english_draft` at **12,000**:

| step | 2,750 | 4,000 | 8,000 | 12,000 | 15,250 |
|---|---|---|---|---|---|
| draft_only Token F1 | ~.7724 | .7807 | .7902 | .7968 | **.8011** |

**Two thirds of the gain arrived after the old budget ended.** No turnover, and loss flattens
with the metric — the loss/metric divergence seen on the old question→answer task is a property
of *that* task, not of BanglaT5. On a T4 this single run would have taken ~57 h; it was
unreachable on the original hardware, not overlooked.

### 2.2 English is worth +0.0220. The patient question is worth nothing. The draft is worth +0.0053.

At matched caps and matched budget, so the input is the only variable:

| input | Token F1 | reading |
|---|---|---|
| all inputs, un-truncated | 0.8042 | truncation buys +0.0007 — **closed** |
| all inputs | 0.8035 | the question buys +0.0003 on top — **nothing** |
| **english + draft** | **0.8032** | 🥇 winner |
| english only | 0.7979 | the Bengali draft is worth only **+0.0053** |
| draft only | 0.7807 | **English alone beats the draft alone by +0.0172** |
| question + draft | 0.7734 | ≈ 0 |

🔴 **The Bengali draft is the weak input, not the strong one.** A model that never sees a single
Bengali token still reproduces the corpus register exactly (`হেলো` 76.0% vs the references'
76.4%) — the register is learned from the *targets*. This re-costs every draft-quality question
in the program: E17 closed by keeping Google, and E21's draft-robustness arms are insurance on a
component measured at +0.0053.

### 2.3 A stale decoder setting was costing 0.0134 of leaderboard

The shipped decoder forced `min_new_tokens 80`. That floor was correct when models
under-generated; once the model already produced ~100 tokens against a ~100-token reference, it
only padded them.

| decoder | Token F1 | ROUGE-L | LB |
|---|---|---|---|
| beam 4, lp 1.0, min_new **80** | 0.8257 | 0.7968 | 0.88008 |
| **beam 8, lp 1.2, min_new 0** | **0.8328** | **0.8039** | **0.89347** |

Verified on a **disjoint** dev subset (0.8348 there vs 0.8328 on the selection rows), and the
gain is **checkpoint-independent** — all 17 checkpoints gained a uniform +0.005–0.007, so the
ranking did not reshuffle. A second 44-config sweep past every boundary of the first found
**exactly 0.0000** more: four configs tie at the plateau. The decoding lever is exhausted.

### 2.4 🔴 RETRACTION: BERTScore is not an inert fluency floor

The project's standing premise — "BERTScore is flat across fluent in-domain text (≈0.006
spread)" — held for the constant-string and question→answer regimes. **It does not hold here.**

The calibrated predictor `LB ≈ 0.4646 + 0.3098·F1 + 0.2·RL` fitted three real submissions to
**±0.0003**, then under-predicted the fourth by **+0.0101**. Lexical components are
deterministic, so that entire miss is BERTScore: the organizers' value moved **0.9442 → ~0.9644**.

Removing the padding improved *semantic* quality in a way Token F1 and ROUGE-L could not see —
BERTScore supplied about a third of that submission's gain. **The predictor is now a floor, not
an estimate**, and BERTScore is live at this quality level.

### 2.5 Ensembling is dead — in both forms, on a diverse pool

| method | result |
|---|---|
| pooled MBR, 2 seeds *(MBR-01, earlier)* | −0.0027 LB |
| **pooled MBR, 6 members across architectures + inputs** | **+0.0020 — inside noise** |
| weight soup, top-3 | 0.8328 — exact tie |
| weight soup, greedy | 0.8319 |
| weight soup, all 10 seeds | 0.8282 — *worse than the best single* |

MBR-01 could be dismissed as "two identical seeds gave consensus nothing to choose from". This
pool spans architectures and input combinations, mT5 disagrees at 0.86 pairwise, and the per-row
**oracle ceiling is +0.0326** — and consensus still cannot convert any of it. Averaging ten seeds
is *worse* than the best single seed. **E14 and E19 are both closed.**

---

## 3. Model selection: BanglaT5 wins, and the mechanism is the tokenizer

Tokens needed per Bengali answer, measured on this corpus:

| model | vocab | tokens/answer | handicap | best Token F1 |
|---|---|---|---|---|
| **BanglaT5** | 32,100 | **142** | 1.00× | **0.8328** |
| Gemma-2-2B-IT | 256,000 | 333 | 2.34× | **0.8068** ← best decoder |
| Qwen3.5-2B / 0.8B | 248,044 | 294 | 2.07× | 0.7835 / 0.7732 |
| mT5-base | 250,100 | 271 | 1.91× | 0.8017 |
| Qwen2.5-1.5B / Qwen3-1.7B / 0.6B | 151,643 | **689** | 4.85× | 0.7306 / 0.7287 / 0.7363 |
| IndicBART | 64,000 | — | — | 0.4401 |

**The NLP4Health prior is partly vindicated and partly refuted.** Gemma-2-2B *is* the best
decoder, and the Indic-tokenizer mechanism the paper credits shows up cleanly — Qwen3.5 (248k
vocab) beats Qwen3 (151k) at every matched step, exactly as its 2.07× vs 4.85× handicap predicts.
But **no decoder beats the encoder-decoder here**: Gemma trails BanglaT5 by 0.026 at equal
budget. Decoders do better the closer their tokenizer gets to Bengali-native; none gets there.

mT5 also fails Phase 2: it leaves **27.9%** of answers cut off mid-sentence against the
references' 6.8%, where BanglaT5 repairs the draft's 35.3% truncation rate exactly to 6.8%.

---

## 4. Phase 2 (20% of final score)

Audited against the organizers' own answers and our draft, since the rates are uninterpretable
without both:

| | truncated % | repeat sent. % | tautology % | len p50 |
|---|---|---|---|---|
| **references** | 6.8 | 0.1 | 7.9 | 93 |
| our draft (model input) | 35.3 | 0.0 | 10.1 | 92 |
| 🥇 champion | **6.8** | 0.9 | 9.3 | 93 |

**No Phase-1 gain in this program was bought with Phase-2 quality** — the champion matches the
reference distribution on every measured axis, and the repetition failure that motivated E16
does not recur (worst arm 1.8% vs references 0.1%).

🔴 **Not covered:** clinical correctness, contradiction, unsafe advice. These need a medical
judge and there is no LLM-judge API on this machine. Three of E16's five checks are **open**.

~~⚠️ **Reproduction gap.** The Phase-2 notebook regenerates **639/1000** rows of the scored
submission byte-exactly (mean Token F1 0.9578). The old decoder reproduced 1000/1000; `beam 8 /
min_new 0` is not precision-stable across bf16→fp32, since more near-ties flip. Fix: submit the
notebook's own output once, making the entry byte-identical by construction.~~

✅ **CLOSED 2026-08-21/22 — the gap was precision, and pinning it fixed it.** The routed bundle
(`PHASE2_BUNDLE_latest/PHASE2_BUNDLE/`) reproduces **1000/1000 rows byte-identical** to the scored
0.89552 CSV — `verification/bundle_phase1.csv` and `weights/champion_banglat5_peak5/submission.csv`
hash to the same sha256. The fix was running the champion branch in **fp32** (bf16 decoded 280/1000
rows differently, because beam-8 is decided by small margins) in its own **transformers 4.57** env,
since 4.57 ties BanglaT5's `shared`/`lm_head` weights and 5.14 does not. **No submission needed to
be spent on this.**

---

## 5. Bugs found — six, all silent

| | what | impact |
|---|---|---|
| BUG-04 | `04_decode.py --max-source-len` defaulted to 384 while arms train at 768/1024/1280 | long-input arms **scored on truncated inputs** |
| BUG-05 | decoder generation caps carried over from BanglaT5 (142 vs 689 tokens/answer) | **3 zoo arms invalid** — measured the cap, not the model |
| BUG-06 | IndicBART's Albert tokenizer emits `token_type_ids`; MBart rejects them | trained fine, decode crashed after |
| BUG-07 | both trainers fell back to **CPU** silently on a dead GPU | 3 arms "trained" on CPU for minutes |
| BUG-08 | `pkill -f <task>` matched the pool script's argv, killing unintended arms | 4 arms lost, twice |
| BUG-09 | **GPU indices are not stable across srun steps** | 3 arms OOM'd on cards a probe reported idle |

Every one had the same shape: **nothing crashes, the output is well-formed, the number is
plausible.** Guards added: a CUDA assert that refuses CPU training, a length guard asserting
`max_new_tokens ≥ p95 target length`, decode caps read from `run.json`, and UUID-based GPU pinning.

### 🔴 A Phase-2 reproducibility finding

Two runs of an identical config produced **300/300 identical predictions** and equal dev F1 to
6 dp — but **different `checkpoint_hash`**. Outputs reproduce exactly; weights do not.
**Reproduction evidence must be the decoded outputs, never a weight hash.**

---

## 6. Program status

**17 of 20 experiments closed.** Open: E21/E22 (never built — E21's rationale was gutted by the
draft measuring +0.0053), and E16's three judge-dependent checks (blocked on API access).

**Closed by measurement:** convergence, input selection, LR, truncation, mT5, IndicBART,
warm-start (+0.0028), multitask (−0.022), decoding, seed diversity, output ensembling, weight
ensembling, and distillation.

🔴 **E20's teacher gate FAILS: 0.5841.** Qwen3.5-9B few-shot scores **0.249 below** the 248 M
student. Per E20's own table: *"< 0.7724 → STOP. Scale does not substitute for fine-tuning on a
fingerprint-matching task."* A 36× larger model cannot match a fine-tuned small one at
reproducing one translator's lexical fingerprint — consistent with E17, where Qwen3-14B lost as a
translator too.

## 7. Recommendation

1. **Ship the champion** — already submitted, holding #1 at 0.89347.
2. **Spend one submission on the Phase-2 fix** (submit the notebook's own output) if you expect
   top-10. 20% of the final score rests on reproduction, and the gap is 361 rows.
3. **Do not build E21.** Its premise is a component worth +0.0053.
4. **Do not pursue ensembling or distillation.** Both are closed with direct measurements.
5. The remaining headroom is BERTScore-shaped, not lexical — and now known to be live.

### Where things live

```
fine_tune_project/_slurm/     registry.py · submit.py · run_pool*.sh · collect.py · analysis/
fine_tune_project/E*/RESULTS.md   per-experiment records
LOCAL_EXPERIMENTS.md · PROGRESS.md · PREDICTIONS.md
```
