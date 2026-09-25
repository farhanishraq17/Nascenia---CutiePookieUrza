# E17 — Re-translate the draft with a stronger model

**Tier 1 — INFORMATION · Priority: HIGHEST · No GPU required for the decisive measurement**

## The question

> Our draft was translated with **Google Translate**. It aligns to the organizers' translation at
> **Token F1 0.5984**. Does a stronger translator raise that floor — and with it, every experiment's ceiling?

## RESULT (2026-08-07) — E17 is CLOSED. Keep the Google draft.

Four translators, paired against Google on each candidate's own rows:

| Translator | n | Token F1 | Google* | vs Google | t | wins |
|---|---|---|---|---|---|---|
| **Claude Opus 5** | 24 | **0.6865** | 0.6234 | **+0.0631** | 5.88 | 21/24 |
| Codex (GPT-5) | 10 | 0.6483 | 0.6230 | +0.0253 | 1.34 | 6/10 |
| *Google Translate* | — | *baseline* | — | — | — | — |
| NLLB-200 1.3B | 200 | 0.5480 | 0.5918 | **−0.0439** | −11.41 | 40/200 |
| **Qwen3-14B** | 200 | **0.4663** | 0.5918 | **−0.1255** | **−20.38** | **10/200** |

\* Google scored on that candidate's own rows.

**Only frontier LLMs beat Google. Everything deployable loses, and loses badly.**

### The Qwen3 result is not an artifact — it is the finding

| | Qwen3-14B | Google | Target |
|---|---|---|---|
| mean words | 95.5 | 99.3 | 99.8 |
| Bengali char fraction | 0.81 (0 rows < 0.5) | — | — |
| Latin letters | 4% | — | 6% |

Correct length, fluent Bengali, no truncation, no commentary, no register leakage. It simply
chooses **different synonyms** — `কয়েকটি সম্ভাবনা` where Google *and* the target both say
`বেশ কিছু সম্ভাবনা`.

**This is the sharpest statement of what the metric actually measures.** It does not reward
good Bengali. It rewards **lexical coincidence with one particular translator**, and Google's
vocabulary happens to sit closer to the organizers' than a strong modern LLM's does.

### Why the line closes

- **Claude wins (+0.0631) but there is no Claude API here** — not deployable across 107,737 rows.
- **Qwen3-235B would have to gain +0.146 over the 14B** just to clear the +0.02 usefulness bar.
  The entire Qwen3-14B→Claude spread is 0.189, so that is most of the achievable range. Possible,
  not likely. Cheap enough to run on the fleet as a final check — **but it must not block E05.**
- **Both hypotheses that motivated E17 are dead:** dedicated MT loses (NLLB), and open-weights LLM
  translation loses harder (Qwen3).

**Decision: the Google Translate draft stays.** The remaining headroom is in **E05 (train to
convergence)** — the incumbent peaked at step 2,750 and was *still improving* when Kaggle's clock
stopped it.

**One thing E17 did buy:** NLLB and Qwen3 are now measured points in *draft space*. That makes
them ideal augmentation sources for **E21 arm A** — back-translating real targets needs a
translator that is genuinely *different* from the production one, and both qualify by measurement.

---

## Why it matters

This is the only idea on the board that attacks the **actual** bottleneck.

```
competition target = f_B(English)        the organizers' translation — what we are scored on
our draft          = f_A(English)        f_A = Google Translate API
model              : f_A(English) → f_B(English)
```

The model reached **0.7724** starting from a draft that itself only reaches **0.5984**. The draft is
the floor everything is built on. **Raise the floor and you raise the ceiling for E01–E16 at once** —
including every result already measured, which would need re-running against a better draft.

Every other Tier-1 experiment changes *which fields* the model reads. This one improves the *quality
of the most important field*. It is also the cheapest test here: the decisive measurement is an API
job and a metric call, **no training at all**.

## The caveat that makes this non-obvious

