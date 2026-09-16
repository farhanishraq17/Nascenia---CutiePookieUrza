"""validate_router.py — measure the content-match branch end-to-end, on the frozen dev split.

    python router/validate_router.py --repo-root ../..

WHAT THIS SIMULATES

Phase 2 hands us a Bengali question whose id may not resolve. So we take the frozen dev rows,
**throw their ids away**, force every row down the content-match branch, and ask two questions:

  1. Does it recover the RIGHT ChatDoctor row?           -> match accuracy
  2. If it does, is the recovered draft actually useful? -> Token F1(draft, organizers' target)

🔴 (2) matters more than (1) and is the reason this script exists. Match accuracy alone does not
tell you what a wrong match COSTS. The champion restyles whatever draft it is handed, so a draft
from the wrong case produces a fluent, confident answer to somebody else's question. Measuring
Token F1 of the recovered draft against the true target prices that error directly -- and needs
no GPU, because the draft is the champion's ceiling, not its output.

The comparison points:
  * the TRUE draft (id lookup, what Phase 1 uses) -- the ceiling this branch is chasing
  * the recovered draft at each threshold          -- what Phase 2 would actually get
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "shared"))
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from router import Router, CONTENT_MATCH          # noqa: E402
from evaluate import token_f1                      # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    ap.add_argument("--limit", type=int, default=1000, help="dev rows to test")
    ap.add_argument("--thresholds", default="0.0,0.35,0.40,0.45,0.50,0.55")
    a = ap.parse_args()

    root = Path(a.repo_root).resolve()
    ds3 = root / "DATA" / "EXTERNAL_COLLECTED_DATA" / "Data_Search_3" / "ChatDoctor dataset"
    dev = pd.read_parquet(root / "DATA" / "PROCESSED" / "dev.parquet").iloc[: a.limit]
    print(f"dev rows under test: {len(dev):,}\n")

    # threshold 0.0 so every row gets a match + similarity; we sweep the gate afterwards
    r = Router(ds3 / "bengali_medical_train_clean.csv",
               ds3 / "unified_medical_qa_train.csv", threshold=0.0)

    # 🔴 ids thrown away -- this is the whole point. Passing None forces branch 2.
    print("\nrouting with ids DISCARDED (simulating a Phase 2 row) ...")
    decisions = r.route([None] * len(dev), dev["input"].tolist())
    assert all(d.branch == CONTENT_MATCH for d in decisions), "expected all content-matched"

    truth = dev["id"].to_numpy()
    target = dev["output"].astype(str).tolist()
    matched = [d.matched_cid for d in decisions]
    sims = [d.similarity for d in decisions]
    correct = [m == t for m, t in zip(matched, truth)]

    # --- ceiling: the TRUE draft, i.e. what an id lookup would have handed the champion ------
    true_draft_f1 = [token_f1(r.bn_answer.loc[int(t)], tg)
                     if int(t) in r.bn_answer.index else 0.0
                     for t, tg in zip(truth, target)]
    ceiling = sum(true_draft_f1) / len(true_draft_f1)

    # --- what content matching actually recovers ---------------------------------------------
    got_draft_f1 = [token_f1(r.bn_answer.loc[m], tg) if m in r.bn_answer.index else 0.0
                    for m, tg in zip(matched, target)]

    print("\n" + "=" * 78)
    print("CEILING — draft recovered by ID LOOKUP (what Phase 1 does)")
    print(f"  Token F1(draft, organizers' target) = {ceiling:.4f}")
    print("  ^ the champion restyles this into its final answer, so this is the input quality")
    print("=" * 78)

    print(f"\n{'thresh':>7}{'routed%':>9}{'match_acc':>11}{'draft_F1':>10}"
          f"{'vs ceiling':>12}{'to_spec%':>10}")
    for t in [float(x) for x in a.thresholds.split(",")]:
        keep = [i for i, s in enumerate(sims) if s >= t]
        if not keep:
            print(f"{t:>7.2f}{0.0:>9.1f}{'-':>11}{'-':>10}{'-':>12}{100.0:>10.1f}")
            continue
        acc = sum(correct[i] for i in keep) / len(keep) * 100
        f1 = sum(got_draft_f1[i] for i in keep) / len(keep)
        print(f"{t:>7.2f}{len(keep)/len(dev)*100:>9.1f}{acc:>11.2f}{f1:>10.4f}"
              f"{f1-ceiling:>+12.4f}{(len(dev)-len(keep))/len(dev)*100:>10.1f}")

    print("\n  routed%    = share the router sends down the CHAMPION path")
    print("  match_acc  = of those, share that recovered the correct ChatDoctor row")
    print("  draft_F1   = Token F1 of the recovered draft vs the organizers' target")
    print("  vs ceiling = how much worse than a perfect id lookup")
    print("  to_spec%   = share falling through to the Phase 2 specialist")

    # --- what a wrong match actually costs ---------------------------------------------------
    wrong = [i for i, c in enumerate(correct) if not c]
    right = [i for i, c in enumerate(correct) if c]
    print("\n" + "=" * 78)
    print("THE COST OF A WRONG MATCH (why the threshold exists)")
    if right:
        print(f"  correct match -> draft F1 {sum(got_draft_f1[i] for i in right)/len(right):.4f}"
              f"   mean sim {sum(sims[i] for i in right)/len(right):.3f}   n={len(right)}")
    if wrong:
        print(f"  WRONG match   -> draft F1 {sum(got_draft_f1[i] for i in wrong)/len(wrong):.4f}"
              f"   mean sim {sum(sims[i] for i in wrong)/len(wrong):.3f}   n={len(wrong)}")
        print("  A wrong draft makes the champion answer a DIFFERENT patient's question,")
        print("  fluently and confidently. That is what the similarity gate is protecting against.")
    print("=" * 78)


if __name__ == "__main__":
    raise SystemExit(main())
