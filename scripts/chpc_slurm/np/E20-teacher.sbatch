#!/bin/bash
#SBATCH --job-name=nd-E20-teacher
#SBATCH --account=owner-gpu-guest
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --gres=gpu:a6000:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 12:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E20-teacher.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/np/logs/E20-teacher.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia_q35/bin/python
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E20_teacher_ceiling
# 🔴 E20 stage 1: can a much larger model do register transfer few-shot AT ALL?
# Teacher choice: Qwen3.5-9B rather than the spec's Qwen3-235B. Reasons, stated plainly:
#   * 235B is ~440 GB and needs a whole node; no single card can host it.
#   * The tokenizer measurement makes Qwen3.5 the right family — it needs 294 subword
#     tokens per Bengali answer where Qwen3 needs 689, and E17 already showed Qwen3-14B
#     losing badly on this corpus partly for that reason.
# This is a STAGED probe, not the spec's teacher: if 9B lands nowhere near 0.82 the whole
# "bigger teacher" line is closed cheaply; if it is close, escalating is justified.
# In-context examples come from TRAIN only — the script asserts zero dev overlap.
$PY ../code/12_teacher_probe.py \
  --model Qwen/Qwen3.5-9B --data-dir ../data/draft_only \
  --shots 16 --limit 300 --batch-size 2 --shot-max-chars 600 \
  --max-new-tokens 640 --min-new-tokens 80 \
  --out teacher_qwen35_9b.json
echo "exit=$?  $(date)"
