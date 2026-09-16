"""build_branch3_probe.py — extract the exact rows branch 3 would serve, with every candidate input.

    python build_branch3_probe.py --repo-root ../..

Settles the one question the draft-level numbers cannot: on the rows branch 3 would actually
claim, is the CHAMPION fed an ai_medical_chatbot draft better than the SPECIALIST answering the
question directly? Draft F1 measures the champion's *input*; only output F1 decides the router.

Emits `branch3_probe.parquet`, one row per case, with three competing inputs:

    champion_in_aimc  champion input built from the ai_medical_chatbot match   (branch 3)
    champion_in_cd    champion input from ChatDoctor's SUB-threshold match     (lower t1 instead)
    question          the raw patient question                                 (branch 4, Qwen)
    target            the organizers' true answer

🔴 Leak control: every frozen dev/test id is dropped from both corpora before retrieval, so no row
can retrieve its own answer.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TEMPLATE = "english: {en}\nbangla: {bn}"


def top1(vec, X, queries, chunk=256):
    Q = vec.transform(queries)
    bi = np.empty(Q.shape[0], dtype=np.int64)
    bs = np.empty(Q.shape[0], dtype=np.float32)
    for s in range(0, Q.shape[0], chunk):
        S = (Q[s:s + chunk] @ X.T).toarray()
        bi[s:s + chunk] = S.argmax(axis=1)
        bs[s:s + chunk] = S.max(axis=1)
    return bi, bs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    ap.add_argument("--n-queries", type=int, default=1000)
    ap.add_argument("--t1", type=float, default=0.40)
    ap.add_argument("--t2", type=float, default=0.35)
    ap.add_argument("--max-features", type=int, default=200_000)
    ap.add_argument("--out", default="branch3_probe.parquet")
    a = ap.parse_args()
    root = Path(a.repo_root).resolve()
    from sklearn.feature_extraction.text import TfidfVectorizer

    dev = pd.read_parquet(root / "DATA/PROCESSED/dev.parquet")
    test_ids = set(pd.read_csv(root / "DATA/COMPETITION_PROVIDED_DATA/test.csv", dtype=str)["id"])
    dev_ids = set(dev["id"].astype(str))

    # ---- corpora, leak-controlled -------------------------------------------------------
    bn = pd.read_csv(root / "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_3/ChatDoctor dataset/"
                            "bengali_medical_train_clean.csv", dtype=str).dropna(subset=["input", "output"])
    en = pd.read_csv(root / "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_3/ChatDoctor dataset/"
                            "unified_medical_qa_train.csv", dtype=str).dropna(subset=["output"])
    cd = bn[bn["source"] == "healthcaremagic"].copy()
    cd["cid"] = cd["id"].str.replace("hcm_", "", regex=False)
    cd = cd[~cd["cid"].isin(dev_ids | test_ids)].drop_duplicates("cid").reset_index(drop=True)
    en_map = dict(zip(en["id"].str.replace("hcm_", "", regex=False), en["output"]))
    cd = cd[cd["cid"].isin(en_map)].reset_index(drop=True)
    print(f"ChatDoctor corpus (leak-free, English present): {len(cd):,}")

    master = pd.read_csv(root / "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_5/"
                                "bengali_medical_train_master.csv", dtype=str).dropna(subset=["input", "output"])
    aimc = master[master["source"] == "ai_medical_chatbot"].copy()
    aimc = aimc[~aimc["id"].isin(dev_ids | test_ids)]
    d4 = pd.read_csv(root / "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_4/"
                            "ai_medical_chatbot_unique_non_chatdoctor.csv", dtype=str).dropna(subset=["doctor"])
    eng = {f"aimc_{r}": d for r, d in zip(d4["source_row"], d4["doctor"])}
    aimc["english"] = aimc["id"].map(eng)
    aimc = aimc.dropna(subset=["english"]).reset_index(drop=True)
    print(f"ai_medical_chatbot corpus (English recovered): {len(aimc):,}")

    q = dev.iloc[: a.n_queries].reset_index(drop=True)

    # ---- branch 2: ChatDoctor first -----------------------------------------------------
    v1 = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                         max_features=a.max_features, min_df=2, sublinear_tf=True)
    X1 = v1.fit_transform(cd["input"].astype(str))
    i1, s1 = top1(v1, X1, q["input"].astype(str).tolist())
    fall = s1 < a.t1
    print(f"branch 2 serves {int((~fall).sum())}/{len(q)}; {int(fall.sum())} fall through")

    # ---- branch 3: ai_medical_chatbot on the fall-through only --------------------------
    idxf = np.where(fall)[0]
    v2 = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                         max_features=a.max_features, min_df=2, sublinear_tf=True)
    X2 = v2.fit_transform(aimc["input"].astype(str))
    i2, s2 = top1(v2, X2, q["input"].astype(str).values[idxf].tolist())
    claim = s2 >= a.t2
    sel = idxf[claim]
    print(f"branch 3 claims {len(sel)} rows at t2={a.t2}")
    assert len(sel), "branch 3 claims nothing -- lower --t2"

    rows = []
    for k, gi in enumerate(np.where(claim)[0]):
        row_i = sel[k]
        ar = aimc.iloc[i2[gi]]
        cr = cd.iloc[i1[row_i]]
        rows.append({
            "id": str(q["id"].iloc[row_i]),
            "question": str(q["input"].iloc[row_i]),
            "target": str(q["output"].iloc[row_i]),
            "champion_in_aimc": TEMPLATE.format(en=ar["english"], bn=ar["output"]),
            "champion_in_cd": TEMPLATE.format(en=en_map[cr["cid"]], bn=cr["output"]),
            "aimc_sim": float(s2[gi]),
            "cd_sim": float(s1[row_i]),
            "aimc_id": ar["id"],
            "cd_cid": cr["cid"],
        })
    out = pd.DataFrame(rows)
    out.to_parquet(a.out, index=False)
    print(f"\nwrote {a.out}  ({len(out)} rows)")
    print(f"  aimc similarity : mean {out['aimc_sim'].mean():.3f}  min {out['aimc_sim'].min():.3f}")
    print(f"  cd   similarity : mean {out['cd_sim'].mean():.3f}  (all below t1={a.t1})")


if __name__ == "__main__":
    raise SystemExit(main())
