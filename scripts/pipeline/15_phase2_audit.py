"""15_phase2_audit.py — E16. Audit generated answers for the failure modes an LLM judge
punishes and Token F1 rewards.

    python 15_phase2_audit.py ../E05_train_to_convergence/english_draft/main/test.json \\
        ../E01_add_english/main/test.json --out ../E16_phase2_audit/audit.json

**Phase 2 is 20 % of the final score and judged on a different objective.** Token F1 is
happy to pay for a repeated clause — repetition raises recall and barely dents precision —
so the Phase-1 leaderboard cannot see the one failure this experiment exists to catch. One
arm already produced *"gastroenteritis can be caused by gastroenteritis"*: free on Token
F1, near-zero to a judge.

WHAT THIS MEASURES (deterministic, no model, no API — runs anywhere in seconds)

  repeat_sentence_pct   answers containing the same sentence twice — the loop failure
  repeat_5gram_max      worst within-answer 5-gram repetition rate
  tautology_pct         "X ... caused by ... X" / "X is a X" self-reference
  truncated_pct         ends without terminal punctuation — a cut-off answer
  latin_frac_mean       fraction of Latin characters. The corpus mixes in parenthesised
                        English on purpose (`পিসিওডি (PCOD)`), so a HIGH value means
                        untranslated English leaked, not that the term list was used
  empty / very_short    degenerate outputs
  len_p05 / p50 / p95   length distribution against the references' ~100 tokens

🔴 WHAT THIS DOES NOT MEASURE. Clinical correctness, contradiction, and unsafe advice need
a judge with medical knowledge. There is no LLM-judge API on this machine, so those three
rows of E16's spec are **not covered here** and must not be reported as passing. This
script narrows the manual review to the arms and rows most likely to fail.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metric import tokenize  # noqa: E402

SENT_SPLIT = re.compile(r"[।\.\!\?\n]+")
TERMINAL = ("।", ".", "!", "?", "…")


def sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text) if len(s.strip()) > 12]


def max_ngram_repeat(toks, n=5):
    if len(toks) < n * 2:
        return 0.0
    grams = Counter(tuple(toks[i:i + n]) for i in range(len(toks) - n + 1))
    return (max(grams.values()) - 1) / max(1, len(grams))


def tautology(text):
    """'X ... caused by ... X' and 'X is a X' — the shape that scores free Token F1."""
    for s in sentences(text):
        w = [t for t in tokenize(s) if len(t) > 3]
        if not w:
            continue
        c = Counter(w)
        top, n = c.most_common(1)[0]
        if n >= 3 and len(w) <= 25:      # one content word dominating a short sentence
            return True
    return False


def audit(preds, name):
    n = max(len(preds), 1)
    lens = [len(tokenize(p)) for p in preds]
    lens_sorted = sorted(lens)

    def q(f):
        return lens_sorted[min(len(lens_sorted) - 1, int(f * len(lens_sorted)))]

    rep_sent = sum(1 for p in preds
                   if len(sentences(p)) != len(set(sentences(p))) and sentences(p))
    rep5 = [max_ngram_repeat(tokenize(p)) for p in preds]
    latin = [sum(c.isascii() and c.isalpha() for c in p) / max(1, len(p)) for p in preds]
    trunc = sum(1 for p in preds if p.strip() and not p.strip().endswith(TERMINAL))
    return dict(
        arm=name, rows=len(preds),
        repeat_sentence_pct=round(100 * rep_sent / n, 2),
        repeat_5gram_mean=round(sum(rep5) / n, 4),
        repeat_5gram_max=round(max(rep5) if rep5 else 0, 4),
        tautology_pct=round(100 * sum(tautology(p) for p in preds) / n, 2),
        truncated_pct=round(100 * trunc / n, 2),
        latin_frac_mean=round(sum(latin) / n, 4),
        empty_pct=round(100 * sum(1 for p in preds if not p.strip()) / n, 2),
        very_short_pct=round(100 * sum(1 for L in lens if L < 30) / n, 2),
        len_p05=q(0.05), len_p50=q(0.50), len_p95=q(0.95),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records", nargs="+", help="dev.json / test.json with predictions")
    ap.add_argument("--sample", type=int, default=100,
                    help="worst-offender rows to dump per arm for manual review")
    ap.add_argument("--out", default="audit.json")
    a = ap.parse_args()

    results, worst = [], {}
    for f in a.records:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        preds = d.get("predictions")
        if not preds:
            print(f"⏭  {f}: no predictions (decoded before 04_decode.py saved them)")
            continue
        name = f"{Path(f).parent.parent.name.split('_')[0]}/{Path(f).parent.name}"
        r = audit(preds, name)
        results.append(r)
        scored = sorted(((max_ngram_repeat(tokenize(p)), i, p)
                         for i, p in enumerate(preds)), reverse=True)
        worst[name] = [{"row": i, "repeat_5gram": round(s, 3), "text": p[:400]}
                       for s, i, p in scored[: a.sample] if s > 0]

    keys = ["arm", "rows", "repeat_sentence_pct", "repeat_5gram_mean", "tautology_pct",
            "truncated_pct", "latin_frac_mean", "very_short_pct",
            "len_p05", "len_p50", "len_p95"]
    print("| " + " | ".join(keys) + " |")
    print("|" + "---|" * len(keys))
    for r in sorted(results, key=lambda r: -r["repeat_sentence_pct"]):
        print("| " + " | ".join(str(r[k]) for k in keys) + " |")
    print("\nreferences: ~100 tokens. 🔴 clinical correctness / contradiction / unsafe "
          "advice are NOT measured here — they need a medical judge.")

    Path(a.out).write_text(json.dumps({"summary": results, "worst_rows": worst},
                                      ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {a.out}  (worst {a.sample} rows per arm, for manual review)")


if __name__ == "__main__":
    raise SystemExit(main())
