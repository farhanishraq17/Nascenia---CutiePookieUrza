# CLAUDE.md — Working Agreement for the Nascenia AI Hackathon

This file governs how Claude works on this repository. Read it at the start of
every session and follow it without exception.

**Source of truth:** [`Rulebook_Nascenia.pdf`](Rulebook_Nascenia.pdf) (official
rulebook, 13 sections). This file is a working summary of it plus our process
rules. **If the two ever conflict, the rulebook wins** — and tell me about the
conflict rather than silently picking one.

## 1. The Competition

- **Name:** Nascenia AI Hackathon — **Bengali Medical Dialogue Generation**
- **Platform:** Kaggle Competitions (URL: see `COMPETITION-LINK.txt` — currently empty, fill it in)
- **Organizer:** Nascenia LTD · Contact: `wasiahmad@nascenia.com`
- **Task:** **Text generation, not classification.** Given a patient's
  prompt/query in Bengali, generate the doctor's response in Bengali.
- **Hard model cap:** the model(s) used at inference must total
  **≤ 3,000,000,000 (3B) parameters**. This is verified by organizers in
  Phase 2 and is the single most disqualifying constraint in the whole
  competition. See §3.

### Two-phase structure

| Phase | What | Weight in final score |
|---|---|---|
| **Phase 1 — Leaderboard** | Automated scoring on Kaggle public/private test split | **80%** |
| **Phase 2 — Verification & LLM-as-Judge** | Top 10 from the *private* leaderboard submit model + inference script; parameter check + blind LLM judging | **20%** |

`Final Score = 0.8 × Phase 1 Score + 0.2 × Phase 2 Score`

Only the **top 10 on the private leaderboard** advance to Phase 2, and only
entries that **pass parameter verification** are eligible for final ranking or
prizes — a top Phase 1 score with an oversized model scores nothing.

### Evaluation metric (Phase 1)

A custom composite, computed per-example against the reference doctor response,
then averaged over the test set:

```
Phase 1 Score = 0.50 × BERTScore
              + 0.30 × Token-level F1
              + 0.20 × ROUGE-L F1
```

**Implications we should actually design around:**
- Optimize the composite, **not** any single component. Report all three
  separately in every experiment so we can see which one is moving.
- 80% of the score (BERTScore + ROUGE-L) rewards *semantic and structural
  overlap* with the reference — not raw fluency and not clinical correctness.
  Response **length and phrasing style** are therefore first-class tuning
  knobs, alongside the model itself.
- Medical/clinical accuracy only enters via the 20% Phase 2 LLM judge. Don't
  over-index on it during Phase 1, but don't generate unsafe advice either
  (§9).
- We need a **local implementation of this exact metric** before any modeling
  work. BERTScore needs a Bengali-capable encoder — pin the model/version and
  record it, since BERTScore is not comparable across different backbones.

### Data

- **Language:** Bengali.
- **Input:** patient prompt/query. **Output (target):** expected doctor response.
- **Splits:** train (released) / public test (live leaderboard) / private test
  (revealed at close, determines who advances).
- **External data is allowed** for fine-tuning, but **must be disclosed** in the
  submission notes. Log every external source in `EXPERIMENTS/EXP-LOG.md` the
  moment we use it, so the Phase 2 write-up is a copy-paste job.
- The dataset is **CC BY-NC 4.0, competition use only** — never redistribute it,
  never push it to a public repo, never upload it to a third-party service.

## 2. Golden Rules (non-negotiable)

1. **NEVER submit to Kaggle without my explicit go-ahead.** Prepare the
   submission file, report the local validation score, tell me what you expect
   it to score, and *wait for me to say "submit"*. No exceptions, no "I'll just
   try it quickly."
2. **NEVER auto-submit inside a script, notebook, or scheduled task.**
   Submission is always a deliberate, human-approved step.
3. **Submissions are extremely scarce — 5 for the ENTIRE Phase 1** (see §6).
   Treat every one as a considered, irreversible decision.
4. **Always validate locally first.** Report the composite score *and* its three
   components, with the validation split scheme and seed, before proposing any
   submission.
