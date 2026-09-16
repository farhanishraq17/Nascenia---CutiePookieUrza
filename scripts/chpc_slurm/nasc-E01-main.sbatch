#!/bin/bash
#SBATCH --job-name=nasc-E01-main
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 3-00:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/nasc-E01-main-%j.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/nasc-E01-main-%j.out
set -uo pipefail

export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
export HF_HUB_OFFLINE=0
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=8
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python

echo "node=$(hostname)  job=$SLURM_JOB_ID  $(date)"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader

cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E01_add_english

# ---- train ------------------------------------------------------------------
# --resume makes a requeued job pick up the last checkpoint instead of restarting.
$PY ../code/02_train_t5.py \
  --data-dir ../data/english_draft \
  --model csebuetnlp/banglat5 \
  --out-dir . --run-name main \
  --seed 11 \
  --lr 0.001 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 \
  --batch-size 32 --grad-accum 2 --eval-batch-size 32 \
  --eval-subset 300 --eval-steps 250 --max-steps 4000 \
  --save-total-limit 2 \
  --early-stopping-patience 5 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length --resume
rc=$?
echo "train exit=$rc"
[ $rc -ne 0 ] && exit $rc

# ---- score on the frozen dev split -------------------------------------------
$PY ../code/04_decode.py --ckpt main/best --data-dir ../data/english_draft \
  --split dev --limit 300 --mode beam --num-beams 4 \
  --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \
  --no-bertscore --record main/dev.json
echo "decode exit=$?"

# ---- test-split predictions, so the arm is submittable without a retrain ------
$PY ../code/04_decode.py --ckpt main/best --data-dir ../data/english_draft \
  --split test --mode beam --num-beams 4 \
  --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \
  --no-bertscore --out main/submission.csv --record main/test.json
echo "test-decode exit=$?  done $(date)"