**Better translation ≠ closer to theirs.** The metric rewards matching *one specific translator's
fingerprint*, not translation quality. A more fluent, more idiomatic Bengali rendering could easily
score **lower** if the organizers used a plain machine translator — which the register evidence
suggests they did (heavy boilerplate, `হেলো` opener at 76.4%, mechanical structure).

So this is genuinely 50/50, and that is exactly why it is worth two hours instead of an assumption.

## Method — measure before you spend anything

**Step 1 — probe (no GPU, ~1–2 h).** Re-translate the **English answers of 1,000 dev rows** with each
candidate, then score each rendering against the competition target with `code/metric.py`:

| Translator | Token F1 vs target | ROUGE-L |
|---|---|---|
| **Google Translate (current baseline)** | **0.5984** | **0.5482** |
| GPT-4o-mini | | |
| Llama-3-70B / Llama-3.1-70B | | |
| Gemini Flash / DeepSeek — optional | | |

Use the *same* 1,000 dev ids for all of them so the comparison is like-for-like, and prompt for a
plain, faithful medical translation — **not** a polished or "improved" one.

**Step 2 — only if a candidate clearly wins.** Re-translate all 112,164 English answers, rebuild the
datasets with `code/09_build_inputs.py`, and re-run **E01** as the head-to-head.

## What it must beat

**Token F1 0.5984 / ROUGE-L 0.5482** — the current draft, measured on the frozen dev split.

Require a margin well above the **0.0044** noise floor. On 1,000 rows the sampling error is larger
than on 5,000, so treat anything under **+0.02** as inconclusive and re-measure on the full 5,000.

## How to read the result

| Result | Meaning | Next |
|---|---|---|
| **≫ 0.5984** (e.g. 0.65+) | **The single most valuable finding available.** The floor rises and every experiment's ceiling rises with it. | Re-translate all 112k · rebuild all datasets · re-run E01 · **re-baseline everything** |
| ≈ 0.5984 | Translator choice does not matter — the residual gap is genuine translator-to-translator variance, not quality | Close the line permanently; the model, not the draft, is the remaining lever |
| **< 0.5984** | **A stronger translator is *further* from the organizers'** — strong evidence they used plain machine translation | Very informative: it means the draft is near-optimal, and E05 (train longer) is where the remaining gain is |

**All three outcomes are valuable**, which is rare. Even the negative case tells you the draft is
close to as good as it gets and redirects effort with confidence.

## Cost and disclosure

- **Probe:** ~1,000 API calls per candidate. Minutes of compute, a few dollars.
- **Full re-translation:** 112,164 calls — budget for it *only after* the probe wins.

**Any new translation must be disclosed** exactly like the current one: model name and version,
the prompt used, chunking and retry policy, row counts. Rules §2.6.a. **And it must preserve row
order / carry the `hcm_<index>` key** — the id alignment is the whole approach, and shuffling or
deduping before translating destroys it irrecoverably.

---

## Non-negotiables (every experiment)

- **`transformers==4.57.3`** — assert it.
- **bf16 on sm_80+, fp32 otherwise. NEVER fp16** — T5 goes NaN *silently*.
- **Never change the split**: `--seed 42 --dev-size 5000`.
- **Report Token F1 and ROUGE-L**, never the local composite.
  `LB ≈ 0.4646 + 0.3098·TokenF1 + 0.2·ROUGE-L`.
- **Ignore differences below 0.0044.**
- **Keep EVERY arm's `best/` — the weights are the deliverable, losers included.** Metrics
  alone force a full retrain before anything here can be submitted, and a low-scoring model that
  *disagrees usefully* is exactly what E14/E19 need. One directory per arm; `run.json` beside the
  weights (`checkpoint_hash` is not a run identity). **Record everything in this folder's
  `RESULTS.md`** — the top-level one is only the cross-experiment scoreboard.
  See README → *Reporting back*.

Record in [`../RESULTS.md`](../RESULTS.md).
