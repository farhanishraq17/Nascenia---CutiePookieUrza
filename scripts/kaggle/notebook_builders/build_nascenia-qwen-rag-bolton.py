import json
from pathlib import Path

C = []
def md(s): C.append({"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)})
def code(s): C.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                       "source": s.strip("\n").splitlines(keepends=True)})

md(r"""
# X6 — RAG bolted onto the X2 checkpoint, EXPANDED retrieval corpus

**Question:** `Phase2 Final architecture/B_Qwen35_2B` trained X2 (finetune, plain, no retrieval) —
`Qwen/Qwen3.5-2B`, peak Token F1 **0.2641** @ step 3000, clears the 0.1454 bar
(`run_X2.json`, never entered in `RESULTS.md` — filled in as part of this run). This notebook is
**X6** per `EXPERIMENTS.md`: take that checkpoint *as-is, no retraining*, and feed it a retrieved
reference case at decode time only, using the exact `RAG_TEMPLATE` `X3`/`X6` share.

**The one deliberate difference from a plain X6:** the retrieval corpus is **expanded** past the
118,912-row Tier-1 pool `build_index.py` builds. It now also includes the **106,154 leak-safe
`healthcaremagic` rows** (our own translation of ChatDoctor, `router_corpus.parquet` minus every
frozen dev/test id) — **225,066 rows total**, the most data available for this without touching
the frozen split. Rationale: `healthcaremagic` was excluded from the *training* pool because it's
the same cases the competition already gives us — that reasoning does not apply to *retrieval*,
where a topically similar case is still useful grounding even in a different register.

**Bar to beat: Token F1 0.1454. Noise floor 0.0044.** Both baseline (plain, replicated here as a
sanity check against the recorded 0.2641) and X6 are measured in the same run for a clean paired
comparison. **The copy-check matters more than the headline number** — see `EXPERIMENTS.md` §X3.
""")

code(r"""
# 1 -- pinned libs + hardware gate.
# 🔴 transformers==4.57.3 is pinned ELSEWHERE in this project for T5/BanglaT5 stability --
# it does NOT recognize Qwen3.5's architecture (model_type "qwen3_5_text" was added later).
# run_X2.json (the actual training run that produced this checkpoint) records the real
# environment used: transformers 5.14.1. Pin to THAT, not the T5 pin -- copying a pin across
# model families without checking the run record is exactly the mistake this comment exists to
# stop someone repeating.
!pip install -q --upgrade "transformers==5.14.1" accelerate sentencepiece
import transformers, torch, glob, os, re, json, time
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd
assert transformers.__version__ == "5.14.1", transformers.__version__
assert torch.cuda.is_available(), "no GPU"
cap = torch.cuda.get_device_capability()
BF16 = cap[0] >= 8
DTYPE = torch.bfloat16 if BF16 else torch.float32
print(f"{torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} -> {DTYPE}  transformers {transformers.__version__}")
""")

code(r"""
# 2 -- locate inputs. Three dataset sources: the checkpoint+eval bundle, the Tier-1 pool,
# and the healthcaremagic corpus for the expanded index.
CKPT = os.path.dirname(glob.glob("/kaggle/input/**/best/config.json", recursive=True)[0])
DEV_PLAIN = glob.glob("/kaggle/input/**/dev_plain.parquet", recursive=True)[0]
POOL_DIR = os.path.dirname(glob.glob("/kaggle/input/**/nascenia-phase2-pool/train.parquet",
                                     recursive=True)[0]) if glob.glob(
    "/kaggle/input/**/nascenia-phase2-pool/train.parquet", recursive=True) else \
    os.path.dirname(glob.glob("/kaggle/input/**/train.parquet", recursive=True)[0])
ROUTER = glob.glob("/kaggle/input/**/router_corpus.parquet", recursive=True)[0]
print("ckpt      :", CKPT)
print("dev_plain :", DEV_PLAIN)
print("pool_dir  :", POOL_DIR)
print("router    :", ROUTER)
""")

