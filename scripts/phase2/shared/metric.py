"""
metric.py — exact local reimplementation of the Phase 1 composite metric.

    Phase 1 Score = 0.5 * BERTScore_F1 + 0.3 * TokenF1 + 0.2 * ROUGE-L_F1

Scored per example against the reference doctor response, then averaged.

⚠️ THREE THINGS THE ORGANIZERS HAVE NOT DISCLOSED
   Each is exposed as a parameter here rather than silently assumed:

   1. TOKENIZER. The Kaggle formulas use set/LCS notation over "tokens" without
      defining them. Default here strips punctuation and digits, then splits on
      whitespace (TOKENIZER="punct"). Use TOKENIZER="whitespace" for a plain split.

   2. TOKEN F1 MULTISET vs SET. Kaggle writes |tokens(y_hat) & tokens(y)| in set
      notation, but every standard implementation (SQuAD, HF) uses multiset
      (Counter) intersection. Default is multiset; pass multiset=False to compare.

   3. BERTSCORE MODEL, LAYER, AND RESCALING. Default is
      bert-base-multilingual-cased layer 9 (the bert_score library default for
      that model), idf=False, rescale_with_baseline=False.
      If rescaling turns out to be on, pass baseline=<float> to rescale:
          rescaled = (score - baseline) / (1 - baseline)

   Measured on this corpus, unrescaled BERTScore sits in a ~0.68-0.70 band for
   ANY fluent in-domain text, so it barely discriminates. See PLAN.md section 0.

Usage
-----
    from metric import compute_metrics, token_f1, rouge_l_f1

    res = compute_metrics(preds, refs)                 # dict of means + per-example
    res = compute_metrics(preds, refs, bertscore=False)  # fast lexical-only

    # CLI
    python metric.py --pred submission.csv --ref dev.parquet
    python metric.py --selftest
"""

from __future__ import annotations

import re
import sys
import unicodedata
from collections import Counter
from typing import Iterable, Optional, Sequence

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

WEIGHTS = {"bertscore": 0.5, "token_f1": 0.3, "rouge_l": 0.2}

DEFAULT_BERT_MODEL = "bert-base-multilingual-cased"
DEFAULT_BERT_LAYER = 9

_PUNCT = re.compile(r"[।,\.\?\!;:\(\)\[\]\{\}\"'`\-—–/\\|~@#\$%\^&\*\+=<>০-৯0-9]")
_WS = re.compile(r"\s+")


# --------------------------------------------------------------------------
# tokenization
# --------------------------------------------------------------------------
def normalize_text(s: str) -> str:
    """NFC-normalize and collapse whitespace. Does not strip punctuation."""
    return _WS.sub(" ", unicodedata.normalize("NFC", str(s))).strip()


def tokenize(s: str, mode: str = "punct") -> list[str]:
    """
    mode="punct"      strip punctuation/digits, then split on whitespace (default)
    mode="whitespace" plain .split() after NFC normalization
    """
    s = unicodedata.normalize("NFC", str(s))
    if mode == "whitespace":
        return s.split()
    if mode == "punct":
        return _PUNCT.sub(" ", s).split()
    raise ValueError(f"unknown tokenize mode: {mode!r}")


# --------------------------------------------------------------------------
# Token-level F1
# --------------------------------------------------------------------------
def token_f1(pred, ref, mode: str = "punct", multiset: bool = True) -> float:
    """
    Bag-of-tokens F1.

        P = |tokens(pred) & tokens(ref)| / |tokens(pred)|
        R = |tokens(pred) & tokens(ref)| / |tokens(ref)|
        F1 = 2PR / (P + R)

    multiset=True  -> Counter intersection (SQuAD convention, the default)
    multiset=False -> set intersection (literal reading of the Kaggle formula)
    """
    p = tokenize(pred, mode) if isinstance(pred, str) else list(pred)
    r = tokenize(ref, mode) if isinstance(ref, str) else list(ref)
    if not p or not r:
        return 0.0

    if multiset:
        overlap = sum((Counter(p) & Counter(r)).values())
        n_p, n_r = len(p), len(r)
    else:
        sp, sr = set(p), set(r)
        overlap = len(sp & sr)
        n_p, n_r = len(sp), len(sr)

    if overlap == 0:
        return 0.0
    prec, rec = overlap / n_p, overlap / n_r
    return 2 * prec * rec / (prec + rec)


