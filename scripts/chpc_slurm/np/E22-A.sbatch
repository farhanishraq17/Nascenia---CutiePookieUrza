#!/bin/bash
#SBATCH --job-name=nd-E22-A
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:a6000:1
#SBATCH --exclude=notch294,notch299
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 12:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E22-A.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E22-A.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia_q35/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E22_retrieval
# arm A: identical to E20 stage 1 EXCEPT the in-context examples are the query's nearest
# TRAIN neighbours rather than a fixed random draw. Compare against E20's 0.5841.
$PY ../code/12_teacher_probe.py --model Qwen/Qwen3.5-9B --data-dir ../data/draft_only \
  --shots 16 --limit 300 --batch-size 2 --shot-max-chars 600 \
  --max-new-tokens 640 --min-new-tokens 80 \
  --knn-file knn16.json --out teacher_knn_qwen35_9b.json
echo "exit=$?  $(date)"
