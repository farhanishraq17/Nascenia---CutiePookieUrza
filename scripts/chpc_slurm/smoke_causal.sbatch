#!/bin/bash
#SBATCH --job-name=nasc-smoke-causal
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 00:50:00
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/smoke-causal-%j.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/smoke-causal-%j.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm
$PY ../code/03_train_causal.py --data-dir ../data/draft_only --model Qwen/Qwen3-0.6B \
  --out-dir ./_smoke --run-name smoke_causal --smoke \
  --batch-size 2 --grad-accum 2 --eval-batch-size 4 --max-len 1024 \
  --num-beams 2 --min-new-tokens 40 --max-new-tokens 96
echo "causal smoke exit=$?  $(date)"
