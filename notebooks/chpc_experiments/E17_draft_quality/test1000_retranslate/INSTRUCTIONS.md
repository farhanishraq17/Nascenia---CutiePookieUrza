# Re-translate the 1,000 test drafts — handoff instructions

🔴 **Read §8 before doing anything else.** The cheap 24-row version of this experiment has since
been run end-to-end and came back negative — the full 1,000-row job below is probably not worth
your time as currently scoped. This file is kept intact below for context.

**Give this whole folder, and the prompt in §6, to Claude.** Everything needed is here.

---

## 1. What this is, in one paragraph

We hold **#1 on the leaderboard at 0.89552** with a BanglaT5 model that does *register transfer*:
it is handed an English ChatDoctor answer plus a **Bengali draft translation of that answer**, and
rewrites both into the organizers' Bengali style. The Bengali draft is currently **Google
Translate output**. This task replaces that draft — for the 1,000 test rows only — with a
Claude translation, to see whether a better draft raises the final score.

**You are translating English → Bengali. Nothing else.**

## 2. Files in this folder

| File | Rows | What it is |
|---|---|---|
| **`TEST_1000_english.csv`** | **1,000** | 🥇 **Your input.** Columns: `hcm_id`, `english` |
| `TEST_1000_google_draft.csv` | 1,000 | The *current* Google draft, for reference only — **do not copy its wording** |
| `INSTRUCTIONS.md` | — | This file |

**Volume: 113,434 English words / 669,697 characters.** Mean 113 words per row, p95 207, max 511.

## 3. Output format — exactly two columns

```csv
hcm_id,bengali
34654,আপনার লাইপেজ লেভেল বৃদ্ধির কারণ...
3116,আপনার এই লক্ষণগুলোর জন্য...
```

Save as **`TEST_1000_claude.csv`**. Rows may be in any order — they are re-joined by `hcm_id`.

## 4. 🔴 The four rules that matter more than translation quality

These are counter-intuitive. Read them twice.

**① Never drop, merge, reorder or renumber a row.**
`hcm_id` is a row index into the public ChatDoctor corpus and is what aligns this data to the
competition's test set. **All 1,000 currently resolve.** One dropped row silently breaks the
alignment and the damage shows up much later as a collapsed score. **Exactly 1,000 rows out.**

**② Translate faithfully and plainly — do NOT improve the text.**
We are not looking for good Bengali. We are trying to land **close to one particular translator's
output**. Do not polish, restructure, summarise, expand, or fix the doctor's grammar. Mirror the
English sentence-for-sentence. If the English is clumsy, the Bengali should be clumsy in the same
places.

**③ Do not add greetings, branding, or sign-offs.**
You will notice the target style opens with `হেলো` and mentions `নাসেনিয়া ডক`. **Do not add
those.** A separate model learns that conversion. Injecting it here contaminates the experiment.

**④ Translate any `ChatDoctor` / `Chat Doctor` mentions faithfully — do not delete or fix them.**
The source corpus has its own branding baked into the answers. It gets normalised downstream. If
the English says it, translate it as-is.

**Also:** keep Latin-script medical abbreviations in Latin script — `PCOD`, `LH/FSH`, `CA 125`,
`MRI`. The target corpus does this too, e.g. `পিসিওডি (PCOD)`.

## 5. Batching — the proven throughput

This project has already done this at small scale (`../claude_batches/`). **10–14 rows per turn**
was the sustainable rate, roughly 1,200–1,400 Bengali words per response.

```
1,000 rows ÷ ~12 per turn  ≈  80–100 turns
```

Realistically **4–6 hours of continuous back-and-forth, across several sessions** — context fills
long before 1,000 rows, so plan to start fresh sessions and keep completed batches on disk.

**Suggested procedure**
1. Work in numbered batches: `batch_001.csv`, `batch_002.csv`, … each 10–15 rows.
2. After each batch, **immediately save it to disk.** Do not accumulate work in the conversation.
3. Every ~10 batches, run the row-count check in §7.
4. At the end, concatenate to `TEST_1000_claude.csv` and run the §7 check on the whole thing.

## 6. The prompt to give Claude

> You are translating English doctor's replies into Bengali for a machine-translation alignment
> task. Produce a **faithful, plain, sentence-by-sentence** translation.
>
> **Do not improve the text.** Do not polish, restructure, summarise, expand, or fix grammar. If
> the English is awkward, keep the Bengali awkward in the same way. The goal is to land close to a
> specific existing machine translation, not to write good Bengali.
>
> **Do not add** greetings, sign-offs, or any branding that is not in the English source.
> **Do translate** any "ChatDoctor" / "Chat Doctor" mentions as they appear — do not remove them.
> Keep Latin-script medical abbreviations (PCOD, LH/FSH, CA 125, MRI) in Latin script.
>
> Output CSV with exactly two columns, `hcm_id,bengali`, one row per input row, `hcm_id`
> unchanged. Quote fields containing commas.
>
> I will paste batches of 10–15 rows. Translate every row in the batch.

