"""A pun-quality proxy: how SURPRISING a word is in its context.

WHY THIS EXISTS
The research was blunt: nothing off the shelf scores whether wordplay is GOOD. The nearest thing is
hhexiy/pungen's "local-global surprise" (Pun Generation with Surprise, ACL 2019), which correlates
with human funniness ratings. Its reference implementation is PyTorch/fairseq, so this borrows the
IDEA and implements it with what the repo already has: a small LM built from OUR OWN bars (no
licence problem, no third-party text) plus wordfreq.

The signal: a word is a better pun when it is UNEXPECTED in the local context but its second reading
is still plausible. So we score a candidate as
    surprise = log P(word | previous word)  -  log P(word)          (more negative = more surprising)
and a pun pair as the surprise of the word whose homophone the line also invokes.

WHAT THIS IS NOT
It is not a funniness classifier and it has never been validated against Joe's ear. Treat it as a
TIEBREAK between two versions of the same wordplay, never as a reason to keep or cut a bar. The
literature (Art or Artifice?, CHI 2024) and this repo's own judge both show quality models of
creative writing failing confidently.

usage:
    python toolkit/funny.py FILE|-             surprise score per bar, worst-scoring word named
    python toolkit/funny.py --selftest
"""

import argparse
import collections
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import rhyme_tools as rt     # noqa: E402

MIN = 1e-9


def _bars_from_corpus():
    """Every bar the repo has written. Our own text, so it can be used as a corpus."""
    out = []
    for path in glob.glob(os.path.join(ROOT, "writing", "*.md")):
        if os.path.basename(path).startswith(("pipeline_", "forge_")):
            continue
        try:
            with open(path, encoding="utf-8-sig") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith(("#", "|", ">", "-", "*", "`")):
                        continue
                    if "|" in line or line.endswith(":"):
                        continue
                    if 2 <= len(line.split()) <= 14:
                        out.append(re.sub(r"[^a-z' ]", " ", line.lower()).split())
        except Exception:
            continue
    return out


class LM:
    """A stupidly simple bigram/unigram model. Small corpus: smoothing matters more than sophistication."""

    def __init__(self, docs=None):
        docs = docs if docs is not None else _bars_from_corpus()
        self.uni = collections.Counter()
        self.bi = collections.Counter()
        self.total = 0
        for d in docs:
            prev = "<s>"
            for w in d:
                self.uni[w] += 1
                self.bi[(prev, w)] += 1
                self.total += 1
                prev = w
        self.vocab = len(self.uni) + 1

    def p_uni(self, w):
        return (self.uni.get(w, 0) + 0.5) / (self.total + 0.5 * self.vocab)

    def p_bi(self, prev, w):
        denom = self.uni.get(prev, 0) + 0.5 * self.vocab
        return (self.bi.get((prev, w), 0) + 0.5) / max(denom, MIN)


_LM = None


def lm():
    global _LM
    if _LM is None:
        _LM = LM()
    return _LM


def unexpectedness(word):
    """How unusual the word choice is, 0 (banal) up to ~7 (very rare). wordfreq-based.

    This replaces pungen's P(word|context) term, and the reason is a measured limitation: our
    corpus is ~1k bars, so a bigram model over it mostly reports whether the exact pair happens to
    appear in our own drafts - it rated the locked bars' own pun words as unsurprising. So this
    claims only what can be supported: the word is rare, therefore not the obvious choice.
    """
    try:
        from wordfreq import zipf_frequency
        return round(max(0.0, 8.0 - zipf_frequency(word, "en")), 2)
    except Exception:
        return 0.0


def second_reading(word, floor=2.0):
    """A real English word with the same pronunciation that a listener could also hear."""
    ph = rt.pron(word)
    if not ph:
        return None
    key = tuple(p.rstrip("012") for p in ph)
    best = None
    for cand in _HOMO_INDEX().get(key, []):
        if cand == word or len(cand) < 3:
            continue
        try:
            from wordfreq import zipf_frequency
            if zipf_frequency(cand, "en") < floor:
                continue
        except Exception:
            pass
        if best is None or len(cand) < len(best):
            best = cand
    return best


