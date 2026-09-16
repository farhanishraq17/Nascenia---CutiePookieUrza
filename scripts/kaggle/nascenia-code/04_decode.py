"""
04_decode.py — decoding strategies, MBR selection, and submission generation.

This is where the competition is won. See PLAN.md sections 0.25-0.27 and 6.

WHY MBR
    Beam search maximizes sequence probability. The leaderboard scores lexical overlap
    with one reference. Those are different objectives, and the gap between them is
    free score.

    Minimum Bayes Risk decoding optimizes the actual metric: sample N candidates, then
    pick the one with the highest expected utility against the others. The other
    samples stand in for the unknown reference, so the winner is whichever candidate
    sits closest to the centre of the model's own output distribution.

    It fits this corpus unusually well. Responses share heavy boilerplate, so candidates
    agree on scaffolding and disagree on specifics; MBR keeps the agreed scaffolding and
    picks the least-risky specifics. Measured evidence that this is the right instinct:
    generic beat specific by 0.454 vs 0.431 in the retrieval baseline.

UTILITY FUNCTION
    utility(c) = mean over other candidates c' of  [0.3*TokenF1(c,c') + 0.2*ROUGE-L(c,c')]

    BERTScore is deliberately EXCLUDED, for two reasons:
      1. It is nearly flat across fluent in-domain text (0.0008-0.042 spread across
         every model/layer tested), so it adds ~nothing to candidate ranking.
      2. It is ~100x more expensive than the lexical metrics.
    The one thing BERTScore does punish is degeneracy (CONST-OPT-01: -0.024 for word
    salad) — but every MBR candidate is model-generated and therefore fluent, so that
    failure mode cannot arise here.

USAGE
    # score a checkpoint on the frozen dev split
    python 04_decode.py --ckpt ../RUNS/banglat5_seed42/best --split dev --mode beam
    python 04_decode.py --ckpt ../RUNS/banglat5_seed42/best --split dev --mode mbr -n 24

    # sweep decoding hyperparameters on dev
    python 04_decode.py --ckpt ../RUNS/banglat5_seed42/best --split dev --sweep

    # pooled MBR across independently-seeded checkpoints (asserts the 3B cap)
    python 04_decode.py --ckpt A/best --ckpt B/best --ckpt C/best --split dev --mode mbr

    # produce a submission
    python 04_decode.py --ckpt ../RUNS/banglat5_seed42/best --split test \
        --mode mbr -n 24 --out ../submission.csv

Every run writes a JSON record with seeds, decoding config and checkpoint hashes —
Phase 2 requires reproducing leaderboard outputs exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from metric import tokenize, token_f1, rouge_l_f1, compute_metrics, format_report  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "DATA" / "PROCESSED"

W_F1, W_RL = 0.3, 0.2   # metric weights, used as the MBR utility


# ---------------------------------------------------------------- helpers
def get_normalizer(enabled: bool = True):
    """Must match 02_train_t5.py exactly — inputs are normalized at training time."""
    if not enabled:
        return lambda s: str(s)
    try:
        from normalizer import normalize  # type: ignore
        return lambda s: normalize(str(s))
    except ImportError:
        print("⚠️  csebuetnlp `normalizer` missing — inputs will NOT match training "
              "preprocessing. pip install git+https://github.com/csebuetnlp/normalizer",
              file=sys.stderr)
        return lambda s: str(s)


def ckpt_hash(path: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(Path(path).rglob("*")):
        if f.is_file() and f.suffix in {".bin", ".safetensors", ".json", ".model"}:
            h.update(f.name.encode())
            h.update(str(f.stat().st_size).encode())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- MBR
def mbr_select(cands: list[str], utility: str = "combined") -> tuple[int, np.ndarray]:
    """
    Return (index of the MBR-optimal candidate, utility vector).

    Pairwise utilities are symmetric, so only the upper triangle is computed —
    halving the O(N^2) cost.
    """
    n = len(cands)
    if n == 1:
        return 0, np.array([0.0])

    toks = [tokenize(c) for c in cands]
    cnts = [Counter(t) for t in toks]
    U = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(i + 1, n):
            # inline multiset F1 using precomputed Counters: 2*overlap/(|a|+|b|)
            ov = sum((cnts[i] & cnts[j]).values())
            li, lj = len(toks[i]), len(toks[j])
            f1 = 0.0 if (ov == 0 or li == 0 or lj == 0) else 2 * ov / (li + lj)
            if utility == "f1":
                u = W_F1 * f1
            else:
                u = W_F1 * f1 + W_RL * rouge_l_f1(toks[i], toks[j])
            U[i, j] = U[j, i] = u

    util = U.sum(axis=1) / max(n - 1, 1)
    return int(util.argmax()), util


# ---------------------------------------------------------------- generation
class Decoder:
    def __init__(self, ckpts: list[str], device: str | None = None, fp16: bool = False):
        """fp16 defaults to FALSE and should stay that way on a T4.

        T5 overflows to NaN in fp16 — the activations exceed fp16 range, which is why every
        training run here is fp32. Loading with .half() silently produced NaN logits and
        garbage generations that still "looked" like a working run: arm C emitted 1 token
        per row (NaN -> immediate EOS, Token F1 0.0002) and arm F emitted 227 tokens of
        noise (0.0267), against 0.2576 and 0.2444 measured in fp32 during training.

        bf16 would be safe, but only on Ampere+ (sm_80). A T4 is sm_75, so fp32 it is.
        """
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if fp16 and self.device == "cuda":
            cap = torch.cuda.get_device_capability(0)
            print(f"  ⚠️  fp16 requested on sm_{cap[0]}{cap[1]} — T5 is known to produce NaN "
                  f"in fp16. Expect garbage output; use fp32 unless you have verified this.")
        # ONE TOKENIZER PER CHECKPOINT. Using ckpts[0]'s tokenizer for every model is
        # only safe when all checkpoints share a vocabulary. Pooling across
        # architectures (BanglaT5 + mT5) with a single tokenizer silently produces
        # garbage: different SentencePiece vocabs map the same id to different pieces.
        self.toks, self.models, total = [], [], 0
        for c in ckpts:
            self.toks.append(AutoTokenizer.from_pretrained(c))
            m = AutoModelForSeq2SeqLM.from_pretrained(c).eval().to(self.device)
            if fp16 and self.device == "cuda":
                m = m.half()
            n = sum(p.numel() for p in m.parameters())
            total += n
            dt = next(m.parameters()).dtype
            print(f"  loaded {c}  ({n/1e6:.1f}M params, {dt}, hash {ckpt_hash(Path(c))})")

            # Fail here, not after a 4-minute decode. An fp16 T5 returns NaN logits and
            # still generates happily — the run looks healthy and the output is worthless.
            with torch.no_grad():
                probe = self.toks[-1]("হেলো", return_tensors="pt").to(self.device)
                logits = m(**probe, decoder_input_ids=torch.zeros(
                    (1, 1), dtype=torch.long, device=self.device)).logits
            assert torch.isfinite(logits).all(), (
                f"❌ NON-FINITE LOGITS from {c} in {dt}. T5 overflows to NaN in fp16 — "
                f"load in fp32 (the default) rather than passing fp16=True.")
            self.models.append(m)

        vocabs = {t.vocab_size for t in self.toks}
        if len(vocabs) > 1:
            print(f"  note: heterogeneous tokenizers {sorted(vocabs)} — each model "
                  f"generates with its own, candidates pooled as decoded STRINGS")
        self.tok = self.toks[0]   # kept for submission-side decoding only

        self.total_params = total
        print(f"\nTOTAL INFERENCE PARAMETERS: {total:,} ({total/1e9:.3f}B)")
        assert total <= 3_000_000_000, (
            f"❌ 3B PARAMETER CAP BREACHED: {total:,}. This entry would be disqualified.")
        print(f"✅ within the 3B cap  (headroom {(3_000_000_000-total)/1e6:.0f}M)\n")

    @property
    def n_models(self):
        return len(self.models)

    def generate(self, texts, model_idx=0, *, mode="beam", n=1, num_beams=4,
                 temperature=0.8, top_p=0.95, min_new_tokens=80, max_new_tokens=256,
                 length_penalty=1.0, batch_size=16, seed=42, max_source_len=384):
        """Returns list[list[str]] — n candidates per input."""
        torch = self.torch
        model = self.models[model_idx]
        tok = self.toks[model_idx]          # this model's OWN tokenizer
        out: list[list[str]] = []
        torch.manual_seed(seed)

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tok(batch, return_tensors="pt", padding=True,
                      truncation=True, max_length=max_source_len).to(self.device)
            kw = dict(min_new_tokens=min_new_tokens, max_new_tokens=max_new_tokens)
            if mode == "greedy":
                kw.update(do_sample=False, num_beams=1, num_return_sequences=1)
            elif mode == "beam":
                kw.update(do_sample=False, num_beams=num_beams,
                          length_penalty=length_penalty, num_return_sequences=1)
            else:  # sample -> MBR
                kw.update(do_sample=True, top_p=top_p, temperature=temperature,
                          num_return_sequences=n)
            with torch.no_grad():
                g = model.generate(**enc, **kw)
            dec = tok.batch_decode(g, skip_special_tokens=True)
            k = n if mode == "sample" else 1
            for j in range(len(batch)):
                out.append(dec[j * k:(j + 1) * k])
        return out


# ---------------------------------------------------------------- pipeline
def run(dec: Decoder, inputs, *, mode, n, utility, **gen_kw):
    """Returns (final predictions, mean #candidates, seconds)."""
    t0 = time.time()
    if mode in ("greedy", "beam"):
        cands = dec.generate(inputs, mode=mode, **gen_kw)
        preds = [c[0] for c in cands]
        ncand = 1
    else:
        # pooled MBR: draw candidates from every checkpoint, then select over the union
        per_model = max(1, n // dec.n_models)
        pooled: list[list[str]] = [[] for _ in inputs]
        for mi in range(dec.n_models):
            got = dec.generate(inputs, model_idx=mi, mode="sample", n=per_model,
                               seed=gen_kw.get("seed", 42) + mi * 1000, **{
                                   k: v for k, v in gen_kw.items() if k != "seed"})
            for i, c in enumerate(got):
                pooled[i].extend(c)
        preds = [p[mbr_select(p, utility)[0]] for p in pooled]
        ncand = float(np.mean([len(p) for p in pooled]))
    return preds, ncand, time.time() - t0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="decode / MBR / submit")
    ap.add_argument("--ckpt", action="append", required=True,
                    help="checkpoint dir; repeat for a pooled ensemble")
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--mode", default="beam", choices=["greedy", "beam", "mbr"])
    ap.add_argument("-n", "--num-candidates", type=int, default=24)
    ap.add_argument("--utility", default="combined", choices=["combined", "f1"],
                    help="combined = 0.3*TokenF1 + 0.2*ROUGE-L (matches the metric)")
    ap.add_argument("--num-beams", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--min-new-tokens", type=int, default=80)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--length-penalty", type=float, default=1.0)
    ap.add_argument("--max-source-len", type=int, default=384)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--limit", type=int, default=None, help="subsample rows (fast iteration)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-normalizer", action="store_true")
    ap.add_argument("--no-bertscore", action="store_true")
    ap.add_argument("--sweep", action="store_true", help="beam length_penalty x min_new_tokens")
    ap.add_argument("--out", default=None, help="write submission.csv (test split)")
    ap.add_argument("--record", default=None, help="write a JSON run record")
    # PROC is derived from this file's location (NOTEBOOKS/ -> ../DATA/PROCESSED), which is
    # only correct in the local repo. On Kaggle the code is copied to /kaggle/working/code/,
    # so it resolved to a non-existent /kaggle/working/DATA/PROCESSED. 02_train_t5.py always
    # had --data-dir; this one did not, so every hosted decode failed at the first read.
    ap.add_argument("--data-dir", default=None,
                    help="dir holding train/dev/test.parquet (default: ../DATA/PROCESSED)")
    a = ap.parse_args(argv)

    proc = Path(a.data_dir) if a.data_dir else PROC
    split_file = proc / f"{a.split}.parquet"
    assert split_file.is_file(), (
        f"no {split_file}\n"
        f"Run 01_prep.py first, and pass --data-dir if its --out was not {PROC}.")
    df = pd.read_parquet(split_file)
    if a.limit:
        df = df.head(a.limit)
    norm = get_normalizer(not a.no_normalizer)
    inputs = [norm(s) for s in df["input"]]
    refs = df["output"].tolist() if "output" in df.columns else None
    print(f"{a.split}: {len(df)} rows | checkpoints: {len(a.ckpt)}\n")

    dec = Decoder(a.ckpt)
    gen_kw = dict(num_beams=a.num_beams, temperature=a.temperature, top_p=a.top_p,
                  min_new_tokens=a.min_new_tokens, max_new_tokens=a.max_new_tokens,
                  length_penalty=a.length_penalty, batch_size=a.batch_size,
                  seed=a.seed, max_source_len=a.max_source_len)

    # ---------------- sweep ----------------
    if a.sweep:
        if refs is None:
            ap.error("--sweep needs the dev split (it requires references)")
        print(f"{'lp':>5} {'min_tok':>8} {'TokenF1':>9} {'ROUGE-L':>9} {'lexical':>9} {'tokens':>7}")
        best = None
        for lp in [0.6, 0.8, 1.0, 1.2, 1.5]:
            for mnt in [60, 80, 100]:
                kw = {**gen_kw, "length_penalty": lp, "min_new_tokens": mnt}
                preds, _, _ = run(dec, inputs, mode="beam", n=1, utility=a.utility, **kw)
                f1 = float(np.mean([token_f1(p, r) for p, r in zip(preds, refs)]))
                rl = float(np.mean([rouge_l_f1(p, r) for p, r in zip(preds, refs)]))
                lex = W_F1 * f1 + W_RL * rl
                tl = float(np.mean([len(tokenize(p)) for p in preds]))
                mark = ""
                if best is None or lex > best[0]:
                    best, mark = (lex, lp, mnt), "  <== best"
                print(f"{lp:5.1f} {mnt:8d} {f1:9.4f} {rl:9.4f} {lex:9.4f} {tl:7.1f}{mark}")
        print(f"\nbest: length_penalty={best[1]} min_new_tokens={best[2]} (lexical {best[0]:.4f})")
        return 0

    # ---------------- decode ----------------
    preds, ncand, secs = run(dec, inputs, mode=a.mode, n=a.num_candidates,
                             utility=a.utility, **gen_kw)
    print(f"decoded {len(preds)} rows in {secs/60:.1f} min "
          f"({ncand:.0f} candidate(s)/row, mode={a.mode})")

    record = {
        "split": a.split, "mode": a.mode, "n_candidates": a.num_candidates,
        "utility": a.utility, "checkpoints": a.ckpt,
        "checkpoint_hashes": [ckpt_hash(Path(c)) for c in a.ckpt],
        "total_params": dec.total_params, "seed": a.seed,
        "decoding": {k: v for k, v in gen_kw.items() if k != "batch_size"},
        "normalizer": not a.no_normalizer, "rows": len(df), "minutes": round(secs / 60, 1),
    }

    if refs is not None:
        res = compute_metrics(preds, refs, bertscore=not a.no_bertscore)
        print("\n" + format_report(res))
        record["dev"] = {k: res[k] for k in
                         ["token_f1", "rouge_l", "bertscore", "composite", "mean_pred_tokens"]}
        lex = W_F1 * res["token_f1"] + W_RL * res["rouge_l"]
        print(f"\n  lexical (0.3*F1 + 0.2*RL) = {lex:.4f}")
        print(f"  {'✅' if res['token_f1'] > 0.3519 else '❌'} vs CONST-OPT-01 bar "
              f"TokenF1 0.3519  ({res['token_f1']-0.3519:+.4f})")
        print(f"  {'✅' if res['token_f1'] > 0.2669 else '❌'} vs LB constant "
              f"TokenF1 0.2669  ({res['token_f1']-0.2669:+.4f})")
        print("\n  ⚠️  composite is mis-calibrated (~ -0.118); judge on Token F1 / ROUGE-L.")

    # ---------------- submission ----------------
    if a.out:
        sub = pd.DataFrame({"id": df["id"], "output": preds})
        problems = []
        if a.split == "test" and len(sub) != 1000:
            problems.append(f"expected 1000 rows, got {len(sub)}")
        if sub["id"].duplicated().any():
            problems.append("duplicate ids")
        if sub["output"].isna().any() or (sub["output"].str.strip() == "").any():
            problems.append("empty predictions")
        sub.to_csv(a.out, index=False)
        print(f"\nwrote {a.out}  shape={sub.shape}  columns={list(sub.columns)}")
        print("❌ " + "; ".join(problems) if problems else "✅ submission checks passed")

    if a.record:
        Path(a.record).write_text(json.dumps(record, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        print(f"run record: {a.record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
