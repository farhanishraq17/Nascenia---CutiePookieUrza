# Claude Data Search 1 — Source Manifest

**Downloaded:** 2026-07-24 · **Total on disk:** ~715 MB · **Files verified by
loading them**, not by trusting dataset cards.

Task we are matching: **Bengali patient prompt → Bengali doctor response**
(Nascenia AI Hackathon). See
[`../../QUESTIONS-FOR-ORGANIZERS.md`](../../QUESTIONS-FOR-ORGANIZERS.md) §B1 for
the unresolved question of whether external data is even permitted.

> **Nothing here has been cleared for use yet.** Rulebook §2 is
> self-contradictory about external data, and several items below have no
> stated license. Read "Licensing status" and "Contamination risk" before
> training on any of it.

## Bottom line

**No public dataset is an exact match** for the competition spec — single-turn,
natively-authored Bengali patient→doctor consultation pairs. Everything found is
one of: machine-translated from English, LLM-synthesized, a different task shape
(MCQ, summarization, NER, ASR), or small. Several are nonetheless close enough
to be genuinely useful for fine-tuning or domain adaptation.

**No pre-existing Bengali translation of ChatDoctor/HealthCareMagic exists**, as
far as this search could determine. Producing one ourselves (via an MT model or
an LLM) is therefore a live data strategy — and rulebook §3 explicitly permits
distillation, so a >3B *teacher* generating training data appears legal provided
the *deployed* model stays ≤3B. Confirm before relying on it (§B1).

---

## Folder layout

```
Claude_Data_Search_1/
├── SOURCES.md      ← this file
├── huggingface/    9 datasets
├── kaggle/         7 datasets
└── github/         1 dataset
```

---

## Tier 1 — Correct task shape, Bengali

