"""submit.py — turn registry entries into SLURM jobs, one GPU per arm.

    python submit.py --wave 1                 # write + submit wave 1
    python submit.py --wave 1 --dry-run       # write the scripts, submit nothing
    python submit.py --arm E01_add_english/main
    python submit.py --smoke                  # 3-minute pipeline check, one GPU

🔴 Jobs are pinned to GPUs that are ACTUALLY FREE. `--nodelist` defaults to grn008
(8x H100 NVL, idle) — SLURM will not start a job on a busy GPU, so a pending job is the
correct outcome when the node fills, never a reason to widen the request.

Each job: 1 GPU, bf16 (sm_90), train -> decode dev -> write dev.json, and `--requeue`
with `--resume` so a preemption costs one eval interval, not a whole run.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import ARMS, validate  # noqa: E402

PROJ = Path(__file__).resolve().parent.parent
SLURM = PROJ / "_slurm"
LOGS = SLURM / "logs"
VENV = "/scratch/general/nfs1/u1592009/envs/nascenia"
HF_HOME = "/scratch/general/nfs1/u1592009/huggingface"

TEMPLATE = """#!/bin/bash
#SBATCH --job-name={job}
#SBATCH --account=kmarino
#SBATCH --partition={partition}
#SBATCH --qos={qos}
{nodelist_line}#SBATCH --gres=gpu:1
#SBATCH -c {cpus}
#SBATCH --mem={mem}
#SBATCH -t {walltime}
#SBATCH --requeue
#SBATCH -o {logs}/{job}-%j.out
#SBATCH -e {logs}/{job}-%j.out
set -uo pipefail

export HF_HOME={hf_home}
export HF_HUB_OFFLINE=0
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS={cpus}
PY={venv}/bin/python

echo "node=$(hostname)  job=$SLURM_JOB_ID  $(date)"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader

cd {expdir}

# ---- train ------------------------------------------------------------------
# --resume makes a requeued job pick up the last checkpoint instead of restarting.
$PY ../code/02_train_t5.py \\
  --data-dir {data} \\
  --model {model} \\
  --out-dir . --run-name {arm} \\
  --seed {seed} \\
  --lr {lr} --warmup {warmup} --optim adafactor \\
  --max-source-len {src} --max-target-len {tgt} \\
  --batch-size {bs} --grad-accum {accum} --eval-batch-size {eval_bs} \\
  --eval-subset 300 --eval-steps 250 --max-steps {steps} \\
  --save-total-limit {save_limit} \\
  --early-stopping-patience {patience} \\
  --gen-num-beams 4 --gen-min-new-tokens 80 \\
  --precision auto --no-group-by-length --resume
rc=$?
echo "train exit=$rc"
[ $rc -ne 0 ] && exit $rc

# ---- score on the frozen dev split -------------------------------------------
$PY ../code/04_decode.py --ckpt {arm}/best --data-dir {data} \\
  --split dev --limit 300 --mode beam --num-beams 4 \\
  --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \\
  --max-source-len {src} \\
  --no-bertscore --record {arm}/dev.json
echo "decode exit=$?"

# ---- test-split predictions, so the arm is submittable without a retrain ------
$PY ../code/04_decode.py --ckpt {arm}/best --data-dir {data} \\
  --split test --mode beam --num-beams 4 \\
  --min-new-tokens 80 --max-new-tokens 320 --length-penalty 1.0 \\
  --max-source-len {src} \\
  --no-bertscore --out {arm}/submission.csv --record {arm}/test.json
echo "test-decode exit=$?  done $(date)"
"""

# Decoder-only arms (E18's zoo): a different trainer, a different LR, and generation
# eval that left-pads. 03_train_causal.py writes the same best/ + run.json layout.
CAUSAL_TEMPLATE = """#!/bin/bash
#SBATCH --job-name={job}
#SBATCH --account=kmarino
#SBATCH --partition={partition}
#SBATCH --qos={qos}
{nodelist_line}#SBATCH --gres=gpu:1
#SBATCH -c {cpus}
#SBATCH --mem={mem}
#SBATCH -t {walltime}
#SBATCH --requeue
#SBATCH -o {logs}/{job}-%j.out
#SBATCH -e {logs}/{job}-%j.out
set -uo pipefail

export HF_HOME={hf_home}
# 🔴 the env HF_TOKEN is DEAD and overrides the token file; unset it so gated repos
# (gemma) resolve through HF_HOME/token, which holds the account that has access.
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS={cpus}
PY={venv}/bin/python

