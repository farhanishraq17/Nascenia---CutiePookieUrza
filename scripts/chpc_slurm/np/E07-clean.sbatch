#!/bin/bash
#SBATCH --job-name=nd-E07-clean
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:3090:1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 2-00:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E07-clean.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E07-clean.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E07_no_truncation
# 3090 = sm_86 -> bf16. 24 GB at 1280/768 needs batch 2; effective batch stays 64.
# NO --resume: the previous run inherited a reset early-stopping counter from a mid-run
# restart and stopped at a stale "best" (peak step 1500, 0.7911). This must start clean.
$PY ../code/02_train_t5.py \
  --data-dir ../data/all_inputs --model csebuetnlp/banglat5 \
  --out-dir . --run-name conv12k --seed 11 \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 1280 --max-target-len 768 \
  --batch-size 2 --grad-accum 32 --eval-batch-size 2 \
  --eval-subset 300 --eval-steps 250 --max-steps 12000 \
  --save-total-limit 2 --early-stopping-patience 8 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length
rc=$?; echo "train exit=$rc"; [ $rc -ne 0 ] && exit $rc
$PY ../code/04_decode.py --ckpt conv12k/best --data-dir ../data/all_inputs \
  --split dev --limit 300 --mode beam --num-beams 8 --length-penalty 1.2 \
  --min-new-tokens 0 --max-new-tokens 320 --max-source-len 1280 \
  --no-bertscore --record conv12k/dev_e15dec.json
echo "done $(date)"
