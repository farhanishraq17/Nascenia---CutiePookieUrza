#!/bin/bash
#SBATCH --job-name=nd-E04-conv12k
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:2080ti:1
#SBATCH -c 4
#SBATCH --mem=40G
#SBATCH -t 03:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-E04-conv12k.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-E04-conv12k.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E04_english_only
# 2080ti is sm_75 -> fp32, exactly the precision the 0.85030 model was trained in.
# E15 winner: beam 8 / lp 1.2 / min_new 0. batch 4 keeps it inside 11 GB.
$PY ../code/04_decode.py --ckpt conv12k/best --data-dir ../data/english_only \
  --split dev --limit 300 --mode beam --num-beams 8 --length-penalty 1.2 \
  --min-new-tokens 0 --max-new-tokens 320 --batch-size 4 \
  --no-bertscore --record conv12k/dev_e15dec.json
echo "exit=$?  $(date)"