echo "node=$(hostname)  job=$SLURM_JOB_ID  $(date)"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader

cd {expdir}
$PY ../code/03_train_causal.py \\
  --data-dir {data} \\
  --model {model} \\
  --out-dir . --run-name {arm} \\
  --seed {seed} \\
  --lr {lr} --warmup {warmup} \\
  --max-len {max_len} \\
  --batch-size {bs} --grad-accum {accum} --eval-batch-size {eval_bs} \\
  --eval-subset 300 --eval-steps 250 --max-steps {steps} \\
  --early-stopping-patience {patience} \\
  --num-beams 4 --min-new-tokens {min_new} --max-new-tokens {max_new} \\
  --precision auto --grad-checkpointing --optim {optim}
echo "train exit=$?  done $(date)"
"""

SMOKE = """#!/bin/bash
#SBATCH --job-name=nasc-smoke
#SBATCH --account=kmarino
#SBATCH --partition={partition}
#SBATCH --qos={qos}
{nodelist_line}#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -t 00:40:00
#SBATCH -o {logs}/smoke-%j.out
#SBATCH -e {logs}/smoke-%j.out
set -uo pipefail
export HF_HOME={hf_home}
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONUNBUFFERED=1
PY={venv}/bin/python
echo "node=$(hostname)  $(date)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
$PY -c "import torch;c=torch.cuda.get_device_capability();print('sm_%d%d'%c,'bf16-hw',c[0]>=8)"
cd {proj}/_slurm
# Plumbing only: the score is meaningless (LR never leaves warmup). Success = no crash.
$PY ../code/02_train_t5.py --data-dir ../data/draft_only --out-dir ./_smoke \\
  --smoke --max-train 1000 --epochs 1 --batch-size 8 --grad-accum 2 \\
  --eval-subset 100 --eval-steps 20 --eval-batch-size 8 --gen-num-beams 2 \\
  --no-bertscore-eval --run-name smoke
echo "smoke train exit=$?"
$PY ../code/04_decode.py --ckpt ./_smoke/smoke/best --data-dir ../data/draft_only \\
  --split dev --limit 32 --mode beam --num-beams 2 --min-new-tokens 80 \\
  --max-new-tokens 320 --no-bertscore --record ./_smoke/dev.json