5. **Check the parameter count before anything else.** Any experiment that
   loads or trains a model must print `sum(p.numel() for p in model.parameters())`
   and assert it is ≤ 3e9. An idea that can't pass this check is dead on
   arrival, no matter how good the score.
6. **One change at a time.** When comparing ideas, change a single variable so
   we can attribute score movement.
7. **Reproducibility is a rule, not a nicety.** Fix and log seeds; every
   experiment must be re-runnable from a single command. In Phase 2 our
   inference script must reproduce our leaderboard outputs "within a reasonable
   tolerance" — a non-reproducible submission is **disqualified**. Pin package
   versions, save decoding params (temperature, top-p, beams, max tokens, and
   the seed) alongside every submission.
8. **Never leak the test set** into training or fine-tuning, and never fit any
   transform on validation/test data. This is also an explicit
   disqualification-level rule in the rulebook (§8).
9. **Notebooks are mandatory for anything that produces a submission** (§4).

## 3. Model Constraints (rulebook §3 — read before proposing any model)

- **Any base LLM is allowed** provided it is ≤ 3B parameters at inference time.
- **Permitted:** fine-tuning, LoRA/adapters, quantization, distillation,
  prompt engineering.
- **Ensembling is permitted, but the parameter budget is shared** — the
  *combined* count of all models used at inference must stay under 3B. Two 2B
  models is a violation.
- **Quantization does not shrink the parameter count.** A 7B model in 4-bit is
  still 7B parameters and is disqualified. Parameter count, not memory.
- Anything running at inference counts — including a reranker, a retriever's
  encoder, or a BERTScore-style scorer if we ship one in the pipeline. When in
  doubt, count it and tell me.
- **Every candidate base model must be recorded** in `EXPERIMENTS/EXP-LOG.md`
  with its exact HF repo id, revision/commit, and measured parameter count.
- Misrepresenting parameter count is grounds for disqualification.

## 4. File Format Policy (notebooks vs. scripts)

- **Submissions & the modeling pipeline → always `.ipynb`.** Any work that
  produces (or is intended to produce) a Kaggle submission must be written
  **explicitly and in full** as a Jupyter notebook under `NOTEBOOKS/`: data
  loading, preprocessing, model loading/fine-tuning, generation, and writing
  the submission CSV, end to end. No hidden helper scripts doing the real work
  behind a thin notebook. This keeps submissions self-contained, reviewable,
  and Kaggle-kernel-friendly — and it *is* most of our Phase 2 deliverable.
- **Experiments → `.py` or `.ipynb`, Claude's choice.** For everything in
  `EXPERIMENTS/` — smoke tests, plumbing checks, ablations, quick probes — use
  whichever format is fastest to write and run.

## 5. Logging Discipline (do this every time, automatically)

### `RESULT.md` — the submission ledger
Update **every time a submission is made**. With only 5 submissions total, this
ledger is our whole record of leaderboard signal. Each entry records:
- Date/time of submission, and **which of the 5 it is** (e.g. "3 of 5")
- Which experiment / notebook produced it
- Base model + HF revision, and **measured parameter count**
- Local validation: composite score **and** BERTScore / Token-F1 / ROUGE-L
  separately, with split scheme + seed
- Decoding params (temperature, top-p, beams, max new tokens, seed)
- **Public leaderboard score once known**
- Wall-clock time to train + generate
- Any external data used (needed for the Phase 2 write-up)
- Short note on what was tried and the takeaway

### `EXPERIMENTS/` — the experiment workspace
- Every model idea, smoke test, or ablation lives here as its own script or
  notebook (e.g. `EXPERIMENTS/exp_003_qwen25_1p5b_lora.py`).
- Keep a **smoke test** path in each experiment (tiny data / few steps / few
  generations) so we can verify the pipeline end-to-end in seconds before
  committing GPU hours.
- **`EXPERIMENTS/EXP-LOG.md`** — append an entry whenever an experiment runs
  (smoke or full). Record: experiment id, date, what it does, command, base
  model + param count, local composite + components, runtime, external data
  used, and status/outcome. Chronological and terse.

