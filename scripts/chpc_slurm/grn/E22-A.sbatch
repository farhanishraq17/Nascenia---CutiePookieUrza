#!/bin/bash
#SBATCH --job-name=nd-E22-A
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn010
#SBATCH --gres=gpu:l40s:1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 12:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-E22-A.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-E22-A.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
PY=/scratch/general/nfs1/u1592009/envs/nascenia_q35/bin/python
cd $P/E22_retrieval
$PY ../code/12_teacher_probe.py --model Qwen/Qwen3.5-9B --data-dir ../data/draft_only \
  --shots 16 --limit 300 --batch-size 2 --shot-max-chars 600 \
  --max-new-tokens 640 --min-new-tokens 80 \
  --knn-file knn16.json --out teacher_knn_qwen35_9b.json
echo "exit=$?  $(date)"
