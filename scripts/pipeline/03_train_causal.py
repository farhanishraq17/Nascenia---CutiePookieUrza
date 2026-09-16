"""03_train_causal.py — decoder-only counterpart to 02_train_t5.py, for E18's model zoo.

`02_train_t5.py` is seq2seq-only. E18 asks whether a decoder beats BanglaT5 on this task —
the NLP4Health shared task, run under the same <3B cap on Indic medical dialogue, found
decoders beating encoder-decoders — and that question cannot be answered without this.

WHAT IS DELIBERATELY THE SAME AS 02_train_t5.py, so the comparison is honest
  * the frozen seed-42 / 5,000-row split, read from the same --data-dir parquet
  * effective batch 64, eval on the same 300 dev rows, every 250 steps
  * selection on dev COMPOSITE, never eval_loss
  * bf16 on sm_80+, fp32 below, 🔴 never fp16
  * run.json written beside the weights

WHAT MUST DIFFER, and why each one is load-bearing
  * LR ~2e-5, not BanglaT5's 1e-3. Decoder fine-tuning wants ~50x lower; carrying 1e-3
    across diverges and the run reads as "bad model" when it is a broken run.
  * Instruction format + loss masked on the prompt, so only answer tokens train.
  * LEFT padding for generation. Right-padding puts pad tokens between the prompt and the
    first generated token; the output is garbage that still decodes cleanly — a silent
    failure that also scores as "bad model".
  * Qwen3 needs enable_thinking=False: register transfer is not a reasoning task and
    <think> blocks would have to be stripped out of every prediction.
  * Generation eval runs in a callback rather than through Seq2SeqTrainer, because HF's
    eval path assumes right-padded seq2seq batches.
"""

from __future__ import annotations

import argparse
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

INSTRUCTION = "Rewrite this Bengali draft in the target register."
# ^ default, used by E18. Override with --instruction for tasks that aren't register transfer
#   (e.g. E25's Phase 2 specialist, which answers from a retrieved reference case, not a draft).


def get_normalizer(enabled: bool):
    if not enabled:
        return lambda s: s
    try:
        from normalizer import normalize  # type: ignore
        return lambda s: normalize(str(s))
    except ImportError:
        print("⚠️  csebuetnlp `normalizer` not installed — continuing unnormalized.",
              file=sys.stderr)
        return lambda s: str(s)


