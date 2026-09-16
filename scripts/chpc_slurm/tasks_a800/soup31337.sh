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
$PY $P/code/17_model_soup.py $CH $E/sched31337/best --out ch_31337 --data-dir $D || echo FAILED a
$PY $P/code/17_model_soup.py $CH $E/sched777/best $E/sched31337/best --out ch_777_31337 --data-dir $D || echo FAILED b
echo done
