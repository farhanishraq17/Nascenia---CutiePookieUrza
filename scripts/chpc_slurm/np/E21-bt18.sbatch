#!/bin/bash
#SBATCH --job-name=nd-E21-bt18
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:1
#SBATCH --exclude=notch294,notch299
#SBATCH -c 4
#SBATCH --mem=40G
#SBATCH -t 12:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E21-bt18.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E21-bt18.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E21_synthetic_pairs
$PY ../code/18_backtranslate.py --shard 18 --num-shards 20 --out bt --batch-size 24
echo "exit=$?  $(date)"
