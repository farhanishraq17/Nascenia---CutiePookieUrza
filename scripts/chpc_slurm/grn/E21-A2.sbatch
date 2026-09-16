#!/bin/bash
#SBATCH --job-name=nd-E21-A2
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn009
#SBATCH --gres=gpu:l40s:1
#SBATCH -c 8
#SBATCH --mem=44G
#SBATCH -t 1-12:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-E21-A2.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-E21-A2.out
set -uo pipefail
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
bash /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/tasks/nasc-E21-A2.sh
# the shipped E15 decoder — the champion's 0.8328 is on this path, so the
# comparison has to be made here and not on the old beam-4/min-80 record.
/scratch/general/nfs1/u1592009/envs/nascenia/bin/python /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/code/04_decode.py \
  --ckpt /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E21_synthetic_pairs/A2/best --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft_a2 --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E21_synthetic_pairs/A2/dev_e15dec.json
echo "e15-decode exit=$?  $(date)"
