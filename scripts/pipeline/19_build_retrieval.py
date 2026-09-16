"""19_build_retrieval.py — E22 arms A and B: nearest-neighbour exemplars from TRAIN only.

    python 19_build_retrieval.py --mode knn-examples --k 16 --out ../E22_retrieval/knn16.json
    python 19_build_retrieval.py --mode augment-input --out ../data/english_draft_rag

🔴 THE INDEX IS BUILT OVER `train` ONLY. Retrieving a dev or test row's own neighbours from
a pool containing dev/test would leak the evaluation set — the same trap that removed 6,000
rows from warmstart_corpus. Asserted below, not assumed.

Retrieval is char-ngram TF-IDF rather than a dense encoder, deliberately:
  * a dense retriever that SHIPS would count against the 3B cap (e5-base is 278M);
  * this corpus is one translator's fingerprint, so surface n-gram overlap is closer to
    what the metric rewards than semantic similarity is;
  * measured earlier in this project, char-TF-IDF retrieval (0.2047 Token F1) beat word
    TF-IDF (0.2020) as a standalone predictor.

Modes
  knn-examples  — for E22 arm A: pick k in-context examples per dev row for the E20 teacher,
                  replacing E20's random draw. Writes a JSON of row -> example ids.
  augment-input — for E22 arm B: prepend the single nearest TRAIN target to each row's input
                  as a style exemplar, producing a new dataset directory.
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="../data/english_draft")
    ap.add_argument("--draft-dir", default="../data/draft_only",
                    help="Bengali drafts, used as the retrieval surface")
    ap.add_argument("--mode", required=True, choices=["knn-examples", "augment-input"])
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors

    d = Path(a.draft_dir)
    train = pd.read_parquet(d / "train.parquet")
    print(f"index over TRAIN only: {len(train):,} rows")

    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=200_000,
                          min_df=2)
    X = vec.fit_transform(train["input"].astype(str))
    nn = NearestNeighbors(n_neighbors=a.k, metric="cosine").fit(X)

    def neighbours(queries, k):
        Q = vec.transform([str(q) for q in queries])
        dist, idx = nn.kneighbors(Q, n_neighbors=k)
        return idx, 1.0 - dist

    if a.mode == "knn-examples":
        dev = pd.read_parquet(d / "dev.parquet").iloc[: a.limit]
        idx, sim = neighbours(dev["input"].tolist(), a.k)
        train_ids = set(train["id"].astype(str))
        dev_ids = set(dev["id"].astype(str))
        assert not (train_ids & dev_ids), "🔴 dev ids present in the retrieval index"
        out = []
        for r in range(len(dev)):
            picks = [int(i) for i in idx[r]]
            out.append({"dev_id": str(dev["id"].iloc[r]),
                        "example_ids": [str(train["id"].iloc[i]) for i in picks],
                        "mean_sim": float(sim[r].mean())})
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        ms = sum(o["mean_sim"] for o in out) / len(out)
        print(f"wrote {a.out}  ·  mean neighbour similarity {ms:.4f}")
        print("🔴 0 dev ids in the index ✅")
        return

    # ---- augment-input: prepend the nearest TRAIN target as a style exemplar ----
    src = Path(a.data_dir)
    outd = Path(a.out); outd.mkdir(parents=True, exist_ok=True)
    tgt_by_row = train["output"].astype(str).tolist()
    for split in ("train", "dev", "test"):
        df = pd.read_parquet(src / f"{split}.parquet")
        drafts = pd.read_parquet(d / f"{split}.parquet")["input"].astype(str).tolist()
        # 🔴 a TRAIN row must not retrieve ITSELF — that would paste the answer into the
        # input and produce a model that cannot work at test time.
        k = 2 if split == "train" else 1
        idx, _ = neighbours(drafts, k)
        picks = []
        for r in range(len(df)):
            cand = [int(i) for i in idx[r]]
            if split == "train":
                self_i = r if r < len(train) else -1
                cand = [c for c in cand if c != self_i] or [cand[0]]
            picks.append(tgt_by_row[cand[0]])
        df = df.copy()
        df["input"] = ["শৈলী উদাহরণ: " + p + "\n\n" + str(x)
                       for p, x in zip(picks, df["input"].astype(str))]
        df.to_parquet(outd / f"{split}.parquet", index=False)
        print(f"  {split}: {len(df):,} rows augmented with a retrieved exemplar")
    (outd / "FIELDS.txt").write_text("english_draft + nearest TRAIN target as style exemplar\n")


if __name__ == "__main__":
    raise SystemExit(main())
