set -uo pipefail
PY=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
cd /scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/E15_decode_sweep
echo "node=$(hostname) gpu=$CUDA_VISIBLE_DEVICES seed1337 $(date)"
DATA=../data/english_draft; case "seed1337" in E03conv) DATA=../data/all_inputs;; esac
$PY ../code/04_decode.py --ckpt ../E19_multiseed_ensemble/seed1337/best --data-dir $DATA \
  --split dev --limit 300 --mode beam --num-beams 8 --length-penalty 1.2 \
  --min-new-tokens 0 --max-new-tokens 320 --no-bertscore --record dev_e15dec_seed1337.json
echo "seed1337 exit=$?"
