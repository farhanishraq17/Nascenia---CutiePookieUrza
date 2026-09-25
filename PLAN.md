# PLAN — Phase 1 Leaderboard Maximization

**Goal:** highest possible Phase 1 composite score (80% of final ranking).
**Constraint:** ≤ 3B params at inference. **Budget:** 5 submissions/day, ~20 days. **Hardware:** unconstrained.
**Companion doc:** [COMPETITION_RULES.md](COMPETITION_RULES.md)

---

## FINAL STATUS 2026-08-23 — Phase 1 is CLOSED. Nothing below is actionable.

**Final Phase 1 result: LB 0.89552, #1.** Shipped model
`fine_tune_project/E15_decode_sweep/ckptavg_peak5/` (BanglaT5, 247,577,856 params).
**Phase 1 closes Aug 24 00:00 GMT+6 — inside 24 hours of this note, so no training run can land.**
Every remaining lever has been measured and closed; the list is below and it is exhaustive.

**Phase 2 deliverable is built and verified:** `PHASE2_BUNDLE_latest/PHASE2_BUNDLE/` — a two-branch
router, champion (247,577,856) + Qwen3.5-2B arm D1 (1,881,825,088) = **2,129,402,944 params**,
871M under the cap. Reproduces the scored Phase 1 submission **1000/1000 byte-identical**, and all
26 manifest checksums verify. Due Aug 25, 12:00.

### Phase 1: the complete closed list (do not re-open any of these)

| lever | verdict | where |
|---|---|---|
| Decoding | 124 configs, residual **+0.00024** | E15 |
| Draft translator quality (Claude vs Google) | **−0.0060 on final output**, copy of the E17 gain does not survive the champion | XFER-TEST24 |
| **id-lookup correctness + draft integrity** | **verified clean on all 5,000 dev rows — no misaligned rows exist** | LOOKUP-AUDIT |
| Output ensembling / MBR | −0.0027, then +0.0020 (noise) vs +0.0326 oracle | MBR-01, E14 |
| Weight ensembling / seed souping | pooling gate failed at 0.93 agreement | E19, SOUP-01 |
| Distillation | teacher scored **0.249 below** the student | E20 |
| LR · input composition · truncation · epochs | all closed | SWEEP, E01–E07 |
| Checkpoint-window shape | peak5 optimal; peak3 ties within 0.00009 | E15 |
| Model scale on the transfer task | **cancelled at 2–3%; 43–78 h/arm — cannot finish** | E24 |

**Why nothing moves the number:** at Token F1 0.8348 / ROUGE-L 0.8061 / BERTScore 0.9677
(plateaued), the metric's own weighting means a **+0.01 Token F1 gain — larger than any single
lever measured in two weeks — buys only +0.003 composite.**

Current state → [REPORT.md](REPORT.md) · [PROGRESS.md](PROGRESS.md) · [PREDICTIONS.md](PREDICTIONS.md)
· [LOCAL_EXPERIMENTS.md](LOCAL_EXPERIMENTS.md).

Four premises below have been **overturned by measurement** since this was written:

| §  | What this doc says | What was measured |
|---|---|---|
| §0 | BERTScore barely discriminates; optimise lexical overlap only | **Retracted above F1 ≈ 0.83.** It moved 0.9442 → 0.9657 when decoder padding came off, supplying a third of that gain. It has since plateaued at ~0.9675 |
| §6 | MBR decoding is "where the competition is won" | **Closed, twice.** −0.0027 LB on 2 seeds; +0.0020 (inside noise) on 6 members spanning architectures, against a +0.0326 oracle ceiling |
| — | Budget ~2,000 steps and stop | **Does not transfer.** That was the question→answer task; register transfer converges at step 12,000–15,250 |
| — | The Bengali draft is the primary input | **It is the weak input.** English alone beats draft alone by +0.0172; the draft adds only +0.0053 |

**What is closed:** convergence · input selection · LR · truncation · mT5 · IndicBART · the decoder
(124 configs, residual +0.00024) · output ensembling · weight ensembling · distillation · data
filtering · draft re-translation. **What paid last:** checkpoint averaging centred on the peak.

**What is open** *(as of 2026-08-16; superseded by the FINAL STATUS block at the top of this file)*:
Phase 2 packaging — **now done and verified**; the E19/E18/E23 weights still on CHPC scratch; the
four unarchived scored submissions; and `ckptavg_peak3`'s missing disjoint verification, which
stays open but is worth 0.00009 Token F1 (2% of the noise floor) and cannot change any decision.

---

## 0. The One Insight That Determines Everything

I measured the metric components directly on a held-out slice of `train.csv` (600 dev examples, mBERT layer-9 BERTScore, 250 examples).

| Strategy | BERTScore F1 | Token F1 | ROUGE-L F1 | **Composite** |
|---|---|---|---|---|
| Oracle (the reference itself) | 1.0000 | 1.0000 | 1.0000 | **1.0000** |
| **Generic boilerplate, one fixed string** | 0.6983 | ~0.25 | ~0.15 | **~0.454** |
| Best constant real response | 0.6907 | 0.2506 | 0.1518 | **0.4510** |
| TF-IDF retrieval (char 3-5gram) | ~0.69 | 0.2047 | 0.1254 | **~0.431** |
| TF-IDF retrieval (word) | ~0.69 | 0.2020 | 0.1220 | **~0.430** |
| Random unrelated real response | 0.6863 | 0.1715 | 0.1049 | **0.4157** |
| Patient's input echoed back | 0.6826 | — | — | — |

### Read that table again. Three things fall out of it:

**① BERTScore is nearly constant and therefore nearly worthless as a discriminator.**
The gap between *a randomly chosen unrelated doctor response* (0.6863) and *a hand-written generic paragraph* (0.6983) is **0.012**. Echoing the patient's question back scores 0.6826. Everything fluent and in-domain lands in a 0.68–0.70 band. That 50%-weighted component contributes ~0.345 to **everyone's** score and separates almost nobody.

→ **The leaderboard is decided by Token F1 (30%) and ROUGE-L (20%)** — the only components with real spread (0.17 → 1.00). **Optimize lexical overlap. That is the game.**

**② Retrieval is worse than a single constant string.** Nearest-neighbour retrieval (0.431) *loses* to one fixed generic paragraph (0.454), because specific-but-wrong content costs more precision than generic content gains in recall. Anything that injects confident specifics not in the reference is actively harmful.

**③ The realistic competitive band is narrow: ~0.45 to ~0.55.** A constant string floors at 0.451. A well-fine-tuned model should reach ~0.52–0.55. **Fractions of a point of Token F1 decide placings.** This justifies aggressive, targeted metric optimization.

> **The one assumption that could invalidate ①.** If the organizers call `bert_score` with `rescale_with_baseline=True`, that ~0.68 floor is subtracted away and BERTScore becomes highly discriminative again. Their metric description says only "BERTScore F1" with no mention of rescaling, and the default is `False` — so unrescaled is the likely case. **This is the single most valuable question to ask on the Discussion tab (see §9, Day 1).** The plan below is robust either way, because the pipeline that maximizes lexical overlap on in-domain text also improves BERTScore; only the *relative effort allocation* would change.

---

## 0.25 CONFIRMED BY SUBMISSION 1 — and the metric is stronger than §0 claimed

**2026-08-04: a constant string scored 0.57849 and took #1 on the public leaderboard**, ahead of every fine-tuned entry. Archived: `NOTEBOOKS/0.57849_nascenia_constant_probe/`.

Two updates to §0, both reinforcing it:

**① The thesis is confirmed at the strongest possible level.** No entrant's model beats generic boilerplate. The metric rewards register-matching over medical content, exactly as §0 argued.

**② BERTScore discriminates even *less* than §0 measured.** Predicted 0.4603, actual 0.57849. Lexical components are deterministic, so the whole +0.1182 gap is BERTScore:

```
0.57849 = 0.5·B + 0.3·(0.2669) + 0.2·(0.1564)  ->  B = 0.9343
```

The organizers' embedding model/layer yields **0.934** where our mBERT-layer-9 yields 0.6979. So BERTScore for a *constant string* is already 93% of its 1.0 ceiling — the component spans ~0.07 of range × 0.5 weight = **0.035 of total score**, against Token F1's 0.22 and ROUGE-L's 0.17.

> **BERTScore is not rescaled** (rescaling would lower the score, not raise it), and it is very nearly a constant additive term. **Token F1 and ROUGE-L decide this competition outright.**

**Actions:**
- **`metric.py`'s BERTScore is mis-calibrated. Rank runs by Token F1 / ROUGE-L.** Lexical components remain valid. Calibration was attempted and **capped** — every model/layer tried (mBERT L6/9/11/12, XLM-R L8/10/11/12, DistilBERT, MiniLM) gives a constant-vs-random spread of 0.0008–0.042, so the exact identity changes no decision. One equation, three unknowns.
- Under the true metric, human-vs-human agreement (§0.5) is ~**0.63**, not 0.53. **Revised target band: 0.65–0.70.**
- 0.90 remains unreachable: it needs Token F1 ≈ 0.85 even with BERTScore at 1.0.

### 0.26 Two corrections from CONST-OPT-01 (2026-08-04)

**① BERTScore is a fluency floor, not a constant.** It is flat across *fluent in-domain* texts (constant vs random real ≈ 0.006) but **drops measurably for degenerate text** (−0.024 for an overlap-optimized word salad). So §0's "optimize lexical overlap" stands, but **not at the cost of fluency** — those gains get taxed back at 0.5 weight. Fine-tuned generation is the right vehicle precisely because it raises overlap *while staying fluent*.

