Phase 1 Score carries an 80% weight into the final ranking


# Hugginface

1) https://huggingface.co/datasets/shetumohanto/doctor_qa_bangla
2) 
3)
4)
5)
6)
7)



# Kaggle

1) https://www.kaggle.com/datasets/pialghosh/english-and-bangla-medical-qa-dataset
2) https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research
3) 


# Github 

1) https://github.com/alvi-khan/BanglaCHQ-Summ/tree/main/Dataset
2) https://github.com/sartajekram419/BanglaRQA?tab=readme-ov-file#dataset
3)



# Papers 

1) https://aclanthology.org/2023.banglalp-1.10/
2) 
3) 
4)
5)


# Models 

1) https://github.com/alvi-khan/BanglaCHQ-Summ
2) Bangla T5 (special)
3) mT5-base (oneke fine-tune kore and transforms this model into a monolingual or specialized domain model)
4) mBART-50
5) BanglaT5-mHealth ( very special) https://huggingface.co/faisal4590aziz/bangla-t5-mHealth
6) Bangla MedER [https://arxiv.org/pdf/2512.17769]
7) Med-mT5
8) https://huggingface.co/ai4bharat/IndicBART
9) https://github.com/AI4Bharat/IndicF5
10) https://huggingface.co/lumatic-ai/BongLlama-1.1B-Chat-alpha-v0/tree/637bce2f3d06b574293b4d403f49074866237be1
11)Clinical-T5 -> fine tune large (770M)same concept as banglaT5 except we do the fine tuning...https://huggingface.co/xyla/Clinical-T5-Large


Upper class (Maximized for Phase 2 Reasoning)

These models sit right at the parameter ceiling. They will excel in the Phase 2 LLM-as-judge evaluation because they possess strong internal reasoning, allowing them to output clinically appropriate and clear doctor responses.

12)Qwen2.5-3B-Instruct
13)Llama-3.2-3B ( suggested to look into pretrained bengali variants) https://huggingface.co/hishab/titulm-llama-3.2-3b-v1.1
!4)Gemma-2-2B

Lower Class (Maximized for Phase 1 Leaderboard)

Because Phase 1 heavily rewards models that mimic the exact length, vocabulary, and phrasing of the reference target, sequence-to-sequence (Seq2Seq) models are a strategic choice. They generate highly controlled, concise text.

15) BanglaT5 (Base) (247M parameters)
16) mT5-large: At 1.2B parameters


Fine-Tuning and Deployment StrategiesThe rulebook explicitly permits fine-tuning, LoRA/adapters, quantization, distillation, and ensembling, provided the final combined inference setup is $\le3\text{B}$ parameters.  LoRA / QLoRA for LLMs: If you choose a 3B model like Llama 3.2 or Qwen 2.5, you will likely need to use Parameter-Efficient Fine-Tuning (PEFT) like LoRA. You are allowed to use external data as long as you disclose it in your submission notes. You could compile a high-quality external dataset of Bengali medical Q&A to mix with the provided dataset to enhance the model's clinical accuracy.  Full Fine-Tuning for T5: If you choose BanglaT5, its small size allows you to do full-parameter fine-tuning easily. You can forcefully train it to adopt the exact "tone" and format of the Kaggle reference dataset, gaming the ROUGE and F1 metrics.  Ensembling: The rules allow you to ensemble multiple models, as long as their combined parameter count at inference stays under 3B. A highly competitive strategy could be ensembling an 800M parameter model with a 1.2B parameter model, or ensembling three uniquely fine-tuned BanglaT5 (~247M each) models to achieve the highest possible Phase 1 Score. 











