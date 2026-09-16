set -uo pipefail
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E15_decode_sweep
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES E03conv $(date)"
DATA=../data/english_draft; case "E03conv" in E03conv) DATA=../data/all_inputs;; esac
$PY ../code/04_decode.py --ckpt ../E03_all_inputs/conv12k/best --data-dir $DATA \
  --split dev --limit 300 --mode beam --num-beams 8 --length-penalty 1.2 \
  --min-new-tokens 0 --max-new-tokens 320 --no-bertscore --record dev_e15dec_E03conv.json
echo "E03conv exit=$?"
