"""
01_prep.py — clean the competition data and freeze the dev split.

Implements PLAN.md section 4:
  1. Drop nulls; drop degenerate rows (input < 10 tokens, output < 15 tokens)
  2. Normalize the residual চ্যাটডক্টর -> নাসেনিয়া ডক branding
  3. Unicode NFC + whitespace collapse; parenthesized English terms preserved
  4. Deduplicate exact (input, output) pairs; keep duplicate outputs
  5. Split 5,000 dev / rest train, fixed seed, saved to disk

Outputs to DATA/PROCESSED/:
    train.parquet   training rows           (id, input, output)
    dev.parquet     frozen holdout, 5,000   (id, input, output)
    test.parquet    competition test, 1,000 (id, input)
    prep_report.txt human-readable summary

THE DEV SPLIT IS THE SOURCE OF TRUTH. Never train on it. Never regenerate it with
a different seed once experiments have started — every number in
LOCAL_EXPERIMENTS.md would silently stop being comparable.

Usage
-----
    python 01_prep.py
    python 01_prep.py --dev-size 5000 --seed 42
    python 01_prep.py --no-brand-normalize     # ablation
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "DATA" / "COMPETITION_PROVIDED_DATA"
OUT = ROOT / "DATA" / "PROCESSED"

# Bengali "ChatDoctor" -> "Nascenia Doc".
# Plain stem replacement is correct here: Bengali case suffixes attach cleanly, so
#   চ্যাটডক্টরে   -> নাসেনিয়া ডকে
#   চ্যাটডক্টরকে  -> নাসেনিয়া ডককে
#   চ্যাটডক্টরের  -> নাসেনিয়া ডকের
# all fall out of replacing the stem alone. Verified against the 12 observed forms.
BRAND_BN_FROM = "চ্যাটডক্টর"
BRAND_BN_TO = "নাসেনিয়া ডক"
BRAND_LATIN = re.compile(r"chat\s*doctor", re.IGNORECASE)

_WS = re.compile(r"\s+")

MIN_INPUT_TOKENS = 10
MIN_OUTPUT_TOKENS = 15


def normalize_text(s: str) -> str:
    """NFC + whitespace collapse. Punctuation and English terms are left intact."""
    return _WS.sub(" ", unicodedata.normalize("NFC", str(s))).strip()


def normalize_brand(s: str) -> str:
    """
    Rewrite residual ChatDoctor branding to Nascenia Doc.

    Why: ~48% of references contain নাসেনিয়া ডক and only ~2.9% contain চ্যাটডক্টর.
    The model cannot know which variant a given reference used, so always emitting
    the majority form maximizes expected token overlap. Predicting the 2.9%
    minority form is never the optimal bet.
    """
    return BRAND_LATIN.sub(BRAND_BN_TO, str(s).replace(BRAND_BN_FROM, BRAND_BN_TO))


def n_tokens(s: str) -> int:
    return len(str(s).split())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Prepare data and freeze the dev split")
    ap.add_argument("--dev-size", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--min-input-tokens", type=int, default=MIN_INPUT_TOKENS)
    ap.add_argument("--min-output-tokens", type=int, default=MIN_OUTPUT_TOKENS)
    ap.add_argument("--no-brand-normalize", action="store_true")
    ap.add_argument("--raw", default=None,
                    help="dir containing train.csv/test.csv "
                         "(Kaggle: /kaggle/input/competitions/nascenia-ai-hackathon)")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)

    raw_dir = Path(a.raw) if a.raw else RAW
    if not (raw_dir / "train.csv").exists():
        # fall back to globbing the Kaggle mount, whose dir name is not the slug
        import glob as _glob
        hits = _glob.glob("/kaggle/input/**/train.csv", recursive=True)
        if hits:
            raw_dir = Path(hits[0]).parent
        else:
            raise FileNotFoundError(f"train.csv not found under {raw_dir}")

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    log: list[str] = []

    def say(msg=""):
        print(msg)
        log.append(msg)

    say("=" * 68)
    say("01_prep.py — data preparation")
    say("=" * 68)
    say(f"seed={a.seed}  dev_size={a.dev_size}  brand_normalize={not a.no_brand_normalize}")
    say()

    # ---------------- load ----------------
    say(f"raw dir: {raw_dir}")
    train = pd.read_csv(raw_dir / "train.csv")
    test = pd.read_csv(raw_dir / "test.csv")
    say(f"loaded train.csv  {train.shape}")
    say(f"loaded test.csv   {test.shape}")
    n0 = len(train)

    # ---------------- 1. nulls ----------------
    train = train.dropna(subset=["input", "output"]).copy()
    say(f"\n[1] dropped nulls                  -{n0 - len(train):>6}   -> {len(train)}")

    # ---------------- 2/3. normalize ----------------
    train["input"] = train["input"].map(normalize_text)
    train["output"] = train["output"].map(normalize_text)
    test["input"] = test["input"].map(normalize_text)

    if not a.no_brand_normalize:
        hits_out = int(train["output"].str.contains(BRAND_BN_FROM, regex=False).sum())
        hits_in = int(train["input"].str.contains(BRAND_BN_FROM, regex=False).sum())
        hits_lat = int(train["output"].str.contains(BRAND_LATIN).sum())
        hits_test = int(test["input"].str.contains(BRAND_BN_FROM, regex=False).sum())

        train["input"] = train["input"].map(normalize_brand)
        train["output"] = train["output"].map(normalize_brand)
        # test inputs get the identical transform so train/test stay consistent
        test["input"] = test["input"].map(normalize_brand)

        say(f"\n[2] brand normalize চ্যাটডক্টর -> নাসেনিয়া ডক")
        say(f"      train outputs rewritten     {hits_out:>6}  ({100*hits_out/len(train):.2f}%)")
        say(f"      train inputs rewritten      {hits_in:>6}")
        say(f"      latin 'ChatDoctor' outputs  {hits_lat:>6}")
        say(f"      test inputs rewritten       {hits_test:>6}")
        left = int(train["output"].str.contains(BRAND_BN_FROM, regex=False).sum())
        say(f"      residual after rewrite      {left:>6}  {'✅' if left == 0 else '⚠️'}")
    else:
        say("\n[2] brand normalization SKIPPED (--no-brand-normalize)")

    say("\n[3] NFC + whitespace collapse applied to all text fields")

    # ---------------- 4. degenerate rows ----------------
    it = train["input"].map(n_tokens)
    ot = train["output"].map(n_tokens)
    keep = (it >= a.min_input_tokens) & (ot >= a.min_output_tokens)
    dropped_short = int((~keep).sum())
    train = train[keep].copy()
    say(f"\n[4] dropped degenerate rows        -{dropped_short:>6}   -> {len(train)}")
    say(f"      (input < {a.min_input_tokens} tokens or output < {a.min_output_tokens} tokens)")

    # ---------------- 5. dedup ----------------
    before = len(train)
    train = train.drop_duplicates(subset=["input", "output"]).copy()
    say(f"\n[5] dropped exact (input,output) dupes -{before - len(train):>2}   -> {len(train)}")
    dup_out = int(train["output"].duplicated().sum())
    say(f"      duplicate outputs KEPT       {dup_out:>6}  (they encode the boilerplate prior)")

    # ---------------- 6. split ----------------
    rng = np.random.RandomState(a.seed)
    perm = rng.permutation(len(train))
    dev = train.iloc[perm[: a.dev_size]].reset_index(drop=True)
    tr = train.iloc[perm[a.dev_size :]].reset_index(drop=True)

    assert set(dev["id"]).isdisjoint(set(tr["id"])), "dev/train id leakage"
    assert len(dev) + len(tr) == len(train)

    say(f"\n[6] split (seed={a.seed})")
    say(f"      train  {len(tr):>7}")
    say(f"      dev    {len(dev):>7}   FROZEN — never train on this")

    # ---------------- stats ----------------
    say("\n" + "-" * 68)
    say("token length stats (whitespace)")
    say("-" * 68)
    say(f"{'field':16s} {'mean':>7} {'p25':>6} {'p50':>6} {'p75':>6} {'p90':>6} {'p99':>6}")
    for name, ser in [
        ("train input", tr["input"]), ("train output", tr["output"]),
        ("dev input", dev["input"]), ("dev output", dev["output"]),
        ("test input", test["input"]),
    ]:
        L = ser.map(n_tokens)
        q = L.quantile([0.25, 0.5, 0.75, 0.90, 0.99])
        say(f"{name:16s} {L.mean():7.1f} " + " ".join(f"{q[k]:6.0f}" for k in [0.25, 0.5, 0.75, 0.90, 0.99]))

    # use metric.py's tokenizer so this stat matches how the metric actually tokenizes
    # (a plain .split() leaves "হেলো," attached and badly undercounts)
    from metric import tokenize as metric_tokenize

    op = tr["output"].map(lambda s: (metric_tokenize(s) + [""])[0])
    say(f"\noutputs starting with 'হেলো': {100 * (op == 'হেলো').mean():.2f}%")
    say(f"outputs containing 'নাসেনিয়া ডক': "
        f"{100 * tr['output'].str.contains(BRAND_BN_TO, regex=False).mean():.2f}%")

    # sanity: no test leakage into training
    overlap = int(test["input"].isin(set(tr["input"])).sum())
    say(f"\ntest inputs found in train: {overlap}  {'✅' if overlap == 0 else '⚠️'}")

    # ---------------- write ----------------
    tr.to_parquet(out_dir / "train.parquet", index=False)
    dev.to_parquet(out_dir / "dev.parquet", index=False)
    test.to_parquet(out_dir / "test.parquet", index=False)

    say("\n" + "-" * 68)
    say(f"written to {out_dir}")
    for f in ["train.parquet", "dev.parquet", "test.parquet"]:
        p = out_dir / f
        say(f"  {f:16s} {p.stat().st_size / 1e6:8.2f} MB")

    (out_dir / "prep_report.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    say(f"  prep_report.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
