---
dataset_info:
  features:
  - name: instruction
    dtype: string
  - name: input
    dtype: string
  - name: output
    dtype: string
  splits:
  - name: train
    num_bytes: 84833527
    num_examples: 47531
  download_size: 30445724
  dataset_size: 84833527
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---
