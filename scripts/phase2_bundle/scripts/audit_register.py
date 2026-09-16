#!/usr/bin/env python
"""audit_register.py — the judge-facing quality check for a branch's output.

    python scripts/audit_register.py work/specialist.json [more.json ...]

Phase 2's score comes from an LLM judge scoring "tone, completeness, clarity as a doctor's
response" (rules §5.3). Token F1 does not measure any of those. This reports the axes that do,
against the organizers' own reference distribution.

`truncated_pct` is the one that matters most and the reason this script exists: the shipped D1
specialist fails to close a sentence on 27.3% of its answers against a reference rate of 6.8%.
An answer that stops mid-sentence is the most visible defect an LLM judge can see.

Definitions match fine_tune_project/code/15_phase2_audit.py exactly, so numbers are comparable
to every arm in docs/RESULTS_B_Qwen35_2B.md.

🔴 WHAT THIS DOES NOT MEASURE: clinical correctness, contradiction, unsafe advice. Those need a
medical judge. Do not report them as passing on the strength of this script.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")

TERMINAL = ("।", ".", "!", "?", "…")
_PUNCT = re.compile(r"[।,\.\?\!;:\(\)\[\]\{\}\"'`\-—–/\\|~@#\$%\^&\*\+=<>০-৯0-9]")

# measured on the organizers' references — docs/RESULTS_B_Qwen35_2B.md
REFERENCE = {"truncated_pct": 6.8, "helo_pct": 76.4, "nasenia_pct": 50.0, "len_p50": 100}


def tokens(s: str) -> list[str]:
    return _PUNCT.sub(" ", s).split()


def audit(name: str, preds: list[str]) -> dict:
    n = max(1, len(preds))
    lens = sorted(len(tokens(p)) for p in preds)

    def q(f: float) -> int:
        return lens[min(len(lens) - 1, int(f * len(lens)))] if lens else 0

    return {
        "arm": name,
        "rows": len(preds),
        "truncated_pct": round(100 * sum(1 for p in preds
                                         if p.strip() and not p.strip().endswith(TERMINAL)) / n, 1),
        "helo_pct": round(100 * sum(1 for p in preds if p.strip().startswith("হেলো")) / n, 1),
        "nasenia_pct": round(100 * sum(1 for p in preds if "নাসেনিয়া" in p) / n, 1),
        "empty_pct": round(100 * sum(1 for p in preds if not p.strip()) / n, 1),
        "very_short_pct": round(100 * sum(1 for L in lens if L < 30) / n, 1),
        "len_p05": q(0.05), "len_p50": q(0.50), "len_p95": q(0.95),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("records", nargs="+", help="branch JSON from bundle_decode.py")
    ap.add_argument("--show", type=int, default=3, help="truncated examples to print per arm")
    args = ap.parse_args()

    rows = []
    for r in args.records:
        d = json.loads(Path(r).read_text(encoding="utf-8"))
        # bundle_decode.py writes "preds"; the E15/dev records in this project write
        # "predictions". Accept both so this can be pointed at any of them.
        preds = d.get("preds") or d.get("predictions")
        if not preds:
            raise SystemExit(f"🔴 {r}: no 'preds' or 'predictions' key")
        ckpt = d.get("ckpt") or r
        name = f"{d.get('mode', '?')}:{Path(ckpt).name}"
        rows.append((audit(name, preds), preds))

    keys = ["arm", "rows", "truncated_pct", "helo_pct", "nasenia_pct",
            "empty_pct", "very_short_pct", "len_p05", "len_p50", "len_p95"]
    print("| " + " | ".join(keys) + " |")
    print("|" + "---|" * len(keys))
    for a, _ in rows:
        print("| " + " | ".join(str(a[k]) for k in keys) + " |")
    print("| *references* | — | **6.8** | 76.4 | 50.0 | — | — | — | ~100 | — |")

    for a, preds in rows:
        t = a["truncated_pct"]
        verdict = ("✅ at/below the reference rate" if t <= 10
                   else "⚠️ elevated" if t <= 20
                   else "🔴 far above the references' 6.8% — the judge will see cut-off answers")
        print(f"\n{a['arm']}: truncated {t}%  {verdict}")
        if args.show:
            bad = [p for p in preds if p.strip() and not p.strip().endswith(TERMINAL)]
            for p in bad[: args.show]:
                print(f"    …{p.strip()[-90:]}")


if __name__ == "__main__":
    main()
