#!/bin/bash
#SBATCH --job-name=nd-test-E04-conv12k
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:2080ti:1
#SBATCH -c 4
#SBATCH --mem=40G
#SBATCH -t 04:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-test-E04-conv12k.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-test-E04-conv12k.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E04_english_only
$PY ../code/04_decode.py --ckpt conv12k/best --data-dir ../data/english_only \
  --split test --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 \
  --max-new-tokens 320 --batch-size 4 --no-bertscore \
  --out conv12k/submission_e15.csv --record conv12k/test_e15.json
echo "exit=$?  $(date)"
