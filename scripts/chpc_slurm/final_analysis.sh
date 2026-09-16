#!/bin/bash
# final_analysis.sh — every number the write-up needs, computed in parallel across cores.
#
#   srun --jobid=<alloc> --overlap -c 16 bash final_analysis.sh
#
# All CPU: the models are already trained and every arm's predictions are on disk, so this
# is scoring and aggregation only. Runs the independent analyses concurrently and waits.
set -uo pipefail
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
V=/scratch/general/nfs1/u1592009/envs/nascenia/bin/python
OUT=$P/_slurm/analysis; mkdir -p "$OUT"
export HF_HOME=/scratch/general/nfs1/u1592009/huggingface
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
cd "$P"
echo "cores: $(nproc)  node: $(hostname)  $(date)"

# ---- 1. scoreboard over every arm that has a dev record ----------------------
( $V _slurm/collect.py > "$OUT/scoreboard.md" 2>&1
  $V _slurm/collect.py --json > "$OUT/scoreboard.json" 2>&1
  echo "  [1] scoreboard done" ) &

# ---- 2. Phase-2 audit across every arm with test predictions -----------------
# includes the reference + draft baselines, without which the rates are uninterpretable
( recs=$(ls E*/*/test_e15.json E*/*/test.json E16_phase2_audit/_baselines/*/test.json 2>/dev/null)
  $V code/15_phase2_audit.py $recs --out "$OUT/audit_all.json" > "$OUT/audit_all.md" 2>&1
  echo "  [2] phase-2 audit done" ) &

# ---- 3. pooled-MBR gate over every E15-decoded member ------------------------
( recs=$(ls E05_train_to_convergence/english_draft/dev_e15.json E*/*/dev_e15dec.json 2>/dev/null)
  $V code/13_disagreement.py $recs --refs-from data/english_draft \
      > "$OUT/disagreement.md" 2>&1
  $V code/16_pool_mbr.py $recs --refs-from data/english_draft \
      > "$OUT/pool_mbr.md" 2>&1
  echo "  [3] ensemble gates done" ) &

# ---- 4. truncation audit (all datasets x both tokenizers) --------------------
( $V code/10_truncation_report.py --sample 20000 --out "$OUT/truncation.json" \
      > "$OUT/truncation.md" 2>&1
  echo "  [4] truncation done" ) &

# ---- 5. per-arm trajectories + peak steps, straight from trainer_state -------
( $V - <<'PY' > "$OUT/trajectories.md" 2>&1
import json, glob
from pathlib import Path
P=Path("/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project")
rows=[]
for rj in sorted(P.glob("E*/*/run.json")):
    d=json.loads(rj.read_text()); arm=rj.parent
    st=sorted(arm.glob("ckpt/checkpoint-*/trainer_state.json"),
              key=lambda p:int(p.parent.name.split("-")[-1]))
    hist=[]
    if st: hist=[h for h in json.loads(st[-1].read_text())["log_history"] if "eval_token_f1" in h]
    elif (arm/"trainer_state.json").is_file():
        hist=[h for h in json.loads((arm/"trainer_state.json").read_text()).get("log_history",[]) if "token_f1" in h]
    if not hist: continue
    k="eval_token_f1" if "eval_token_f1" in hist[0] else "token_f1"
    best=max(hist,key=lambda h:h[k])
    rows.append((f"{arm.parent.name.split('_')[0]}/{arm.name}", d.get("model","?").split("/")[-1],
                 d.get("max_steps"), best["step"], round(best[k],4), len(hist),
                 round(d.get("train_minutes",0)/60,2)))
rows.sort(key=lambda r:-r[4])
print("| arm | model | budget | peak step | best F1 | evals | hours |")
print("|"+"---|"*7)
for r in rows: print("| "+" | ".join(str(x) for x in r)+" |")
PY
  echo "  [5] trajectories done" ) &

wait
echo "ALL ANALYSES COMPLETE $(date)"
ls -la "$OUT"
