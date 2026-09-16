"""registry.py — every experiment arm in the program, as data.

One entry per ARM (not per experiment): E18 has 6 bases, E06 has 3 learning rates, and
each of those is its own SLURM job on its own GPU. `submit.py` turns an entry into a
sbatch script; nothing here knows about SLURM.

Layout each arm produces, which is the layout README.md's "Reporting back" demands:

    <experiment>/<arm>/best/            the weights
    <experiment>/<arm>/run.json         config + dev metrics, BESIDE the weights
    <experiment>/<arm>/ckpt/            checkpoints (trainer_state.json = the trajectory)
    <experiment>/<arm>/dev.json         decode record from 04_decode.py

Hardware choices (per HANDOFF_PROMPTS "YOU DECIDE THE HARDWARE"): one H100 NVL per arm,
bf16 (sm_90), per-device batch x accum straight from each EXPERIMENT.md so the EFFECTIVE
batch stays 64. Nothing here shortens a run, coarsens an eval grid, or drops an arm.
"""

# The one number that is not ours to change. Asserted for every arm below.
EFFECTIVE_BATCH = 64

BANGLAT5 = "csebuetnlp/banglat5"

# ---------------------------------------------------------------------------
# fields:
#   exp    experiment folder
#   arm    subdirectory + run name (single-arm experiments use "main")
#   data   dataset dir under data/
#   model  HF id
#   src/tgt        sequence caps, from EXPERIMENT.md
#   bs/accum       per-device batch x grad accum  (bs*accum must be EFFECTIVE_BATCH)
#   steps          hard step budget
#   lr, warmup     from EXPERIMENT.md
#   patience       early-stopping patience in evals (each eval = 250 steps)
#   save_limit     rolling checkpoint count; 0 = keep every one (E05 only)
# ---------------------------------------------------------------------------
ARMS = [
    # ---------------- Wave 1 ----------------
    # E05 doubles as the re-baselined draft_only control for E01/E02: same sequence
    # caps, same budget grid, only the input differs.
    dict(exp="E05_train_to_convergence", arm="main", data="draft_only", model=BANGLAT5,
         src=768, tgt=512, bs=32, accum=2, steps=30000, lr=1e-3, warmup=200,
         patience=8, save_limit=0, seed=11, wave=1,
         note="30k budget with patience 8; EXPERIMENT.md's 10k is a floor, not a cap"),

    dict(exp="E01_add_english", arm="main", data="english_draft", model=BANGLAT5,
         src=768, tgt=512, bs=32, accum=2, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=1),

    dict(exp="E02_add_question", arm="main", data="question_draft", model=BANGLAT5,
         src=640, tgt=512, bs=32, accum=2, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=1),

    dict(exp="E08_mt5_control", arm="main", data="draft_only", model="google/mt5-base",
         src=640, tgt=640, bs=16, accum=4, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=1),

    # 🔴 Added 2026-08-09 once E05 and E01 had both reported, because the decision table
    # says so outright: "E05 peaks >> 2,750  ->  free score was being left on the table
    # -> re-run every Tier-1 winner at the longer budget". Measured at matched 768/512
    # caps and a matched 4,000-step budget:
    #     draft_only (E05 @4000)     0.7807
    #     english_draft (E01 @4000)  0.8027   <- +0.0220, 5x the noise floor
    # and E05 kept climbing to 0.7926 by step 8,250 (+0.0119 past its own 4,000).
    # This arm is the only run that combines both confirmed gains.
    dict(exp="E05_train_to_convergence", arm="english_draft", data="english_draft",
         model=BANGLAT5, src=768, tgt=512, bs=32, accum=2, steps=30000, lr=1e-3,
         warmup=200, patience=8, save_limit=0, seed=11, wave=2,
         note="Tier-1 winner at the convergence budget — the headline follow-up"),

    # ---------------- Wave 2 ----------------
    # Input combinations that only make sense once E01/E02 report, plus the LR re-tune.
    dict(exp="E03_all_inputs", arm="main", data="all_inputs", model=BANGLAT5,
         src=1024, tgt=512, bs=16, accum=4, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),

    dict(exp="E04_english_only", arm="main", data="english_only", model=BANGLAT5,
         src=640, tgt=512, bs=32, accum=2, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),

    dict(exp="E06_lr_retune", arm="lr3e-4", data="WINNER", model=BANGLAT5,
         src=768, tgt=512, bs=32, accum=2, steps=4000, lr=3e-4, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),
    dict(exp="E06_lr_retune", arm="lr1e-3", data="WINNER", model=BANGLAT5,
         src=768, tgt=512, bs=32, accum=2, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),
    dict(exp="E06_lr_retune", arm="lr3e-3", data="WINNER", model=BANGLAT5,
         src=768, tgt=512, bs=32, accum=2, steps=4000, lr=3e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),

    # E07 asks what truncation cost, so it is the only arm allowed longer caps.
    dict(exp="E07_no_truncation", arm="main", data="all_inputs", model=BANGLAT5,
         src=1280, tgt=768, bs=8, accum=8, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),

    dict(exp="E09_mt5_best_input", arm="main", data="WINNER", model="google/mt5-base",
         src=1024, tgt=640, bs=16, accum=4, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2,
         gate="only if E08 is competitive with the incumbent"),

    # E13 trains on transfer + Q->A jointly. Its dataset is built by
    # code/11_build_stage_datasets.py, which asserts 0 dev/test id overlap.
    # 🔴 It must ALSO be decoded against ../data/question_only — the Q->A score is half
    # the point (robustness insurance if the alignment route is ever closed off).
    dict(exp="E13_multitask_qa", arm="main", data="multitask_WINNER", model=BANGLAT5,
         src=768, tgt=512, bs=32, accum=2, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=3),

    # ---- E18 model zoo. Decoders are a different trainer AND a different LR. ----
    dict(exp="E18_model_zoo", arm="banglat5", data="draft_only", model=BANGLAT5,
         src=384, tgt=256, bs=8, accum=8, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2,
         note="the zoo's own control, at the incumbent's 384/256"),
    dict(exp="E18_model_zoo", arm="indicbart", data="draft_only", model="ai4bharat/IndicBART",
         src=384, tgt=256, bs=8, accum=8, steps=4000, lr=1e-3, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),
    # 🔴 LENGTH, corrected 2026-08-09 after the first pass was invalidated.
    # EXPERIMENT.md says "1024 total" for decoders, written when the only tokenizer in
    # play was BanglaT5's. Measured on this corpus: one answer costs ~142 BanglaT5
    # subwords but ~689 Qwen subwords (p95 1149). At max_len 1024 the prompt was being
    # shredded to fit, and --max-new-tokens 320 capped output at ~46 metric words against
    # a ~100-word reference. All three arms scored ~0.48 — the cap, not the model.
    # These caps are the SAME EXPERIMENT expressed in each tokenizer's units.
    dict(exp="E18_model_zoo", arm="qwen3_1p7b", data="draft_only", model="Qwen/Qwen3-1.7B",
         kind="causal", max_len=2560, min_new=200, max_new=1280,
         bs=8, accum=8, steps=4000, lr=2e-5, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),
    dict(exp="E18_model_zoo", arm="qwen25_1p5b", data="draft_only",
         model="Qwen/Qwen2.5-1.5B-Instruct",
         kind="causal", max_len=2560, min_new=200, max_new=1280,
         bs=8, accum=8, steps=4000, lr=2e-5, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),
    dict(exp="E18_model_zoo", arm="qwen3_0p6b", data="draft_only", model="Qwen/Qwen3-0.6B",
         kind="causal", max_len=2560, min_new=200, max_new=1280,
         bs=8, accum=8, steps=4000, lr=3e-5, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2),
    # 🔴 gemma_2_2b_it and llama32_1b are GATED on huggingface.co and return 401 with this
    # account's token. They are specified, not dropped — see E18_model_zoo/RESULTS.md.
    dict(exp="E18_model_zoo", arm="gemma_2_2b_it", data="draft_only",
         model="google/gemma-2-2b-it",
         kind="causal", max_len=2560, min_new=200, max_new=1280, bs=8, accum=8, steps=4000, lr=2e-5, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2,
         blocked="HF 401 — licence not accepted by this account"),
    dict(exp="E18_model_zoo", arm="llama32_1b", data="draft_only",
         model="meta-llama/Llama-3.2-1B-Instruct",
         kind="causal", max_len=2560, min_new=200, max_new=1280, bs=8, accum=8, steps=4000, lr=2e-5, warmup=200,
         patience=5, save_limit=2, seed=11, wave=2,
         blocked="HF 401 — licence not accepted by this account"),
]

