"""
02_train_t5.py — Track A: fine-tune a Bengali seq2seq model to clone the corpus register.

This is the primary bet. See PLAN.md sections 0, 0.5 and 3.

WHY SEQ2SEQ AND WHY STYLE-CLONING
    Measured on this data (PLAN.md §0.5):
        constant string ............ 0.4603
        two real doctors, same Q ... 0.5327
        public LB #1 ............... 0.57756
    The leaderboard leader already beats human-human agreement, because the metric
    rewards reproducing THIS corpus's boilerplate scaffolding — which two independent
    doctors would never share — not clinical correctness. So the objective here is
    distribution cloning, not reasoning.

KEY RECIPE CHOICES (each is a deliberate metric decision, not a default)
  * label_smoothing = 0.0
        Smoothing deliberately blunts peaked output distributions. Peaked is exactly
        what earns Token F1 here — we WANT confident reproduction of frequent phrasing.
  * Early stopping on DEV COMPOSITE, not val loss.
        Loss and the metric diverge: loss rewards calibrated probability over all
        tokens, the metric rewards overlap with one reference. Selecting on loss picks
        the wrong checkpoint.
  * csebuetnlp normalizer applied before tokenization.
        REQUIRED for BanglaT5 — the model card is explicit that skipping it degrades
        results. Not optional.
  * min_new_tokens enforced at generation time.
        Measured length sensitivity: score rises to ~120 tokens then saturates, so
        undershooting costs real points while overshooting costs almost nothing.

USAGE
    python 02_train_t5.py                          # BanglaT5, seed 42
    python 02_train_t5.py --seed 1337              # another ensemble member
    python 02_train_t5.py --model google/mt5-base
    python 02_train_t5.py --max-train 5000 --epochs 1 --smoke   # fast sanity run

Every run appends its config + dev components to LOCAL_EXPERIMENTS.md-style JSON in
the run directory. Phase 2 requires reproducing leaderboard outputs exactly, so seed,
config and checkpoint hash are recorded from run #1.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "DATA" / "PROCESSED"
RUNS = ROOT / "RUNS"

DEFAULT_MODEL = "csebuetnlp/banglat5"


# ---------------------------------------------------------------- normalizer
def get_normalizer(enabled: bool):
    """
    csebuetnlp normalizer. REQUIRED for BanglaT5 per its model card:
    'make sure the text units are normalized using this pipeline before tokenizing'.

        pip install git+https://github.com/csebuetnlp/normalizer
    """
    if not enabled:
        return lambda s: s
    try:
        from normalizer import normalize  # type: ignore
        return lambda s: normalize(str(s))
    except ImportError:
        print(
            "⚠️  csebuetnlp `normalizer` NOT INSTALLED.\n"
            "    BanglaT5's model card requires it; results will be degraded.\n"
            "    pip install git+https://github.com/csebuetnlp/normalizer\n"
            "    Continuing unnormalized — record this in LOCAL_EXPERIMENTS.md.",
            file=sys.stderr,
        )
        return lambda s: str(s)


def set_seed(seed: int):
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def sha256_dir(path: Path) -> str:
    """Stable hash over checkpoint weight files — Phase 2 reproducibility evidence.

    Hashes file CONTENTS, not just names and sizes. Name+size alone is constant across
    every BanglaT5 run — three different sweep arms reported the identical hash
    9e3126b85e78323a, and a 2.6-minute smoke run collided with a 393-minute real run.
    """
    h = hashlib.sha256()
    for f in sorted(path.rglob("*")):
        if f.is_file() and f.suffix in {".bin", ".safetensors", ".json", ".model"}:
            h.update(f.name.encode())
            with f.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Track A seq2seq fine-tune")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--eval-batch-size", type=int, default=8)
    # 384/256 subword tokens comfortably covers p99 (235/223 words) for BanglaT5's
    # Bengali-native vocab. 512/320 wasted memory on padding almost no row needed.
    ap.add_argument("--max-source-len", type=int, default=384)
    ap.add_argument("--max-target-len", type=int, default=256)
    ap.add_argument("--optim", default="adafactor",
                    help="adafactor is the canonical T5 optimizer and uses factored "
                         "second moments — roughly 2GB less than adamw for a 247M "
                         "model in fp32. Use adamw_torch only if you have headroom.")
    ap.add_argument("--warmup", type=int, default=1000)
    ap.add_argument("--label-smoothing", type=float, default=0.0)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--max-train", type=int, default=None, help="subsample training rows")
    ap.add_argument("--eval-subset", type=int, default=1000,
                    help="dev rows used for in-training metric eval (full dev is slow)")
    ap.add_argument("--eval-steps", type=int, default=2000)
    ap.add_argument("--no-normalizer", action="store_true")
    ap.add_argument("--no-bertscore-eval", action="store_true",
                    help="skip BERTScore during training (faster; lexical only)")
    ap.add_argument("--gen-num-beams", type=int, default=4)
    ap.add_argument("--gen-min-new-tokens", type=int, default=80)
    ap.add_argument("--gen-max-new-tokens", type=int, default=320)
    ap.add_argument("--gen-length-penalty", type=float, default=1.0)
    ap.add_argument("--precision", default="auto", choices=["auto", "fp32", "fp16", "bf16"],
                    help="auto = bf16 if the GPU supports it, else fp32. "
                         "fp16 is NOT chosen automatically: T5-family models overflow "
                         "in fp16 and produce NaN losses.")
    ap.add_argument("--grad-checkpointing", action="store_true",
                    help="trade compute for memory; needed for long seqs on 16GB cards")
    # DEFAULT OFF. When enabled without a precomputed `length` column, HF Trainer
    # builds lengths by iterating every Arrow row in Python — ~14 SILENT minutes on
    # 101,740 rows, indistinguishable from a hang. It cost two runs. The `length`
    # column is now emitted during tokenization, but the default stays off so a
    # stale notebook cannot reintroduce the stall.
    ap.add_argument("--group-by-length", action="store_true", default=False,
                    help="batch similar-length sequences (20-30%% faster). OFF by "
                         "default; only safe because preprocess() now emits `length`.")
    ap.add_argument("--no-group-by-length", dest="group_by_length", action="store_false")
    ap.add_argument("--run-name", default=None)
    ap.add_argument("--data-dir", default=None, help="dir with train.parquet/dev.parquet")
    ap.add_argument("--out-dir", "--out", dest="out_dir", default=None,
                    help="where to write runs (Kaggle: /kaggle/working)")
    ap.add_argument("--smoke", action="store_true", help="tiny run to validate the pipeline")
    # A step budget is the honest unit here: epochs are an artefact of batch size, and
    # every EXPERIMENT.md states its budget in steps. --epochs stays for back-compat.
    ap.add_argument("--max-steps", type=int, default=None,
                    help="hard step budget; overrides --epochs when set")
    ap.add_argument("--save-steps", type=int, default=None,
                    help="checkpoint interval; defaults to --eval-steps. Must be a "
                         "multiple of it (load_best_model_at_end requires that).")
    ap.add_argument("--save-total-limit", type=int, default=2,
                    help="rolling checkpoint count. 0 = keep every one (E05 only: its "
                         "trajectory checkpoints ARE the result).")
    ap.add_argument("--early-stopping-patience", type=int, default=3,
                    help="evals without a composite improvement before stopping")
    ap.add_argument("--resume", action="store_true",
                    help="resume from the latest checkpoint in the run dir if present. "
                         "Makes a preempted/requeued SLURM job cheap to restart.")
    a = ap.parse_args(argv)

    global PROC, RUNS
    if a.data_dir:
        PROC = Path(a.data_dir)
    if a.out_dir:
        RUNS = Path(a.out_dir)

    if a.smoke:
        a.max_train = a.max_train or 2000
        a.epochs = min(a.epochs, 1.0)
        a.eval_subset = min(a.eval_subset, 200)
        a.eval_steps = 50

    import torch
    from transformers import (
        AutoModelForSeq2SeqLM, AutoTokenizer, DataCollatorForSeq2Seq,
        Seq2SeqTrainer, Seq2SeqTrainingArguments, EarlyStoppingCallback,
    )
    from datasets import Dataset
    from metric import compute_metrics as composite_metrics, BERTScorer

    set_seed(a.seed)
    run_name = a.run_name or f"{a.model.split('/')[-1]}_seed{a.seed}_{time.strftime('%m%d-%H%M')}"
    run_dir = RUNS / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(f"Track A fine-tune — {run_name}")
    print("=" * 70)
    print(f"model={a.model}  seed={a.seed}  epochs={a.epochs}  lr={a.lr}")
    print(f"effective batch = {a.batch_size} x {a.grad_accum} = {a.batch_size * a.grad_accum}")

    # ---------------- precision ----------------
    # T5-family models are numerically unstable in fp16: their activations exceed the
    # fp16 range and training collapses to NaN. bf16 has the same exponent range as
    # fp32 and is safe — but bf16 needs Ampere or newer. Kaggle's T4 is Turing, so on
    # Kaggle the correct choice is fp32, NOT fp16.
    n_gpu = torch.cuda.device_count()
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"
    # DO NOT gate on torch.cuda.is_bf16_supported(): on Turing (T4, sm_75) it returns
    # True because bf16 can be *emulated*, not because the hardware supports it.
    # Emulated bf16 on a T4 is SLOWER than plain fp32. Real bf16 tensor cores start
    # at Ampere (sm_80), so gate on compute capability instead.
    cap = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else (0, 0)
    bf16_ok = torch.cuda.is_available() and cap[0] >= 8

    if a.precision == "auto":
        precision = "bf16" if bf16_ok else ("fp32" if torch.cuda.is_available() else "fp32")
    else:
        precision = a.precision
    if precision == "fp16":
        print("⚠️  fp16 requested. T5-family models commonly diverge to NaN in fp16.\n"
              "    If loss becomes nan, rerun with --precision fp32.", file=sys.stderr)
    if precision == "bf16" and not bf16_ok:
        print("⚠️  bf16 unsupported on this GPU; falling back to fp32.", file=sys.stderr)
        precision = "fp32"

    # 🔴 "will be very slow" was too soft: torch falls back to CPU with no error and a
    # tqdm bar that advances, so a dead GPU looks like a healthy run for hours. grn008's
    # faulty GPU4 leaves that whole node at device_count()==0 and three arms ran on CPU
    # before a 0 MiB VRAM reading caught it. Refuse instead of warning.
    assert torch.cuda.is_available(), (
        "❌ no CUDA device visible — refusing to train on CPU. Check `nvidia-smi` on this "
        "node and CUDA_VISIBLE_DEVICES; on a shared allocation export it INSIDE the srun "
        "step, not via --export (SLURM overwrites it).")
    print(f"device: {gpu_name}  (n_gpu={n_gpu})")
    print(f"compute capability sm_{cap[0]}{cap[1]}  bf16 hardware: {bf16_ok}  "
          f"->  precision = {precision}")
    if n_gpu > 1 and os.environ.get("LOCAL_RANK") is None:
        print(f"⚠️  {n_gpu} GPUs visible and not launched under torchrun, so HF Trainer\n"
              f"    will use DataParallel. DataParallel gathers every replica's outputs\n"
              f"    onto GPU 0, so GPU 0 OOMs long before GPU 1 is full — it is the most\n"
              f"    common cause of 'GPU 0 out of memory' with 2x T4.\n"
              f"    Prefer DDP:  torchrun --nproc_per_node={n_gpu} 02_train_t5.py ...\n"
              f"    or pin one GPU:  CUDA_VISIBLE_DEVICES=0 python 02_train_t5.py ...")
        print(f"    per_device batch={a.batch_size} is PER GPU -> effective "
              f"{a.batch_size * a.grad_accum * n_gpu}")

    # ---------------- data ----------------
    train_df = pd.read_parquet(PROC / "train.parquet")
    dev_df = pd.read_parquet(PROC / "dev.parquet")
    if a.max_train:
        train_df = train_df.sample(min(a.max_train, len(train_df)), random_state=a.seed)
    print(f"\ntrain={len(train_df)}  dev={len(dev_df)} (eval on {a.eval_subset})")

    norm = get_normalizer(not a.no_normalizer)
    tok = AutoTokenizer.from_pretrained(a.model)

    def preprocess(batch):
        src = [norm(x) for x in batch["input"]]
        tgt = [norm(x) for x in batch["output"]]
        enc = tok(src, max_length=a.max_source_len, truncation=True)
        lab = tok(text_target=tgt, max_length=a.max_target_len, truncation=True)
        enc["labels"] = lab["input_ids"]
        # Precompute the length column. Without it, group_by_length makes Trainer
        # build lengths by iterating all 101,740 rows in Python and deserializing
        # each Arrow row one at a time — several silent minutes with no progress bar.
        # Providing it here is free (we already have the tokenized ids).
        enc["length"] = [len(x) for x in enc["input_ids"]]
        return enc

    # Every DDP rank runs this. Two constraints pull in opposite directions:
    #   - sharing one on-disk arrow cache across ranks risks lock contention
    #   - keep_in_memory=True makes EVERY rank hold the whole tokenized set in RAM,
    #     which exhausted host memory on 2x T4 and stalled weight materialization
    # Rank-scoped cache files satisfy both: separate files, no contention, on disk.
    cols = ["input", "output"]
    _rank = os.environ.get("LOCAL_RANK", "0")
    _cdir = run_dir / "tokcache"
    _cdir.mkdir(parents=True, exist_ok=True)

    ds_train = Dataset.from_pandas(train_df[cols], preserve_index=False).map(
        preprocess, batched=True, remove_columns=cols, desc="tokenize train",
        cache_file_name=str(_cdir / f"train_rank{_rank}.arrow"))
    dev_eval_df = dev_df.iloc[: a.eval_subset]
    ds_dev = Dataset.from_pandas(dev_eval_df[cols], preserve_index=False).map(
        preprocess, batched=True, remove_columns=cols, desc="tokenize dev",
        cache_file_name=str(_cdir / f"dev_rank{_rank}.arrow"))

    model = AutoModelForSeq2SeqLM.from_pretrained(a.model)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"\nparameters: {n_params:,} ({n_params/1e6:.1f}M)")
    assert n_params <= 3_000_000_000, f"PARAMETER CAP BREACHED: {n_params:,} > 3B"
    print(f"✅ within 3B cap  (headroom for ensembling: {3_000_000_000 // n_params} copies)")

    # ---------------- metric-driven eval ----------------
    bert_scorer = None if a.no_bertscore_eval else BERTScorer(batch_size=32)
    dev_refs = dev_eval_df["output"].tolist()

    ZERO = {"token_f1": 0.0, "rouge_l": 0.0, "bertscore": 0.0,
            "composite": 0.0, "pred_tokens": 0.0}

    def hf_compute_metrics(eval_pred):
        # NEVER let a metric bug kill a multi-hour run. Trainer evaluates BEFORE it
        # saves, so an exception here destroys the checkpoint too — that cost 1h20m
        # of seed-42 training once already.
        try:
            preds = eval_pred.predictions
            if isinstance(preds, tuple):
                preds = preds[0]
            preds = np.where(preds != -100, preds, tok.pad_token_id)
            decoded = tok.batch_decode(preds, skip_special_tokens=True)

            # Distributed eval PADS the dataset so it divides evenly across ranks, so
            # len(decoded) can EXCEED len(dev_refs): 300 dev rows on 2 GPUs at
            # eval_batch_size 8 -> 19 batches x 8 x 2 = 304 predictions. Truncating
            # refs to len(preds) cannot fix an overshoot; clamp BOTH to the minimum.
            n = min(len(decoded), len(dev_refs))
            if len(decoded) != len(dev_refs):
                print(f"  [eval] DDP padding: {len(decoded)} preds vs {len(dev_refs)} "
                      f"refs -> scoring first {n}", flush=True)
            res = composite_metrics(
                decoded[:n], dev_refs[:n],
                bertscore=not a.no_bertscore_eval, scorer=bert_scorer,
            )
        except Exception as e:
            import traceback
            print(f"⚠️  compute_metrics FAILED: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc()
            print("    returning zeros so training and checkpointing continue.",
                  file=sys.stderr)
            return dict(ZERO)
        return {
            "token_f1": res["token_f1"],
            "rouge_l": res["rouge_l"],
            "bertscore": res["bertscore"] or 0.0,
            "composite": res["composite"],
            "pred_tokens": res["mean_pred_tokens"],
        }

    import transformers
    print(f"transformers {transformers.__version__}")

    targs = dict(
        output_dir=str(run_dir / "ckpt"),
        seed=a.seed,
        num_train_epochs=a.epochs,
        learning_rate=a.lr,
        warmup_steps=a.warmup,
        weight_decay=a.weight_decay,
        label_smoothing_factor=a.label_smoothing,   # 0.0 on purpose — see module docstring
        per_device_train_batch_size=a.batch_size,
        per_device_eval_batch_size=a.eval_batch_size,
        gradient_accumulation_steps=a.grad_accum,
        optim=a.optim,
        group_by_length=a.group_by_length,
        bf16=(precision == "bf16"),
        fp16=(precision == "fp16"),
        gradient_checkpointing=a.grad_checkpointing,
        eval_accumulation_steps=4,   # move logits off-GPU during eval, else they pile up
        predict_with_generate=True,
        generation_num_beams=a.gen_num_beams,
        generation_max_length=a.gen_max_new_tokens,
        eval_steps=a.eval_steps,
        save_strategy="steps",
        save_steps=(a.save_steps or a.eval_steps),
        save_total_limit=(None if a.save_total_limit == 0 else a.save_total_limit),
        load_best_model_at_end=True,
        metric_for_best_model="composite",          # NOT eval_loss — see docstring
        greater_is_better=True,
        logging_steps=100,
        report_to=[],
        dataloader_num_workers=2,
    )
    if a.max_steps:
        # max_steps wins over num_train_epochs in HF Trainer, but leaving epochs at its
        # default also leaves a misleading number in run.json — so make the budget explicit.
        targs["max_steps"] = a.max_steps
    # `evaluation_strategy` was renamed to `eval_strategy` in transformers 4.41.
    # Kaggle images lag, so try the new name and fall back rather than crashing
    # several minutes into a GPU session.
    try:
        args = Seq2SeqTrainingArguments(eval_strategy="steps", **targs)
    except TypeError:
        args = Seq2SeqTrainingArguments(evaluation_strategy="steps", **targs)
    # enforce the measured length floor at generation time
    model.generation_config.min_new_tokens = a.gen_min_new_tokens
    model.generation_config.length_penalty = a.gen_length_penalty

    trainer = Seq2SeqTrainer(
        model=model, args=args,
        train_dataset=ds_train, eval_dataset=ds_dev,
        data_collator=DataCollatorForSeq2Seq(tok, model=model),
        compute_metrics=hf_compute_metrics,
        callbacks=[EarlyStoppingCallback(
            early_stopping_patience=a.early_stopping_patience)],
    )

    print("\n" + "-" * 70)
    print("training — selecting on dev COMPOSITE, not loss")
    print("-" * 70)
    t0 = time.time()
    resume = False
    if a.resume:
        ckpts = sorted((run_dir / "ckpt").glob("checkpoint-*"),
                       key=lambda p: int(p.name.split("-")[-1]))
        resume = bool(ckpts)
        print(f"resume: {ckpts[-1].name if resume else 'no checkpoint yet — fresh start'}")
    trainer.train(resume_from_checkpoint=resume or None)
    mins = (time.time() - t0) / 60

    best = trainer.evaluate()
    final_dir = run_dir / "best"
    trainer.save_model(str(final_dir))
    tok.save_pretrained(str(final_dir))

    record = {
        "run_name": run_name,
        "model": a.model,
        # WHICH input combination this run saw. Seven experiments train on "the winner of
        # Tier 1", so the dataset is a result, not a constant — record it beside the score.
        "data_dir": str(PROC),
        "seed": a.seed,
        "params": n_params,
        "train_rows": len(train_df),
        "epochs": a.epochs,
        "max_steps": a.max_steps,
        "eval_steps": a.eval_steps,
        "early_stopping_patience": a.early_stopping_patience,
        "lr": a.lr,
        "effective_batch": a.batch_size * a.grad_accum,
        "label_smoothing": a.label_smoothing,
        "optim": a.optim,
        "max_source_len": a.max_source_len,
        "max_target_len": a.max_target_len,
        "grad_checkpointing": a.grad_checkpointing,
        "precision": precision,
        "gpu": gpu_name,
        "n_gpu": n_gpu,
        "normalizer": not a.no_normalizer,
        "decoding": {
            "num_beams": a.gen_num_beams,
            "min_new_tokens": a.gen_min_new_tokens,
            "max_new_tokens": a.gen_max_new_tokens,
            "length_penalty": a.gen_length_penalty,
        },
        "dev": {k.replace("eval_", ""): v for k, v in best.items() if k.startswith("eval_")},
        "eval_subset": a.eval_subset,
        "train_minutes": round(mins, 1),
        "checkpoint_hash": sha256_dir(final_dir),
        "versions": {"torch": torch.__version__},
    }
    (run_dir / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"done in {mins:.1f} min — checkpoint: {final_dir}")
    print("=" * 70)
    for k in ["token_f1", "rouge_l", "bertscore", "composite", "pred_tokens"]:
        v = best.get(f"eval_{k}")
        if v is not None:
            print(f"  {k:12s} {v:.4f}")
    if a.smoke:
        # A smoke run is ~30 steps against warmup_steps=1000, so the LR never leaves
        # ~0 and the model does not train. Comparing it to the real bars produced
        # alarming ❌ marks on a run that had actually SUCCEEDED — so don't.
        print("\n  ℹ️  SMOKE RUN — plumbing check only. The score above is meaningless")
        print("     (LR never left warmup). Success here = no crash + checkpoint saved.")
    else:
        f1 = best.get("eval_token_f1")
        if f1 is not None:
            print(f"\n  vs LB constant      TokenF1 0.2669   "
                  f"{'✅' if f1 > 0.2669 else '❌'} {f1 - 0.2669:+.4f}")
            print(f"  vs frequency-only   TokenF1 0.3519   "
                  f"{'✅' if f1 > 0.3519 else '❌'} {f1 - 0.3519:+.4f}   "
                  f"(below this = no better than unigram stats)")
    print(f"\n  checkpoint hash: {record['checkpoint_hash']}")
    print(f"  run record:      {run_dir / 'run.json'}")
    print("\n  ⚠️  Eval above is on a subset with beam search. Re-score the full 5k dev")
    print("      split via 04_decode.py before trusting it or submitting.")
    print("  ⚠️  Append this run to LOCAL_EXPERIMENTS.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
