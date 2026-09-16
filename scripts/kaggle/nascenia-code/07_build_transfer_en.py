"""Build the ENGLISH+DRAFT -> competition-register transfer dataset.

The hypothesis (PLAN.md 5.0 follow-up):

    competition target = f_B(English)     organizers' translation
    our draft          = f_A(English)     our translation
    current XFER model : f_A(English) -> f_B(English)      two hops
    THIS model         : English + f_A(English) -> f_B(English)

The English original is the common ancestor of both translations. Feeding it adds
information the draft lost, rather than adding model capacity — which is the right
lever, since two BanglaT5 seeds already agree to 0.0001 (the model is not the bottleneck).

Emits train/dev/test.parquet with `input`/`output`, so `02_train_t5.py --data-dir` and
`04_decode.py --data-dir` consume it unchanged.

🔴 The frozen split is respected: dev/test rows never enter train, and coverage on
dev/test must be total or the build fails — a row without a source cannot be predicted.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# Explicit field tags. mT5 has no pretrained notion of these, but a stable, unambiguous
# separator lets the model learn which span is which — and keeps the format reproducible
# for Phase 2, which matters more than squeezing tokens.
TEMPLATE = "english: {en}\nbangla: {bn}"


def load_keyed(path: Path, col: str) -> pd.Series:
    """Read a ChatDoctor-format csv and key it by the competition id."""
    df = pd.read_csv(path, dtype=str)
    df = df[df["source"] == "healthcaremagic"].copy()
    df["cid"] = df["id"].str.replace("hcm_", "", regex=False).astype(int)
    return df.drop_duplicates("cid").set_index("cid")[col]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build english+draft transfer data")
    ap.add_argument("--english", required=True, help="unified_medical_qa_train.csv")
    ap.add_argument("--bengali", required=True, help="bengali_medical_train_clean.csv")
    ap.add_argument("--proc", required=True, help="01_prep.py output dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--english-only", action="store_true",
                    help="ablation: drop the Bengali draft from the input")
    ap.add_argument("--draft-only", action="store_true",
                    help="control: drop the English, reproducing the 0.7724 incumbent's input")
    a = ap.parse_args(argv)
    assert not (a.english_only and a.draft_only), "pick at most one ablation"

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    print("reading sources …")
    en = load_keyed(Path(a.english), "output")   # the English DOCTOR ANSWER
    bn = load_keyed(Path(a.bengali), "output")   # our Bengali translation of it
    print(f"  english {len(en):,}  ·  bengali draft {len(bn):,}")

    for split in ("train", "dev", "test"):
        df = pd.read_parquet(Path(a.proc) / f"{split}.parquet")
        have = df[df["id"].isin(en.index) & df["id"].isin(bn.index)]
        cov = len(have) / len(df) * 100

        # dev/test must be total: a row with no source is a row this model cannot predict
        # at all, which would be a silent scoring hole rather than an error.
        if split in ("dev", "test"):
            assert len(have) == len(df), (
                f"❌ {split} coverage {len(have)}/{len(df)} — a missing source is unrecoverable")

        if a.english_only:
            src = [str(x) for x in en.loc[have["id"]]]
        elif a.draft_only:
            # Control: reproduces the incumbent's input exactly (Token F1 0.7724, LB 0.85030),
            # so a new model trained on this is directly comparable to BanglaT5.
            src = [str(x) for x in bn.loc[have["id"]]]
        else:
            src = [TEMPLATE.format(en=e, bn=b)
                   for e, b in zip(en.loc[have["id"]], bn.loc[have["id"]])]

        rec = pd.DataFrame({"id": have["id"].values, "input": src})
        if "output" in have.columns:
            rec["output"] = have["output"].values
        rec.to_parquet(out / f"{split}.parquet", index=False)

        w = rec["input"].str.split().str.len()
        print(f"  {split:5s} {len(rec):6,d}/{len(df):6,d} ({cov:5.1f}%)  "
              f"src {w.mean():6.1f} words (p95 {w.quantile(0.95):.0f})")

    print(f"\nwritten to {out}   mode = {'ENGLISH ONLY' if a.english_only else 'DRAFT ONLY (control)' if a.draft_only else 'english + bengali draft'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
