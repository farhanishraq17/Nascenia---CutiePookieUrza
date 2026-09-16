set -uo pipefail
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E18_model_zoo
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
for split in dev test; do
  if [ "$split" = dev ]; then EXTRA="--limit 300 --record indicbart/dev.json";
  else EXTRA="--out indicbart/submission.csv --record indicbart/test.json"; fi
  $PY ../code/04_decode.py --ckpt indicbart/best --data-dir ../data/draft_only \
    --split $split --mode beam --num-beams 4 --min-new-tokens 80 \
    --max-new-tokens 320 --length-penalty 1.0 --max-source-len 384 \
    --no-bertscore $EXTRA
  echo "$split decode exit=$?"
done
