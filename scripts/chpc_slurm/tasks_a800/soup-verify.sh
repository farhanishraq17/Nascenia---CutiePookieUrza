set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
D=$P/data/english_draft
E=$P/E19_multiseed_ensemble
CH=$P/E05_train_to_convergence/english_draft/best
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cd $P/E14_arch_ensemble
# greedy soup = champion + sched777, dev[0:300] 0.8345 vs champion 0.8328 (+0.0017,
# INSIDE the 0.0044 noise floor). Score it on the disjoint rows before spending a
# Kaggle submission on it.
$PY $P/code/14_decode_sweep.py --ckpt $P/E14_arch_ensemble/soup_greedy_champ \
  --data-dir $D --max-source-len 768 --beams 8 --length-penalties 1.2 --min-new 0 \
  --max-new 320 --batch-size 8 --verify-top 1 --out $P/E15_decode_sweep/verify_soupwin.json
# and the champion itself on the SAME two subsets, so the comparison is like-for-like
$PY $P/code/14_decode_sweep.py --ckpt $CH --data-dir $D \
  --beams 8 --length-penalties 1.2 --min-new 0 --max-new 320 --batch-size 8 \
  --verify-top 1 --out $P/E15_decode_sweep/verify_champ.json
echo "done $(date)"
