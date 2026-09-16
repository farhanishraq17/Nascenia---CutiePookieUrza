#!/usr/bin/env python
"""bundle_decode.py — one branch of the Phase 2 routed pipeline. Called twice by run_bundle.sh,
once per conda env, because the two branches need different transformers versions.

    P2_MODE=champion|specialist  P2_CKPT=...  P2_ROWS=<parquet id,input>  P2_OUT=<json>

Deliberately NOT shared with logs/decode.py: that one keys "is this seq2seq?" off the model
directory name and has no normalizer, both of which are wrong for the champion branch. The two
branches differ in four ways that each silently corrupt the output if crossed over:

              architecture   dtype   input text            decode
  champion    seq2seq        fp32    csebuetnlp-normalized beam 8, lp 1.2, src 768, new 320
  specialist  causal         bf16    raw                   beam 4, lp 1.0, src 1024, new 640

  fp32 for the champion: bf16 decoded 280/1000 rows differently, because beam-8 is decided by
  small margins, and rules §5.2 requires reproducing the submitted outputs.
  bf16 + raw for the specialist: every B/C number in this project was measured that way, and
  build_data.py never runs the normalizer, so normalizing would be a train/test mismatch.
"""
import json
import os
import re

import pandas as pd
import torch

MODE = os.environ["P2_MODE"]
CKPT = os.environ["P2_CKPT"]
ROWS = os.environ["P2_ROWS"]
OUT = os.environ["P2_OUT"]
BEAMS = int(os.environ.get("P2_BEAMS", 4))
LP = float(os.environ.get("P2_LP", 1.0))
MAX_SRC = int(os.environ.get("P2_MAX_SRC", 1024))
MAX_NEW = int(os.environ.get("P2_MAX_NEW", 640))
BS = int(os.environ.get("P2_BATCH", 8))
assert MODE in ("champion", "specialist"), MODE

SEQ2SEQ = MODE == "champion"
cap = torch.cuda.get_device_capability()
# 🔴 never fp16: T5 overflows to NaN silently and still writes a well-formed CSV of garbage.
DTYPE = torch.float32 if SEQ2SEQ else (torch.bfloat16 if cap[0] >= 8 else torch.float32)

if SEQ2SEQ:
    try:
        from normalizer import normalize          # csebuetnlp, matches the champion's training prep
        norm = lambda s: normalize(str(s))
        print("normalizer: csebuetnlp (matches champion training)")
    except ImportError:
        raise SystemExit("🔴 csebuetnlp normalizer missing — the champion branch REQUIRES it; "
                         "omitting it left 16/1000 rows differing from the scored CSV")
else:
    norm = str                                    # specialist saw raw text in training

from transformers import (AutoModelForCausalLM, AutoModelForSeq2SeqLM,  # noqa: E402
                          AutoTokenizer)

tok = AutoTokenizer.from_pretrained(CKPT, trust_remote_code=True)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
Cls = AutoModelForSeq2SeqLM if SEQ2SEQ else AutoModelForCausalLM
model = Cls.from_pretrained(CKPT, dtype=DTYPE, trust_remote_code=True).cuda().eval()
n = sum(p.numel() for p in model.parameters())
print(f"{MODE}: {n:,} params  {str(DTYPE).replace('torch.', '')}  {torch.cuda.get_device_name(0)}")

with torch.no_grad():                             # the only check that ever caught an fp16 NaN
    enc = tok("হেলো", return_tensors="pt").to("cuda")
    lg = (model(**enc, decoder_input_ids=torch.zeros((1, 1), dtype=torch.long, device="cuda"))
          if SEQ2SEQ else model(**enc)).logits
assert torch.isfinite(lg).all(), "🔴 NON-FINITE LOGITS — wrong dtype"

SYSTEM = ("You are Nascenia Doc (নাসেনিয়া ডক), a professional doctor answering a patient in "
          "Bengali. Reply only in Bengali, with a greeting, clear medical guidance, and a "
          "polite closing.\n\n"
          "আপনি নাসেনিয়া ডক, একজন পেশাদার ডাক্তার। শুধুমাত্র বাংলায় সম্পূর্ণ, সহানুভূতিশীল "
          "উত্তর লিখুন।")


def prompt(q):
    if SEQ2SEQ:
        return norm(q)                            # champion consumes the draft text directly
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": str(q)}]
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                      enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


@torch.no_grad()
def run(texts):
    out, side = [], tok.padding_side
    if not SEQ2SEQ:
        tok.padding_side = "left"   # right padding inserts pads between prompt and continuation
    for i in range(0, len(texts), BS):
        enc = tok([prompt(t) for t in texts[i:i + BS]], return_tensors="pt", padding=True,
                  truncation=True, max_length=MAX_SRC,
                  add_special_tokens=SEQ2SEQ).to("cuda")
        torch.manual_seed(42)                     # the champion's decode seeds before each batch
        g = model.generate(**enc, num_beams=BEAMS, length_penalty=LP, min_new_tokens=0,
                           max_new_tokens=MAX_NEW, do_sample=False,
                           pad_token_id=tok.pad_token_id)
        if not SEQ2SEQ:
            g = g[:, enc["input_ids"].shape[1]:]  # drop the prompt back off
        dec = tok.batch_decode(g, skip_special_tokens=True)
        out += dec if SEQ2SEQ else [re.sub(r"<think>.*?</think>", "", x, flags=re.S).strip()
                                    for x in dec]
        print(f"  {min(i + BS, len(texts))}/{len(texts)}", flush=True)
    tok.padding_side = side
    return out


df = pd.read_parquet(ROWS)
preds = run(df["input"].tolist())
assert len(preds) == len(df)
json.dump({"mode": MODE, "ckpt": CKPT, "beams": BEAMS, "lp": LP, "max_src": MAX_SRC,
           "max_new": MAX_NEW, "dtype": str(DTYPE), "params": int(n),
           "ids": [str(x) for x in df["id"].tolist()], "preds": preds},
          open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"wrote {OUT}  ({len(preds)} rows)")
