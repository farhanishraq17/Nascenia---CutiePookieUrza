# `code/` — shared scripts

**Do not copy these into the experiment folders.** All 16 experiments call them from here as
`../code/<script>.py`, so there is one copy to fix if a bug turns up. Sixteen copies would drift.

| Script | What it does |
|---|---|
| **`02_train_t5.py`** | The trainer. `--data-dir --model --precision auto` · Adafactor · fail-safe `compute_metrics` · selects the best checkpoint on **composite**, never loss |
| **`04_decode.py`** | Beam / MBR decoding + submission writer. **fp32 by default** with a non-finite-logits probe at load, and takes `--data-dir` |
| **`metric.py`** | The exact competition composite. `python metric.py --selftest` verifies the LCS implementation against brute force — **run it once after install** |
| `01_prep.py` | Rebuilds the frozen split from the raw competition CSVs. 🔴 `--seed 42 --dev-size 5000`, never anything else |
| **`09_build_inputs.py`** | Composes any input combination: `--fields q,en,bn`. This is how you build a dataset the prebuilt set does not cover |
| `07_build_transfer_en.py` | Earlier english+draft builder — superseded by `09`, kept for provenance |
| `05_build_transfer.py` | Original draft-only builder |
| `08_trim_mt5_vocab.py` | Trims mT5's 250k vocab to the ~23k tokens this corpus uses. **E10 only** |

## Two of these carry hard-won fixes — do not "simplify" them

**`04_decode.py` is fp32 by default.** T5 overflows to NaN in fp16 and fails **silently**: it prints
a parameter count, reports "decoded 300 rows", and writes a well-formed CSV in which every row is a
single token. That cost a full submission cycle. The load-time probe asserting
`torch.isfinite(logits).all()` exists for that reason.

**Both scripts take `--data-dir` rather than deriving paths from `__file__`.** An earlier version
computed `Path(__file__).parent.parent / "DATA" / "PROCESSED"`, which is correct in the source repo
and resolves to a non-existent directory anywhere else. Every hosted run failed at the first read.

## Quick check after install

```bash
python metric.py --selftest        # LCS vs brute force, 200 random pairs
python 02_train_t5.py --help       # confirm --data-dir and --precision exist
python 04_decode.py --help         # confirm --data-dir exists (stale copies lack it)
```
