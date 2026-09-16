#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E17 — translate the probe set with a local open-weights model.

One script, three model families. Same rows, same prompt, greedy decoding, so the
only variable is the model.

    # LLM via vLLM (Qwen3, Qwen2.5, Llama, Gemma, Aya ...)
    python run_local_models.py --family vllm --model Qwen/Qwen3-235B-A22B --tag qwen3_235b \
        --tensor-parallel 8

    # Dedicated EN->BN MT (IndicTrans2 — the strongest open EN->BN system)
    python run_local_models.py --family indictrans2 --model ai4bharat/indictrans2-en-indic-1B \
        --tag indictrans2

    # Dedicated multilingual MT (NLLB-200)
    python run_local_models.py --family nllb --model facebook/nllb-200-3.3B --tag nllb33b

Writes <tag>_TRANSLATED.csv with columns hcm_id,bengali — the format score_all.py reads.
Asserts rows-in == rows-out, because a dropped row silently breaks the id alignment
that the entire approach rests on.
"""
import argparse, os, re, sys, time
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# The same instruction every LLM candidate gets. Do not tune per model — a prompt
# advantage is not a model advantage, and we are comparing models.
PROMPT = (
    "Translate this English doctor's reply into Bengali.\n\n"
    "Rules:\n"
    "- Faithful, plain, sentence-by-sentence. Do NOT improve, polish, shorten, "
    "expand, restructure, or fix the author's grammar.\n"
    "- Keep medical abbreviations in Latin script (PCOD, LH/FSH, CA 125, MRI, PFT).\n"
    "- Do NOT add a greeting, sign-off, branding, or any commentary.\n"
    "- Output ONLY the Bengali translation, nothing else.\n\n"
    "English:\n{en}\n\nBengali:"
)

# IndicTrans2 / NLLB are sentence-level systems. Feeding them a 108-word paragraph
# degrades output badly, so split, translate, and rejoin.
_SENT = re.compile(r"(?<=[.!?])\s+")


def sentences(text: str) -> list[str]:
    parts = [s.strip() for s in _SENT.split(str(text).strip()) if s.strip()]
    return parts or [str(text).strip() or "."]


# ───────────────────────────────────────────────────────── vLLM (decoder LLMs)
def run_vllm(rows, a):
    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    llm = LLM(
        model=a.model,
        tensor_parallel_size=a.tensor_parallel,
        max_model_len=a.max_model_len,
        gpu_memory_utilization=a.gpu_mem,
        trust_remote_code=True,
        dtype="bfloat16",
    )
    prompts = []
    for en in rows["english"]:
        msgs = [{"role": "user", "content": PROMPT.format(en=en)}]
        kw = {}
        # Qwen3 defaults to thinking mode; translation does not need it and it
        # wraps the answer in <think> blocks we would have to strip.
        if "qwen3" in a.model.lower():
            kw["enable_thinking"] = False
        prompts.append(
            tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw)
        )
    out = llm.generate(
        prompts,
        SamplingParams(temperature=0.0, top_p=1.0, max_tokens=a.max_new_tokens, seed=0),
    )
    return [o.outputs[0].text.strip() for o in out]


# ─────────────────────────────────────────────── IndicTrans2 (EN -> Indic MT)
def run_indictrans2(rows, a):
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    try:
        from IndicTransToolkit.processor import IndicProcessor
    except ImportError:
        sys.exit("pip install git+https://github.com/VarunGumma/IndicTransToolkit.git")

    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        a.model, trust_remote_code=True, torch_dtype=torch.bfloat16
    ).to("cuda").eval()
    ip = IndicProcessor(inference=True)

    flat, owner = [], []
    for i, en in enumerate(rows["english"]):
        for s in sentences(en):
            flat.append(s); owner.append(i)

    pieces = []
    for i in range(0, len(flat), a.batch_size):
        chunk = ip.preprocess_batch(flat[i:i + a.batch_size], src_lang="eng_Latn", tgt_lang="ben_Beng")
        enc = tok(chunk, truncation=True, padding="longest", return_tensors="pt").to("cuda")
        with torch.no_grad():
            gen = model.generate(**enc, num_beams=5, max_length=512, num_return_sequences=1)
        dec = tok.batch_decode(gen, skip_special_tokens=True)
        pieces += ip.postprocess_batch(dec, lang="ben_Beng")
        print(f"  {min(i + a.batch_size, len(flat))}/{len(flat)} sentences", flush=True)

    joined = [[] for _ in range(len(rows))]
    for o, p in zip(owner, pieces):
        joined[o].append(p)
    return [" ".join(x) for x in joined]


# ──────────────────────────────────────────────────── NLLB-200 (multilingual MT)
def run_nllb(rows, a):
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.model, src_lang="eng_Latn")
    model = AutoModelForSeq2SeqLM.from_pretrained(a.model, torch_dtype=torch.bfloat16).to("cuda").eval()
    bos = tok.convert_tokens_to_ids("ben_Beng")

    flat, owner = [], []
    for i, en in enumerate(rows["english"]):
        for s in sentences(en):
            flat.append(s); owner.append(i)

    pieces = []
    for i in range(0, len(flat), a.batch_size):
        enc = tok(flat[i:i + a.batch_size], truncation=True, max_length=256,
                  padding=True, return_tensors="pt").to("cuda")
        with torch.no_grad():
            gen = model.generate(**enc, forced_bos_token_id=bos, num_beams=5, max_length=512)
        pieces += tok.batch_decode(gen, skip_special_tokens=True)
        print(f"  {min(i + a.batch_size, len(flat))}/{len(flat)} sentences", flush=True)

    joined = [[] for _ in range(len(rows))]
    for o, p in zip(owner, pieces):
        joined[o].append(p)
    return [" ".join(x) for x in joined]


RUNNERS = {"vllm": run_vllm, "indictrans2": run_indictrans2, "nllb": run_nllb}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True, choices=list(RUNNERS))
    p.add_argument("--model", required=True)
    p.add_argument("--tag", required=True, help="output prefix, e.g. qwen3_235b")
    p.add_argument("--input", default="PROBE_200_dev.csv")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--tensor-parallel", type=int, default=1)
    p.add_argument("--max-model-len", type=int, default=4096)
    p.add_argument("--gpu-mem", type=float, default=0.90)
    p.add_argument("--max-new-tokens", type=int, default=1024)
    p.add_argument("--batch-size", type=int, default=32)
    a = p.parse_args()

    rows = pd.read_csv(a.input)
    if a.limit:
        rows = rows.head(a.limit)
    print(f"{a.tag}: {len(rows)} rows | {a.family} | {a.model}", flush=True)

    t0 = time.time()
    bn = RUNNERS[a.family](rows, a)
    mins = (time.time() - t0) / 60

    assert len(bn) == len(rows), f"❌ {len(bn)} outputs for {len(rows)} rows — id alignment broken"
    blank = sum(1 for x in bn if not str(x).strip())
    assert blank == 0, f"❌ {blank} empty translations"

    out = f"{a.tag}_TRANSLATED.csv"
    pd.DataFrame({"hcm_id": rows["hcm_id"].values, "bengali": bn}).to_csv(
        out, index=False, encoding="utf-8"
    )
    print(f"\n✅ {out} | {mins:.1f} min | {mins * 60 / len(rows):.2f} s/row")
    print(f"   full-set projection: {mins / len(rows) * 107737 / 60:.1f} GPU-hours")
