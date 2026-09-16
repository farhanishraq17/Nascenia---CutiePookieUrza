"""evaluate.py — the shared scoring harness. Import from every notebook so all three models
are measured identically.

    from evaluate import score_predictions, report
    res = score_predictions(preds, refs, ref_examples=rag_ref_outputs)  # ref_examples optional
    report(res, arm="X3 finetune+rag", model="mt5-base")

Metrics are Token F1 and ROUGE-L, implemented here exactly as elsewhere in this project so the
numbers are comparable. 🔴 The local *composite* is mis-calibrated by ~0.118 and is deliberately
NOT reported -- judge on Token F1 / ROUGE-L only.
"""
from __future__ import annotations

import re
import sys
from collections import Counter

# report() prints Bengali. A Windows cp1252 console raises UnicodeEncodeError on it and the
# whole cell dies AFTER the model has already been scored -- losing the result to a print bug.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BENGALI = r"[ঀ-৿]+"
TOKEN_RE = re.compile(rf"{BENGALI}|[A-Za-z]+|\d+")

# Reference-corpus constants, measured on the competition's own training data.
REF_HELO_PCT = 76.4      # % of reference answers opening with হেলো
REF_NASENIA_PCT = 50.0   # % containing নাসেনিয়া
REF_MEAN_TOKENS = 100.0
REF_TRUNCATED_PCT = 6.8  # 🔴 the references' OWN rate -- 6.8% is correct, not a defect
NOISE_FLOOR = 0.0044


def tokenize(s) -> list[str]:
    return TOKEN_RE.findall(str(s))


def token_f1(pred, ref) -> float:
    p, r = Counter(tokenize(pred)), Counter(tokenize(ref))
    ov = sum((p & r).values())
    if not ov:
        return 0.0
    prec, rec = ov / max(1, sum(p.values())), ov / max(1, sum(r.values()))
    return 2 * prec * rec / (prec + rec)


def _lcs(a: list[str], b: list[str]) -> int:
    """Row-wise DP. Pure-Python full-matrix LCS is far too slow at this scale."""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def rouge_l(pred, ref) -> float:
    p, r = tokenize(pred), tokenize(ref)
    if not p or not r:
        return 0.0
    l = _lcs(p, r)
    if l == 0:
        return 0.0
    prec, rec = l / len(p), l / len(r)
    return 2 * prec * rec / (prec + rec)


def looks_truncated(s: str) -> bool:
    """Ends without terminal punctuation. Compare against REF_TRUNCATED_PCT, never against 0."""
    s = str(s).strip()
    return bool(s) and s[-1] not in "।?!.।"


def score_predictions(preds, refs, ref_examples=None) -> dict:
    """
    preds        : model outputs
    refs         : gold targets
    ref_examples : for RAG arms, the RETRIEVED reference answer shown to the model for each row.
                   Supplying it enables the copy-check -- the most important RAG diagnostic.
    """
    assert len(preds) == len(refs), f"{len(preds)} preds vs {len(refs)} refs"
    f1s = [token_f1(p, r) for p, r in zip(preds, refs)]
    rls = [rouge_l(p, r) for p, r in zip(preds, refs)]
    toks = [len(tokenize(p)) for p in preds]
    n = len(preds)

    out = {
        "n": n,
        "token_f1": sum(f1s) / n,
        "rouge_l": sum(rls) / n,
        "mean_pred_tokens": sum(toks) / n,
        "helo_opener_pct": 100.0 * sum(str(p).strip().startswith("হেলো") for p in preds) / n,
        "nasenia_pct": 100.0 * sum("নাসেনিয়া" in str(p) for p in preds) / n,
        "truncated_pct": 100.0 * sum(looks_truncated(p) for p in preds) / n,
        "empty_pct": 100.0 * sum(not str(p).strip() for p in preds) / n,
        "per_row_f1": f1s,
    }

    if ref_examples is not None:
        assert len(ref_examples) == n, "ref_examples must align with preds"
        copy = [token_f1(p, e) for p, e in zip(preds, ref_examples)]
        out["copy_overlap_with_reference"] = sum(copy) / n
        out["copy_margin"] = out["token_f1"] - out["copy_overlap_with_reference"]
        # copy_margin > 0  -> closer to the true answer than to the shown example: answering.
        # copy_margin < 0  -> closer to the example it was shown: COPYING, not answering.
    return out


def report(res: dict, arm: str = "", model: str = "", floor: float = 0.1454) -> str:
    """Human-readable block. Paste straight into RESULTS.md."""
    L = []
    L.append("=" * 68)
    L.append(f"{model}   arm: {arm}   (n={res['n']})")
    L.append("=" * 68)
    L.append(f"  Token F1              {res['token_f1']:.4f}")
    L.append(f"  ROUGE-L               {res['rouge_l']:.4f}")
    d = res["token_f1"] - floor
    verdict = "✅ clears" if d > NOISE_FLOOR else ("➖ inside noise" if abs(d) <= NOISE_FLOOR
                                                  else "❌ below")
    L.append(f"  vs floor {floor:.4f}      {d:+.4f}   {verdict}")
    L.append("")
    L.append("  register read-out            model     references")
    L.append(f"    mean output tokens        {res['mean_pred_tokens']:7.1f}   {REF_MEAN_TOKENS:7.1f}")
    L.append(f"    হেলো opener %             {res['helo_opener_pct']:7.1f}   {REF_HELO_PCT:7.1f}")
    L.append(f"    নাসেনিয়া %                {res['nasenia_pct']:7.1f}   {REF_NASENIA_PCT:7.1f}")
    L.append(f"    truncated %               {res['truncated_pct']:7.1f}   {REF_TRUNCATED_PCT:7.1f}"
             "   <- 6.8% is CORRECT, not a defect")
    if res["empty_pct"]:
        L.append(f"    🔴 EMPTY outputs          {res['empty_pct']:7.1f}   %")
    if "copy_overlap_with_reference" in res:
        L.append("")
        L.append("  🔴 RAG copy-check (more important than the score above)")
        L.append(f"    overlap w/ TRUE target        {res['token_f1']:.4f}")
        L.append(f"    overlap w/ SHOWN reference    {res['copy_overlap_with_reference']:.4f}")
        L.append(f"    margin                        {res['copy_margin']:+.4f}")
        L.append("    margin > 0 -> answering.  margin < 0 -> COPYING the example, not answering;")
        L.append("    a good-looking Token F1 with a negative margin is a FAILED arm.")
    L.append("=" * 68)
    s = "\n".join(L)
    print(s)
    return s


if __name__ == "__main__":
    # Self-test: identical strings must score 1.0, disjoint must score 0.0.
    assert abs(token_f1("ক খ গ", "ক খ গ") - 1.0) < 1e-9
    assert token_f1("ক খ গ", "ঘ ঙ চ") == 0.0
    assert abs(rouge_l("ক খ গ", "ক খ গ") - 1.0) < 1e-9
    assert _lcs(list("abcde"), list("ace")) == 3
    assert looks_truncated("কিছু একটা") and not looks_truncated("কিছু একটা।")
    print("✅ evaluate.py self-test passed")
