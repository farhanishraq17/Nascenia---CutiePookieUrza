#!/bin/bash
#SBATCH --job-name=nd-soup-top3
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:3090:1
#SBATCH -c 6
#SBATCH --mem=48G
#SBATCH -t 03:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-soup-top3.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-soup-top3.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
$PY code/17_model_soup.py \
  /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E05_train_to_convergence/english_draft/best \
  /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E19_multiseed_ensemble/seed11/best /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E19_multiseed_ensemble/seed1337/best \
  --out /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E14_arch_ensemble/soup_top3 --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft
echo "exit=$?"
