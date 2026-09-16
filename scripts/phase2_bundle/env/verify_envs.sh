#!/bin/bash
# verify_envs.sh — prove this machine can reproduce the submission, in ~30 seconds.
#
#   ./env/verify_envs.sh [PREFIX]                       # PREFIX default: ./envs
#   P2_ENV_CHAMPION=... P2_ENV_SPECIALIST=... ./env/verify_envs.sh
#
# Checks everything run_bundle.sh depends on BEFORE a multi-hour decode: both interpreters, both
# transformers versions, the normalizer, the GPU and its bf16 capability, both weight
# directories and their real parameter counts against the 3B cap, and the lookup corpus.
#
# Exit 0 = the pipeline will run. Non-zero = it would have failed, with the reason named.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${1:-$HERE/envs}"
ENV_CHAMPION="${P2_ENV_CHAMPION:-$PREFIX/nascenia}"
ENV_SPECIALIST="${P2_ENV_SPECIALIST:-$PREFIX/nascenia_q35}"
SPECIALIST_DIR="${P2_SPECIALIST_DIR:-$HERE/weights/specialist_qwen35_2b_D1}"
fail=0
note() { echo "  ok  $*"; }
bad()  { echo "🔴 $*" >&2; fail=1; }

echo "=== interpreters ==="
check_env() {   # $1 = interpreter, $2 = expected transformers major.minor, $3 = label
  if [ ! -x "$1" ]; then
    bad "$3: no interpreter at $1"
    echo "     build it:  $HERE/env/setup_envs.sh    (or use env/Dockerfile)" >&2
    return
  fi
  got=$("$1" -c 'import transformers;print(transformers.__version__)' 2>/dev/null) \
    || { bad "$3: $1 cannot import transformers — env incomplete"; return; }
  case "$got" in
    "$2"*) note "$3  transformers $got" ;;
    *) bad "$3: transformers $got, expected $2.x — this WILL silently change the output"
       echo "     (4.57 ties BanglaT5 shared/lm_head, 5.14 does not: different weights)" >&2 ;;
  esac
}
check_env "$ENV_CHAMPION/bin/python"   "4.57" "champion "
check_env "$ENV_SPECIALIST/bin/python" "5.14" "specialist"

if [ -x "$ENV_CHAMPION/bin/python" ]; then
  "$ENV_CHAMPION/bin/python" -c "import normalizer" 2>/dev/null \
    && note "csebuetnlp normalizer present" \
    || bad "csebuetnlp normalizer MISSING from the champion env — omitting it left 16/1000 rows differing"
fi

echo "=== gpu ==="
if [ -x "$ENV_SPECIALIST/bin/python" ]; then
  "$ENV_SPECIALIST/bin/python" - <<'PY' || fail=1
import sys, torch
if not torch.cuda.is_available():
    sys.exit("🔴 no CUDA device visible — both branches call .cuda()")
cap = torch.cuda.get_device_capability()
print(f"  ok  {torch.cuda.get_device_name(0)}  sm_{cap[0]}{cap[1]}  torch {torch.__version__}")
if cap[0] < 8:
    print("  ⚠️  compute capability < 8.0: the specialist falls back to fp32 (slower, and its "
          "numbers were measured in bf16). The champion is fp32 either way and is unaffected.")
PY
fi

echo "=== weights and the 3B cap ==="
if [ -x "$ENV_SPECIALIST/bin/python" ]; then
  P2_CH="$HERE/weights/champion_banglat5_peak5" P2_SP="$SPECIALIST_DIR" \
  "$ENV_SPECIALIST/bin/python" - <<'PY' || fail=1
import json, os, sys
from pathlib import Path
try:
    from safetensors import safe_open
except ImportError:
    sys.exit("🔴 safetensors missing from the specialist env")

CAP, total = 3_000_000_000, 0
for label, key in (("champion  ", "P2_CH"), ("specialist", "P2_SP")):
    d = Path(os.environ[key])
    if not d.is_dir():
        sys.exit(f"🔴 {label}: no weights directory at {d}")
    shards = sorted(d.glob("*.safetensors"))
    if not shards:
        sys.exit(f"🔴 {label}: no .safetensors in {d}")
    n, seen = 0, set()
    for s in shards:
        with safe_open(s, framework="pt") as f:
            for k in f.keys():
                if k in seen:      # sharded checkpoints never repeat a key; guard anyway
                    continue
                seen.add(k)
                sh = f.get_slice(k).get_shape()
                c = 1
                for x in sh:
                    c *= x
                n += c
    arch = json.loads((d / "config.json").read_text()).get("architectures", ["?"])[0]
    print(f"  ok  {label}  {n:>15,} params  {arch}")
    total += n

print(f"      combined     {total:>15,}")
if total > CAP:
    sys.exit(f"🔴 3B CAP BREACHED by {total - CAP:,}")
print(f"  ok  within the 3B cap (headroom {(CAP - total) / 1e6:.0f}M)")
PY
fi

echo "=== lookup corpus ==="
[ -f "$HERE/lookup/test.parquet" ] \
  && note "lookup/test.parquet present (routes ids to the champion branch)" \
  || bad "lookup/test.parquet missing — every row would route to the specialist and Phase 1 would NOT reproduce"

echo
if [ "$fail" -eq 0 ]; then
  echo "✅ verification passed — this machine can run scripts/run_bundle.sh"
else
  echo "❌ verification FAILED — fix the 🔴 lines above before running the pipeline" >&2
fi
exit "$fail"
