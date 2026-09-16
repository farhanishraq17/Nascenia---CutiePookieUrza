# External Medical Fine-Tuning Data Search

Search completed across Kaggle, Hugging Face, published-paper repositories, dataset portals, and project websites. These are the relevant results for the Bengali patient-to-doctor response-generation competition. This is an audit of data *fitness*, not a claim that more data will necessarily improve the leaderboard score.

## Decision summary

| Candidate | Recommendation |
| --- | --- |
| [AI medical chatbot (Kaggle)](https://www.kaggle.com/datasets/yousefsaeedian/ai-medical-chatbot) | **Audited Stage-0 candidate.** The download contains 256,916 English rows, not 220k. It reuses 81,170 ChatDoctor patient inputs, so raw data must not be trained. The generated [166,427-row filtered subset](datasets/Data_Search_4/SOURCES.md) removes all such inputs, duplicate pairs, and conflicting second answers. It still requires translation, post-translation deduplication against the official train, and a frozen-dev ablation. See the [audit](datasets/Data_Search_4/SOURCES.md). |
| [MTS-Dialog](https://github.com/abachaa/MTS-Dialog) | **Small controlled ablation.** 1.7k English doctor-patient conversations, CC BY 4.0. Convert patient context to next-doctor-turn pairs, translate, then use only as a short Stage-0 warm-start. Its native task is clinical-note generation, so do not mix it heavily. |
| [Simulated patient-physician interviews](https://springernature.figshare.com/collections/A_dataset_of_simulated_patient-physician_medical_interviews_with_a_focus_on_respiratory_cases/5545842/1) / [MediTOD](https://github.com/dair-iitd/MediTOD) | **Small controlled ablation.** 272 manually corrected simulated English consultations; MediTOD provides history-taking annotations over this source. It is high-quality but narrow and multi-turn, so it cannot replace the main data. |
| [NLP4Health-2025](https://nlpai4health.com/) | **Do not use unless organisers grant permission.** This is the strongest Bangla lead: more than 45k validated multilingual patient-provider dialogues with Bangla QA pairs. The organiser site says the data is licensed for shared-task purposes only. See the [shared-task paper](https://aclanthology.org/2025.nlpai4health-main.5/). |
| [IndicMedDialog](https://arxiv.org/abs/2605.13292) | **Watch / contact authors; not usable today.** The paper describes 2,980 parallel medical dialogues, including Bengali, translated and native-speaker checked. No downloadable dataset or reuse licence is linked. |
| [MedAidDialog](https://arxiv.org/abs/2603.24132) | **Do not use yet.** It describes Bengali multi-turn synthetic medical dialogues, but the paper says the data and code will be made public later. |
| [BanglaMedQA / BanglaMMedBench](https://huggingface.co/datasets/Oni279/BanglaMedQA) | **Do not SFT.** Bengali medical exam MCQs with rationales—not patient-to-doctor answers. The dataset card does not give a licence. |
| [Bengali descriptive symptoms-to-disease dataset](https://data.mendeley.com/datasets/c47cxw8cz4/1) | **Do not SFT.** It is CC BY 4.0 but is symptom-to-disease classification, not answer generation. It could support a future classifier only. |
| [MedMemoryBench](https://huggingface.co/datasets/Cyan27/MedMemoryBench) | **Exclude.** Its 31,976 English medical dialogue turns arise from only 20 synthetic patient personas and the benchmark targets long-term memory. It would distort the intended response style. |
| [MedDialog](https://huggingface.co/datasets/bigbio/meddialog), [HealthCareMagic-100k](https://huggingface.co/datasets/fzkuji/HealthCareMagic-100k), [Kaggle ChatDoctor](https://www.kaggle.com/datasets/punyaslokaprusty/chatdoctor/data), and [CovidDialog](https://www.kaggle.com/datasets/xuehaihe/covid-dialogue-dataset) | **Do not add.** These are overlapping or repackaged web-consultation sources. MedDialog identifies HealthCareMagic and iCliniq as sources and says their copyrights belong to those websites; the existing Bengali ChatDoctor corpus already uses those high-value source families. |

## Additional sources assessed and rejected

| Candidate | Decision | Reason |
| --- | --- | --- |
| [Bengali Medical Dataset (Kaggle)](https://www.kaggle.com/datasets/shashwatwork/bengali-medical-dataset) | Exclude from generator SFT. | CC BY 4.0 Bengali specialist classification and named-entity labels, not doctor answers. |
| [Atanuc Bengali Medical Chatbot Dataset](https://huggingface.co/datasets/Atanuc73/Bengali-Medical-Chatbot-Dataset) | Exclude. | Only ten examples; the shown English source/answer content is ChatDoctor-derived and adds no useful unique supervision. |
| [Bangla medical question-answering, 901 rows](https://huggingface.co/datasets/Shakil2448868/Bangla-medical-question-answering) | Exclude. | Existing repository candidate; reasoning/CoT schema, unclear licence, and low value beside Bengali ChatDoctor. |
| [BanglaCHQ-Summ](https://github.com/alvi-khan/BanglaCHQ-Summ) | Exclude. | Bengali consumer-health-question summarization, not doctor response generation; CC BY-NC-SA 4.0. |
| [MDDial](https://github.com/srijamacherla24/MDDial) | Exclude. | English template-generated differential-diagnosis dialogue. It is useful as the basis for IndicMedDialog research, but too templatic for this leaderboard model. |
| [Synthetic doctor-patient conversations, 3k](https://huggingface.co/datasets/syntech-ai/doctor-patient-conversations-3000) | Exclude. | English synthetic triage corpus under CC BY-NC 4.0; less trustworthy and less natural than the selected external data. |
| [Postzeun Patient-Doctor](https://huggingface.co/datasets/Postzeun/Patient-Doctor) | Exclude. | 60.6k template-like English history-taking records with no dataset card or stated licence. |
| [know_medical_dialogues](https://huggingface.co/datasets/knowrohit07/know_medical_dialogues) | Exclude. | Small synthetic/GPT-4-derived dialogue dataset with an OpenRAIL licence; it does not provide a sufficiently auditable training advantage. |
| [COVID-Dialogue](https://github.com/UCSD-AI4H/COVID-Dialogue) | Exclude. | Only 603 English consultations, narrow and time-specific; source material comes from the same web-consultation sites as MedDialog/ChatDoctor. |
| [Clinical conversations V1.2](https://huggingface.co/datasets/CodCodingCode/clinical-conversations-V1.2) | Exclude. | Synthetic dialogue-to-clinical-vignette task with explicit reasoning traces, not the required doctor-answer task. |
| [PARCOMED research-only](https://huggingface.co/datasets/HealthDataHub/PARCOMED_research_only) | Exclude. | Large French research-only corpus. Its dialogue components are not Bengali patient-answer pairs, and translating this mixed corpus would be a poor first experiment. |
| [Spanish Medical Dialogue Dataset, TEME-v1](https://zenodo.org/records/17280661) | Exclude. | Only 90 Spanish dialogues, primarily for speech-transcription evaluation; no stated reuse licence on the record. |
| [EMSDialogue Datasets](https://huggingface.co/datasets/Xueren/EMSDialogue-Datasets) | Exclude. | English emergency-services dialogue/annotation data, CC BY-NC 4.0, not consumer doctor-answer generation. |
| [MSK Medical Rehabilitation Dialogue Assessment](https://huggingface.co/datasets/Atereoyin/MSK-Medical-Rehabilitation-Dialogue-Assessment) | Exclude. | Mostly synthetic rehabilitation material; its 1,200 medical consultations are derived from MTS-Dialog, so it adds duplicate data. |
| [Bangla instruction datasets](https://huggingface.co/datasets/kamruzzaman-asif/bangla-instruction-dataset) and [Bangla-SFT-50k](https://huggingface.co/datasets/spitfire4794/Bangla-SFT-50k) | Exclude for this phase. | Broad or synthetic general instruction data, not medical patient-to-doctor supervision. They may alter the desired medical register. |
| MedMCQA, BigBio/MedQA reading comprehension, MediQAl, medical-o1 reasoning SFT, and textbook/reference corpora | Exclude. | Exam, extractive-QA, reasoning, or reference-prose formats. Translating them does not create high-quality doctor-response supervision. |

## Training order for data that survives the audit

1. Train a BanglaT5 **official-data-only** control model.
2. Train the principal challenger: **Bengali ChatDoctor warm-start -> official competition train**.
3. If the Kaggle 220k data passes provenance, exact/near-duplicate, language, and quality checks: **translated unique Kaggle subset -> Bengali ChatDoctor -> official train**.
4. Run one small alternate: **translated MTS-Dialog plus simulated interviews -> Bengali ChatDoctor -> official train**.
5. Retain a candidate only if it beats step 2 on the frozen dev split for Token F1 and ROUGE-L. Never train on the frozen dev split or any competition test material.

## Required audit before adding any candidate

- Verify its licence and derivative/translation permission from the original publisher, not only a mirror's metadata.
- Remove exact duplicates and high-similarity duplicates against Bengali ChatDoctor and the official training data.
- Translate deterministically, record the model/version/prompt, preserve medical names and dosage strings, and spot-check Bengali clinical terminology.
- Save source URLs, original and processed dataset hashes, row counts, filters, deduplication reports, and stage-wise epochs for competition disclosure.
- Keep retrieval out of the leaderboard submission; the existing retrieval baseline was worse than a fluent constant and the above sources are for controlled SFT experiments.
