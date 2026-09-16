"""16_pool_mbr.py — consensus (MBR) selection over prediction sets that already exist.

    python 16_pool_mbr.py A/dev.json B/dev.json ... --refs-from ../data/english_draft

No GPU and no decoding: every member's predictions are already on disk, so selection is
pure CPU. For each row it picks the candidate with the highest mean Token F1 against the
other candidates — the same consensus rule MBR uses, with Token F1 as the utility because
that is what the competition scores.

🔴 MBR LOST HERE ONCE (−0.0027 LB), and the reason matters: the two members were seeds of
one config that agreed to 0.0001, so consensus had nothing to choose between. This pool is
different — it spans input combinations AND architectures (mT5 disagrees with BanglaT5 at
0.86 pairwise). Whether that is enough is exactly what this measures.

🔴 Selection is done on rows [0:limit] and re-verified on the DISJOINT rows that follow.
A 6-way per-row choice over 300 rows will find spurious winners otherwise.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metric import token_f1  # noqa: E402

NOISE = 0.0044


def load(p):
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    preds = d.get("predictions")
    if not preds:
        raise SystemExit(f"{p}: no predictions saved")
    exp = Path(p).parent.parent.name.split("_")[0]
    return f"{exp}/{Path(p).parent.name}", preds


def consensus_pick(cands):
    """The candidate with the highest mean utility against its peers."""
    if len(cands) == 1:
        return cands[0]
    best, best_u = cands[0], -1.0
    for i, c in enumerate(cands):
        u = sum(token_f1(c, o) for j, o in enumerate(cands) if j != i) / (len(cands) - 1)
        if u > best_u:
            best, best_u = c, u
    return best


def score(preds, refs):
    return sum(token_f1(p, r) for p, r in zip(preds, refs)) / len(refs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records", nargs="+")
    ap.add_argument("--refs-from", required=True)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    members = [load(p) for p in a.records]
    refs_all = pd.read_parquet(Path(a.refs_from) / "dev.parquet")["output"].tolist()
    n = min(min(len(p) for _, p in members), len(refs_all))
    sel = min(a.limit, n)
    print(f"{len(members)} members · {n} rows available · selecting on [0:{sel}]\n")

    singles = {nm: score(p[:sel], refs_all[:sel]) for nm, p in members}
    best_nm = max(singles, key=singles.get)
    for nm, v in sorted(singles.items(), key=lambda kv: -kv[1]):
        print(f"  {nm:26s} {v:.4f}")

    picked = [consensus_pick([p[i] for _, p in members]) for i in range(sel)]
    mbr = score(picked, refs_all[:sel])
    best_single = singles[best_nm]
    print(f"\nbest single ({best_nm}) : {best_single:.4f}")
    print(f"pooled MBR               : {mbr:.4f}   ({mbr - best_single:+.4f})")

    verdict = ("✅ MBR beats the best single member" if mbr - best_single > NOISE else
               "🔴 MBR does NOT beat the best single member — consensus adds nothing here")
    print(verdict)

    # disjoint re-verification, only worth the compute if selection looked like a win
    if mbr - best_single > NOISE and n > sel:
        lo, hi = sel, min(2 * sel, n)
        picked_v = [consensus_pick([p[i] for _, p in members]) for i in range(lo, hi)]
        mbr_v = score(picked_v, refs_all[lo:hi])
        single_v = score(members[[m[0] for m in members].index(best_nm)][1][lo:hi],
                         refs_all[lo:hi])
        print(f"\nDISJOINT rows [{lo}:{hi}] — best single {single_v:.4f} · "
              f"MBR {mbr_v:.4f} ({mbr_v - single_v:+.4f})")
        print("✅ survives" if mbr_v - single_v > NOISE else
              "🔴 does NOT survive the disjoint check — it was a selection artifact")
    if a.out:
        Path(a.out).write_text(json.dumps({"predictions": picked}, ensure_ascii=False))
        print(f"wrote {a.out}")


if __name__ == "__main__":
    raise SystemExit(main())
