# EXPERIMENTS — the matrix

> **This file describes the complete matrix, not necessarily the plan you should launch.**
> **You have 5 days** (Phase 2 due Aug 25, 12:00 GMT+6), and decoders cost **15–35× more per step**
> than the seq2seq model. **Read `GPU_BUDGET.md` first** — it has measured throughput from this
> project's own runs, three config changes that cut cost at no scientific cost, a priority order
> for what to drop, and the gate for cutting model **C**. Budget the wall clock against your own
> fleet before launching all of this.

**X0–X7 run for every model.** The whole point is a fair three-way comparison, so an arm skipped
for one model and not another makes the comparison worthless.

**D1–D3 run on `A_mT5_base` AND `B_Qwen35_2B`** — one seq2seq, one decoder-only. They answer a
*data* question, and running them on two different architectures makes them a **cross-check**:

| A and B... | Conclusion |
|---|---|
| **agree** | The data verdict is architecture-independent — **C inherits it**, no re-run needed |
| **disagree** | Data effects *are* architecture-specific. A real finding — say so, and run D1–D3 on C too before trusting its X2 |

`C_BanglaAI_17B` does **not** run them up front, and should only do so if A and B disagree.

**The bar every arm is measured against: Token F1 `0.1454`** — the best any inference-time-only
fix achieved on the frozen champion. **Noise floor: `0.0044`.** Ignore smaller differences.

---

## The matrix

| ID | Name | Trains? | Data | What question it answers |
|---|---|---|---|---|
| **X0** | Zero-shot | no | — | What does this base model do with no help at all? |
| **X1** | Few-shot (k=4) | no | train pool | Does prompting alone get anywhere? |
| **X2** | **Fine-tune, plain** | yes | `data/plain/` | The primary arm. Can it learn to answer? |
| **X3** | **Fine-tune + RAG** | yes | `data/rag/` | Does a retrieved reference case, *trained in*, beat plain? |
| **X4** | Data ablation | yes | `data/plain_core_only/` | Do the extra 17k non-competition rows help, or is competition-only enough? |
| **X5** | LR sweep | yes | winner of X2/X3 | Is the default LR right for **this** model? |
| **X6** | RAG-at-inference-only | no | X2's checkpoint | Must RAG be trained in, or can it be bolted on? |
| **X7** | Decode sweep | no | best checkpoint | Cheapest remaining gain. Always run last. |

### Data decomposition — `A_mT5_base` + `B_Qwen35_2B`

| ID | Name | Trains? | Data | What question it answers |
|---|---|---|---|---|
| **D1** | + iCliniq only | yes | `plain_core_plus_icliniq` | Does the closest-register extra help? |
| **D2** | + GenMedGPT only | yes | `plain_core_plus_genmedgpt` | Does the **length outlier** hurt? |
| **D3** | + doctor_qa_bangla only | yes | `plain_core_plus_doctor_qa_bangla` | Does the only **natively Bengali** source help? |

---

## X0 — Zero-shot baseline · no training

Run the base model untouched on `dev[0:300]` with a Bengali+English system instruction (given in
each `INSTRUCTIONS.md`). ~15 minutes.

**Why it matters even though it will score badly:** it establishes what the fine-tuning actually
bought. If X2 lands at 0.45 and X0 was already 0.40, the fine-tune barely did anything and you
have a different problem than the number alone suggests.

**mT5-base is a pure pretrained seq2seq with no instruction tuning** — expect near-gibberish,
possibly empty strings or sentinel tokens (`<extra_id_0>`). That is the correct, expected result,
not a bug. Record it and move on.

## X1 — Few-shot · no training

Same, plus **k=4 real `(question, answer)` example pairs** in the prompt, drawn **from the train
split only**. Use the *same* 4 examples for every dev row (seeded, recorded) so the arm is
reproducible.

**Never draw few-shot examples from dev or test.** That is a direct leak of the evaluation set.

**Gate:** if X1 ≫ X2 for a given model, stop and investigate before trusting X2 — it almost
certainly means the fine-tune is broken (wrong LR, wrong loss masking, wrong padding side), not
that prompting genuinely beats training.

