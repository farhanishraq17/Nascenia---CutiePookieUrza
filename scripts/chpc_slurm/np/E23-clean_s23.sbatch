#!/bin/bash
#SBATCH --job-name=nd-E23-clean_s23
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:3090:1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 1-12:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E23-clean_s23.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E23-clean_s23.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E23_data_filter
$PY ../code/02_train_t5.py --data-dir ../data/english_draft_clean --model csebuetnlp/banglat5 \
  --out-dir . --run-name clean_s23 --seed 23 --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 --batch-size 4 --grad-accum 16 --eval-batch-size 4 \
  --eval-subset 300 --eval-steps 250 --max-steps 12000 --save-total-limit 2 \
  --early-stopping-patience 8 --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length --resume
rc=$?; echo "train exit=$rc"; [ $rc -ne 0 ] && exit $rc
$PY ../code/04_decode.py --ckpt clean_s23/best --data-dir ../data/english_draft_clean \
  --split dev --limit 300 --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 \
  --max-new-tokens 320 --max-source-len 768 --no-bertscore --record clean_s23/dev_e15dec.json
echo "done $(date)"
