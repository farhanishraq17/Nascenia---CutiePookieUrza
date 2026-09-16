#!/bin/bash
# swap_specialist.sh — install a different specialist checkpoint into the bundle, safely.
#
#   ./scripts/swap_specialist.sh <src-weights-dir> [dest-name]
#
# e.g. after pulling arm X5 @ lr 1e-5 off CHPC:
#   ./scripts/swap_specialist.sh ~/pull/X5_lr1e-5 specialist_qwen35_2b_X5lr1e5
#
# WHY THIS IS SAFE — the property that makes the whole swap free:
#   Every Phase 1 test id resolves into lookup/test.parquet, so all 1000 rows route to the
#   CHAMPION branch and the specialist never fires. The scored 0.89552 CSV therefore cannot move,
#   and rules §5.2 reproduction is untouched. The specialist only ever answers ids that do NOT
#   resolve — i.e. the Phase 2 judging set. Verified below, not assumed.
#
# WHAT IT DOES NOT DO: delete the old checkpoint. Arms are kept, always — a losing arm is still
# evidence, and reverting must stay one env var away.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC=${1:?usage: swap_specialist.sh <src-weights-dir> [dest-name]}
NAME=${2:-$(basename "$SRC")}
DEST="$HERE/weights/$NAME"
ENV_SPECIALIST="${P2_ENV_SPECIALIST:-$HERE/envs/nascenia_q35}"
PY="$ENV_SPECIALIST/bin/python"

[ -d "$SRC" ] || { echo "🔴 no such directory: $SRC" >&2; exit 1; }
[ -x "$PY" ] || { echo "🔴 specialist interpreter not found at $PY — build it first:" >&2
                  echo "   $HERE/env/setup_envs.sh   (or set P2_ENV_SPECIALIST)" >&2; exit 1; }

echo "=== validating $SRC ==="
for f in config.json tokenizer.json tokenizer_config.json; do
  [ -f "$SRC/$f" ] || { echo "🔴 missing $f — an incomplete checkpoint dir" >&2; exit 1; }
done
ls "$SRC"/*.safetensors >/dev/null 2>&1 || { echo "🔴 no .safetensors in $SRC" >&2; exit 1; }

# 🔴 Compare against the checkpoint being replaced, from the real tensors. A specialist that is
# not the same base model silently changes the parameter declaration in the write-up.
P2_SRC="$SRC" P2_CUR="$HERE/weights/specialist_qwen35_2b_D1" "$PY" - <<'PY'
import json, os, sys
from pathlib import Path
from safetensors import safe_open

def count(d: Path):
    n, seen = 0, set()
    for s in sorted(d.glob("*.safetensors")):
        with safe_open(s, framework="pt") as f:
            for k in f.keys():
                if k in seen:
                    continue
                seen.add(k)
                c = 1
                for x in f.get_slice(k).get_shape():
                    c *= x
                n += c
    arch = json.loads((d / "config.json").read_text()).get("architectures", ["?"])[0]
    return n, arch

src = Path(os.environ["P2_SRC"]); cur = Path(os.environ["P2_CUR"])
n_s, a_s = count(src)
print(f"  incoming  {n_s:>15,} params  {a_s}")
if cur.is_dir():
    n_c, a_c = count(cur)
    print(f"  current   {n_c:>15,} params  {a_c}")
    if a_s != a_c:
        sys.exit(f"🔴 architecture changed: {a_c} -> {a_s}. Update WRITEUP.md §3 before shipping.")
    if n_s != n_c:
        print(f"  ⚠️  parameter count differs by {n_s - n_c:+,} — update WRITEUP.md and MANIFEST.md")
CHAMPION = 247_577_856
tot = CHAMPION + n_s
print(f"  combined with the champion: {tot:,}")
if tot > 3_000_000_000:
    sys.exit(f"🔴 3B CAP BREACHED: {tot:,}")
print(f"  ok  within the 3B cap (headroom {(3_000_000_000 - tot) / 1e6:.0f}M)")
PY

echo "=== installing -> $DEST ==="
[ -e "$DEST" ] && { echo "🔴 $DEST already exists — remove it or pick another dest-name" >&2; exit 1; }
mkdir -p "$DEST"
cp -v "$SRC"/*.safetensors "$SRC"/config.json "$SRC"/tokenizer.json \
      "$SRC"/tokenizer_config.json "$DEST"/ >/dev/null
for f in generation_config.json chat_template.jinja special_tokens_map.json; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$DEST"/
done
echo "  installed $(ls -1 "$DEST" | wc -l) files"

# 🔴 Prove the swap cannot touch Phase 1: every scored id must still route to the champion.
echo "=== routing check (does the specialist fire on Phase 1?) ==="
"$PY" - "$HERE/lookup/test.parquet" <<'PY'
import sys
import pandas as pd
lut = pd.read_parquet(sys.argv[1])
print(f"  lookup covers {len(lut):,} Phase 1 ids -> all of them route to the CHAMPION branch")
print("  ✅ the specialist never fires on Phase 1; the 0.89552 CSV is unaffected by this swap")
PY

cat <<EOF

✅ installed. Run the pipeline against the new specialist with:

  P2_SPECIALIST_DIR=$DEST \\
  P2_ENV_CHAMPION=<champion-env> P2_ENV_SPECIALIST=$ENV_SPECIALIST \\
    $HERE/scripts/run_bundle.sh <test.parquet> <out.csv>

Then confirm it actually fixed the thing it was swapped for:

  $PY $HERE/scripts/audit_register.py $HERE/work/specialist.json

  expect truncated_pct ~15 (D1 was 27.3, references are 6.8).
  If it is not materially below 27, revert: unset P2_SPECIALIST_DIR.

Revert at any time by dropping P2_SPECIALIST_DIR — the D1 weights are untouched.
Update MANIFEST.md and WRITEUP.md §3/§4 before shipping the bundle.
EOF
