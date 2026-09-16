"""
08_lexical_gap.py — where does the champion lose Token F1, token by token?

Compares the champion's dev predictions against the organizers' references and
reports the corpus-level surplus/deficit per token, plus the achievable Token F1
if the top-N systematic mismatches were fixed exactly.

    python NOTEBOOKS/08_lexical_gap.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from metric import tokenize, token_f1  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="fine_tune_project/E15_decode_sweep/ckptavg_peak5/dev_e15dec.json")
    ap.add_argument("--dev", default="fine_tune_project/data/english_draft/dev.parquet")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    preds = json.loads((ROOT / args.pred).read_text(encoding="utf-8"))["predictions"]
    dev = pd.read_parquet(ROOT / args.dev)
    refs = dev["output"].tolist()[: len(preds)]
    assert len(preds) == len(refs), (len(preds), len(refs))

    base = sum(token_f1(p, r) for p, r in zip(preds, refs)) / len(preds)
    print(f"rows={len(preds)}  mean Token F1={base:.4f}\n")

    surplus, deficit = Counter(), Counter()
    ref_tot, pred_tot = Counter(), Counter()
    rows_with_deficit = defaultdict(set)
    rows_with_surplus = defaultdict(set)

    for i, (p, r) in enumerate(zip(preds, refs)):
        pc, rc = Counter(tokenize(p)), Counter(tokenize(r))
        pred_tot += pc
        ref_tot += rc
        for t, n in (pc - rc).items():
            surplus[t] += n
            rows_with_surplus[t].add(i)
        for t, n in (rc - pc).items():
            deficit[t] += n
            rows_with_deficit[t].add(i)

    n_pred = sum(pred_tot.values())
    n_ref = sum(ref_tot.values())
    print(f"pred tokens={n_pred}  ref tokens={n_ref}  "
          f"unmatched surplus={sum(surplus.values())} ({sum(surplus.values())/n_pred:.1%})  "
          f"deficit={sum(deficit.values())} ({sum(deficit.values())/n_ref:.1%})\n")

    print(f"--- top {args.top} DEFICIT (reference says it, we don't) ---")
    print(f"{'token':<28}{'deficit':>8}{'ref_n':>8}{'pred_n':>8}{'miss%':>8}")
    for t, n in deficit.most_common(args.top):
        print(f"{t:<28}{n:>8}{ref_tot[t]:>8}{pred_tot[t]:>8}{n/ref_tot[t]:>8.0%}")

    print(f"\n--- top {args.top} SURPLUS (we say it, reference doesn't) ---")
    print(f"{'token':<28}{'surplus':>8}{'pred_n':>8}{'ref_n':>8}{'junk%':>8}")
    for t, n in surplus.most_common(args.top):
        print(f"{t:<28}{n:>8}{pred_tot[t]:>8}{ref_tot[t]:>8}{n/pred_tot[t]:>8.0%}")

    # substitution candidates: surplus token S and deficit token D that co-occur
    # in the same rows far more often than chance.
    print(f"\n--- substitution candidates (we say S where they say D) ---")
    print(f"{'we say (S)':<24}{'they say (D)':<24}{'rows':>6}{'S_rows':>8}{'D_rows':>8}{'lift':>7}")
    cands = []
    top_s = [t for t, _ in surplus.most_common(150)]
    top_d = [t for t, _ in deficit.most_common(150)]
    N = len(preds)
    for s in top_s:
        for d in top_d:
            if s == d:
                continue
            both = len(rows_with_surplus[s] & rows_with_deficit[d])
            if both < 8:
                continue
            exp = len(rows_with_surplus[s]) * len(rows_with_deficit[d]) / N
            lift = both / exp if exp else 0
            if lift >= 1.5:
                cands.append((both, lift, s, d))
    for both, lift, s, d in sorted(cands, key=lambda x: -x[0])[: args.top]:
        print(f"{s:<24}{d:<24}{both:>6}{len(rows_with_surplus[s]):>8}"
              f"{len(rows_with_deficit[d]):>8}{lift:>7.2f}")

    # Ceiling: if every occurrence of the top-K deficit tokens were supplied and
    # every occurrence of the top-K surplus tokens removed, what is Token F1?
    print(f"\n--- oracle ceiling from fixing the top-K mismatched token types ---")
    for K in (5, 10, 25, 50, 100, 250):
        fix_d = {t for t, _ in deficit.most_common(K)}
        fix_s = {t for t, _ in surplus.most_common(K)}
        tot = 0.0
        for p, r in zip(preds, refs):
            pc, rc = Counter(tokenize(p)), Counter(tokenize(r))
            for t in fix_s:                       # drop our unmatched extras
                if t in pc:
                    pc[t] = min(pc[t], rc.get(t, 0))
            for t in fix_d:                       # supply what they had
                if rc.get(t, 0) > pc.get(t, 0):
                    pc[t] = rc[t]
            pc = +pc
            npd, nrf = sum(pc.values()), sum(rc.values())
            ov = sum((pc & rc).values())
            f1 = 0.0 if not ov else 2 * (ov / npd) * (ov / nrf) / ((ov / npd) + (ov / nrf))
            tot += f1
        print(f"  K={K:<5} Token F1 = {tot/len(preds):.4f}   (+{tot/len(preds)-base:.4f})")


if __name__ == "__main__":
    main()
