"""Build MASTER_C_BENGALI — the curated, leak-safe subset of Data_Search_5.

Data_Search_5's `bengali_medical_train_master.csv` (410,525 rows) is a raw union of nine
sources. Three are unusable, one is off-register, and one is not external data at all and
carries a dev-split leak. This script keeps what is defensible and documents the rest.

Two outputs, deliberately separate:

  aligned_pairs.csv    THE asset. Competition id <-> our Bengali ChatDoctor translation
                       (ALIGN-01). Columns: comp_id, split, draft, target.
                       This is the register-transfer training/eval/inference data.

  master_c_bengali.csv A clean Bengali medical-dialogue corpus for optional warm-start
                       and Phase 2 clinical quality. Columns: id, source, input, output.
                       🔴 hcm rows for dev/test ids are REMOVED — they are a different
                       translation of answers we evaluate on, so training on them leaks.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# Kept. Real Bengali patient->doctor dialogue with a usable register.
KEEP = ["healthcaremagic", "icliniq", "genmedgpt", "doctor_qa_bangla"]

# Dropped, with the measured reason. See SOURCES.md for the evidence behind each.
DROP = {
    "alpaca_health": "not medical — the 'medical keyword' filter matched homographs "
                     "(computer virus/worm, the Great Depression)",
    "disease_db": "wrong shape — structured symptom/test/drug bullet lists, not dialogue",
    "mts_dialog": "wrong task — clinical note in, doctor's opening line out; not question->answer",
    "ai_medical_chatbot": "off-register — English translated by a different pass; opens 'হাই' "
                          "where the target corpus opens 'হেলো'. Held out, not deleted.",
    "given_train": "NOT external data — this is the competition train.csv, and it contains "
                   "all 5,000 frozen dev rows. Mixing it into a training pool destroys the "
                   "dev split.",
}

BRAND = [
    (re.compile(r"চ্যাট\s*ডক্টর"), "নাসেনিয়া ডক"),
    (re.compile(r"Chat\s*Doctor", re.I), "নাসেনিয়া ডক"),
]


def normalize_brand(s: str) -> str:
    s = str(s)
    for pat, rep in BRAND:
        s = pat.sub(rep, s)
    return re.sub(r"\s+", " ", s).strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build MASTER_C_BENGALI")
    ap.add_argument("--master", required=True, help="bengali_medical_train_master.csv")
    ap.add_argument("--proc", required=True, help="01_prep.py output dir (dev/test.parquet)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    print("reading master …")
    m = pd.read_csv(a.master, dtype=str)
    print(f"  {len(m):,} rows, sources: {m['source'].nunique()}")

    dev = pd.read_parquet(Path(a.proc) / "dev.parquet")
    test = pd.read_parquet(Path(a.proc) / "test.parquet")
    train = pd.read_parquet(Path(a.proc) / "train.parquet")
    dev_ids, test_ids = set(dev["id"]), set(test["id"])
    print(f"  frozen split: train {len(train):,} · dev {len(dev):,} · test {len(test):,}")

    # ---------------------------------------------------------------- aligned pairs
    hcm = m[m["source"] == "healthcaremagic"].copy()
    hcm["comp_id"] = hcm["id"].str.replace("hcm_", "", regex=False).astype(int)
    hcm = hcm.drop_duplicates("comp_id").set_index("comp_id")

    rows = []
    for name, df in (("train", train), ("dev", dev), ("test", test)):
        have = df[df["id"].isin(hcm.index)]
        rows.append(pd.DataFrame({
            "comp_id": have["id"].values,
            "split": name,
            "draft": hcm.loc[have["id"], "output"].values,
            "target": have["output"].values if "output" in have.columns else "",
        }))
        print(f"  aligned {name:5s}: {len(have):,}/{len(df):,} ({len(have)/len(df)*100:.1f}%)")
    aligned = pd.concat(rows, ignore_index=True)
    aligned.to_csv(out / "aligned_pairs.csv", index=False, encoding="utf-8")

    # dev/test coverage must be total: a row without a draft cannot be predicted at all
    for name, n in (("dev", len(dev)), ("test", len(test))):
        got = (aligned["split"] == name).sum()
        assert got == n, f"❌ {name} coverage {got}/{n} — fix before training"

    # ---------------------------------------------------------------- corpus
    keep = m[m["source"].isin(KEEP)].copy()

    # 🔴 Remove hcm rows for dev/test ids. They are a SECOND TRANSLATION of answers we
    # score against, so training on them leaks the evaluation set just as surely as
    # training on dev itself would.
    hcm_mask = keep["source"] == "healthcaremagic"
    cid = keep.loc[hcm_mask, "id"].str.replace("hcm_", "", regex=False).astype(int)
    leak = keep.loc[hcm_mask].index[cid.isin(dev_ids | test_ids)]
    print(f"\n  removing {len(leak):,} hcm rows whose id is in the frozen dev/test split")
    keep = keep.drop(index=leak)

    before = len(keep)
    keep["input"] = [normalize_brand(x) for x in keep["input"]]
    keep["output"] = [normalize_brand(x) for x in keep["output"]]
    keep = keep[(keep["input"].str.split().str.len() >= 5)
                & (keep["output"].str.split().str.len() >= 10)]
    keep = keep.drop_duplicates(subset=["input", "output"])
    print(f"  {before:,} -> {len(keep):,} after brand-normalise, degenerate filter, dedup")

    corpus = keep[["id", "source", "input", "output"]].reset_index(drop=True)
    corpus.to_csv(out / "master_c_bengali.csv", index=False, encoding="utf-8")

    print(f"\n{'source':22s} {'kept':>8s}")
    for s, g in corpus.groupby("source"):
        print(f"{s:22s} {len(g):8,d}")
    print(f"{'TOTAL':22s} {len(corpus):8,d}")

    print("\nexcluded:")
    for s, why in DROP.items():
        n = (m["source"] == s).sum()
        print(f"  {s:20s} {n:7,d}  {why[:70]}")

    L = corpus["output"].str.split().str.len()
    print(f"\ncorpus output tokens: mean {L.mean():.1f}  p50 {L.median():.0f}  "
          f"(competition references ~100)")
    print(f"written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