## X2 — Fine-tune, plain *the primary arm*

`data/plain/` — `input` = the patient's question, `output` = the doctor's answer. No retrieval,
no template scaffolding beyond the model's own instruction format.

This is the arm that directly tests the finding this whole folder exists for: **the champion
could not answer because it was only ever trained to restyle.** A model trained on real
question→answer pairs at convergence has never been tried at this budget.

**Budget:** do **not** guess a small step count. This project has been burned exactly once and
badly — its champion was trained for 2,750 steps under a "budget ~2,000 and stop" rule inherited
from a *different* task; when finally run properly it peaked at **12,000** and two thirds of the
available gain was sitting past the old cutoff. Set a large `max_steps`, evaluate every 250–500
steps, and let **early stopping on the composite metric** find the peak.

## X3 — Fine-tune + RAG

`data/rag/` — identical targets, but each input is prefixed with **one retrieved reference case**
(a different, similar real patient question + its real doctor answer), then the actual question.

**The point of training this in rather than bolting it on:** a model that has never seen a
reference case during training will frequently ignore it at inference. X6 tests exactly that
difference.

**Report the copy-check, and treat it as more important than the headline score.**
`shared/evaluate.py` computes, per row, the token overlap between the prediction and (a) the true
target, and (b) **its own retrieved reference**. High overlap with the reference and low with the
target means the model is *copying the example*, not answering — a failure mode that can still
produce a respectable-looking Token F1 because medical Bengali shares so much boilerplate.

## X4 — Data ablation

Re-run X2's exact config on `data/plain_core_only/` (competition `train.parquet` alone, 101,740
rows) versus the full core mix (118,912 rows incl. iCliniq + GenMedGPT + doctor_qa_bangla).

**Isolates:** does non-competition Bengali medical dialogue actually help generalization, or does
its different register hurt? This project has measured a 166k-row corpus *hurting* for exactly
this reason, so the answer is genuinely not obvious.

**If the difference is under 0.0044, prefer the smaller dataset** — faster, and less external data
to disclose.

## D1 / D2 / D3 — which extra source actually helps? *(A + B, as a cross-check)*

X4 compares *all* extras against *none*. If it comes back negative it cannot tell you **which**
source caused it — and the three are very unalike:

| source | rows | output p50 | opens `হেলো` | the concern |
|---|---|---|---|---|
| `icliniq` | 7,321 | 77 words | **0.0%** | closest to the competition's 93 — plausibly harmless |
| `doctor_qa_bangla` | 4,651 | 41 words | **0.0%** | short, but the **only natively-Bengali** source anywhere in this project |
| `genmedgpt` | 5,200 | **31 words** | **0.0%** | **a third the reference length.** The prime suspect if X4 goes negative |

**All three open with `হেলো` 0.0% of the time against the competition's 76.4%** — the same
off-register signature that got a 166,193-row corpus excluded from this project earlier. That is
why this decomposition exists rather than a coin-flip on the bundle.

Run each at **X2's exact config**, changing only `DATA`. Then read the ladder:

| Pattern | Conclusion |
|---|---|
| D1 ≈ D3 > X4, D2 < X4 | `genmedgpt`'s short answers are the problem — **drop it, keep the other two** |
| all three ≈ X4 | Extra data is neutral at this scale; **ship `plain_core_only`** — fewer sources to disclose, faster training |
| all three > X4 | Diversity genuinely helps despite the register mismatch — **ship `plain`**, and say so, because it contradicts this project's Phase 1 prior |
| all three < X4 | Off-register data hurts even for Phase 2 — **ship `plain_core_only`** and record it as a clean negative |

**Judge these against the 0.0044 noise floor, not against each other's decimals.** 17,172 rows
is 14% of the pool; the honest expectation is that most of these differences are small.

**Also record `mean_pred_tokens` for every D arm.** If the short extras hurt, the mechanism should
show up as output length dragged below the references' ~100 words. That is the diagnostic that
tells you *why*, and it may land differently on a decoder than on a seq2seq.

### The cross-check is the point — resolve it explicitly

