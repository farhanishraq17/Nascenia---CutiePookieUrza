"""build_data.py — STEP 2. Turn the index into every dataset variant the experiments need.

Run ONCE after build_index.py. All three models share its output.

    python shared/build_data.py

Reads only from `data/_sources/` and `data/_index/` -- this folder is self-contained.

Produces (each with train/dev/test.parquet, schema `id · input · output`):

    data/plain/             X2, X5  -- question -> answer. No retrieval.
    data/rag/               X3, X6  -- retrieved reference case + question -> answer.
    data/plain_core_only/   X4      -- competition train.parquet ONLY (no iCliniq/GenMedGPT/dqb).
    data/plain_core_plus_icliniq/           D1  -- competition + icliniq only
    data/plain_core_plus_genmedgpt/         D2  -- competition + genmedgpt only
    data/plain_core_plus_doctor_qa_bangla/  D3  -- competition + doctor_qa_bangla only
                                    ^ D1/D2/D3 decompose X4. mT5-base ONLY -- see EXPERIMENTS.md

`dev` is always the frozen dev[0:300] selection slice with REAL targets, so every arm is scored
on identical rows and is directly comparable to this project's other numbers.
`test` is the 1,000 competition test rows (no targets) -- built so a winning arm can be decoded
without rebuilding anything.

🔴 TWO INVARIANTS, both asserted, neither safe to disable:
  1. No frozen dev/test id may appear in any TRAIN split.
  2. In `rag/train`, a row may never retrieve ITSELF or a near-duplicate (cosine > --sim-ceiling)
     as its own reference -- that pastes the answer into the input and the model collapses at
     test time. VERIFY THIS BY READING BUILT EXAMPLES, not just by trusting the assert.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

RAG_TEMPLATE = ("অনুরূপ কেস:\nরোগী: {ref_q}\nডাক্তার: {ref_a}\n\n"
                "নতুন রোগীর প্রশ্ন:\n{question}")
# Bengali field labels on purpose: the target output is Bengali, and an English scaffold around
# a Bengali payload is an unnecessary code-switch for a model whose Bengali is the thing we care
# about. (The champion used English labels, but it was translating FROM English.)


def topk_excluding_self(emb: np.ndarray, k: int, sim_ceiling: float, batch: int = 1024):
    """Top-k nearest OTHER rows for every row. Excludes self and near-duplicates.

    Chunked because a 119k x 119k similarity matrix is ~56 GB materialized whole.
    """
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    E = torch.from_numpy(emb).to(device)
    n = E.shape[0]
    out = np.full((n, k), -1, dtype=np.int64)
    for i in range(0, n, batch):
        q = E[i:i + batch]
        sims = q @ E.T
        rows = torch.arange(i, min(i + batch, n), device=device)
        sims[torch.arange(sims.shape[0], device=device), rows] = -2.0   # never itself
        sims[sims > sim_ceiling] = -2.0                                  # never a near-dup
        out[i:i + batch] = torch.topk(sims, k=k, dim=1).indices.cpu().numpy()
        if i % (batch * 20) == 0:
            print(f"  retrieval {i}/{n}", flush=True)
    return out


def topk_query(qemb: np.ndarray, pemb: np.ndarray, k: int, batch: int = 1024):
    """Top-k pool rows for external queries (dev/test) -- no self to exclude, they aren't in it."""
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    Q, P = torch.from_numpy(qemb).to(device), torch.from_numpy(pemb).to(device)
    out = np.full((Q.shape[0], k), -1, dtype=np.int64)
    for i in range(0, Q.shape[0], batch):
        out[i:i + batch] = torch.topk(Q[i:i + batch] @ P.T, k=k, dim=1).indices.cpu().numpy()
    return out


