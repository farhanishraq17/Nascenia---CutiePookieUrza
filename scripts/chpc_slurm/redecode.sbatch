#!/bin/bash
#SBATCH --job-name=nasc-redecode
#SBATCH --account=kmarino
#SBATCH --partition=granite-gpu
#SBATCH --qos=granite-gpu-freecycle
#SBATCH --nodelist=grn008
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 04:00:00
#SBATCH -o /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/redecode-%j.out
#SBATCH -e /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm/logs/redecode-%j.out
set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
echo "node=$(hostname) $(date)"

# Arms decoded before the --max-source-len fix: their source was cut to 384 at inference
# while they trained at 768 / 640. Re-score at the cap they trained at.
redo () {   # $1=expdir  $2=data  $3=src
  cd $P/$1
  echo "===== $1  data=$2  max_source_len=$3"
  $PY ../code/04_decode.py --ckpt main/best --data-dir ../data/$2 \
    --split dev --limit 300 --mode beam --num-beams 4 \
    --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \
    --max-source-len $3 --no-bertscore --record main/dev.json
  $PY ../code/04_decode.py --ckpt main/best --data-dir ../data/$2 \
    --split test --mode beam --num-beams 4 \
    --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \
    --max-source-len $3 --no-bertscore --out main/submission.csv --record main/test.json
}
redo E01_add_english english_draft 768
redo E02_add_question question_draft 640
echo "redecode done $(date)"