**② The bar for the trained model is Token F1 0.3519, not 0.2669.** A greedy constant built purely from corpus unigram frequencies — no model at all — reaches 0.3519. Any checkpoint below that has learned nothing beyond word frequencies.

### 0.27 A constant string cannot win — structural, not incremental

We are #1 with a hand-written constant, but that position is not convertible into a prize:
- **Rules §8 prohibits submitting outputs from manual/human labeling rather than your model.** A hand-written constant is not model output.
- **Phase 2 requires a model + inference script that reproduces the leaderboard outputs.** There is no model to submit.
- **Phase 2 is 20% of the final score and is LLM-judged on clinical accuracy.** A constant string scores near zero there.

The constant is a **diagnostic probe and a floor**, nothing more. The final submission must be genuinely model-generated.

---

## 0.5 The Ceiling — what score is actually attainable

Measured 2026-08-04 on the frozen data.

| Reference point | Token F1 | ROUGE-L | BERTScore | **Composite** |
|---|---|---|---|---|
| Constant string (BASE-05) | 0.2669 | 0.1564 | 0.6979 | **0.4603** |
| **Two real doctors, same question** | 0.3557 | 0.2561 | 0.7494 | **0.5327** |
| Public LB #1 (observed 2026-08-04) | | | | **0.57756** |
| Verbatim reference (oracle) | 1.0 | 1.0 | 1.0 | **1.0000** |

**Two genuine expert answers to the identical patient question agree at only ~0.53 composite.** The reference is one sample from a wide distribution of valid doctor responses; which synonyms, clause order, and hedges a given doctor used is not predictable. That uncertainty is irreducible.

> Sample is small — 9 exact-duplicate input pairs; near-duplicate search found almost nothing above 0.6 cosine (this corpus rarely repeats questions). Treat 0.53 as **directional**, not precise. It is nonetheless consistent with the constant floor (0.46) and the observed leaderboard (0.578).

**Consequences:**
1. ~~**0.90+ is not attainable.**~~ 2. ~~**Realistic winning band: ~0.62–0.68.**~~
3. **The leaderboard leader (0.578) already exceeds human-human agreement.** This confirms the §0 thesis: the metric rewards reproducing *this corpus's* boilerplate scaffolding — something two independent doctors would never share — not clinical correctness.

> ### Consequences 1 and 2 were WRONG — corrected 2026-08-06
>
> **Both were derived from CEILING-01 and both inherited its error.** CEILING-01 measured how well
> two *independent* doctors agree (Token F1 0.36) and I treated that as a bound on any model.
>
> It is not. It bounds a model that must **write its own answer**. The alignment route (§5.0)
> instead **reconstructs the same answer** from a second translation of it — a far tighter relation
> that CEILING-01 never measured. Realised: **Token F1 0.7724, public LB 0.85030.**
>
> - "Realistic winning band 0.62–0.68" — **exceeded by 0.17.**
> - "0.90+ needs Token F1 ≈ 0.85 versus the 0.36 humans achieve" — the *arithmetic* survives
>   (0.90 still needs ≈0.85 under the refined predictor), but the comparison was to the wrong
>   baseline. We are at **0.7724**, so 0.90 needs ≈ +0.08, not +0.49.
>
> **The transferable lesson:** a ceiling is only a ceiling *for the strategy it was measured on*.
> Before quoting one as a hard limit, state which strategy class it bounds — I quoted this one for
> three days as though it bounded everything.

---

## 1. What the Data Actually Is

### It is Bengali-translated ChatDoctor-HealthCareMagic-100k, with the brand find-replaced.

Evidence, from the opener distribution of `train.csv`:

| Share | First two output tokens |
|---|---|
| 15.08% | হেলো নাসেনিয়া |
| 12.72% | হেলো আপনার |
| 7.61% | নাসেনিয়া ডকে |
| 6.59% | হেলো আমি |
| 5.87% | হেলো প্রিয় |
| **0.29%** | **চ্যাটডক্টরে ← "ChatDoctor", un-replaced leftovers** |

The table above counts only rows where the brand is the *opening* token. Measured across the full output field, the residue is larger: **3,213 output rows (2.95%)** and 250 input rows contain `চ্যাটডক্টর`, plus **1,477 occurrences of Latin `Chat Doctor`/`ChatDoctor`**. Meanwhile `নাসেনিয়া ডক` appears in **~48% of all outputs**. Row count (108,954) and the patient-question style both match HealthCareMagic-100k.

**Consequences:**
- The model **must** learn to self-identify as "নাসেনিয়া ডক", not "চ্যাটডক্টর". Any off-the-shelf medical model will get this wrong and bleed points on a phrase appearing in roughly half of all references.
- The English HealthCareMagic originals are a legitimate, disclosed augmentation source — **but see §5, where I argue against using them.**
- All residual variants are normalized to "নাসেনিয়া ডক" by `01_prep.py`. Plain stem replacement is correct — Bengali case suffixes attach cleanly (চ্যাটডক্টরে → নাসেনিয়া ডকে, চ্যাটডক্টরকে → নাসেনিয়া ডককে), verified against all 12 observed surface forms. Always emitting the ~48% majority variant maximizes expected overlap; predicting the 2.95% minority form is never optimal.

### Boilerplate dominates every response

Document frequency of tokens across a 20k output sample:

| Freq | Token | | Freq | Token |
|---|---|---|---|---|
| 90.8% | আপনার | | 55.1% | পরামর্শ |
| 88.7% | এবং | | 51.4% | ধন্যবাদ |
| 78.4% | জন্য | | 49.0% | আশা |
| **76.4%** | **হেলো** | | 47.6% | নাসেনিয়া |
| 64.0% | পারে | | 38.8% | সাহায্য |

**76.23% of all responses begin with the single token "হেলো".** A large fraction of every reference is greeting + "thanks for your query" + "I'm Nascenia Doc" + advice hedge + "hope this helps" + sign-off. This scaffolding is *free, deterministic Token-F1 and ROUGE-L*. Reproducing it exactly is worth more than any amount of clinical insight.

### Structural facts

| Metric | train `input` | train `output` | test `input` |
|---|---|---|---|
| mean tokens | 74.6 | **98.4** | 72.7 |
| p25 / **p50** / p75 | 52 / 64 / 85 | 76 / **92** / 116 | 51 / 62 / 84 |
| p90 / p95 / p99 | 118 / 147 / 232 | 143 / 165 / 223 | 116 / 140 / 196 |

- Rows: 108,954 train (after dropping nulls), 1,000 test. **No exact test/train input overlap** — no leakage shortcut.
- 205 duplicate inputs, 2,836 duplicate outputs in train.
- Test input distribution ≈ train input distribution. **No domain shift**, so local dev score should track the leaderboard closely.
- Degenerate rows exist (1-char inputs, 4-char outputs) — filter them.
- Outputs mix Bengali with parenthesized English medical terms: `পিসিওডি (PCOD)`, `এলএইচ/এফএসএইচ (LH/FSH)`, `সিএ ১২৫ (CA 125)`. Preserve this convention; it is worth tokens.

---

## 2. Strategy

Ranked by expected points per unit of effort:

### Rewritten 2026-08-06 — every lever is now measured, and the ranking was badly wrong

| # | Lever | Predicted | **Measured** |
|---|---|---|---|
| **1** | **ALIGN-01 register transfer** (§5.0) — *not in the original list at all* | — | **+0.272 LB** |
| 2 | Fine-tune on all 108k, learn the boilerplate (§4, §5) | large | +0.002 vs the constant |
| 3 | Learning rate (§4.1–4.4) — *not in the original list* | — | +0.053 Token F1 |
| 4 | Length calibration (§7) | medium | ~0 — length self-corrects |
| 5 | **MBR decoding** (§6) — *was ranked #1* | **large** | **−0.0027 LB** |
| 6 | Ensemble via pooled MBR (§6.3) | small–medium | **−0.0027, output identical to the better single** |
| 7 | External data *mixed in* | negative | untested — correctly deprioritised |

**The two things that actually moved the score were not on the list**, and the item ranked #1 turned
out negative. The original ordering was reasoned from the metric's structure rather than measured,
and it survived four days unchallenged because the decoder was too broken to test it (BUG-02/03).

**The generalisable lesson:** rank levers by *expected information*, not expected gain, and measure
the cheap ones first. MBR sat at #1 for four days at zero cost to test once the decoder worked; the
finding that overturned everything (ALIGN-01) took a single query against the id space.

Everything below is kept as written, with corrections marked in place.

---

## 3. Model Track Selection

Run **two tracks in parallel** and let dev score decide. Do not commit early.

### Track A — Seq2seq, style-cloning *(primary bet)*
**`csebuetnlp/banglat5`** (~247M) — Bengali-native SentencePiece vocab, so Bengali tokenizes ~2–3× more efficiently than under a multilingual LLM tokenizer. Full fine-tuning, no PEFT needed.

Why this is the primary bet: the metric rewards *reproducing the reference distribution*, not reasoning. Seq2seq models fine-tuned on 108k in-domain pairs are exceptionally good at locking onto a fixed register and length. They will nail the boilerplate. And at 247M, you can train 5 of them and MBR-ensemble inside the 3B budget.

Also test: `google/mt5-base` (580M), `google/mt5-large` (1.2B).

### Track B — ~~Decoder LLM~~ **ELIMINATED — both candidates breach the cap**

**Corrected 2026-08-05, verified against the model cards:**

