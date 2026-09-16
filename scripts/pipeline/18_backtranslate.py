"""18_backtranslate.py — E21 arm A: build a SECOND draft for every training row.

    python 18_backtranslate.py --shard 3 --num-shards 16 --out bt/

Round-trips the organizers' Bengali target through English and back:

    T ──NLLB bn→en──► E' ──NLLB en→bn──► D'      new pair: (D', T)

🔴 The target is never synthesized. `T` stays the organizers' real text; only the *input*
side is generated. Synthesizing targets would teach the wrong register, which is the trap
E21's spec calls out first.

🔴 NLLB on purpose, not Google. E17 measured NLLB at −0.0439 against the production draft,
and that distance is the point: a round-trip through the *same* translator would give
D' ≈ D and the augmentation would add nothing. NLLB output is genuinely another point in
draft space, which is what makes A1 a robustness test rather than a duplication.

Sharded because 101,737 rows x 2 translation passes is embarrassingly parallel — run one
shard per GPU and concatenate.
"""

import argparse
import time
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="../data/english_draft")
    ap.add_argument("--model", default="facebook/nllb-200-distilled-600M")
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--num-shards", type=int, required=True)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    assert torch.cuda.is_available(), "❌ no CUDA device — refusing to run on CPU"
    cap = torch.cuda.get_device_capability()
    dtype = torch.float16 if cap[0] >= 7 else torch.float32   # NLLB is fp16-safe (not T5)
    print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {dtype}", flush=True)

    df = pd.read_parquet(Path(a.data_dir) / "train.parquet")
    df = df.iloc[a.shard::a.num_shards].reset_index(drop=True)
    print(f"shard {a.shard}/{a.num_shards}: {len(df):,} rows", flush=True)

    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(a.model, dtype=dtype).cuda().eval()

    def translate(texts, src, tgt):
        tok.src_lang = src
        out = []
        bos = tok.convert_tokens_to_ids(tgt)
        for i in range(0, len(texts), a.batch_size):
            enc = tok([str(t) for t in texts[i:i + a.batch_size]], return_tensors="pt",
                      padding=True, truncation=True, max_length=a.max_len).to("cuda")
            with torch.no_grad():
                g = model.generate(**enc, forced_bos_token_id=bos, num_beams=4,
                                   max_new_tokens=a.max_len)
            out += tok.batch_decode(g, skip_special_tokens=True)
            if i % (a.batch_size * 20) == 0:
                print(f"  {i}/{len(texts)}", flush=True)
        return out

    t0 = time.time()
    print("pass 1: bn -> en", flush=True)
    en = translate(df["output"].tolist(), "ben_Beng", "eng_Latn")
    print("pass 2: en -> bn", flush=True)
    bn = translate(en, "eng_Latn", "ben_Beng")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"id": df["id"], "bt_draft": bn, "output": df["output"]}).to_parquet(
        out / f"shard{a.shard:03d}.parquet", index=False)
    print(f"wrote {out}/shard{a.shard:03d}.parquet in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    raise SystemExit(main())