def homophone_of(word):
    return second_reading(word)


_HOMOS = None


def _HOMO_INDEX():
    global _HOMOS
    if _HOMOS is not None:
        return _HOMOS
    idx = collections.defaultdict(list)
    for w in rt.D:
        if not w.isalpha() or len(w) > 12:
            continue
        ph = rt.pron(w)
        if not ph:
            continue
        idx[tuple(p.rstrip("012") for p in ph)].append(w)
    for w in rt.OVR:
        ph = rt.pron(w)
        if not ph:
            continue
        idx[tuple(p.rstrip("012") for p in ph)].append(w)
    _HOMOS = idx
    return idx


def score_bar(bar):
    """Per content word: how unexpected the choice is, and whether a second reading exists."""
    words = re.findall(r"[a-z']+", bar.lower())
    out = {"bar": bar, "words": [], "pun": None}
    for w in words:
        if w in rt.FUNC or len(w) < 3:
            continue
        u = unexpectedness(w)
        second = second_reading(w)
        out["words"].append({"word": w, "unexpected": u, "second": second})
        if second and out["pun"] is None:
            out["pun"] = (w, second, u)
    return out


def base_rate():
    """How often a bar carries a word with an available second reading.

    This is the number that decides how much the signal is worth: if most bars already carry one,
    then "a second reading exists" is not evidence of wit, only a flag to look at.
    """
    bars = []
    for path in glob.glob(os.path.join(ROOT, "writing", "*.md")):
        if os.path.basename(path).startswith(("pipeline_", "forge_")):
            continue
        try:
            with open(path, encoding="utf-8-sig") as fh:
                for raw in fh:
                    line = raw.strip()
                    if line and not line.startswith(("#", "|", ">", "-", "*", "`")) \
                            and "|" not in line and 2 <= len(line.split()) <= 14:
                        bars.append(line)
        except Exception:
            continue
    bars = list(dict.fromkeys(bars))
    with_second = [b for b in bars if score_bar(b)["pun"]]
    return len(bars), len(with_second)


def selftest():
    ok = True
    checks = [
        ("a banal word scores low", unexpectedness("the") < 1.5 or unexpectedness("time") < 1.5),
        ("a rarer word scores higher", unexpectedness("panniers") > unexpectedness("time")),
        ("a homophone is found for plane", homophone_of("plane") in ("plain",)),
        ("a homophone is not the word itself", homophone_of("plane") != "plane"),
        ("no false second reading for a plain word", second_reading("kettle") is None),
        ("a known pun line reports a pair", score_bar("So boarded a plane out to Bordeaux")["pun"] is not None),
        ("an available second reading is found wherever it exists",
         score_bar("Might hit the road past the border")["pun"] is not None),
    ]
    for name, good in checks:
        if not good:
            ok = False
            print(f"  FAIL {name}")
    s = score_bar("So boarded a plane out to Bordeaux")
    print(f"  pun: {s['pun']}")
    print("FUNNY SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--base", action="store_true", help="what share of our own bars carry a second reading")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.base:
        n, k = base_rate()
        print(f"{k}/{n} of the repo's own bars carry a word with an available second reading "
              f"({100.0 * k / max(1, n):.0f}%)")
        print("So availability alone is a weak signal - it flags where a pun COULD be, "
              "and says nothing about whether one is meant or good.")
        return 0
    text = sys.stdin.read() if (not a.path or a.path == "-") else open(
        a.path, encoding="utf-8-sig").read()
    for line in [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]:
        s = score_bar(line)
        words = sorted(s["words"], key=lambda x: -x["unexpected"])[:3]
        wtxt = ", ".join(f"{w['word']} {w['unexpected']:.1f}" for w in words)
        pun = f"  PUN {s['pun'][0]}/{s['pun'][1]}" if s["pun"] else ""
        print(f"  {line[:46]:<46} most unexpected: {wtxt}{pun}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
