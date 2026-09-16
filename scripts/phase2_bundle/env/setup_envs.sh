#!/bin/bash
# setup_envs.sh — build both interpreters the routed pipeline needs, without Docker.
#
#   ./env/setup_envs.sh [PREFIX]         # default PREFIX: ./envs under the bundle root
#
# Creates PREFIX/nascenia (transformers 4.57.3, champion branch) and PREFIX/nascenia_q35
# (transformers 5.14.1, specialist branch), then prints the exact run_bundle.sh invocation.
#
# Plain python venvs, not conda: both requirements files are pip freezes, so venv reproduces them
# exactly and needs no extra tooling. run_bundle.sh only ever looks for <env>/bin/python, which
# venv and conda both provide.
#
# Requires: python 3.11 on PATH (or set P2_PYTHON), git, ~20 GB disk, NVIDIA driver >= 570.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${1:-$HERE/envs}"
PYTHON="${P2_PYTHON:-python3.11}"

command -v "$PYTHON" >/dev/null 2>&1 || {
  echo "🔴 '$PYTHON' not found. Install Python 3.11 (the envs were frozen at 3.11.13) or set" >&2
  echo "   P2_PYTHON=/path/to/python3.11 $0 $*" >&2; exit 1; }
command -v git >/dev/null 2>&1 || {
  echo "🔴 git not found. Both envs pin the csebuetnlp normalizer as a git+https requirement," >&2
  echo "   and the champion branch hard-fails without it." >&2; exit 1; }

ver=$("$PYTHON" -c 'import sys;print("%d.%d"%sys.version_info[:2])')
[ "$ver" = "3.11" ] || echo "⚠️  $PYTHON is $ver, the envs were frozen at 3.11 — pins may not resolve."

# 🔴 torch==2.8.0+cu128 is NOT on plain PyPI. Without this index the very first requirement fails.
export PIP_EXTRA_INDEX_URL="${PIP_EXTRA_INDEX_URL:-https://download.pytorch.org/whl/cu128}"
export PIP_DISABLE_PIP_VERSION_CHECK=1

build() {   # $1 = env name, $2 = requirements file, $3 = expected transformers major.minor
  local dir="$PREFIX/$1"
  echo "=== building $dir  (from env/$2) ==="
  "$PYTHON" -m venv "$dir"
  "$dir/bin/pip" install --upgrade pip >/dev/null
  "$dir/bin/pip" install -r "$HERE/env/$2"
  "$dir/bin/python" - "$3" <<'PY'
import sys, transformers, torch
want = sys.argv[1]
assert transformers.__version__.startswith(want), \
    f"resolved transformers {transformers.__version__}, expected {want}.x"
print(f"  ok  transformers {transformers.__version__}  torch {torch.__version__}")
PY
}

mkdir -p "$PREFIX"
build nascenia     requirements_nascenia.txt     4.57
build nascenia_q35 requirements_nascenia_q35.txt 5.14

# The champion branch imports this and refuses to run without it — check it here, not at decode.
"$PREFIX/nascenia/bin/python" -c "import normalizer; print('  ok  csebuetnlp normalizer present')"

cat <<EOF

✅ both environments built under $PREFIX

Run the pipeline with:

  P2_ENV_CHAMPION=$PREFIX/nascenia \\
  P2_ENV_SPECIALIST=$PREFIX/nascenia_q35 \\
    $HERE/scripts/run_bundle.sh <test.parquet> <out.csv>

Verify them at any time with:

  $HERE/env/verify_envs.sh $PREFIX
EOF
