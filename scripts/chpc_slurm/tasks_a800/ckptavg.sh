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
cd $P/E15_decode_sweep
C=$P/E05_train_to_convergence/english_draft/ckpt
avg () { n=$1; shift; args=""; for s in "$@"; do args="$args $C/checkpoint-$s"; done
  echo "===== $n : $*"
  $PY $P/code/17_model_soup.py $args --out $P/E15_decode_sweep/ckptavg_$n --data-dir $D || echo "  FAILED $n"; }
avg tail5   11000 11250 11500 11750 12000
avg tail7   10500 10750 11000 11250 11500 11750 12000
avg peak5   11500 11750 12000 12250 12500
avg peak9   11000 11250 11500 11750 12000 12250 12500 12750 13000
avg wide12  9500 10000 10500 11000 11500 11750 12000 12250 12500 13000 13500 14000
echo "done $(date)"
