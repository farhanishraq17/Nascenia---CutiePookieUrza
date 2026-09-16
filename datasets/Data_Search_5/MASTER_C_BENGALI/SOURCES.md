# MASTER_C_BENGALI — sources, licences, and what was kept

Curated from `Data_Search_5/bengali_medical_train_master.csv` (410,525 rows, 9 sources).
Built by [`NOTEBOOKS/06_build_master_c.py`](../../../scripts/analysis/06_build_master_c.py) on 2026-08-05.

**410,525 raw → 123,289 kept.** Five of nine sources were dropped, and 6,000 further rows were
removed to protect the frozen dev split. Every decision below is backed by a measurement.

---

## Files

| File | Rows | What it is |
|---|---|---|
| **`aligned_pairs.csv`** | **107,737** | 🥇 **The asset.** `comp_id · split · draft · target` — competition id joined to our Bengali ChatDoctor translation. Training data for the register-transfer model. |
| **`master_c_bengali.csv`** | **123,289** | Clean Bengali medical-dialogue corpus. `id · source · input · output`. For optional warm-start and Phase 2 clinical quality. |

### `aligned_pairs.csv` coverage

| split | aligned | of | coverage |
|---|---|---|---|
| train | 101,737 | 101,740 | 100.0% |
| dev | 5,000 | 5,000 | **100.0%** |
| test | 1,000 | 1,000 | **100.0%** |

`draft` = our translation of the ChatDoctor answer · `target` = the competition's answer
(empty for test). Drafts are left **raw** — converting their register is the model's job.

---

## 🔴 The leak this dataset ships with, and how it was removed

**`bengali_medical_train_master.csv` contains the competition `train.csv` in full** as
`source == given_train` (108,954 rows, ids `0,1,2,…`). Measured: **all 5,000 of our frozen dev
ids are present.** Fine-tuning on the master as shipped trains on the dev set and silently
invalidates every dev number recorded since the project began.

**A second, subtler leak:** the `healthcaremagic` rows are *a different translation of the same
answers*. An hcm row whose id is in our dev split is a paraphrase of a dev reference. Training on
it leaks the evaluation set just as surely as training on dev itself.

**Both are removed.** `given_train` is excluded entirely, and **6,000 hcm rows whose id falls in
the frozen dev or test split are dropped** from the corpus. They survive only inside
`aligned_pairs.csv`, correctly labelled `split=dev` / `split=test`, where they are used for
**evaluation and inference — never for training.**

---

## ✅ Kept (123,289 rows)