# ---- CONVERGENCE SWEEP, added 2026-08-10 after the LB came back at 0.88008 ----------
# E05/english_draft (12,000 steps) scored 0.88008 vs the 4,000-step E01's ~0.850 lineage.
# Measured: 4k -> 12k was worth +0.0225 Token F1 on english_draft. EVERY other input
# combination was only ever run to 4,000 steps and all of them tie E01 there:
#     all_inputs (E03) 0.8035 · all_inputs untruncated (E07) 0.8042 · E01 0.8032
# So their 4k numbers are lower bounds and the ranking between inputs at CONVERGENCE is
# simply unknown. That is the open question with the best expected value on the board.
# Sized for 24 GB RTX PRO 4000s: effective batch stays 64, reached as 4x16 or 8x8.
CONV = [
    ("E03_all_inputs",      "all_inputs",    1024, 512,  4, 16, 1e-3),
    ("E07_no_truncation",   "all_inputs",    1280, 768,  2, 32, 1e-3),
    ("E04_english_only",    "english_only",   640, 512,  8,  8, 1e-3),
    ("E02_add_question",    "question_draft", 640, 512,  8,  8, 1e-3),
    ("E13_multitask_qa",    "multitask_english_draft", 768, 512, 4, 16, 1e-3),
]
for _exp, _data, _src, _tgt, _bs, _ac, _lr in CONV:
    ARMS.append(dict(exp=_exp, arm="conv12k", data=_data, model=BANGLAT5,
                     src=_src, tgt=_tgt, bs=_bs, accum=_ac, steps=12000, lr=_lr,
                     warmup=200, patience=8, save_limit=2, seed=11, wave=4))
