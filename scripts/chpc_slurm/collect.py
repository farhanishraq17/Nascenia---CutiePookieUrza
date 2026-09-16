"""collect.py — one scoreboard over every arm that has landed.

    python collect.py              # markdown table, paste-ready for RESULTS.md
    python collect.py --json       # same data, machine-readable
    python collect.py --winner     # just the Tier-1 winner's dataset name, for submit.py

Reads each arm's own files — nothing is retyped by hand:
    <exp>/<arm>/dev.json           Token F1 / ROUGE-L / register read-out (04_decode.py)
    <exp>/<arm>/run.json           config, wall-clock, checkpoint hash
    <exp>/<arm>/ckpt/.../trainer_state.json   the eval trajectory -> peak step

🔴 Ranks on Token F1, never the local composite (mis-calibrated by ~0.118), and marks any
gap under the 0.0044 noise floor as noise rather than a result.

🔴 Ranks WITHIN a step budget, never across one. E05 showed 4,000 steps is roughly two thirds
of the way up the curve, so a 4,000-step arm and a converged one are not the same measurement
and must not share a ranking. Budget-capped arms are printed in their own block below.
"""

import argparse
import json
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
INCUMBENT_F1, INCUMBENT_RL = 0.7724, 0.7324
NOISE = 0.0044
CONV_BUDGET = 12000      # the budget every arm was re-run at once E05 peaked at 15,250


def pred_lb(f1, rl):
    """Calibrated on two real submissions 0.5 of Token F1 apart; fits both to ±0.0001."""
    return 0.4646 + 0.3098 * f1 + 0.2 * rl


def peak_step(armdir: Path):
    """Where the run peaked on composite, and the last step it reached. That is often the
    finding, not the score: last step < budget means early stopping fired and the run chose
    to stop; last step == budget means it ran out of steps and the score is a lower bound."""
    states = sorted(armdir.glob("ckpt/checkpoint-*/trainer_state.json"),
                    key=lambda p: int(p.parent.name.split("-")[-1]))
    hist = None
    if states:
        hist = json.loads(states[-1].read_text()).get("log_history", [])
    elif (armdir / "trainer_state.json").is_file():          # causal trainer writes this
        hist = json.loads((armdir / "trainer_state.json").read_text()).get("log_history", [])
    if not hist:
        return None, 0, None
    last = max((h["step"] for h in hist if "step" in h), default=None)
    evals = [h for h in hist if "eval_composite" in h or "composite" in h]
    if not evals:
        return None, 0, last
    key = "eval_composite" if "eval_composite" in evals[0] else "composite"
    best = max(evals, key=lambda h: h[key])
    return best.get("step"), len(evals), last


def scan():
    rows = []
    for expdir in sorted(PROJ.glob("E*_*")):
        for dev in sorted(expdir.glob("*/dev.json")):
            arm = dev.parent
            d = json.loads(dev.read_text(encoding="utf-8"))
            m = d.get("dev", {})
            run = {}
            if (arm / "run.json").is_file():
                run = json.loads((arm / "run.json").read_text(encoding="utf-8"))
            # Runs launched before run.json carried data_dir: recover the input from the
            # sbatch script that actually ran, not from the registry (which would report
            # the intent rather than the fact).
            data = Path(run.get("data_dir", "")).name
            if not data:
                sb = PROJ / "_slurm" / f"nasc-{expdir.name.split('_')[0]}-{arm.name}.sbatch"
                if sb.is_file():
                    for tok in sb.read_text().split():
                        if tok.startswith("../data/"):
                            data = tok.split("/")[-1]
                            break
            step, n_evals, last = peak_step(arm)
            # The step budget the arm was given, straight from its own run.json — and whether
            # it ran out of it. A run that hit its cap never satisfied early stopping, so its
            # score is a lower bound; if that cap was also below CONV_BUDGET the arm is a
            # short probe and cannot be ranked against a converged one at all.
            budget = run.get("max_steps")
            hit_cap = budget is not None and last is not None and last >= budget
            capped = hit_cap and budget < CONV_BUDGET
            f1, rl = m.get("token_f1"), m.get("rouge_l")
            reg = d.get("register", {})
            rows.append(dict(
                exp=expdir.name.split("_")[0], arm=arm.name,
                model=(run.get("model") or "?").split("/")[-1],
                data=data or "-",
                token_f1=f1, rouge_l=rl,
                pred_lb=pred_lb(f1, rl) if f1 is not None and rl is not None else None,
                delta=(f1 - INCUMBENT_F1) if f1 is not None else None,
                budget=budget, last_step=last, hit_cap=hit_cap, capped=capped,
                peak_step=step, n_evals=n_evals,
                tokens=m.get("mean_pred_tokens"),
                helo=reg.get("helo_opener_pct"), nasenia=reg.get("nasenia_pct"),
                hours=round(run.get("train_minutes", 0) / 60, 2) or None,
                gpu=run.get("gpu", ""), precision=run.get("precision", ""),
                ckpt=str((arm / "best").resolve()) if (arm / "best").is_dir() else "🔴 MISSING",
            ))
    # Converged arms first, capped probes after — never interleaved, at any score.
    rows.sort(key=lambda r: (r["capped"], r["token_f1"] is None, -(r["token_f1"] or 0)))
    return rows


