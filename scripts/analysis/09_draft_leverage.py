"""
09_draft_leverage.py — how much does draft quality actually move the champion?

Per dev row: score the Google draft against the organizers' reference, score the
champion's prediction against the same reference, and regress one on the other.
The slope is the marginal Token F1 the model returns per unit of draft alignment
-- i.e. exactly what a better translator would buy us.

    python NOTEBOOKS/09_draft_leverage.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from metric import token_f1  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="fine_tune_project/E15_decode_sweep/ckptavg_peak5/dev_e15dec.json")
    ap.add_argument("--draft", default="fine_tune_project/data/draft_only/dev.parquet")
    args = ap.parse_args()

    preds = json.loads((ROOT / args.pred).read_text(encoding="utf-8"))["predictions"]
    dr = pd.read_parquet(ROOT / args.draft).iloc[: len(preds)]
    drafts = [s.split("draft:", 1)[-1].strip() for s in dr["input"].tolist()]
    refs = dr["output"].tolist()

    d = np.array([token_f1(x, r) for x, r in zip(drafts, refs)])
    m = np.array([token_f1(p, r) for p, r in zip(preds, refs)])

    print(f"rows={len(d)}")
    print(f"draft  Token F1 vs reference : {d.mean():.4f}  (sd {d.std():.4f})")
    print(f"model  Token F1 vs reference : {m.mean():.4f}  (sd {m.std():.4f})")
    print(f"model - draft                : {m.mean()-d.mean():+.4f}")
    print(f"rows where the draft beats the model: {(d > m).sum()}/{len(d)}\n")

    slope, intercept = np.polyfit(d, m, 1)
    r = np.corrcoef(d, m)[0, 1]
    print(f"OLS  model_f1 = {intercept:.4f} + {slope:.4f} * draft_f1     (r={r:.3f}, r^2={r*r:.3f})")

    for gain in (0.02, 0.05, 0.0631, 0.10, 0.20):
        print(f"  a draft +{gain:.4f} better everywhere -> model +{slope*gain:.4f} Token F1"
              f"  -> LB +{0.3098*slope*gain:.4f}")

    print("\n--- by draft-quality quartile ---")
    q = pd.qcut(d, 4, labels=False)
    print(f"{'quartile':<10}{'draft f1':>10}{'model f1':>10}{'lift':>10}")
    for k in range(4):
        s = q == k
        print(f"Q{k+1:<9}{d[s].mean():>10.4f}{m[s].mean():>10.4f}{m[s].mean()-d[s].mean():>10.4f}")


if __name__ == "__main__":
    main()
