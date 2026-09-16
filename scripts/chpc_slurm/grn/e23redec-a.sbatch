#!/bin/bash
#SBATCH --job-name=nd-e23redec-a
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --gres=gpu:l40s:1
#SBATCH -c 8
#SBATCH --mem=56G
#SBATCH -t 08:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/e23redec-a.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/e23redec-a.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E23_data_filter

echo "===== clean"
$PY ../code/04_decode.py --ckpt clean/best --data-dir ../data/english_draft_clean --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record clean/dev_e15dec.json
$PY ../code/04_decode.py --ckpt clean/best --data-dir ../data/english_draft_clean --split test \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --out clean/submission_e15.csv --record clean/test_e15.json
echo "===== len20"
$PY ../code/04_decode.py --ckpt len20/best --data-dir ../data/english_draft_len20 --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record len20/dev_e15dec.json
$PY ../code/04_decode.py --ckpt len20/best --data-dir ../data/english_draft_len20 --split test \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --out len20/submission_e15.csv --record len20/test_e15.json
echo "done $(date)"
