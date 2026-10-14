"""export_pairs: turn the labelled dataset into training data for a future writer model.

Two formats, because fine-tuning a writer needs both:

  ml/data/sft.jsonl   one row per accepted bar: {"prompt": "<slot constraints>", "completion": bar}
                      - the model learns to fill a stated end-sound family and syllable count.
  ml/data/dpo.jsonl   {"prompt": ..., "chosen": <bar Joe kept>, "rejected": <bar he rejected>}
                      - preference pairs for DPO. There are no MATCHED pairs in the history, so
                        these are CROSS pairs (a kept bar against a rejected one of similar length),
                        which is weaker evidence and is labelled as such.

THE HONEST POSITION (CLAUDE.md rule 6): the environment has no torch and no GPU, and the label set is
tiny (21 positives vs 56 negatives). A LoRA trained on this would memorise, not generalise. This
script builds the data and the exact command; see ml/lora/README.md for what must be true first.

  python ml/export_pairs.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (HERE, os.path.join(ROOT, "toolkit")):
    if p not in sys.path:
        sys.path.insert(0, p)

import features as F             # noqa: E402  (also puts toolkit/ on sys.path)
import rhyme_tools as rt         # noqa: E402
import train_judge as T          # noqa: E402

DATA = os.path.join(HERE, "data")


def constraint_of(bar):
    """The prompt side: the bar's own end sound and syllable count, so the model fills a slot."""
    ws = [w for w in bar.replace(",", " ").split() if w.strip("'")]
    last = ws[-1].strip(".,;:!?'\"") if ws else ""
    ph = rt.pron(last) if last else None
    tail = "-".join(rt.strip(p) for p in (ph or []) if rt.is_v(p))[-12:] or "?"
    n = rt.nsyl(rt.pron_phrase(bar)[0]) if rt.pron_phrase(bar)[0] else len(ws)
    return f"end sound ~{tail}; about {n} syllables"


def main():
    rows = T.load()
    pos = [r for r in rows if r["label"] in T.POSITIVE]
    neg = [r for r in rows if r["label"] in T.NEGATIVE]

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "sft.jsonl"), "w", encoding="utf8") as fh:
        for r in pos:
            fh.write(json.dumps({"prompt": constraint_of(r["text"]), "completion": r["text"],
                                 "source": r["source"], "tier": r["label"]}, ensure_ascii=False) + "\n")

    # cross pairs, matched on length so the model cannot learn "longer = better"
    pairs, used = [], 0
    for p in pos:
        n = len(p["text"].split())
        close = sorted(neg, key=lambda r: abs(len(r["text"].split()) - n))[:3]
        for c in close:
            pairs.append({"prompt": constraint_of(p["text"]), "chosen": p["text"],
                          "rejected": c["text"], "kind": "cross"})
        used += 1
    with open(os.path.join(DATA, "dpo.jsonl"), "w", encoding="utf8") as fh:
        for row in pairs:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"ml/data/sft.jsonl: {len(pos)} rows")
    print(f"ml/data/dpo.jsonl: {len(pairs)} cross pairs from {used} positives x 3 negatives")
    print("\nNOT TRAINABLE YET: no torch/GPU here, and 21 positives is far below the ~1k that a "
          "lyric LoRA needs. This is the data + the format; the trigger to train is ml/lora/README.md.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
