# redemption/FINDINGS.md — Bengali medical dialogue/QA data sweep, 2026-08-17

**Why this exists:** Phase 2 uses the organizers' own private judging data — never ChatDoctor-derived,
so the `hcm_<id>` lookup that drives the current champion's Phase 1 score will never resolve there.
An inference-time fix was tested and measured (`LOCAL_EXPERIMENTS.md`, PHASE2-GEN-01) and it failed:
even a correctly-shaped, well-translated input only moved Token F1 from 0.1235 to 0.1454, because the
champion has memorized one external corpus's translation distribution, not "answer Bengali patient
messages" in general. **The fix has to be training data, not a bolted-on translator.**

**Method, in two passes:**
1. WebSearch + WebFetch across HuggingFace, GitHub, Kaggle, arXiv for anything not already in this
   repo.
2. 🔴 **A full local audit of `DATA/` itself** — this mattered more than the web search. Three prior
   sessions in this project (`Data_Search_1/SOURCES.md`, dated 2026-07-24; `Data_Search_4/SOURCES.md`
   and `Data_Search_5/MASTER_C_BENGALI/SOURCES.md`, dated 2026-08-05) already did this exact
   investigation — more rigorously, by actually loading and measuring files rather than reading
   dataset cards — and left a documented, **measured** verdict on nearly everything the web search
   turned up. Where the two passes overlap, the local audit is authoritative.

---

## 🥇 The answer, if you only read one section

**`Data_Search_5/MASTER_C_BENGALI/master_c_bengali.csv`** already contains a ready-to-use,
leak-checked, non-HealthCareMagic-ChatDoctor slice:

| source | rows | language | provenance |
|---|---|---|---|
| **icliniq** | 7,321 | EN→BN (our translation) | Real patient→doctor consultations, different site than HealthCareMagic, same translation pass so a consistent fingerprint |
| **genmedgpt** | 5,200 | EN→BN (our translation) | Real dialogue shape, short (~35 tokens) |
| **doctor_qa_bangla** | 4,651 | **native Bengali** | Zero translation fingerprint |
| **Total** | **17,172** | | Already brand-normalized, deduped, degenerate-filtered, dev/test-leak-checked |

This is filterable from `master_c_bengali.csv` by its `source` column **right now** — no download,
no translation, no license research needed. It's the natural first training-data addition for a
generalization-focused retrain. (`healthcaremagic`, 106,117 rows, is excluded from that count
deliberately — it **is** ChatDoctor/HealthCareMagic, same as `Data_Search_3`.)

Four other candidate sources were **already tried and measured as failures**, documented in
`Data_Search_5/MASTER_C_BENGALI/SOURCES.md` — do not re-attempt them without a new reason:

| source | rows | why it failed |
|---|---|---|
| `ai_medical_chatbot` | 166,193 | **Off-register, measured.** Opens `হাই`/`হ্যালো` 70.06% vs the competition references' `হেলো` 76.37%. Held, not deleted — "the last experiment to run, not the next." |
| `alpaca_health` | 1,021 | Keyword filter matched homographs — 6.4%+ of "medical" rows are computing/economics/business content mistranslated as medical Bengali. |
| `disease_db` | 796 | Wrong output shape — structured bullet lists, no doctor voice. |
| `mts_dialog` | 3,503 | Wrong task — input is a clinical note, output is the doctor's *opening line*. Inverse of what's needed. |

---

## What the web search found that ISN'T already accounted for above

### Genuinely new: additional Medical Meadow subsets, English, translation-ready

`Data_Search_1/huggingface/medical-qa-multi/` is a stub (131–134 byte LFS pointers, confirmed) for
**`Malikeh1375/medical-question-answering-datasets`**, MIT-licensed, 10 subsets. `NEW_DATASETS_D1`
already translated only the `medical_meadow_medical_flashcards` subset (33,222 rows after cleaning).
Three *other* subsets in this same collection were already flagged useful and were **never fetched
at all**:

| subset | rows | note (from `Data_Search_1/SOURCES.md`) |
|---|---|---|
| `medical_meadow_wikidoc_patient_information` | 5,942 | "Patient-facing explanations — register close to what we want." |
| `medical_meadow_wikidoc` | 10,000 | "Long-form medical prose." |
| `medical_meadow_mediqa` | 2,208 | "Consumer health QA." |
| `chatdoctor_icliniq` | 7,321 | Same iCliniq content already captured via `Data_Search_5` — **do not re-translate, would double-count.** |

~18,150 genuinely new English rows (excluding the icliniq duplicate), MIT-licensed, needing
translation. Second-priority after the 17,172 already-ready rows above.

### 🔴 Provenance trap, confirmed twice independently — MedAidDialog and IndicMedDialog