# lr 3e-3 tied 1e-3 at 4,000 steps (0.8040 vs 0.8032). E05 showed the peak moves a long
# way out, and on the old question->answer task a higher LR reached its peak SOONER and
# LOWER — untested here. This is the only arm that asks whether that holds at convergence.
ARMS.append(dict(exp="E06_lr_retune", arm="conv12k-lr3e-3", data="english_draft",
                 model=BANGLAT5, src=768, tgt=512, bs=4, accum=16, steps=12000,
                 lr=3e-3, warmup=200, patience=8, save_limit=2, seed=11, wave=4))

# ---- Qwen3.5 decoder arms, added 2026-08-10 -----------------------------------------
# Measured on this corpus, tokens per Bengali answer:
#     BanglaT5 142 · mT5 271 · Qwen3 689 · **Qwen3.5 294**
# Qwen3.5's vocab grew 151k -> 248k and more than HALVED Qwen3's Bengali handicap
# (4.85x -> 2.07x, i.e. mT5-class). That is the mechanism NLP4Health credited for
# Gemma-2-2B beating encoder-decoders, and it is the first time a Qwen model has been a
# credible carrier for Bengali generation here.
# 🔴 Params verified by LOADING the model, not from the name (trap #0):
#     Qwen3.5-0.8B =   752,393,024   Qwen3.5-2B = 1,881,825,088   both within the 3B cap.
# Lengths from the same measurement: target p95 696, source p95 673 -> max_len 1536
# covers prompt+answer, max_new 768 clears the p95 the length guard asserts against.
# Needs transformers>=5 (model_type qwen3_5 is absent from the pinned 4.57.3), so these
# arms carry their own venv; the BanglaT5 pin is untouched.
Q35 = "/scratch/general/nfs1/u1592009/envs/nascenia_q35"
# 🔴 The two sizes need DIFFERENT memory profiles and must not share one loop body.
# Measured twice on a 24 GB card: the 1.88B arm needs ~28 GB with AdamW at batch 2 and
# OOMs at any batch >= 2. Adafactor factors the second moment and batch 1 halves the
# 248k-vocab logits tensor; effective batch stays 64 either way, so the experiment is
# unchanged and only the route to it differs.
for _arm, _model, _lr, _bs, _ac, _opt in [
        ("qwen35_0p8b", "Qwen/Qwen3.5-0.8B", 3e-5, 2, 32, "adamw_torch"),
        ("qwen35_2b",   "Qwen/Qwen3.5-2B",   2e-5, 1, 64, "adafactor")]:
    ARMS.append(dict(exp="E18_model_zoo", arm=_arm, data="draft_only", model=_model,
                     kind="causal", max_len=1536, min_new=120, max_new=768,
                     bs=_bs, accum=_ac, optim=_opt, steps=4000, lr=_lr, warmup=200,
                     patience=5, save_limit=2, seed=11, wave=4, venv=Q35))

