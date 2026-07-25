---
language:
- en
task_categories:
- question-answering
tags:
- medical
- clinical
- healthcare
dataset_info:
- config_name: all-processed
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  - name: __index_level_0__
    dtype: int64
  splits:
  - name: train
    num_bytes: 276980695
    num_examples: 246678
  download_size: 0
  dataset_size: 276980695
- config_name: chatdoctor_healthcaremagic
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 126454896
    num_examples: 112165
  download_size: 70518147
  dataset_size: 126454896
- config_name: chatdoctor_icliniq
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 7347194
    num_examples: 7321
  download_size: 4153680
  dataset_size: 7347194
- config_name: medical_meadow_cord19
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 1336834621
    num_examples: 821007
  download_size: 752855706
  dataset_size: 1336834621
- config_name: medical_meadow_health_advice
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 2196957
    num_examples: 8676
  download_size: 890725
  dataset_size: 2196957
- config_name: medical_meadow_medical_flashcards
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 16453987
    num_examples: 33955
  download_size: 6999958
  dataset_size: 16453987
- config_name: medical_meadow_mediqa
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 15690088
    num_examples: 2208
  download_size: 3719929
  dataset_size: 15690088
- config_name: medical_meadow_medqa
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 10225018
    num_examples: 10178
  download_size: 5505473
  dataset_size: 10225018
- config_name: medical_meadow_mmmlu
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 1442124
    num_examples: 3787
  download_size: 685604
  dataset_size: 1442124
- config_name: medical_meadow_pubmed_causal
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 846695
    num_examples: 2446
  download_size: 210947
  dataset_size: 846695
- config_name: medical_meadow_wikidoc
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 10224074
    num_examples: 10000
  download_size: 5593178
  dataset_size: 10224074
- config_name: medical_meadow_wikidoc_patient_information
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 3262558
    num_examples: 5942
  download_size: 1544286
  dataset_size: 3262558
configs:
- config_name: all-processed
  data_files:
  - split: train
    path: all-processed/train-*
- config_name: chatdoctor_healthcaremagic
  data_files:
  - split: train
    path: chatdoctor_healthcaremagic/train-*
- config_name: chatdoctor_icliniq
  data_files:
  - split: train
    path: chatdoctor_icliniq/train-*
- config_name: medical_meadow_cord19
  data_files:
  - split: train
    path: medical_meadow_cord19/train-*
- config_name: medical_meadow_health_advice
  data_files:
  - split: train
    path: medical_meadow_health_advice/train-*
- config_name: medical_meadow_medical_flashcards
  data_files:
  - split: train
    path: medical_meadow_medical_flashcards/train-*
- config_name: medical_meadow_mediqa
  data_files:
  - split: train
    path: medical_meadow_mediqa/train-*
- config_name: medical_meadow_medqa
  data_files:
  - split: train
    path: medical_meadow_medqa/train-*
- config_name: medical_meadow_mmmlu
  data_files:
  - split: train
    path: medical_meadow_mmmlu/train-*
- config_name: medical_meadow_pubmed_causal
  data_files:
  - split: train
    path: medical_meadow_pubmed_causal/train-*
- config_name: medical_meadow_wikidoc
  data_files:
  - split: train
    path: medical_meadow_wikidoc/train-*
- config_name: medical_meadow_wikidoc_patient_information
  data_files:
  - split: train
    path: medical_meadow_wikidoc_patient_information/train-*
license: mit
---