def write_split(df: pd.DataFrame, path: Path, name: str):
    path.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path / f"{name}.parquet", index=False)
    print(f"  {path.name}/{name}.parquet: {len(df):,} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="data/_sources")
    ap.add_argument("--index", default="data/_index")
    ap.add_argument("--out", default="data")
    ap.add_argument("--sim-ceiling", type=float, default=0.97)
    ap.add_argument("--dev-limit", type=int, default=300)
    a = ap.parse_args()

    import torch
    from transformers import AutoModel, AutoTokenizer
    from build_index import EMBED_MODEL, embed_texts

    proc = Path(a.sources).resolve()
    idx = Path(a.index)
    outd = Path(a.out)

    pool = pd.read_parquet(idx / "pool_metadata.parquet")
    emb = np.load(idx / "pool_embeddings.npy")
    assert len(pool) == emb.shape[0], "pool/embedding row mismatch -- rebuild the index"
    print(f"pool: {len(pool):,} rows, embeddings {emb.shape}")

    dev = pd.read_parquet(proc / "dev.parquet").iloc[: a.dev_limit].reset_index(drop=True)
    test = pd.read_parquet(proc / "test.parquet").reset_index(drop=True)

    # ---- leak re-assert (cheap, and the one mistake that invalidates everything) -------------
    dev_ids, test_ids = set(dev["id"].astype(str)), set(test["id"].astype(str))
    assert not (set(pool["id"].astype(str)) & (dev_ids | test_ids)), "🔴 dev/test id in pool"
    print("✅ leak re-check passed")

    # ================= plain =================
    print("\n[plain]")
    write_split(pool[["id", "input", "output"]], outd / "plain", "train")
    write_split(dev[["id", "input", "output"]], outd / "plain", "dev")
    write_split(test[["id", "input"]], outd / "plain", "test")

    # ================= plain_core_only (X4 ablation) =================
    print("\n[plain_core_only] -- competition train.parquet only")
    core = pool[pool["source"] == "competition_train"]
    write_split(core[["id", "input", "output"]], outd / "plain_core_only", "train")
    write_split(dev[["id", "input", "output"]], outd / "plain_core_only", "dev")
    write_split(test[["id", "input"]], outd / "plain_core_only", "test")

    # ================= D1/D2/D3 -- per-source decomposition ==================
    # X4 only compares "all extras" vs "no extras". If that comes back negative it cannot say
    # WHICH source hurt -- and the three are very unalike: genmedgpt's median answer is 31 words
    # against the competition's 93, icliniq's is 77. These three variants isolate each one.
    #
    # 🔴 Run these on mT5-base ONLY. Data effects transfer across architectures; model
    # differences are what the A/B/C comparison is for. Running all of them on all three models
    # triples the cost of answering a question that is not model-specific.
    for src_name in ("icliniq", "genmedgpt", "doctor_qa_bangla"):
        variant = f"plain_core_plus_{src_name}"
        sub = pool[pool["source"].isin(["competition_train", src_name])]
        n_extra = int((sub["source"] == src_name).sum())
        assert n_extra > 0, f"🔴 no {src_name} rows in the pool -- check extra_sources.parquet"
        print(f"\n[{variant}] -- competition + {src_name} ({n_extra:,} extra rows)")
        write_split(sub[["id", "input", "output"]], outd / variant, "train")
        write_split(dev[["id", "input", "output"]], outd / variant, "dev")
        write_split(test[["id", "input"]], outd / variant, "test")

    # ================= rag =================
    print("\n[rag] train -- each row retrieves a DIFFERENT case")
    tr_idx = topk_excluding_self(emb, k=1, sim_ceiling=a.sim_ceiling)
    rows, dropped = [], 0
    for i in range(len(pool)):
        j = tr_idx[i][0]
        if j < 0:
            dropped += 1
            continue
        ref = pool.iloc[j]
        rows.append({"id": pool["id"].iloc[i],
                     "input": RAG_TEMPLATE.format(ref_q=ref["input"], ref_a=ref["output"],
                                                  question=pool["input"].iloc[i]),
                     "output": pool["output"].iloc[i]})
    rag_train = pd.DataFrame(rows)
    assert len(rag_train) > 0.95 * len(pool), (
        f"🔴 only {len(rag_train):,}/{len(pool):,} rows got a reference -- sim_ceiling "
        f"({a.sim_ceiling}) is probably too low, excluding almost everything")
    write_split(rag_train, outd / "rag", "train")
    if dropped:
        print(f"  ({dropped} rows dropped -- no valid reference under the ceiling)")

    print("\n[rag] dev/test -- fresh query embeddings against the pool")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(EMBED_MODEL)
    emodel = AutoModel.from_pretrained(EMBED_MODEL).to(device).eval()

    for split_df, name, has_target in ((dev, "dev", True), (test, "test", False)):
        qemb = embed_texts(split_df["input"].tolist(), tok, emodel, device, prefix="query: ")
        qidx = topk_query(qemb, emb, k=1)
        out_rows = []
        for i in range(len(split_df)):
            ref = pool.iloc[qidx[i][0]]
            r = {"id": split_df["id"].iloc[i],
                 "input": RAG_TEMPLATE.format(ref_q=ref["input"], ref_a=ref["output"],
                                              question=split_df["input"].iloc[i]),
                 "ref_input": ref["input"], "ref_output": ref["output"]}
            if has_target:
                r["output"] = split_df["output"].iloc[i]
            out_rows.append(r)
        write_split(pd.DataFrame(out_rows), outd / "rag", name)
    # ref_output is carried through so evaluate.py can run the copy-check (X3) without
    # re-running retrieval.

    (outd / "MANIFEST.json").write_text(json.dumps({
        "built_from_index": str(idx),
        "variants": ["plain", "plain_core_only", "rag",
                     "plain_core_plus_icliniq", "plain_core_plus_genmedgpt",
                     "plain_core_plus_doctor_qa_bangla"],
        "pool_rows": int(len(pool)),
        "pool_sources": {k: int(v) for k, v in pool["source"].value_counts().items()},
        "rag_train_rows": int(len(rag_train)),
        "rag_dropped_no_reference": int(dropped),
        "sim_ceiling": a.sim_ceiling,
        "dev_rows": int(len(dev)), "test_rows": int(len(test)),
        "rag_template": RAG_TEMPLATE,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 70)
    print("🔴 NOW GO READ 5 ROWS OF data/rag/train.parquet BY HAND.")
    print("Confirm the 'অনুরূপ কেস' reference is a DIFFERENT case from the question being")
    print("asked. The assert above cannot catch a subtly wrong template -- your eyes can.")
    print("=" * 70)


if __name__ == "__main__":
    raise SystemExit(main())
