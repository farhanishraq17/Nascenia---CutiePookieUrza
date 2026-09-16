set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=6
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E15_decode_sweep
$PY /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/code/14_decode_sweep.py --ckpt /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E19_multiseed_ensemble/seed11/best --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft --max-source-len 768 \
  --beams 8,12,20 --length-penalties 1.0,1.2,1.4,1.6,1.8,2.0,2.4,2.8,3.2 --min-new 0 --max-new 320 \
  --batch-size 8 --verify-top 4 --out sweep2_seed11.json
echo "exit=$? $(date)"