# --------------------------------------------------------------------------
# ROUGE-L F1
# --------------------------------------------------------------------------
def _lcs_len(a_ids: np.ndarray, b_ids: np.ndarray) -> int:
    """
    LCS length via row-wise DP, vectorized over the inner loop.

    Pure-Python LCS is far too slow for thousands of ~100-token pairs; this keeps
    the O(la*lb) work inside numpy. Iterates over the shorter sequence.
    """
    la, lb = len(a_ids), len(b_ids)
    if la == 0 or lb == 0:
        return 0
    if la > lb:
        a_ids, b_ids = b_ids, a_ids
        la, lb = lb, la

    prev = np.zeros(lb + 1, dtype=np.int32)
    cur = np.zeros(lb + 1, dtype=np.int32)
    for i in range(la):
        # cur[j+1] = max(prev[j] + 1 if a[i]==b[j] else 0, prev[j+1], cur[j])
        cand = np.where(b_ids == a_ids[i], prev[:-1] + 1, 0)
        np.maximum(cand, prev[1:], out=cur[1:])
        cur[0] = 0
        np.maximum.accumulate(cur, out=cur)  # folds in the cur[j] dependency
        prev, cur = cur, prev
    return int(prev[lb])


def rouge_l_f1(pred, ref, mode: str = "punct", beta: float = 1.0) -> float:
    """
    LCS-based F-measure with beta = 1 (precision and recall weighted equally).

        R_lcs = LCS / |ref|,  P_lcs = LCS / |pred|
        F = (1 + b^2) * R * P / (R + b^2 * P)
    """
    p = tokenize(pred, mode) if isinstance(pred, str) else list(pred)
    r = tokenize(ref, mode) if isinstance(ref, str) else list(ref)
    if not p or not r:
        return 0.0

    vocab: dict[str, int] = {}
    pa = np.fromiter((vocab.setdefault(t, len(vocab)) for t in p), dtype=np.int32, count=len(p))
    ra = np.fromiter((vocab.setdefault(t, len(vocab)) for t in r), dtype=np.int32, count=len(r))

    lcs = _lcs_len(pa, ra)
    if lcs == 0:
        return 0.0
    prec, rec = lcs / len(p), lcs / len(r)
    b2 = beta * beta
    return (1 + b2) * rec * prec / (rec + b2 * prec)


