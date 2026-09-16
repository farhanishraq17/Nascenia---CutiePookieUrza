#!/bin/bash
# run_pool.sh — saturate every GPU of an allocation we ALREADY HOLD.
#
#   ./run_pool.sh <jobid> <ngpus> <task.sh> [task.sh ...]
#   ./run_pool.sh 1758640 8 tasks/*.sh
#
# Why this and not sbatch: grn023 is already ours for 13 days (job 1758640). Queueing
# new jobs would put them behind other users; srun --overlap runs inside the allocation
# we hold, so every task starts immediately.
#
# One worker per GPU, each pinned with CUDA_VISIBLE_DEVICES, pulling from a shared
# flock'd queue — so a worker that finishes a short task immediately takes the next one
# instead of idling while another worker grinds through a 12-hour seed. With 10 long
# tasks on 8 GPUs that is the difference between 2 full rounds and 1.25.
set -uo pipefail

# NGPU may be a count ("8") or an explicit index list ("0,1,2,3,5,6,7").
# The list form exists because grn008's GPU4 is faulty — `nvidia-smi` cannot get a device
# handle for it, and any worker pinned there dies with "CUDA driver error: unknown error".
# That fault already killed a 10-seed E19 sweep on that node.
JOBID=$1; NGPU=$2; shift 2
ROOT=/scratch/general/nfs1/u1592009/Nascenia_Datathon/fine_tune_project/_slurm
LOGS=$ROOT/logs; mkdir -p "$LOGS"
QUEUE=$ROOT/.pool_queue.$$
LOCK=$ROOT/.pool_lock.$$
printf '%s\n' "$@" > "$QUEUE"
: > "$LOCK"
echo "pool: $(wc -l < "$QUEUE") tasks over $NGPU GPUs of job $JOBID"

take_next () {                    # atomically pop one task off the queue
  flock 9
  local t; t=$(head -1 "$QUEUE")
  [ -n "$t" ] && sed -i 1d "$QUEUE"
  echo "$t"
} 9<>"$LOCK"

worker () {
  local gpu=$1 task
  while :; do
    task=$(take_next)
    [ -z "$task" ] && break
    local name; name=$(basename "$task" .sh)
    echo "[gpu$gpu] START $name  $(date +%H:%M:%S)"
    # --overlap: share the allocation rather than asking SLURM for new resources.
    # -c 7: 56 CPUs / 8 GPUs.
    # 🔴 CUDA_VISIBLE_DEVICES must be exported INSIDE the step, not via --export.
    # SLURM rewrites it to the allocation's full GPU list, so `--export=...,CVD=3`
    # silently yields all 8 devices — verified: torch.cuda.device_count() == 8. Every
    # worker would then train on GPU 0 and the node would OOM eight ways at once.
    srun --jobid="$JOBID" --overlap -n1 -c7 \
      bash -c "export CUDA_VISIBLE_DEVICES=$gpu OMP_NUM_THREADS=7; exec bash '$task'" \
      > "$LOGS/$name.out" 2>&1
    echo "[gpu$gpu] DONE  $name exit=$? $(date +%H:%M:%S)"
  done
  echo "[gpu$gpu] queue empty, worker exiting"
}

case "$NGPU" in
  *,*) GPUS=$(echo "$NGPU" | tr ',' ' ') ;;      # explicit indices, skipping bad GPUs
  *)   GPUS=$(seq 0 $((NGPU-1))) ;;
esac
echo "pool: workers on GPU [$GPUS]"
for g in $GPUS; do worker "$g" & done
wait
rm -f "$QUEUE" "$LOCK"
echo "pool: all tasks finished $(date)"
