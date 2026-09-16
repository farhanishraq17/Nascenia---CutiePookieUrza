"""10_truncation_report.py — how much does each experiment's sequence cap actually cut?

Every EXPERIMENT.md asks for "% truncated (source and target)" and none of the training
scripts measure it. It matters because a weak score from a truncated input measures the
truncation, not the hypothesis — E07 exists entirely to price that.

    python 10_truncation_report.py                       # all six input combinations
    python 10_truncation_report.py --sample 20000        # faster, still ±0.3%

Reports the cap each dataset is trained at, plus p95/p99/max token counts, so a cap that
is about to start biting is visible before it does.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# dataset -> (source cap, target cap, tokenizer) exactly as the registry trains it
CAPS = {
    "draft_only":     (768, 512, "csebuetnlp/banglat5"),
    "english_draft":  (768, 512, "csebuetnlp/banglat5"),
    "question_draft": (640, 512, "csebuetnlp/banglat5"),
    "all_inputs":     (1024, 512, "csebuetnlp/banglat5"),
    "english_only":   (640, 512, "csebuetnlp/banglat5"),
    "question_only":  (768, 512, "csebuetnlp/banglat5"),
}
# E08/E09 read the same rows through a tokenizer that needs 88% more target tokens.
EXTRA = [("draft_only", 640, 640, "google/mt5-base")]


def pct(series, cap):
    return round(100.0 * float((series > cap).mean()), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--split", default="train")
    ap.add_argument("--out", default=None, help="also write JSON here")
    a = ap.parse_args()

    from transformers import AutoTokenizer
    try:
        from normalizer import normalize
    except ImportError:
        def normalize(s):
            return s

    jobs = [(d, s, t, m) for d, (s, t, m) in CAPS.items()] + list(EXTRA)
    toks, out = {}, []
    print(f"| dataset | tokenizer | src cap | % src cut | src p95 | src max | "
          f"tgt cap | % tgt cut | tgt p95 | tgt max |")
    print("|" + "---|" * 10)
    for data, scap, tcap, model in jobs:
        f = ROOT / "data" / data / f"{a.split}.parquet"
        if not f.is_file():
            print(f"| {data} | — | missing {f} |")
            continue
        df = pd.read_parquet(f)
        if a.sample and len(df) > a.sample:
            df = df.sample(a.sample, random_state=42)
        if model not in toks:
            toks[model] = AutoTokenizer.from_pretrained(model)
        tok = toks[model]
        src = pd.Series([len(x) for x in tok([normalize(s) for s in df["input"]],
                                             add_special_tokens=True)["input_ids"]])
        tgt = pd.Series([len(x) for x in tok([normalize(s) for s in df["output"]],
                                             add_special_tokens=True)["input_ids"]])
        row = dict(dataset=data, tokenizer=model, split=a.split, rows=len(df),
                   src_cap=scap, src_cut_pct=pct(src, scap),
                   src_p95=int(src.quantile(.95)), src_max=int(src.max()),
                   tgt_cap=tcap, tgt_cut_pct=pct(tgt, tcap),
                   tgt_p95=int(tgt.quantile(.95)), tgt_max=int(tgt.max()))
        out.append(row)
        print(f"| {data} | {model.split('/')[-1]} | {scap} | **{row['src_cut_pct']}%** | "
              f"{row['src_p95']} | {row['src_max']} | {tcap} | "
              f"**{row['tgt_cut_pct']}%** | {row['tgt_p95']} | {row['tgt_max']} |")
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    raise SystemExit(main())
