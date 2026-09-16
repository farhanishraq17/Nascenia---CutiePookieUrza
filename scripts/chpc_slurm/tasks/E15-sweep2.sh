set -uo pipefail
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E15_decode_sweep
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
$PY ../code/14_decode_sweep.py --ckpt ../E05_train_to_convergence/english_draft/best \
  --data-dir ../data/english_draft \
  --beams 8,12 --length-penalties 0.4,0.8,1.2,1.6,2.0 --min-new 0 \
  --max-new 192,256,320,448 --subset 300 --verify-top 4 --batch-size 12 --out sweep2.json
echo "sweep2 exit=$?  $(date)"