code(r"""
# 3 -- 🔴 FAIL FAST: load the X2 checkpoint FIRST, before the 58-minute pool-embedding step
# below. This is exactly the checkpoint load that crashed the first attempt of this notebook
# on a version mismatch -- if loading ever breaks again (bad path, wrong dtype, cap breach),
# it must break here in seconds, not after an hour of GPU time.
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained(CKPT, trust_remote_code=True)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(CKPT, dtype=DTYPE, trust_remote_code=True).cuda().eval()

n = sum(p.numel() for p in model.parameters())
print(f"parameters: {n:,}")
assert n <= 3_000_000_000, f"3B CAP BREACHED: {n:,}"
print(f"✅ within cap. Combined with champion (247,577,856): {(n + 247_577_856)/1e9:.2f}B "
     f"before the retriever's ~278M")

with torch.no_grad():
    probe = tok("হেলো", return_tensors="pt").to("cuda")
    lg = model(**probe).logits
assert torch.isfinite(lg).all(), "NON-FINITE LOGITS -- wrong dtype"
print("✅ logits finite -- checkpoint loads and runs")
""")

code(r"""
# 4 -- build the EXPANDED pool: Tier-1 (train + icliniq/genmedgpt/doctor_qa_bangla, 118,912)
# + healthcaremagic MINUS every frozen dev/test id (106,154 leak-safe rows). Zero overlap
# between the two halves by construction -- Tier-1 never bundled healthcaremagic at all.
KEEP_SOURCES = ("icliniq", "genmedgpt", "doctor_qa_bangla")

train = pd.read_parquet(f"{POOL_DIR}/train.parquet")[["id", "input", "output"]].copy()
train["source"] = "competition_train"
extra = pd.read_parquet(f"{POOL_DIR}/extra_sources.parquet")
assert not (set(extra["source"]) - set(KEEP_SOURCES)), set(extra["source"])
tier1 = pd.concat([train, extra[["id", "source", "input", "output"]]], ignore_index=True)
tier1 = tier1.dropna(subset=["input", "output"])
tier1 = tier1[tier1["input"].astype(str).str.strip().astype(bool)
             & tier1["output"].astype(str).str.strip().astype(bool)]
print(f"Tier-1 pool: {len(tier1):,} rows  (sources: {dict(tier1['source'].value_counts())})")

dev_full = pd.read_parquet(f"{POOL_DIR}/dev.parquet")
test_full = pd.read_parquet(f"{POOL_DIR}/test.parquet")
dev_ids  = set(dev_full["id"].astype(str))
test_ids = set(test_full["id"].astype(str))
assert not (set(tier1["id"].astype(str)) & (dev_ids | test_ids)), "Tier-1 leaks dev/test"

rc = pd.read_parquet(ROUTER)  # cid, bn_question, bn_answer, en_answer
rc_safe = rc[~rc["cid"].astype(str).isin(dev_ids | test_ids)].copy()
rc_safe = rc_safe.rename(columns={"cid": "id", "bn_question": "input", "bn_answer": "output"})
rc_safe["source"] = "healthcaremagic"
rc_safe = rc_safe[["id", "source", "input", "output"]]
print(f"healthcaremagic (leak-safe): {len(rc_safe):,} rows  "
      f"(dropped {len(rc)-len(rc_safe):,} dev/test-overlapping ids)")

pool = pd.concat([tier1, rc_safe], ignore_index=True).reset_index(drop=True)
assert not (set(pool["id"].astype(str)) & (dev_ids | test_ids)), "🔴 LEAK in combined pool"
print(f"\n✅ EXPANDED pool: {len(pool):,} rows, 0 dev/test leak")
print(pool["source"].value_counts())
""")

