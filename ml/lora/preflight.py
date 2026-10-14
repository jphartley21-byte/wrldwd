"""preflight: is this repo ready to actually TRAIN the writer model?

Run this before believing any "fine-tune the LLM" plan. It fails loudly and names the missing piece,
so the answer is never a guess. Training the writer in ml/lora/README.md needs all of:

  * a deep-learning runtime (torch) with a CUDA GPU - neither is present in the current environment;
  * enough preference data: ml/data/dpo.jsonl grows by one row per kept bar and three per rejected
    bar. A LoRA on a few hundred rows memorises; the working threshold used here is 1000 pairs.

  python ml/lora/preflight.py      # exit 0 = ready to train, 1 = not yet (and why)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
DPO = os.path.join(ML, "data", "dpo.jsonl")
SFT = os.path.join(ML, "data", "sft.jsonl")
MIN_PAIRS = 1000

reasons = []

try:
    import torch  # noqa: F401
    has_torch = True
    try:
        gpu = torch.cuda.is_available()
    except Exception:
        gpu = False
except Exception:
    has_torch, gpu = False, False

if not has_torch:
    reasons.append("torch is not installed (pip install torch --index-url .../cu12x)")
if has_torch and not gpu:
    reasons.append("no CUDA GPU available (a CPU LoRA is possible but ~50x slower)")


def count(path):
    if not os.path.exists(path):
        return 0
    return sum(1 for _ in open(path, encoding="utf8"))


pairs, sft = count(DPO), count(SFT)
if pairs < MIN_PAIRS:
    reasons.append(f"only {pairs} preference pairs in ml/data/dpo.jsonl, need >= {MIN_PAIRS} "
                   f"(keep labelling: every Joe verdict adds rows)")

print(f"torch={has_torch}  cuda={gpu}  sft_rows={sft}  dpo_pairs={pairs}")
if reasons:
    print("\nNOT READY TO TRAIN:")
    for r in reasons:
        print("  -", r)
    print("\nUntil then the judge (ml/judge.py) is the working ML layer: rules + a small fitted "
          "diction model, no GPU needed. See ml/README.md.")
    sys.exit(1)

print("\nREADY: run the recipe in ml/lora/README.md, then re-run `python ml/evaluate.py` and "
      "`python toolkit/calibrate.py` before using any output.")
sys.exit(0)