# --------------------------------------------------------------------------
# BERTScore
# --------------------------------------------------------------------------
class BERTScorer:
    """
    Greedy-matching BERTScore F1 over contextual embeddings.

    Loads the model lazily so importing metric.py stays cheap for lexical-only work.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_BERT_MODEL,
        layer: int = DEFAULT_BERT_LAYER,
        device: Optional[str] = None,
        max_length: int = 512,
        batch_size: int = 32,
        fp16: bool = True,
        baseline: Optional[float] = None,
    ):
        self.model_name = model_name
        self.layer = layer
        self.max_length = max_length
        self.batch_size = batch_size
        self.fp16 = fp16
        self.baseline = baseline
        self._device = device
        self._tok = None
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        import torch
        from transformers import AutoModel, AutoTokenizer

        self._device = self._device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._tok = AutoTokenizer.from_pretrained(self.model_name)
        m = AutoModel.from_pretrained(self.model_name).eval().to(self._device)
        if self.fp16 and self._device == "cuda":
            m = m.half()
        self._model = m

    def _embed(self, texts: Sequence[str]) -> list:
        import torch

        self._load()
        out = []
        for i in range(0, len(texts), self.batch_size):
            batch = [normalize_text(t) or "." for t in texts[i : i + self.batch_size]]
            enc = self._tok(
                batch, return_tensors="pt", padding=True,
                truncation=True, max_length=self.max_length,
            ).to(self._device)
            with torch.no_grad():
                hs = self._model(**enc, output_hidden_states=True).hidden_states[self.layer]
            hs = torch.nn.functional.normalize(hs.float(), dim=-1)
            for j in range(len(batch)):
                mask = enc["attention_mask"][j].bool()
                out.append(hs[j][mask][1:-1].cpu())  # drop [CLS] / [SEP]
        return out

    def score(self, preds: Sequence[str], refs: Sequence[str]) -> np.ndarray:
        import torch

        E_p, E_r = self._embed(list(preds)), self._embed(list(refs))
        scores = np.zeros(len(E_p), dtype=np.float64)
        for i, (p, r) in enumerate(zip(E_p, E_r)):
            if len(p) == 0 or len(r) == 0:
                continue
            sim = p @ r.T
            prec = sim.max(dim=1).values.mean().item()
            rec = sim.max(dim=0).values.mean().item()
            scores[i] = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
        if self.baseline is not None:
            scores = (scores - self.baseline) / (1.0 - self.baseline)
        return scores


_DEFAULT_SCORER: Optional[BERTScorer] = None


def get_scorer(**kw) -> BERTScorer:
    """Process-wide cached scorer so the model loads once."""
    global _DEFAULT_SCORER
    if _DEFAULT_SCORER is None or kw:
        _DEFAULT_SCORER = BERTScorer(**kw)
    return _DEFAULT_SCORER


# --------------------------------------------------------------------------
# composite
# --------------------------------------------------------------------------
def compute_metrics(
    preds: Iterable[str],
    refs: Iterable[str],
    bertscore: bool = True,
    mode: str = "punct",
    multiset: bool = True,
    scorer: Optional[BERTScorer] = None,
    verbose: bool = False,
    **scorer_kw,
) -> dict:
    """
    Returns means plus per-example arrays.

    Always inspect the three components separately — watching only the composite
    hides which lever actually moved.

    bertscore=False computes the lexical half only. The returned "composite" is
    then partial (0.3*TokenF1 + 0.2*ROUGE-L, max 0.5) and is labelled as such by
    "bertscore_included": False.
    """
    preds, refs = [str(p) for p in preds], [str(r) for r in refs]
    if len(preds) != len(refs):
        raise ValueError(f"length mismatch: {len(preds)} preds vs {len(refs)} refs")
    n = len(preds)

    p_toks = [tokenize(p, mode) for p in preds]
    r_toks = [tokenize(r, mode) for r in refs]

    f1 = np.array([token_f1(p, r, mode, multiset) for p, r in zip(p_toks, r_toks)])
    rl = np.array([rouge_l_f1(p, r, mode) for p, r in zip(p_toks, r_toks)])

    if bertscore:
        sc = scorer or get_scorer(**scorer_kw)
        bs = sc.score(preds, refs)
    else:
        bs = np.zeros(n)

    composite = WEIGHTS["bertscore"] * bs + WEIGHTS["token_f1"] * f1 + WEIGHTS["rouge_l"] * rl

    res = {
        "n": n,
        "bertscore_included": bool(bertscore),
        "token_f1": float(f1.mean()),
        "rouge_l": float(rl.mean()),
        "bertscore": float(bs.mean()) if bertscore else None,
        "composite": float(composite.mean()),
        "mean_pred_tokens": float(np.mean([len(t) for t in p_toks])),
        "mean_ref_tokens": float(np.mean([len(t) for t in r_toks])),
        "per_example": {"token_f1": f1, "rouge_l": rl, "bertscore": bs, "composite": composite},
    }
    if verbose:
        print(format_report(res))
    return res


def format_report(res: dict) -> str:
    bs = "n/a (skipped)" if res["bertscore"] is None else f"{res['bertscore']:.4f}"
    tag = "" if res["bertscore_included"] else "   ⚠️ PARTIAL — lexical only, max 0.5"
    return (
        f"n = {res['n']}\n"
        f"  BERTScore F1  {bs}   (weight 0.5)\n"
        f"  Token F1      {res['token_f1']:.4f}   (weight 0.3)\n"
        f"  ROUGE-L F1    {res['rouge_l']:.4f}   (weight 0.2)\n"
        f"  COMPOSITE     {res['composite']:.4f}{tag}\n"
        f"  mean tokens   pred {res['mean_pred_tokens']:.1f} vs ref {res['mean_ref_tokens']:.1f}"
    )


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------
def _selftest() -> int:
    ok = True

    def check(name, got, want, tol=1e-9):
        nonlocal ok
        good = abs(got - want) <= tol
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: got {got:.6f}, want {want:.6f}")

    print("token_f1")
    check("identical", token_f1("a b c", "a b c"), 1.0)
    check("disjoint", token_f1("a b c", "x y z"), 0.0)
    check("half overlap", token_f1("a b", "a c"), 0.5)
    check("multiset counts repeats", token_f1("a a b", "a b"), 2 * (2 / 3) * (2 / 2) / ((2 / 3) + 1))
    check("set mode ignores repeats", token_f1("a a b", "a b", multiset=False), 1.0)

    print("rouge_l_f1")
    check("identical", rouge_l_f1("a b c", "a b c"), 1.0)
    check("disjoint", rouge_l_f1("a b c", "x y z"), 0.0)
    # LCS("a b c d", "a c d") = "a c d" = 3 -> P=3/4, R=3/3
    check("subsequence", rouge_l_f1("a b c d", "a c d"), 2 * 0.75 * 1.0 / 1.75)
    # order matters for LCS but not for token F1
    check("order-sensitive", rouge_l_f1("a b", "b a"), 2 * 0.5 * 0.5 / 1.0)
    check("token_f1 order-insensitive", token_f1("a b", "b a"), 1.0)

    print("LCS vs brute force (random)")
    import random
    rng = random.Random(0)
    def brute(a, b):
        m = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                m[i + 1][j + 1] = m[i][j] + 1 if x == y else max(m[i][j + 1], m[i + 1][j])
        return m[len(a)][len(b)]
    mismatches = 0
    for _ in range(200):
        a = [rng.choice("abcde") for _ in range(rng.randint(0, 25))]
        b = [rng.choice("abcde") for _ in range(rng.randint(0, 25))]
        va = np.array([ord(c) for c in a], dtype=np.int32)
        vb = np.array([ord(c) for c in b], dtype=np.int32)
        if _lcs_len(va, vb) != brute(a, b):
            mismatches += 1
    ok &= mismatches == 0
    print(f"  [{'PASS' if mismatches == 0 else 'FAIL'}] 200 random pairs, {mismatches} mismatches")

    print("bengali tokenization")
    t = tokenize("হেলো, নাসেনিয়া ডকে আপনাকে স্বাগতম। সিএ ১২৫ (CA 125) স্বাভাবিক।")
    print(f"  tokens: {t}")
    ok &= "হেলো" in t and "CA" in t
    print(f"  [{'PASS' if 'হেলো' in t and 'CA' in t else 'FAIL'}] keeps Bengali + parenthesized English")

    print("composite weighting")
    r = compute_metrics(["a b c"], ["a b c"], bertscore=False)
    check("perfect lexical -> 0.5 partial", r["composite"], 0.5)

    print("\n" + ("ALL PASS" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def _read_any(path: str):
    import pandas as pd
    return pd.read_parquet(path) if str(path).endswith(".parquet") else pd.read_csv(path)


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Phase 1 composite metric")
    ap.add_argument("--pred", help="csv/parquet with id + prediction column")
    ap.add_argument("--ref", help="csv/parquet with id + reference column")
    ap.add_argument("--pred-col", default="output")
    ap.add_argument("--ref-col", default="output")
    ap.add_argument("--id-col", default="id")
    ap.add_argument("--no-bertscore", action="store_true", help="lexical only (fast)")
    ap.add_argument("--bert-model", default=DEFAULT_BERT_MODEL)
    ap.add_argument("--bert-layer", type=int, default=DEFAULT_BERT_LAYER)
    ap.add_argument("--baseline", type=float, default=None,
                    help="rescale_with_baseline constant, if organizers use one")
    ap.add_argument("--tokenize", default="punct", choices=["punct", "whitespace"])
    ap.add_argument("--set-f1", action="store_true", help="set instead of multiset intersection")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()
    if not a.pred or not a.ref:
        ap.error("--pred and --ref are required (or use --selftest)")

    dp, dr = _read_any(a.pred), _read_any(a.ref)
    if a.id_col in dp.columns and a.id_col in dr.columns:
        merged = dr[[a.id_col, a.ref_col]].merge(
            dp[[a.id_col, a.pred_col]], on=a.id_col, how="left", suffixes=("_ref", "_pred")
        )
        rc = a.ref_col + "_ref" if a.ref_col == a.pred_col else a.ref_col
        pc = a.pred_col + "_pred" if a.ref_col == a.pred_col else a.pred_col
        missing = merged[pc].isna().sum()
        if missing:
            print(f"⚠️  {missing} reference ids have no prediction; scoring them as empty")
        refs, preds = merged[rc].fillna(""), merged[pc].fillna("")
    else:
        print("⚠️  no shared id column; aligning by row order")
        refs, preds = dr[a.ref_col].fillna(""), dp[a.pred_col].fillna("")

    res = compute_metrics(
        preds, refs,
        bertscore=not a.no_bertscore,
        mode=a.tokenize,
        multiset=not a.set_f1,
        model_name=a.bert_model, layer=a.bert_layer, baseline=a.baseline,
    )
    print(format_report(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
