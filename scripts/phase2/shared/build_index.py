"""build_index.py — STEP 1. Build the Tier-1 training pool and its dense retrieval index.

Run this ONCE, from the folder root. All three models share its output.

    python shared/build_index.py

Everything it reads is bundled in `data/_sources/` -- this folder is self-contained and does NOT
need the wider repo.

What it does
  1. Assembles the Tier-1 core mix (see DATA_GUIDE.md):
       train.parquet (competition, dev/test already removed)   101,740
       + extra_sources.parquet, source=='icliniq'                7,321
       + extra_sources.parquet, source=='genmedgpt'              5,200
       + extra_sources.parquet, source=='doctor_qa_bangla'       4,651
       = 118,912 rows
     healthcaremagic is NOT bundled at all -- it is our own re-translation of the same cases the
     competition already provides, so it was excluded at extraction time. See DATA_GUIDE.md.
  2. Asserts ZERO frozen dev/test ids are present.
  3. Embeds every `input` with intfloat/multilingual-e5-base (L2-normalized).
  4. Saves embeddings + metadata + a MANIFEST.json for the Phase 2 write-up.

Why dense embeddings and not the char-TF-IDF used elsewhere in this repo: that retriever fed a
model which ALREADY had the answer via id-lookup, so surface n-gram overlap was all that
mattered. This retriever feeds a model with no lookup at all, where two patients describing the
same condition in different words must still match.

🔴 The retriever SHIPS at inference if a RAG arm wins, so its ~278M params count toward the 3B
cap. Budget in README.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

EMBED_MODEL = "intfloat/multilingual-e5-base"
KEEP_SOURCES = ("icliniq", "genmedgpt", "doctor_qa_bangla")


def mean_pool(last_hidden, attention_mask):
    mask = attention_mask.unsqueeze(-1).float()
    return (last_hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)


def embed_texts(texts, tok, model, device, batch_size=64, prefix="passage: ", max_length=256):
    """L2-normalized mean-pooled embeddings. e5 REQUIRES the query:/passage: prefix."""
    import torch
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            chunk = [prefix + str(t) for t in texts[i:i + batch_size]]
            enc = tok(chunk, padding=True, truncation=True, max_length=max_length,
                      return_tensors="pt").to(device)
            emb = mean_pool(model(**enc).last_hidden_state, enc["attention_mask"])
            emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            out.append(emb.cpu().numpy().astype(np.float32))
            if i % (batch_size * 50) == 0:
                print(f"  embedded {i}/{len(texts)}", flush=True)
    return np.concatenate(out, axis=0)


def load_pool(src: Path) -> pd.DataFrame:
    for p in (src / "train.parquet", src / "extra_sources.parquet"):
        assert p.is_file(), f"missing bundled input: {p}"

    train = pd.read_parquet(src / "train.parquet")[["id", "input", "output"]].copy()
    train["source"] = "competition_train"
    print(f"competition_train : {len(train):,}")

    m = pd.read_parquet(src / "extra_sources.parquet")
    assert {"id", "source", "input", "output"} <= set(m.columns), m.columns
    # Sanity: healthcaremagic must not be here -- see the module docstring / DATA_GUIDE.md.
    assert not (set(m["source"]) - set(KEEP_SOURCES)), (
        f"🔴 unexpected sources in extra_sources.parquet: "
        f"{set(m['source']) - set(KEEP_SOURCES)}")
    for s in KEEP_SOURCES:
        print(f"{s:18s}: {int((m['source'] == s).sum()):,}")

    pool = pd.concat([train, m[["id", "source", "input", "output"]]], ignore_index=True)
    pool = pool.dropna(subset=["input", "output"])
    pool = pool[pool["input"].astype(str).str.strip().astype(bool)
                & pool["output"].astype(str).str.strip().astype(bool)]
    return pool.reset_index(drop=True)


def assert_no_leak(pool: pd.DataFrame, src: Path):
    """🔴 Do not disable. A dev row in the pool means its own answer is retrievable."""
    dev_ids = set(pd.read_parquet(src / "dev.parquet")["id"].astype(str))
    test_ids = set(pd.read_parquet(src / "test.parquet")["id"].astype(str))
    pool_ids = set(pool["id"].astype(str))
    leak = (pool_ids & dev_ids) | (pool_ids & test_ids)
    assert not leak, (f"🔴 LEAK: {len(leak)} pool rows are in the frozen dev/test split. "
                      f"Examples: {list(leak)[:10]}")
    print(f"✅ leak check passed -- 0 of {len(dev_ids):,} dev + {len(test_ids):,} test ids in pool")
    return len(dev_ids), len(test_ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="data/_sources",
                    help="bundled data dir (train/dev/test.parquet + extra_sources.parquet)")
    ap.add_argument("--out", default="data/_index")
    ap.add_argument("--batch-size", type=int, default=64)
    a = ap.parse_args()

    import torch
    from transformers import AutoModel, AutoTokenizer

    src = Path(a.sources).resolve()
    outd = Path(a.out); outd.mkdir(parents=True, exist_ok=True)
    print(f"sources: {src}\n")

    pool = load_pool(src)
    print(f"\npool total: {len(pool):,} rows")
    n_dev, n_test = assert_no_leak(pool, src)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("⚠️  no GPU visible -- embedding 118k rows on CPU will take hours.")
    tok = AutoTokenizer.from_pretrained(EMBED_MODEL)
    model = AutoModel.from_pretrained(EMBED_MODEL).to(device).eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"\nretriever: {EMBED_MODEL} on {device}, {n_params:,} params")
    print("🔴 these params count toward the 3B cap if a RAG arm ships\n")

    emb = embed_texts(pool["input"].tolist(), tok, model, device, batch_size=a.batch_size)
    print(f"embeddings: {emb.shape}")

    np.save(outd / "pool_embeddings.npy", emb)
    pool.to_parquet(outd / "pool_metadata.parquet", index=False)
    (outd / "MANIFEST.json").write_text(json.dumps({
        "embed_model": EMBED_MODEL,
        "embed_params": int(n_params),
        "pool_rows": int(len(pool)),
        "pool_sources": {k: int(v) for k, v in pool["source"].value_counts().items()},
        "healthcaremagic_included": False,   # excluded at extraction time, not bundled
        "dev_ids_checked": int(n_dev),
        "test_ids_checked": int(n_test),
        "leak_assert": "PASSED - 0 overlap",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ wrote {outd}/ -- pool_embeddings.npy, pool_metadata.parquet, MANIFEST.json")
    print("next: python shared/build_data.py")


if __name__ == "__main__":
    raise SystemExit(main())
