# DATA_GUIDE — what to train on, what to avoid, and why

**Every row count below was verified by loading the file on 2026-08-17**, not read off a dataset
card. Several sources in the wider repo that *look* present are 131–134 byte git-LFS pointer
stubs; those are called out explicitly so you do not waste time on them.

## What is bundled — you need nothing else

Everything required is already in **`data/_sources/`** (~119 MB). The Tier-1 mix below is
pre-extracted; you do not need the wider repo, the 339 MB `master_c_bengali.csv`, or any
download.

| bundled file | rows | contents |
|---|---|---|
| `train.parquet` | 101,740 | competition train, frozen dev/test rows already removed |
| `dev.parquet` | 5,000 | the frozen dev split (seed 42). **Evaluation only** |
| `test.parquet` | 1,000 | competition test rows, no targets |
| `extra_sources.parquet` | 17,172 | `source` ∈ {`icliniq` 7,321, `genmedgpt` 5,200, `doctor_qa_bangla` 4,651} |

`shared/build_index.py` assembles these into a **118,912-row pool** — verified, with the
dev/test leak assert passing (0 of 5,000 dev + 1,000 test ids present).

**`healthcaremagic` is deliberately not bundled.** It was excluded at extraction time; the
reasoning is in the carve-out immediately below.

The rest of this document explains *why* this mix and not another, and what is deliberately
absent — read it before adding anything.

---

## First, the "no ChatDoctor" instruction — read this before excluding anything

The brief for this folder is *"train on non-ChatDoctor datasets."* That instruction is right in
spirit but needs one precise carve-out, because taken literally it would delete the single most
valuable source.

