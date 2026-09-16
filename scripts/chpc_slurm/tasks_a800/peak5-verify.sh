set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
D=$P/data/english_draft
E=$P/E19_multiseed_ensemble
C=$P/E05_train_to_convergence/english_draft/ckpt
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cp $P/E05_train_to_convergence/english_draft/best/{spiece.model,tokenizer.json,tokenizer_config.json,special_tokens_map.json} $P/E15_decode_sweep/ckptavg_peak5/ 2>/dev/null
$PY $P/code/14_decode_sweep.py --ckpt $P/E15_decode_sweep/ckptavg_peak5 --data-dir $D \
  --max-source-len 768 --beams 8 --length-penalties 1.2 --min-new 0 --max-new 320 \
  --batch-size 8 --verify-top 1 --out $P/E15_decode_sweep/verify_peak5.json
echo "done $(date)"
