#!/bin/bash
#SBATCH --job-name=nd-e23redec-b
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --gres=gpu:l40s:1
#SBATCH -c 8
#SBATCH --mem=56G
#SBATCH -t 08:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/e23redec-b.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/e23redec-b.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E23_data_filter

echo "===== len40"
$PY ../code/04_decode.py --ckpt len40/best --data-dir ../data/english_draft_len40 --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record len40/dev_e15dec.json
$PY ../code/04_decode.py --ckpt len40/best --data-dir ../data/english_draft_len40 --split test \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --out len40/submission_e15.csv --record len40/test_e15.json
echo "===== len40_s23"
$PY ../code/04_decode.py --ckpt len40_s23/best --data-dir ../data/english_draft_len40 --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record len40_s23/dev_e15dec.json
$PY ../code/04_decode.py --ckpt len40_s23/best --data-dir ../data/english_draft_len40 --split test \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --out len40_s23/submission_e15.csv --record len40_s23/test_e15.json
echo "===== len60"
$PY ../code/04_decode.py --ckpt len60/best --data-dir ../data/english_draft_len60 --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record len60/dev_e15dec.json
$PY ../code/04_decode.py --ckpt len60/best --data-dir ../data/english_draft_len60 --split test \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --out len60/submission_e15.csv --record len60/test_e15.json
echo "done $(date)"