Two brand-new (Mar/May 2026) arXiv datasets, both multilingual-including-Bengali, both **synthetic
LLM-generated + machine-translated** — the exact failure mode that got NLP4Health dropped from this
project (LIT-01). `Data_Search_1/SOURCES.md` independently reached the same "deliberately not
downloaded" verdict on both, before this session's web search ever ran them down again:

- **MedAidDialog** (arXiv 2603.24132) — Llama-3.3-70B-generated, translated via TranslateGemma/TinyAya.
  CC BY-NC-SA 4.0. No public download link found by either pass.
- **IndicMedDialog** (arXiv 2605.13292) — same pattern, "verified by native speakers" (better than
  MedAidDialog, but still synthetic at the root). 🔴 **License is CC BY-NC-ND 4.0** — No-Derivatives
  plausibly forbids fine-tuning outright, independent of the provenance concern. No download link.

**Verdict stands from both passes: skip for training.** Worth knowing what these look like from the
outside, since competitors doing the same arXiv search will find them and some won't check
provenance — same mistake this project already caught once.

### `Data_Search_4` — ai-medical-chatbot — same verdict as `ai_medical_chatbot` above

The web search's "Patient–Doctor Conversation Dataset, 50k samples" and similar Kaggle hits are very
likely re-packagings of `yousefsaeedian/ai-medical-chatbot` (256,916 rows), already pulled and
audited in `Data_Search_4/SOURCES.md`: 81,170 of its rows are verbatim-input duplicates of English
ChatDoctor, the unique 166,427-row remainder is exactly the `ai_medical_chatbot` slice measured
off-register above. **Not a new source — same data under a different Kaggle listing.**

### Structured, non-dialogue finds — narrow, specific uses only

| Dataset | What it is | Use |
|---|---|---|
| **`Bangla-MedER`** (arXiv, [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13054271/)) | 2,980 expert-annotated Bangla drug/entity records (medicine name, organ, disease, hormone, pharmacological class) | RAG drug-entity grounding, not generator training — needs reformatting from NER spans |
| **`ArnobBot/Medicine-Dataset-of-Bangladesh`** | Bangladesh pharmaceutical data (dosage forms, brands), MIT, **English**. Already downloaded whole in `Data_Search_1/huggingface/Medicine-Dataset-of-Bangladesh/` (generic.csv, medicine.csv, indication.csv, manufacturer.csv — all real, not stubs) | Same use as Bangla-MedER: a real drug-facts base for RAG's medication/interaction cases |
| **`csebuetnlp/banglat5_nmt_bn_en`** | 247M-param Bengali↔English NMT, same org/tokenizer family as the champion | Already tried as the Phase 2 fallback translator — **measured, and it wasn't the fix** (PHASE2-GEN-01). Not useless — just proves the bottleneck is elsewhere. |
| **BanglaCHQ-Summ** (2,350 rows), **BanglaHealth-paraphrase** (200,000 rows) | Native Bengali, but summarization and paraphrase pairs respectively — wrong task shape for dialogue generation | Not training-pair sources for this task |

---

## Correcting one claim from the first pass of this document

The original version of this file said `susnatak/Bengali-healthcare` (47,531 rows) was "never
actually fetched." **That's wrong — it was fetched and fully inspected on 2026-07-24**
(`Data_Search_1/SOURCES.md` records exact stats: `instruction`/`input`/`output` schema, 55% empty
`input`, real character-length percentiles) **and reverted to a 133-byte git-LFS stub by 2026-08-04**,
almost certainly from a later `git clone` that didn't pull LFS content — every file under
`Data_Search_1/huggingface/` carries the identical `Aug 4 00:17` timestamp, consistent with one bulk
event, not gradual corruption. `Data_Search_1/SOURCES.md`'s own July verification already flagged the
caveat that matters most: **"much of it is translated general-purpose Alpaca content, not clinical —
filter before use."** Same register risk as `alpaca_health` above. Lower priority than the
ready-now 17,172-row slice, and needs the same filtering step before it's worth re-fetching.

---

## Recommendation, given the time left

1. **Use the 17,172-row `master_c_bengali.csv` non-HealthCareMagic slice first** — zero new cost,
   already leak-safe, already register-measured. This is the natural training-data input for the
   mixed-regime retrain PHASE2-GEN-01 points at.
2. **Fetch the three uncaptured Medical Meadow subsets** (~18,150 rows, MIT) if more volume is
   needed — translate with the same pipeline already used for `NEW_DATASETS_D1`.
3. **Do not re-attempt MedAidDialog, IndicMedDialog, `ai_medical_chatbot`, or `Bengali-healthcare`
   unfiltered** — all four have a documented, measured, or license-based reason they were already
   rejected or deprioritized.
4. **`Bangla-MedER` and `Medicine-Dataset-of-Bangladesh`** are RAG-grounding candidates, not
   generator training data — separate track, lower urgency than the retrain itself.