def verdict(r):
    if r["token_f1"] is None:
        return "no score"
    if r["capped"]:
        return f"🔶 Δ{r['delta']:+.4f} — lower bound, stopped at the {r['budget']}-step cap"
    if abs(r["delta"]) < NOISE:
        return f"= incumbent (Δ{r['delta']:+.4f}, inside noise)"
    return ("✅ beats incumbent" if r["delta"] > 0 else "❌ below incumbent") + \
           f" {r['delta']:+.4f}"


def table(rows, title, note=None):
    """One block, one step budget class. Two blocks never share a ranking."""
    if not rows:
        return
    print(f"\n### {title}\n")
    if note:
        print(note + "\n")
    print("| Exp | Arm | Model | Input | Token F1 | ROUGE-L | pred LB | vs 0.7724 | "
          "budget | peak step | হেলো% | নাসেনিয়া% | tokens | hours | ckpt |")
    print("|" + "---|" * 15)
    for r in rows:
        fmt = lambda v, p=4: "" if v is None else f"{v:.{p}f}"  # noqa: E731
        budget = "?" if r["budget"] is None else f"{r['budget']}{'†' if r['hit_cap'] else ''}"
        print(f"| {r['exp']} | {r['arm']} | {r['model']} | {r['data']} | "
              f"**{fmt(r['token_f1'])}** | {fmt(r['rouge_l'])} | {fmt(r['pred_lb'])} | "
              f"{verdict(r)} | {budget} | {r['peak_step'] or ''} | {fmt(r['helo'],1)} | "
              f"{fmt(r['nasenia'],1)} | {fmt(r['tokens'],1)} | {r['hours'] or ''} | "
              f"{'✅' if 'MISSING' not in r['ckpt'] else '🔴 MISSING'} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--winner", action="store_true",
                    help="print the Tier-1 (E01/E02/E03/E04/E05) winner's dataset")
    a = ap.parse_args()
    rows = scan()

    if a.winner:
        tier1 = [r for r in rows if r["exp"] in {"E01", "E02", "E03", "E04", "E05"}
                 and r["token_f1"] is not None]
        print(tier1[0]["data"] if tier1 else "")
        return
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return

    if not rows:
        print("no arms have produced a dev.json yet")
        return
    table([r for r in rows if not r["capped"]],
          f"Converged arms — early-stopped, or given ≥ {CONV_BUDGET:,} steps")
    table([r for r in rows if r["capped"]],
          "🔶 Budget-capped probes — ranked separately, NOT against the block above",
          f"Each of these ran out of steps at a budget below {CONV_BUDGET:,} and was still "
          f"climbing when it stopped. Every score here is a LOWER BOUND: E05/main gained "
          f"+0.0205 Token F1 between step 4,000 and its peak at 15,250. Do not compare a row "
          f"here with a row above — re-run the arm at {CONV_BUDGET:,} first.")
    print(f"\nincumbent Token F1 {INCUMBENT_F1} · ROUGE-L {INCUMBENT_RL} · LB 0.85030 · "
          f"noise floor {NOISE} · convergence budget {CONV_BUDGET}")
    print("† = the run reached its step budget, so early stopping never fired and even this "
          "score is a lower bound.")
    print("references: হেলো opener 76.4% · নাসেনিয়া 50.0%   |   "
          "draft: 0.06% · 0.00%")


if __name__ == "__main__":
    main()
