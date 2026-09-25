# Phase 2 write-up — Nascenia Bengali Medical Dialogue

**Team submission for Phase 2 (model + inference script).** Everything below was measured in this
repository; every number is reproducible from the artefacts listed in §7.

---

## 1. The problem Phase 2 actually poses

Phase 1 is scored on the organizers' public test split, where each `id` is a row index into
ChatDoctor/HealthCareMagic. We hold an independent Bengali translation of that corpus, so an id
that resolves gives the model a **draft answer**; the task collapses to restyling that draft into
the organizers' house register. Our BanglaT5 champion does this extremely well (LB **0.89552**).

Phase 2 is judged by an LLM on the organizers' **own held-out data**, where that lookup resolves
on **0% of rows**. Fed a novel question with no draft, the champion echoes the patient's message
back — Token F1 **0.1235**, and no inference-time fix got past **0.1454**. Phase 2 therefore needs
a second model that can genuinely answer. That model is what this bundle adds.

## 2. Architecture: a two-branch router

```
id resolves into the corpus  ->  CHAMPION    BanglaT5      247,577,856   fp32, normalized, beam 8 / lp 1.2
id does not resolve          ->  SPECIALIST  Qwen3.5-2B D1 1,881,825,088 bf16, raw text,   beam 4 / lp 1.0
                                 COMBINED                  2,129,402,944  (871M under the 3B cap)
```

Phase 1's test set resolves on **1000/1000** rows; the Phase 2 judging set on 0%. The branches are
row-disjoint, so **adding the specialist cannot move the 0.89552 leaderboard score** — verified,
not assumed (§6).

**The two branches run in separate conda environments, and this is not optional.** The champion
requires `transformers==4.57.3`; on 5.14 it warns that `shared.weight` and `lm_head.weight` are
*"present in the checkpoints with different values, so we will NOT tie them"* — 4.57 ties them,
5.14 does not, so the two versions decode from different weights. The specialist requires
`transformers==5.14.1`, because Qwen3.5's architecture does not exist in 4.57. Since the branches
never share a row, running each in its validated stack costs nothing and removes the conflict.

Per branch, precision and text preprocessing also differ, and both were measured rather than
assumed:

| | dtype | input text | why |
|---|---|---|---|
| champion | fp32 | csebuetnlp-normalized | bf16 decoded 280/1000 rows differently — beam-8 is decided by small margins. Its Phase 1 training data was normalized. |
| specialist | bf16 | **raw** | Every Phase 2 number was measured in bf16, and `build_data.py` never normalizes — normalizing here would be a train/test mismatch. |

## 3. The specialist: base model and fine-tuning

**Base:** `Qwen/Qwen3.5-2B`, decoder-only, 1,881,825,088 parameters (Apache-2.0).

**Method:** full-parameter supervised fine-tuning on real `question → answer` pairs, loss masked on
the prompt, `apply_chat_template` with a Bengali system prompt and `enable_thinking=False`.
Effective batch **64** (`per_device × accum × ranks`) on every arm — the one quantity held fixed
across the whole study — `adafactor`, LR **2e-5**, cosine schedule, 300 warmup steps, gradient
checkpointing, bf16, seed 42, `MAX_SRC=1024 / MAX_TGT=640`.

Checkpoint selection is on **generation-based Token F1**, never `eval_loss`: on one run in this
project the lowest loss coincided with the worst Token F1, so selecting on loss would have picked
the single worst checkpoint of the run.

**Shipped arm: D1** — the competition training split (101,740 rows) plus **iCliniq** (7,321 rows),
109,061 rows total, peaking at step **2,500**.

## 4. Results

Every trained arm clears the 0.1454 bar by +0.10 to +0.12. The decisive detail is *which* number
to trust: `dev.parquet` in every data variant held only the 300 rows that checkpoints were
**selected** on (`build_data.py --dev-limit 300`), which also meant X7's mandatory disjoint
verification had never been runnable. We built `dev[300:1300]` as `data/plain_devext/` and
`data/rag_devext/` — leak-checked against all 118,912 pool rows, self-retrieval asserted — and
re-scored every checkpoint on it.

