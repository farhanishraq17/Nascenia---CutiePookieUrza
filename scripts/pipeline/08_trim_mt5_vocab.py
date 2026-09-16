"""Trim mT5's 250k vocabulary to the tokens this corpus actually uses.

Measured on 15,000 train rows: **22,991 of 250,100 mT5 tokens are ever used (9.2%)**.
Embeddings are ~66% of mT5-base (192.1M x 2 of 580M) and ~42% of mT5-large.

    trim to 32k  ->  mT5-base  580M -> ~245M   ·  mT5-large 1.23B -> ~785M
                     decoder logits tensor 7.8x smaller  <- the dominant memory term

🔴 WHAT THIS DOES AND DOES NOT DO

  DOES  cut parameters, optimizer state and (decisively) the `batch x len x vocab`
        logits tensor, so batches get much larger and steps much faster.
  DOES  keep every retained token's PRETRAINED embedding — this is row selection,
        not re-initialisation, so no pretrained knowledge is discarded.
  DOES NOT change tokens-per-sentence. SentencePiece segments Bengali identically;
        mT5 still needs ~88% more tokens than BanglaT5 for the same Bengali text.
        Trimming is an efficiency win, NOT a quality win.

Keeps: every token appearing anywhere in train/dev/test (both fields), plus all special
ids and a byte-fallback margin. Unused ids are dropped and the tokenizer is rebuilt so
old ids never reach the model.

Usage:
    python 08_trim_mt5_vocab.py --model google/mt5-base \
        --data ../data/english_draft --out ../models/mt5-base-trimmed
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="trim mT5 vocabulary to observed tokens")
    ap.add_argument("--model", default="google/mt5-base")
    ap.add_argument("--data", required=True, help="dir with train/dev/test.parquet")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-keep", type=int, default=32000,
                    help="pad the kept set to at least this many ids (headroom for unseen text)")
    a = ap.parse_args(argv)

    import pandas as pd
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(a.model)
    V = model.config.vocab_size
    before = sum(p.numel() for p in model.parameters())
    print(f"{a.model}: vocab {V:,}  params {before/1e6:.1f}M")

    # ---- collect every id the corpus can produce or consume
    used: set[int] = set()
    for split in ("train", "dev", "test"):
        p = Path(a.data) / f"{split}.parquet"
        if not p.is_file():
            continue
        df = pd.read_parquet(p)
        for col in ("input", "output"):
            if col in df.columns:
                for chunk in range(0, len(df), 2000):
                    batch = df[col].iloc[chunk:chunk + 2000].astype(str).tolist()
                    for ids in tok(batch)["input_ids"]:
                        used.update(ids)
        print(f"  {split:5s} scanned — cumulative distinct ids {len(used):,}")

    # every special id must survive, whatever the corpus contains
    used.update(i for i in tok.all_special_ids if i is not None)
    used.update(range(min(1000, V)))          # sentinels / extra_ids live low
    if len(used) < a.min_keep:                # headroom for text we have not seen
        used.update(range(a.min_keep))
    keep = sorted(i for i in used if i < V)
    print(f"\nkeeping {len(keep):,} / {V:,} ids ({len(keep)/V*100:.1f}%)")

    # ---- row-select the embedding + lm_head. Pretrained vectors are preserved.
    old_to_new = {old: new for new, old in enumerate(keep)}
    idx = torch.tensor(keep, dtype=torch.long)

    emb = model.get_input_embeddings()
    new_emb = torch.nn.Embedding(len(keep), emb.embedding_dim)
    new_emb.weight.data = emb.weight.data[idx].clone()
    model.set_input_embeddings(new_emb)

    if getattr(model, "lm_head", None) is not None and not model.config.tie_word_embeddings:
        old_head = model.lm_head
        new_head = torch.nn.Linear(old_head.in_features, len(keep), bias=old_head.bias is not None)
        new_head.weight.data = old_head.weight.data[idx].clone()
        if old_head.bias is not None:
            new_head.bias.data = old_head.bias.data[idx].clone()
        model.lm_head = new_head

    model.config.vocab_size = len(keep)
    for attr in ("decoder_start_token_id", "pad_token_id", "eos_token_id", "bos_token_id"):
        v = getattr(model.config, attr, None)
        if isinstance(v, int) and v in old_to_new:
            setattr(model.config, attr, old_to_new[v])
    if model.generation_config is not None:
        for attr in ("decoder_start_token_id", "pad_token_id", "eos_token_id", "bos_token_id"):
            v = getattr(model.generation_config, attr, None)
            if isinstance(v, int) and v in old_to_new:
                setattr(model.generation_config, attr, old_to_new[v])

    after = sum(p.numel() for p in model.parameters())
    print(f"params {before/1e6:.1f}M -> {after/1e6:.1f}M  ({after/before*100:.0f}%)")
    assert after <= 3_000_000_000, "❌ 3B cap"

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out)

    # ---- rebuild the tokenizer so it can only ever emit the retained ids
    from tokenizers import Tokenizer
    fast = tok.backend_tokenizer if hasattr(tok, "backend_tokenizer") else None
    if fast is None:
        print("⚠️  no fast tokenizer — saving the ORIGINAL tokenizer.\n"
              "    Ids will NOT match the trimmed model. Do not train until this is resolved.")
        tok.save_pretrained(out)
        return 1

    import json
    state = json.loads(fast.to_str())
    vocab = state["model"].get("vocab")
    if isinstance(vocab, list):        # unigram: [[piece, score], ...]
        state["model"]["vocab"] = [vocab[i] for i in keep]
    elif isinstance(vocab, dict):      # bpe/wordpiece
        inv = {v: k for k, v in vocab.items()}
        state["model"]["vocab"] = {inv[i]: n for n, i in enumerate(keep) if i in inv}
        state["model"]["merges"] = []
    else:
        raise RuntimeError(f"unexpected tokenizer model type: {state['model'].get('type')}")

    new_tok = Tokenizer.from_str(json.dumps(state))
    from transformers import PreTrainedTokenizerFast
    wrapped = PreTrainedTokenizerFast(
        tokenizer_object=new_tok,
        unk_token=tok.unk_token, pad_token=tok.pad_token, eos_token=tok.eos_token,
        additional_special_tokens=list(tok.additional_special_tokens or []),
    )
    wrapped.save_pretrained(out)

    # ---- prove it round-trips before anyone spends GPU hours on it
    probe = "english: Hi, thank you for your query.\nbangla: হেলো, নাসেনিয়া ডকে আপনাকে স্বাগতম।"
    ids = wrapped(probe)["input_ids"]
    assert max(ids) < len(keep), f"❌ id {max(ids)} >= trimmed vocab {len(keep)}"
    print(f"\nround-trip: {len(ids)} ids, max {max(ids)} < {len(keep)} ✅")
    print(f"decoded: {wrapped.decode(ids)[:90]}…")
    print(f"\nwritten to {out}")
    print("⚠️  Re-tokenise ALL data with THIS tokenizer. Original mT5 ids are now invalid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
