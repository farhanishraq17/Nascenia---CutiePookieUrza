set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=6
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E14_arch_ensemble
E=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E19_multiseed_ensemble
ORD="/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E05_train_to_convergence/english_draft/best $E/seed1337/best $E/seed42/best $E/sched777/best $E/seed2024/best $E/seed11/best $E/seed23/best $E/seed21/best $E/seed555/best $E/seed99/best $E/seed314/best $E/seed7/best"
echo "===== greedy soup, seeded from the CHAMPION (0.8328) not seed11"
$PY /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/code/17_model_soup.py $ORD --greedy --out soup_greedy_champ --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft
for K in 2 4 5 6 8; do
  echo "===== uniform top-$K"
  $PY /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/code/17_model_soup.py $(echo $ORD | cut -d" " -f1-$K) --out soup_top$K --data-dir /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/data/english_draft
done
echo "done $(date)"
