set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
D=$P/data/english_draft; E=$P/E19_multiseed_ensemble
C=$P/E05_train_to_convergence/english_draft/ckpt
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
$PY $P/code/17_model_soup.py $P/E15_decode_sweep/ckptavg_peak5 $E/sched777/best \
  --out $P/E14_arch_ensemble/peak5_plus_sched777 --data-dir $D || echo "FAILED compose"
$PY $P/code/17_model_soup.py $C/checkpoint-11750 $C/checkpoint-12000 $C/checkpoint-12250 \
  --out $P/E15_decode_sweep/ckptavg_peak3 --data-dir $D || echo "FAILED peak3"
$PY $P/code/17_model_soup.py $C/checkpoint-11250 $C/checkpoint-11500 $C/checkpoint-11750 \
  $C/checkpoint-12000 $C/checkpoint-12250 $C/checkpoint-12500 $C/checkpoint-12750 \
  --out $P/E15_decode_sweep/ckptavg_peak7 --data-dir $D || echo "FAILED peak7"
echo "done $(date)"
