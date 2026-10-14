"""Flow check: stress clashes, lapses, mid-bar pauses, consonant pile-ups and mouth-shape transitions per bar.
Usage: python toolkit/flow_check.py -   (stdin: draft bars; optionally reference bars, then a line '---', then draft bars)
Stress is a text estimate (content words stressed, function words not): a screen, not an ear. Joe's ear decides.

Mouth-shape transitions (14 Oct 2026): `joins()` reports where the mouth must reorganise across a word
boundary -- the thing Joe heard as "difficulty mouth shape transitions" in "whites, he's" and "he's wrecked".
The blunt 3+ consonant count ("cluster") is NOT the signal: the original averages 0.93 of those per bar. The
signal is the RARE set (a fricative into /h/, a voiced fricative into a liquid, a same-place stop into a
stop): the original carries 0 of those in 78% of its 92 bars and 2 or more in only 6 of them, while our
"whites he's wrecked" bar carries two in one bar -- and they are the two rarest types in the whole song
(3 occurrences each in 92 lines). Calibrated 14 Oct 2026 by counting the original; see rare_joins().
"""
import re, sys
sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from rhyme_tools import pron, is_v, strip

FUNC = set("""a an the and but or so to of in on at for with by from up as is it it's its i i'm my me we our you your he she they them their his her him us 'em em
that that's this then than be been was were are am do did has have had will would can could might may must shall should not no
there here what when where who how if just got get""".split())
VOICE = set("B D G V DH Z ZH JH M N NG L R W Y".split())

# place of articulation and manner, for the mouth-shape measure. Front-to-back order for PLACE_ORDER.
PLACE = {}
for _g, _ps in (("bilabial", "P B M"), ("labiodental", "F V"), ("dental", "TH DH"), ("alveolar", "T D N L S Z"),
                ("postalveolar", "SH ZH CH JH R"), ("velar", "K G NG"), ("labiovelar", "W"),
                ("palatal", "Y"), ("glottal", "HH")):
    for _p in _ps.split():
        PLACE[_p] = _g
MANNER = {}
for _g, _ps in (("stop", "P B T D K G"), ("fricative", "F V TH DH S Z SH ZH HH"), ("affricate", "CH JH"),
                ("nasal", "M N NG"), ("approximant", "L R W Y")):
    for _p in _ps.split():
        MANNER[_p] = _g
# The rare, ear-catching shifts. Named so a writer can act on them; each is measured on the ORIGINAL in the
# module docstring. "fricative to H" is a glottal reset (the tongue must stop hissing and open the glottis);
# "voiced fricative to liquid" is the tongue-and-lip jolt of /z/ into /r/; "same-place stop-stop" needs a
# release to be heard at all.
RARE = ("fricative to H glottis reset", "voiced fricative to liquid", "same-place stop-stop")


def _word_parts(w):
    """(coda, onset): the consonants after the last vowel and before the first, from the fixed pronouncer."""
    raw = pron(w.lower().strip("'")) or []
    vi = [i for i, p in enumerate(raw) if is_v(p)]
    if not vi:
        return [], []
    ph = [strip(p) for p in raw]
    return ph[vi[-1] + 1:], ph[:vi[0]]


def joins(line):
    """[(word_a, word_b, shift, ...)] for every word boundary where the mouth must reorganise.
    A shift is named, not scored: the callers decide which names matter (see RARE)."""
    ws = re.findall(r"[A-Za-z'å]+", line)
    out = []
    for a, b in zip(ws, ws[1:]):
        coda, _ = _word_parts(a)
        _, onset = _word_parts(b)
        reasons = []
        if len(coda) + len(onset) >= 3:
            reasons.append(f"{len(coda)}+{len(onset)} consonants")
        if coda and onset:
            p1, p2 = PLACE.get(coda[-1]), PLACE.get(onset[0])
            m1, m2 = MANNER.get(coda[-1]), MANNER.get(onset[0])
            if p1 and p2 and p1 != p2 and m1 != m2:
                reasons.append(f"{coda[-1]} to {onset[0]}: place and manner both change")
            if p1 == p2 and m1 == m2 == "stop":
                reasons.append("same-place stop-stop")
            if m1 in ("fricative", "affricate") and m2 == "fricative" and onset[0] == "HH":
                reasons.append("fricative to H glottis reset")
            if m1 == "fricative" and coda[-1] in "ZV" and m2 == "approximant" and onset[0] in "RL":
                reasons.append("voiced fricative to liquid")
        if reasons:
            out.append((a, b, reasons))
    return out


