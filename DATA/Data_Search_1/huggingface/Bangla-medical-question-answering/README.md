---
dataset_info:
  features:
  - name: Question
    dtype: string
  - name: Complex_CoT
    dtype: string
  - name: Response
    dtype: string
  - name: Question_Bangla
    dtype: string
  - name: Complex_CoT_Bangla
    dtype: string
  - name: Response_Bangla
    dtype: string
  splits:
  - name: train
    num_bytes: 9509873
    num_examples: 901
  download_size: 4034966
  dataset_size: 9509873
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---
