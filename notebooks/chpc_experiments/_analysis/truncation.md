/scratch/general/nfs1/u1592009/envs/nascenia/lib64/python3.11/site-packages/transformers/utils/hub.py:110: FutureWarning: Using `TRANSFORMERS_CACHE` is deprecated and will be removed in v5 of Transformers. Use `HF_HOME` instead.
  warnings.warn(
| dataset | tokenizer | src cap | % src cut | src p95 | src max | tgt cap | % tgt cut | tgt p95 | tgt max |
|---|---|---|---|---|---|---|---|---|---|
You are using the default legacy behaviour of the <class 'transformers.models.t5.tokenization_t5.T5Tokenizer'>. This is expected, and simply means that the `legacy` (previous) behavior will be used so nothing changes for you. If you want to use the new behaviour, set `legacy=False`. This should only be set if you understand what it means, and thoroughly read the reason why this was added as explained in https://github.com/huggingface/transformers/pull/24565
Token indices sequence length is longer than the specified maximum sequence length for this model (698 > 512). Running this sequence through the model will result in indexing errors
| draft_only | banglat5 | 768 | **0.0%** | 234 | 698 | 512 | **0.05%** | 237 | 623 |
| english_draft | banglat5 | 768 | **1.62%** | 603 | 1851 | 512 | **0.05%** | 237 | 623 |
| question_draft | banglat5 | 640 | **0.37%** | 387 | 1509 | 512 | **0.05%** | 237 | 623 |
| all_inputs | banglat5 | 1024 | **0.83%** | 734 | 1925 | 512 | **0.05%** | 237 | 623 |
| english_only | banglat5 | 640 | **0.25%** | 368 | 1046 | 512 | **0.035%** | 236 | 665 |
| question_only | banglat5 | 768 | **0.015%** | 202 | 969 | 512 | **0.035%** | 236 | 665 |
/scratch/general/nfs1/u1592009/envs/nascenia/lib64/python3.11/site-packages/transformers/convert_slow_tokenizer.py:566: UserWarning: The sentencepiece tokenizer that you are converting to a fast tokenizer uses the byte fallback option which is not implemented in the fast tokenizers. In practice this means that the fast version of the tokenizer can produce unknown tokens whereas the sentencepiece version would have converted these unknown tokens into a sequence of byte tokens matching the original piece of text.
  warnings.warn(
| draft_only | mt5-base | 640 | **0.95%** | 455 | 1409 | 640 | **0.715%** | 448 | 1217 |

wrote /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/analysis/truncation.json
