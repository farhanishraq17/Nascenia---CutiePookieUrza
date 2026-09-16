# E17 — which translators to actually test

Current standings on the same 10 rows (paired, so row difficulty cancels):

| Translator | Token F1 | vs Google | t | wins |
|---|---|---|---|---|
| **Claude (Opus 5)** | **0.6947** | **+0.0717** | 4.38 | 10/10 |
| Codex (GPT-5) | 0.6483 | +0.0253 | 1.34 | 6/10 |
| Google Translate *(current draft)* | 0.6230 | — | — | — |

---

## 🔴 The finding that changes the plan

**The organizers did not use Google Translate.** If they had, our Google draft would score
~0.95 against their text, not **0.6230**. And an LLM — Claude — lands *closer to their
translator than Google Translate does*.

This retires a caution I raised earlier. I argued the target looked like plain machine output
(76.4% `হেলো` openers, mechanical boilerplate) and therefore a *better* translator would land
*further* away. **The data says otherwise**: the target's fingerprint is more LLM-like than
Google-like. Testing strong LLMs is the right call, and the register evidence was measuring
their post-processing, not their translator.

---

## Corrections to the Qwen shortlist

Three of the four proposed models need adjusting before spending GPU time.

### ✅ `Qwen/Qwen3-235B-A22B` — **the right Qwen to test**

This is the one worth running, and it was the Kaggle link rather than the #1 pick.

**Qwen3 expanded to 119 languages and dialects, and Bengali is among them.** MoE: 235B total,
**22B active**, so it generates at roughly 22B-dense speed on a big node.

⚠️ **Qwen3 defaults to thinking mode.** Translation does not need it, and it wraps output in
`<think>` blocks you would have to strip. `run_local_models.py` passes
`enable_thinking=False` automatically for any model with `qwen3` in the name.

### ⚠️ `Qwen/Qwen2.5-72B-Instruct` — **Bengali is the open question, not the size**

Ranked #1 in the brief on the strength of "29+ languages including Bengali." **Qwen2.5's
headline language list is Chinese, English, French, Spanish, Portuguese, German, Italian,
Russian, Japanese, Korean, Vietnamese, Thai, Arabic and others — I do not believe Bengali is
in it.** Qwen3's 119-language list is where Bengali is explicit.

Worth running as a **control** — it is cheap and settles the question empirically — but expect
Qwen3 to beat it on Bengali specifically, which is the opposite of the brief's ranking.

### ❌ `Qwen/Qwen3-Coder-480B-A35B-Instruct` — **skip this one**

The brief says the "Coder" designation shouldn't fool us because large code models excel at
"structured reasoning and preserving exact document formats."

That is true and **not what this task needs.** Our output is **Bengali prose** — there is no
structure to preserve. A code-specialized post-train reallocates capacity toward code and
English at the expense of multilingual prose generation, which is the single thing we are
measuring. Format preservation is handled by the CSV harness, not the model.

**Run `Qwen3-235B-A22B` instead** — same family, same generation, general-purpose post-train,
and *smaller*. If you want the Coder model tested anyway it costs one command, but I would
spend the slot elsewhere.

### ❌ `Qwen/Qwen1.5-110B-Chat` — **skip; superseded**

Qwen1.5 is early-2024 and its multilingual coverage is far weaker than 2.5, let alone 3.
Parameter count does not compensate for a generation gap in language coverage — Bengali was
not a target language for that release. 110B dense is also the most expensive thing on the
list to serve, for the weakest expected Bengali.

---

## 🥇 The category the shortlist is missing: dedicated EN→BN MT

All four proposals are general LLMs. The strongest **open-weights English→Bengali** systems are
purpose-built translation models, and they are *far* cheaper to run:

| Model | Params | Why it belongs in this test |
|---|---|---|
| **`ai4bharat/indictrans2-en-indic-1B`** | 1B | Purpose-built for 22 Indic languages. Generally SOTA open EN→BN. **1B — cheaper than everything else here by two orders of magnitude.** |
| **`facebook/nllb-200-3.3B`** | 3.3B | 200 languages, native `ben_Beng`. The standard multilingual MT baseline. |

Two reasons these matter beyond quality:

1. **They may match the target's fingerprint better than any LLM.** The target is *someone's
   translation system*. If it was an MT model rather than an LLM, an MT model will land closer —
   and that is exactly the hypothesis Claude-beats-Google leaves open.
2. **They make the full run nearly free.** IndicTrans2 at 1B translates 107,737 rows in a
   fraction of the time a 235B MoE needs.

⚠️ Both are **sentence-level** systems — feeding them a 108-word paragraph degrades output
badly. `run_local_models.py` splits into sentences, translates, and rejoins.

---

## Run order

Everything writes `<tag>_TRANSLATED.csv`; `score_all.py` picks up whatever is present.

```bash
# 1. Cheapest and possibly best — start here
python run_local_models.py --family indictrans2 --model ai4bharat/indictrans2-en-indic-1B --tag indictrans2
python run_local_models.py --family nllb --model facebook/nllb-200-3.3B --tag nllb33b --batch-size 64

# 2. The right Qwen
python run_local_models.py --family vllm --model Qwen/Qwen3-235B-A22B --tag qwen3_235b --tensor-parallel 8

# 3. Controls — settle the Bengali-coverage question, and add a strong non-Qwen LLM
python run_local_models.py --family vllm --model Qwen/Qwen2.5-72B-Instruct --tag qwen25_72b --tensor-parallel 4
python run_local_models.py --family vllm --model CohereForAI/aya-expanse-32b --tag aya32b --tensor-parallel 2

# 4. Score every candidate against the target, paired vs Google
python score_all.py
```

`aya-expanse-32b` is Cohere's multilingual-first model — a useful non-Qwen LLM datapoint at
modest cost.

## How to read the result

A candidate is worth acting on only if **vs_google > +0.02 AND |t| > 2**. The scorer prints
both, plus a contamination check.

🔴 **The contamination check is not a formality.** An LLM that notices the target style and
adds `হেলো` / `নাসেনিয়া ডক` scores higher for the wrong reason — that is styling, which a
separate model already learns. Both must read ~0%. A candidate that leaks register is
disqualified regardless of its score.

## Cost of the full run, once a winner exists

107,737 rows = **11.8M words in ≈ 16.5M tokens, ~33M tokens out.**

`run_local_models.py` prints a measured GPU-hour projection for the full set after every probe,
so you get a real number from the 200-row run rather than an estimate from this table.
