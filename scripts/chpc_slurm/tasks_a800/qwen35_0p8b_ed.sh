set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=6
PY=/scratch/general/nfs1/u1592009/envs/nascenia_q35/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cd $P/E24_model_size
$PY ../code/03_train_causal.py \
  --data-dir ../data/english_draft --model Qwen/Qwen3.5-0.8B \
  --out-dir . --run-name qwen35_0p8b_ed --seed 11 \
  --lr 2e-05 --warmup 200 \
  --max-len 3072 --max-new-tokens 1280 --min-new-tokens 200 \
  --batch-size 2 --grad-accum 32 --eval-batch-size 2 \
  --eval-subset 300 --eval-steps 500 --max-steps 12000 \
  --early-stopping-patience 8 --num-beams 4 \
  --precision auto --grad-checkpointing --optim adafactor
echo "train exit=$?  done $(date)"
