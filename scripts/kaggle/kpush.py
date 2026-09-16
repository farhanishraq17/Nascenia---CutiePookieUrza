"""Guarded kaggle kernels push — REFUSES to push a GPU notebook that is not pinned to T4.

Usage:  python kpush.py <push-dir> [token-suffix]
        python kpush.py KAGGLE_PUSH/submit_arms/c-lr1e3
        python kpush.py KAGGLE_PUSH/sweep6/G-lr3e3 ishmam1

Why this exists: `kaggle kernels push` reads `machine_shape` from kernel-metadata.json, and
when it is absent Kaggle assigns a **P100 (sm_60)**, which Kaggle's own PyTorch build cannot
run — it ships kernels for sm_70+ only. That silently burned ~8 runs. `"enable_gpu": true`
does NOT name a GPU type. The correct value is "NvidiaTeslaT4", confirmed by pulling the
metadata of a kernel that had been set to T4x2 in the UI.
"""
import json, os, subprocess, sys

REQUIRED = "NvidiaTeslaT4"
ROOT = r"D:\Project Based Learning\Nascenia_Datathon"
sys.stdout.reconfigure(encoding="utf-8")

def main(argv):
    if not argv:
        print(__doc__); return 2
    d = argv[0] if os.path.isabs(argv[0]) else os.path.join(ROOT, argv[0])
    token = argv[1] if len(argv) > 1 else None

    meta_path = os.path.join(d, "kernel-metadata.json")
    if not os.path.isfile(meta_path):
        print(f"❌ no kernel-metadata.json in {d}"); return 1
    meta = json.load(open(meta_path, encoding="utf-8"))

    if meta.get("enable_gpu"):
        shape = meta.get("machine_shape")
        if shape != REQUIRED:
            print(f"❌ REFUSING TO PUSH {meta.get('id')}\n"
                  f"   enable_gpu is true but machine_shape is {shape!r}, not {REQUIRED!r}.\n"
                  f"   Kaggle would assign a P100 (sm_60) and the run would die at the\n"
                  f"   hardware gate. Add \"machine_shape\": \"{REQUIRED}\" to kernel-metadata.json.")
            return 1

    # The account is part of the target, not a detail: a push without the right token
    # silently re-owns the kernel to whoever authenticates (this already happened once).
    owner = meta.get("id", "/").split("/")[0]
    env = dict(os.environ, PYTHONUTF8="1")
    if token:
        env["KAGGLE_API_TOKEN"] = os.path.expanduser(f"~/.kaggle/access_token.{token}")
    print(f"pushing {meta.get('id')}  (owner {owner}, machine_shape {meta.get('machine_shape')}, "
          f"token {token or 'default'})")

    r = subprocess.run(["kaggle", "kernels", "push", "-p", d, "--accelerator", REQUIRED],
                       env=env, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print(out)
    if f"/{owner}/" not in out and "successfully pushed" in out:
        print(f"⚠️  pushed, but the URL is not under {owner} — wrong token?")
        return 1
    return 0 if "successfully pushed" in out else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