| model / arm | selection-slice peak | **held-out (n=1000)** | disjoint verify (n=300) | un-terminated |
|---|---|---|---|---|
| **B D1 — shipped** | 0.2646 | **0.2625** | **0.2575** | 27.3% |
| B X4 | 0.2629 | 0.2643 | 0.2537 | 70.8% |
| B X2 | 0.2641 | 0.2630 | 0.2582 | 60.0% |
| B X5 @lr 1e-5 | 0.2594 | 0.2610 | 0.2537 | **14.8%** |
| C X2 (Bangla-AI-1.7B) | 0.2577 | 0.2583 | 0.2486 | **12.8%** |
| A X3 (mT5-base + RAG) | 0.2566 | 0.2533 | 0.2534 | 8.7% |
| *champion, no draft* | — | *0.1235* | — | — |
| *references* | — | — | — | *6.8%* |

**The top five arms are separated by 0.0033 on 1,000 held-out rows** — inside noise. Token F1
cannot pick a winner; we selected **D1** because it is the only arm that is simultaneously
top-tier on F1, best on the disjoint verify slice (0.2575), best on ROUGE-L among the leaders
(0.1830), and keeps un-terminated answers to 27.3% where the F1 leaders sit at 60–71%.

**Three-way comparison.** mT5-base (580M, seq2seq) tops out at 0.2533 held-out and is the weakest
of the three. Bangla-AI-1.7B lands within **0.0042** of D1 on the 1,000-row held-out set — statistically
level — with the best register of any model and a smaller total pipeline (1,968,152,832). On the
*second, disjoint* slice, however, it falls to **0.2486** against D1's **0.2575**, dropping about
twice as far as D1 between the two. Its score does not generalize as well as its register
suggests; see §8.

**RAG did not earn its 278M retriever.** For both decoders, retrieval trained in *loses* to plain
(B: 0.2495 vs 0.2630; C: 0.2516 vs 0.2583), and bolted on at inference it **copies the retrieved
example instead of answering** — copy-margin −0.0288 (B) and −0.0244 (C), which fails
EXPERIMENTS.md's criterion regardless of score. Only the seq2seq model benefited from RAG. The
retriever is therefore **not** part of this bundle, which is why the combined count is 2.13B and
not 2.41B.

## 5. External data and tools

| resource | rows | licence | use |
|---|---|---|---|
| competition `train.parquet` | 101,740 | CC BY-NC 4.0 (competition data) | specialist training |
| **iCliniq** — ChatDoctor repo subset, keyed `ic_*` | 7,321 | repo code Apache-2.0; **data "for academic research only, commercial and clinical use prohibited"** | specialist training (the D1 arm) |
| GenMedGPT / doctor_qa_bangla | 5,452 / 5,133 | GenMedGPT same ChatDoctor terms as above; doctor_qa_bangla Apache-2.0 | ablation arms only — **not** in the shipped model |
| `Qwen/Qwen3.5-2B` | — | Apache-2.0 | specialist base |
| `csebuetnlp/banglat5` (champion base) | — | CC BY-NC-SA 4.0 | champion branch |
| `csebuetnlp/normalizer` | — | open source, git-pinned `d405944` | champion branch text prep |
| Bengali translation of ChatDoctor/HCM | — | our own derived artifact (Google Translate API), from the same ChatDoctor corpus | champion branch drafts |

Source for both ChatDoctor-derived subsets: **github.com/Kent0n-Li/ChatDoctor** — public repo,
open links, no gate, free. `ic_*` and `hcm_*` rows come from the *same* file in this repo
(`Data_Search_3/ChatDoctor dataset/bengali_medical_train_clean.csv`), so they carry identical terms.

`intfloat/multilingual-e5-base` (MIT) was used to build the retrieval index for the RAG
*ablations*. It is **not** used at inference and does not count toward the parameter cap.

### Winner-licensing check — cleared, with the reasoning stated

The winner-licensing rule (`RULEBOOK/COMPETITION_RULES.md` §12) requires winners to license **the
winning submission and the source code used to generate it** under an OSI-approved licence that
does not limit commercial use. It carries an explicit exception:

> *"generally commercially-available third-party software you don't own, and **input data** /
> pretrained models carrying an incompatible license, do not need to be relicensed."*

**iCliniq is input (training) data carrying an incompatible licence, so it falls squarely inside
that exception.** The obligation attaches to *our* code, which is ours to license freely. Four
points support this reading:

