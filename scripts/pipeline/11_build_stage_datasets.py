"""11_build_stage_datasets.py — the two datasets that only exist once Tier 1 has a winner.

    python 11_build_stage_datasets.py --winner draft_only

Builds, under data/:

  warmstart_stage1/   E12 stage 1. train = the 123,289-row curated Bengali medical corpus
                      (question -> answer); dev/test copied from the WINNER so stage 1 and
                      stage 2 are scored on the identical frozen split.
  multitask_<winner>/ E13. train = winner's transfer pairs + question_only's Q->A pairs;
                      dev/test from the winner. E13 must also be scored on question_only's
                      dev, which needs no new dataset — decode against ../data/question_only.

🔴 Leak safety is re-asserted here, not assumed. warmstart_corpus/SOURCES.md says its 6,000
dev/test rows were already removed; this script fails if any dev or test id reappears.
Training on a second translation of the answers we evaluate on leaks the eval set just as
surely as training on dev itself.
"""

import argparse
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def assert_no_leak(train: pd.DataFrame, winner: Path, label: str):
    """A dataset that overlaps dev is not a weaker experiment, it is a void one."""
    if "id" not in train.columns:
        print(f"  {label}: no id column — cannot check overlap, and will not pretend to")
        return
    ids = set(train["id"].astype(str))
    for split in ("dev", "test"):
        held = set(pd.read_parquet(winner / f"{split}.parquet")["id"].astype(str))
        n = len(ids & held)
        assert n == 0, f"🔴 {label}: {n} {split} ids leaked into train"
        print(f"  {label}: 0 / {len(held)} {split} ids in train ✅")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--winner", required=True, help="Tier-1 winning dataset dir name")
    a = ap.parse_args()
    winner = DATA / a.winner
    assert (winner / "train.parquet").is_file(), f"no such winner dataset: {winner}"

    # ---- E12 stage 1 -------------------------------------------------------
    src = DATA / "warmstart_corpus" / "master_c_bengali.csv"
    out = DATA / "warmstart_stage1"
    out.mkdir(exist_ok=True)
    df = pd.read_csv(src)
    df = df[["id", "input", "output"]].dropna()
    df = df[(df["input"].str.strip() != "") & (df["output"].str.strip() != "")]
    assert_no_leak(df, winner, "warmstart_stage1")
    df.to_parquet(out / "train.parquet", index=False)
    for split in ("dev", "test"):
        shutil.copy(winner / f"{split}.parquet", out / f"{split}.parquet")
    (out / "FIELDS.txt").write_text(f"stage1 warm start; dev/test from {a.winner}\n")
    print(f"warmstart_stage1: {len(df):,} train rows  ->  {out}")

    # ---- E13 multitask -----------------------------------------------------
    qa = DATA / "question_only"
    out = DATA / f"multitask_{a.winner}"
    out.mkdir(exist_ok=True)
    tr_w = pd.read_parquet(winner / "train.parquet")
    tr_q = pd.read_parquet(qa / "train.parquet")
    # Both halves keep their own id, so a row can be traced back to which task it came
    # from; the model sees only input/output either way.
    both = pd.concat([tr_w[["id", "input", "output"]], tr_q[["id", "input", "output"]]],
                     ignore_index=True)
    assert_no_leak(both, winner, f"multitask_{a.winner}")
    both.to_parquet(out / "train.parquet", index=False)
    for split in ("dev", "test"):
        shutil.copy(winner / f"{split}.parquet", out / f"{split}.parquet")
    (out / "FIELDS.txt").write_text(
        f"multitask: {a.winner} transfer + question_only Q->A; dev/test from {a.winner}\n")
    print(f"multitask_{a.winner}: {len(tr_w):,} transfer + {len(tr_q):,} Q->A "
          f"= {len(both):,} train rows  ->  {out}")
    print("\n🔴 E13 must ALSO be decoded against ../data/question_only to report the "
          "question->answer score, per its EXPERIMENT.md.")


if __name__ == "__main__":
    raise SystemExit(main())