### Naming
- Experiments: `exp_NNN_short-slug` (zero-padded, incrementing).
- Submission files: `SUBMISSIONS/sub_NNN_short-slug.csv` matching the experiment.

## 6. Submission Rules & Fair Play (rulebook §8)

- **Submission limit: 5 for all of Phase 1.** This is a *total*, not per-day —
  read that way in the rulebook, and it is the strictest reading, so we plan
  against it. (Flagged as worth confirming with organizers, see §11.)
- Final leaderboard rank uses the **last submission, or the one I explicitly
  select as final** before the deadline. Remind me to select the right one.
- **Forbidden, at any stage, on pain of disqualification:**
  - Accessing, reverse-engineering, or manually labelling the private test set
  - Using test inputs for training or fine-tuning
  - Submitting human-written outputs instead of model outputs
  - Exceeding the 3B cap or misrepresenting parameter count
  - Sharing private test data or Phase 2 submissions with other teams
- Organizers may request training logs, code, or proof of compliance at any
  time — another reason experiments must stay reproducible and logged.

## 7. Phase 2 Deliverables (start collecting these from day one)

If we make the top 10, we must submit **all four** by the Phase 2 deadline:

1. **Full inference script** — reproducible, documented, runnable end-to-end
2. **Model weights/checkpoint**, or a script that downloads them from a
   reproducible source
3. **A short write-up** — approach, base model, fine-tuning method, and any
   external data/tools used
4. **Environment/dependency file**

Because of this, keep a `requirements.txt` (or lockfile) current and keep the
write-up notes accumulating in `EXPERIMENTS/EXP-LOG.md` as we go. Do not leave
this to the end — the Phase 2 window is roughly a day.

## 8. Timeline (rulebook §7 — all deadlines GMT+6 / BD time)

| Milestone | Date |
|---|---|
| Team registration deadline | **August 2nd** |
| Competition opens / data released | **August 4th** |
| Phase 1 submission deadline (leaderboard closes) | **August 24th, 00:00 BDT** |
| Private leaderboard revealed · top 10 announced · Phase 2 opens | Immediately after close |
| Phase 2 submission deadline (model + inference script) | **August 25th** (time disputed — see §11) |
| LLM-judge results, final ranking & winners announced | **August 26th** |

**Prizes:** 1st 30,000 BDT · 2nd 10,000 BDT · 3rd 5,000 BDT. Ties for 1st–3rd
are broken by a rerun of Phase 2.

**Teams:** up to 4 members, finalized by August 2nd, one team per person.

## 9. Ethical & Medical Guardrails (rulebook §11)

- This is **research/education only**. Nothing we build is validated for
  clinical use and must not be presented as a real medical advice tool.
- Outputs containing harmful, unsafe, or clearly unethical medical advice can
  be **flagged and penalized** by the LLM judge in Phase 2. Safety is not just
  ethics here — it costs points.
- If a modeling choice trades measurable Phase 1 score against obviously unsafe
  generations, surface the tradeoff to me rather than silently taking the
  points.

## 10. Directory Layout

```
.
├── CLAUDE.md               # this file
├── Rulebook_Nascenia.pdf   # official rulebook — source of truth
├── RESULT.md               # submission ledger (update on every submission)
├── COMPETITION-LINK.txt    # the competition URL
├── plan.md                 # current strategy / roadmap
├── secrets.env             # Kaggle credential — NEVER print, commit, or leak
├── DATA/                   # competition data (downloaded via Kaggle API)
├── EDA/                    # exploratory analysis
├── NOTEBOOKS/              # submission-producing pipelines (.ipynb, mandatory)
├── SUBMISSIONS/            # generated submission CSVs
└── EXPERIMENTS/
    ├── EXP-LOG.md          # chronological experiment log
    └── exp_*.{py,ipynb}    # individual experiments (Claude's choice of format)
```

## 11. Open Questions / Rulebook Ambiguities