def rare_joins(line):
    """the joins from RARE only: what the ear actually catches. The original's own rate is the par."""
    return [(a, b, r) for a, b, rs in joins(line) for r in rs if r in RARE]


# Vowel position (height 0 close..3 open, backness 0 front..2 back, rounded). Inference from standard phonetics tables; see
# benchmark/mouth_and_duration.md. Used for vowel travel between adjacent syllables, report-only until calibrated.
VPOS = {"IY": (0, 0, 0), "IH": (1, 0, 0), "EY": (1, 0, 0), "EH": (2, 0, 0), "AE": (3, 0, 0), "AY": (3, 1, 0), "AA": (3, 2, 0),
        "AO": (2, 2, 1), "OW": (1, 2, 1), "UH": (1, 2, 1), "UW": (0, 2, 1), "AW": (3, 2, 1), "OY": (2, 2, 1), "AH": (2, 1, 0), "ER": (2, 1, 0)}


def vowel_travel(line):
    """[(word_a, word_b, distance)] between the stressed-or-full vowels of adjacent content syllables.
    Distance = height + backness + 2*rounding change (0..~7). Report-only: the par is not yet measured on the original."""
    seq = []
    for w in re.findall(r"[A-Za-z'å]+", line):
        if w.lower() in FUNC:
            continue
        for p in (pron(w.lower().replace("å", "a")) or []):
            if is_v(p) and strip(p) in VPOS and (p[-1] in "12" or strip(p) not in ("AH", "ER")):
                seq.append((w, VPOS[strip(p)]))
    out = []
    for (a, va), (b, vb) in zip(seq, seq[1:]):
        d = abs(va[0] - vb[0]) + abs(va[1] - vb[1]) + 2 * abs(va[2] - vb[2])
        out.append((a, b, d))
    return out


def bar_profile(line):
    words = re.findall(r"[A-Za-z'å]+|[,;:\-–—]", line)
    stress, pauses, clusters = [], 0, 0
    prev_coda = []
    for w in words:
        if w in ",;:–—":
            pauses += 1
            continue
        ph = pron(w.lower().replace("å", "a")) or []
        if not ph and w.isupper() and len(w) > 1:  # initialism, spoken letter by letter
            ph = ["AH1"] + ["AH0"] * (sum(3 if c == "W" else 1 for c in w) - 1)
        if not ph:  # out-of-dictionary: estimate syllables from vowel groups, stress the first
            n = max(1, len(re.findall(r"[aeiouy]+", w.lower().rstrip("e"))))
            ph = ["AH1"] + ["AH0"] * (n - 1)
        vs = [p for p in ph if is_v(p)]
        if not vs:
            continue
        func = w.lower() in FUNC
        for p in vs:
            s = 0 if func else (1 if p[-1] in "12" or len(vs) == 1 else 0)
            if not func and p[-1] == "2":
                s = 0
            stress.append(s)
        first_v = next(i for i, p in enumerate(ph) if is_v(p))
        last_v = max(i for i, p in enumerate(ph) if is_v(p))
        onset, coda = ph[:first_v], ph[last_v + 1:]
        if len(prev_coda) + len(onset) >= 3:
            clusters += 1
        prev_coda = coda
    clashes = sum(1 for a, b in zip(stress, stress[1:]) if a and b)
    lapse = max((len(m) for m in re.findall(r"0+", "".join(map(str, stress)))), default=0)
    pos = [i + 1 for i, s in enumerate(stress) if s]
    j = joins(line)
    return dict(syl=len(stress), grid=pos, clash=clashes, lapse=lapse, pause=pauses, cluster=clusters,
                joins=len(j), rare=[(a, b, r) for a, b, rs in j for r in rs if r in RARE])


