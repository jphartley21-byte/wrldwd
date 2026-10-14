"""Write benchmark/slot_targets.json: per-slot NUMBERS measured from the original (never its words).

Reads the private original locally (like calibrate.py / anticopy). Output keys per slot:
  first_person_bars   bars containing I / I'm / my / me / we / our ...   (the narrator is in the bar)
  subject_bars        bars where the narrator is the grammatical subject (I / I'm / we ...)
  internal_total      sum of the profile's per-bar internal-rhyme counts
  multisyl            the profile's multisyllabic-rhyme run count for the slot
  carpet_pairs / carpet_total  the profile's end-rhyme carpet
  suffix_ended        end words carried by a derivational/inflectional suffix (-ing -ed -er -ary -ly ...): the original has 4 of 76
  beat_weak_mean      weak (unstressed) syllables landing on a downbeat per bar, laying the bar's syllables on the audio-measured steps
  weak_run_max        longest run of consecutive weak syllables in any bar
Run:  python -m ww.write.make_targets
"""
from __future__ import annotations

import json
import re

from .. import config

FP = re.compile(r"\b(i|i'm|i've|i'd|i'll|my|me|mine|myself|we|we're|we've|our|us|ours)\b", re.I)
SUBJ = re.compile(r"\b(i|i'm|i've|i'd|i'll|we|we're|we've)\b", re.I)
OUT = config.BENCHMARK / "slot_targets.json"


SUFFIXES = ("ing", "ings", "ed", "ly", "ers", "er", "ier", "ies", "ary", "ory", "ery", "ation", "ations", "ness", "ful", "able", "ment", "ments", "ous", "ive", "ity", "ish", "est", "less")


def suffix_ended(word: str) -> bool:
    w = word.lower()
    return any(w.endswith(x) and len(w) > len(x) + 1 for x in SUFFIXES)


def beat_stats(bars: list[str], start: int) -> tuple[float, int]:
    """mean weak-syllables-on-a-downbeat per bar and longest weak run, using the original's measured syllable steps (start = 0-based song bar)."""
    import flow_fit as ff
    from .. import bridge  # noqa: F401  (puts toolkit on sys.path)
    bw, wr = [], 0
    for i, b in enumerate(bars):
        t = ff.T[start + i]
        if t.get("missing"):
            continue
        weak = ff.sylls(b)
        n = len(weak)
        o = t["steps"]
        steps = list(o[:n]) + [o[-1] + 1] * max(0, n - len(o))
        bw.append(sum(1 for k, st in enumerate(steps) if st % 4 == 0 and k < n and weak[k]))
        run = best = 0
        for w in weak:
            run = run + 1 if w else 0
            best = max(best, run)
        wr = max(wr, best)
    return (sum(bw) / len(bw) if bw else 0.0), wr


def build() -> dict:
    from ..calib import original as o
    lines = o._lines()
    prof = json.loads((config.BENCHMARK / "original_profile.json").read_text(encoding="utf-8"))
    out = {}
    for name, a, b in o.SECTIONS:
        bars = lines[a:b]
        p = prof[name]
        from .. import bridge
        ends = [(bridge.words(x) or [""])[-1] for x in bars]
        bwm, wrm = beat_stats(bars, a)
        out[name] = {"suffix_ended": sum(suffix_ended(e) for e in ends), "beat_weak_mean": round(bwm, 2), "weak_run_max": wrm, "bars": len(bars), "first_person_bars": sum(bool(FP.search(x)) for x in bars),
                     "subject_bars": sum(bool(SUBJ.search(x)) for x in bars), "internal_total": sum(p["internal"]),
                     "multisyl": p["quad"]["multisyl"], "carpet_pairs": p["carpet"]["pairs"], "carpet_total": p["carpet"]["total"]}
    return out


def main() -> int:
    t = build()
    OUT.write_text(json.dumps(t, indent=1), encoding="utf-8")
    for k, v in t.items():
        print(k, v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