# ---- Unblocked 2026-08-10: SECRETS.env holds a DIFFERENT HF token (account
# omarhawktuah) that has accepted Gemma's licence, where the env HF_TOKEN is dead.
# 🔴 Params verified by loading: 2,614,341,888 — within the 3B cap with 386M to spare,
# so it fits alone but leaves no ensemble room. Lengths measured through ITS tokenizer:
# target p95 597, source p95 555 -> max_len 1536 / max_new 640.
# adafactor because AdamW's fp32 moments alone are ~31 GB for 2.6B on a 24 GB card.
ARMS.append(dict(exp="E18_model_zoo", arm="gemma2_2b_it", data="draft_only",
                 model="google/gemma-2-2b-it", kind="causal",
                 max_len=1536, min_new=100, max_new=640, optim="adafactor",
                 bs=1, accum=64, steps=4000, lr=2e-5, warmup=200,
                 patience=5, save_limit=2, seed=11, wave=4))
# E12 scored 0.8060 at 4k — 2nd best of the 4k arms — and was never taken to convergence.
ARMS.append(dict(exp="E12_warmstart", arm="conv12k", data="english_draft", model=BANGLAT5,
                 src=768, tgt=512, bs=2, accum=32, steps=12000, lr=1e-3, warmup=200,
                 patience=8, save_limit=2, seed=11, wave=4))
# E09 closes the mT5 line at convergence rather than leaving it judged at 4k only.
ARMS.append(dict(exp="E09_mt5_best_input", arm="conv12k", data="english_draft",
                 model="google/mt5-base", src=1024, tgt=640, bs=2, accum=32,
                 steps=12000, lr=1e-3, warmup=200, patience=8, save_limit=2,
                 seed=11, wave=4))

# ---- E19b: the champion's SCHEDULE, which E19's ten seeds never had -----------------
# E19 ran every seed at a FIXED 12,000 steps. The champion ran max_steps 30,000 with
# patience 8 and happened to peak at 12,000 — but it was free to keep going and they were
# not. So "does a seed ever run past 12k and land higher?" is untested: E19 could not
# answer it by construction. These three carry the champion's schedule.
# They also re-measure whether 0.8328 is a real level or a lucky draw: E19's ten seeds
# spanned 0.8267-0.8319 under identical decoding, so the champion sits ~0.001 above the
# best of ten. Three more samples tighten that.
for _seed in (777, 2468, 31337):
    ARMS.append(dict(exp="E19_multiseed_ensemble", arm=f"sched{_seed}",
                     data="english_draft", model=BANGLAT5, src=768, tgt=512,
                     bs=8, accum=8, steps=30000, lr=1e-3, warmup=200,
                     patience=8, save_limit=2, seed=_seed, wave=5))

# ---- E23: the last data lever with a mechanism behind it ----------------------------
# Measured 2026-08-12: the training data is clean. Alignment is near-perfect (median
# draft<->target Token F1 0.604; only 0.11% of pairs below 0.10), duplicates are 2.15% and
# degenerate targets 0.84%. So there is no pool of noise to remove — EXCEPT one thing with
# an actual mechanism: 3,671 rows have targets under 40 words against a ~100-word reference
# distribution. Those teach the model to stop early, and now that the shipped decoder uses
# min_new_tokens 0 the model is free to act on it. Length calibration feeds the BERTScore
# term that the 0.89347 submission proved is LIVE (it moved 0.9442 -> 0.9644).
# Everything else is identical to the champion, so the filter is the only variable.
# 🔴 Expected to land inside the noise floor. Recorded as a prediction, not a hope.
for _arm, _data in [("len40", "english_draft_len40"), ("clean", "english_draft_clean")]:
    ARMS.append(dict(exp="E23_data_filter", arm=_arm, data=_data, model=BANGLAT5,
                     src=768, tgt=512, bs=8, accum=8, steps=12000, lr=1e-3, warmup=200,
                     patience=8, save_limit=2, seed=11, wave=5))

# ---- E23 dose-response + paired seeds --------------------------------------------
# A single filtered arm cannot be read: the expected effect (~0.005) is the size of the
# seed spread E19 measured (0.8204-0.8258 across ten seeds). Two things make it readable:
#   DOSE  — filter at 20 / 40 / 60 words. A real length-calibration mechanism should be
#           monotone in filter strength; noise will not be.
#   PAIRED— every arm has an unfiltered twin at the SAME seed and batch split among E19's
#           seeds (bs 8x8, 12,000 steps, english_draft), so each is a matched comparison
#           rather than a comparison against a differently-configured champion.
for _arm, _data, _seed in [("len20", "english_draft_len20", 11),
                           ("len60", "english_draft_len60", 11),
                           ("len40_s23", "english_draft_len40", 23),
                           ("clean_s23", "english_draft_clean", 23)]:
    ARMS.append(dict(exp="E23_data_filter", arm=_arm, data=_data, model=BANGLAT5,
                     src=768, tgt=512, bs=8, accum=8, steps=12000, lr=1e-3, warmup=200,
                     patience=8, save_limit=2, seed=_seed, wave=5))