code(r"""
# 5 -- embed the expanded pool with the same retriever build_index.py uses.
EMBED_MODEL = "intfloat/multilingual-e5-base"
from transformers import AutoModel, AutoTokenizer
retr_tok = AutoTokenizer.from_pretrained(EMBED_MODEL)
retr_model = AutoModel.from_pretrained(EMBED_MODEL).cuda().eval()
retr_params = sum(p.numel() for p in retr_model.parameters())
print(f"retriever: {EMBED_MODEL}  {retr_params:,} params  "
      f"(counts toward the 3B cap if a RAG arm ships)")

def mean_pool(last_hidden, mask):
    m = mask.unsqueeze(-1).float()
    return (last_hidden * m).sum(1) / m.sum(1).clamp(min=1e-9)

@torch.no_grad()
def embed_texts(texts, prefix, batch_size=128, max_length=256):
    out = []
    for i in range(0, len(texts), batch_size):
        chunk = [prefix + str(t) for t in texts[i:i+batch_size]]
        enc = retr_tok(chunk, padding=True, truncation=True, max_length=max_length,
                       return_tensors="pt").to("cuda")
        emb = mean_pool(retr_model(**enc).last_hidden_state, enc["attention_mask"])
        emb = torch.nn.functional.normalize(emb, p=2, dim=1)
        out.append(emb.cpu().numpy().astype(np.float32))
        if i % (batch_size * 40) == 0: print(f"  embedded {i}/{len(texts)}", flush=True)
    return np.concatenate(out, axis=0)

t0 = time.time()
pool_emb = embed_texts(pool["input"].tolist(), prefix="passage: ")
print(f"pool embeddings: {pool_emb.shape}  ({(time.time()-t0)/60:.1f} min)")
""")

code(r"""
# 6 -- retrieve top-1 for dev[0:300]. sim_ceiling 0.97 matches build_data.py's convention
# (guards against a near-duplicate paraphrase leaking as its own "different" reference);
# no self-exclusion needed -- dev is asserted disjoint from the pool above.
SIM_CEILING = 0.97
dev = pd.read_parquet(DEV_PLAIN).reset_index(drop=True)   # already the frozen dev[0:300], plain schema
assert list(dev.columns[:3]) == ["id", "input", "output"] or {"id","input","output"} <= set(dev.columns)
print(f"dev: {len(dev)} rows")

q_emb = embed_texts(dev["input"].tolist(), prefix="query: ")
sims = q_emb @ pool_emb.T                      # (300, 225066), both L2-normalized -> cosine
sims[sims > SIM_CEILING] = -2.0
top1 = sims.argmax(axis=1)
top1_sim = sims[np.arange(len(dev)), top1]
ref_q = pool["input"].values[top1]
ref_a = pool["output"].values[top1]
ref_src = pool["source"].values[top1]
print(f"mean top-1 similarity: {top1_sim.mean():.4f}   min: {top1_sim.min():.4f}")
print("retrieved-source breakdown:", Counter(ref_src))
""")

code(r"""
# 7 -- build both input variants: plain (X2's own format, sanity-check replication) and
# RAG (X6: X3's exact template, over the expanded pool).
RAG_TEMPLATE = ("অনুরূপ কেস:\nরোগী: {ref_q}\nডাক্তার: {ref_a}\n\n"
                "নতুন রোগীর প্রশ্ন:\n{question}")

plain_inputs = dev["input"].astype(str).tolist()
rag_inputs = [RAG_TEMPLATE.format(ref_q=rq, ref_a=ra, question=q)
             for rq, ra, q in zip(ref_q, ref_a, plain_inputs)]
refs = dev["output"].astype(str).tolist()

print("--- sample RAG input (row 0) ---")
print(rag_inputs[0][:700])
print("\n--- true target (row 0) ---")
print(refs[0][:200])
""")

