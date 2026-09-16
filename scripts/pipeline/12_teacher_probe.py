"""12_teacher_probe.py — E20 stage 1: can a large teacher do register transfer at all?

    python 12_teacher_probe.py --model Qwen/Qwen3-32B --data-dir ../data/draft_only \\
        --shots 20 --limit 300 --out probe_qwen3_32b.json

Few-shot only, no training. The teacher never ships — it exists to find out whether a
fundamentally more capable model has headroom the 248M student could inherit.

🔴 IN-CONTEXT EXAMPLES COME FROM `train` ONLY. Drawing them from dev leaks the evaluation
set and the number becomes meaningless — the same trap that removed 6,000 rows from
warmstart_corpus. This script reads examples from train.parquet and asserts none of their
ids appear in dev.

🔴 STAGE GATE, from EXPERIMENT.md — apply it before running anything downstream:
    > 0.82        real headroom  -> run stage 2 (sequence-level KD)
    0.77 - 0.82   marginal       -> judgment call; prefer E05
    < 0.7724      🔴 STOP        -> scale does not substitute for fine-tuning on a
                                    fingerprint-matching task. A genuinely useful negative.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

PREAMBLE = (
    "You rewrite Bengali medical answers into one specific house style. "
    "Below are examples of a DRAFT and the exact REWRITE expected. "
    "Reproduce that style precisely — the same greeting, the same phrasing habits, "
    "the same length. Output only the rewrite."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--shots", type=int, default=20)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--max-new-tokens", type=int, default=320)
    ap.add_argument("--min-new-tokens", type=int, default=80)
    ap.add_argument("--shot-max-chars", type=int, default=700,
                    help="cap each in-context pair so 20 shots fit the context window")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--knn-file", default=None,
                    help="E22 arm A: JSON from 19_build_retrieval.py giving per-row example "
                         "ids. When set, in-context examples are the query's NEAREST train "
                         "rows instead of a fixed random draw.")
    ap.add_argument("--out", default="teacher_probe.json")
    a = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from metric import compute_metrics

    proc = Path(a.data_dir)
    train = pd.read_parquet(proc / "train.parquet")
    dev = pd.read_parquet(proc / "dev.parquet").iloc[: a.limit]

    shots = train.sample(a.shots, random_state=a.seed)
    leak = set(shots["id"].astype(str)) & set(dev["id"].astype(str))
    assert not leak, f"🔴 in-context examples leaked from dev: {leak}"
    print(f"{a.shots} in-context pairs from TRAIN (0 dev overlap ✅), "
          f"probing {len(dev)} dev rows")

    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"        # 🔴 decoder-only batched generation

    def clip(s):
        return str(s)[: a.shot_max_chars]

    def block_from(rows):
        return "\n\n".join(f"DRAFT:\n{clip(r['input'])}\n\nREWRITE:\n{clip(r['output'])}"
                            for _, r in rows.iterrows())

    shot_block = block_from(shots)
    knn = None
    if a.knn_file:
        import json as _j
        by_id = {str(k): v for k, v in
                 ((e["dev_id"], e["example_ids"]) for e in _j.loads(Path(a.knn_file).read_text()))}
        tr_by_id = train.set_index(train["id"].astype(str))
        knn = (by_id, tr_by_id)
        print(f"E22 arm A: per-row k-NN examples from {a.knn_file}")

    def prompt_for(draft):
        user = f"{PREAMBLE}\n\n{shot_block}\n\nDRAFT:\n{draft}\n\nREWRITE:"
        msgs = [{"role": "user", "content": user}]
        try:
            return tok.apply_chat_template(msgs, tokenize=False,
                                           add_generation_prompt=True,
                                           enable_thinking=False)
        except TypeError:
            return tok.apply_chat_template(msgs, tokenize=False,
                                           add_generation_prompt=True)

    print(f"loading {a.model} …", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="auto", trust_remote_code=True).eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"teacher parameters: {n_params/1e9:.1f}B "
          f"(over the 3B cap on purpose — it never ships)", flush=True)

    if knn:
        by_id, tr_by_id = knn
        prompts = []
        for _, row in dev.iterrows():
            ids = [i for i in by_id.get(str(row["id"]), []) if i in tr_by_id.index][: a.shots]
            blk = block_from(tr_by_id.loc[ids]) if ids else shot_block
            user = f"{PREAMBLE}\n\n{blk}\n\nDRAFT:\n{row['input']}\n\nREWRITE:"
            msgs = [{"role": "user", "content": user}]
            try:
                prompts.append(tok.apply_chat_template(msgs, tokenize=False,
                                                       add_generation_prompt=True,
                                                       enable_thinking=False))
            except TypeError:
                prompts.append(tok.apply_chat_template(msgs, tokenize=False,
                                                       add_generation_prompt=True))
    else:
        prompts = [prompt_for(x) for x in dev["input"].tolist()]
    print(f"prompt tokens: {len(tok(prompts[0])['input_ids']):,}", flush=True)

    preds, t0 = [], time.time()
    for i in range(0, len(prompts), a.batch_size):
        enc = tok(prompts[i: i + a.batch_size], return_tensors="pt",
                  padding=True, add_special_tokens=False).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, do_sample=False,
                                 min_new_tokens=a.min_new_tokens,
                                 max_new_tokens=a.max_new_tokens,
                                 pad_token_id=tok.pad_token_id)
        preds += tok.batch_decode(out[:, enc["input_ids"].shape[1]:],
                                  skip_special_tokens=True)
        done = min(i + a.batch_size, len(prompts))
        print(f"  {done}/{len(prompts)}  ({(time.time()-t0)/60:.1f} min)", flush=True)

    preds = [p.strip().split("\n\nDRAFT:")[0].strip() for p in preds]
    res = compute_metrics(preds, dev["output"].tolist(), bertscore=False)

    f1 = res["token_f1"]
    gate = ("✅ >0.82 — real headroom, RUN STAGE 2" if f1 > 0.82 else
            "⚠️ 0.77–0.82 — marginal, prefer E05" if f1 >= 0.7724 else
            "🔴 <0.7724 — STOP. Scale does not substitute for fine-tuning here.")
    rec = {"model": a.model, "params": n_params, "shots": a.shots, "rows": len(dev),
           "token_f1": f1, "rouge_l": res["rouge_l"],
           "mean_pred_tokens": res["mean_pred_tokens"],
           "pred_lb": 0.4646 + 0.3098 * f1 + 0.2 * res["rouge_l"],
           "student_token_f1": 0.7724, "gate": gate,
           "minutes": round((time.time() - t0) / 60, 1), "predictions": preds}
    Path(a.out).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nteacher Token F1 {f1:.4f}  ROUGE-L {res['rouge_l']:.4f}  "
          f"vs student 0.7724\n{gate}\nwrote {a.out}")


if __name__ == "__main__":
    raise SystemExit(main())
