"""Syllable duration vs the time the beat gives it (15 Oct 2026). Report-only until calibrated (see benchmark/mouth_and_duration.md).
Durations: Klatt/MITalk table (toolkit/klatt_durs.scm). Consonant joins: PanPhon feature distance (toolkit/articulation.py).

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
import articulation as art

TEMPLATE = os.path.join(HERE, "..", "benchmark", "flow_template.json")
STEP_MS = {"line=2bars@140 (measured layout)": 60000 / 140 * 8 / 16, "line=1bar@140 (double speed)": 60000 / 140 * 4 / 16}
LONGV = {"ii", "uu", "aa", "oo", "@@", "ei", "ai", "au", "oi", "ou", "i@", "e@", "u@"}
CLUSTER, FINAL_LENGTHEN = 0.6, 1.4  # Klatt: consonants in a cluster shorten; phrase-final syllable lengthens (approximations of his rules)
# Durations now come from the Klatt/MITalk table (articulation.klatt): inherent ms for a stressed vowel, minimum for an unstressed one.
# SCALE converts read-speech ms to rapped ms; calibrated 15 Oct 2026 on the original (see benchmark/mouth_and_duration.md).
SCALE = float(os.environ.get('DUR_SCALE', '0.45'))
JOIN_T = float(os.environ.get('DUR_JOIN_T', '3.0'))  # PanPhon cost at or above which a consonant join counts as hard on a 1-step gap
FUNC = set("a an the and but or so to of in on at for with by from as is it it's its i i'm my me we our you your he she they them their his her him us that this then than be was were are am do did has have had not no".split())


def _vowel_mrpa(base, stress, word):
    if base == "AA":
        w = word.lower()
        return "o" if ("o" in w and "ar" not in w) else "aa"
    if base == "AH":
        return "uh" if stress else "@"
    if base == "AA" or base not in art.ARPA2MRPA:
        return None
    return art.ARPA2MRPA[base]


def syllables(line):
    """[(word, vowel_class, need_ms, is_phrase_final, onset_first, coda_last, first_in_word, last_in_word)] one per syllable.
    need_ms = Klatt vowel (inherent if stressed, minimum if not) + the syllable's consonants, in read-speech ms (not yet SCALEd)."""
    out = []
    ws = re.findall(r"[A-Za-z'å]+", line)
    for wi, w in enumerate(ws):
        ph = pron(w.lower().replace("å", "a")) or []
        vi = [i for i, p in enumerate(ph) if is_v(p)]
        for k, i in enumerate(vi):
            p = ph[i]
            base = strip(p)
            stress = (p[-1] in "12" or len(vi) == 1) and not (w.lower() in FUNC and len(vi) == 1)
            m = _vowel_mrpa(base, stress, w) or "uh"
            inh, mn = art.klatt(m) or (120.0, 60.0)
            fin = wi == len(ws) - 1 and k + 1 == len(vi)
            vms = (inh if stress else mn) * (FINAL_LENGTHEN if fin else 1.0)
            if k == 0:
                on = [strip(x) for x in ph[:i]]
            else:
                inter = [strip(x) for x in ph[vi[k - 1] + 1:i]]
                on = inter[1:] if len(inter) >= 2 else inter
            if k + 1 == len(vi):
                co = [strip(x) for x in ph[i + 1:]]
            else:
                inter = [strip(x) for x in ph[i + 1:vi[k + 1]]]
                co = inter[:1] if len(inter) >= 2 else []
            cms = 0.0
            for grp in (on, co):
                for c in grp:
                    d = art.klatt(art.ARPA2MRPA.get(c, ""))
                    cms += (d[0] if d else 70.0) * (CLUSTER if len(grp) > 1 else 1.0)
            if not stress:
                cls = "schwa"
            else:
                cls = "long" if m in LONGV else "short"
            out.append((w, cls, vms + cms, fin, on[0] if on else None, co[-1] if co else None, k == 0, k + 1 == len(vi)))
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


def hard_joins(laid, gaps):
    """[(word_a, word_b, cost, gap)] word boundaries where the mouth travels far (PanPhon) across a gap of <= 1 step"""
    out = []
    for i in range(len(laid) - 1):
        a, b = laid[i][0], laid[i + 1][0]
        if a[7] and b[6] and a[5] and b[4]:
            c = art.join_cost(a[5], b[4])
            if c is not None:
                out.append((a[0], b[0], c, gaps[i]))
    return out


def pressure(line, bar, step_ms):
    """flags for one bar: need vs have, heavy syllable in a fast run"""
    laid = lay(line, bar)
    if not laid:
        return ["syllable count %d != template %d" % (len(syllables(line)), len(bar.get("steps") or []))]
    flags = []
    gaps = [b[1] - a[1] for a, b in zip(laid, laid[1:])] + [4]  # last syllable: assume room (a phrase-final syllable may ring on; 3 steps flagged half the final vowels once lengthened)
    for (syl, st), g in zip(laid, gaps):
        w, cls, ms = syl[0], syl[1], syl[2]
        have = max(1, g) * step_ms
        need = ms * SCALE
        if need > have * 1.0 and cls != "schwa":
            flags.append("%s (%s vowel, ~%dms) has %dms" % (w, cls, need, have))
    for a, b, c, g in hard_joins(laid, gaps):
        if c >= JOIN_T and g <= 1:
            flags.append("hard join %s|%s (mouth travel %.1f) on a %d-step gap" % (a, b, c, g))
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


def scan(path):
    """counts only: need>have rate per SCALE, and the join-cost distribution on <=1-step gaps, over the original"""
    global SCALE
    bars = load_bars()
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()]
    ms = list(STEP_MS.values())[0]
    for sc in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4):
        SCALE = sc
        n = need = 0
        for l, b in zip(lines, bars):
            f = pressure(l, b, ms)
            if f and f[0].startswith("syllable count"):
                continue
            n += 1
            need += any("has" in x and "hard join" not in x for x in f)
        print("scale %.2f: need>have %d/%d (%d%%)" % (sc, need, n, 100 * need // max(1, n)))
    costs = []
    for l, b in zip(lines, bars):
        laid = lay(l, b)
        if laid:
            gaps = [y[1] - x[1] for x, y in zip(laid, laid[1:])] + [4]
            costs += [(c, g) for _, _, c, g in hard_joins(laid, gaps)]
    fast = sorted(c for c, g in costs if g <= 1)
    print("consonant joins: %d total, %d on <=1-step gaps; fast-gap cost sorted: %s" % (len(costs), len(fast), fast))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok, msg = selftest()
        print(("PASSED: " if ok else "FAILED: ") + msg)
        sys.exit(0 if ok else 1)
    if "--scan" in sys.argv:
        scan(sys.argv[sys.argv.index("--scan") + 1])
    elif "--calibrate" in sys.argv:
        calibrate(sys.argv[sys.argv.index("--calibrate") + 1])
    elif "--slot-bar" in sys.argv:
        n = int(sys.argv[sys.argv.index("--slot-bar") + 1])
        bar = load_bars()[n - 1]
        line = sys.stdin.read().strip()
        for name, ms in STEP_MS.items():
            print(name, pressure(line, bar, ms) or "ok")