echo "smoke decode exit=$?  $(date)"
"""


def write_and_submit(script: str, path: Path, dry: bool) -> str | None:
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    if dry:
        print(f"  [dry-run] wrote {path}")
        return None
    out = subprocess.run(["sbatch", str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        print(f"  ❌ sbatch failed: {out.stderr.strip()}")
        return None
    jid = out.stdout.strip().split()[-1]
    print(f"  submitted {jid}  <- {path.name}")
    return jid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int)
    ap.add_argument("--arm", action="append", default=[], help="exp/arm, repeatable")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--partition", default="granite-gpu")
    ap.add_argument("--qos", default="granite-gpu-freecycle")
    ap.add_argument("--nodelist", default="grn008",
                    help="pin to a node with genuinely free GPUs; '' to let SLURM place")
    ap.add_argument("--walltime", default="3-00:00:00")
    ap.add_argument("--cpus", type=int, default=8)
    ap.add_argument("--mem", default="80G")
    ap.add_argument("--data-override", default=None,
                    help="resolve arms whose data is WINNER (set after Tier 1 reports)")
    ap.add_argument("--steps-override", type=int, default=None,
                    help="resolve arms whose budget comes from another run (E19 <- E05)")
    ap.add_argument("--force-blocked", action="store_true",
                    help="submit arms marked blocked (e.g. after a licence is accepted)")
    # --- emit mode: print commands instead of submitting sbatch jobs -------------
    # Used to drive an allocation we already hold (grn023) through run_pool.sh, rather
    # than queueing new jobs. Same registry, same validation, same output layout.
    ap.add_argument("--emit", action="store_true",
                    help="print one shell command per arm instead of sbatch-ing")
    ap.add_argument("--bs", type=int, default=None,
                    help="override per-device batch (bs x accum must still be 64)")
    ap.add_argument("--accum", type=int, default=None,
                    help="override grad accumulation")
    a = ap.parse_args()

    validate()
    LOGS.mkdir(parents=True, exist_ok=True)
    nodelist_line = f"#SBATCH --nodelist={a.nodelist}\n" if a.nodelist else ""
    common = dict(partition=a.partition, qos=a.qos, nodelist_line=nodelist_line,
                  logs=LOGS, hf_home=HF_HOME, venv=VENV, proj=PROJ)

    if a.smoke:
        return 0 if write_and_submit(SMOKE.format(**common),
                                     SLURM / "smoke.sbatch", a.dry_run) else 1

    selected = [x for x in ARMS
                if (a.wave and x["wave"] == a.wave)
                or f"{x['exp']}/{x['arm']}" in a.arm]
    if not selected:
        print("nothing selected — pass --wave N or --arm exp/arm")
        return 1

    for x in selected:
        if x.get("blocked") and not a.force_blocked:
            print(f"  🔴 {x['exp']}/{x['arm']} BLOCKED: {x['blocked']} — not submitted")
            continue
        data = x["data"]
        if data.startswith("multitask_"):
            # built by 11_build_stage_datasets.py, named after the winner it wraps
            if not a.data_override:
                print(f"  ⏭  {x['exp']}/{x['arm']} needs --data-override (Tier-1 winner)")
                continue
            data = f"multitask_{a.data_override}"
        elif data == "WINNER":
            if not a.data_override:
                print(f"  ⏭  {x['exp']}/{x['arm']} needs --data-override (Tier-1 winner)")
                continue
            data = a.data_override
        steps = x["steps"]
        if not isinstance(steps, int):
            if not a.steps_override:
                print(f"  ⏭  {x['exp']}/{x['arm']} needs --steps-override "
                      f"(budget comes from {steps})")
                continue
            steps = a.steps_override
        expdir = PROJ / x["exp"]
        assert expdir.is_dir(), f"no such experiment dir: {expdir}"
        datadir = PROJ / "data" / data
        assert (datadir / "train.parquet").is_file(), f"no train.parquet in {datadir}"

        job = f"nasc-{x['exp'].split('_')[0]}-{x['arm']}"
        kind = x.get("kind", "seq2seq")
        bs, accum = (a.bs or x["bs"]), (a.accum or x["accum"])
        # 🔴 The one number that is not ours to change, re-checked after any override:
        # HOW we reach 64 is a hardware call, THAT it is 64 is the experiment.
        assert bs * accum == 64, (
            f"{x['exp']}/{x['arm']}: {bs}x{accum}={bs*accum}, effective batch must be 64")
        shared = dict(job=job, cpus=a.cpus, mem=a.mem, walltime=a.walltime,
                      expdir=expdir, data=f"../data/{data}", model=x["model"],
                      arm=x["arm"], seed=x["seed"], lr=x["lr"], warmup=x["warmup"],
                      # Decoder eval generates ~700 tokens x beam 4; keep the eval
                      # batch small so the KV cache fits a 40 GB a800.
                      bs=bs, accum=accum,
                      eval_bs=(4 if kind == "causal" else min(bs, 32)),
                      steps=steps, patience=x["patience"],
                      **{**common, "venv": x.get("venv", VENV)})

        if a.emit:
            # Strip the sbatch header and blank lines: what is left is a runnable
            # train -> decode-dev -> decode-test script for one GPU.
            body = (CAUSAL_TEMPLATE if kind == "causal" else TEMPLATE).format(
                **({"max_len": x["max_len"], "min_new": x["min_new"],
                   "max_new": x["max_new"],
                   "optim": x.get("optim", "adamw_torch")} if kind == "causal"
                   else {"src": x["src"], "tgt": x["tgt"],
                         "save_limit": x["save_limit"]}), **shared)
            body = "\n".join(l for l in body.splitlines()
                             if not l.startswith("#SBATCH") and l != "#!/bin/bash")
            script = SLURM / "tasks" / f"{job}.sh"
            script.parent.mkdir(exist_ok=True)
            script.write_text(body, encoding="utf-8")
            script.chmod(0o755)
            print(f"{script}")
            continue

        if kind == "causal":
            script = CAUSAL_TEMPLATE.format(max_len=x["max_len"],
                                            optim=x.get("optim","adamw_torch"),
                                            min_new=x["min_new"],
                                            max_new=x["max_new"], **shared)
        else:
            script = TEMPLATE.format(src=x["src"], tgt=x["tgt"],
                                     save_limit=x["save_limit"], **shared)
        print(f"{x['exp']}/{x['arm']}: {data} · {x['model']} · {steps} steps · "
              f"{x['bs']}x{x['accum']} · lr {x['lr']} · {kind}")
        write_and_submit(script, SLURM / f"{job}.sbatch", a.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
