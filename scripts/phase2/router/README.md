> ⚠️ **Repo note — the headline result below is RETRACTED.** ROUTER-01's "~88% of rows recovered, within 0.006 of a perfect lookup" was measured with a leak: the leak control compared ChatDoctor ids (`hcm_0`) with competition ids (`17200`), matched nothing, and so let every dev query retrieve its own answer (BUG-10). Re-measured leak-free ([`validate_router_leakfree.py`](validate_router_leakfree.py)), ChatDoctor content-match serves 2.6% of rows at the wrong-match floor (Token F1 0.19–0.21). The shipped router dropped it and retrieves from the ai-medical-chatbot corpus instead (0.6257 on rows whose ids do not resolve). See [`PROGRESS.md`](../../../PROGRESS.md), 2026-08-23 (later). The generated `inference_routed.ipynb` is [`notebooks/phase2_submissions/01_routed_inference/`](../../../notebooks/phase2_submissions/01_routed_inference/). The text below is kept as written.

# router/ — the three-branch router

**The measured result: content matching recovers the champion's input for ~88% of rows that have
no usable id, at 98.07% precision — landing within 0.006 Token F1 of a perfect id lookup.**

---

## Why this exists

The champion (BanglaT5, LB **0.89552**) does *register transfer*. It is handed an English
ChatDoctor answer plus our own Bengali translation of that answer, and rewrites them into the
organizers' register. **It cannot answer a question from scratch** — measured at Token F1
**0.1235** when given only the raw question (`PHASE2-GEN-01`).

Getting it that input has always depended on the competition `id` being a row index into the
public ChatDoctor corpus (ALIGN-01). That covers **100% of Phase 1's test.csv**. Phase 2 is the
organizers' private judging set, so those ids may not resolve.

**But the competition uses only 109,954 of the corpus's 112,165 rows.** The other **2,211 are
held back, and they are scattered — 4, 36, 165, 202, 279 … — not a contiguous tail.** That is the
signature of a random ~2% holdout. And we hold Bengali translations of **2,211 / 2,211** of them.

So a Phase 2 row may well *be* a ChatDoctor case whose id merely does not resolve. Matching on
**content** recovers the draft the champion needs.

## The branches

```
id resolves                  →  champion                        (Phase 1: 100%)
no id, cosine ≥ τ            →  champion, recovered draft        (~88% at τ=0.40)
below τ                      →  Phase 2 specialist               (genuinely novel rows)
```

## Measured — 1,000 frozen dev rows, ids discarded

Reproduce with `python validate_router.py --repo-root ../..`

**Ceiling (perfect id lookup): draft Token F1 `0.5963`.**

| τ | routed to champion | match accuracy | recovered draft F1 | vs ceiling | to specialist |
|---|---|---|---|---|---|
| 0.00 | 100.0% | 93.90% | 0.5705 | −0.0258 | 0% |
| 0.35 | 94.1% | 96.49% | 0.5830 | −0.0133 | 5.9% |
| **0.40** | **88.0%** | **98.07%** | **0.5901** | **−0.0062** | 12.0% |
| 0.45 | 77.1% | 99.09% | 0.5924 | −0.0039 | 22.9% |
| 0.50 | 62.0% | 99.35% | 0.5927 | −0.0036 | 38.0% |

**Default τ = 0.40.** Near-ceiling quality on the large majority of rows, with a clean fallback.

### 🔴 Why the threshold is not optional

| | draft F1 | mean similarity | n |
|---|---|---|---|
| correct match | **0.5959** | 0.549 | 939 |
| **wrong match** | **0.1795** | 0.362 | 61 |

A wrong match costs **~0.42 Token F1** — the champion fluently and confidently answering a
*different patient's* question. The two populations separate on similarity, which is what makes
gating work. **Rows below τ must go to the specialist, not be force-matched.**

This also means the router is **self-protecting**: if Phase 2 turns out to be genuinely novel
non-ChatDoctor content, similarity comes in low and everything routes to the specialist
automatically. Nothing is lost by having built it.

## Why retrieval beats a bigger model here

Measured alternatives for a Phase-2 row, on the same scale:

| approach | Token F1 |
|---|---|
| champion given only the raw question | 0.1235 |
| + live NMT translation into its template | 0.1454 |
| Bangla-AI-1.7B zero-shot | 0.1564 |
| Qwen3.5 specialist *(submitted, LB 0.57249)* | ≈ 0.21 |
| **content-match → champion** | **≈ 0.59 draft → ~0.83** |

Generation-from-scratch caps around 0.12–0.21 because reconstructing *one specific translator's*
answer is not learnable from more medical text. Retrieval sidesteps that entirely: the champion
doesn't need to know medicine, it needs the right draft.

## Parameter cost: zero

The retriever is **char-ngram TF-IDF — not a neural model**, so it adds **0 parameters** to the
3B cap. A dense retriever (`multilingual-e5-base`) would have cost 278M for a likely-small
accuracy gain. Worth re-measuring if a dense index is ever wanted, but TF-IDF is the better
default here.

## Files

| file | what it does |
|---|---|
| `router.py` | the `Router` class — importable, plus a CLI for routing a file |
| `validate_router.py` | reproduces the tables above on the frozen dev split (no GPU needed) |
| `build_inference_nb.py` | generates the submission notebook — **edit this, not the .ipynb** |
| `inference_routed.ipynb` | 🥇 **the submission notebook.** One swappable `INPUT_PATH`, handles all three branches |

## Using the notebook

Organizers change **`INPUT_PATH` in cell 1** and Run All. It needs, attached as datasets:

- the champion checkpoint (`best/` with `config.json`)
- `bengali_medical_train_clean.csv` — our Bengali ChatDoctor translation
- `unified_medical_qa_train.csv` — the English ChatDoctor source
- *(optional)* a Phase-2 specialist checkpoint for branch 3

Without a specialist attached the notebook **degrades gracefully** — below-threshold rows fall
back to the champion's best-effort match with a loud warning, rather than emitting empty rows
that would fail validation and score zero.

## Disclosure

Branch 2 uses the same public ChatDoctor corpus and team-produced Bengali translation already
disclosed for Phase 1 (ALIGN-01). **The draft is an input to the model, never copied to the
output** — every submitted row is model-generated, satisfying Rules §8.
