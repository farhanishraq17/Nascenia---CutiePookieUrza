#!/bin/bash
#SBATCH --job-name=nd-soup-uniform
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:3090:1
#SBATCH -c 6
#SBATCH --mem=48G
#SBATCH -t 04:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-soup-uniform.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-soup-uniform.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
$PY code/17_model_soup.py /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E19_multiseed_ensemble/seed*/best \
  --out /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E14_arch_ensemble/soup_uniform --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft
echo "exit=$?"