| # | Local path | Source | Rows | License | Verified shape |
|---|---|---|---|---|---|
| 1 | `huggingface/doctor_qa_bangla/` | [shetumohanto/doctor_qa_bangla](https://huggingface.co/datasets/shetumohanto/doctor_qa_bangla) | **5,135** | **Apache-2.0** | Single `text` col; **all 5,135 rows** match `[INST]…[/INST]`. Bengali. Median 365 chars, p95 906. **Best match in the whole set.** |
| 2 | `huggingface/Bengali-healthcare/` | [susnatak/Bengali-healthcare](https://huggingface.co/datasets/susnatak/Bengali-healthcare) | **47,531** | none stated | `instruction`/`input`/`output`; Bengali in `instruction`+`output`. 55% have empty `input` (clean instruction→response). instruction p50 125 ch, output p50 358 ch. **Caveat: much of it is translated general-purpose Alpaca content, not clinical.** Filter before use. |
| 3 | `huggingface/Bangla-medical-question-answering/` | [Shakil2448868/…](https://huggingface.co/datasets/Shakil2448868/Bangla-medical-question-answering) | **901** | none stated | Parallel EN/BN: `Question`,`Complex_CoT`,`Response` + `_Bangla` variants. Bengali confirmed in all three `_Bangla` cols. Identical schema to **#15**, so it is a translation of that. |
| 4 | `huggingface/Medical-english-bangla-QA/` | [Pial2233/Medical-english-bangla-QA](https://huggingface.co/datasets/Pial2233/Medical-english-bangla-QA) | **499** | none stated | Single `text` col, `[INST]` format, mixed EN/BN. |

> **#4 and #10 are byte-identical.** I hashed every row: 499/499 overlap.
> The Kaggle "English and Bangla medical QA dataset" is a mirror of the HF one.
> Use one, not both — double-counting would skew any training mix.

## Tier 2 — Bengali medical, different task shape

| # | Local path | Source | Rows | License | What it actually is |
|---|---|---|---|---|---|
| 5 | `github/BanglaCHQ-Summ/` | [alvi-khan/BanglaCHQ-Summ](https://github.com/alvi-khan/BanglaCHQ-Summ/tree/main/Dataset) | 1,880 / 235 / 235 | see repo | `id`,`question`,`indices`,`summary` — Bengali confirmed in `question`+`summary`. **Abstractive summarization** of consumer health questions, not response generation. Paper: [BLP-2023](https://aclanthology.org/2023.banglalp-1.10/). BanglaT5 baseline ROUGE-L **48.35**. |
| 6 | `huggingface/BanglaHealth-paraphrase/` | [faisal4590aziz/bangla-health-related-paraphrased-dataset](https://huggingface.co/datasets/faisal4590aziz/bangla-health-related-paraphrased-dataset) | **200,000** | **CC-BY-4.0** | `source_sentence`/`paraphrased_sentence`, both Bengali. Paraphrase pairs — ideal for **Bengali health register/style adaptation**, useless as dialogue. |
| 7 | `huggingface/Medicine-Dataset-of-Bangladesh/` | [ArnobBot/Medicine-Dataset-of-Bangladesh](https://huggingface.co/datasets/ArnobBot/Medicine-Dataset-of-Bangladesh) | 21,714 medicines + 1,711 generics | **MIT** | 6 relational CSVs (medicine, generic, indication, drug class, manufacturer, dosage form). **English**, not Bengali. Drug reference — possible RAG grounding (mind the 3B cap on any retriever). |
| 8 | `kaggle/bengali-medical-dataset_shashwatwork/` | [shashwatwork/bengali-medical-dataset](https://www.kaggle.com/datasets/shashwatwork/bengali-medical-dataset) | 8,539 NER tokens; 659 specialist rows | CC-BY-SA-4.0 (per Kaggle) | Bengali Medical **NER** + **Specialist Classification** (`Gender`,`Problem`,`Specialist`). The 659 `Problem` texts are genuine Bengali patient complaints — small but authentic. |
| 9 | `kaggle/bengali-medical-dataset_saurabhshahane/` | [saurabhshahane/bengali-medical-dataset](https://www.kaggle.com/datasets/saurabhshahane/bengali-medical-dataset) | 8,539 / 659 | CC-BY-4.0 (per Kaggle) | **Same content as #8**, delivered as `.xlsx`. Duplicate. |
| 10 | `kaggle/english-and-bangla-medical-qa/` | [pialghosh/english-and-bangla-medical-qa-dataset](https://www.kaggle.com/datasets/pialghosh/english-and-bangla-medical-qa-dataset) | 499 | not stated | **Duplicate of #4.** Note: the CSV is **headerless** — the first record is consumed as the column name if read naively. Pass `header=None`. |
| 11 | `kaggle/bengali-english-disease-symptom/` | [imamzubaer/bengali-english-disease-symptom-dataset](https://www.kaggle.com/datasets/imamzubaer/bengali-english-disease-symptom-dataset) | **91,010** | not stated | Wide one-hot matrix: `রোগ` (disease) + ~380 bilingual symptom columns. Tabular diagnosis data, **not text**. Could seed synthetic symptom→advice pairs. |
| 12 | `kaggle/bengali-chat-conversation/` | [dinmaybrahma/bengali-chat-coversation](https://www.kaggle.com/datasets/dinmaybrahma/bengali-chat-coversation) | 1,045 | not stated | `Question`/`Answer`, Bengali, but **very short** (Q ≈54 ch, A ≈60 ch) and general chit-chat, not medical. Malformed quoting — needs `quoting=3, on_bad_lines='skip'`. Low value. |
| 13 | `kaggle/bengali-medical-corpus/` | [musfiqrahmanramim/bengali-medical-corpus](https://www.kaggle.com/datasets/musfiqrahmanramim/bengali-medical-corpus) | — | not stated | Downloaded; inspect before use. |

## Tier 3 — English source corpora (for translate-then-train / distillation)

| # | Local path | Source | Rows | License | Notes |
|---|---|---|---|---|---|
| 14 | `huggingface/ChatDoctor-HealthCareMagic-100k/` | [lavita/ChatDoctor-HealthCareMagic-100k](https://huggingface.co/datasets/lavita/ChatDoctor-HealthCareMagic-100k) | **112,165** | none stated | `instruction`/`input`/`output`. **English.** The canonical real patient→doctor corpus and the most likely upstream source of any translated Bengali set. |
| 15 | `huggingface/medical-o1-reasoning-SFT/` | [FreedomIntelligence/medical-o1-reasoning-SFT](https://huggingface.co/datasets/FreedomIntelligence/medical-o1-reasoning-SFT) | 19,704 EN · 20,171 ZH · 24,887 mix · 25,358 mix-ZH | **Apache-2.0** | `Question`/`Complex_CoT`/`Response`. **Confirmed upstream of #3** (identical schema). Reasoning-heavy. |
| 16 | `kaggle/MedQuAD/` | [pythonafroz/medquad-…](https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research) | **16,412** | CC-BY-4.0 (NIH-derived) | `question`/`answer`/`source`/`focus_area`. **English**, authoritative NIH content. |
| 17 | `huggingface/medical-qa-multi/` | [Malikeh1375/medical-question-answering-datasets](https://huggingface.co/datasets/Malikeh1375/medical-question-answering-datasets) | **331,191** across 10 subsets | **MIT** | Multi-corpus aggregation. **English.** Best license of any Tier-3 item. Subset breakdown below. |

### #17 subset breakdown (all `instruction`/`input`/`output`)

| Subset | Rows | Output p50 | Worth anything? |
|---|---|---|---|
| `chatdoctor_icliniq` | **7,321** | 480 ch | **The new find.** Real patient→doctor dialogues from iCliniq — a *different* source than HealthCareMagic (#14), so it adds genuinely new material rather than duplicating. |
| `medical_meadow_wikidoc_patient_information` | 5,942 | 304 ch | Patient-facing explanations — register is close to what we want. |
| `medical_meadow_wikidoc` | 10,000 | 431 ch | Long-form medical prose. |
| `medical_meadow_mediqa` | 2,208 | 417 ch | Consumer health QA. |
| `all-processed` | 246,678 | 417 ch | Superset aggregation — **overlaps every other subset**, including #14. Use *either* this *or* the individual subsets, never both. |
| `medical_meadow_medical_flashcards` | 33,955 | 150 ch | Terse flashcard answers. |
| `medical_meadow_health_advice` | 8,676 | **17 ch** | Classification labels, not prose. |
| `medical_meadow_medqa` | 10,178 | **25 ch** | MCQ answers. |
| `medical_meadow_pubmed_causal` | 2,446 | 43 ch | Classification. |
| `medical_meadow_mmmlu` | 3,787 | **1 ch** | Single-letter MCQ answers. Useless here. |

---

## Deliberately NOT downloaded

| Item | Size | Why skipped |
|---|---|---|
| [pr0mila-gh0sh/MediBeng](https://huggingface.co/datasets/pr0mila-gh0sh/MediBeng) | 325 MB | **Audio/ASR** dataset (code-switched BN-EN clinical speech). Cannot contribute to a text-generation task, and would have been 40% of total bytes. Say the word and I'll pull it. |
| [IndicMedDialog](https://arxiv.org/abs/2605.13292) | — | **CC BY-NC-ND 4.0** — "No Derivatives" plausibly forbids fine-tuning. No download link published on the abstract page. |
| [MedAidDialog](https://arxiv.org/abs/2603.24132) | — | CC BY-NC-SA 4.0. No download link found. |
| [dadhichisarker/bangladeshi-multipurpose-dataset](https://www.kaggle.com/datasets/dadhichisarker/bangladeshi-multipurpose-dataset) | **3.16 GB** | Generic Bangladeshi corpus, not medical dialogue. Poor size-to-value ratio. |
| `medical_meadow_cord19` (subset of #17) | **753 MB** | COVID-19 research paper abstracts. Not dialogue, and 75% of that repo's bytes. |
| `chatdoctor_healthcaremagic` (subset of #17) | 70.5 MB | Byte-for-byte the same size as #14, which we already have. Skipped as a duplicate. |

## Reference only (no dataset to download)

- **BanglaMedQA / BanglaMMedBench** — [arXiv 2511.04560](https://arxiv.org/html/2511.04560). Bangla medical MCQ from MBBS/BDS/AFMC admission tests. Wrong output format, useful as a medical-knowledge probe.
- **MTS-Dialog-Bangla** — [IEEE 11429289](https://ieeexplore.ieee.org/abstract/document/11429289/). 1,701 Bangla clinical dialogue→note pairs (see "Calibration anchor" below).
- **Bangla MedER** — [arXiv 2512.17769](https://arxiv.org/pdf/2512.17769). Multi-BERT ensemble for Bangla medical entity recognition, 89.58% acc. Release status unstated.

## Candidate models (≤3B — all need param verification before use)

From `../links.md`, none yet verified against the 3B cap:

- **BanglaT5** — csebuetnlp; the BanglaCHQ-Summ paper's best model (ROUGE-L 48.35).
- **[BanglaT5-mHealth](https://huggingface.co/faisal4590aziz/bangla-t5-mHealth)** — BanglaT5 fine-tuned on BanglaHealth (#6). Health-domain Bengali already.
- **mT5-base** (~580M) — best performer on MTS-Dialog-Bangla.
- **mBART-50** (~610M).

Per CLAUDE.md §2 rule 5, **print `sum(p.numel() …)` and assert ≤3e9 before
using any of these.** Encoder-decoder models with large multilingual
vocabularies carry heavy embedding tables.

---

## Licensing status — read before training

**Cleanly licensed:** #1 Apache-2.0 · #6 CC-BY-4.0 · #7 MIT · #15 Apache-2.0 ·
#16 CC-BY-4.0 · #9 CC-BY-4.0 · #8 CC-BY-SA-4.0.

**No license stated** (#2, #3, #4, #10, #11, #12, #13, #14): absence of a
license is *not* permission. #2 and #14 are the two largest of these and the
most tempting — treat both as unresolved. Rulebook §2 requires disclosing all
external data anyway, so anything used here goes in the Phase 2 write-up.

## Contamination risk — the thing that could disqualify us

The organizers' Bengali corpus had to come from somewhere, and the two cheapest
recipes are exactly what's in this folder: **machine-translate ChatDoctor
(#14)**, or **LLM-synthesize from an English seed (#15)**. If they used either,
public data here may overlap the **private test set** — and rulebook §8 makes
training on test inputs a disqualifying offence regardless of intent.

**Do this once the competition data lands (August 4th):**

1. Near-duplicate-hash the official train split against every dataset here.
2. If any shows high overlap with *train*, assume *test* is drawn from the same
   pool and exclude it from training.
3. Check whether the official Bengali reads like machine translation (calque
   syntax, uniform MT artifacts) — that identifies the pipeline, hence the source.
4. Log everything used in `EXPERIMENTS/EXP-LOG.md` for the Phase 2 write-up.

## Recommended next steps

1. **Get §B1 answered in writing** before investing in any external-data plan.
   Everything in this folder is worthless if external data turns out to be
   disallowed.
2. **Start with #1 `doctor_qa_bangla`** — Apache-2.0, right shape, verified
   Bengali. It is the only item that is simultaneously well-licensed, correctly
   shaped, and unambiguously Bengali.
3. **Treat the unlicensed sets as provisional** (#2, #3, #4, #10–#14).
   Unspecified is not the same as permissive.
4. **Watch for double-counting.** Three overlaps are confirmed: #4≡#10,
   #8≡#9, and `all-processed` ⊇ the other #17 subsets ∪ #14.
5. **Re-run this survey after August 4th.** Knowing the actual style and length
   of the official reference responses will sharply narrow which of these is
   worth anything — response length is a first-class scoring knob under the
   composite metric (CLAUDE.md §1).

## Calibration anchor

MTS-Dialog-Bangla reports **mT5-base at BERTScore F1 0.7619 / ROUGE-1 F1
0.2421** on Bangla clinical text generation; BanglaCHQ-Summ reports **BanglaT5
at ROUGE-L 48.35** on Bangla health-question summarization. Different tasks, so
neither is a target — but together they anchor the order of magnitude to expect
on Bengali medical generation, and they show the **large gap between BERTScore
and ROUGE** that our 0.5/0.3/0.2 composite will have to straddle.

## Reproducing this download

Scripts are in the session scratchpad; the operations were:
`huggingface_hub.snapshot_download(repo_id, repo_type="dataset")` for the HF
sets, `python -m kaggle datasets download -d <ref> --unzip` for Kaggle, and
raw `raw.githubusercontent.com` fetches for BanglaCHQ-Summ.

**Gotchas found the hard way:**
- pandas 3.0 reports string columns as `str` dtype, **not** `object` — dtype
  checks written for pandas 2 silently match nothing.
- Printing Bengali to a Windows cp1252 console raises `UnicodeEncodeError`.
  Write to UTF-8 files; keep console output ASCII. (CLAUDE.md §12.)
- Don't name a script `inspect.py` — it shadows the stdlib module numpy imports.
