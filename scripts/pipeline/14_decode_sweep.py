"""14_decode_sweep.py — E15. Sweep decoder settings on a trained checkpoint.

    python 14_decode_sweep.py --ckpt ../E05_train_to_convergence/english_draft/best \\
        --data-dir ../data/english_draft --out ../E15_decode_sweep/sweep.json

`04_decode.py --sweep` covers length_penalty x min_new_tokens only, on fixed grids, and
reloads the model for every call. This does E15's actual grid — **num_beams x
length_penalty x min_new_tokens** — with the model loaded once.

🔴 Two guards E15 asks for by name:

  * **A second, DISJOINT dev subset.** "A 3-way sweep over 300 rows will find spurious
    winners." Every config is scored on rows [0:300] — the same subset every arm in the
    program trained against — and the top candidates are then re-scored on rows
    [300:600], which no config was selected on. The re-verified number is the one to
    believe; a winner that does not survive it was noise.
  * **Judge on Token F1 / ROUGE-L**, never the local composite.

No training. Cheap: the whole grid is one model load and 48 decodes of 300 rows.
"""

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from metric import token_f1, rouge_l_f1, tokenize  # noqa: E402

# 04_decode.py starts with a digit, so it cannot be imported by name.
_spec = importlib.util.spec_from_file_location("decode_mod", HERE / "04_decode.py")
_dec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dec)

NOISE = 0.0044


def score(preds, refs):
    f1 = sum(token_f1(p, r) for p, r in zip(preds, refs)) / len(refs)
    rl = sum(rouge_l_f1(p, r) for p, r in zip(preds, refs)) / len(refs)
    tl = sum(len(tokenize(p)) for p in preds) / len(preds)
    return f1, rl, tl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--max-source-len", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--subset", type=int, default=300)
    ap.add_argument("--beams", default="4,8,12")
    ap.add_argument("--length-penalties", default="0.6,0.8,1.0,1.2")
    ap.add_argument("--min-new", default="0,40,60,80")
    # Sweep 1 held this at 320. Its winners all sat at min_new 0 — the grid
    # BOUNDARY — so the length knobs were never actually explored past the edge.
    ap.add_argument("--max-new", default="320")
    ap.add_argument("--verify-top", type=int, default=3)
    ap.add_argument("--out", default="sweep.json")
    a = ap.parse_args()

    max_src = a.max_source_len
    if max_src is None:
        rj = Path(a.ckpt).parent / "run.json"
        max_src = json.loads(rj.read_text())["max_source_len"] if rj.is_file() else 384
    print(f"max_source_len {max_src}")

    proc = Path(a.data_dir)
    dev = pd.read_parquet(proc / "dev.parquet")
    norm = _dec.get_normalizer(True)
    # A = the selection subset (what every arm was scored on).
    # B = disjoint verification rows, never used to pick anything.
    A = dev.iloc[: a.subset]
    B = dev.iloc[a.subset: 2 * a.subset]
    inA = [norm(s) for s in A["input"]]
    inB = [norm(s) for s in B["input"]]
    refA, refB = A["output"].tolist(), B["output"].tolist()
    print(f"selection rows [0:{a.subset}]  ·  verification rows "
          f"[{a.subset}:{a.subset*2}] (disjoint)")

    dec = _dec.Decoder([a.ckpt])
    beams = [int(x) for x in a.beams.split(",")]
    lps = [float(x) for x in a.length_penalties.split(",")]
    mins = [int(x) for x in a.min_new.split(",")]
    maxs = [int(x) for x in a.max_new.split(",")]

    rows, t0 = [], time.time()
    print(f"\n| beams | lp | min_new | max_new | Token F1 | ROUGE-L | lexical | tokens |")
    print("|" + "---|" * 8)
    for nb in beams:
      for lp in lps:
        for mn in mins:
            for mx in maxs:
                preds, _, _ = _dec.run(dec, inA, mode="beam", n=1,
                                       utility="combined", num_beams=nb,
                                       length_penalty=lp, min_new_tokens=mn,
                                       max_new_tokens=mx, batch_size=a.batch_size,
                                       max_source_len=max_src)
                f1, rl, tl = score(preds, refA)
                rows.append(dict(num_beams=nb, length_penalty=lp, min_new_tokens=mn,
                                 max_new_tokens=mx, token_f1=f1, rouge_l=rl,
                                 lexical=0.3 * f1 + 0.2 * rl, mean_tokens=tl))
                print(f"| {nb} | {lp} | {mn} | {mx} | {f1:.4f} | {rl:.4f} | "
                      f"{0.3*f1+0.2*rl:.4f} | {tl:.1f} |", flush=True)

    rows.sort(key=lambda r: -r["lexical"])
    print(f"\nswept {len(rows)} configs in {(time.time()-t0)/60:.1f} min")

    # ---- re-verify the top candidates on the disjoint subset --------------------
    print(f"\n🔴 re-verifying the top {a.verify_top} on rows "
          f"[{a.subset}:{a.subset*2}] — a 48-way sweep over 300 rows finds "
          f"spurious winners\n")
    print("| rank | beams | lp | min_new | F1 (selection) | **F1 (verify)** | Δ |")
    print("|" + "---|" * 7)
    for i, r in enumerate(rows[: a.verify_top]):
        preds, _, _ = _dec.run(dec, inB, mode="beam", n=1, utility="combined",
                               num_beams=r["num_beams"],
                               length_penalty=r["length_penalty"],
                               min_new_tokens=r["min_new_tokens"],
                               max_new_tokens=r.get("max_new_tokens", 320),
                               batch_size=a.batch_size,
                               max_source_len=max_src)
        f1b, rlb, _ = score(preds, refB)
        r["verify_token_f1"], r["verify_rouge_l"] = f1b, rlb
        print(f"| {i+1} | {r['num_beams']} | {r['length_penalty']} | "
              f"{r['min_new_tokens']} | {r['token_f1']:.4f} | **{f1b:.4f}** | "
              f"{f1b - r['token_f1']:+.4f} |", flush=True)

    # The shipped decoder, for reference: beam 4 / min_new 80 / lp 1.0
    base = next((r for r in rows if r["num_beams"] == 8 and r["length_penalty"] == 1.2
                 and r["min_new_tokens"] == 0), None)
    best = max(rows[: a.verify_top], key=lambda r: r.get("verify_token_f1", -1))
    if base:
        gain = best["token_f1"] - base["token_f1"]
        print(f"\ncurrent shipped decoder (beam 8 / lp 1.2 / min_new 0): "
              f"{base['token_f1']:.4f}")
        print(f"best swept config: {best['token_f1']:.4f}  (Δ {gain:+.4f})")
        print("✅ worth changing the decoder" if gain > NOISE else
              "➖ inside the 0.0044 noise floor — keep the shipped decoder")
    Path(a.out).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    raise SystemExit(main())
