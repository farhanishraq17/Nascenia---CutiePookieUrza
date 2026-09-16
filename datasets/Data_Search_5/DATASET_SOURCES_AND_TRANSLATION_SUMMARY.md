====================================================================================================
BENGALI MEDICAL DIALOGUE GENERATION — DATASET SOURCES & TRANSLATION METHODOLOGY SUMMARY
====================================================================================================

This document provides a comprehensive inventory of all datasets available in this repository,
including their original source links, row counts, language status, and exact translation methodology.

----------------------------------------------------------------------------------------------------
1. GIVEN DATASETS (Official Nascenia Competition Ground-Truth Dataset)
----------------------------------------------------------------------------------------------------
- Directory Path: Given datasets/
- Primary Files:
  * Given datasets/train.csv (108,954 rows, 295.96 MB)
  * Given datasets/test.csv  (1,000 rows, 1.07 MB)
- Columns: ['id', 'input', 'output']
- Source Link / Organizer: Nascenia LTD · Nascenia AI Hackathon (Kaggle Competition)
- Language: Native Bengali
- Translation Method: 
  * NATIVE BENGALI DATASET — No translation required. Released directly in Bengali by competition 
    organizers as ground-truth patient query and doctor response benchmark data.

----------------------------------------------------------------------------------------------------
2. MORE DATASETS (AI Medical Chatbot & MTS Dialog Collection)
----------------------------------------------------------------------------------------------------
- Directory Path: More datasets/
- Primary Files:
  * More datasets/more_datasets_bengali_train.csv  (169,930 rows, 390.49 MB) — Translated Bengali
  * More datasets/more_datasets_bengali_train.json (169,930 records, 402.32 MB) — Translated Bengali
  * More datasets/more_datasets_unified_en.csv     (169,946 rows, 151.93 MB) — English Source
  * More datasets/more_datasets_unified_en.json    (169,946 records, 163.76 MB) — English Source
  * More datasets/ai_medical_chatbot_unique_non_chatdoctor.csv (166,427 rows) — Raw English Source
  * More datasets/MTS-Dialog-Augmented-TrainingSet-3-FR-and-ES-3603-Pairs-final.csv (3,603 rows) — Raw English Source
- Columns: ['id', 'source', 'input', 'output']

- Sub-Dataset A: AI Medical Chatbot (166,427 rows)
  * Source Link: Hugging Face / Kaggle Medical Dialogue Datasets (Unique non-ChatDoctor AI Medical Chatbot)
  * Raw Format: Columns ['source_row', 'description', 'patient', 'doctor']
  * Translation Method:
    - Prepared using `New folder/src/prepare_more_datasets.py` mapping 'patient' -> input and 'doctor' -> output.
    - Translated from English to Bengali using Google Translate API (`client=gtx`) via Python script
      `New folder/src/translate_more_datasets_to_bangla.py` (20 concurrent worker threads).
    - Text chunking (1,200 chars), retry backoff, zero-width symbol sanitization (`clean_code_symbols_and_syntax`),
      and digit transliteration to Bengali (`EN_TO_BN_DIGITS`).

- Sub-Dataset B: MTS Dialog (3,603 rows)
  * Source Link: MTS-Dialog Dataset / Kaggle Clinical Dialogue Benchmark
    (URL: https://www.kaggle.com/datasets/mts-dialog)
  * Raw Format: Multi-turn clinical conversation strings ('Doctor:', 'Patient:') & clinical summaries.
  * Translation Method:
    - Dialogue turns parsed into Patient inquiry ('input') and Doctor response ('output').
    - Translated from English to Bengali using multi-threaded Google Translate API engine with chunking and retries.

----------------------------------------------------------------------------------------------------
3. CHATDOCTOR DATASET COLLECTION
----------------------------------------------------------------------------------------------------
- Directory Path: ChatDoctor dataset/
- Primary Files:
  * ChatDoctor dataset/bengali_medical_train_clean.csv (131,877 rows, 344.07 MB) — Translated Bengali
  * ChatDoctor dataset/bengali_medical_train_clean.json (131,877 records, 353.24 MB) — Translated Bengali
  * ChatDoctor dataset/unified_medical_qa_train.csv (126,792 rows, 130.22 MB) — English Source
  * ChatDoctor dataset/non_medical_filtered_data.csv (31 rows, 0.03 MB) — Excluded non-medical records
- Columns: ['id', 'source', 'input', 'output']
- Sub-Component Sources & Links:
  1) HealthCareMagic-100k (112,154 rows):
     * Source Link: https://github.com/Liazylee/ChatDoctor / Hugging Face `Liaobing/HealthCareMagic-100k`
  2) iCliniq (7,321 rows):
     * Source Link: https://github.com/Liazylee/ChatDoctor / Hugging Face `Liaobing/iCliniq`
  3) GenMedGPT-5k (5,452 rows):
     * Source Link: https://huggingface.co/datasets/GenMedGPT
  4) doctor_qa_bangla (5,133 rows):
     * Source Link: https://huggingface.co/datasets/shetumohanto/doctor_qa_bangla
  5) Alpaca Health (1,021 rows):
     * Source Link: https://github.com/tatsu-lab/stanford_alpaca (filtered for medical keywords)
  6) Disease Database / format_dataset (796 rows):
     * Source Link: Disease & Symptom Database format dataset
