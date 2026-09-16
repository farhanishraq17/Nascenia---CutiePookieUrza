"""17_model_soup.py — average the WEIGHTS of several checkpoints into one model.

    python 17_model_soup.py --out soup/ ../E19_multiseed_ensemble/seed*/best

Why this is not the ensembling that just failed. Output ensembling (MBR) picks among
finished generations and was measured dead here twice: −0.0027 on two seeds, and +0.0015
on a six-member pool spanning architectures. A soup instead averages parameters and ships
**one** model — so it costs nothing at inference, stays trivially inside the 3B cap, and
does not need a selector at all. It works when members sit in the same loss basin, which
independent seeds of one config usually do.

🔴 Only average checkpoints that share an architecture AND a tokenizer. The script refuses
otherwise: averaging across architectures produces a well-formed model that emits noise,
which is exactly the silent-failure shape this project keeps getting bitten by.

Greedy mode adds members one at a time and keeps a member only if dev Token F1 improves —
the standard "greedy soup", which protects against one bad member poisoning the average.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpts", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--data-dir", default=None, help="enables greedy mode + scoring")
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--greedy", action="store_true")
    a = ap.parse_args()

    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    cfgs = [json.loads((Path(c) / "config.json").read_text()) for c in a.ckpts]
    archs = {tuple(c.get("architectures") or []) for c in cfgs}
    vocabs = {c.get("vocab_size") for c in cfgs}
    assert len(archs) == 1, f"🔴 refusing to average across architectures: {archs}"
    assert len(vocabs) == 1, f"🔴 refusing to average across vocab sizes: {vocabs}"
    print(f"{len(a.ckpts)} checkpoints · arch {archs.pop()} · vocab {vocabs.pop()}")

    def load_sd(p):
        m = AutoModelForSeq2SeqLM.from_pretrained(p, dtype=torch.float32)
        return m.state_dict(), m

    def score_sd(sd, base):
        """Dev Token F1 for a state dict, using the shared decode path."""
        from metric import token_f1
        import pandas as pd
        base.load_state_dict(sd)
        base.eval().cuda()
        tok = AutoTokenizer.from_pretrained(a.ckpts[0])
        try:
            from normalizer import normalize
        except ImportError:
            def normalize(s):
                return s
        df = pd.read_parquet(Path(a.data_dir) / "dev.parquet").iloc[: a.limit]
        preds = []
        with torch.no_grad():
            for i in range(0, len(df), 8):
                chunk = [normalize(str(x)) for x in df["input"].iloc[i:i + 8]]
                enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                          max_length=768).to("cuda")
                g = base.generate(**enc, num_beams=8, length_penalty=1.2,
                                  min_new_tokens=0, max_new_tokens=320, do_sample=False)
                preds += tok.batch_decode(g, skip_special_tokens=True)
        refs = df["output"].tolist()
        return sum(token_f1(p, r) for p, r in zip(preds, refs)) / len(refs)

    sd0, base = load_sd(a.ckpts[0])
    if a.greedy and a.data_dir:
        kept = [a.ckpts[0]]
        running = {k: v.clone().float() for k, v in sd0.items()}
        best = score_sd({k: v.clone() for k, v in running.items()}, base)
        print(f"  start {Path(a.ckpts[0]).parent.name}: {best:.4f}")
        for c in a.ckpts[1:]:
            sd, _ = load_sd(c)
            n = len(kept)
            trial = {k: (running[k] * n + sd[k].float()) / (n + 1) for k in running}
            s = score_sd({k: v.clone() for k, v in trial.items()}, base)
            keep = s > best
            print(f"  + {Path(c).parent.name}: {s:.4f} {'KEEP' if keep else 'drop'}")
            if keep:
                running, best, kept = trial, s, kept + [c]
        print(f"\ngreedy soup: {len(kept)} members, dev Token F1 {best:.4f}")
        final = running
    else:
        final = {k: v.clone().float() for k, v in sd0.items()}
        for c in a.ckpts[1:]:
            sd, _ = load_sd(c)
            for k in final:
                final[k] += sd[k].float()
        for k in final:
            final[k] /= len(a.ckpts)
        kept = list(a.ckpts)
        best = score_sd({k: v.clone() for k, v in final.items()}, base) if a.data_dir else None
        print(f"uniform soup of {len(kept)}: dev Token F1 {best if best is None else f'{best:.4f}'}")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    base.load_state_dict(final)
    base.save_pretrained(out)
    for f in ("spiece.model", "tokenizer.json", "tokenizer_config.json",
              "special_tokens_map.json", "generation_config.json"):
        src = Path(a.ckpts[0]) / f
        if src.is_file():
            shutil.copy(src, out / f)
    n = sum(p.numel() for p in base.parameters())
    assert n <= 3_000_000_000, f"3B CAP BREACHED: {n:,}"
    (out / "soup.json").write_text(json.dumps(
        {"members": [str(c) for c in kept], "dev_token_f1": best, "params": n}, indent=2))
    print(f"wrote {out}  ({n:,} params, within the 3B cap)")


if __name__ == "__main__":
    raise SystemExit(main())