code(r"""
# 8 -- prompt/generate, exactly reproducing train.ipynb's generate() so this is a true
# bolt-on: same model (loaded in cell 3), same decode config, only the INPUT TEXT differs
# between arms.
print(f"retriever params ({retr_params:,}) + specialist ({n:,}) + champion (247,577,856) = "
      f"{(n + 247_577_856 + retr_params)/1e9:.2f}B")

SYSTEM = ("You are Nascenia Doc (নাসেনিয়া ডক), a professional doctor answering a patient in "
          "Bengali. Reply only in Bengali, with a greeting, clear medical guidance, and a "
          "polite closing.\n\n"
          "আপনি নাসেনিয়া ডক, একজন পেশাদার ডাক্তার। শুধুমাত্র বাংলায় সম্পূর্ণ, সহানুভূতিশীল "
          "উত্তর লিখুন।")

def build_prompt(question):
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": str(question)}]
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

# X2's own config, from run_X2.json: max_src 1024, max_tgt 640, beam search, min_new 0.
MAX_SRC, MAX_TGT, NUM_BEAMS, EVAL_BATCH = 1024, 640, 4, 8

@torch.no_grad()
def generate(texts):
    side = tok.padding_side; tok.padding_side = "left"; out = []
    for i in range(0, len(texts), EVAL_BATCH):
        prompts = [build_prompt(t) for t in texts[i:i+EVAL_BATCH]]
        enc = tok(prompts, return_tensors="pt", padding=True, truncation=True,
                  max_length=MAX_SRC, add_special_tokens=False).to("cuda")
        g = model.generate(**enc, num_beams=NUM_BEAMS, max_new_tokens=MAX_TGT,
                           min_new_tokens=0, length_penalty=1.0, do_sample=False,
                           pad_token_id=tok.pad_token_id)
        out += tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        if i % (EVAL_BATCH*10) == 0: print(f"  {i}/{len(texts)}", flush=True)
    tok.padding_side = side
    return out

def strip_think(t): return re.sub(r"<think>.*?</think>", "", str(t), flags=re.S).strip()
""")

code(r"""
# 9 -- scoring harness, copied from shared/evaluate.py so numbers are directly comparable
# to every other RESULTS.md in this project.
BENGALI = r"[ঀ-৿]+"
TOKEN_RE = re.compile(rf"{BENGALI}|[A-Za-z]+|\d+")
def tokenize(s): return TOKEN_RE.findall(str(s))

def token_f1(pred, ref):
    p, r = Counter(tokenize(pred)), Counter(tokenize(ref))
    ov = sum((p & r).values())
    if not ov: return 0.0
    prec, rec = ov/max(1,sum(p.values())), ov/max(1,sum(r.values()))
    return 2*prec*rec/(prec+rec)

def _lcs(a, b):
    if not a or not b: return 0
    prev = [0]*(len(b)+1)
    for x in a:
        cur = [0]*(len(b)+1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j-1]+1 if x == y else max(prev[j], cur[j-1])
        prev = cur
    return prev[-1]

def rouge_l(pred, ref):
    p, r = tokenize(pred), tokenize(ref)
    if not p or not r: return 0.0
    l = _lcs(p, r)
    if l == 0: return 0.0
    prec, rec = l/len(p), l/len(r)
    return 2*prec*rec/(prec+rec)

def looks_truncated(s):
    s = str(s).strip()
    return bool(s) and s[-1] not in "।?!.।"

REF_HELO_PCT, REF_MEAN_TOKENS, REF_TRUNCATED_PCT, NOISE_FLOOR = 76.4, 100.0, 6.8, 0.0044

def score(preds, refs, ref_examples=None):
    f1s = [token_f1(p, r) for p, r in zip(preds, refs)]
    rls = [rouge_l(p, r) for p, r in zip(preds, refs)]
    toks = [len(tokenize(p)) for p in preds]; n = len(preds)
    out = {"n": n, "token_f1": sum(f1s)/n, "rouge_l": sum(rls)/n,
          "mean_pred_tokens": sum(toks)/n,
          "helo_opener_pct": 100.0*sum(str(p).strip().startswith("হেলো") for p in preds)/n,
          "truncated_pct": 100.0*sum(looks_truncated(p) for p in preds)/n,
          "empty_pct": 100.0*sum(not str(p).strip() for p in preds)/n}
    if ref_examples is not None:
        copy = [token_f1(p, e) for p, e in zip(preds, ref_examples)]
        out["copy_overlap_with_reference"] = sum(copy)/n
        out["copy_margin"] = out["token_f1"] - out["copy_overlap_with_reference"]
    return out

def show(res, name, floor=0.1454):
    d = res["token_f1"] - floor
    verdict = "clears" if d > NOISE_FLOOR else ("inside noise" if abs(d) <= NOISE_FLOOR else "below")
    print(f"\n=== {name} (n={res['n']}) ===")
    print(f"  Token F1 {res['token_f1']:.4f}   ROUGE-L {res['rouge_l']:.4f}   vs floor {floor}: {d:+.4f} ({verdict})")
    print(f"  mean tokens {res['mean_pred_tokens']:.1f} (ref {REF_MEAN_TOKENS})   "
         f"হেলো% {res['helo_opener_pct']:.1f} (ref {REF_HELO_PCT})   "
         f"truncated% {res['truncated_pct']:.1f} (ref {REF_TRUNCATED_PCT})   empty% {res['empty_pct']:.1f}")
    if "copy_margin" in res:
        print(f"  🔴 copy-check: overlap w/ TRUE target {res['token_f1']:.4f}  vs  "
             f"overlap w/ SHOWN reference {res['copy_overlap_with_reference']:.4f}  "
             f"margin {res['copy_margin']:+.4f}")
        print("     margin > 0 -> answering.  margin < 0 -> COPYING the retrieved example, not answering.")
""")

