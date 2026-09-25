# Specialist swap: D1 → X5 @ lr 1e-5

**Status:** prepared, not applied. The bundle still ships **D1**. Applying it needs one file
transfer off CHPC and one command.

---

## Why

Phase 2's score is an **LLM judge** scoring *"tone, completeness, clarity as a doctor's response"*
(rules §5.3). It is not Token F1. The shipped specialist is the weaker arm on the one axis the
judge can most easily see.

| arm | held-out Token F1 | **truncated %** | mean tokens | হেলো % |
|---|---|---|---|---|
| **D1 + iCliniq** *(shipped)* | 0.2625 | **27.3** | 114.1 | 78.5 |
| **X5 @ lr 1e-5** | 0.2610 | **14.8** | 103.7 | 78.5 |
| *references* | — | ***6.8*** | *~100* | *76.4* |

The Token F1 gap is **0.0015**. The noise floor this task actually exhibits is **~0.02**
(`RESULTS_B_Qwen35_2B.md`), so the two arms are indistinguishable on F1 — and X5 is *also* closer
to the reference length. The trade is **~12.5 percentage points of answers that stop mid-sentence,
for nothing measurable.**

X5's advantage is not incidental. Truncation is monotonic in learning rate across the whole sweep —
**14.8% → 60.0% → 94.8%** at 1e-5 → 2e-5 → 5e-5 — while F1 traces a flat inverted-U. The shipped
default sits at the F1 peak and near the truncation worst.

## Why it is free

Every Phase 1 test id resolves into `lookup/test.parquet`, so **all 1000 scored rows route to the
champion branch and the specialist never fires.** Swapping it cannot move the 0.89552 leaderboard
score or break rules §5.2 reproduction. `swap_specialist.sh` re-verifies this rather than assuming
it. The specialist answers only ids that do *not* resolve — which is exactly the Phase 2 judging
set.

## What it is worth

Phase 1 among the top 10 spans 0.90015 → 0.88487, so the *entire* #1-to-#10 Phase 1 spread is
worth ~1.2 points of `Final = 0.8×P1 + 0.2×P2` (on the natural reading that a [0,1] composite is
scaled ×100). A judge spread of 10 points across finalists is worth 2.0. Cutting truncation on
12.5% of judged answers plausibly returns **~0.5–0.8 Final points** — more than retaking #1 on
Phase 1 would have, at zero GPU cost.

If the organizers instead min-max normalize Phase 1 across finalists, that arithmetic inverts
and Phase 1 dominates. The swap still costs nothing on Phase 1, so it is correct under both
readings — but do not quote the point estimate as if the normalization were known.

---

## How to apply

**1. Fetch the checkpoint from CHPC.** The X5 @ 1e-5 arm's `best/` directory, under the Phase 2
run root on `/scratch/general/nfs1/u1592009/`. Confirm you have the **1e-5** arm and not the 2e-5
default — they differ only by LR in the run name, and `run.json` carries `"lr": 1e-05`.

```bash
rsync -avh --progress <chpc>:/scratch/general/nfs1/u1592009/<phase2-runs>/X5_lr1e-5/best/ ~/pull/X5_lr1e-5/
```

**2. Install it.** Validates the architecture, counts real tensors, re-checks the 3B cap, and
proves the routing property before copying anything:

```bash
./scripts/swap_specialist.sh ~/pull/X5_lr1e-5 specialist_qwen35_2b_X5lr1e5
```

**3. Run with it.** The champion path is deliberately not overridable; only the specialist is:

```bash
P2_SPECIALIST_DIR=weights/specialist_qwen35_2b_X5lr1e5 ./scripts/run_bundle.sh <test.parquet> <out.csv>
```

**4. Confirm it did what it was swapped for.** This is the gate — do not ship on the strength of
the table above:

```bash
python scripts/audit_register.py work/specialist.json
```

Expect `truncated_pct` ≈ **15**, versus D1's 27.3. If it is not materially below 27, the wrong
checkpoint was pulled — revert by dropping `P2_SPECIALIST_DIR`.

**5. Re-verify Phase 1 still reproduces**, because it is cheap and the whole gate rests on it:

```bash
./scripts/run_bundle.sh lookup/test.parquet work/phase1_recheck.csv
```

Must stay **1000/1000 byte-identical** to `verification/bundle_phase1.csv`. It will — the
specialist does not fire — but prove it.

**6. Update the paperwork before shipping:** `MANIFEST.md` (checksums, weights listing) and
`WRITEUP.md` §3 (fine-tuning: LR 1e-5, not 2e-5) and §4 (results table). The parameter count is
unchanged — same base model, 1,881,825,088.

## Revert

Drop `P2_SPECIALIST_DIR`. D1's weights are never deleted or overwritten.

## What this does not fix

Both arms over-use the brand name (~80–85% `নাসেনিয়া` vs the references' 50%), and **clinical
correctness, contradiction and unsafe advice remain unaudited** — three of E16's five checks are
still open for want of a medical judge. `audit_register.py` narrows manual review; it does not
substitute for it.
