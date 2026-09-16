"""validate_router_leakfree.py — ROUTER-01 re-measured with the leak actually closed.

    python validate_router_leakfree.py --repo-root ../..

🔴 WHY THIS FILE EXISTS
`validate_router.py` has no leak exclusion at all, and the ad-hoc scripts written on 2026-08-23
had one that silently did nothing: they compared ChatDoctor ids (`hcm_0`) against competition dev
ids (`17200`), which never match, so **not one ChatDoctor row was ever removed**. Every dev query
could therefore retrieve its own answer, and ROUTER-01's headline numbers measure self-retrieval:

    reported: 88.0% routed - 98.07% "match accuracy" - recovered draft F1 0.5901 vs ceiling 0.5963

A supposedly independent retrieval channel landing 0.0002 from a perfect id lookup was the tell.
It was not near-perfect retrieval; it WAS the perfect lookup.

This script strips the `hcm_` prefix first, then excludes every frozen dev/test id, and reports
what content-matching is really worth.

🔴 NOTE ON "match accuracy": with the row's own entry removed it is ~0 by construction and is not
reported. The honest metric is the quality of the RECOVERED DRAFT against the true target, since
that draft is what the champion consumes.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TOKEN_RE = re.compile(r"[ঀ-৿]+|[A-Za-z]+|\d+")


def token_f1(pred, ref) -> float:
    p, r = Counter(TOKEN_RE.findall(str(pred))), Counter(TOKEN_RE.findall(str(ref)))
    ov = sum((p & r).values())
    if not ov:
        return 0.0
    pr, rc = ov / max(1, sum(p.values())), ov / max(1, sum(r.values()))
    return 2 * pr * rc / (pr + rc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--max-features", type=int, default=200_000)
    a = ap.parse_args()
    root = Path(a.repo_root).resolve()
    from sklearn.feature_extraction.text import TfidfVectorizer

    dev = pd.read_parquet(root / "DATA/PROCESSED/dev.parquet")
    dev_ids = set(dev["id"].astype(str))
    test_ids = set(pd.read_csv(root / "DATA/COMPETITION_PROVIDED_DATA/test.csv", dtype=str)["id"])
    q = dev.iloc[: a.limit].reset_index(drop=True)

    src = root / "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_3/ChatDoctor dataset"
    bn = pd.read_csv(src / "bengali_medical_train_clean.csv", dtype=str).dropna(subset=["input", "output"])
    cd = bn[bn["source"] == "healthcaremagic"].copy()
    cd["cid"] = cd["id"].str.replace("hcm_", "", regex=False)      # 🔴 strip BEFORE excluding
    cd = cd.drop_duplicates("cid")
    full = cd.set_index("cid")

    # ---- the ceiling: perfect id lookup (what Phase 1 gets). Unaffected by the leak. --------
    have = [i for i in q["id"].astype(str) if i in full.index]
    ceiling = np.mean([token_f1(full.at[i, "output"], t) for i, t in
                       zip(q["id"].astype(str), q["output"].astype(str)) if i in full.index])
    print(f"perfect id lookup ({len(have)}/{len(q)} resolve): draft F1 = {ceiling:.4f}   <- the ceiling\n")

    # ---- leak-free index -------------------------------------------------------------------
    before = len(cd)
    cdx = cd[~cd["cid"].isin(dev_ids | test_ids)].reset_index(drop=True)
    print(f"corpus {before:,} -> {len(cdx):,}  (dropped {before-len(cdx):,} dev/test rows)")
    assert before - len(cdx) > 0, "🔴 exclusion removed nothing -- the key mismatch is back"

    v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                        max_features=a.max_features, min_df=2, sublinear_tf=True)
    X = v.fit_transform(cdx["input"].astype(str))
    Q = v.transform(q["input"].astype(str))
    bi = np.empty(Q.shape[0], dtype=np.int64); bs = np.empty(Q.shape[0], dtype=np.float32)
    for s in range(0, Q.shape[0], 256):
        S = (Q[s:s + 256] @ X.T).toarray()
        bi[s:s + 256] = S.argmax(axis=1); bs[s:s + 256] = S.max(axis=1)

    draft = cdx["output"].astype(str).values[bi]
    f1 = np.array([token_f1(d, t) for d, t in zip(draft, q["output"].astype(str))])
    print(f"mean top-1 similarity: {bs.mean():.4f}\n")

    print(f"{'tau':>6} {'routed':>9} {'recovered draft F1':>20} {'vs ceiling':>12}")
    for t in (0.0, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50):
        m = bs >= t
        if m.sum() == 0:
            continue
        print(f"{t:>6.2f} {100*m.mean():>8.1f}% {f1[m].mean():>20.4f} {f1[m].mean()-ceiling:>+12.4f}")

    print("\n🔴 Compare against what ROUTER-01 reported (leaked): 88.0% routed, draft F1 0.5901,")
    print("   -0.0062 from ceiling. Any large gap between that and the table above is the leak.")


if __name__ == "__main__":
    raise SystemExit(main())
