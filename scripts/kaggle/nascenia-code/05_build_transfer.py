"""Build the register-transfer dataset: external Bengali draft -> competition-register answer.

Why this task shape (ALIGN-01, LOCAL_EXPERIMENTS.md):
  The competition `id` is a row index into ChatDoctor / HealthCareMagic-100k
  (github.com/Kent0n-Li/ChatDoctor). Our own Bengali translation of that corpus is keyed
  `hcm_<same index>`, so every competition row has an independent Bengali translation of
  the SAME doctor answer. Predicting that translation verbatim scores Token F1 0.5984 /
  ROUGE-L 0.5482 on the frozen dev split, versus 0.2576 / 0.1776 for our best fine-tune.

  But a lookup is not model output (Rules Sec.8) and cannot satisfy Phase 2 reproducibility.
  So instead we train a model to do the remaining work: map the external translator's
  register onto the competition translator's. The gap is large and systematic --

      opener 'হেলো'    external  0.06%  vs references 76.62%
      brand  'নাসেনিয়া' external  0.00%  vs references 49.98%

  -- so the model has something real to learn, and its output is genuinely generated.

Emits train/dev/test parquet with columns (id, input, output) so 02_train_t5.py and
04_decode.py consume them unchanged.

    input  = the external Bengali draft   (+ optionally the patient question)
    output = the competition-register answer   (absent for test)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

DRAFT_TAG = "খসড়া:"
QUESTION_TAG = "প্রশ্ন:"


def load_hcm(path: Path) -> pd.DataFrame:
    """External translation keyed by ChatDoctor row index."""
    d = pd.read_csv(path)
    if "hcm_id" not in d.columns:              # raw Data_Search_3 export
        d = d[d["source"] == "healthcaremagic"].copy()
        d["hcm_id"] = d["id"].str.replace("hcm_", "", regex=False).astype(int)
    return d.drop_duplicates("hcm_id").set_index("hcm_id")


def build(split: pd.DataFrame, hcm: pd.DataFrame, with_question: bool) -> pd.DataFrame:
    have = split[split["id"].isin(hcm.index)].copy()
    draft = hcm.loc[have["id"], "output"].astype(str).values

    if with_question:
        src = [f"{QUESTION_TAG} {q}\n{DRAFT_TAG} {d}"
               for q, d in zip(have["input"].astype(str), draft)]
    else:
        src = list(draft)

    out = pd.DataFrame({"id": have["id"].values, "input": src})
    if "output" in have.columns:
        out["output"] = have["output"].values
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build register-transfer parquets")
    ap.add_argument("--proc", required=True, help="01_prep.py output dir (train/dev/test.parquet)")
    ap.add_argument("--hcm", required=True, help="hcm_bn.csv, or the raw Data_Search_3 csv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--with-question", action="store_true",
                    help="prepend the patient question to the draft (longer source)")
    a = ap.parse_args(argv)

    proc, out = Path(a.proc), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    hcm = load_hcm(Path(a.hcm))
    print(f"hcm rows {len(hcm)}  index {hcm.index.min()}–{hcm.index.max()}")

    for split in ("train", "dev", "test"):
        src = proc / f"{split}.parquet"
        if not src.is_file():
            print(f"  skip {split}: {src} missing")
            continue
        df = pd.read_parquet(src)
        built = build(df, hcm, a.with_question)
        cov = len(built) / len(df) * 100
        built.to_parquet(out / f"{split}.parquet", index=False)

        n_src = built["input"].str.split().str.len()
        line = (f"  {split:5s} {len(built):6d}/{len(df):6d} rows ({cov:5.1f}% covered)  "
                f"src tokens mean {n_src.mean():6.1f} p95 {n_src.quantile(.95):6.0f}")
        if "output" in built.columns:
            n_tgt = built["output"].str.split().str.len()
            line += f"  tgt mean {n_tgt.mean():6.1f}"
        print(line)

        # A dev/test row without a draft cannot be predicted by this model at all, so a
        # coverage hole is a silent scoring hole. Fail loudly rather than shipping short.
        if split in ("dev", "test") and len(built) != len(df):
            raise SystemExit(
                f"❌ {split}: only {len(built)}/{len(df)} rows have an external draft. "
                f"This model cannot predict the rest — add a fallback before training.")

    print(f"\nwritten to {out}   (input = {'question + draft' if a.with_question else 'draft only'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
