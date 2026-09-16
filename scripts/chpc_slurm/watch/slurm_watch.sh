#!/bin/bash
# slurm_watch.sh — resubmits ONLY the sbatch jobs named in slurm_tasks.list.
#
# 🔴 whitelist, never a glob over *.sbatch. The first version globbed, and resubmitted arms
# that were already running as a800 tmux tasks — two trainers writing one out-dir. The a800
# tasks belong to nasc_watch.sh; this watcher must never see them.
# Every arm runs with --resume, so a resubmission continues from its last checkpoint.
set -uo pipefail
P=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project
LOG=$P/_slurm/watch/slurm_watch.log
INTERVAL=${INTERVAL:-420}
say () { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
declare -A TRIES
say "slurm watcher up (whitelist mode)"
while true; do
  [ -f "$P/_slurm/watch/STOP" ] && { say "STOP — exiting"; exit 0; }
  live=$( { squeue -M granite -h -u "$USER" -o "%j"; squeue -M notchpeak -h -u "$USER" -o "%j"; } 2>/dev/null )
  while read -r arm; do
    [ -z "$arm" ] && continue
    f=$P/_slurm/grn/$arm.sbatch; [ -f "$f" ] || { say "  ! no sbatch for $arm"; continue; }
    echo "$live" | grep -qx "nd-$arm" && continue
    lg=$P/_slurm/grn/logs/$arm.out
    [ -f "$lg" ] && tail -3 "$lg" 2>/dev/null | grep -qE "^done |exit=0" && continue
    t=${TRIES[$arm]:-0}
    [ "$t" -ge 3 ] && { say "  ! $arm failed ${t}x — needs a human"; continue; }
    TRIES[$arm]=$((t+1)); say "  ↻ resubmitting $arm (attempt $((t+1)))"
    sbatch -M granite "$f" >/dev/null 2>&1
  done < <(grep -vE '^\s*#|^\s*$' "$P/_slurm/watch/slurm_tasks.list" 2>/dev/null)
  sleep "$INTERVAL"
done
