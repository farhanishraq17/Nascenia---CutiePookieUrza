#!/bin/bash
#SBATCH --job-name=nd-E21-A2
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --gres=gpu:l40s:1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 1-00:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/re-E21-A2.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/re-E21-A2.out
set -uo pipefail
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
bash /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/tasks/nasc-E21-A2.sh
rc=$?; echo "task exit=$rc"
/scratch/general/nfs1/u1592009/envs/nascenia/bin/python /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/code/04_decode.py \
  --ckpt /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E21_synthetic_pairs/A2/best --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft_a2 --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E21_synthetic_pairs/A2/dev_e15dec.json
echo "e15 exit=$?  $(date)"
