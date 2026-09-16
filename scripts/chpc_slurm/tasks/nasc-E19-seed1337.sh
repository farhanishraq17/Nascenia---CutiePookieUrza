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

cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E19_multiseed_ensemble

# ---- train ------------------------------------------------------------------
# --resume makes a requeued job pick up the last checkpoint instead of restarting.
$PY ../code/02_train_t5.py \
  --data-dir ../data/english_draft \
  --model csebuetnlp/banglat5 \
  --out-dir . --run-name seed1337 \
  --seed 1337 \
  --lr 0.001 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 \
  --batch-size 8 --grad-accum 8 --eval-batch-size 8 \
  --eval-subset 300 --eval-steps 250 --max-steps 12000 \
  --save-total-limit 2 \
  --early-stopping-patience 5 \
  --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length --resume
rc=$?
echo "train exit=$rc"
[ $rc -ne 0 ] && exit $rc

# ---- score on the frozen dev split -------------------------------------------
$PY ../code/04_decode.py --ckpt seed1337/best --data-dir ../data/english_draft \
  --split dev --limit 300 --mode beam --num-beams 4 \
  --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \
  --max-source-len 768 \
  --no-bertscore --record seed1337/dev.json
echo "decode exit=$?"

# ---- test-split predictions, so the arm is submittable without a retrain ------
$PY ../code/04_decode.py --ckpt seed1337/best --data-dir ../data/english_draft \
  --split test --mode beam --num-beams 4 \
  --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \
  --max-source-len 768 \
  --no-bertscore --out seed1337/submission.csv --record seed1337/test.json
echo "test-decode exit=$?  done $(date)"