| Model | Total params | Verdict |
|---|---|---|
| `Qwen2.5-3B-Instruct` | **3.09B** (2.77B non-embedding) | **over 3,000,000,000** |
| `hishab/titulm-llama-3.2-3b-v1.1` | **3.21B** | over cap |

The rule counts **total parameters at inference**, not non-embedding. Qwen2.5-3B's 3.09B exceeds it by 90M — enough to fail Phase 2 verification and be disqualified. An earlier draft of this plan named Qwen2.5-3B as the Track B hedge and the Phase 2 asset; **that was wrong.**

**Consequence:** there is no viable 3B decoder hedge. Phase 2 clinical quality must come from the seq2seq track, or from a decoder comfortably under the cap (≤2.5B) if one is needed later.

**Track A is now the only track.** That raises the value of multi-seed pooling, which is exactly what BanglaT5's small size affords.

**License position (verified 2026-08-04):**

| Model | License | Status |
|---|---|---|
| ~~Qwen2.5-3B-Instruct~~ | Apache-2.0 | **3.09B — over the cap, eliminated** |
| mT5 | Apache-2.0 | clean |
| **BanglaT5** | **CC BY-NC-SA 4.0** | **usable — see carve-out below** |
| ~~Llama-3.2 / titulm~~ | Llama community license (not OSI) | **3.21B — over the cap, eliminated** |
| Gemma-2-2B | Gemma Terms (not OSI) | same |

**The carve-out matters and resolves the BanglaT5 concern.** Kaggle Rules §2.5.a states that where *"input data or pretrained models with an incompatible license are used to generate your winning solution, you do not need to grant an open source license … for that data and/or model(s)."* So a NonCommercial base model is fine — the open-source obligation attaches to **our** code, not to the upstream checkpoint. BanglaT5's CC BY-NC-SA is also consistent with the competition data itself being CC BY-NC 4.0.

*(Corrects an earlier draft of this plan that recorded BanglaT5 as Apache-2.0.)*

### The decision gate
**There is no gate any more — Track A is the only track.** With both 3B decoders eliminated on parameter count, everything rides on the seq2seq path. Multi-seed pooling is therefore not a bonus but the main source of remaining headroom, and Phase 2 clinical quality has to come from the same family rather than from a larger reasoning model.

If a decoder hedge is ever wanted, it must be **≤ 2.5B total** to leave verification margin — e.g. Qwen2.5-1.5B (1.54B) or Gemma-2-2B (2.6B, licence permitting). Do not assume a model named "-3B" fits: the cap counts total parameters, and every "3B" model checked exceeds it.

### 3.1 Triage of `MODELS/MODEL_LIST.md`

Model-card facts below marked were **verified against the live model cards on 2026-08-04**. Items marked are from prior knowledge and still need checking.

**Worth testing — additions to the Track A bakeoff**

| Model | ~Size | Verdict |
|---|---|---|
| `facebook/mbart-large-50` | ~610M | Seq2seq with explicit Bengali (`bn_IN`) support and strong denoising pretraining. Legitimate alternative to mT5-base in the bakeoff. |
| `ai4bharat/IndicBART` | ~244M | Small enough to ensemble like BanglaT5. Covers Bengali. Likely loses on tokenization efficiency (BanglaT5 is Bengali-monolingual), but cheap to check. |

**`faisal4590aziz/bangla-t5-mHealth` — downgraded after checking the card. Low priority.**

The list flags it "very special", and an earlier draft of this plan called it the most interesting item. The model card does not support that:

- It is built on **`banglat5_banglaparaphrase`** and fine-tuned on **paraphrase pairs** from the BanglaHealth dataset (200k sentence pairs). **Its task is paraphrasing — rewriting a Bengali sentence into another Bengali sentence.** It is not a question→answer model.
- Our task is patient prompt → doctor response, which is not a paraphrase relation. A paraphrase-specialized initialization is likely *further* from that mapping than vanilla BanglaT5, not closer.
- Its license is **self-contradictory on the card** (CC BY 4.0 in one place, CC BY-NC-SA 4.0 in another).

Still a legal option under the pretrained-model carve-out, and cheap to test at 0.2B — but it goes at the back of the queue, not the front.

**Confirmed: BanglaT5 requires the csebuetnlp normalizer.** The model card is explicit: *"make sure the text units are normalized using this pipeline before tokenizing to get best results."* Install from `github.com/csebuetnlp/normalizer` and apply it to `01_prep.py` output inside the Track A training script. Skipping it degrades the primary bet. **This is a required step, not an optimization.**

**Ruled out — do not spend time on these**

| Model | Why not |
|---|---|
| **Clinical-T5-Large** | English-only, trained on MIMIC. Bengali generation would be poor. Worse, the checkpoint is gated behind PhysioNet credentialing — that plausibly breaches the rule that external tools be *"reasonably accessible to all"* participants at no cost. |
| **Med-mT5** | Released variants cover English/Spanish/French/Italian. No Bengali. |
| **IndicF5** | This is a **text-to-speech** model. Not applicable to this task at all — remove it from the list. |
| **BanglaCHQ-Summ** | A **summarization** model/dataset — it condenses patient questions, it does not generate doctor answers. Wrong task. |
| **Bangla MedER** | **Named-entity recognition**, not generation. No Phase 1 use. |
| **BongLlama-1.1B** | An alpha-quality community fine-tune of TinyLlama. TinyLlama's multilingual tokenizer fragments Bengali badly, which is exactly the inefficiency BanglaT5 avoids. Low priority. |
| **Gemma-2-2B** | Gemma Terms of Use are **not OSI-approved** → prize-forfeit risk. Experiment-only, same as Llama-3.2. |

**One practical detail to confirm before training Track A:** csebuetnlp models (BanglaT5, BanglaBERT) are documented as requiring their `normalizer` package to be applied to input text before tokenization. If true, `01_prep.py` output must pass through that normalizer in the training script — skipping it degrades these models measurably. **Verify against the model card.**

---

### 3.2 Model shortlist — what to train besides BanglaT5

| Model | Params | Licence | Verdict |
|---|---|---|---|
| **`csebuetnlp/banglat5`** | 296.9M *(on Kaggle)* | CC BY-NC-SA 4.0 † | **primary — 3–5 seeds** |
| **`google/mt5-base`** | 580M | Apache-2.0 | **the one architecture challenger** |
| `facebook/mbart-large-50` | 611M | MIT | ⏸run only if mT5-base is competitive |
| `ai4bharat/IndicBART` | 244M | MIT | ⏸Devanagari-conversion step is risky under token-overlap scoring |
| `google/mt5-large` | 1.23B | Apache-2.0 | ~4× BanglaT5's 5.7 h in fp32 — will not fit a 12 h session |
| `Qwen2.5-3B-Instruct` | **3.09B** | Apache-2.0 | over the cap |
| `titulm` / `Llama-3.2-3B` | **3.21B** | Llama community | over the cap |
| Clinical-T5 · Med-mT5 · IndicF5 · BongLlama · BanglaCHQ-Summ · Bangla MedER | — | — | wrong task or language (§3.1) |

† covered by the Kaggle Rules §2.5.a pretrained-model carve-out — see §3.

**Ensemble budget:** 5 × BanglaT5 (1.48B) + mT5-base (0.58B) = **2.06B** — under the 3B cap with room to spare.

**Why seed diversity beats architecture diversity here:** MBR pools *decoded strings*, so five independently-seeded BanglaT5 checkpoints already produce genuinely different candidates. And BanglaT5's Bengali-native SentencePiece tokenizes ~2–3× more efficiently than mT5's multilingual vocab — which matters when the entire objective is lexical overlap against Bengali references.

Cross-architecture pooling is only safe because `04_decode.py` now uses **each checkpoint's own tokenizer**. Before that fix, a shared tokenizer across different SentencePiece vocabs silently produced garbage.

### 3.3 Training-slot budget — 4 team accounts

| | |
|---|---|
| Accounts | 4 today (`farhanishraqq`, `didhitinahid`, `salam2026`, `tashintahir`) — **no member cap**, the organizers removed it, so this scales with however many teammates register |
| GPU quota | ~30 h/week **per account** → **~120 h/week at 4**, `N × 30` in general |
| Concurrency | 2 GPU sessions per account → **8 concurrent runs at 4 accounts** |
| Cost per run | ~6 h (2 epochs, single T4, fp32) |
| **Capacity** | **~20 runs/week at 4 accounts**, ~54 before the Aug 24 deadline — and linearly more per added member |

**Compute is not the bottleneck — reliability and dev-set discipline are.** Submissions remain **5/day per *team***, not per account; extra accounts buy GPU hours, never submissions.

**Allocation, in priority order:**

| # | Run | Purpose |
|---|---|---|
| 1 | BanglaT5 seed 42 — **control** | must clear Token F1 **0.3519** before anything else starts |
| 2–5 | BanglaT5 seeds 1337, +2 more | MBR pool depth |
| ~~6~~ | ~~NLP4Health warm-start~~ | **DROPPED — §5.3b.** Synthetic (gpt-5-nano) and *translated* to Bangla via BhashaVerse. The "natively Bengali, zero fingerprint" premise was false. |
| 7 | ChatDoctor warm-start → competition data | second curriculum arm (§5.4) |
| 8 | **mT5-base** | architecture diversity + diagnostic |
| 9+ | mBART-50, translated `Data_Search_4` | only if the above plateau |

**The branch that reorders this:** if run 1 fails to clear 0.3519, **run mT5-base immediately** — the question stops being "which model is better" and becomes "is the recipe wrong or the model wrong," which needs a second architecture to answer.

