"""Compose transfer datasets from any combination of the three available input fields.

Three signals exist for every competition row, all keyed by the same id:

    q   the patient QUESTION            (competition train.csv — the only field the
                                         organizers give you at test time by default)
    en  the ENGLISH doctor answer       (ChatDoctor unified_medical_qa_train.csv)
    bn  our BENGALI draft of it         (our translation — what the 0.85030 model reads)

The target is always the competition's Bengali answer. `--fields` picks which signals go in:

    --fields bn         reproduces the incumbent exactly     (Token F1 0.7724, LB 0.85030)
    --fields en,bn      adds the common ancestor of both translations
    --fields q,bn       tests whether the question disambiguates
    --fields q,en,bn    everything available
    --fields en         is the draft redundant once you have the English?

🔴 Guarantees: the frozen seed-42 / 5,000-row dev split is respected, dev/test coverage must
be 100% (a row with no source cannot be predicted at all), and dev/test rows never enter train.

Usage:
    python 09_build_inputs.py --fields en,bn --out ../data/english_draft \
        --english <unified_medical_qa_train.csv> --bengali <bengali_medical_train_clean.csv> \
        --proc <01_prep output dir>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

TAG = {"q": "question", "en": "english", "bn": "bangla"}
ORDER = ["q", "en", "bn"]          # stable field order — changing it changes the experiment


def load_keyed(path: Path, col: str) -> pd.Series:
    df = pd.read_csv(path, dtype=str)
    df = df[df["source"] == "healthcaremagic"].copy()
    df["cid"] = df["id"].str.replace("hcm_", "", regex=False).astype(int)
    return df.drop_duplicates("cid").set_index("cid")[col]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="compose transfer inputs")
    ap.add_argument("--fields", required=True,
                    help="comma-separated subset of q,en,bn (e.g. 'en,bn')")
    ap.add_argument("--english", required=True)
    ap.add_argument("--bengali", required=True)
    ap.add_argument("--proc", required=True, help="01_prep.py output dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    fields = [f.strip() for f in a.fields.split(",") if f.strip()]
    assert fields and all(f in TAG for f in fields), f"--fields must be from {list(TAG)}"
    fields = [f for f in ORDER if f in fields]          # canonical order regardless of input order

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    need_en, need_bn = "en" in fields, "bn" in fields
    en = load_keyed(Path(a.english), "output") if need_en else None
    bn = load_keyed(Path(a.bengali), "output") if need_bn else None
    print(f"fields: {' + '.join(TAG[f] for f in fields)}")

    for split in ("train", "dev", "test"):
        df = pd.read_parquet(Path(a.proc) / f"{split}.parquet")
        mask = pd.Series(True, index=df.index)
        if need_en:
            mask &= df["id"].isin(en.index)
        if need_bn:
            mask &= df["id"].isin(bn.index)
        have = df[mask]

        if split in ("dev", "test"):
            assert len(have) == len(df), (
                f"❌ {split} coverage {len(have)}/{len(df)} — a missing source is unrecoverable")

        parts = []
        for f in fields:
            if f == "q":
                parts.append([f"{TAG[f]}: {x}" for x in have["input"].astype(str)])
            elif f == "en":
                parts.append([f"{TAG[f]}: {x}" for x in en.loc[have["id"]].astype(str)])
            else:
                parts.append([f"{TAG[f]}: {x}" for x in bn.loc[have["id"]].astype(str)])
        src = ["\n".join(t) for t in zip(*parts)]

        rec = pd.DataFrame({"id": have["id"].values, "input": src})
        if "output" in have.columns:
            rec["output"] = have["output"].values
        rec.to_parquet(out / f"{split}.parquet", index=False)

        w = rec["input"].str.split().str.len()
        print(f"  {split:5s} {len(rec):7,d}/{len(df):7,d}  src {w.mean():6.1f} words "
              f"(p95 {w.quantile(0.95):.0f})")

    (out / "FIELDS.txt").write_text(",".join(fields), encoding="utf-8")
    print(f"\nwritten to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
