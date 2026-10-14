"""Syllable duration vs the time the beat gives it (15 Oct 2026). Report-only until calibrated (see benchmark/mouth_and_duration.md).

The template (benchmark/flow_template.json) gives every syllable of the original a 16th-note step. The gap to the next onset is the
time that syllable HAS; this module estimates the time it NEEDS (long vowel / diphthong > short > schwa, plus coda and onset
consonants) and flags the bars where need exceeds have, and where a run of 1-step syllables includes a heavy one.
All durations are INFERENCE (phonetics averages, US-leaning), not measurements of Suno or of the original's audio.

  python toolkit/duration.py --selftest
  python toolkit/duration.py --slot-bar N -        (stdin: one bar, laid on template bar N)
  python toolkit/duration.py --calibrate PATH      (counts only; PATH = the private original, one line per bar, in template order)

Step length: the template lays a line over 2 bars at 140 BPM (8 beats, 3.43 s) in 16 steps = 214 ms per step. If a renderer
puts one line in ONE 140 BPM bar a step is 107 ms (full-time double speed). STEP_MS names both.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rhyme_tools import pron, is_v, strip

TEMPLATE = os.path.join(HERE, "..", "benchmark", "flow_template.json")
STEP_MS = {"line=2bars@140 (measured layout)": 60000 / 140 * 8 / 16, "line=1bar@140 (double speed)": 60000 / 140 * 4 / 16}
LONG = {"IY", "UW", "AA", "AO", "ER", "EY", "AY", "AW", "OY", "OW"}
SHORT = {"IH", "UH", "AH", "EH", "AE"}
BASE = {"long": 190.0, "short": 120.0, "schwa": 70.0}  # ms, inference
CODA_MS, ONSET_MS, FINAL_MS = 35.0, 15.0, 40.0
SCALE = float(os.environ.get('DUR_SCALE', '0.8'))  # rapped speech is faster than citation form. 0.8 = the largest scale at which the original's own 69 laid bars raise 0 need>have flags at 214 ms (15 Oct 2026); 0.85 gives 14%
FUNC = set("a an the and but or so to of in on at for with by from as is it it's its i i'm my me we our you your he she they them their his her him us that this then than be was were are am do did has have had not no".split())


def syllables(line):
    """[(word, vowel_class, weight_ms, is_phrase_final)] one per syllable"""
    out = []
    ws = re.findall(r"[A-Za-z'å]+", line)
    for wi, w in enumerate(ws):
        ph = pron(w.lower().replace("å", "a")) or []
        vi = [i for i, p in enumerate(ph) if is_v(p)]
        for k, i in enumerate(vi):
            p = ph[i]
            base = strip(p)
            stress = p[-1] in "12" or len(vi) == 1
            if base == "AH" and not stress:
                cls = "schwa"
            elif base == "AA" and "o" in w.lower() and "ar" not in w.lower():
                cls = "short"  # US /ɑ/ is British short /ɒ/ (on, not, got, Porto's first syllable)
            elif base in LONG:
                cls = "long"
            else:
                cls = "short"
            if w.lower() in FUNC and len(vi) == 1:
                cls = "schwa" if cls == "short" else cls
            end = vi[k + 1] if k + 1 < len(vi) else len(ph)
            coda = max(0, end - i - 1) if k + 1 == len(vi) else min(1, end - i - 1)
            onset = (i - (vi[k - 1] + 1)) if k else i
            ms = BASE[cls] + CODA_MS * coda + ONSET_MS * max(0, onset - 1)
            out.append((w, cls, ms, wi == len(ws) - 1 and k + 1 == len(vi)))
    return out


def lay(line, bar):
    """pair syllables with template steps; None unless the counts agree"""
    s = syllables(line)
    steps = bar.get("steps") or []
    if not steps:
        return None
    if len(s) != len(steps):
        return None
    return list(zip(s, steps))


def pressure(line, bar, step_ms):
    """flags for one bar: need vs have, heavy syllable in a fast run"""
    laid = lay(line, bar)
    if not laid:
        return ["syllable count %d != template %d" % (len(syllables(line)), len(bar.get("steps") or []))]
    flags = []
    gaps = [b[1] - a[1] for a, b in zip(laid, laid[1:])] + [3]  # last syllable: assume room
    for (syl, st), g in zip(laid, gaps):
        w, cls, ms, fin = syl
        have = max(1, g) * step_ms
        need = (ms + (FINAL_MS if fin else 0)) * SCALE
        if need > have * 1.0 and cls != "schwa":
            flags.append("%s (%s vowel, ~%dms) has %dms" % (w, cls, need, have))
    run = 0
    for (syl, st), g in zip(laid, gaps):
        run = run + 1 if g <= 1 else 0
        if run >= 3 and syl[1] == "long":
            flags.append("note: long vowel in a fast run at '%s' (fires on 37%% of the original, so never a gate)" % syl[0])
    return flags


def load_bars():
    return json.load(open(TEMPLATE, encoding="utf8"))["bars"]


def selftest():
    p = []
    s = syllables("Cold beer on the house in Porto")
    if len(s) != 8:
        p.append("syllable count %d" % len(s))
    if [x[1] for x in syllables("beat bit")] != ["long", "short"]:
        p.append("long/short classes wrong: %s" % [x[1] for x in syllables("beat bit")])
    bar = {"steps": [1, 2, 3, 4], "syl": 4}
    if not pressure("Pie pie pie pie", bar, 107.0):
        p.append("long vowels on 1-step gaps at 107ms not flagged")
    if pressure("Pie pie pie pie", {"steps": [1, 5, 9, 13]}, 107.0):
        p.append("4-step gaps flagged")
    return (not p, "; ".join(p) if p else "classes, laying and need-vs-have flags hold")


def calibrate(path):
    bars = load_bars()
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()]
    for name, ms in STEP_MS.items():
        hist, n, skipped = {}, 0, 0
        for l, b in zip(lines, bars):
            f = pressure(l, b, ms)
            if f and f[0].startswith("syllable count"):
                skipped += 1
                continue
            n += 1
            hist[len(f)] = hist.get(len(f), 0) + 1
        print("%s: flags per bar %s over %d bars (%d skipped on count)" % (name, dict(sorted(hist.items())), n, skipped))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok, msg = selftest()
        print(("PASSED: " if ok else "FAILED: ") + msg)
        sys.exit(0 if ok else 1)
    if "--calibrate" in sys.argv:
        calibrate(sys.argv[sys.argv.index("--calibrate") + 1])
    elif "--slot-bar" in sys.argv:
        n = int(sys.argv[sys.argv.index("--slot-bar") + 1])
        bar = load_bars()[n - 1]
        line = sys.stdin.read().strip()
        for name, ms in STEP_MS.items():
            print(name, pressure(line, bar, ms) or "ok")
