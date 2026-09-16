#!/bin/bash
#SBATCH --job-name=nd-E22-B
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn009
#SBATCH --gres=gpu:l40s:1
#SBATCH -c 8
#SBATCH --mem=44G
#SBATCH -t 1-12:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-E22-B.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-E22-B.out
set -uo pipefail
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
bash /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/tasks/nasc-E22-B.sh
# the shipped E15 decoder — the champion's 0.8328 is on this path, so the
# comparison has to be made here and not on the old beam-4/min-80 record.
/scratch/general/nfs1/u1592009/envs/nascenia/bin/python /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/code/04_decode.py \
  --ckpt /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E22_retrieval/B/best --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft_rag --split dev --limit 300 \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --no-bertscore --record /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E22_retrieval/B/dev_e15dec.json
echo "e15-decode exit=$?  $(date)"
