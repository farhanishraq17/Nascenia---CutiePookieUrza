#!/bin/bash
#SBATCH --job-name=nd-test-E02-conv12k
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:1
#SBATCH --exclude=notch294,notch299
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 06:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-test-E02-conv12k.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/nd-test-E02-conv12k.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E02_add_question
$PY ../code/04_decode.py --ckpt conv12k/best --data-dir ../data/question_draft --split dev --limit 300 \
  --mode beam --num-beams 4 --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \
  --max-source-len 640 --batch-size 4 --no-bertscore --record conv12k/dev.json
$PY ../code/04_decode.py --ckpt conv12k/best --data-dir ../data/question_draft --split test \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --max-source-len 640 --batch-size 4 --no-bertscore \
  --out conv12k/submission_e15.csv --record conv12k/test_e15.json
echo "exit=$?  $(date)"
