#!/bin/bash
# run_pool_multi.sh — one shared work queue, workers spread across SEVERAL allocations.
#
#   ./run_pool_multi.sh <queue-name> <jobid:gpus> [jobid:gpus ...] -- <task.sh> ...
#   ./run_pool_multi.sh conv 1756810:0,1,2,3 1761182:0,1,2 -- tasks/*conv12k*.sh
#
# Separate from run_pool.sh on purpose: that script is currently EXECUTING on grn023, and
# bash reads a running script lazily by byte offset — editing it mid-run can corrupt the
# parse. New file, no risk to the live pool.
#
# Why one queue across nodes instead of one pool per node: the tasks here differ by ~3x in
# cost (E07 at 1280/768 vs E04 at 640/512). Pre-splitting per node leaves fast nodes idle
# while one grinds; a shared queue lets whoever frees up take the next job.
set -uo pipefail

NAME=$1; shift
SPECS=()
while [ "${1:-}" != "--" ] && [ $# -gt 0 ]; do SPECS+=("$1"); shift; done
shift   # drop the --

ROOT=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm
LOGS=$ROOT/logs; mkdir -p "$LOGS"
QUEUE=$ROOT/.queue_$NAME
LOCK=$ROOT/.lock_$NAME
printf '%s\n' "$@" > "$QUEUE"; : > "$LOCK"
echo "pool[$NAME]: $(wc -l < "$QUEUE") tasks across ${#SPECS[@]} allocation(s)"

take_next () { flock 9; local t; t=$(head -1 "$QUEUE"); [ -n "$t" ] && sed -i 1d "$QUEUE"; echo "$t"; } 9<>"$LOCK"

worker () {                       # $1=jobid  $2=gpu index
  local jid=$1 gpu=$2 task name
  while :; do
    task=$(take_next); [ -z "$task" ] && break
    name=$(basename "$task" .sh)
    echo "[$jid/gpu$gpu] START $name $(date +%H:%M:%S)"
    # CUDA_VISIBLE_DEVICES must be exported INSIDE the step — SLURM overwrites it when
    # passed via --export, which would silently put every worker on GPU 0.
    #
    # 🔴 PIN BY UUID, NOT INDEX. Device *indices* are not stable across srun steps: a
    # probe step and a worker step can enumerate the same physical cards in different
    # orders, so "index 4 is idle" measured in one step can be a 33 GB-occupied card in
    # another. That mismatch OOM'd three runs instantly. CUDA accepts
    # CUDA_VISIBLE_DEVICES=GPU-<uuid>, which names the device unambiguously.
    # Pass UUIDs in the jobid:gpus spec to use this.
    srun --jobid="$jid" --overlap -n1 -c5 \
      bash -c "export CUDA_VISIBLE_DEVICES=$gpu OMP_NUM_THREADS=5; exec bash '$task'" \
      > "$LOGS/$name.out" 2>&1
    echo "[$jid/gpu$gpu] DONE  $name exit=$? $(date +%H:%M:%S)"
  done
  echo "[$jid/gpu$gpu] idle — queue empty"
}

for spec in "${SPECS[@]}"; do
  jid=${spec%%:*}; gpus=${spec##*:}
  for g in $(echo "$gpus" | tr ',' ' '); do worker "$jid" "$g" & done
done
wait
rm -f "$QUEUE" "$LOCK"
echo "pool[$NAME]: all tasks finished $(date)"
