set -uo pipefail

export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
# 🔴 the env HF_TOKEN is DEAD and overrides the token file; unset it so gated repos
# (gemma) resolve through HF_HOME/token, which holds the account that has access.
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=8
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python

echo "node=$(hostname)  job=$SLURM_JOB_ID  $(date)"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader

cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E18_model_zoo
$PY ../code/03_train_causal.py \
  --data-dir ../data/draft_only \
  --model Qwen/Qwen3-1.7B \
  --out-dir . --run-name qwen3_1p7b \
  --seed 11 \
  --lr 2e-05 --warmup 200 \
  --max-len 2560 \
  --batch-size 4 --grad-accum 16 --eval-batch-size 4 \
  --eval-subset 300 --eval-steps 250 --max-steps 4000 \
  --early-stopping-patience 5 \
  --num-beams 4 --min-new-tokens 200 --max-new-tokens 1280 \
  --precision auto --grad-checkpointing --optim adamw_torch
echo "train exit=$?  done $(date)"