code(r"""
# 10 -- run both arms.
print("Generating: baseline (plain, X2's own format) ...")
plain_preds = [strip_think(p) for p in generate(plain_inputs)]
res_plain = score(plain_preds, refs)
show(res_plain, "BASELINE -- plain input, no RAG (replicates run_X2.json's 0.2641)")

print("\nGenerating: X6 -- RAG bolt-on, expanded 225,066-row corpus ...")
rag_preds = [strip_think(p) for p in generate(rag_inputs)]
res_rag = score(rag_preds, refs, ref_examples=list(ref_a))
show(res_rag, "X6 -- RAG bolt-on (expanded corpus)")
""")

code(r"""
# 11 -- verdict, per EXPERIMENTS.md's X6 outcome table.
d = res_rag["token_f1"] - res_plain["token_f1"]
print("="*70)
print(f"Token F1   plain={res_plain['token_f1']:.4f}   X6(RAG)={res_rag['token_f1']:.4f}   delta={d:+.4f}")
print(f"ROUGE-L    plain={res_plain['rouge_l']:.4f}   X6(RAG)={res_rag['rouge_l']:.4f}   "
     f"delta={res_rag['rouge_l']-res_plain['rouge_l']:+.4f}")
print(f"copy_margin (X6): {res_rag['copy_margin']:+.4f}  "
     f"({'answering' if res_rag['copy_margin']>0 else 'COPYING -- arm has failed regardless of F1'})")
print()
if abs(d) <= NOISE_FLOOR:
    print("~ X2: RAG doesn't need to be trained in for this checkpoint to at least not be hurt by it --")
    print("  bolt-on is enough, no retrain required to ship retrieval.")
elif d < -NOISE_FLOOR:
    print("<< X2: the extra context actively hurts an unprepared model -- clean negative.")
    print("  Do not ship bolt-on RAG with this checkpoint. If RAG is still worth pursuing,")
    print("  it must be TRAINED IN (X3), not bolted on.")
else:
    print(">> X2: RAG bolted on even without training helps. Worth also running X3")
    print("  (trained-in RAG) since X3 typically beats X6 when the model has never seen")
    print("  retrieved context during training.")
print("="*70)

# save for RESULTS.md
Path("x6_result.json").write_text(json.dumps({
    "arm": "X6", "model": "Qwen/Qwen3.5-2B (X2 checkpoint, no retrain)",
    "retrieval_corpus_rows": int(len(pool)),
    "retriever": EMBED_MODEL, "retriever_params": int(retr_params),
    "sim_ceiling": SIM_CEILING, "mean_top1_sim": float(top1_sim.mean()),
    "baseline_plain": {k: v for k, v in res_plain.items()},
    "x6_rag": {k: v for k, v in res_rag.items()},
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n✅ wrote x6_result.json")
""")

nb = {"cells": C, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
      "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}

Path("nascenia-qwen-rag-bolton.ipynb").write_text(
    json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote nascenia-qwen-rag-bolton.ipynb  ({len(C)} cells)")
