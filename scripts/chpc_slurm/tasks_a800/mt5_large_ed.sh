set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=6
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cd $P/E24_model_size
$PY ../code/02_train_t5.py --data-dir ../data/english_draft --model google/mt5-large \
  --out-dir . --run-name mt5_large_ed --seed 11 --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 1024 --max-target-len 640 --batch-size 2 --grad-accum 32 --eval-batch-size 4 \
  --eval-subset 300 --eval-steps 500 --max-steps 12000 --save-total-limit 2 \
  --early-stopping-patience 8 --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length --resume
echo "train exit=$?  done $(date)"
