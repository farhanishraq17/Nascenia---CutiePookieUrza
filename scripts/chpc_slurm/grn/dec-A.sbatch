#!/bin/bash
#SBATCH --job-name=nd-dec-A
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn010
#SBATCH --gres=gpu:l40s:1
#SBATCH -c 6
#SBATCH --mem=40G
#SBATCH -t 08:00:00
#SBATCH --requeue
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-dec-A.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/grn/logs/nd-dec-A.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
echo "node=$(hostname) $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
dec () {   # $1=arm dir (relative to project)  $2=optional data-dir override
  cd $P/$1/..  2>/dev/null || cd $P/$(dirname $1)
  arm=$(basename $1)
  dd=${2:-$($PY -c "import json;print(json.load(open(\"$arm/run.json\"))[\"data_dir\"])")}
  echo "===== $1  data=$dd  $(date)"
  $PY $P/code/04_decode.py --ckpt $arm/best --data-dir $dd --split dev --limit 300 \
    --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
    --no-bertscore --record $arm/dev_e15dec${3:-}.json
  $PY $P/code/04_decode.py --ckpt $arm/best --data-dir $dd --split test \
    --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
    --no-bertscore --out $arm/submission${3:-}.csv --record $arm/test${3:-}.json
}
dec E07_no_truncation/conv12k
# E13's outstanding deliverable: can the multitask model answer from the QUESTION alone?
dec E13_multitask_qa/conv12k ../data/question_only _qonly
echo "done $(date)"
