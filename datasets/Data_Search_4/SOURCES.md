# AI Medical Chatbot Audit

## Source

- **Dataset:** [AI medical chatbot](https://www.kaggle.com/datasets/yousefsaeedian/ai-medical-chatbot)
- **Kaggle slug:** `yousefsaeedian/ai-medical-chatbot`
- **Accessed:** 2026-08-05
- **Declared Kaggle licence:** Apache-2.0
- **Declared schema:** `Description`, `Patient`, `Doctor`
- **Important provenance limitation:** the Kaggle card does not identify the original producers of its 256k English patient/doctor rows. The Kaggle licence declaration alone does not establish the rights of underlying web text. Preserve the source URL and disclose this limitation if the data is used.

## Files preserved

| File | Purpose | SHA-256 |
| --- | --- | --- |
| `ai-medical-chatbot.zip` | Original Kaggle download; 86,753,103 bytes. | `9e8d2c4afbd6b5dc9a27d412a608e6d99b4c89b13fbfcd4018c2800bed2106745` |
| `ai-medical-chatbot.csv` | Extracted original CSV; 267,263,847 bytes. | `84b8144978974dba4c433e07d1ca8ffde6cbcf6c6a88ac5a6cc12e568a6c2011` |
| `ai_medical_chatbot_unique_non_chatdoctor.csv` | Audit-filtered English candidate; 163,209,111 bytes. | `a2dff3beffe7580c963110b6d1f67f993a2d6148e7c176febd7751c542b7add6` |

## Raw-data profile

| Measure | Result |
| --- | ---: |
| Rows | 256,916 |
| Empty `Description`, `Patient`, or `Doctor` values | 0 |
| Duplicate `Patient` + `Doctor` pairs | 10,390 |
| `Description` median / p95 characters | 56 / 103 |
| `Patient` median / p95 characters | 353 / 899 |
| `Doctor` median / p95 characters | 475 / 1,129 |
| Rows containing Bengali script | 0 |

The dataset is English. `Description` is a short repeated question title and is not recommended as model input; use `Patient` as the source prompt and `Doctor` as the target response.

## Overlap audit

The candidate was compared to `Data_Search_3/ChatDoctor dataset/unified_medical_qa_train.csv`, the English source-side corpus underlying the Bengali ChatDoctor data.

| Test | Result |
| --- | ---: |
| Candidate rows whose normalized `Patient` text already occurs in English ChatDoctor | 81,170 |
| Of those, HealthCareMagic source rows | 78,687 |
| Of those, iCliniq source rows | 2,483 |
| Candidate rows linked through the same ID to Bengali ChatDoctor | 81,159 |
| Exact normalized `Patient` + `Doctor` pair matches | 605 |

Many duplicate-input rows have doctor answers that differ only in branding, greeting, punctuation, or source-version edits; others have materially different text. Exclude **every candidate row whose normalized `Patient` text is already in ChatDoctor**, rather than trying to retain only exact answer-pair differences.

The competition train is Bengali and has no English source-side counterpart in this repository, so a meaningful semantic English-to-Bengali overlap check is not possible before translation. After translating this candidate, run normalized and semantic deduplication against the official train before training. Never use competition test data or labels.

## Generated candidate subset

`ai_medical_chatbot_unique_non_chatdoctor.csv` contains **166,427 rows** with columns `source_row`, `description`, `patient`, and `doctor`.

It was built in this order:

1. Remove 10,390 duplicate normalized `Patient` + `Doctor` pairs.
2. Remove 79,849 remaining unique pairs whose normalized `Patient` already occurs in English ChatDoctor.
3. For the remaining data, retain the first response for each patient input, removing 250 additional conflicting responses.

Verification confirms 166,427 rows, zero English-ChatDoctor input overlaps, zero duplicate pairs, and one doctor target per patient input.

## Recommendation

This is an **English, filtered Stage-0 candidate**, not training-ready Bengali data. If it is cleared after provenance review:

1. Translate `patient` to Bengali input and `doctor` to Bengali response with a documented deterministic translation workflow.
2. Preserve clinical terms, doses, units, and brand/generic medicine names; manually inspect a stratified sample before use.
3. Re-run decontamination against Bengali ChatDoctor and the official competition train after translation.
4. Compare this curriculum against the existing winner on the frozen dev split:
   `translated filtered candidate -> Bengali ChatDoctor -> official competition train`.
5. Keep it only if it improves Token F1 and ROUGE-L over `Bengali ChatDoctor -> official competition train`.

Do not train on raw `ai-medical-chatbot.csv`; it contains a large re-use of the selected ChatDoctor source material.
