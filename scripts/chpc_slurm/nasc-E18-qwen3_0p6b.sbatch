#!/bin/bash
#SBATCH --job-name=nasc-E18-qwen3_0p6b
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 3-00:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/nasc-E18-qwen3_0p6b-%j.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/nasc-E18-qwen3_0p6b-%j.out
set -uo pipefail

export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
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
  --model Qwen/Qwen3-0.6B \
  --out-dir . --run-name qwen3_0p6b \
  --seed 11 \
  --lr 3e-05 --warmup 200 \
  --max-len 1024 \
  --batch-size 8 --grad-accum 8 --eval-batch-size 8 \
  --eval-subset 300 --eval-steps 250 --max-steps 4000 \
  --early-stopping-patience 5 \
  --num-beams 4 --min-new-tokens 80 --max-new-tokens 320 \
  --precision auto --grad-checkpointing
echo "train exit=$?  done $(date)"
