"""13_disagreement.py — the gate E14 and E19 must pass before any pooling is attempted.

    python 13_disagreement.py ../E18_model_zoo/*/dev.json ../E05_train_to_convergence/main/dev.json

🔴 Run this BEFORE combining anything. MBR already lost once here (−0.0027 LB) for exactly
one reason: the two members agreed to 0.0001, so the consensus selector had nothing to work
with. If members agree on >90% of rows there is nothing to pool, and the remaining steps of
E14/E19 cannot help.

"Disagreement" is reported three ways, because they answer different questions:

  exact        % of rows where the two outputs are not byte-identical.
               Saturates near 100% and is nearly useless on its own — kept only because it
               is the number the docs quote.
  token_f1     mean pairwise Token F1 between members. This is the honest one: it is the
               same function the competition scores with, so 0.95 means "these two would
               score almost identically on any row" no matter how the bytes differ.
  oracle_gain  Token F1 if an oracle picked the best member per row, minus the best single
               member. 🔴 THE CEILING on any selection-based ensemble. If this is under the
               0.0044 noise floor, no reranker, MBR or voting scheme can pay for itself.
"""

import argparse
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metric import token_f1  # noqa: E402

NOISE = 0.0044


def load(p: Path):
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    preds = d.get("predictions")
    if not preds:
        raise SystemExit(f"{p} has no predictions — it predates the 04_decode.py change "
                         f"that saves them. Re-run the dev decode for that arm.")
    # Label from exp/arm, which is what a reader recognises. The file stem is only a
    # tiebreaker: several experiments now hold a record with the SAME filename
    # (dev_e15dec.json), and collapsing those silently corrupts the per-member table —
    # "best single" would report whichever landed last rather than the max.
    exp, arm = Path(p).parent.parent.name.split('_')[0], Path(p).parent.name
    return f"{exp}/{arm}", Path(p).stem, preds, d.get("dev", {}).get("token_f1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records", nargs="+", help="dev.json files, one per member")
    ap.add_argument("--refs-from", default=None,
                    help="dataset dir with dev.parquet, for the oracle-gain ceiling")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()

    raw = [load(Path(p)) for p in a.records]
    # disambiguate any exp/arm collision with the file stem, rather than refusing to run
    counts = {}
    for nm, _, _, _ in raw:
        counts[nm] = counts.get(nm, 0) + 1
    members = [((f"{nm}:{stem}" if counts[nm] > 1 else nm), preds, f1)
               for nm, stem, preds, f1 in raw]
    names = [m[0] for m in members]
    assert len(set(names)) == len(names), f'duplicate member labels: {names}'
    n = min(len(m[1]) for m in members)
    if a.limit:
        n = min(n, a.limit)
    print(f"{len(members)} members over {n} rows\n")

    print("| A | B | exact-diff % | mean pairwise Token F1 |")
    print("|---|---|---|---|")
    sims = []
    for (na, pa, _), (nb, pb, _) in itertools.combinations(members, 2):
        exact = 100.0 * sum(pa[i].strip() != pb[i].strip() for i in range(n)) / n
        sim = sum(token_f1(pa[i], pb[i]) for i in range(n)) / n
        sims.append(sim)
        print(f"| {na} | {nb} | {exact:.1f}% | **{sim:.4f}** |")

    mean_sim = sum(sims) / len(sims) if sims else 1.0
    print(f"\nmean pairwise Token F1 between members: **{mean_sim:.4f}**")

    if a.refs_from:
        import pandas as pd
        refs = pd.read_parquet(Path(a.refs_from) / "dev.parquet")["output"].tolist()[:n]
        singles = {name: sum(token_f1(p[i], refs[i]) for i in range(n)) / n
                   for name, p, _ in members}
        best_single = max(singles.values())
        oracle = sum(max(token_f1(p[i], refs[i]) for _, p, _ in members)
                     for i in range(n)) / n
        gain = oracle - best_single
        print("\n| member | Token F1 |")
        print("|---|---|")
        for k, v in sorted(singles.items(), key=lambda kv: -kv[1]):
            print(f"| {k} | {v:.4f} |")
        print(f"\nbest single **{best_single:.4f}** · per-row oracle **{oracle:.4f}** · "
              f"**oracle gain {gain:+.4f}**")
        print("\n" + ("✅ worth pooling — an oracle has real headroom" if gain > NOISE else
                      "🔴 STOP: oracle gain is inside the 0.0044 noise floor. No "
                      "selection scheme can pay for itself here."))
    else:
        print("\n(pass --refs-from ../data/<winner> for the oracle-gain ceiling — "
              "that is the number that actually decides whether to pool)")

    if mean_sim > 0.90:
        print("\n⚠️  members agree above the 0.90 similarity line the docs set as the "
              "abandon threshold.")


if __name__ == "__main__":
    raise SystemExit(main())