| Source | Rows kept | Origin | Language | Why kept |
|---|---|---|---|---|
| **healthcaremagic** | 106,117 | [github.com/Kent0n-Li/ChatDoctor](https://github.com/Kent0n-Li/ChatDoctor) | EN → BN, our translation | **The reason this dataset matters.** Keyed `hcm_<row index>` = the competition's own `id`. See ALIGN-01. |
| **icliniq** | 7,321 | ChatDoctor repo | EN → BN, our translation | Real patient→doctor consultations, same translation pass as hcm, so a consistent fingerprint. |
| **genmedgpt** | 5,200 | [GenMedGPT-5k](https://huggingface.co/datasets/GenMedGPT) | EN → BN, our translation | Real dialogue shape. Short (35 tokens) — use sparingly. |
| **doctor_qa_bangla** | 4,651 | [shetumohanto/doctor_qa_bangla](https://huggingface.co/datasets/shetumohanto/doctor_qa_bangla) | **Native Bengali** | The only natively-Bengali source here — **zero translation fingerprint**. Small and terse, but genuine. |

Applied to all four: brand normalised (`চ্যাট ডক্টর` / `ChatDoctor` → `নাসেনিয়া ডক`), whitespace
collapsed, degenerate rows dropped (input < 5 or output < 10 tokens), exact `(input, output)`
duplicates removed. 124,058 → 123,289.

Corpus output length: **mean 95.4, median 88 tokens** against competition references at ~100. Close.

---

## ❌ Excluded (287,236 rows), with the measurement

### `given_train` — 108,954 — **not external data**
It is the competition training set, and it contains the frozen dev split. See the leak section above.

### `ai_medical_chatbot` — 166,193 — off-register, held not deleted
The largest single block (40% of the raw master) and the riskiest. Register measurement on outputs:

| Corpus | opens `হেলো` | opens `হাই`/`হ্যালো` | mean tokens |
|---|---|---|---|
| **competition references** | **76.37%** | 0.01% | 99.7 |
| ai_medical_chatbot | 0.04% | **70.06%** | 71.4 |

The metric is lexical overlap against *this* corpus's translation. A different translation pass
carries a different fingerprint, and off-register content is precisely what the scoring punishes —
we measured retrieval (0.2047) losing to a fixed constant (0.2669) for the same reason.

**Not deleted, held.** It remains in the raw master and can be revisited if the register-transfer
track stalls. It is the last experiment to run, not the next.

### `alpaca_health` — 1,021 — **not medical**
Sourced from [stanford_alpaca](https://github.com/tatsu-lab/stanford_alpaca) "filtered for medical
keywords." The filter matched **homographs**. Measured: **65/1,021 (6.4%)** of outputs contain
clearly non-medical vocabulary (computing, economics, business), and inspection of the head shows
the rot is not marginal:

- *"মহামন্দার কারণগুলো আলোচনা কর"* — discuss the causes of the Great Depression
- *"একটি ভাইরাস এবং একটি কৃমির মধ্যে পার্থক্য কি?"* — answered about **computer** viruses and worms
- *"নিম্নলিখিত নিবন্ধটি ১০০ শব্দে সংক্ষিপ্ত করুন"* — summarise the following article

6.4% is the floor, not the estimate — it counts only rows with unmistakable non-medical keywords.
The task shape is also wrong: these are instruction-following prompts, not patient consultations.

### `disease_db` — 796 — wrong shape
Outputs are structured bullet lists (`- উপসর্গ: …`, tests, drugs), not a doctor's reply. No
greeting, no sign-off, none of the boilerplate that carries the score.

### `mts_dialog` — 3,503 — wrong task
Input is a **clinical note**; output is the doctor's **opening line** (*"what brought you back to
the clinic today?"*). That is note→dialogue, the inverse of patient-question→doctor-answer.

---

## Licences and disclosure

| Source | Licence |
|---|---|
| ChatDoctor (healthcaremagic, icliniq) | Code Apache-2.0. Data: *"ChatDoctor is for academic research only and any commercial use and clinical use is prohibited."* |
| GenMedGPT-5k | Research use, distributed with ChatDoctor |
| doctor_qa_bangla | Hugging Face dataset card terms |
| Competition data | CC BY-NC 4.0 |

**Kaggle Rules §2.6.a is satisfied** for the ChatDoctor components: the source repo is public, the
dataset links are open Google Drive URLs, and no registration, approval or payment is required —
any competitor has identical access. The research-only restriction is compatible with a
Community/Kudos-only competition whose own data is CC BY-NC 4.0.

**Translation:** English → Bengali via multi-threaded Google Translate API (`client=gtx`), 1,200-char
chunking, retry backoff, zero-width symbol sanitisation, English→Bengali digit transliteration.
Performed by this team; the Bengali text is our own derived artifact.

🔴 **Disclosure is mandatory** in the Phase 2 write-up and must name: the repo URL, the research-only
restriction, the translation method above, row counts, and the dedup/filter rules in this document.

---

## Relationship to the rest of the repo

- **`Data_Search_3` is now redundant.** Its `healthcaremagic` rows are **byte-identical** to
  Data_Search_5's — verified 100.00% match across all 112,154 shared ids. Prefer this folder.
- **`aligned_pairs.csv` supersedes** the ad-hoc `hcm_bn.csv` extraction used by the first
  register-transfer runs; it carries the split labels and the leak removal that file lacked.
- Register-transfer recipe + the 16-experiment follow-on program: `fine_tune_project/`.
- The alignment finding itself: **ALIGN-01** in
  [`LOCAL_EXPERIMENTS.md`](../../../LOCAL_EXPERIMENTS.md).

## Rebuild

```bash
python NOTEBOOKS/06_build_master_c.py \
  --master "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_5/bengali_medical_train_master.csv" \
  --proc DATA/PROCESSED \
  --out "DATA/EXTERNAL_COLLECTED_DATA/Data_Search_5/MASTER_C_BENGALI"
```

The script **asserts 100% dev and test coverage** in `aligned_pairs.csv` and fails loudly
otherwise — a missing draft is a row the register-transfer model cannot predict at all, which
would be a silent scoring hole rather than an error.