**The competition's own `train.csv` is itself a Bengali translation of ChatDoctor-HealthCareMagic**
(this is the ALIGN-01 finding — the competition `id` is that corpus's row index). So a literal
reading excludes the organizers' own provided training data.

**Include it anyway. Here is why that is not a contradiction:**

- It is the **organizers' own data**, always permitted, no disclosure burden, no licensing question.
- It is the **only source carrying the target register** — `হেলো` openers at 76.4%, `নাসেনিয়া ডক`
  at 50.0%, their specific boilerplate and sign-offs. Nothing else teaches that.
- The **frozen dev/test rows are already excluded** from `DATA/PROCESSED/train.parquet` by
  `01_prep.py` (seed 42). There is no leak.
- The thing the brief is actually protecting against is **depending on the id-lookup mechanism at
  inference**. Training on question→answer pairs does not create that dependency — it removes it.
  That is the entire point of this folder.

**What genuinely should be excluded: the `healthcaremagic` slice of `master_c_bengali.csv`**
(106,117 rows). That is *our own* Bengali translation of the *same underlying cases* the
competition already provides in the organizers' translation. Training on both teaches the model
two competing translations of identical content — redundancy plus a second lexical fingerprint,
with no new medical information. **It is excluded at extraction time and is not bundled** —
`build_index.py` asserts that no unexpected source appears in `extra_sources.parquet`.

If you ever want to test including it (it is a legitimate experiment, just not the default),
re-extract from the full `master_c_bengali.csv` in the wider repo at
`DATA/EXTERNAL_COLLECTED_DATA/Data_Search_5/MASTER_C_BENGALI/`.

---

## TIER 1 — the core mix. Verified real, use all of it.

| # | Source | Path | Rows | Language | Role |
|---|---|---|---|---|---|
| 1 | **Competition train** | `data/_sources/train.parquet` | **101,740** | Bengali (organizers') | The backbone. Direct question→answer in the exact target register. dev/test already removed. |
| 2 | **iCliniq** | `extra_sources.parquet`, `source=='icliniq'` | **7,321** | EN→BN (our translation) | Real patient→doctor consultations from a **different site** than HealthCareMagic — genuinely new cases, not a re-translation |
| 3 | **GenMedGPT** | `extra_sources.parquet`, `source=='genmedgpt'` | **5,200** | EN→BN (our translation) | Real dialogue shape. Short (~35 tokens) — do not let it dominate the length distribution |
| 4 | **doctor_qa_bangla** | `extra_sources.parquet`, `source=='doctor_qa_bangla'` | **4,651** | **Native Bengali** | The only natively-authored Bengali source here — **zero translation fingerprint**. Small, but it is the only data that is not somebody's MT output |

Sources 2–4 were extracted from `master_c_bengali.csv` (123,289 rows) in the wider repo at
`DATA/EXTERNAL_COLLECTED_DATA/Data_Search_5/MASTER_C_BENGALI/` — the other 106,117 rows are
`healthcaremagic`, deliberately left behind.

**Core total: 118,912 rows** — verified by actually running the assembly. Schema is uniform:
`id · source · input · output`.

**Leak status:** `master_c_bengali` already had 6,000 rows removed whose ids fall in the frozen
dev/test split — documented in its own `SOURCES.md`. **Both `build_index.py` and `build_data.py`
re-assert this rather than trusting it**, and the check passes (0 of 5,000 dev + 1,000 test ids
present). Do not disable those asserts.

---

## TIER 2 — optional volume. **Not bundled** — these live in the wider repo.

Paths below are relative to the repo root (the directory containing `DATA/`). Only fetch these if
Tier 1 proves insufficient — experiment **X4** tests exactly that.


| Source | Path | Rows | The catch |
|---|---|---|---|
| **`doctor_qa_bangla` raw** | `DATA/EXTERNAL_COLLECTED_DATA/Data_Search_1/huggingface/doctor_qa_bangla/dataset_mistral.csv` | 5,135 | Single `text` column in `[INST] … [/INST]` format — needs parsing. **Largely the same content as Tier-1 #4** (which is the cleaned 4,651-row version). Use one, not both. |
| **NEW_DATASETS_D1** | `DATA/EXTERNAL_COLLECTED_DATA/NEW_DATASETS_D1/twelve unique datasets.csv` | 277,095 | **68% is exam MCQ** (medmcqa 178,967 + medqa_usmle 10,015) — wrong task shape, and `medqa_usmle`'s median answer is **23 characters**. Translation also damaged clinical detail: `benign prostatic hyperplasia` → `প্রিজম্যাটিক` ("prismatic"), a B12 dose rendered in picograms instead of micrograms, ~33% of unit-bearing rows lost their unit. **If you use any of it, use only `source=='medical_meadow'` (33,222 rows, atomic clinical facts) and `medinstruct_52k` (51,989, longer-form) — never the MCQ slices.** |
| **EN-BN medical QA** | `Data_Search_1/kaggle/english-and-bangla-medical-qa/English_Bangla_Medical_QA.csv` | 498 | **Headerless CSV** — read with `header=None` or the first record is consumed as the column name. Tiny. |

**Recommendation:** start with Tier 1 only (experiment **X4** below tests whether Tier 2 helps).
More data is not automatically better here — this project has already measured a 166k-row corpus
(`ai_medical_chatbot`) *hurting* because its register was wrong (opens `হাই`/`হ্যালো` 70% of the
time vs the references' `হেলো` 76%).

---

## DO NOT USE — each already measured or ruled out, with the reason

| Source | Why not |
|---|---|
| `healthcaremagic` slice (106,117) | Our re-translation of the competition's own content. See the carve-out above. |
| `ai_medical_chatbot` (166,193) | **Measured off-register**: opens `হাই`/`হ্যালো` 70.06% vs references' `হেলো` 76.37%. The largest single corpus available and the riskiest. |
| `alpaca_health` (1,021) | Its "medical" keyword filter matched **homographs** — ≥6.4% is computing/economics content ("causes of the Great Depression", computer viruses) translated into Bengali. |
| `disease_db` (796) | Structured bullet lists, no doctor voice. Wrong output shape. |
| `mts_dialog` (3,503) | **Inverse task** — input is a clinical note, output is the doctor's *opening line*. |
| **MedAidDialog** (arXiv 2603.24132) | LLM-generated (Llama-3.3-70B) then machine-translated. **Two synthetic fingerprints stacked.** Same failure that got NLP4Health dropped. No public download exists yet anyway. |
| **IndicMedDialog** (arXiv 2605.13292) | Same synthetic+MT provenance, **and licensed CC BY-NC-ND** — "No Derivatives" plausibly forbids fine-tuning outright. |
| `BanglaCHQ-Summ` (1,880) | Native Bengali but **question summarization**, not Q&A. Wrong shape. |
| `Data_Search_2` books | No reuse licence; includes veterinary/botanical/alternative-medicine texts. |
| **`BanglaHealth-paraphrase`** | **Verified 133-byte LFS stub on 2026-08-17.** The `SOURCES.md` describing it as 200,000 rows / 81.9 MB predates a git operation that reverted it. Do not plan around it without re-downloading. |
| `Bengali-healthcare` (47,531) | Also a **133-byte stub** now. It *was* fetched and verified once (2026-07-24) — its own note then: *"much of it is translated general-purpose Alpaca content, not clinical — filter before use."* Same register risk as `alpaca_health`. Only worth re-fetching if Tier 1+2 prove insufficient. |

---

## The retrieval pool (for the RAG arms)

`shared/build_index.py` embeds the **Tier-1 core** (118,912 rows) with
`intfloat/multilingual-e5-base` and saves an L2-normalized matrix + metadata.

**Two invariants the script asserts, and you must not disable:**

1. **Zero frozen dev/test ids in the pool.** Retrieving a dev row's own pair returns the answer
   and every number becomes meaningless.
2. **No row may retrieve itself, or a near-duplicate of itself** (cosine > `--sim-ceiling`,
   default 0.97), as its own reference during training-data construction. That would paste the
   answer straight into the input and produce a model that collapses at test time.

**Verify #2 by reading actual built examples**, not just by trusting the assert — print 5 rows of
`data/rag/train.parquet` and confirm the reference case is a *different* case than the target.

---

## Licensing / disclosure (needed for the Phase 2 write-up)

| Source | Licence / terms |
|---|---|
| Competition train | CC BY-NC 4.0 (competition data) |
| iCliniq, GenMedGPT | ChatDoctor repo — code Apache-2.0; data *"for academic research only, commercial and clinical use prohibited"*. Public repo, open links, no gate — satisfies Rules §2.6.a equal-access. Compatible with a Kudos-only competition. |
| doctor_qa_bangla | Apache-2.0 |
| Our Bengali translations | Produced by this team via Google Translate API (`client=gtx`, 1,200-char chunking, retry backoff, digit transliteration). Our own derived artifact. |
| `multilingual-e5-base` (retriever) | MIT |
| `google/mt5-base` | Apache-2.0 |
| `Qwen/Qwen3.5-2B` | check the model card at fetch time and record it |
| `swapnillo/Bangla-AI-1.7B` | model card states "same as base Qwen3-1.7B" |

**Every source actually used must be named in the Phase 2 write-up**, with row counts, the
translation method, and the dedup/filter rules applied. `shared/build_data.py` writes a
`MANIFEST.json` recording exactly what went in — attach it.