def set_seed(seed: int):
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_prompt(tok, draft: str) -> str:
    """Chat-templated prompt. enable_thinking=False for Qwen3; harmless elsewhere."""
    msgs = [{"role": "user", "content": f"{INSTRUCTION}\n\n{draft}"}]
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    except Exception:
        # Base models without a chat template: a plain, explicit framing.
        return f"{INSTRUCTION}\n\n{draft}\n\nAnswer:\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="decoder-only register-transfer fine-tune")
    ap.add_argument("--model", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--instruction", default=None,
                    help="overrides the module-level INSTRUCTION constant")
    ap.add_argument("--out-dir", "--out", dest="out_dir", default=".")
    ap.add_argument("--run-name", default=None)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--warmup", type=int, default=200)
    ap.add_argument("--weight-decay", type=float, default=0.0)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--eval-batch-size", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=1024,
                    help="total prompt+answer cap (EXPERIMENT.md: 1024 for decoders)")
    ap.add_argument("--max-new-tokens", type=int, default=320)
    ap.add_argument("--min-new-tokens", type=int, default=80)
    ap.add_argument("--num-beams", type=int, default=4)
    ap.add_argument("--eval-subset", type=int, default=300)
    ap.add_argument("--eval-steps", type=int, default=250)
    ap.add_argument("--max-steps", type=int, default=4000)
    ap.add_argument("--early-stopping-patience", type=int, default=5)
    ap.add_argument("--precision", default="auto", choices=["auto", "fp32", "bf16"])
    ap.add_argument("--grad-checkpointing", action="store_true")
    # AdamW keeps fp32 m+v: ~12 bytes/param, which is 31 GB for a 2.6B model before a
    # single activation. Adafactor factors the second moment and fits the same model on
    # a 24 GB card. It is also T5's canonical optimizer, so it is not an exotic choice.
    ap.add_argument("--optim", default="adamw_torch")
    ap.add_argument("--no-normalizer", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(argv)

    global INSTRUCTION
    if a.instruction:
        INSTRUCTION = a.instruction

    if a.smoke:
        a.max_steps, a.eval_steps, a.eval_subset = 20, 10, 32

    import torch
    from torch.utils.data import Dataset as TorchDataset
    from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                              TrainingArguments, TrainerCallback)
    from metric import compute_metrics as composite_metrics

    # 🔴 FAIL FAST ON A DEAD GPU. torch falls back to CPU silently: no error, a tqdm bar
    # that advances, and a run that would finish in about a month. That is exactly what
    # happened on grn008, whose faulty GPU4 leaves the whole node at
    # `torch.cuda.device_count() == 0` — three arms sat "training" on CPU before the
    # 0 MiB VRAM reading gave it away. A run without a GPU is never what was intended.
    assert torch.cuda.is_available(), (
        "❌ no CUDA device visible — refusing to train on CPU. "
        "Check the node's GPUs (`nvidia-smi`) and CUDA_VISIBLE_DEVICES; on a shared "
        "allocation, export it INSIDE the srun step, not via --export.")

    set_seed(a.seed)
    run_name = a.run_name or Path(a.model).name
    run_dir = Path(a.out_dir) / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    cap = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else (0, 0)
    # 🔴 capability, NOT is_bf16_supported() — that returns True on a T4 via emulation.
    bf16_ok = torch.cuda.is_available() and cap[0] >= 8
    precision = ("bf16" if bf16_ok else "fp32") if a.precision == "auto" else a.precision
    if precision == "bf16" and not bf16_ok:
        precision = "fp32"
    dtype = torch.bfloat16 if precision == "bf16" else torch.float32

    print("=" * 70)
    print(f"decoder fine-tune — {run_name}   model={a.model}")
    print(f"sm_{cap[0]}{cap[1]}  precision={precision}  "
          f"effective batch = {a.batch_size} x {a.grad_accum} = {a.batch_size * a.grad_accum}")
    print("=" * 70, flush=True)

    proc = Path(a.data_dir)
    train_df = pd.read_parquet(proc / "train.parquet")
    dev_df = pd.read_parquet(proc / "dev.parquet").iloc[: a.eval_subset]
    norm = get_normalizer(not a.no_normalizer)

    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    eos = tok.eos_token or ""

    class PromptAnswerDS(TorchDataset):
        """Tokenize lazily: the zoo's tokenizers differ, and 108k rows x 7 arms of
        pre-tokenized cache is pure waste when the collator pads per batch anyway."""

        def __init__(self, df):
            self.src = [norm(x) for x in df["input"].tolist()]
            self.tgt = [norm(x) for x in df["output"].tolist()]

        def __len__(self):
            return len(self.src)

        def __getitem__(self, i):
            prompt = build_prompt(tok, self.src[i])
            p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
            a_ids = tok(self.tgt[i] + eos, add_special_tokens=False)["input_ids"]
            # Truncate the PROMPT first: the answer is what we are scored on, so losing
            # answer tokens would train the model to stop early.
            room = a.max_len - len(a_ids)
            if room < 16:
                a_ids = a_ids[: a.max_len - 16]
                room = 16
            p_ids = p_ids[-room:]
            ids = p_ids + a_ids
            labels = [-100] * len(p_ids) + list(a_ids)   # loss on the answer only
            return {"input_ids": ids, "labels": labels}

    def collate(batch):
        n = max(len(b["input_ids"]) for b in batch)
        pad = tok.pad_token_id
        out = {"input_ids": [], "attention_mask": [], "labels": []}
        for b in batch:                                   # right-pad for TRAINING only
            k = n - len(b["input_ids"])
            out["input_ids"].append(b["input_ids"] + [pad] * k)
            out["attention_mask"].append([1] * len(b["input_ids"]) + [0] * k)
            out["labels"].append(b["labels"] + [-100] * k)
        return {k: torch.tensor(v, dtype=torch.long) for k, v in out.items()}

    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=dtype,
                                                 trust_remote_code=True)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"parameters: {n_params:,} ({n_params/1e9:.3f}B)")
    assert n_params <= 3_000_000_000, f"PARAMETER CAP BREACHED: {n_params:,} > 3B"
    print(f"✅ within the 3B cap", flush=True)
    if a.grad_checkpointing:
        model.gradient_checkpointing_enable()
        model.config.use_cache = False

    dev_prompts = [build_prompt(tok, norm(x)) for x in dev_df["input"].tolist()]
    dev_refs = dev_df["output"].tolist()

    # 🔴 LENGTH GUARD. Generation caps are in SUBWORD tokens, and the subword cost of one
    # Bengali answer is wildly tokenizer-dependent: BanglaT5 needs ~142, Qwen ~689 — 4.8x.
    # Carrying BanglaT5's --max-new-tokens 320 across caps Qwen at ~46 metric words against
    # a ~100-word reference, and the run scores ~0.48 while looking completely healthy.
    # That already happened once here. Fail loudly instead.
    tgt_lens = sorted(len(tok(r, add_special_tokens=False)["input_ids"])
                      for r in dev_refs)
    p95 = tgt_lens[int(0.95 * len(tgt_lens))]
    med = tgt_lens[len(tgt_lens) // 2]
    print(f"target length in THIS tokenizer: median {med}, p95 {p95} subword tokens")
    assert a.max_new_tokens >= p95, (
        f"❌ --max-new-tokens {a.max_new_tokens} < p95 target length {p95} for "
        f"{a.model}. The model would be cut off mid-answer on 5%+ of rows and the score "
        f"would measure the cap, not the model. Raise it to at least {p95}.")
    if a.min_new_tokens > med:
        print(f"⚠️  --min-new-tokens {a.min_new_tokens} exceeds the median target "
              f"({med}) — forcing over-long answers.", file=sys.stderr)
    if a.max_len < p95 * 2:
        print(f"⚠️  --max-len {a.max_len} leaves little room for prompt+answer when the "
              f"answer alone reaches {p95} tokens; the prompt is being truncated.",
              file=sys.stderr)

    @torch.no_grad()
    def generate_dev(m) -> list[str]:
        """🔴 LEFT-pad here. Right padding inserts pads between prompt and continuation
        and yields fluent-looking garbage — a silent failure that scores as a bad model."""
        m.eval()
        side = tok.padding_side
        tok.padding_side = "left"
        preds = []
        for i in range(0, len(dev_prompts), a.eval_batch_size):
            chunk = dev_prompts[i: i + a.eval_batch_size]
            enc = tok(chunk, return_tensors="pt", padding=True,
                      add_special_tokens=False).to(m.device)
            out = m.generate(**enc, num_beams=a.num_beams,
                             min_new_tokens=a.min_new_tokens,
                             max_new_tokens=a.max_new_tokens,
                             length_penalty=1.0, do_sample=False,
                             pad_token_id=tok.pad_token_id)
            gen = out[:, enc["input_ids"].shape[1]:]       # continuation only
            preds += tok.batch_decode(gen, skip_special_tokens=True)
        tok.padding_side = side
        m.train()
        return preds

    history, best = [], {"composite": -1.0, "step": -1}

    class GenEval(TrainerCallback):
        """HF's eval path assumes right-padded seq2seq batches, so generation eval,
        best-checkpoint selection and early stopping all live here instead."""

        def __init__(self):
            self.bad = 0

        def on_step_end(self, args, state, control, model=None, **kw):
            if state.global_step == 0 or state.global_step % a.eval_steps:
                return control
            t = time.time()
            preds = generate_dev(model)
            res = composite_metrics(preds, dev_refs, bertscore=False)
            rec = {"step": state.global_step,
                   "token_f1": round(res["token_f1"], 5),
                   "rouge_l": round(res["rouge_l"], 5),
                   "composite": round(res["composite"], 5),
                   "pred_tokens": round(res["mean_pred_tokens"], 1),
                   "secs": round(time.time() - t, 1)}
            history.append(rec)
            print(f"  [eval] step {rec['step']:6d}  TokenF1 {rec['token_f1']:.4f}  "
                  f"ROUGE-L {rec['rouge_l']:.4f}  tokens {rec['pred_tokens']:.0f}  "
                  f"({rec['secs']:.0f}s)", flush=True)
            (run_dir / "trainer_state.json").write_text(
                json.dumps({"log_history": history, "best": best}, indent=2))
            # Selection is on the composite, never eval_loss.
            if res["composite"] > best["composite"]:
                best.update(composite=res["composite"], step=state.global_step,
                            token_f1=res["token_f1"], rouge_l=res["rouge_l"])
                model.save_pretrained(run_dir / "best", safe_serialization=True)
                tok.save_pretrained(run_dir / "best")
                self.bad = 0
                print(f"         ✅ new best -> {run_dir/'best'}", flush=True)
            else:
                self.bad += 1
                if self.bad >= a.early_stopping_patience:
                    print(f"         early stop: {self.bad} evals without improvement")
                    control.should_training_stop = True
            return control

    targs = TrainingArguments(
        output_dir=str(run_dir / "ckpt"),
        seed=a.seed,
        max_steps=a.max_steps,
        learning_rate=a.lr,
        warmup_steps=a.warmup,
        weight_decay=a.weight_decay,
        per_device_train_batch_size=a.batch_size,
        gradient_accumulation_steps=a.grad_accum,
        bf16=(precision == "bf16"),
        fp16=False,                      # 🔴 never — see the module docstring
        optim=a.optim,
        logging_steps=50,
        save_strategy="no",              # the GenEval callback owns best/
        report_to=[],
        dataloader_num_workers=2,
        gradient_checkpointing=a.grad_checkpointing,
        lr_scheduler_type="cosine",
    )
    trainer = Trainer(model=model, args=targs, train_dataset=PromptAnswerDS(train_df),
                      data_collator=collate, callbacks=[GenEval()])

    t0 = time.time()
    trainer.train()
    mins = (time.time() - t0) / 60

    if best["step"] < 0:                 # never improved (e.g. a 20-step smoke run)
        model.save_pretrained(run_dir / "best", safe_serialization=True)
        tok.save_pretrained(run_dir / "best")

    record = {
        "run_name": run_name, "model": a.model, "data_dir": str(proc),
        "seed": a.seed, "params": n_params,
        "train_rows": len(train_df), "max_steps": a.max_steps, "lr": a.lr,
        "effective_batch": a.batch_size * a.grad_accum, "max_len": a.max_len,
        "precision": precision, "gpu": torch.cuda.get_device_name(0),
        "normalizer": not a.no_normalizer, "eval_subset": a.eval_subset,
        "eval_steps": a.eval_steps, "architecture": "decoder-only",
        "optim": a.optim,
        "decoding": {"num_beams": a.num_beams, "min_new_tokens": a.min_new_tokens,
                     "max_new_tokens": a.max_new_tokens, "length_penalty": 1.0},
        "best": best, "trajectory": history, "train_minutes": round(mins, 1),
        "versions": {"torch": torch.__version__},
    }
    (run_dir / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("\n" + "=" * 70)
    print(f"done in {mins:.1f} min — best step {best['step']} "
          f"TokenF1 {best.get('token_f1')} ROUGE-L {best.get('rouge_l')}")
    print(f"checkpoint: {run_dir/'best'}   record: {run_dir/'run.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
