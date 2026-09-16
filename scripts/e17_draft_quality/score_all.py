#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E17 — score every candidate translation against the competition target.

Finds every *_TRANSLATED.csv (plus the Claude/Codex batch files) in this folder,
joins by hcm_id, and scores each with the exact competition metric on whatever
rows that candidate covers. Every comparison is PAIRED against the Google draft
on the same rows, so row difficulty cancels.

    python score_all.py                 # score everything present
    python score_all.py --min-rows 50   # ignore tiny partial files
"""
import argparse, glob, os, sys
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "NOTEBOOKS"))
from metric import token_f1, rouge_l_f1  # noqa: E402

ALIGNED = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "DATA", "EXTERNAL_COLLECTED_DATA", "Data_Search_5",
    "MASTER_C_BENGALI", "aligned_pairs.csv",
)


def candidates():
    """(label, DataFrame[hcm_id,bengali]) for every candidate file present."""
    out = []
    for f in sorted(glob.glob("*_TRANSLATED.csv")):
        out.append((os.path.basename(f).replace("_TRANSLATED.csv", ""), pd.read_csv(f)))
    for folder, label in (("claude_batches", "claude"), ("codex_batches", "codex")):
        parts = sorted(glob.glob(os.path.join(folder, "*.csv")))
        if parts:
            out.append((label, pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-rows", type=int, default=1)
    a = ap.parse_args()

    ref = pd.read_csv(ALIGNED)
    ref = ref[ref.split == "dev"].set_index("comp_id")

    rows = []
    for label, df in candidates():
        df = df.dropna(subset=["bengali"]).drop_duplicates("hcm_id")
        ids = [i for i in df.hcm_id if i in ref.index]
        if len(ids) < a.min_rows:
            continue
        df = df.set_index("hcm_id").loc[ids]
        sub = ref.loc[ids]

        cand_f1 = np.array([token_f1(b, t) for b, t in zip(df.bengali, sub.target)])
        cand_rl = np.array([rouge_l_f1(b, t) for b, t in zip(df.bengali, sub.target)])
        goog_f1 = np.array([token_f1(d, t) for d, t in zip(sub.draft, sub.target)])
        d = cand_f1 - goog_f1
        se = d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else float("nan")

        b = df.bengali.astype(str)
        rows.append(dict(
            candidate=label, n=len(ids),
            token_f1=cand_f1.mean(), rouge_l=cand_rl.mean(),
            vs_google=d.mean(), se=se, t=d.mean() / se if se else float("nan"),
            wins=f"{(d > 0).sum()}/{len(d)}",
            helo=b.str.startswith("হেলো").mean() * 100,
            nasc=b.str.contains("নাসেনিয়া").mean() * 100,
            google_on_same_rows=goog_f1.mean(),
        ))

    if not rows:
        sys.exit("no candidate files found (expected *_TRANSLATED.csv)")

    r = pd.DataFrame(rows).sort_values("token_f1", ascending=False)
    print("=" * 92)
    print("E17 — candidate translators vs the competition target")
    print("=" * 92)
    print(f"{'candidate':<22}{'n':>5}{'TokenF1':>9}{'Google*':>9}{'vs Google':>11}{'SE':>8}{'t':>7}{'wins':>9}")
    print("-" * 92)
    for _, x in r.iterrows():
        print(f"{x.candidate:<22}{x.n:>5}{x.token_f1:>9.4f}{x.google_on_same_rows:>9.4f}"
              f"{x.vs_google:>+11.4f}{x.se:>8.4f}{x.t:>7.2f}{x.wins:>9}")
    print("-" * 92)
    print("* Google scored on THAT candidate's own rows — candidates cover different subsets,")
    print("  so compare each candidate to its own Google column, never across rows.")
    print()
    print("🔴 CONTAMINATION CHECK — both must be ~0; the target has হেলো 76.4%, নাসেনিয়া 50.0%")
    for _, x in r.iterrows():
        flag = "  ⚠️ LEAKED REGISTER" if (x.helo > 5 or x.nasc > 5) else ""
        print(f"   {x.candidate:<22} হেলো {x.helo:5.1f}%   নাসেনিয়া {x.nasc:5.1f}%{flag}")
    print()
    print("Read: a candidate is only interesting if vs_google is > +0.02 AND |t| > 2.")
    print("A leaked-register candidate is disqualified — it measures styling, not translation.")
    r.to_csv("SCORES.csv", index=False)
    print("\nwrote SCORES.csv")
