"""judge: score bars against the HUMAN gates the toolkit cannot decide.

This is the payoff of the ml/ layer. toolkit/check_all.py and quality_gate.py measure the 24
machine-decidable criteria; this scores the OTHER 17 (cringe, does the joke land, plain-beats-clever,
nonchalance, character by words alone...). It is a screen that RANKS: it tells you which bars to
rewrite and why, never that a bar is good.

  python ml/judge.py FILE|-            per-bar risk + the drivers behind the score
  python ml/judge.py FILE|- --k 6      more drivers per bar
  python ml/judge.py --selftest        must flag the rejected fixtures and pass Joe's locked bars

Risk near 1 = the shape of a bar Joe rejected. Risk near 0 = the shape of one he accepted or kept.
The drivers are printed as feature -> contribution, so the reason is inspectable, not a black box.
"""
import argparse
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLKIT = os.path.join(ROOT, "toolkit")
for _p in (HERE, TOOLKIT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fixtures                      # noqa: E402
import features as F                 # noqa: E402
import train_judge as T              # noqa: E402

MODEL = os.path.join(HERE, "models", "judge.joblib")


def blocks_from_text(text):
    """Blank line separates stanzas; each stanza becomes a block, so the judge sees context.
    Uses the shared bar cleaner, so a prose note is never scored as a bar."""
    out, cur = [], []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            if cur:
                out.append(cur)
                cur = []
            continue
        cleaned = F.clean_bars([s])
        cur += cleaned
    if cur:
        out.append(cur)
    return [b for b in out if b]


def load_model():
    if not os.path.exists(MODEL):
        sys.exit(f"no model at {os.path.relpath(MODEL, ROOT)} - run:\n"
                 f"  python ml/build_dataset.py && python ml/train_judge.py")
    return T.JudgeModel.load(MODEL)


def score_block(model, bars):
    row = F.block_row(bars, "stdin", "unknown", "ad-hoc")
    texts = [r["text"] for r in row["bars"]]
    feats = [r["features"] for r in row["bars"]]
    return texts, feats, model.risk(texts, feats)


def explain(model, text, feats, k=6):
    """Top contributions to this bar's risk, by |contribution|."""
    X = model._design([text], [feats])
    coef = model.lr.coef_[0]
    contrib = np.asarray(X.multiply(coef).todense())[0]
    names = (list(model.numeric_features)
             + list(model.word.get_feature_names_out())
             + list(model.char.get_feature_names_out()))
    pairs = sorted(zip(names, contrib), key=lambda t: -abs(t[1]))
    return [(n, round(float(v), 3)) for n, v in pairs[:k] if abs(v) > 1e-9]


def band(r):
    return "LAND" if r < 0.35 else ("EDGE" if r < 0.6 else "REJECT")


def render(model, blocks, k):
    lines = []
    for block in blocks:
        texts, feats, risks = score_block(model, block)
        mean = float(np.mean(risks))
        lines.append(f"\n== block of {len(block)} bars: mean risk {mean:.2f} "
                     f"({band(mean)}) ==")
        worst = int(np.argmax(risks))
        for i, (t, r) in enumerate(zip(texts, risks), 1):
            mark = " <-- weakest" if (i - 1) == worst else ""
            lines.append(f"  {band(r):6} {r:.2f}  bar {i:>2}: {t[:66]}{mark}")
        lines.append("  drivers for bar %d:" % (worst + 1))
        for name, v in explain(model, texts[worst], feats[worst], k):
            sign = "raises" if v > 0 else "lowers"
            lines.append(f"      {sign} risk {v:+.2f}  {name}")
    return "\n".join(lines)


def selftest(model):
    """The minimum bar for trusting the model: Joe's rejections flag, his locked bars do not."""
    ok = True
    locked = fixtures.joe_bars()
    _t, _f, r = score_block(model, locked)
    good = float(np.mean(r)) < 0.5
    ok &= good
    print(("ok  " if good else "BAD ") + f"Joe's locked bars score {np.mean(r):.2f} (< 0.5)")
    for path in sorted(glob.glob(os.path.join(ROOT, "toolkit", "tests", "rejected_*.txt"))):
        bars = blocks_from_text(open(path, encoding="utf8").read())
        if not bars:
            continue
        _t, _f, r = score_block(model, bars[0])
        caught = float(np.mean(r)) >= 0.5
        ok &= caught
        print(("ok  " if caught else "BAD ") +
              f"{os.path.basename(path)} scores {np.mean(r):.2f} (>= 0.5)")
    print("JUDGE SELFTEST", "PASSED" if ok else "FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="a bars file, or - for stdin")
    ap.add_argument("--k", type=int, default=6, help="drivers per block")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    model = load_model()
    if a.selftest:
        sys.exit(0 if selftest(model) else 1)
    text = sys.stdin.read() if (not a.file or a.file == "-") else open(a.file, encoding="utf8").read()
    blocks = blocks_from_text(text)
    if not blocks:
        sys.exit("no bar-like lines found - point this at a bars file (one bar per line, blank line "
                 "between stanzas), not a report. See ml/README.md.")
    print(render(model, blocks, a.k))
    print("\nSCREEN ONLY: a low risk is not 'good'. The 17 human gates need Joe's ear "
          "(benchmark/gate_coverage.md).")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
