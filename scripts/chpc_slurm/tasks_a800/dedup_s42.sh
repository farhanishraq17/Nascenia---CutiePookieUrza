set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=6
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cd $P/E23_data_filter
$PY ../code/02_train_t5.py --data-dir ../data/english_draft_dedup --model csebuetnlp/banglat5 \
  --out-dir . --run-name dedup_s42 --seed 42 --lr 1e-3 --warmup 200 --optim adafactor \
  --max-source-len 768 --max-target-len 512 --batch-size 8 --grad-accum 8 --eval-batch-size 8 \
  --eval-subset 300 --eval-steps 250 --max-steps 12000 --save-total-limit 2 \
  --early-stopping-patience 8 --gen-num-beams 4 --gen-min-new-tokens 80 \
  --precision auto --no-group-by-length --resume
rc=$?; echo "train exit=$rc"; [ $rc -ne 0 ] && exit $rc
for SP in dev test; do
  EX=""; [ $SP = dev ] && EX="--limit 300 --record dedup_s42/dev_e15dec.json" || EX="--out dedup_s42/submission.csv --record dedup_s42/test.json"
  $PY ../code/04_decode.py --ckpt dedup_s42/best --data-dir ../data/english_draft_dedup --split $SP \
    --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
    --no-bertscore $EX
done
echo "done $(date)"
