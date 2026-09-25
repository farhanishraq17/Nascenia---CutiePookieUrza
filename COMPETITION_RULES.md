# Nascenia AI Hackathon — Rules & Reference

**Task:** Bengali Medical Dialogue Generation
**Full title:** *Nasenica AI Hackathon: Bengali Medical Dialogue Generation*
**Tagline:** Fine-Tune LLMs Under 3B Params for Doctor-Level Responses
**Platform:** Kaggle — https://www.kaggle.com/competitions/nascenia-ai-hackathon
**Type:** Community Prediction Competition · **PRIVATE** · Custom Metric · Kudos only (no Points/Medals)
**Host:** WasiAhmad057 · **Sponsor:** Nascenia LTD
**Hard constraint:** deployed inference model ≤ 3B parameters

**Sources merged into this document:**
1. `RULEBOOK/Rulebook_Nascenia.pdf` — the official organizer rulebook
2. Kaggle **Overview** tab (Description + Evaluation)
3. Kaggle **Data** tab (Dataset Description)
4. Kaggle **Rules** tab (competition-specific + Kaggle Foundational Rules)
5. Local inspection of `DATA/COMPETITION_PROVIDED_DATA/`

> **In any conflict between the PDF rulebook and Kaggle, the Kaggle page is final.** See §0.

**Competition status at time of writing:** 144 entrants · ~20 days remaining · rules accepted on our account.

---

## 0.0 ORGANIZER RULE UPDATES — relayed by the user, these supersede the text below

Organizers may amend the rules with notice (§14). The following were confirmed by the user and **override both the PDF rulebook and the older Kaggle Rules text quoted later in this document**:

| Date | Rule | Old | **Now** |
|---|---|---|---|
| 2026-08-05 | Team size | maximum four (4) | **no limit — unlimited members** |
| 2026-08-05 | Team data sharing | §2.4.b read as barring data on non-registered accounts | **teammate accounts may hold the competition data for training, registration not required first** |
| 2026-08-05 | NLP4Health-2025 dataset | read as shared-task-only | **owners permit research use** (see PLAN.md §5.3a) |

**Practical effect:** GPU capacity scales as `N × 30 h/week` with team size, and worker accounts can be given the data directly as a private Kaggle dataset rather than each joining the competition.

---

## 0. PRECEDENCE RULE & REMAINING CONFLICTS

