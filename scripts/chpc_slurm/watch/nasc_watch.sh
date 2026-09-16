#!/bin/bash
# nasc_watch.sh — keeps the Nascenia task set alive on the a800 allocation.
#
#   tmux new-session -d -s nasc-watch 'bash _slurm/watch/nasc_watch.sh'
#
# What it does every cycle:
#   1. reads _slurm/watch/tasks.list  (one task name per line, scripts in _slurm/tasks_a800/)
#   2. a task is DONE if its log ends with "done " / "exit=0"; RUNNING if a matching python
#      process is alive; otherwise it is DEAD and gets relaunched on a free GPU.
#   3. GPUs are claimed by UUID — indices are NOT stable across srun steps, and a probe that
#      says "index 3 is idle" can hand you a card another step has 33 GB on.
#   4. a GPU counts as free below FREE_MB, so a card another user is filling is never taken.
#      Every OOM in this project came from landing on an already-occupied card.
#
# 🔴 never pkill -f a task name: this script's own argv contains every task name, so the
#    pattern matches the watcher and kills it. Kill by PID only.
set -uo pipefail
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
JOBID=${NASC_ALLOC:-1758640}
FREE_MB=${FREE_MB:-2000}
INTERVAL=${INTERVAL:-300}
LOG=$P/_slurm/watch/watch.log
mkdir -p "$(dirname "$LOG")"
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

free_gpus () {   # -> UUIDs of cards under FREE_MB, newline separated
  srun --jobid=$JOBID --overlap -n1 nvidia-smi \
       --query-gpu=uuid,memory.used --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' -v m=$FREE_MB '$2+0 < m {print $1}'
}

task_state () {  # $1=task -> done|running|dead
  local t=$1 lg=$P/_slurm/logs_a800/$t.out
  if [ -f "$lg" ] && tail -3 "$lg" 2>/dev/null | grep -qE "^done |exit=0 |test-decode exit=0"; then
    echo done; return; fi
  # a live task owns a python process whose argv names its own directory or run-name
  if srun --jobid=$JOBID --overlap -n1 pgrep -f "run-name $t|/$t\.sh|--out .*$t" >/dev/null 2>&1; then
    echo running; return; fi
  echo dead
}

say "watcher up — alloc $JOBID, interval ${INTERVAL}s, free threshold ${FREE_MB}MB"
while true; do
  [ -f "$P/_slurm/watch/STOP" ] && { say "STOP file present — exiting"; exit 0; }
  mapfile -t TASKS < <(grep -vE '^\s*#|^\s*$' "$P/_slurm/watch/tasks.list" 2>/dev/null)
  mapfile -t GPUS < <(free_gpus)
  gi=0; ndone=0; nrun=0; nrelaunched=0
  for t in "${TASKS[@]}"; do
    case "$(task_state "$t")" in
      done)    ndone=$((ndone+1)) ;;
      running) nrun=$((nrun+1)) ;;
      dead)
        [ -f "$P/_slurm/tasks_a800/$t.sh" ] || { say "  ! no script for $t"; continue; }
        u=${GPUS[$gi]:-}
        [ -z "$u" ] && { say "  · $t dead, no free GPU — will retry"; continue; }
        gi=$((gi+1)); nrelaunched=$((nrelaunched+1))
        tmux kill-window -t nasc-a800:"$t" 2>/dev/null
        tmux new-window -d -t nasc-a800 -n "$t" \
          "srun --jobid=$JOBID --overlap -n1 --cpus-per-task=6 bash -c 'export CUDA_VISIBLE_DEVICES=$u; bash $P/_slurm/tasks_a800/$t.sh' > $P/_slurm/logs_a800/$t.out 2>&1"
        say "  ↻ relaunched $t on ${u#GPU-}"
        ;;
    esac
  done
  say "done=$ndone running=$nrun relaunched=$nrelaunched free_gpus=${#GPUS[@]}"
  sleep "$INTERVAL"
done
