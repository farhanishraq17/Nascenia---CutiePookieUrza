# E18_model_zoo — results

**Running 2026-08-09 on CHPC granite `grn008`, 1 × H100 NVL per arm, bf16.**
Decoder arms use `../code/03_train_causal.py`, written for this experiment because
`02_train_t5.py` is seq2seq-only. See `../_slurm/README.md`.

## The most important number here is not a zoo result at all

**`banglat5` reproduces the incumbent.** Same recipe (draft only, 384/256, 8×8, lr 1e-3, seed 11),
different hardware and precision (H100 bf16 vs Kaggle T4 fp32):

| | Token F1 | ROUGE-L |
|---|---|---|
| the 0.85030 submission, at its peak step 2,750 | 0.7724 | 0.7324 |
| **this arm, at step 2,750** | **0.7723** | **0.7336** |
| this arm, at its own peak (3,750) | 0.7769 | 0.7387 |

**A gap of 0.0001 at the matched step.** The migration from Kaggle T4/fp32 to H100/bf16 changed
nothing measurable, which is what licenses comparing every number in this program against the
0.85030 baseline. It also means bf16 is safe for BanglaT5 here — worth stating explicitly, given
that fp16 silently destroys this model (trap #20).

## Scoreboard

| Arm | Model | Params | Kind | Token F1 | ROUGE-L | pred LB | vs 0.7724 | peak step | Status |
|---|---|---|---|---|---|---|---|---|---|
| **banglat5** | csebuetnlp/banglat5 | 247.6 M | enc-dec | **0.7768** | 0.7389 | 0.8531 | +0.0044 | 3,750 | done |
| **indicbart** | ai4bharat/IndicBART | 244 M | enc-dec | *(training)* ~0.43 @1,750 | | | far below | | running |
| qwen3_1p7b | Qwen/Qwen3-1.7B | 1.7 B | decoder | | | | | | ⏳ queued |
| qwen25_1p5b | Qwen/Qwen2.5-1.5B-Instruct | 1.54 B | decoder | | | | | | ⏳ queued |
| qwen3_0p6b | Qwen/Qwen3-0.6B | 0.60 B | decoder | | | | | | ⏳ queued |
| **gemma_2_2b_it** | google/gemma-2-2b-it | 2.6 B | decoder | — | — | — | — | — | **BLOCKED — HF 401** |
| **llama32_1b** | meta-llama/Llama-3.2-1B-Instruct | 1.24 B | decoder | — | — | — | — | — | **BLOCKED — HF 401** |

## Two arms are blocked upstream, and one of them is the arm the literature points at

`google/gemma-2-2b-it` and `meta-llama/Llama-3.2-1B-Instruct` are **gated repos**. Both return
`401` on `config.json` anonymously *and* with this machine's `$HF_TOKEN` — the account has not
accepted their licences.

This matters more than a missing row: **LIT-01's whole decoder-beats-encoder-decoder finding rests
on Gemma-2-2B**, which the NLP4Health overview credits specifically for Indic-script tokenizer
support. Without it the zoo tests the claim only through Qwen.

**To unblock:** accept the licences at `huggingface.co/google/gemma-2-2b-it` and
`huggingface.co/meta-llama/Llama-3.2-1B-Instruct` with the account behind `$HF_TOKEN`, then

```bash
python ../_slurm/submit.py --arm E18_model_zoo/gemma_2_2b_it \
                           --arm E18_model_zoo/llama32_1b --force-blocked
```

Both arms are already specified in `../_slurm/registry.py` and marked `blocked=` — they are
**deferred, not dropped**. Gemma-2-2B is 2.6 B: within the 3 B cap alone, but it leaves no
ensemble room at all, so a win there closes off E14/E19.

## Per-arm read-out

| Arm | mean output tokens | `হেলো` opener % | `নাসেনিয়া` % | precision | GPU | hours |
|---|---|---|---|---|---|---|
| banglat5 | 98.9 | 76.3 % | 53.0 % | bf16 | H100 NVL | 1.15 |

References ~100 tokens · `হেলো` 76.4 % · `নাসেনিয়া` 50.0 %. banglat5 matches the references on
all three — the register conversion is learned, not copied.

## Trajectory — banglat5

| step | 250 | 500 | 750 | 1000 | 1250 | 1500 | 1750 | 2000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .5720 | .7085 | .7353 | .7443 | .7554 | .7586 | .7642 | .7680 |

| step | 2250 | 2500 | **2750** | 3000 | 3250 | 3500 | **3750** | 4000 |
|---|---|---|---|---|---|---|---|---|
| Token F1 | .7660 | .7696 | **.7723** | .7735 | .7748 | .7756 | **.7769** | .7759 |

Still climbing at 4,000, like every other arm in this program.

## Notes

**Decoders need lr 1e-5–5e-5, not BanglaT5's 1e-3** — carried across, 1e-3 diverges and the run
reads as a bad model. Registry uses 2e-5 (3e-5 for the 0.6 B).
**Decoder-only models must LEFT-pad for batched generation.** `03_train_causal.py` flips
`padding_side` inside its generation eval; right-padding produces fluent garbage that scores as a
bad model. Qwen3 arms run with `enable_thinking=False`.
Decoder arms keep only `best/` (no rolling checkpoints), so a **preemption on the freecycle QOS
restarts them from zero** rather than from the last eval.

## Anything surprising

**IndicBART is not competitive** — ~0.43 Token F1 at step 1,750 against banglat5's 0.7642 at the
same step. It is a 244 M enc-dec like BanglaT5 and reads the identical input, so this is a clean
statement about the *model*, not the data. Keeping the checkpoint anyway: a member that disagrees
this strongly is precisely what E14 cannot get from another seed, and its value there is
independent of its score here.