- Translation Method:
  * English components translated to Bengali using multi-threaded Google Translate API script (`translate_chatli_to_bangla.py`).
  * Text sanitized using code symbol cleaner (`clean_code_symbols.py`).
  * Filtered against explicit non-medical keywords using `filter_non_medical_data.py`.

----------------------------------------------------------------------------------------------------
4. NATIVE BENGALI & SEARCH DATASETS (DATA/Data_Search_1/)
----------------------------------------------------------------------------------------------------
- Directory Path: DATA/Data_Search_1/

- Sub-Dataset A: doctor_qa_bangla
  * File: DATA/Data_Search_1/huggingface/doctor_qa_bangla/dataset_mistral.csv (5.41 MB)
  * Source Link: https://huggingface.co/datasets/shetumohanto/doctor_qa_bangla
  * Language: Native Bengali
  * Translation Method: NATIVE BENGALI DATASET — Parsed from Mistral `[INST] prompt [/INST] response` format.

- Sub-Dataset B: BanglaHealth-paraphrase
  * File: DATA/Data_Search_1/huggingface/BanglaHealth-paraphrase/all_paraphrased_data.csv (81.90 MB)
  * Source Link: https://huggingface.co/datasets/BanglaHealth-paraphrase
  * Language: Native Bengali
  * Translation Method: NATIVE BENGALI DATASET — Paraphrased healthcare pairs in Bengali.

- Sub-Dataset C: BanglaCHQ-Summ
  * Files: DATA/Data_Search_1/github/BanglaCHQ-Summ/ (train/valid/test.csv)
  * Source Link: https://github.com/alvi-khan/BanglaCHQ-Summ/tree/main/Dataset
  * Language: Native Bengali
  * Translation Method: NATIVE BENGALI DATASET — Consumer Health Question Summarization in Bengali.

- Sub-Dataset D: English_Bangla_Medical_QA
  * File: DATA/Data_Search_1/kaggle/english-and-bangla-medical-qa/English_Bangla_Medical_QA.csv (0.57 MB)
  * Source Link: https://www.kaggle.com/datasets/pialghosh/english-and-bangla-medical-qa-dataset
  * Language: Native Parallel Bengali & English
  * Translation Method: NATIVE PARALLEL DATASET — Pre-existing parallel Bengali-English medical Q&A.

- Sub-Dataset E: MedQuAD
  * File: DATA/Data_Search_1/kaggle/MedQuAD/medquad.csv (21.84 MB)
  * Source Link: https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research
  * Language: English
  * Translation Method: Raw English medical QA dataset.

----------------------------------------------------------------------------------------------------
5. MASTER COMBINED TRAINING DATASET (DATA/)
----------------------------------------------------------------------------------------------------
- Directory Path: DATA/
- Primary Files:
  * DATA/bengali_medical_train_master.csv  (410,525 rows, 687.80 MB) — Master Training Set
  * DATA/bengali_medical_train_master.json (410,525 records, 707.15 MB) — Master Training Set
- Columns: ['id', 'input', 'output', 'source']
- Composition:
  1) More datasets (more_datasets_bengali_train.csv): 169,930 rows (41.39%)
  2) ChatDoctor dataset (bengali_medical_train_clean.csv): 131,877 rows (32.12%)
  3) Given datasets (Given datasets/train.csv): 108,954 rows (26.54%)
  * Total Master Dataset: 410,525 deduplicated Bengali Q&A records.
- Pipeline Script: `New folder/src/package_master_bengali_dataset.py`
  * Combines all sub-datasets, removes cross-dataset exact duplicates, applies natural sorting by ID,
    and formats into the competition target schema ['id', 'input', 'output'].

====================================================================================================
SUMMARY TABLE
====================================================================================================
Dataset Name               | Record Count | Primary Language | Source Link / Origin                     | Translation Engine
------------------------------------------------------------------------------------------------------------------------------------
Given datasets (train.csv) | 108,954      | Native Bengali   | Nascenia AI Hackathon (Kaggle)           | Native (No translation needed)
More datasets (bengali)    | 169,930      | Translated BN    | AI Medical Chatbot + MTS Dialog          | Multi-threaded Google Translate API
ChatDoctor dataset (clean) | 131,877      | Translated BN    | HealthCareMagic, iCliniq, GenMedGPT, etc.| Multi-threaded Google Translate API
DATA Master Dataset        | 410,525      | Unified Bengali  | Master Combination (All above sources)   | Automated Master Packaging Pipeline
====================================================================================================