def show(bars, tag):
    out = []
    for i, b in enumerate(bars, 1):
        p = bar_profile(b)
        out.append(p)
        line = (f"{tag}{i}. syl={p['syl']:>2} stress={p['grid']} clash={p['clash']} lapse={p['lapse']} "
                f"pause={p['pause']} cluster={p['cluster']} rare={len(p['rare'])}")
        if tag != "R" and p["rare"]:
            line += "   | " + "; ".join(f"{a} {b}: {r}" for a, b, r in p["rare"])
        print(line + ("" if tag == "R" else f"   | {b}"))
    return out


def selftest():
    """the measure must fire on the line Joe flagged, stay quiet on the others, and be quiet on reportage"""
    problems = []
    bad = "Cop in whites, he's wrecked my picket"
    got = {r for _, _, r in rare_joins(bad)}
    for want in ("fricative to H glottis reset", "voiced fricative to liquid"):
        if want not in got:
            problems.append(f"{want!r} not found in the flagged bar (got {sorted(got)})")
    for clean in ("Gnome's in good nick, so he says I nicked it",
                  "Might nip off, Oslo's the ticket",
                  "Two glasses, cold lager, back road corners"):
        if rare_joins(clean):
            problems.append(f"rare joins fired on {clean!r}: {rare_joins(clean)}")
    # the apostrophe fix is load-bearing: "he's" had no pronunciation at all and lost its /h/ and /z/
    d = pron("he's")
    if d != ["HH", "IY1", "Z"]:
        problems.append("pron of the contraction he's = %s, so the contraction table is unreachable" % d)
    return (not problems, "; ".join(problems) if problems else
            "rare joins fire on the flagged bar, quiet elsewhere; contractions pronounce")


def calibrate(path):
    """counts only (rule 4): the original's rare joins per bar. Never prints a line of the original."""
    import collections
    hist = collections.Counter()
    reasons = collections.Counter()
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()]
    for l in lines:
        rj = rare_joins(l)
        hist[len(rj)] += 1
        for _, _, r in rj:
            reasons[r] += 1
    n = len(lines)
    print(f"original rare joins per bar: {dict(sorted(hist.items()))} over {n} bars")
    print(f"  bars with 2 or more: {sum(c for k, c in hist.items() if k >= 2)} of {n}")
    for k, c in reasons.most_common():
        print(f"  {c:>3}  {k}")


def main():
    if "--selftest" in sys.argv:
        ok, msg = selftest()
        print(("PASSED: " if ok else "FAILED: ") + msg)
        sys.exit(0 if ok else 1)
    if "--calibrate" in sys.argv:
        calibrate(sys.argv[sys.argv.index("--calibrate") + 1])
        return
    lines = [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]
    ref, draft = ([], lines)
    if "---" in lines:
        k = lines.index("---")
        ref, draft = lines[:k], lines[k + 1:]
    r = show(ref, "R") if ref else []
    d = show(draft, "D")
    tot = lambda P, k: sum(x[k] for x in P)
    for k in ("clash", "pause", "cluster", "joins"):
        print(f"total {k}: draft {tot(d, k)}" + (f" vs ref {tot(r, k)}" if r else ""))
    print(f"total rare (mouth-shape) draft {sum(len(x['rare']) for x in d)}"
          + (f" vs ref {sum(len(x['rare']) for x in r)}" if r else "")
          + "   [the original's par: 0 in 78% of its bars, 2+ in 6 of 92]")
    if r:
        for i, (a, b) in enumerate(zip(r, d), 1):
            flags = []
            if b["clash"] > a["clash"]: flags.append("more clashes")
            if b["pause"] > a["pause"]: flags.append("mid-bar pause")
            if b["cluster"] > a["cluster"]: flags.append("consonant pile-up")
            if len(b["rare"]) > max(1, len(a["rare"])): flags.append("mouth-shape transition")
            if b["lapse"] > a["lapse"] + 1: flags.append("long weak run")
            if a["grid"] and b["grid"] and a["syl"] - a["grid"][-1] != b["syl"] - b["grid"][-1]: flags.append("rhyme stress moved")
            print(f"bar {i}: " + (", ".join(flags) if flags else "ok"))


if __name__ == "__main__":
    main()