# ---- E23 factorial completion ------------------------------------------------------
# E23 as first run left a hole. `clean` = short-filter AND dedup, and it is the only cell
# with a positive delta (+0.0019). But `len40` (short-filter alone) is -0.0002 / +0.0001
# across two seeds — so if clean's gain is real, DEDUP is what produced it, and dedup
# alone was never run. Three cells x three seeds makes the 2x2 readable:
#     len40  = short only     dedup = dedup only     clean = both
# with unfiltered twins already measured at the same seeds among E19's ten.
for _arm, _data, _seed in [("dedup", "english_draft_dedup", 11),
                           ("dedup_s23", "english_draft_dedup", 23),
                           ("dedup_s42", "english_draft_dedup", 42),
                           ("len40_s42", "english_draft_len40", 42),
                           ("clean_s42", "english_draft_clean", 42)]:
    ARMS.append(dict(exp="E23_data_filter", arm=_arm, data=_data, model=BANGLAT5,
                     src=768, tgt=512, bs=4, accum=16, steps=12000, lr=1e-3, warmup=200,
                     patience=8, save_limit=2, seed=_seed, wave=5))

# ---- E21 arm A + E22 arm B ----------------------------------------------------------
# E21 A1/A2: every training row gets a SECOND draft, produced by round-tripping the real
# target through NLLB (bn->en->bn). The target is never synthesized — only the input side.
# Verified before training: the NLLB round-trip draft shares only 0.4147 Token F1 with the
# production Google draft, so it is genuinely another point in draft space rather than a
# duplicate (E21's spec warns that D' ~= D would make the augmentation pointless).
# A2 additionally tags augmented rows with <synthetic>.
# E22 arm B: prepend the nearest TRAIN target as a style exemplar (char-TFIDF retrieval,
# index over train only, a train row may not retrieve itself).
for _exp, _arm, _data in [("E21_synthetic_pairs", "A1", "english_draft_a1"),
                          ("E21_synthetic_pairs", "A2", "english_draft_a2"),
                          ("E22_retrieval", "B", "english_draft_rag")]:
    ARMS.append(dict(exp=_exp, arm=_arm, data=_data, model=BANGLAT5,
                     src=768, tgt=512, bs=8, accum=8, steps=12000, lr=1e-3, warmup=200,
                     patience=8, save_limit=2, seed=11, wave=6))

# ---- E19: ten seeds of the Tier-1 winner. Config identical; seed is the variable. ----
# Appended programmatically because ten near-identical literals hide the one field
# that differs.
for _seed in (11, 23, 42, 99, 555, 1337, 2024, 7, 21, 314):
    ARMS.append(dict(exp="E19_multiseed_ensemble", arm=f"seed{_seed}", data="WINNER",
                     model=BANGLAT5, src=768, tgt=512, bs=32, accum=2,
                     steps="E05", lr=1e-3, warmup=200, patience=5, save_limit=2,
                     seed=_seed, wave=3,
                     gate="steps = whatever E05 establishes as the convergence point"))


def validate(arms=ARMS):
    """Effective batch is the experiment, not a speed knob. Fail loudly, not silently."""
    bad = [f"{a['exp']}/{a['arm']}: {a['bs']}x{a['accum']}={a['bs'] * a['accum']}"
           for a in arms if a["bs"] * a["accum"] != EFFECTIVE_BATCH]
    assert not bad, "effective batch != 64 for: " + "; ".join(bad)
    dupes = [k for k in {f"{a['exp']}/{a['arm']}" for a in arms}
             if sum(1 for a in arms if f"{a['exp']}/{a['arm']}" == k) > 1]
    assert not dupes, f"duplicate arm ids: {dupes}"
    return True


if __name__ == "__main__":
    validate()
    for a in ARMS:
        flag = " 🔴BLOCKED" if a.get("blocked") else (" ⏳gated" if a.get("gate") else "")
        print(f"wave {a['wave']}  {a['exp']:28s} {a['arm']:14s} "
              f"{a['data']:14s} {a['model']:30s} {str(a['steps']):>6s} steps  "
              f"{a['bs']}x{a['accum']}  lr {a['lr']:<7} {a.get('kind','seq2seq')}{flag}")
    n_blocked = sum(1 for a in ARMS if a.get("blocked"))
    print(f"\n{len(ARMS)} arms at effective batch {EFFECTIVE_BATCH}"
          f"  ({n_blocked} blocked upstream)")
