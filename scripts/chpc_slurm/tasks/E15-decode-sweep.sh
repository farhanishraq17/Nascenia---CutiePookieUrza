set -uo pipefail
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E15_decode_sweep
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
# Swept on the program's best checkpoint: E05/english_draft (Token F1 0.8257).
$PY ../code/14_decode_sweep.py \
  --ckpt ../E05_train_to_convergence/english_draft/best \
  --data-dir ../data/english_draft \
  --beams 4,8,12 --length-penalties 0.6,0.8,1.0,1.2 --min-new 0,40,60,80 \
  --subset 300 --verify-top 3 --batch-size 16 --out sweep.json
echo "sweep exit=$?  $(date)"
