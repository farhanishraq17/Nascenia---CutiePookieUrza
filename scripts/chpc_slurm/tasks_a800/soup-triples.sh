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
for m in seed11 seed1337 seed42 seed21 seed314 seed2024; do
  echo "===== champion + sched777 + $m"
  $PY $P/code/17_model_soup.py $CH $E/sched777/best $E/$m/best \
    --out $P/E14_arch_ensemble/tri_$m --data-dir $D || echo "  FAILED $m"
done
echo "done $(date)"
