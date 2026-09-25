# E17 — Re-translation task for Codex

Translate the `english` column of the CSVs here into **Bengali**.

---

## Do the probe first

| File | Rows | Do it |
|---|---|---|
| **`PROBE_1000_dev.csv`** | **1,000** | **Start here.** ~1% of the work, and it decides whether the rest is worth doing. |
| `FULL_107737.csv` | 107,737 | ⏸Only after the probe wins. ~12M words. |

The current draft was made with **Google Translate** and matches the target at **Token F1 0.5984**.
The probe answers one question: *does a stronger translator land closer, or further away?* It is
genuinely 50/50 — see "Why this might fail" below — so 1,000 rows before 107,737.

---

## Output format

Write a CSV with **exactly these two columns**:

```
hcm_id,bengali
44,হেলো, আপনার প্রশ্নের জন্য ধন্যবাদ। …
1729,…
```

Name it `PROBE_1000_dev_TRANSLATED.csv` (or `FULL_107737_TRANSLATED.csv`).

## The three rules that matter more than translation quality

**1. Never drop, merge, reorder or renumber a row.**
`hcm_id` is a row index into the original ChatDoctor corpus, and it is what aligns this data to the
competition's test set — **1,000/1,000 test ids currently resolve**. One dropped row silently breaks
the alignment for everything downstream, and the failure shows up only as a collapsed score much
later. Output exactly one Bengali row per input row, same ids, any order (they get re-joined by id).

**2. Translate faithfully and plainly — do NOT improve the text.**
This is counter-intuitive. We are not looking for good Bengali; we are trying to land close to *one
particular machine translation*. Do not polish, restructure, summarise, expand, fix the doctor's
grammar, or make it more idiomatic. Mirror the English sentence-for-sentence.

**3. Do not add greetings, branding or sign-offs.**
You may notice the target style opens with `হেলো` and mentions `নাসেনিয়া ডক`. **Do not add those.**
A separate model learns that conversion; injecting it here contaminates the experiment and we would
not be able to tell whether a gain came from the translator or from the styling.

## Suggested prompt

> Translate each English doctor's reply into Bengali. Produce a faithful, plain, sentence-by-sentence
> translation — do not improve, polish, shorten, expand or restructure the text. Keep medical terms
> accurate; where the English uses an abbreviation (PCOD, LH/FSH, CA 125), keep it in Latin script.
> Output one row per input row with its `hcm_id` unchanged.

**Model settings:** use the strongest general model available, but **turn reasoning effort DOWN**.
Translation is not a reasoning task — high effort costs time and tokens without improving it.

---

## What happens next

Put the translated CSV in this folder and tell me. I score it against the frozen dev split with the
exact competition metric and compare to the **0.5984 / 0.5482** baseline — a paired comparison on
the same 1,000 rows, so row difficulty cancels and ±0.007 is detectable.

| Probe result | Meaning | Next |
|---|---|---|
| **≫ 0.5984** | The draft floor rises, and every downstream ceiling with it | Run `FULL_107737.csv`, rebuild the data, retrain — **the retrain fits Kaggle** (7.9 h vs a 12 h limit) |
| ≈ 0.5984 | Translator choice does not matter here | Stop; the residual gap is genuine translator variance |
| **< 0.5984** | A stronger translator is *further* from the organizers' | Also valuable — proves the draft is near-optimal, and effort moves to training longer |

## Why this might fail — worth knowing before you spend the time

The competition's Bengali looks like plain machine output: **76.4% of answers open with `হেলো`**,
with mechanical boilerplate throughout. If the organizers used a basic translator, then a *better*
model lands **further** from them, not closer. A negative result is a real outcome here, not a
mistake — and it is still worth having, because it closes the line and redirects effort with
confidence.

---

## Provenance — record this, it is mandatory

Rules §2.6.a requires disclosing external data and how it was processed. Note down:

- **model name and version** used to translate
- **the exact prompt**
- batching / chunking approach, and any retry policy
- date, and row counts in vs out

Whatever produces the final submission has to be described in the Phase 2 write-up.