**Setting:** use the strongest model available but **turn reasoning effort DOWN**. Translation is
not a reasoning task; high effort costs time without improving output.

## 7. 🔴 Validation — run this before handing anything back

```python
import pandas as pd
src = pd.read_csv("TEST_1000_english.csv", dtype=str)
out = pd.read_csv("TEST_1000_claude.csv", dtype=str)

assert len(out) == 1000, f"expected 1000 rows, got {len(out)}"
assert out["hcm_id"].nunique() == 1000, "duplicate hcm_ids"
assert set(out["hcm_id"]) == set(src["hcm_id"]), "hcm_id set does not match the source"
assert out["bengali"].notna().all() and (out["bengali"].str.strip() != "").all(), "empty rows"

bn = out["bengali"].str.count(r"[ঀ-৿]") / out["bengali"].str.len().clip(lower=1)
print(f"Bengali character fraction: mean {bn.mean():.2f}, min {bn.min():.2f}")
print(f"rows under 50% Bengali: {(bn < 0.5).sum()}   <- inspect these, likely untranslated")

w = out["bengali"].str.split().str.len()
print(f"word count: mean {w.mean():.0f} (English source mean 113)")
print("✅ all checks passed" if len(out) == 1000 else "❌ FIX BEFORE SENDING")
```

**A mean word count far from ~113, or any row under 50% Bengali characters, means something was
skipped or left in English.** Fix before sending.

## 8. 🔴 UPDATE 2026-08-19 — the 24-row transfer test ran, and the news is bad

**Before you spend the 4-6 hours in §5, read this.** The cheap version of this experiment — using
the 24 rows that already had a Claude translation (`../claude_batches/`) and happen to sit inside
the frozen dev split — has now been run all the way through the champion, not just scored on the
draft. Result (`nascenia-transfer-test24` on Kaggle, `LOCAL_EXPERIMENTS.md` XFER-TEST24):

| | Token F1 | ROUGE-L |
|---|---|---|
| google draft → final output | 0.8374 | 0.8077 |
| claude draft → final output | 0.8314 | 0.8056 |
| delta | **−0.0060** (t=−0.77, not significant) | **−0.0021** (not significant) |

Claude won only **7 of 24 rows** on Token F1. **The draft-level gain (+0.0631, below) does not
survive the champion — if anything it reverses, though not significantly at n=24.** Implied LB
composite delta: **≈ −0.002**, not the +0.01 to +0.03 this file originally guessed.

**Recommendation: do not run the full 1,000-row translation as currently scoped.** The expected
payoff is approximately zero to slightly negative against 4-6 hours of work. If you want to spend
that time on this lever anyway, the more promising variant is investigating *why* it reverses
(the champion likely keys off Google Translate's specific lexical fingerprint as a register cue,
not the draft's semantic content — see the analysis in `LOCAL_EXPERIMENTS.md`) before re-running
at 1,000-row scale with the same recipe. **This section is intentionally left below for context —
it's what motivated the test, not a promise the test paid off.**

## 8b. Original write-up (kept for context — see the update above)

The translated file gets scored against the frozen dev metric and, more importantly, **fed
through the champion model** to measure the effect on final output.

**This is genuinely uncertain, and a negative result is a real outcome.** Prior measurement
(`../RESULTS.md`, E17):

| translator | vs Google, on draft Token F1 | significance |
|---|---|---|
| **Claude Opus 5** | **+0.0631** | t = 5.88, n = 24 ✅ |
| Codex (GPT-5) | +0.0253 | t = 1.34, n = 10 — not significant |
| NLLB-200 1.3B | −0.0439 | t = −11.41 ❌ |
| Qwen3-14B | −0.1255 | t = −20.38 ❌ |

So Claude *does* beat Google on draft quality. **But two caveats:**

1. **That +0.0631 was measured on the draft, not on the final output.** The champion converts a
   0.5963 draft into 0.8348 output, so the transfer is not 1:1 — **and §8's 24-row test above
   shows it does not survive at all.**
2. **The champion was trained exclusively on Google-draft distribution.** A better-but-different
   draft is also a distribution shift, which **fully cancelled the gain in the 24-row test, not
   just partly**.

The reason a negative is plausible at all: the competition's Bengali looks like **plain machine
output** — 76.4% of answers open with `হেলো`, with mechanical boilerplate throughout. If the
organizers used a basic translator, a *better* model can land **further** from them. That is
exactly what happened to Qwen3-14B, whose output was verified fluent and correctly-sized and still
lost by 0.1255 — it chose `কয়েকটি সম্ভাবনা` where the target said `বেশ কিছু সম্ভাবনা`.

**The metric rewards lexical coincidence with one specific translator, not good Bengali.** Rule ②
exists because of this.

## 9. Provenance — mandatory, record as you go

Rules §2.6.a requires disclosing external data and processing. Note down:

- **model name and version** used
- **the exact prompt** (§6, plus any changes)
- batching approach and any retries
- **date**, and **row counts in vs out**

This goes into the Phase 2 write-up. A translation whose provenance is not recorded cannot be
used in the final submission.
