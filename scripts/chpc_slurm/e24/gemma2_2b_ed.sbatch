#!/bin/bash
#SBATCH --job-name=nd-e24-gemma2_2b_ed
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:a40:1
#SBATCH --exclude=notch294,notch299

#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 1-00:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E24_model_size/logs/gemma2_2b_ed.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E24_model_size/logs/gemma2_2b_ed.out
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
  --data-dir ../data/english_draft --model google/gemma-2-2b-it \
  --out-dir . --run-name gemma2_2b_ed --seed 11 \
  --lr 2e-05 --warmup 200 \
  --max-len 2048 --max-new-tokens 768 --min-new-tokens 150 \
  --batch-size 1 --grad-accum 64 --eval-batch-size 2 \
  --eval-subset 300 --eval-steps 500 --max-steps 12000 \
  --early-stopping-patience 8 --num-beams 4 \
  --precision auto --grad-checkpointing --optim adafactor
echo "train exit=$?  $(date)"
