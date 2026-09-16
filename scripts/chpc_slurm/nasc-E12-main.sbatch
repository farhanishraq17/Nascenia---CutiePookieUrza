#!/bin/bash
#SBATCH --job-name=nasc-E12-main
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 3-00:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/nasc-E12-main-%j.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/nasc-E12-main-%j.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=8
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E12_warmstart
echo "node=$(hostname) job=$SLURM_JOB_ID $(date)"

# E12 is a two-STAGE curriculum, which is why it is not a registry arm: stage 2's --model
# is stage 1's checkpoint, a path that does not exist until stage 1 finishes.
#
# Stage 1 — Bengali medical warm start (123,289 curated Q->A rows, dev/test ids removed).
# Scored on the WINNER's frozen dev split throughout, so stage 1 and stage 2 sit on one
# comparable axis and the curriculum's effect is visible rather than inferred.
$PY ../code/02_train_t5.py \
  --data-dir ../data/warmstart_stage1 --model csebuetnlp/banglat5 \
  --out-dir . --run-name stage1 --seed 11 \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 \
  --batch-size 32 --grad-accum 2 --eval-batch-size 32 \
  --eval-subset 300 --eval-steps 250 --max-steps 4000 \
  --save-total-limit 2 --early-stopping-patience 5 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length --resume
rc=$?; echo "stage1 exit=$rc"; [ $rc -ne 0 ] && exit $rc

# Stage 2 — the transfer task, starting from those weights instead of vanilla BanglaT5.
# Everything else matches the Tier-1 winner exactly, so the warm start is the only variable.
$PY ../code/02_train_t5.py \
  --data-dir ../data/english_draft --model ./stage1/best \
  --out-dir . --run-name main --seed 11 \
  --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 \
  --batch-size 32 --grad-accum 2 --eval-batch-size 32 \
  --eval-subset 300 --eval-steps 250 --max-steps 4000 \
  --save-total-limit 2 --early-stopping-patience 5 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length --resume
rc=$?; echo "stage2 exit=$rc"; [ $rc -ne 0 ] && exit $rc

$PY ../code/04_decode.py --ckpt main/best --data-dir ../data/english_draft \
  --split dev --limit 300 --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --max-source-len 768 \
  --no-bertscore --record main/dev.json
$PY ../code/04_decode.py --ckpt main/best --data-dir ../data/english_draft \
  --split test --mode beam --num-beams 4 --min-new-tokens 80 \
  --max-new-tokens 320 --length-penalty 1.0 --max-source-len 768 \
  --no-bertscore --out main/submission.csv --record main/test.json
echo "E12 done $(date)"