Fill in the comparison table in **`B_Qwen35_2B/RESULTS.md`** and state a verdict:

- **A and B agree** → the data conclusion is architecture-independent. Use the winning variant for
  C's X2 as well, and do **not** spend three more runs re-deriving it there.
- **A and B disagree** → data effects *are* architecture-specific. This contradicts the assumption
  the design was built on, so **say it plainly**, and run D1–D3 on `C_BanglaAI_17B` before
  trusting its X2.

`C_BanglaAI_17B` does not run these up front — only if the cross-check fails.

## X5 — LR sweep

The defaults in each `INSTRUCTIONS.md` are the correct *class* (≈1e-3 seq2seq, ≈2e-5 decoder) but
not necessarily the optimum for this task. Sweep **3 values, one decade apart, within the class**,
on the winner of X2/X3.

**Never sweep across classes.** Putting 1e-3 on a decoder diverges and produces a run that
looks like a bad model rather than a broken one. This has already happened in this project.

## X6 — RAG at inference only *(no training)*

Take **X2's** checkpoint (trained *without* retrieval) and feed it **X3's** RAG-formatted inputs
at decode time.

| Outcome | Meaning |
|---|---|
| ≈ X3 | RAG does not need to be trained in — simpler pipeline, use X2's checkpoint + retrieval |
| ≪ X3 | Retrieval must be trained in; the model ignores or is confused by unfamiliar context |
| ≪ X2 | The extra context actively hurts an unprepared model — a clean, useful negative |

Cheap (one decode pass) and it settles a real architectural question.

## X7 — Decode sweep *(no training)*

On the single best checkpoint only. Sweep `num_beams ∈ {4, 8}` × `length_penalty ∈ {1.0, 1.2, 1.5}`,
`min_new_tokens = 0`.

Two hard-won notes from this project's own decode work:
- **`min_new_tokens=0`, always.** A stale `min_new_tokens=80` floor was silently costing **0.0134
  of leaderboard score** by padding answers past their natural end.
- **Re-verify any winner on a disjoint dev slice** (`dev[300:600]`). A sweep over 300 rows finds
  spurious winners; the champion's own decode winner was confirmed this way before shipping.

---

## What to record for every arm, in your model's `RESULTS.md`

| Field | Why |
|---|---|
| Token F1, ROUGE-L | The primary metrics. **Never the local composite** — mis-calibrated by ~0.118 |
| Full eval trajectory (step → score) | Where it peaks *is* a finding. Nothing has established whether this task converges fast or slow |
| Peak step, total steps, wall-clock | Tells the next person what budget to set |
| Mean output tokens | References ≈100. Systematically short/long output is diagnostic |
| `হেলো` opener % · `নাসেনিয়া` % | References: 76.4% / 50.0%. Near the *draft's* rates (0.06%/0.00%) ⇒ copying input. Near the references' ⇒ learned the register |
| % truncated | References are 6.8%. **6.8% is correct, not a defect** — judged against a naive 0% target every good model looks broken |
| **Copy-vs-reference overlap** (RAG arms) | See X3. The single most important RAG diagnostic |
| Exact param count | `sum(p.numel())`. Assert < 3B. Never trust the model card |
| Precision actually used, GPU | bf16/fp32 — and confirm it was never fp16 |
| Checkpoint path | **A row with a score and no checkpoint is a result that cannot be submitted without retraining** |

## Deliverables when you are done

1. Each model's `RESULTS.md`, fully filled in — including the arms that lost.
2. **Every checkpoint kept**, one directory per arm, `run.json` beside the weights.
3. A one-paragraph recommendation: **which model, which arm, and why** — including whether RAG
   earned its 278M retriever params.
4. The winning arm's `train.ipynb` and `inference.ipynb`, as actually run (not as shipped, if you
   changed them).

## If a result contradicts something in these documents

**Say so explicitly rather than smoothing it over.** Several claims in this project have already
been overturned by measurement — "budget 2,000 steps and stop", "BERTScore barely discriminates",
"the Bengali draft is the strong input", "ensembling will help". Every one was believed on good
reasoning and every one was wrong. A contradiction is a finding, not a mistake.
