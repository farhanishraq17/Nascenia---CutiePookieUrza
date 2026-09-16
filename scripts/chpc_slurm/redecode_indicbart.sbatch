#!/bin/bash
#SBATCH --job-name=nasc-E18-indicbart-dec
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/redecode-indicbart-%j.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/redecode-indicbart-%j.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E18_model_zoo
echo "node=$(hostname) $(date)"
# Trained fine, then decode died: Albert tokenizer emits token_type_ids, MBart.forward()
# rejects them. 04_decode.py now drops keys the model cannot accept.
$PY ../code/04_decode.py --ckpt indicbart/best --data-dir ../data/draft_only \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --max-source-len 384 \
  --no-bertscore --record indicbart/dev.json
echo "dev decode exit=$?"
$PY ../code/04_decode.py --ckpt indicbart/best --data-dir ../data/draft_only \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --max-source-len 384 \
  --no-bertscore --out indicbart/submission.csv --record indicbart/test.json
echo "test decode exit=$?  done $(date)"
