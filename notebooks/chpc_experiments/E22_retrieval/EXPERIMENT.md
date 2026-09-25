# E22 — Retrieval augmentation (RAG)

**Tier 4 — DATA · Priority: LOW for Phase 1 · HIGH for Phase 2**

## The question

> RAG won the QA track of the NLP4Health shared task. **Does it help us — and where?**

## Read this before running anything

RAG earned its reputation on the paper's **open-ended QA** task, where Team Samvad's RAG system
took the highest QA F1 (**0.78**) because it *"provided superior factual grounding, reducing
hallucinations compared to pure parametric generation."*

**Our Phase 1 task is not that task.** Register transfer is:

```
our Bengali draft  →  the organizers' Bengali answer
```

The model is **not answering a question.** The medical content is already in the draft; the job is
converting one translator's register into another's. There is no fact to retrieve and no
hallucination to ground — the facts arrive with the input.

Two further reasons to keep Phase-1 expectations low:

1. **The model has already seen every training pair.** It is fine-tuned on 101,737 `(draft, target)`
   examples. Retrieving one of those at inference shows it something it memorised. Retrieval helps
   most when a model *cannot* be fine-tuned on the corpus — which is E20's frozen teacher, not this.
2. **Retrieval already lost here once.** CLAUDE.md records char-TF-IDF retrieval at **0.2047**
   Token F1 against a fluent constant's **0.2669**. That measured retrieval as the *prediction*
   rather than as *context* — a different thing — but it is the same corpus telling us something.

**Where RAG genuinely earns its place is Phase 2** (arm C): 20% of the final score, LLM-judged on
clinical accuracy, and *that* is a QA task where grounding is exactly the mechanism that wins.

---

## Arm A — retrieval-selected in-context examples for the frozen teacher

**This is the highest-value Phase-1 arm, and it is a one-line change to E20.**

E20 stage 1 gives the teacher **20 in-context `(draft → target)` pairs drawn at random**. Replace
random with **the 20 nearest neighbours of the test draft**, by embedding similarity over training
drafts.

A frozen teacher cannot memorise the register — so unlike the fine-tuned model, it genuinely
benefits from being shown *relevant* conversions rather than arbitrary ones.

| | |
|---|---|
| Retriever | dense (`intfloat/multilingual-e5-base`) or BM25 over Bengali drafts |
| Index | **train split only** |
| k | 20, matching E20's current budget |
| Compare against | E20 stage 1 with random examples |

**Index train only.** Retrieving a dev row's own pair returns the answer and the number becomes
meaningless — the same leak that removed 6,000 rows from `warmstart_corpus`.

## Arm B — retrieval-augmented input to the fine-tuned model

Prepend the single nearest training `(draft, target)` pair to the model's input as a style exemplar.

**Expected to do nothing**, for the reason above — but it is cheap, and there is one specific case
where it could pay: rows whose draft is unlike anything in training. **Report the score split by
retrieval similarity**; a gain concentrated in the low-similarity tail would be real even if the
average is flat.

## Arm C — RAG for Phase 2 clinical QA

**This is the arm worth building.**

Phase 2 is judged by an LLM on **clinical accuracy**, not token overlap. Nothing in this program
has optimised for it, and grounding is precisely what the paper's RAG system won on.

| | |
|---|---|
| Retrieve over | `data/warmstart_corpus/` — 123,289 curated Bengali medical dialogues |
| Query | the patient question (`data/question_only/`) |
| Use | ground the answer in retrieved real doctor responses instead of generating parametrically |

**The corpus is leak-safe and must stay that way** — 6,000 rows whose ids fall in the frozen
dev/test split were removed because they are a *second translation of answers we evaluate on*.
Retrieving one would leak the eval set. Verified 0 dev-id overlap; **re-verify after any rebuild**.

**A retrieval index counts toward nothing in the 3B cap — but the retriever model does.** If
Arm C ships, `multilingual-e5-base` (278M) is added to the parameter budget alongside the
generator. Assert the total.

## How to read the result

| Arm | Result | Meaning |
|---|---|---|
| **A** | > E20 random-example baseline | Cheap upgrade to the teacher probe — adopt it |
| **A** | ≈ baseline | The teacher generalises the register from any examples; k-NN selection adds nothing |
| **B** | ≈ incumbent *(expected)* | Confirms the fine-tuned model already internalised the register |
| **B** | gain in the low-similarity tail only | Real but narrow — consider it only for out-of-distribution rows |
| **C** | fewer hallucinations / better clinical audit | **Ship for Phase 2** even at zero Phase-1 gain |

**Do not let this displace E05, E17, or E18.** The honest expectation is: **arm A a small win,
arm B nothing, arm C the real prize** — and arm C is measured by the Phase-2 audit in E16, not by
Token F1.

---

## Non-negotiables (every experiment)

- **Index the train split only** — never dev or test.
- **Never change the split**: `--seed 42 --dev-size 5000`.
- **Count the retriever's parameters** toward the 3B cap if it ships.
- **Report Token F1 and ROUGE-L**, never the local composite.
- **Ignore differences below 0.0044.**
- **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.

Record in [`../RESULTS.md`](../RESULTS.md).
