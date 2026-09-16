#!/bin/bash
#SBATCH --job-name=nd-e24-qwen25_1p5b_ed
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --gres=gpu:l40s:1

#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 1-00:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E24_model_size/logs/qwen25_1p5b_ed.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E24_model_size/logs/qwen25_1p5b_ed.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
# 🔴 the env HF_TOKEN is dead; the token FILE (account omarhawktuah) is the one with access
# to the gated repos. Unset so the file wins.
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E24_model_size
# effective batch 2 x 32 = 64 — must be 64, it is the one non-negotiable knob
$PY ../code/03_train_causal.py \
  --data-dir ../data/english_draft --model Qwen/Qwen2.5-1.5B-Instruct \
  --out-dir . --run-name qwen25_1p5b_ed --seed 11 \
  --lr 2e-05 --warmup 200 \
  --max-len 3072 --max-new-tokens 1280 --min-new-tokens 200 \
  --batch-size 2 --grad-accum 32 --eval-batch-size 2 \
  --eval-subset 300 --eval-steps 500 --max-steps 12000 \
  --early-stopping-patience 8 --num-beams 4 \
  --precision auto --grad-checkpointing --optim adafactor
echo "train exit=$?  $(date)"
