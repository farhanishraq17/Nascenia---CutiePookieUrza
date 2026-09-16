# `data/` — shared datasets

**Do not copy these into the experiment folders.** They are shared: `all_inputs` is used by E03 and
E07, `warmstart_corpus` by E12 and E16. More importantly, **seven experiments have no dataset yet** —
E05, E06, E09, E10, E11, E12 and E14 all train on *"the winner of Tier 1"*, which is not known until
E01–E04 report. They point here at run time.

Every dataset below shares the **frozen seed-42 / 5,000-row dev split** and has **100% dev/test
coverage**, asserted at build time — a row with no source cannot be predicted at all, so the builder
fails rather than shipping short.

Schema everywhere: `id · input · output` (`test.parquet` has no `output`).

## The six input combinations

| Dir | Input fields | src words (mean / p95) | Used by |
|---|---|---|---|
| `draft_only/` | our Bengali draft | 101 / 169 | **E08** — reproduces the incumbent exactly |
| `english_draft/` | english + draft | 212 / 355 | **E01**, E09 |
| `question_draft/` | question + draft | 180 / 287 | **E02** |
| `all_inputs/` | question + english + draft | 290 / 462 | **E03**, E07 |
| `english_only/` | english | 110 / 186 | **E04** |
| `question_only/` | question | 78 / 150 | **E13** — the competition's native task |

`draft_only` matters beyond E08: it is the **exact input of the 0.85030 model**, so it is the
control that makes every other number comparable.

## Two more

| Dir | What |
|---|---|
| `warmstart_corpus/` | 123,289 curated Bengali medical dialogues for the E12 two-stage curriculum. **Leak-safe** — see below |
| `_sources/` | the raw English + Bengali corpora and the frozen split, so you can build combinations that are not prebuilt |

## 🔴 `warmstart_corpus` is leak-safe and must stay that way

Its rows whose ids fall in the frozen dev/test split were **removed — 6,000 of them**. Those rows are
*a second translation of the answers we evaluate on*, so training on them leaks the evaluation set
just as surely as training on dev itself. Verified: **0 dev-id overlap**. Provenance, licences and
the full include/exclude reasoning are in `warmstart_corpus/SOURCES.md`.

If you rebuild or extend this corpus, re-run that exclusion.

## Building a combination that is not here

```bash
python ../code/09_build_inputs.py --fields q,en \
  --english _sources/unified_medical_qa_train.csv \
  --bengali _sources/bengali_medical_train_clean.csv \
  --proc _sources --out question_english
```

`--fields` takes any subset of `q` (patient question), `en` (English doctor answer), `bn` (our
Bengali draft). Field order in the input is always `q, en, bn` regardless of the order you pass —
changing it would change the experiment.

## Where these came from

The competition `id` is a row index into ChatDoctor / HealthCareMagic-100k. `en` is that corpus's
original English answer; `bn` is our own Bengali translation of it; the target is the organizers'
Bengali translation. Full provenance and the §2.6.a disclosure obligations are in
`warmstart_corpus/SOURCES.md`.