> ## **PRECEDENCE: KAGGLE IS FINAL.**
> **Wherever the PDF rulebook (`Rulebook_Nascenia.pdf`) and the Kaggle competition pages disagree, the Kaggle page governs.** The PDF is treated as background/context only. Within Kaggle itself, the order is: **Kaggle Foundational Rules → Kaggle competition-specific Rules tab → Data tab → Overview tab.** (Kaggle's Foundational Rules state explicitly that they supersede and nullify contrary competition-specific rules.)

Applying that rule, here is where each conflict lands.

### C1 — Submission column name — **RESOLVED: `id,output`**
| Source | Stated format | |
|---|---|---|
| Kaggle **Data → Submission Format** | `id,output` | **governs** |
| ~~Kaggle **Overview → Submission Format**~~ | ~~`id,doctor_response`~~ | superseded |

Exactly two columns, one row per `id` in `test.csv`:
```
id,output
34654,আপনার লাইপেজ লেভেল বৃদ্ধির কারণ...
3116,আপনার এই লক্ষণগুলোর জন্য...
```
The Data tab is the authoritative page for file schema and matches the `train.csv` column name. Confirmed by the user 2026-08-04.

### C2 — Phase 1 submission limit — **RESOLVED: 5 per day**
| Source | Stated limit |
|---|---|
| **Kaggle Rules §2.2.a** ← **governs** | "You may submit a maximum of **five (5) Submissions per day**" |
| ~~PDF rulebook §8~~ | ~~"Submission limit: 5 during Phase 1" (5 total)~~ — superseded |

**We get 5 submissions per day**, and this is what the platform enforces. Also from the same section: **you may select one (1) Final Submission for judging.**

### C3 — Phase 2 deadline time — **RESOLVED: August 25, 12:00 PM BD**
The PDF contradicted itself (§5.1 "12 PM" vs §7 timeline "00:00"). Kaggle Rules state **August 25th, 12 PM, BD Time Zone** → **that is the deadline.**

### C4 — Data license — **RESOLVED: CC BY-NC 4.0**
The Kaggle **Rules** tab (§1.7 and §2.4.a) states **CC BY-NC 4.0**; the Data tab's metadata sidebar shows CC BY-NC-SA 4.0. The Rules tab is the binding legal text and outranks the Data tab sidebar → **CC BY-NC 4.0**. Either way our obligation is identical: **non-commercial use, no redistribution.**

### C5 — Team registration deadline precedes the start date — **STANDS AS WRITTEN**
Kaggle Rules §2.3 lists team registration deadline **August 2** with data released **August 4**. The PDF says the same, so there is no PDF-vs-Kaggle conflict to resolve — the Kaggle text simply reads as impossible on its face. **Kaggle governs, so August 2 is the stated date.** Worth a Discussion-tab question if we intend to change team composition, but nothing to act on otherwise.

---

## 1. The Task

Given a **patient's prompt in Bengali** describing symptoms, concerns, or a medical question, generate the **doctor's response in Bengali** — fluent, relevant, and medically accurate.

From the Kaggle Overview:

> "This competition challenges you to build an AI system that can act as a doctor — reading a patient's prompt in Bengali and generating a clinically sound, well-communicated response, the way a real physician would."
>
> "The catch: your model must be lightweight. We're capping base LLM size at 3 billion parameters, so this competition is about efficient fine-tuning and clever adaptation, not simply scaling up to the largest model available."

Motivation stated by the host: Bengali is spoken by 230M+ people but is one of the most underserved languages in medical NLP.

---

## 2. Two-Phase Structure

| Phase | What happens | Who | Weight |
|---|---|---|---|
| **Phase 1 — Leaderboard** | Automated composite scoring on held-out test set, public/private split | Everyone | **80%** |
| **Phase 2 — Verification & LLM-as-Judge** | Submit model + inference script → parameter verification + LLM judging | **Top 10 only** | **20%** |

```
Final Score = 0.8 × Phase 1 Score + 0.2 × Phase 2 Score
```

Both normalized to the **same 0–100 scale** before combining (per the Kaggle Evaluation page).
**An entry that fails parameter verification is excluded from final ranking regardless of score.**

---

## 3. Evaluation Metric (Phase 1)

Per example, the prediction ŷ is compared against reference y using three sub-metrics:

**1. BERTScore F1** — semantic similarity via contextual embeddings
```
BERTScore_F1 = 2 · P_BERT · R_BERT / (P_BERT + R_BERT)
```

**2. Token-level F1** — bag-of-tokens word overlap
```
P_tok = |tokens(ŷ) ∩ tokens(y)| / |tokens(ŷ)|
R_tok = |tokens(ŷ) ∩ tokens(y)| / |tokens(y)|
Token F1 = 2 · P_tok · R_tok / (P_tok + R_tok)
```

**3. ROUGE-L F1** — longest common subsequence overlap, β = 1 (precision and recall weighted equally)
```
R_lcs = LCS(ŷ, y) / |y|
P_lcs = LCS(ŷ, y) / |ŷ|
ROUGE-L_F1 = (1+β²) · R_lcs · P_lcs / (R_lcs + β² · P_lcs)
```

**Composite:**
```
Score = 0.5 · BERTScore_F1 + 0.3 · Token F1 + 0.2 · ROUGE-L_F1
Phase 1 Score = (1/N) Σ Score_i
```

| Component | Weight |
|---|---|
| BERTScore F1 | 50% |
| Token-level F1 | 30% |
| ROUGE-L F1 | 20% |

- **Public leaderboard** = public portion of the 1,000 test rows, updates live.
- **Private leaderboard** = private portion, revealed immediately after the deadline. **Private rank decides who advances** — top 10.
- The **private** Phase 1 Score carries into the final weighted ranking.

### Strategic implications
- **All three components are similarity metrics.** Nothing in Phase 1 rewards being clinically right except insofar as it resembles the reference. Matching the reference corpus's *style, length, vocabulary, and phrasing* is the dominant lever for 80% of the final score.
- **Token F1 and ROUGE-L both have precision terms** — over-long generations are directly penalized. Match the reference length distribution (§8).
- The exact BERTScore model isn't disclosed on the page. It must be Bengali-capable, so likely a multilingual BERT (e.g. `bert-base-multilingual-cased` or XLM-R). Worth asking on Discussion — it affects how we optimize.
- **Only Phase 2 (20%) rewards real medical reasoning.** Don't trade away Phase 1 style-matching for it.

---

## 4. Model Constraints

- Any base LLM allowed **as long as it has ≤ 3,000,000,000 (3B) parameters at inference time**.
- **Permitted:** fine-tuning, LoRA / adapters, quantization, distillation, prompt engineering.
- **Ensembling permitted** — but the **combined parameter count of all models used at inference must stay under 3B**.
- Verified in Phase 2 by inspecting submitted weights + inference script.
- **Misrepresenting parameter count = disqualification.**

> **Quantization reduces memory, not parameter count.** A 7B model in 4-bit is still 7B parameters → disqualified.
> **LoRA adapters add parameters.** Count base + merged adapters.
> **Ensembles:** three fine-tuned BanglaT5 (~247M each) ≈ 741M — comfortably legal. One 3B model leaves no headroom for a second.

---

## 5. Phase 2 Requirements (Top 10)

### 5.1 What to submit — by **August 25, 12:00 PM BD (GMT+6)**
1. **Full inference script** — reproducible, documented, runnable end-to-end
2. **Model weights/checkpoint** — or a script that downloads them from a reproducible source
3. **A short write-up** — approach, base model, fine-tuning method, external data/tools used
4. **Environment/dependency file**

### 5.2 Parameter verification
- Organizers load the model and confirm total parameter count ≤ 3B.
- **Also required:** the inference script must **reproduce the leaderboard-submitted outputs within a reasonable tolerance.** Failure → disqualified, replaced by next-highest eligible entry.
  - → **Fix and record every random seed, decoding parameter, library version, and checkpoint hash used for the final Kaggle submission. Archive the exact artifact that produced it.**

### 5.3 LLM-as-judge
- A **separate held-out judging set** (not the private test set).
- Scored on:
  - **Medical diagnostic accuracy** — is the response clinically appropriate/correct?
  - **Response quality/appropriateness** — tone, completeness, clarity as a doctor's response
- **Blind** judging (identities hidden), outputs in randomized order.
- Organizers may add a human review step to spot-check judge reliability.
- Judge scores on a **normalized 0–100 scale**; mean across the judging set = Phase 2 Score.

---

## 6. Data Rules & External Data

- **External data IS allowed** — for both training data and base LLMs.
- **But the Kaggle Rules impose a real constraint the PDF does not.** External data/models must be:
  - **publicly available and equally accessible to all participants at no cost**, **or**
  - satisfy the **"Reasonableness Standard"** — minimal cost, reasonably accessible to all.
  - Example given: a small subscription (e.g. Gemini Advanced) is fine; a proprietary dataset costing more than the prize is not.
- **All external data must be disclosed in the submission notes.**
- **AutoML tools permitted**, provided you hold an appropriate license.
- **No private code sharing** outside your team during the competition. Public sharing is allowed **only** on the competition's own Kaggle forum/notebooks, and doing so licenses it under an OSI-approved license.
- **No redistribution** of Competition Data to anyone not participating. You must take reasonable measures to prevent access by non-participants.
- Non-commercial use only (CC BY-NC 4.0 — see C4).
- **Open-source code only:** if open source code is used in the model, it must be under an **OSI-approved license that does not limit commercial use**. (Rules out GPL-encumbered or research-only-license components in the final pipeline — check base model licenses.)

> Practical note: the local collection under `DATA/EXTERNAL_COLLECTED_DATA/` looks compliant (public HF/Kaggle/GitHub datasets), but **each source's license must be checked** against the "no commercial-use limits" requirement before it goes into a winning submission.

---

## 7. Submission Rules & Fair Play

- **Submission limit: 5 per day** (Kaggle Rules §2.2.a — governs over the PDF's "5 total"; see C2).
- **You may select one (1) Final Submission for judging.** If none is selected, the last submission counts.
  - → With 5/day over ~20 days we have ample budget for leaderboard probing. Still worth building a **local validation split** so submissions confirm rather than explore — the public/private split means public-LB overfitting is a real risk on only 1,000 test rows.
- **One Kaggle account only.** Submitting from multiple accounts = disqualification.
- **Team mergers allowed** by the team leader, subject to size and submission-count caps.
- **Kaggle-level tiebreak:** in a tie, the submission entered **first** wins.
- **Organizer-level tiebreak** for 1st–3rd on Final Score: a **rerun of Phase 2** between tied participants.

**Prohibited — grounds for disqualification at any stage, including after prizes:**
- Accessing, reverse-engineering, or manually labeling the private test set
- **Using test set inputs for training or fine-tuning**
- Submitting outputs from human/manual labeling instead of the model
- Using models over the 3B cap, or misrepresenting parameter count
- Sharing private leaderboard test data or Phase 2 submissions with other teams
- Private sharing of competition code outside the team

Organizers may request **original training logs, code, or additional proof of compliance** from any participant.
→ **Keep a clean, reproducible training log and code history from day one.**

---

## 8. The Data

### As described on the Kaggle Data tab
> "Each example consists of an **input** — a patient's prompt describing their symptoms, concerns, or a medical question, written as a patient would address a doctor — and, for training data, an **output** — the expected doctor's response, including relevant medical guidance."

| File | Rows | Columns | Notes |
|---|---|---|---|
| `train.csv` | **108,954** labeled examples | `id`, `input`, `output` | For fine-tuning |
| `test.csv` | **1,000** unlabeled prompts | `id`, `input` | Split into public + private portions |

Total size **311.46 MB**. Leaderboard during the competition reflects the **public portion only**.

| Column | Description |
|---|---|
| `id` | Unique identifier for each example |
| `input` | The patient's prompt to the doctor, in Bengali |
| `output` | *(train only)* The reference doctor response, in Bengali |

**Submission format (per Data tab — see conflict C1):**
```
id,output
34654,আপনার লাইপেজ লেভেল বৃদ্ধির কারণ...
3116,আপনার এই লক্ষণগুলোর জন্য...
```

The host also notes the data is real medical dialogue content, for research/competition only, **not a clinical decision-making resource**.

### Local inspection findings (`DATA/COMPETITION_PROVIDED_DATA/`)

All `id` values are unique in both files. Row counts match Kaggle exactly.

**Length statistics (characters):**

| Field | Mean | Median | Min | Max |
|---|---|---|---|---|
| train `input` | 439 | 372 | 1 | 10,814 |
| train `output` | **634** | **594** | 4 | 3,322 |
| test `input` | 427 | 366 | 22 | 2,030 |

**Observations that matter for scoring:**
- Test inputs are distributed like train inputs — **no obvious domain shift**.
- **Target length is tightly clustered (median 594, mean 634).** Generating near this length is directly worth ROUGE-L / Token-F1 points.
- Content strongly resembles **Bengali-translated HealthCareMagic / iCliniq-style consumer health Q&A**. Note that `DATA/EXTERNAL_COLLECTED_DATA/Data_Search_1/huggingface/ChatDoctor-HealthCareMagic-100k/` is the same size class (100k) — **likely the source corpus. Check overlap; the English originals could be a legitimate augmentation source.**
- Responses very often open with **"হেলো,"** — a cheap, reliable stylistic prior.
- Outputs mix Bengali script with **parenthesized English medical terms**: `পিসিওডি (PCOD)`, `এলএইচ/এফএসএইচ (LH/FSH)`, `জিটিটি (GTT)`. Reproducing this convention matters for token-level F1.
- **Degenerate rows exist** (input as short as 1 char, output as short as 4 chars) — filter before training.

---

## 9. Timeline

All times **GMT+6 / BD Time Zone**. Dates below reconcile the PDF timeline with the Kaggle Rules page.

| Milestone | Date |
|---|---|
| Competition opens / data released | **August 4** |
| Team registration deadline | **August 2** (see C5) |
| **Phase 1 submission deadline (leaderboard closes)** | **August 24, 12:00 AM (00:00)** |
| Private leaderboard revealed | Immediately after contest end |
| Top 10 announced / Phase 2 submission opens | Immediately after contest end |
| **Phase 2 (model + inference script) deadline** | **August 25, 12:00 PM** |
| LLM-as-judge results, final weighted ranking & winners announced | **August 26** |

> Effective working window for Phase 1: **August 4 → August 24, 00:00** (~20 days).
> The Phase 2 turnaround is roughly **36 hours** after the leaderboard closes. **Prepare the Phase 2 bundle in advance — do not start it after results are announced.**

---

## 10. Eligibility & Teams

- Open to anyone; **18+** (or age of majority in your jurisdiction).
- **Team size: NO LIMIT.** **Updated 2026-08-05** — the organizers removed the cap; a team may have unlimited members. This supersedes the "maximum four (4)" in both the PDF rulebook §6 and the Kaggle Rules tab §2.1.a, which predate the change. Organizers may update rules with notice (§14).
  - **Practical consequence:** GPU quota is **per account** (~30 h/week), so each additional teammate adds ~30 GPU-h/week. Submissions remain **5/day per team** regardless of size.
- Each individual on **only one team**; **one Kaggle account only**.
- Team mergers allowed via the team leader, subject to combined submission-count limits.
- Organizers, sponsors, and immediate family are not eligible for prizes. Nascenia/Kaggle employees may participate but cannot win prizes.
- Residents of Crimea, DNR, LNR, Cuba, Iran, North Korea, or anyone under U.S. export controls/sanctions are **not eligible**.
- Kaggle's Terms of Service and Foundational Competition Rules apply **in addition to** the organizer rulebook, and **supersede it in any conflict**.

---

## 11. Prizes

**Total prize pool: 45,000 BDT**

| Place | Prize |
|---|---|
| 1st | 30,000 BDT |
| 2nd | 10,000 BDT |
| 3rd | 5,000 BDT |

- Awarded on the final weighted Final Score (§2).
- Competition awards **Kudos only — no Kaggle Points or Medals.**
- Winners must complete Phase 2 verification; may need identity/payment verification per Kaggle's prize process.
- Winners are responsible for their own tax and payment arrangements.

---

## 12. IP & Licensing — Open Source is MANDATORY for winners

- **Winner License Type: Open Source.** This is stronger than the PDF's "may be asked to open-source." Winners **must** license the winning submission **and the source code used to generate it** under an **OSI-approved license that does not limit commercial use**.
  - Exception: generally commercially-available third-party software you don't own, and input data / pretrained models carrying an incompatible license, do not need to be relicensed.
- Winners may be required to provide a **detailed reproducible methodology** — architecture, preprocessing, loss function, training details, hyperparameters — plus a **link to a code repository with complete instructions** so results can be reproduced.
- Participants otherwise **retain ownership** of their model/code, granting organizers a license to use, evaluate, and (for winners) showcase it **with attribution**.
- Dataset remains Nascenia LTD property, **CC BY-NC 4.0**, competition use only.

> → Choose base models with permissive licenses (Apache-2.0 / MIT). Check Llama-3.2's community license and Gemma's terms carefully against the "no limits on commercial use" requirement before committing.

---

## 13. Ethical & Medical Disclaimer

- Research and educational purposes only. Models are **not validated for clinical use** and must not be deployed as real medical advice without regulatory review.
- **Harmful, unsafe, or clearly unethical generated medical advice may be flagged during LLM-as-judge review and penalized.**
  - → Phase 2 rewards safe hedging: recommend consulting a physician, avoid definitive dosing claims, avoid dangerous instructions. The training corpus's doctor responses already model this tone well.

---

## 14. Organizer Rights

- Organizers may update rules, extend deadlines, or adjust evaluation methodology, with notice on the competition page. **→ Re-check the Kaggle Overview and Discussion tabs periodically.**
- Organizers' decisions on disqualification, verification, and final ranking are **final**.

---

## 15. Contact

- Questions, data issues, leaderboard bugs: **wasiahmad@nascenia.com**
- Kaggle **Discussion** tab for anything that should be public to all participants.

---

## 16. Operating Checklist

**Hard rules we must never break**
- [ ] Total inference-time parameters **≤ 3B** (base + adapters + every ensemble member)
- [ ] Never train or fine-tune on test set inputs
- [ ] Never manually label / hand-write submission outputs
- [ ] Never privately share code or data outside the team
- [ ] Never redistribute the competition dataset
- [ ] One Kaggle account only

**Things we must do**
- [ ] **Resolve C1 (submission column name) before the first real submission** — the only conflict the Kaggle-precedence rule doesn't settle
- [ ] **Disclose all external data** in submission notes
- [ ] Verify every external dataset and base model carries an **OSI-approved, commercially-unrestricted license**
- [ ] Keep the exact checkpoint + seeds + decoding config for each leaderboard submission (Phase 2 must reproduce it)
- [ ] Maintain reproducible training logs and code history (organizers can demand them)
- [ ] **Build the Phase 2 bundle in advance** — inference script, weights/download script, write-up, environment file. Only ~36h between leaderboard close and the Phase 2 deadline.
- [ ] Explicitly select the Final Submission before the deadline

**Optimization priorities**
1. Match reference **style and length** (median output ≈ 594 chars) — 100% of the Phase 1 metric is similarity, and Phase 1 is 80% of the final score
2. Preserve the Bengali + parenthesized-English-term convention and the "হেলো," opener
3. Keep clinical safety and appropriateness for the 20% Phase 2 judge
4. Filter degenerate train rows; consider the English HealthCareMagic originals as augmentation
