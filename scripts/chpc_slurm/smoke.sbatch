#!/bin/bash
#SBATCH --job-name=nasc-smoke
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/smoke-%j.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/smoke-%j.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname)  $(date)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
$PY -c "import torch;c=torch.cuda.get_device_capability();print('sm_%d%d'%c,'bf16-hw',c[0]>=8)"
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm
# Plumbing only: the score is meaningless (LR never leaves warmup). Success = no crash.
$PY ../code/02_train_t5.py --data-dir ../data/draft_only --out-dir ./_smoke \
  --smoke --max-train 1000 --epochs 1 --batch-size 8 --grad-accum 2 \
  --eval-subset 100 --eval-steps 20 --eval-batch-size 8 --gen-num-beams 2 \
  --no-bertscore-eval --run-name smoke
echo "smoke train exit=$?"
$PY ../code/04_decode.py --ckpt ./_smoke/smoke/best --data-dir ../data/draft_only \
  --split dev --limit 32 --mode beam --num-beams 2 --min-new-tokens 80 \
  --max-new-tokens 320 --no-bertscore --record ./_smoke/dev.json
echo "smoke decode exit=$?  $(date)"
