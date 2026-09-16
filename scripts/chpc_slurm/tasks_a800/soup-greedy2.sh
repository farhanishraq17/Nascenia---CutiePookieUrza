set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
D=$P/data/english_draft; E=$P/E19_multiseed_ensemble
CH=$P/E05_train_to_convergence/english_draft/best
PK=$P/E15_decode_sweep/ckptavg_peak5
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cd $P/E14_arch_ensemble
# greedy seeded from the best artefact found (peak5 0.8348), over the whole
# same-schedule family plus the two seeds that ever beat the champion
$PY $P/code/17_model_soup.py $PK $E/sched777/best $E/sched31337/best $CH \
  $E/seed11/best $E/seed21/best --greedy --out greedy_from_peak5 --data-dir $D || echo FAILED
echo done
