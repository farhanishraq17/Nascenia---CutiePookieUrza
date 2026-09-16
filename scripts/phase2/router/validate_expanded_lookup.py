"""validate_expanded_lookup.py — does a BIGGER lookup corpus actually recover better drafts?

    python validate_expanded_lookup.py --repo-root ../..

ROUTER-01 measured content-matching against the 112,154-row ChatDoctor corpus alone:
88.0% routed / 98.07% precision / recovered draft F1 0.5901 at tau=0.40, against a
perfect-id-lookup ceiling of 0.5963.

This asks whether adding every other Bengali doctor-patient corpus we hold (410,525 rows total)
raises the hit rate without importing false positives. More corpus = more recall, but also more
chances for a spurious match, and ROUTER-01 priced a wrong match at draft F1 0.1795 vs 0.5959
for a correct one. That trade is what this script measures.

🔴 LEAK CONTROL, non-negotiable: `bengali_medical_train_master.csv` contains `given_train`
(108,954 competition rows) which includes ALL 5,000 frozen dev ids. Retrieving a dev row's own
answer would score ~1.0 and mean nothing. Every dev/test id is dropped from the corpus before
a single query runs, and the drop is asserted.
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
    ap.add_argument("--n-queries", type=int, default=1000, help="dev rows to probe")
    ap.add_argument("--max-features", type=int, default=200_000)
    a = ap.parse_args()
    root = Path(a.repo_root).resolve()

    from sklearn.feature_extraction.text import TfidfVectorizer

    dev = pd.read_parquet(root / "DATA/PROCESSED/dev.parquet")
    test_ids = set(pd.read_csv(root / "DATA/COMPETITION_PROVIDED_DATA/test.csv",
                               dtype=str)["id"])
    dev_ids = set(dev["id"].astype(str))

    master = pd.read_csv(root / "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_5/"
                                "bengali_medical_train_master.csv")
    master = master.dropna(subset=["input", "output"])
    master = master[master["input"].astype(str).str.strip().astype(bool)
                    & master["output"].astype(str).str.strip().astype(bool)]
    print(f"master corpus: {len(master):,} rows")

    # 🔴 leak control
    before = len(master)
    ids = master["id"].astype(str)
    master = master[~ids.isin(dev_ids | test_ids)].reset_index(drop=True)
    print(f"dropped {before - len(master):,} dev/test rows -> {len(master):,} usable")
    assert not set(master["id"].astype(str)) & (dev_ids | test_ids), "🔴 LEAK"

    q = dev.iloc[: a.n_queries].reset_index(drop=True)
    print(f"queries: {len(q)} dev rows (ids discarded, as if unresolvable)\n")

    corpora = {
        "chatdoctor_only (ROUTER-01 baseline)":
            master[master["source"] == "healthcaremagic"],
        "EXPANDED (every Bengali corpus)": master,
    }

    for name, corp in corpora.items():
        corp = corp.reset_index(drop=True)
        print("=" * 74)
        print(f"{name} — {len(corp):,} rows")
        print("=" * 74)

        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                              max_features=a.max_features, min_df=2, sublinear_tf=True)
        X = vec.fit_transform(corp["input"].astype(str))
        Q = vec.transform(q["input"].astype(str))

        best_i = np.empty(Q.shape[0], dtype=np.int64)
        best_s = np.empty(Q.shape[0], dtype=np.float32)
        step = 256
        for s in range(0, Q.shape[0], step):
            sims = (Q[s:s + step] @ X.T).toarray()
            best_i[s:s + step] = sims.argmax(axis=1)
            best_s[s:s + step] = sims.max(axis=1)

        draft = corp["output"].astype(str).values[best_i]
        src = corp["source"].values[best_i]
        f1 = np.array([token_f1(d, t) for d, t in zip(draft, q["output"].astype(str))])

        print(f"mean top-1 similarity : {best_s.mean():.4f}")
        print(f"retrieved-source mix  : {dict(Counter(src).most_common())}\n")
        print(f"{'tau':>6} {'routed':>8} {'draft F1 (routed)':>18} {'vs ceiling 0.5963':>18}")
        for t in (0.0, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50):
            m = best_s >= t
            if m.sum() == 0:
                continue
            print(f"{t:>6.2f} {100*m.mean():>7.1f}% {f1[m].mean():>18.4f} {f1[m].mean()-0.5963:>+18.4f}")

        # where do the good drafts come from?
        print("\ndraft F1 by retrieved source (tau=0.40):")
        m = best_s >= 0.40
        for s_name in pd.unique(src[m]):
            sel = m & (src == s_name)
            print(f"  {s_name:20s} n={sel.sum():>5}  draft_f1={f1[sel].mean():.4f}")
        print()


if __name__ == "__main__":
    raise SystemExit(main())
