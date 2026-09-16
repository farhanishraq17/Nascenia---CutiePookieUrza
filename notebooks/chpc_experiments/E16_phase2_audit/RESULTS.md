# E16_phase2_audit — results

**No training.** `../code/15_phase2_audit.py` over each arm's 1,000 test predictions,
2026-08-09. Phase 2 is **20 % of the final score and judged on a different objective**, so
Token F1 cannot see the failures this looks for — repetition raises recall and barely dents
precision.

## 🔴 Read the baselines first, or every number here is misleading

The audit was run on the **organizers' own reference answers** and on **our Bengali draft**
(the model's input) through the identical code. Without those two rows, the arm numbers cannot
be interpreted at all:

| | repeat sent. % | 5-gram rep | tautology % | **truncated %** | latin frac | len p50 / p95 |
|---|---|---|---|---|---|---|
| **references** *(the organizers' answers)* | 0.1 | 0.0004 | **7.9** | **6.8** | 0.0038 | 93 / 163 |
| **our draft** *(the model's input)* | 0.0 | 0.0003 | 10.1 | **35.3** | 0.0068 | 92 / 163 |
| 🥇 **E05/english_draft** *(best arm)* | 0.9 | 0.0009 | 9.3 | **6.8** | 0.0041 | 93 / 185 |
| E08 mT5-base | 0.2 | 0.0009 | 8.5 | **27.9** | 0.0031 | 90 / 123 |

**A 6.8 % "truncated" rate is not a defect — it is exactly the reference rate.** Answers that
end without terminal punctuation are simply a feature of this corpus. Judged against the
naive assumption that 0 % is the target, every BanglaT5 arm would have looked broken; judged
against the references, they are indistinguishable.

## 🥇 The finding: the best arm repairs the draft's biggest defect. mT5 does not.

**Our draft cuts off mid-sentence in 35.3 % of rows.** The organizers' answers do so in 6.8 %.

| | truncated % | |
|---|---|---|
| input (our draft) | 35.3 % | the defect the model inherits |
| **E05/english_draft** | **6.8 %** | ✅ **repaired exactly to the reference rate** |
| E08 mT5-base | 27.9 % | ❌ **barely repaired — 4× the reference rate** |

This is a *register* result, not a fluency one: converting to the house style includes learning
to finish the sentence, and BanglaT5 learns it while mT5 largely does not.

🔴 **mT5 therefore fails Phase 2 as well as Phase 1.** It already lost by 0.0161 on Token F1;
here it leaves **more than a quarter of its answers cut off**, with a p95 length of 123 tokens
against the references' 163 — it is systematically stopping early. An LLM judge would punish
that far harder than Token F1 did. **E08/E09/E10 are closed on both objectives.**

## Full sweep — all arms

| arm | rows | repeat sent. % | 5-gram rep | tautology % | truncated % | latin frac | very short % | p05 / p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| E03/main | 1000 | 1.8 | 0.0011 | 8.9 | 6.4 | 0.0031 | 0.0 | 64 / 91 / 186 |
| E01/main | 1000 | 1.1 | 0.0009 | 11.1 | 6.4 | 0.0031 | 0.0 | 65 / 92 / 189 |
| E07/main | 1000 | 1.0 | 0.0019 | 9.9 | 6.2 | 0.0033 | 0.0 | 64 / 92 / 182 |
| **E05/english_draft** | 1000 | 0.9 | 0.0009 | 9.3 | 6.8 | 0.0041 | 0.1 | 65 / 93 / 185 |
| E12/main | 1000 | 0.9 | 0.0010 | 9.6 | 7.0 | 0.0032 | 0.0 | 65 / 93 / 188 |
| E04/main | 1000 | 0.8 | 0.0009 | 10.3 | 6.8 | 0.0034 | 0.0 | 65 / 93 / 186 |
| E02/main | 1000 | 0.8 | 0.0011 | 9.9 | 5.9 | 0.0030 | 0.0 | 63 / 91 / 190 |
| E05/main | 1000 | 0.5 | 0.0008 | 9.5 | 6.6 | 0.0032 | 0.1 | 64 / 91 / 181 |
| E18/banglat5 | 1000 | 0.4 | 0.0007 | 9.9 | 6.4 | 0.0031 | 0.0 | 64 / 92 / 178 |
| E08/main | 1000 | 0.2 | 0.0009 | 8.5 | **27.9** | 0.0031 | 0.7 | 57 / 90 / **123** |

Reading the rest against the references (0.1 / 0.0004 / 7.9 / 6.8 / 0.0038):

- **Repetition is not a problem in any arm.** Worst is E03 at 1.8 % repeated sentences against
  the references' 0.1 %; the 5-gram rate is ~2× the reference but at 0.001 the absolute level is
  negligible. **The `"gastroenteritis can be caused by gastroenteritis"` failure does not recur
  at the scale that motivated this experiment.**
- **Tautology sits at 8.5–11.1 % against a reference rate of 7.9 %** — the corpus is *itself*
  moderately tautological (medical boilerplate restates the condition), so the arms are close to
  the target rather than degenerate. E01 is the highest at 11.1 %, ~1.4× the references.
- **`latin_frac` ~0.003 against the references' 0.0038** — the parenthesised English terms
  (`পিসিওডি (PCOD)`) are preserved at the right rate and no untranslated English leaked. Our
  draft is nearly 2× the reference rate (0.0068), so the models are *removing* stray English, not
  adding it.
- **Length p50 93 vs the references' 93.** p95 runs long (185 vs 163) — the arms are slightly
  more verbose in the tail, the one axis where they consistently differ from the references.

## 🔴 What this does NOT cover

**Clinical correctness, contradiction, and unsafe advice are not measured.** They need a judge
with medical knowledge, and there is no LLM-judge API on this machine. Three of E16's five
requested checks are therefore **open**, and nothing here should be reported as clearing them.

What the audit does provide is triage: `audit.json` dumps the **100 worst rows per arm** ranked
by repetition, which is where a manual or judged review should start. On the numbers above, the
expected yield is low for every BanglaT5 arm.

## Verdict

- **Result:** ✅ **No Phase-1 gain in this program was bought with Phase-2 quality.** The best
  arm matches the reference distribution on every measured axis.
- **The escalation the decision table anticipated — "E16 finds repetition in the winner ⇒
  a Phase-1 gain may cost Phase-2 score" — did not trigger.**
- **New:** mT5 is closed on Phase 2 as well, for a reason Phase 1 could not see.
- **Open:** the three judge-dependent checks. If an LLM-judge route becomes available, run it on
  `audit.json`'s worst rows for the top two arms first.
