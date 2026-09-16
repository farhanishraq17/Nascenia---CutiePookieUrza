set -uo pipefail
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E05_train_to_convergence
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
# E15 winner: beam 8 / length_penalty 1.2 / min_new_tokens 0 (the shipped decoder forced
# min_new 80, which padded already-correct-length answers and cost precision).
for split in dev test; do
  if [ "$split" = dev ]; then EX="--limit 300 --record english_draft/dev_e15.json";
  else EX="--out english_draft/submission_e15.csv --record english_draft/test_e15.json"; fi
  $PY ../code/04_decode.py --ckpt english_draft/best --data-dir ../data/english_draft \
    --split $split --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 \
    --max-new-tokens 320 --max-source-len 768 --no-bertscore $EX
  echo "$split exit=$?"
done
