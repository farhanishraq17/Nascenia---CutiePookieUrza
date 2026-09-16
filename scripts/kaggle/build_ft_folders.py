"""Create FINE_TUNING_NOTEBOOKS/<arm> folders and populate from what exists locally."""
import io, json, os, shutil, sys, glob
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\Project Based Learning\Nascenia_Datathon"
FT = os.path.join(ROOT, "FINE_TUNING_NOTEBOOKS")

# (folder-name, sweep tag, kaggle owner, kernel slug, push dir, sweep out dir)
ARMS = [
    ("3) Bangla-T5-SWEEP-A-lr3e4",     "A-lr3e4",     "salam2026",   "nascenia-sweep-a-lr3e4",     "A-lr3e4",     "A"),
    ("4) Bangla-T5-SWEEP-B-4epoch",    "B-4epoch",    "salam2026",   "nascenia-sweep-b-4epoch",    "B-4epoch",    "B"),
    ("5) Bangla-T5-SWEEP-C-lr1e3",     "C-lr1e3",     "tashintahir", "nascenia-sweep-c-lr1e3",     "C-lr1e3",     "C"),
    ("6) Bangla-T5-SWEEP-D-smooth",    "D-smooth",    "tashintahir", "nascenia-sweep-d-smooth",    "D-smooth",    "D"),
    ("7) Bangla-T5-SWEEP-E-lr1e3-4ep", "E-lr1e3-4ep", "ishmamahmid", "nascenia-sweep-e-lr1e3-4ep", "E-lr1e3-4ep", "E"),
    ("8) Bangla-T5-SWEEP-F-batch32",   "F-batch32",   "ishmamahmid", "nascenia-sweep-f-batch32",   "F-batch32",   "F"),
    ("9) Bangla-T5-SWEEP-G-lr3e3",     "G-lr3e3",     "ishmamahmid", "nascenia-sweep-g-lr3e3",     "G-lr3e3",     "G"),
]

missing = []
for folder, tag, owner, slug, pushdir, outdir in ARMS:
    dest = os.path.join(FT, folder)
    os.makedirs(dest, exist_ok=True)
    os.makedirs(os.path.join(dest, "nascenia-code"), exist_ok=True)
    got = []

    # 1) the notebook that was pushed
    src_nb = os.path.join(ROOT, "KAGGLE_PUSH", "sweep6", pushdir, f"{slug}.ipynb")
    if os.path.isfile(src_nb):
        shutil.copy(src_nb, dest); got.append("notebook")
    else:
        missing.append(f"{tag}: notebook {src_nb}")

    # 2) kernel metadata
    src_meta = os.path.join(ROOT, "KAGGLE_PUSH", "sweep6", pushdir, "kernel-metadata.json")
    if os.path.isfile(src_meta):
        shutil.copy(src_meta, dest); got.append("metadata")

    # 3) the exact .py code the run used
    n_py = 0
    for f in glob.glob(os.path.join(ROOT, "SWEEP_OUT", outdir, "code", "*.py")):
        shutil.copy(f, os.path.join(dest, "nascenia-code")); n_py += 1
    if n_py == 0:  # fall back to the pushed code dataset
        for f in glob.glob(os.path.join(ROOT, "NOTEBOOKS", "*.py")):
            if os.path.basename(f) in {"metric.py", "01_prep.py", "02_train_t5.py", "04_decode.py"}:
                shutil.copy(f, os.path.join(dest, "nascenia-code")); n_py += 1
        got.append(f"code x{n_py} (from NOTEBOOKS, run copy unavailable)")
    else:
        got.append(f"code x{n_py}")

    # 4) results: run.json + every trainer_state.json (the eval trajectory).
    # Skip runs/smoke — the 1000-row warmup writes its own run.json, and copying it
    # to the same destination name silently overwrote the real 400-minute record.
    for rj in glob.glob(os.path.join(ROOT, "SWEEP_OUT", outdir, "runs", "*", "run.json")):
        if os.path.basename(os.path.dirname(rj)) == "smoke":
            continue
        shutil.copy(rj, dest); got.append("run.json")
    ts = sorted(g for g in glob.glob(os.path.join(ROOT, "SWEEP_OUT", outdir, "runs", "*", "ckpt", "checkpoint-*", "trainer_state.json"))
                if os.sep + "smoke" + os.sep not in g)
    for t in ts:
        step = t.split("checkpoint-")[1].split(os.sep)[0]
        shutil.copy(t, os.path.join(dest, f"trainer_state_step{step}.json"));
    if ts:
        got.append(f"trainer_state x{len(ts)}")
    if not glob.glob(os.path.join(dest, "run.json")) and not ts:
        missing.append(f"{tag}: NO RESULTS — output not downloaded yet")

    # 5) prep report, if the download included it
    pr = os.path.join(ROOT, "SWEEP_OUT", outdir, "processed", "prep_report.txt")
    if os.path.isfile(pr):
        shutil.copy(pr, dest); got.append("prep_report")

    print(f"{folder:34s} <- {', '.join(got)}")

print()
if missing:
    print("MISSING:")
    for m in missing:
        print("  -", m)
else:
    print("nothing missing")