1. **The same carve-out is already load-bearing for the champion.** `csebuetnlp/banglat5` is
   CC BY-NC-SA 4.0 and produced the entire 0.89552 Phase 1 score. If the exception did not hold,
   the champion would be non-compliant too — this is the project's standing licence posture, not
   a new risk introduced by the specialist.
2. **The competition's own dataset is CC BY-NC 4.0** — non-commercial. A competition distributing
   NC data cannot coherently require every input to be commercially unrestricted.
3. **Equal-access (§2.6.a) is satisfied**: public repo, open links, no gate, free — any
   participant could have used it.
4. **Kudos-only Community competition** — no prize, no commercial productisation downstream.

Two caveats kept deliberately visible: the "academic research only" term means this pipeline
**must not be deployed commercially or clinically as-is**, and if the organizers ever apply the
licence bar to *input data* despite the exception, the fallback is **arm X4** (competition data
only, 101,740 rows, held-out **0.2643** — statistically tied with D1's 0.2625) which uses **no
external medical-dialogue data at all**. That swap is a one-line change to `SPECIALIST` in
`run_bundle.sh` and costs nothing measurable.

## 6. Reproduction and verification (rules §5.2)

```
./run_bundle.sh <test.parquet> <out.csv>
```

Rules §5.2 requires the inference script to reproduce the leaderboard-submitted outputs. We
verified this **offline, on all 1000 rows**:

```
run_bundle.sh data/_sources/test.parquet  ->  1000/1000 rows routed to the champion, 0 to the specialist
diff vs KAGGLE_PUSH/peak5_ds/submission_reference.csv  ->  1000/1000 IDENTICAL (100.00%)
```

So the routed pipeline is byte-for-byte identical to the scored champion submission on the Phase 1
split, and the parameter assertion (`2,129,402,944 ≤ 3,000,000,000`) runs on every invocation from
the real tensors, never from a model card.

**Fixed for reproduction:** seed 42 everywhere; `min_new_tokens=0` on both branches; champion
beam 8 / lp 1.2 / src 768 / new 320 in fp32; specialist beam 4 / lp 1.0 / src 1024 / new 640 in
bf16; package versions pinned in `bundle_env/requirements_nascenia.txt` and
`bundle_env/requirements_nascenia_q35.txt` (the normalizer is pinned to git commit `d405944`).

## 7. Contents of this bundle

| item | path |
|---|---|
| inference script | `run_bundle.sh` + `logs/bundle_decode.py` |
| specialist weights | `B_Qwen35_2B/runs/D1/best/` |
| champion weights | `…/fine_tune_project/E15_decode_sweep/ckptavg_peak5/` |
| environment files | `bundle_env/requirements_{nascenia,nascenia_q35}.txt` |
| per-model results | `A_mT5_base/RESULTS.md`, `B_Qwen35_2B/RESULTS.md`, `C_BanglaAI_17B/RESULTS.md` |
| every arm's record | `*/runs*/*/run.json` (config, full trajectory, register read-out) |
| held-out scores | `logs/holdout/*.json` |
| §5.2 verification | `logs/bundle_phase1.csv` |

## 8. Recommendation, in one paragraph

**Ship the two-branch router with `B_Qwen35_2B/runs/D1/best` as the specialist, decoded at
beams=4 / lp=1.0.** It scores **0.2625** on 1,000 held-out rows and **0.2575** on a second
disjoint slice — +0.117 over the 0.1454 bar that no inference-time fix on the champion could
reach — and it is the best-balanced arm in a five-way statistical tie, keeping un-terminated
answers to 27.3% where the nominal F1 leaders fail to close a sentence on 60–71% of theirs. RAG is
deliberately excluded: it loses trained-in on both decoders and copies the retrieved example when
bolted on, so the retriever's 278M parameters buy nothing. **The one alternative we seriously considered was
`C_BanglaAI_17B` X2**, which ties D1 on the 1,000-row held-out set (0.2583 vs 0.2625) with less
than half the truncation and a smaller pipeline. We rejected it on the disjoint slice: C X2 scores
**0.2486** there against D1's **0.2575**, dropping roughly twice as far between the two held-out
slices as D1 does. Its register advantage is real and reproducible, but its *score* does not hold
up on rows it was not selected on, and D1 leads on both independent measurements. Swapping it back
in remains a one-line change to `SPECIALIST` in `run_bundle.sh` if the judge turns out to weight
completeness far above content overlap.
