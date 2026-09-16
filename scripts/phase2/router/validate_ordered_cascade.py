"""validate_ordered_cascade.py — the CORRECT test of "path 3", as an ordered cascade.

    python validate_ordered_cascade.py --repo-root ../..

`validate_expanded_lookup.py` merged every corpus into ONE index and took a global argmax.
That measured the wrong thing: the extra corpora *cannibalised* correct ChatDoctor matches
(healthcaremagic won only 765/1000 top-1 slots instead of 1000), so the mean fell even though
coverage rose. Merging is not what a 4-path router does.

The router the design actually calls for is ORDERED — ChatDoctor is consulted first and only the
rows it cannot serve fall through to the other corpora:

    1. exact id                       -> champion
    2. ChatDoctor content match >= t  -> champion          <- keeps its 0.5961, uncannibalised
    3. OTHER corpora   content match >= t -> champion      <- only sees rows step 2 rejected
    4. otherwise                      -> Qwen specialist

So the only question that matters for step 3 is: **on the rows ChatDoctor rejects, is an
other-corpus draft better than sending the row to the specialist?** That is what this measures,
and it is a much smaller and cheaper query set than the merged test.
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
CHATDOCTOR = "healthcaremagic"


def token_f1(pred, ref) -> float:
    p, r = Counter(TOKEN_RE.findall(str(pred))), Counter(TOKEN_RE.findall(str(ref)))
    ov = sum((p & r).values())
    if not ov:
        return 0.0
    pr, rc = ov / max(1, sum(p.values())), ov / max(1, sum(r.values()))
    return 2 * pr * rc / (pr + rc)


def top1(vec, X, queries, chunk=256):
    Q = vec.transform(queries)
    bi = np.empty(Q.shape[0], dtype=np.int64)
    bs = np.empty(Q.shape[0], dtype=np.float32)
    for s in range(0, Q.shape[0], chunk):
        sims = (Q[s:s + chunk] @ X.T).toarray()
        bi[s:s + chunk] = sims.argmax(axis=1)
        bs[s:s + chunk] = sims.max(axis=1)
    return bi, bs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    ap.add_argument("--n-queries", type=int, default=1000)
    ap.add_argument("--tau", type=float, default=0.40)
    ap.add_argument("--max-features", type=int, default=200_000)
    a = ap.parse_args()
    root = Path(a.repo_root).resolve()

    from sklearn.feature_extraction.text import TfidfVectorizer

    dev = pd.read_parquet(root / "DATA/PROCESSED/dev.parquet")
    test_ids = set(pd.read_csv(root / "DATA/COMPETITION_PROVIDED_DATA/test.csv", dtype=str)["id"])
    dev_ids = set(dev["id"].astype(str))

    m = pd.read_csv(root / "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_5/"
                           "bengali_medical_train_master.csv").dropna(subset=["input", "output"])
    m = m[m["input"].astype(str).str.strip().astype(bool)
          & m["output"].astype(str).str.strip().astype(bool)]
    m = m[~m["id"].astype(str).isin(dev_ids | test_ids)].reset_index(drop=True)
    assert not set(m["id"].astype(str)) & (dev_ids | test_ids), "🔴 LEAK"

    cd = m[m["source"] == CHATDOCTOR].reset_index(drop=True)
    other = m[m["source"] != CHATDOCTOR].reset_index(drop=True)
    print(f"ChatDoctor corpus {len(cd):,} | other corpora {len(other):,} "
          f"({dict(Counter(other['source']))})\n")

    q = dev.iloc[: a.n_queries].reset_index(drop=True)
    tgt = q["output"].astype(str).tolist()

    # ---- step 2: ChatDoctor first --------------------------------------------------------
    v1 = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                         max_features=a.max_features, min_df=2, sublinear_tf=True)
    X1 = v1.fit_transform(cd["input"].astype(str))
    i1, s1 = top1(v1, X1, q["input"].astype(str).tolist())
    f1_cd = np.array([token_f1(d, t) for d, t in zip(cd["output"].values[i1], tgt)])

    served = s1 >= a.tau
    print(f"step 2 — ChatDoctor at tau={a.tau}: serves {served.sum()}/{len(q)} "
          f"({100*served.mean():.1f}%), draft F1 {f1_cd[served].mean():.4f}")

    fall = ~served
    print(f"step 3 — {fall.sum()} rows fall through\n")
    if fall.sum() == 0:
        return

    # ---- step 3: only the fall-through rows, against everything else ---------------------
    v2 = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                         max_features=a.max_features, min_df=2, sublinear_tf=True)
    X2 = v2.fit_transform(other["input"].astype(str))
    qs = [x for x, f in zip(q["input"].astype(str).tolist(), fall) if f]
    ts = [x for x, f in zip(tgt, fall) if f]
    i2, s2 = top1(v2, X2, qs)
    f2 = np.array([token_f1(d, t) for d, t in zip(other["output"].values[i2], ts)])
    src2 = other["source"].values[i2]

    # what those same rows would have got from ChatDoctor anyway (below tau, but not zero)
    cd_fallback = f1_cd[fall]

    print("On the fall-through rows ONLY:")
    print(f"  ChatDoctor's own (sub-threshold) draft : {cd_fallback.mean():.4f}")
    print(f"  best other-corpus draft, ungated       : {f2.mean():.4f}")
    print()
    print(f"{'tau2':>6} {'accepted':>9} {'other-corpus F1':>17} {'same rows via CD':>18}")
    for t2 in (0.0, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60):
        k = s2 >= t2
        if k.sum() == 0:
            continue
        print(f"{t2:>6.2f} {k.sum():>9} {f2[k].mean():>17.4f} {cd_fallback[k].mean():>18.4f}")

    print("\nby retrieved source (ungated):")
    for s_name in pd.unique(src2):
        sel = src2 == s_name
        print(f"  {s_name:20s} n={sel.sum():>4}  draft_f1={f2[sel].mean():.4f}")

    print("\n🔴 The bar step 3 must clear: a draft is only worth routing to the champion if it")
    print("   beats sending the row to the specialist. Qwen D1 answers at Token F1 ~0.26 on its")
    print("   own OUTPUT; a draft near ~0.19 (the measured wrong-match level) is worse than that.")


if __name__ == "__main__":
    raise SystemExit(main())