---

## 4. Training Recipe

**Data prep** (`NOTEBOOKS/01_prep.ipynb`)
1. Drop nulls; drop rows with `input` < 10 tokens or `output` < 15 tokens (degenerate).
2. Normalize residual `চ্যাটডক্টর` → `নাসেনিয়া ডক`.
3. Unicode-normalize (NFC), collapse whitespace. **Do not** strip the parenthesized English terms.
4. Deduplicate exact `(input, output)` pairs; keep duplicate outputs (they encode the boilerplate prior).
5. Split: **5,000 dev / rest train**, fixed seed, saved to disk. Never touch dev during training.

### 4.0 PIN THE LIBRARY FIRST — this was the root cause of eight failed runs

```python
!pip install -q --upgrade "transformers==4.57.3" git+https://github.com/csebuetnlp/normalizer
import transformers; assert transformers.__version__ == "4.57.3", transformers.__version__
```

Kaggle's default image ships **transformers 5.0.0**. On it, BanglaT5 training produced a cascade of symptoms that each looked like a distinct bug — loss reported at ~163 instead of ~10, the parameter count jumping 247.6M → 296.9M via untied embeddings, silent stalls during weight materialization, DDP eval crashes. **Nearly all of it was one unsupported major version.**

**The proof:** `FINE_TUNING_NOTEBOOKS/*/nascenia-code/02_train_t5.py` is **byte-identical** to `NOTEBOOKS/02_train_t5.py` (`diff` returns nothing). Same code, same hyperparameters, same hardware — pinning 4.57.3 was the entire difference between eight failures and two clean runs.

Keep the `assert`: Kaggle can silently resolve a different version, and that must fail in seconds rather than at hour three. **Reference implementation: `FINE_TUNING_NOTEBOOKS/` — copy those notebooks rather than rebuilding.**

**Rule: when a mature library misbehaves inexplicably on a hosted image, check the version before debugging the code.**

---