The full list, with rulebook citations and a ready-to-send email draft, lives in
[`QUESTIONS-FOR-ORGANIZERS.md`](QUESTIONS-FOR-ORGANIZERS.md) — keep that file as
the master copy and record answers there as they arrive. The headlines:

1. **Submission limit semantics.** §8 says "Submission limit: 5 during Phase 1",
   with no "per day". We plan for 5 *total*; worth confirming, since 5/day for
   ~20 days is a completely different strategy.
2. **Phase 2 deadline time.** §5.1 says **August 25th, 12 PM BD**; the §7
   timeline table says **August 25th, 00:00 BD**. Assume the earlier (00:00)
   until confirmed.
3. **Registration before opening.** Team registration closes **August 2nd** but
   the competition opens **August 4th** — verify the registration deadline is
   real and not a typo.
4. **No year is stated** anywhere in the rulebook. Confirm the calendar year
   before treating these dates as absolute.
5. **Competition URL** is not in the rulebook and `COMPETITION-LINK.txt` is
   empty — get the Kaggle link.
6. **Submission file format** (column names, whether output is raw Bengali text
   in a CSV, encoding/quoting rules) is not specified in the rulebook. Take it
   from `sample_submission.csv` once data is released; UTF-8 Bengali text in
   CSV is an easy place to silently corrupt a submission — verify a round-trip
   read/write before trusting any file.
7. **BERTScore backbone** used by the organizers' scorer is unspecified. Our
   local score will not match the leaderboard in absolute terms; treat local
   numbers as *relative* signal until we can calibrate against a real
   submission.

## 12. Environment Notes

- **No local NVIDIA GPU detected** (`nvidia-smi` not present). Fine-tuning a
  ~1–3B model is not going to happen on this machine — plan on Kaggle kernels
  (T4×2 / P100) or Colab for training, and keep the local box for data work,
  metric implementation, and analysis. Raise this with me before designing any
  experiment that assumes local GPU.
- **Python:** 3.14 (`C:\Program Files\Python314\python.exe`). This is very new,
  and `torch` / `transformers` / `peft` / `bitsandbytes` wheels may not exist
  for it yet. If a heavy dependency fails to install, **tell me before**
  switching approaches or Python versions.
- **Kaggle CLI:** installed as a package but not on PATH — invoke via
  `python -m kaggle ...`.
- **OS/Shell:** Windows 11, PowerShell primary. Prefer cross-platform Python
  over shell-specific scripting where practical.
- **Encoding:** Bengali text plus Windows `cp1252` default stdout is a
  reliable source of `UnicodeEncodeError`. Always write files with explicit
  `encoding='utf-8'` and avoid printing raw Bengali to the console.

## 13. Secrets & Safety

- `secrets.env` holds the Kaggle API token. **Never** echo its contents, paste
  it into logs, or include it in any file that could be shared/committed.
- The token is installed once into `~/.kaggle/kaggle.json` (chmod 600 on POSIX).
- If a `.gitignore` is added later, it must exclude `secrets.env`, `~/.kaggle/`,
  `DATA/`, and any model checkpoints.
- The competition dataset is CC BY-NC and must not be redistributed — no
  committing it, no uploading it to third-party services.

## 14. Default Workflow for a New Idea

1. Discuss the idea with me briefly (what and why).
2. **Confirm the parameter budget** — name the exact model(s) and their counts,
   and check the total is ≤ 3B.
3. Write/adjust an `EXPERIMENTS/exp_NNN_*` (`.py` or `.ipynb`, your choice)
   with a smoke-test mode.
4. Run the smoke test; confirm the pipeline is green.
5. Run the full experiment; capture the local composite score + all three
   components + runtime.
6. Append to `EXPERIMENTS/EXP-LOG.md`.
7. If the score is promising, build the full pipeline as a **notebook**
   (`.ipynb`) under `NOTEBOOKS/`, generate the submission CSV into
   `SUBMISSIONS/`, and **stop** — report to me, state which of our 5
   submissions this would consume, and wait for approval.
8. On my approval, submit; then update `RESULT.md` with the public score.
