# ml/lora/: the writer-model recipe (NOT ready to run - see preflight)

The goal: a local model that drafts end-word-first bars for a slot, used **only as a candidate
generator inside the loop** - every candidate still goes through `toolkit/check_all.py`,
`ml/judge.py` and Joe's ear. The model never replaces the verifier; it feeds it.

## Run this first

```
python ml/lora/preflight.py
```

It fails and names what is missing. Today it reports:

```
torch=False  cuda=False  sft_rows=21  dpo_pairs=63
NOT READY TO TRAIN:
  - torch is not installed
  - only 63 preference pairs, need >= 1000
```

Two gates, both real:

1. **Runtime.** LoRA needs `torch` + a CUDA GPU. Neither exists in the current environment
   (`python -c "import torch"` fails). A CPU LoRA is possible but ~50x slower - not worth it here.
2. **Data.** `ml/data/dpo.jsonl` has 63 cross pairs from 21 positives. A LoRA on that memorises the
   positives. The working threshold used here is **1000 pairs**, and the honest route is
   *more positives*: every bar Joe keeps, plus the locked lines of finished sections. The pairs are
   **cross** pairs (kept vs rejected, length-matched), which is weaker than matched pairs - another
   reason to wait for volume.

## The recipe (when preflight passes)

Base model: a small open instruct model that fits the GPU (e.g. a 1-3B model). Nothing
artist- or lyric-specific, and **never** the original's lyrics (they live outside the repo, rule 4).

```
pip install "torch --index-url https://download.pytorch.org/whl/cu121"
pip install transformers peft trl datasets accelerate

# 1. SFT on the accepted bars, to teach the constraint-filling format
python -m trl.train sft \
  --model_name_or_path <base> --dataset_text_field completion \
  --data_files ml/data/sft.jsonl --output_dir ml/models/sft \
  --lora_r 16 --lora_alpha 32 --num_train_epochs 3 --learning_rate 2e-4

# 2. DPO on the preference pairs, to push it off the rejected shapes
python -m trl.train dpo \
  --model_name_or_path ml/models/sft --data_files ml/data/dpo.jsonl \
  --output_dir ml/models/dpo --lora_r 16 --beta 0.1 --num_train_epochs 1
```

## The gate that must pass before any output is used

```
python ml/evaluate.py            # the judge must still separate accept / park / reject
python toolkit/calibrate.py C:\Users\Joe\Documents\Worldwide_private\original_lines.txt
python toolkit/check_all.py --slot "<slot>" -
```

A generated bar is a **candidate**, not a draft: it has to clear the same checks as a hand-written
bar, and it can never lower the bar. If a fine-tune produces bars that pass the tools but that Joe
rejects, that is evidence for the judge, and the pairs go back into `ml/data/dpo.jsonl`.