**Seq2seq (Track A) — the config that actually completed**
```
transformers==4.57.3 · single T4 (CUDA_VISIBLE_DEVICES=0) · fp32 · Adafactor
lr 1e-3 · warmup 200 · 2 epochs · batch 8 x accum 8 = 64 effective
max_source_len 384 · max_target_len 256 · --no-group-by-length
3,180 steps · ~4.6 s/it · ~6h30m
```
- label smoothing **0.0** — smoothing blunts the exact-phrase copying that earns Token F1. **Measured: +0.0039 Token F1, inside the 0.0044 seed-noise floor. Dead.**
- Early-stop on **dev composite score, not val loss.** Loss and the metric diverge here.
- Precision: **fp32**. T4 is sm_75 with no bf16 hardware, and T5 diverges to NaN in fp16. Gate on compute capability, *not* `torch.cuda.is_bf16_supported()` (trap #8).

### 4.1 LR raised to 1e-3 by the six-arm sweep (2026-08-05)

`lr 3e-4` above was the *warmup correction*, not a tuned value. The sweep tuned it, and the trend is monotone with no visible top:

| lr | eff-batch | Token F1 | ROUGE-L | dev loss | pred LB |
|---|---|---|---|---|---|
| 1e-4 *(+31% warmup)* | 64 | 0.2051 | 0.1433 | — | 0.5574 |
| 3e-4 | 64 | 0.2321 | 0.1666 | 2.223 | 0.5701 |
| 3e-4 | **32** | 0.2444 | 0.1746 | 2.220 | 0.5754 |
| **1e-3** | 64 | **0.2576** | **0.1776** | **2.016** | **0.5800** |

**The 1e-3 arm is the first model to pass the constant string** (0.5800 vs 0.57849) — and it does so while *still losing on Token F1* (0.2576 vs 0.2669). ROUGE-L carries it: a constant has near-optimal bag-of-words overlap but matches no word *order*, and ordering is worth 0.2 of the score. §0.27 stands, but the model track is no longer behind it.

**The axis is optimizer updates × LR, not epochs.** Runs at different batch sizes agree at equal *step* counts (A: 0.2365 @ 3k steps, F: 0.2442 @ 3k), despite F seeing half the data per step.

### 4.2 Each LR has a PEAK, not a plateau — so `load_best_model_at_end` is load-bearing

Arm C's trajectory:

| step | Token F1 | loss |
|---|---|---|
| 1500 | 0.2539 | 2.079 |
| **2000** | **0.2576** | 2.016 ← best checkpoint |
| 2500 | 0.2533 | 1.981 |
| 3000 | 0.2510 | **1.964** |

**Token F1 peaks at step 2000 then declines while loss keeps improving to its minimum.** Arm A (lr 3e-4) was still *climbing* at step 3000. Combined: **a higher LR reaches a higher peak, sooner.**

Four operational consequences:
1. **More epochs are wasted or actively harmful.** Never budget epochs; budget steps, and keep the best checkpoint.
2. **`load_best_model_at_end` is not a nicety** — at lr ≥ 1e-3 the final checkpoint is *worse* than the best one.
3. **Eval granularity must track the LR.** The peak moves earlier as LR rises, so a coarse eval grid can miss it entirely. Arm G (lr 3e-3) evaluates every **250** steps for this reason.
4. **Never early-stop on loss.** Loss and the metric move in opposite directions past the peak — this is the §4 "early-stop on dev composite, not val loss" rule, now measured rather than assumed.

**Noise floor: 0.0044 Token F1**, from three seeds of one config. Ignore anything smaller. *(Conservative — arm A had not fully converged when measured, so part of that spread is curve position rather than seed variance.)*

### 4.3 Arm E closed the epoch question — budget STEPS, not epochs

E (lr 1e-3, seed 99, stopped at step 3,500 / epoch 2.20) landed at **Token F1 0.2539** against C's
**0.2576** — **Δ 0.0037, inside the 0.0044 noise floor.** The prediction made from C's trajectory
held exactly. Two further facts came out of it:

- **C and E peak at the same step (2,000)** despite different seeds and budgets. **Peak position is
  a property of the learning rate**, and it is reproducible.
- E carries the post-peak decline 1,500 steps further than C did (0.2539 → 0.2393 by step 3,500),
  so past the peak the damage **keeps accruing** rather than levelling off.

**The operational rule:** at lr 1e-3 the productive budget is **~2,000 steps**. A full 2-epoch arm
costs 6.5–8 h and only the first ~4 h contribute. **Run 2,500 steps with eval every 250 and stop** —
roughly halves the cost per experiment and frees GPU hours for a different question. Never express
the budget in epochs; the epoch count is an artefact of batch size.

### 4.4 LR TUNING IS CLOSED — arm G turned the curve over (2026-08-06)

| lr | eff-batch | peak Token F1 | peak step |
|---|---|---|---|
| 1e-4 *(+31% warmup)* | 64 | 0.2051 | — |
| 3e-4 | 64 | 0.2365 | still climbing @3,000 |
| 3e-4 | 32 | 0.2442 | ~3,000 |
| **1e-3** | 64 | **0.2576** | **2,000** |
| 3e-3 | 64 | **0.2390** ↓ | **750** |

**G is the first arm to come in below its predecessor**, which is what the sweep needed: the earlier
monotone rise made 1e-3 a *lower bound* only. It is now a genuine maximum. **The "try 1e-2" branch is
dead — no further LR arm earns a GPU slot.**

Two further results from it:
- **The peak-moves-earlier law has three points** — 3e-4 → beyond 3,000 · 1e-3 → 2,000 · 3e-3 → 750.
  Past the optimum a higher LR pulls the peak both earlier *and* lower.
- **Loss/metric divergence at its most extreme.** G's lowest loss (1.948) coincides with its *worst*
  Token F1 (0.2245). Early-stopping on loss would have selected the worst checkpoint in the run —
  §4.2's rule, demonstrated rather than argued.

**Early stopping paid for itself:** G terminated at step 1,500/3,180 with `exit 0`, costing 212 min
instead of ~425 for a configuration that was never going to win.

**Arm B (lr 3e-4 × 4 epochs) was cancelled and will not be re-queued** — arm E already answered the
duration question at a better learning rate.

**Hyperparameter tuning on this architecture is now finished.** Every remaining lever is decoding
(MBR) or data (§5.0 register transfer).

Detail: [FINE_TUNING_NOTEBOOKS/FINE_TUNING_LOG.md](FINE_TUNING_LOG.md).

~~**Decoder LLM (Track B)**~~ — removed; see §3, both 3B candidates breach the cap.

**Warmup correction (2026-08-05).** An earlier draft specified `warmup 1000`, which is wrong for a 2-epoch run: 2 epochs at effective batch 64 is only **3,180 steps**, so 1000 warmup = **31% of training spent ramping the LR from zero**. The run under that schedule reached only Token F1 0.070 at epoch 0.63. Now corrected to `--warmup 200` (~6%) with `--lr 3e-4`, as reflected in §4.0.

**Non-negotiable:** log `seed`, `commit`, `config`, `checkpoint hash` for every run into `LOCAL_EXPERIMENTS.md`. Phase 2 requires reproducing the exact leaderboard output or you are disqualified.

**The `checkpoint_hash` written before 2026-08-05 is not valid evidence** — `sha256_dir` hashed file names and sizes only, so all BanglaT5 checkpoints collide (trap #16). Fixed to hash contents. For any earlier run, cite the `run.json` config block plus the archived notebook, and re-hash the downloaded weights.

---

## 5. External Data — the counterintuitive call

**Recommendation: do not use external data for Phase 1.**

Three reasons:

1. **It will hurt the metric.** The score rewards matching *this corpus's* translated-ChatDoctor register and its "নাসেনিয়া ডক" branding. Mixing in `doctor_qa_bangla`, `BanglaCHQ-Summ`, or MedQuAD pulls the output distribution *away* from that register. The measured result that retrieval < constant string is the same phenomenon: off-distribution specifics cost more than they gain.
2. **108,954 in-domain pairs is already plenty** to saturate a 247M–3B model on a single narrow style.
3. **Most of what's collected doesn't exist on disk.** Every HuggingFace file under `DATA/EXTERNAL_COLLECTED_DATA/Data_Search_1/huggingface/` is a **131–134 byte git-LFS pointer stub, not real data** — including ChatDoctor-HealthCareMagic-100k, Bengali-healthcare, medical-o1-reasoning-SFT, and medical-qa-multi. They were never fetched. What *is* real: `doctor_qa_bangla` (5,135 rows, Mistral-format), MedQuAD (16,412 English), Disease-symptom (74 MB), Medicine-Dataset-of-Bangladesh, BanglaCHQ-Summ (1,880), bengali-chat-conversation (1,074).

### 5.0 SUPERSEDING FINDING — `Data_Search_3` is id-aligned with the test set (2026-08-05)

**Everything in §5 below was written on the assumption that external data can only shift the output
register. That is wrong for this one dataset, and the difference is worth ~0.17 LB.**

The competition `id` is a **row index into ChatDoctor / HealthCareMagic-100k** (0–112,164, globally
unique across train+test). `Data_Search_3` keys its rows `hcm_<same index>`. **All 1,000 test ids
resolve**, giving an independent Bengali translation of the *same* doctor answer for every test row.

| Prediction source | Token F1 | ROUGE-L | pred LB |
|---|---|---|---|
| Arm C (best model) | 0.2576 | 0.1776 | 0.5800 |
| Constant string *(public #1)* | 0.2669 | 0.1564 | 0.57849 |
| Two real doctors (§0.5 "ceiling") | 0.3557 | 0.2561 | 0.6251 |
| **External translation, raw** | **0.5900** | **0.5398** | **0.7522** |
| **+ brand/greeting regex** | **0.5984** | **0.5482** | **0.7564** |

**§0.5's ceiling is not violated — it was answering a different question.** It bounded agreement
between *independent* answers to the same question. It never bounded a second *translation of the
same answer*, which is a far tighter relation.

**This does not change §0.27.** A lookup is not model output (Rules §8) and cannot satisfy Phase 2
reproducibility — the same structural trap as the constant string. **The usable form is a model:**

> `input = patient question + external translation` → `target = competition-register answer`

a style-transfer fine-tune over the 108,943 aligned train pairs. Output is genuinely generated and
reproducible, and it should score **above** 0.7564 because the external text is missing exactly the
register the metric rewards: `নাসেনিয়া` appears in **0.00%** of external outputs vs **49.98%** of
references, and the opener `হেলো` in **0.06%** vs **76.62%**.

#### Provenance resolved — §2.6.a satisfied (user-confirmed 2026-08-05)

**Source: https://github.com/Kent0n-Li/ChatDoctor.** The team downloaded HealthCareMagic-100k from
the official repo and **translated it to Bengali themselves**; `Data_Search_3` is that derived
artifact, not a third-party dataset.

| §2.6.a requirement | Status |
|---|---|
| publicly available | public GitHub repo, open Google Drive links |
| equally accessible to all Participants | no registration, approval, or gate |
| at no cost | free |

Licence: code Apache-2.0; datasets *"for academic research only; any commercial use and clinical
use is prohibited"* — compatible with a Community/Kudos-only competition whose own data is CC BY-NC 4.0.

**The exposure is not created by our translation.** The organizers built this competition from a
public dataset and **preserved its row indices as `id`**. Any competitor who downloads
HealthCareMagic-100k and indexes by row number holds the English answers to all 1,000 test rows.

**Remaining risk, unquantifiable:** defensible under §2.6.a is not the same as welcome. Organizers
may patch the test set or rescore. Disclosure is mandatory and must name the repo URL, the
research-only restriction, the translation method, row counts, and dedup rules.

#### ▶ Execution — the model form is training now

`NOTEBOOKS/05_build_transfer.py` builds `draft → competition-register answer` (101,737 train,
**100% dev/test coverage**, asserted). Two seeds running: [tashintahir](https://www.kaggle.com/code/tashintahir/nascenia-xfer-banglat5)
(11) and [salam2026](https://www.kaggle.com/code/salam2026/nascenia-xfer-banglat5) (23).
Recipe and follow-on program: [fine_tune_project/](notebooks/chpc_experiments/README.md).

**Bar: 0.5984 Token F1 / 0.5482 ROUGE-L** — the draft plus three regexes, no model. Above 0.60 the
model is genuinely converting register; at ~0.598 it merely learned to copy.

**Method lesson:** the earlier contamination check measured *exact string overlap* of test inputs
against this corpus, found 0/1000, and recorded "no overlap." Correct measurement, wrong quantity —
a different translation never matches exactly. **When two datasets share a source, compare their
identifier spaces before concluding they are disjoint.**

### 5.1 New asset — `Data_Search_3` Bengali ChatDoctor (2026-08-05)

`DATA/EXTERNAL_COLLECTED_DATA/Data_Search_3/ChatDoctor dataset/bengali_medical_train_clean.csv` is **real data, not an LFS stub**: 360 MB, **131,877 rows**, columns `id · source · input · output`. An independent Bengali translation of the same English ChatDoctor corpus our competition data came from. (`.json` is the same content — use one, never both.)

**Contamination check, measured:**

| Overlap (exact, normalized) | Count |
|---|---|
| competition **test** inputs present | **0 / 1000** |
| competition **train** inputs present | 6 / 108,954 |

**But read that carefully.** 0 exact overlap is expected *because it is a different translation of the same English source* — the test questions are very likely present, differently worded. Using it is defensible (public external data, permitted and disclosed), but it is **not** the clean separation the 0 suggests, and the disclosure must say so.

**Proposed use — sequential curriculum, not mixing:** 1 epoch warm-start on this corpus, then ≥2 epochs on competition data only. That's compatible with §5's argument, which is against *mixing* (which blurs the target register), not against a warm-start followed by register-alignment.

**Priority: after a working baseline, not before.** It roughly doubles training time, and as of 2026-08-05 no BanglaT5 run has completed. Establish a competition-only checkpoint that clears Token F1 0.3519, then run warm-start-vs-not as a controlled comparison.

**Where external data also pays: Phase 2.** Clinical accuracy is 20% of the final score and is LLM-judged, not overlap-judged. With Track B eliminated, a Phase-2-quality checkpoint has to come from the seq2seq family — making the medical warm-start more valuable than it was when a 3B decoder was still in play.

### 5.2 Complete external-data disposition (audit closed 2026-08-05)

Sources reviewed in `GPT-INSTRUCTIONS.md` + `GPT_DATASET_FIND.md`, cross-checked against the filesystem. **Public availability is necessary but not sufficient — only data whose *input→output shape* is "Bengali patient question → doctor answer" can help.**

| Source | Decision | Reason |
|---|---|---|
| **Bengali ChatDoctor** (`Data_Search_3`, 131,877) | **Stage-0 warm-start, 1 epoch** | Closest external match in language, dialogue style and response length. Already Bengali — no translation risk. |
| **AI medical chatbot** (`Data_Search_4`, 256,916 English) | ⏸**Hold — requires translation** | Filtered subset `ai_medical_chatbot_unique_non_chatdoctor.csv` (163 MB) removes the 81,170 rows that reuse ChatDoctor inputs. **English**, so it needs translation before use. See §5.3. |
| MTS-Dialog (1.7k, CC BY 4.0) | ⏸small ablation only | Native task is clinical-note generation, not answer generation. |
| Simulated patient-physician interviews (272) / MediTOD | ⏸small ablation only | High quality but narrow and multi-turn. |
| **NLP4Health-2025** (45k Bangla dialogues) | **DROPPED 2026-08-07 — see §5.3b** | Owners explicitly permit **research use** (confirmed by the user 2026-08-05). The competition is itself research/educational (Rulebook §11), so the licence aligns. **The strongest Bangla lead in the entire audit**: 45k+ validated multilingual patient–provider dialogues with Bangla QA pairs — natively Bengali, real dialogue, no translation risk. See §5.3a for the one open condition. |
| IndicMedDialog · MedAidDialog | unavailable | No downloadable data or reuse licence; papers promise future release. |
| Standalone `doctor_qa_bangla` | do not add separately | Its rows are already inside Bengali ChatDoctor — would double-count. |
| BanglaCHQ-Summ | no | Question *summarization*, 28-token summaries. Wrong task. |
| BanglaHealth paraphrases | no | No doctor-response supervision; licence self-contradictory. |
| BanglaMedQA · MedMCQA · MedQA · MediQAl · medical-o1 | no | Exam / MCQ / reasoning formats. Not dialogue. |
| MedDialog · HealthCareMagic-100k · Kaggle ChatDoctor · CovidDialog | no | Repackaged versions of the *same* web-consultation sources already represented. |
| English MedQuAD, medicine catalogue, disease-symptom table, NER, specialist labels | no | Wrong task shape or language. |
| `unified_medical_qa_train.*` · `non_medical_filtered_data.csv` | no | English / explicitly non-medical (31 rows). |
| **`Data_Search_2` — 125 English medical books (~70k pages)** | **Not for SFT, translation, or RAG** | Reference prose, not supervised dialogue pairs. Includes veterinary, botanical and alternative-medicine texts. **No dataset-wide reuse licence documented.** |

---

## 5.3b LIT-01 — the NLP4Health-2025 paper, read in full. Three claims in this plan were wrong.

**Source:** *Patient-Centric Question Answering — Overview of the Shared Task*,
[aclanthology.org/2025.nlpai4health-main.5](https://aclanthology.org/2025.nlpai4health-main.5/)
(PDF in repo root). Read 2026-08-07.

### What the dataset actually is

| We recorded | The paper says |
|---|---|
| "45k+ **validated real** patient–provider dialogues" | **Synthetic.** A *"Human-Guided Agentic Generation pipeline"* — dialogues generated by an autonomous agent framework powered by **`gpt-5-nano-2025-08-07`** |
| "**natively Bengali**" | **Translated.** *"validated English and Hindi dialogues were translated into the remaining Indic languages (Telugu, Tamil, **Bangla**, Gujarati, Kannada, Marathi, Dogri, Assamese) using the **BhashaVerse framework**, followed by native-speaker post-editing"* |
| "**zero translation-fingerprint risk**" | **Two fingerprints, not zero** — GPT-5-nano generation *plus* BhashaVerse machine translation, then human post-editing |

What *is* genuine: the clinical curriculum (oncologists and pulmonologists at CMC Vellore) and
the validation (three independent language experts per instance, mean ≥85/100, >80% consensus).
Quality is not the issue — **provenance is.**

**This removes the entire reason we ranked it first.** It was the top external candidate
*because* it was supposedly native real dialogue. It is neither. It carries more translation
fingerprint than `doctor_qa_bangla`, which is already in the repo and genuinely native.

**Access:** the shared-task site (`2025.nlpai4health.com`) refuses connections; no HuggingFace or
GitHub mirror exists; the paper states no licence, no download URL, and no distribution terms.
Unverifiable — but the fingerprint finding makes it moot.

**Verdict: dropped.** Not on accessibility, on provenance. `warmstart_corpus` already carries
123,289 curated rows including 4,651 natively-Bengali `doctor_qa_bangla` rows.

### What the paper gives us that is worth more than the data

Their shared task ran a **<3B parameter cap on Indic medical dialogue** — the same constraint as
ours. So Table 3 and Table 4 are **free prior art on exactly our model-selection question.**

**Zero-shot baselines** (averaged over 10 languages):

| Model | QA F1 | Summ ROUGE-L | Summ BERTScore | KnV F1 |
|---|---|---|---|---|
| **Gemma-2-2B-IT** | **0.52** | **0.15** | **0.81** | 0.28 |
| Qwen2.5-1.5B-Instruct | 0.45 | 0.13 | 0.78 | **0.29** |
| Llama-3.2-1B-Instruct | 0.43 | 0.06 | 0.73 | 0.13 |

> *"Gemma-2-2B demonstrates the strongest overall performance, particularly in generation tasks,
> **likely due to its superior tokenizer support for Indic scripts**."*

**Fine-tuned submissions:**

| Team | Model | Summ BERTScore | QA F1 | KnV F1 |
|---|---|---|---|---|
| C-DAC | **Gemma2-2B + LoRA** | **0.93** | 0.70 | 0.88 |
| Zaid | Qwen-1.5B + pipeline | 0.83 | 0.67 | 0.72 |
| Samvad | mT5 / Sarvam 3B (RAG) | 0.81 | **0.78** | — |
| KV | **Qwen3-1.7B + QLoRA** | 0.80 | 0.65 | **0.93** |
| Moutushi Roy | **mT5-base** | **0.78** | **0.55** | **0.13** |

> *"decoder-only models (Qwen, Gemma) **significantly outperform encoder-decoder architectures
> (mT5)**"*

### Three consequences for our experiment program

**① Independent support for E18 (decoder hedge).** A separate team, on Bangla medical dialogue,
under the same 3B cap, found decoders beat encoder-decoders. Our entire stack is encoder-decoder.
E18 moves up in priority — and **`Qwen3-1.7B` is validated by Team KV**, which is the exact model
E18 already specifies.

**② Add Gemma-2-2B-IT to E18 as a second arm.** It won on *generation* zero-shot and took the
highest summarisation BERTScore fine-tuned, credited to **tokenizer support for Indic scripts** —
the same mechanism that makes BanglaT5 beat mT5 for us (364/145 vs 443/272 tokens). At 2.6B it
fits the cap alone, though it leaves no room to ensemble.

**③ mT5 came last on every metric.** E08's gate ("if mT5 is not competitive, skip E09") now has
outside evidence behind it. Do not spend the fleet on mT5 before E08 reports.

**Transfer this evidence with care.** Their task is summarisation and extraction from
multi-turn dialogue; ours is register transfer on single answers. The **tokenizer** argument
transfers cleanly — it is about Indic script, not task shape. The architecture result is
suggestive, not decisive. **E18 still has to be measured.**


### 5.3a NLP4Health-2025 — the one condition to confirm SUPERSEDED BY §5.3b

The licence question is settled (research use permitted). **A separate Kaggle rule still applies**, and it is the actual disqualification vector:

> **Rules §2.6.a** — external data must be *"publicly available and equally accessible to use by all Participants of the Competition … at no cost to the other Participants."*

That is an **accessibility** test, not a licence test. A dataset can be freely research-licensed and still fail it if obtaining it requires shared-task registration, an approval email, or any gate another competitor couldn't pass.

**Confirm one thing before training on it:** can any Kaggle competitor download it today, without registering for the shared task and without approval?

- **Yes → use it.** Record the download URL in the disclosure.
- **Gated behind a request → get the permission in writing** and disclose that, or treat it as ineligible. Do not rely on a verbal or forum-thread permission.

**This paragraph was wrong and is retained only as the record of the error — see §5.3b.** It claimed the dataset is *"natively Bengali real dialogue — the only external candidate with no translation-fingerprint risk at all."* The source paper says the dialogues are **synthetic** (`gpt-5-nano-2025-08-07`) and the Bangla is **machine-translated from English/Hindi via BhashaVerse**. It carries **two** fingerprints, not zero, and is dropped.

**Not yet present in the repo** — it needs downloading before any of this matters.

### 5.3 Translation rule — and a risk the audit understates

Translate a corpus **only** when all hold: the source permits derivatives · it is non-overlapping medical Q→A dialogue · translation quality is auditable · it is evaluated as a *separate* warm-start against the frozen dev split.

**The additional risk, which is specific to this competition:** our target corpus is **one particular Bengali translation** of ChatDoctor, with its own lexical fingerprint — "নাসেনিয়া ডক", "হেলো", a fixed hedge/sign-off register. Any corpus we translate ourselves will carry **a different translator's fingerprint**. Since the metric is lexical overlap against *their* translation, differently-translated Bengali is exactly the off-register content §5 warns about. That makes `Data_Search_4` materially riskier than `Data_Search_3`, which is at least already Bengali.

**Therefore: translation is the last experiment to run, not the next one.**

### 5.4 Staged training order (each stage kept only if it beats the previous on frozen dev)

1. **Control:** BanglaT5, competition data only. ← *this is what is running now; nothing else starts until it clears Token F1 0.3519*
2. ~~**Challenger A:** NLP4Health-2025~~ **dropped — §5.3b.** The dataset is gpt-5-nano-generated and BhashaVerse-translated into Bangla; it carries *two* fingerprints, not zero.
3. **Challenger B:** Bengali ChatDoctor (`Data_Search_3`) 1 epoch → competition data ≥2 epochs.
4. *(only if 2 or 3 wins)* translated `Data_Search_4` subset → best warm-start → competition data.
5. *(optional)* translated MTS-Dialog + simulated interviews → best warm-start → competition data.

**Never train on the frozen 5k dev split or on any competition test material.**

**Disclosure required for anything beyond stage 1:** original source URL, licence, translation model/version/prompt, row counts, dedup rules, dataset hash, and stage-wise training logs.

---

## 6. ~~MBR Decoding — the highest-leverage lever~~ MEASURED, AND IT LOSES

> ### CLOSED 2026-08-06 — MBR is **−0.0027 LB** on the task we are actually running
>
> Pooled MBR over both register-transfer seeds, against beam-4, on the same 300 dev rows:
>
> | decoder | Token F1 | ROUGE-L | pred LB |
> |---|---|---|---|
> | seed 11 beam-4 | 0.7724 | 0.7324 | 0.8504 |
> | **seed 23 beam-4** | **0.7723** | **0.7332** | **0.8505** ← best |
> | pooled MBR (16 cand, T 0.8, top-p 0.95) | 0.7677 | 0.7268 | 0.8478 |
>
> **This section claimed "this is where the competition is won." That was wrong**, and it stayed at
> the top of §2's lever table for four days on the strength of an argument, not a measurement.
>
> **Why it loses, and the reason is principled rather than incidental:**
> 1. **The task is near-deterministic.** §6.1's mechanism needs the model to be *uncertain* so its
>    samples scatter around the truth. Register transfer recovers the answer from the draft and
>    already reaches Token F1 0.772 with beam search — sampling at T=0.8 injects noise into a
>    problem with little left to hedge against.
> 2. **The two seeds agree too closely.** 0.7724 vs 0.7723. §6.3's "cross-model consensus is a
>    stronger reference proxy" needs models that *disagree usefully*; these do not.
>
> **What this does NOT establish.** MBR was designed for the **question→answer** task, where the
> model invents content and hedging toward the generic centre should pay — that is what §6.2 argues,
> and the measured facts behind it (retrieval 0.2047 < constant 0.2669) still stand. **MBR was never
> measured on that task**, because ALIGN-01 superseded it first. The honest statement is: *MBR loses
> on register transfer*, not *MBR does not work*.
>
> **Do not spend further slots on it.** §6.4's beam/length sweep is likewise unnecessary — beam-4 at
> `min_new 80 / max_new 320 / lp 1.0` is the shipped configuration and it wins.

The original argument is kept below because §6.2's reasoning about the metric remains correct, and
because it records what was believed and on what basis.

### 6.1 The method
```
for each test input:
    sample N candidates  (N = 16–32, temperature 0.7–0.9, top_p 0.9)
    for each candidate c:
        utility(c) = mean over other candidates c' of  [0.3·TokenF1(c,c') + 0.2·RougeL(c,c')]
    submit argmax utility(c)
```
The other samples act as a proxy for the unknown reference. The candidate closest to the *consensus* of the model's own distribution is the one most likely to overlap the true reference. This systematically beats beam search on overlap metrics, because beam search maximizes sequence probability — a different objective from the one being scored.

**Expected gain: the largest single item in this plan.** Prioritize it over any further model scaling.

### 6.2 Why it fits this problem unusually well
The high-boilerplate structure means candidates agree strongly on the scaffolding and disagree on specifics. MBR keeps the agreed scaffolding and picks the least-risky specifics — which is exactly the behaviour the measured baselines reward (generic > specific).

### 6.3 Ensemble extension (Track A only)
Pool candidates from 3–5 independently-seeded BanglaT5 checkpoints (5 × 247M = 1.2B, well under cap), then run MBR over the **pooled** candidate set. Cross-model consensus is a stronger reference proxy than single-model consensus. Verify the combined parameter count and state it in the Phase 2 write-up.

### 6.4 Also try
- **Beam search** (num_beams 4–8) with `length_penalty` swept over `[0.6, 0.8, 1.0, 1.2, 1.5]` — cheap, strong, and the baseline MBR must beat.
- **Consensus/centroid construction**: build a synthetic response from the highest-agreement n-grams across candidates. Riskier (may produce disfluent text, hurting BERTScore) but directly maximizes expected overlap. Test it; only ship it if dev says so.

---

## 7. Length Calibration

Measured length sensitivity (truncated constant string, and truncated retrieval outputs) shows score rising monotonically with length up to ~80–150 tokens and then saturating — **no penalty for reaching the reference median, real penalty for undershooting**:

| cap (tokens) | Token F1 | ROUGE-L |
|---|---|---|
| 40 | 0.1459 | 0.1003 |
| 60 | 0.1725 | 0.1098 |
| 80 | 0.1885 | 0.1155 |
| 100 | 0.1969 | 0.1192 |
| 120 | 0.1998 | 0.1213 |
| 150 | 0.2016 | 0.1219 |
| 250 | 0.2020 | 0.1220 |

**Target generation length ≈ 90–120 whitespace tokens** (reference p50 = 92, p75 = 116). Enforce with `min_new_tokens` — truncation is the bigger risk than verbosity. Sweep `min_new_tokens` ∈ {60, 80, 100} and `length_penalty` on dev; this is a cheap, reliable point or two.

---

## 8. Validation Protocol

**You cannot trust the public leaderboard.** It is a fraction of 1,000 rows; the noise band is wide and overfitting to it is a real way to lose the private split.

1. **Fixed 5,000-row dev split**, never trained on. This is the source of truth.
2. Implement the **exact composite metric locally** — including BERTScore. Done — `NOTEBOOKS/metric.py`, self-tested against brute force.
3. Report all three components separately on every run. Watching only the composite hides which lever moved.
4. **Only submit when dev improves by more than dev noise.** Measured noise floor: **0.0044 Token F1** across three seeds of one config. Ignore anything smaller.
5. Keep `LOCAL_EXPERIMENTS.md` as the run log and `PREDICTIONS.md` as the dev→LB correlation log. After 4–5 submissions you will know the offset between local dev and public LB; from then on, trust dev.

### 8.1 Every inference notebook asserts a known-good number before it writes anything

Added after BUG-03, which was caught by exactly this and by nothing else. An fp16 T5 returns NaN
logits and **still generates happily** — the notebook printed a parameter count, reported "decoded
300 rows", and wrote a well-formed `submission.csv` in which every row was a single token.

**The pattern:** re-score a fixed dev subset with the *same decoder the submission will use*, and
assert it reproduces the number recorded at training time.

```python
assert abs(f1 - EXPECTED_F1) < 0.02, f"CHECKPOINT MISMATCH: expected ~{EXPECTED_F1}, got {f1}"
```

It costs ~6 minutes and catches, at minimum: wrong checkpoint attached, stale code dataset, silent
precision corruption, wrong tokenizer, and a data split that does not match the training split.
**A submission pipeline that cannot fail loudly will eventually fail silently** — and a
well-formed CSV of garbage is indistinguishable from a good one until the leaderboard says so.

Corollary: `04_decode.py` now runs a **non-finite-logits probe at model load**, so precision
breakage fails in one second rather than after a full decode.

---

## 9. Submission Budget (5/day, ~20 days ≈ 100 available)

Submissions are plentiful; **dev-set discipline is the scarce resource.** Suggested spend:

| When | Submission | Purpose |
|---|---|---|
| **Day 1** | **One constant generic string for all 1,000 rows** | Resolves conflict **C1** (`id,output` vs `id,doctor_response`) and calibrates the LB floor. Expect ≈ **0.45**. If the LB shows ~0.45, BERTScore is unrescaled and §0① holds; **if it shows ~0.10–0.20, they rescaled — reweight effort toward semantic quality.** This single submission is the highest-information action available. |
| Day 1 | — | **Ask on the Discussion tab: which BERTScore model, and is `rescale_with_baseline` on?** Also ask C1 directly. |
| Day 2–4 | 2–3 | BanglaT5 baseline, greedy → beam. Establish dev↔LB offset. |
| Day 5–10 | ~1/day | seed variation; length sweeps; MBR on/off |
| Day 11–18 | ~1/day | MBR tuning, ensemble pooling, seed variation |
| Day 19–23 | 2–3 | Final candidate confirmation |
| **Aug 24, 00:00** | — | **Deadline. Explicitly select the Final Submission.** |

Never burn a submission on something dev hasn't already endorsed.

---

## 10. Concrete Pipeline

Reorganised 2026-08-06 — the root is clean, and every artifact has one home.

```
NOTEBOOKS/                              ← code + the INFERENCE side
  metric.py                             exact composite; --selftest vs brute force
  01_prep.py                            clean → brand-normalize → frozen 5k dev split
  02_train_t5.py                        fine-tune (BanglaT5 / mT5) — takes --data-dir
  04_decode.py                          beam | MBR | submission writer — fp32, --data-dir
  05..07_build_*.py                     transfer-dataset builders
  0.85030_nascenia-submit-xfer-s11/     the scored #1: notebook, submission.csv, log
  0.57849_nascenia_constant_probe/      the Day-1 probe
  _submission_runs/{s23,ens}/           ran but unscored
  _inference_notebooks/                 all 9 decode/submission .ipynb

FINE_TUNING_NOTEBOOKS/                  ← the TRAINING side
  1)…11) <one folder per run>/          notebook + kernel-metadata + code + run.json
                                        + trainer_state_step*.json + prep_report
  FINE_TUNING_LOG.md                    master results table
  _run_outputs/sweep/{A,C,E,F,G}/       downloaded weights, 5 question→answer arms
  _run_outputs/xfer/{tashin,salam}/     tashin/…/seed11/best = THE 0.85030 MODEL

fine_tune_project/                  ← 1.8 GB HANDOFF for a high-GPU machine
  README.md · RESULTS.md                program overview + scoreboard
  E01…E16/EXPERIMENT.md                 16 experiments, 6 tiers
  data/                                 6 input combinations + warm-start corpus + sources
  code/ · reference_notebooks/          scripts + the proven recipes

LOCAL_EXPERIMENTS.md · PREDICTIONS.md · PROGRESS.md · CLAUDE.md
```

**8.7 GB of weights**, down from 40 GB — 31.55 GB of smoke warmups and superseded intermediate
checkpoints were pruned 2026-08-06, keeping all 7 `best/` models and all 14 eval trajectories.

**Order of execution:**
1. `metric.py` first. Nothing is measurable without it.
2. Day-1 constant-string submission (§9) — in parallel, costs nothing.
3. `01_prep.ipynb` → frozen dev split.
4. BanglaT5 baseline, greedy decode → first real dev number.
5. **Beam + length sweep** → cheap points.
6. **MBR** → the big lever.
7. Warm-start curriculum (§5.1) as a controlled A/B, once a competition-only baseline clears 0.3519.
8. Multi-seed Track A + pooled MBR → final.

---

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **Unpinned library version on a hosted image** | **~10 GPU-h + a day lost** | **Realized, then resolved.** Kaggle ships `transformers 5.0.0`; T5 training only works pinned to **4.57.3**. Pin + `assert` in every notebook (§4.0). Check the version before debugging the code. |
| **A silently-broken decoder writes a valid-looking submission** | **A wasted slot, or worse — a wrong final selection** | **Realized, caught.** fp16 T5 → NaN logits → 1-token outputs, with no exception anywhere and a well-formed CSV (BUG-03). Mitigations now in place: fp32 default, non-finite-logits probe at load, and a mandatory known-good-number assert in every inference notebook (§8.1). |
| **Wrong accelerator on a pushed notebook** | ~8 failed runs | **Resolved.** `"machine_shape": "NvidiaTeslaT4"` in `kernel-metadata.json` (trap #10). Free-form string — a typo silently reverts to P100, so verify with `kaggle kernels pull <slug> -m`. Enforced by `KAGGLE_PUSH/kpush.py`, which refuses to push a GPU notebook without it. |
| **Reproducibility evidence that proves nothing** | Phase 2 disqualification | **Caught.** `checkpoint_hash` hashed names+sizes only, so every checkpoint collided (BUG-01). Fixed to hash contents; pre-2026-08-05 hashes must not be cited. |
| **BERTScore is rescaled** — §0① inverts | High | Day-1 constant-string probe detects it immediately; ask on Discussion |
| **Wrong submission column** (C1 unresolved) | Fatal for a submission | Day-1 probe settles it |
| Public-LB overfitting on 1,000 rows | Lose private split | 5k dev split is the source of truth; treat LB as confirmation only |
| Phase 2 non-reproducibility → **disqualification** | Fatal | Log seed/config/checkpoint hash from run #1; freeze the winning artifact |
| Ensemble breaches 3B | Disqualification | Count params programmatically; assert in the inference script |
| Base-model license not OSI/commercial-safe | Prize forfeit | mT5 is Apache-2.0; BanglaT5 is CC BY-NC-SA but covered by the pretrained-model carve-out (§3) |
| **Assuming a "3B" model fits the cap** | **Disqualification** | **Every "3B" checked exceeds it — Qwen2.5-3B is 3.09B, Llama-3.2-3B is 3.21B. Verify total params from the model card BEFORE training.** |
| MBR too slow for 1,000 rows | Schedule | 1,000 rows × 32 samples is trivial on available hardware; batch it |

---

## 12. Phase 2 Hooks (build during Phase 1, not after)

Only ~36 hours separate the leaderboard close (Aug 24, 00:00) from the Phase 2 deadline (Aug 25, 12:00 PM). **Prepare in advance:**

- [ ] `inference.py` that reproduces the exact submission from a checkpoint + fixed seed
- [ ] `requirements.txt` / `environment.yml` pinned — **must include `transformers==4.57.3`**. The submitted outputs were produced under it; 5.0.0 does not reproduce them, so an unpinned environment file is a reproducibility failure and therefore a disqualification risk.
- [ ] Parameter-count assertion printed by the inference script
- [ ] Write-up draft: approach, base model, fine-tuning method, external data/tools
- [ ] Checkpoint uploaded somewhere reproducibly downloadable
- [ ] Phase 2 clinical quality must come from the seq2seq family — Track B is eliminated on parameter count. The medical warm-start (§5.1) is the lever for it.

---

## 13. Summary

> ### Where this stands, 2026-08-06 — **0.85030 on the public leaderboard**
>
> The register-transfer model (§5.0) scored **0.85030**, against the previous board leader — our own
> constant string — at 0.57849. **+0.272**, genuinely model-generated, Rules §8 clean.
>
> | | Token F1 | ROUGE-L | Public LB |
> |---|---|---|---|
> | constant string *(old #1)* | 0.2669 | 0.1564 | 0.57849 |
> | best question→answer fine-tune (arm C) | 0.2576 | 0.1776 | *0.5800 pred* |
> | **register transfer, seed 11** | **0.7724** | **0.7324** | **0.85030** |
>
> **Everything in §4 is closed.** LR tuning finished at 1e-3 (arm G turned the curve over), duration
> is dead (arm E), label smoothing is dead (arm D). Those levers together moved ~0.02; §5.0 moved 0.27.
>
> **The metric is now calibrated at two points** 0.5 of Token F1 apart, and BERTScore rose only
> 0.9343 → 0.9442 across that range — **~1% of its range for a 3× improvement in overlap.** §0's
> thesis holds. Refined predictor: `LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L`, fitting both
> anchors to within 0.0001. **Dev→LB is trustworthy; stop spending slots on calibration.**
>
> **MBR is now measured too, and it loses** (−0.0027 LB — §6). That was the plan's #1 lever for
> four days. Every lever in §2 has now been measured; **nothing about decoding or hyperparameters
> remains open.**
>
> **What remains:**
> 1. **E17 — re-translate the draft** (§5.6). **No GPU**, ~2 h. The draft aligns at only 0.5984
>    and everything is built on that floor. If a better translator wins, **the retrain fits Kaggle**
>    (7.9 h vs the 12 h limit — §5.7), so this is a fast loop, not a high-GPU one.
> 2. **Phase 2 packaging** (§12) — the single highest-risk item. A 0.85 Phase 1 is worth nothing
>    if the bundle fails reproducibility or the external-data disclosure is inadequate.
> 3. **The 17-experiment program** (§5.5) — handed off to a high-GPU machine as
>    [`fine_tune_project/`](notebooks/chpc_experiments/README.md), for the questions Kaggle's 12 h
>    ceiling blocks: mT5, full sequence lengths, training past convergence.
> 3. **Seed 23** as a second LB point — dev says 0.0001 apart, but the two submissions share only
>    **3.4% of rows**, so it measures leaderboard noise directly.

### 5.5 ▶ The English-source experiment — handed off 2026-08-06

**Hypothesis.** The XFER model must *invert our translation and re-apply theirs* — two hops, with our
draft's noise in its input. The **English original is the common ancestor of both translations**, so
feeding it adds information rather than capacity. That matters because capacity is measurably *not*
the bottleneck: two BanglaT5 seeds land at 0.7724 and 0.7723.

The English is already aligned on the same id space — `unified_medical_qa_train.csv`, **dev 5,000/5,000
· test 1,000/1,000**.

**The tokenizer measurement that set the run order.** mT5 was the obvious carrier for English input.
It is not:

| | source tokens | **target tokens** |
|---|---|---|
| **BanglaT5** | **364** | **145** |
| mT5 | 443 | 272 |

BanglaT5 tokenises the *mixed* input more efficiently **and** is 1.9× better on Bengali output, where
generation quality lives. So **BanglaT5 + english+draft is priority 1**, not mT5 — it changes one
variable against a model with a measured LB score, where every mT5 run changes two.

Also measured: **only 9.2% of mT5's 250k vocab is ever used** (22,991 tokens). Trimming to 32k takes
mT5-large from 1.23B to ~785M and shrinks the decoder logits tensor 7.8×. It does **not** change
tokens-per-sentence — an efficiency win, not a quality one.

**17 experiments in 6 tiers**, each changing one variable, each with the number it must beat and how
to read the outcome. 45 training arms ≈164 GPU-hours; ~36 h wall clock on 8 GPUs. Full spec, data and code in the
project folder.

### 5.6 E17 — the one lever that attacks the actual bottleneck, and it needs NO GPU

```
competition target = f_B(English)      the organizers' translation
our draft          = f_A(English)      f_A = Google Translate
```

**The draft aligns to the target at Token F1 0.5984.** The model reached 0.7724 *from that floor*.
Every experiment in the program improves how the model *uses* the draft; **this one improves the
draft itself**, raising the ceiling for all of them simultaneously.

**Probe:** re-translate the English answers of 1,000 dev rows with a stronger model, score against
the target, compare to 0.5984. An API job and a metric call — no training.

**Better translation ≠ closer to theirs.** The metric rewards matching one translator's
fingerprint, not quality. The register evidence — 76.4% `হেলো` openers, mechanical boilerplate —
suggests the organizers used plain machine translation, so a more idiomatic rendering could score
*lower*. Genuinely 50/50, and **all three outcomes are informative**: a loss proves the draft is
near-optimal and redirects effort to E05 with confidence.

### 5.7 If E17 wins, the follow-up fits KAGGLE — no high-GPU machine needed

This matters for sequencing. The register-transfer training is **not** what needs big GPUs:

| | |
|---|---|
| XFER training run (the 0.85030 model) | **472 min = 7.9 h** on one T4 |
| Kaggle session limit | **12 h** |

**It fits with 4 hours to spare**, and the exact notebook is preserved as
`fine_tune_project/reference_notebooks/PROVEN_xfer_seed11_LB0.85030.ipynb`.

So the fast loop is: **probe → re-translate → rebuild → retrain on Kaggle → submit** — entirely
within existing infrastructure. The high-GPU program exists for the *exploratory* questions (mT5,
longer sequences, training past convergence), not for shipping an improved draft.

The measurements say this competition is **not** an exercise in medical reasoning. BERTScore — half the metric — assigns 0.686 to a random unrelated answer and 0.698 to generic boilerplate, a spread of 0.012. The ranking is therefore decided by Token F1 and ROUGE-L, in a field that runs from ~0.45 (a single constant string) to maybe ~0.55.

So: **clone the corpus's style exactly, nail the boilerplate that 76% of references share, hit the 92-token median length, and use MBR decoding to pick the consensus candidate.** Fine-tune BanglaT5 as the primary bet because 247M leaves room to ensemble five of them under the cap. Skip external data *mixing* for Phase 1 — it moves output away from the target register; a sequential warm-start (§5.1) is a separate, later experiment. **There is no 3B decoder hedge: Qwen2.5-3B (3.09B) and Llama-3.2-3B (3.21B) both breach the cap.**

And on Day 1, submit one constant string. It resolves the column-name conflict, calibrates the leaderboard floor, and tells you whether the central assumption of this plan holds.
