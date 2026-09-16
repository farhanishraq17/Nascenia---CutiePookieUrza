set -uo pipefail
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
S=$P/E14_arch_ensemble/soup_greedy_champ
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES $(date)"
$PY - <<'PY' || exit 1
import json
from pathlib import Path
S = Path("/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E14_arch_ensemble/soup_greedy_champ")
got = json.loads((S/"dev_e15dec.json").read_text())["dev"]["token_f1"]
exp = json.loads((S/"soup.json").read_text())["dev_token_f1"]
print(f"decoded dev Token F1 {got:.6f} vs soup-time {exp:.6f}  delta {got-exp:+.2e}")
assert abs(got-exp) < 0.005, "🔴 decoded dev does not reproduce the soup score — DO NOT SUBMIT"
print("gate passed")
PY
cd $P/E14_arch_ensemble
$PY $P/code/04_decode.py --ckpt $S --data-dir $P/data/english_draft --split test \
  --mode beam --num-beams 8 --length-penalty 1.2 --min-new-tokens 0 --max-new-tokens 320 \
  --max-source-len 768 --no-bertscore --out $S/submission.csv --record $S/test.json
echo "test-decode exit=$?  $(date)"
