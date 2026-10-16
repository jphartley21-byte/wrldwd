"""ear: the sound devices that make a line SOUND good, as opposed to scan correctly.

Joe, 12 Oct 2026, on one of the original's verse couplets: "what about the reason that having Italian then
tell a man then tally up totals sounds so good to the ear?" He then corrected the tool itself: the drum
starts on "i-TAL-ian", in the PREVIOUS bar, and runs TELl, TALly, and the TAL of TOtals -- so the unit is
the SYLLABLE, not the word, and the frame crosses the bar line. The first version worked at word level
(first consonant ... last consonant), which grouped three of the four and could not see a cross-bar frame.

  PIVOT   a word straddling two rhymes: its first vowel is the previous bar's end vowel, its last vowel is
          this bar's end vowel, so one word hands the ear between the rhymes.
  DRUM    one syllable frame (onset consonant, coda consonant) used three or more times with the vowels
          MOVING, inside a window of a few bars. The couplet does it four times on one frame, ending on the
          block's rhyme vowel.
  ECHO    two or more DIFFERENT words sharing a word-level consonant frame with the SAME vowel. Also a
          device: a sound-alike pair, an inflected repeat, or a place name answering a word.
  CRUTCH  the same word (inflections counted together) three or more times. NOT a device -- this is how the
          internal-rhyme density gate was satisfied with filler earlier the same day ("bed" x4, "rail" x3).

The crustch/drum split is the point: density rewarded "bed x4" while the thing our blocks fail to do is the
drum, in which the vowel changes every time.

  python toolkit/ear.py -            (stdin: bars)
  python toolkit/ear.py --selftest
  python toolkit/ear.py --rate PATH_TO_ORIGINAL_LINES
"""
import os, re, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rhyme_tools as rt             # noqa: E402
import flow_fit as ff                # noqa: E402

import helpers                       # noqa: E402
ARPA_VOW = set("AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW".split())
IPA_VOW = helpers.VOWELS + "\u0250"     # + ɐ: Britfone writes the vowel of "one", "but" with it, and helpers.VOWELS lacks it


class _Vowels:
    """a phone is a vowel if it is an ARPAbet vowel (the US fallback) or an IPA vowel (helpers.uk_phones, the British reading)."""
    def __contains__(self, ph):
        return ph in ARPA_VOW or any(c in IPA_VOW for c in ph)


VOW = _Vowels()
STOP_C = set("P T K B D G p t k b d g".split())
PLURAL = {"Z", "S", "z", "s"}
WINDOW = 4                            # bars: a quad, or a couplet that reaches across a bar line
_CACHE = {}


def toks(bar):
    return re.findall(r"[A-Za-z']+", bar.lower())


def rg_stop():
    if "s" not in _CACHE:
        import regression as rg
        _CACHE["s"] = rg.STOP
    return _CACHE["s"]


def content(bar):
    return [w for w in toks(bar) if w not in rg_stop()]


def phones(word):
    """British phones (helpers.uk_phones: Britfone, else CMU + OVR in IPA), stress marks dropped; the US dictionary only when
    neither knows the word. 16 Oct 2026: the US reading gave 'Marathon' the vowel of 'merry' and 'bottle' the vowel of 'Bali',
    so a British ear's echoes were missed and false ones counted."""
    w = word.lower()
    uk = helpers.uk_phones(w) or (helpers.uk_phones(w.replace("'", "")) if "'" in w else None)
    if uk:
        return [x.replace("\u02c8", "").replace("\u02cc", "") for x in uk]
    return [re.sub(r"\d", "", p) for p in (rt.pron(w) or [])]


def sylls_of(word):
    """[(onset, vowel, coda)] -- each vowel paired with its NEAREST consonant on each side.

    Two earlier versions of this were wrong, and Joe's ear corrected both. A word-level frame missed
    "Italian" (its last consonant is N). A strict onset-maximising syllabifier then stripped the L out of
    "tally" into "ly", because phonetically that L does start the next syllable -- but the ear does not
    syllabify like a phonologist. It pairs each vowel with the consonant either side of it, which is what
    makes i-TAL, TELl, TALly and the TAL of TOtals one family. Ambisyllabic consonants are shared, exactly
    as the ear shares them.
    """
    p = phones(word)
    idx = [k for k, ph in enumerate(p) if ph in VOW]
    out = []
    for k in idx:
        prev = ""
        for j in range(k - 1, -1, -1):
            if p[j] not in VOW:
                prev = p[j]
                break
        nxt = ""
        for j in range(k + 1, len(p)):
            if p[j] not in VOW:
                nxt = p[j]
                break
        out.append((prev, p[k], nxt))
    return out


def word_profile(word):
    """(frame, vowels, stressed vowel) at WORD level, for the echo/crutch checks."""
    p = phones(word)
    if not p:
        return None
    cons = [x for x in p if x not in VOW]
    vow = [x for x in p if x in VOW]
    while len(cons) > 1 and cons[-1] in PLURAL:
        cons = cons[:-1]
    if not cons or not vow:
        return None
    return (cons[0], cons[-1]), tuple(vow), vow[0]


def frames(bars, window=WINDOW):
    """(onset, coda) -> [(bar, syllable, vowel)] over a sliding window of bars."""
    seen = {}
    n = len(bars)
    for start in range(max(1, n - window + 1)):
        chunk = bars[start:start + window]
        for i, b in enumerate(chunk):
            for w in toks(b):
                for onset, v, coda in sylls_of(w):
                    if onset and coda:
                        seen.setdefault((onset, coda), []).append((start + i + 1, onset + v.lower() + coda, v))
    return seen


def drums(bars, window=WINDOW):
    """THE DRUM: one syllable frame 3+ times with the vowels moving. [(frame, occ, (bar_from, bar_to))]"""
    out = []
    for f, ws in frames(bars, window).items():
        vowels = [v for _, _, v in ws]
        if len(ws) >= 3 and len(set(vowels)) > 1:
            bars_hit = sorted({b for b, _, _ in ws})
            out.append((f, ws, (bars_hit[0], bars_hit[-1])))
    return out


def end_vowel(bar):
    for w in reversed(toks(bar)):
        pr = word_profile(w)
        if pr:
            return pr[1][0]
    return None


def pivots(bars):
    """Words handing the ear from one bar's end rhyme to the next bar's."""
    found = []
    for i in range(len(bars) - 1):
        a, b = end_vowel(bars[i]), end_vowel(bars[i + 1])
        if not a or not b:
            continue
        for w in content(bars[i + 1]):
            pr = word_profile(w)
            if pr and len(pr[1]) >= 2 and pr[1][0] == a and pr[1][-1] == b:
                found.append((i + 1, i + 2, w, pr[1][0], pr[1][-1]))
    return found


def _stem(w):
    # a possessive is the same word (16 Oct 2026: "guy's guy" read as two words echoing, so one word said twice
    # passed as a sound-alike pair)
    w = w.replace("\u2019", "'")
    for s in ("'s", "s'"):
        if w.endswith(s) and len(w) > len(s):
            w = w[:-len(s)]
    return w[:-1] if len(w) > 3 and w.endswith("s") else w


def echoes(bars):
    """Frames shared by two or more DIFFERENT words (stem-compared) with the same vowel."""
    seen = {}
    for i, b in enumerate(bars):
        for w in content(b):
            pr = word_profile(w)
            if pr:
                seen.setdefault(pr[0], []).append((i + 1, w, pr[1][0]))
    return [(f, ws) for f, ws in seen.items()
            if len({_stem(w) for _, w, _ in ws}) > 1 and len({v for _, _, v in ws}) == 1]


VERBS = set("""grab grabs grabbed have having has had box boxed boxes package packaged packages ship
shipped ships spark sparked sparks take takes took taken get gets got put puts keep keeps kept let lets gave
give given make makes made do does did hold holds held run runs ran hit hits strike struck send sends sent
call calls called tell tells told chuck chucks chucked tap taps tapped slap slaps slapped bag bags bagged
pin pins pinned drop drops dropped fill fills filled pull pulls pulled""".split())


def governed(bars, word):
    """Distinct lexical verbs governing each occurrence of a word, looking back past articles and possessives
    ("grab THE crate" -- the verb is two words back, not one). This is the difference between the
    accumulation device and filler: measured on the original's quad, the repeated victim is governed by a
    different verb every time, so the repetition IS the escalation. In our own filler the repeated word sits
    between instances of itself with no verb governing it at all."""
    out = []
    for b in bars:
        w = toks(b)
        for i, x in enumerate(w):
            if _stem(x) != _stem(word) or not i:
                continue
            j = i - 1
            while j >= 0 and w[j] in rg_stop():
                j -= 1
            if j >= 0 and (w[j] in VERBS or w[j].endswith(("ed", "ing"))):
                out.append(w[j])
    return sorted(set(out))


def crutch(bars, limit=3):
    """The same word (stem-compared) three or more times, NOT governed by a different verb each time.
    Returns {word: (bars, verbs)}. A repeat governed by a different verb every time is the accumulation
    device -- the victim named again while something new is done to him -- and is not reported here."""
    seen = {}
    for i, b in enumerate(bars):
        for w in toks(b):
            if w not in rg_stop():
                seen.setdefault(_stem(w), []).append(i + 1)
    out = {}
    for w, idx in seen.items():
        if len(idx) < limit:
            continue
        v = governed(bars, w)
        if len(v) < limit - 1:
            out[w] = (idx, v)
    return out


def accumulations(bars, limit=3):
    """The opposite verdict: a word repeated three or more times with a different verb doing something to it
    each time. Reported as a DEVICE, because that is what the ear hears."""
    seen = {}
    for i, b in enumerate(bars):
        for w in toks(b):
            if w not in rg_stop():
                seen.setdefault(_stem(w), []).append(i + 1)
    out = {}
    for w, idx in seen.items():
        if len(idx) < limit:
            continue
        v = governed(bars, w)
        if len(v) >= limit - 1:
            out[w] = (idx, v)
    return out


def stops_report(bars):
    return [sum(1 for w in toks(b) for p in phones(w) if p in STOP_C) for b in bars]


def report(bars, label):
    print(f"== {label} ({len(bars)} bars)")
    st = stops_report(bars)
    for i, b in enumerate(bars, 1):
        print(f"  {i:>2}. stops {st[i - 1]:>2}  {b}")
    pv = pivots(bars)
    for a, b, w, va, vb in pv:
        print(f"  PIVOT bars {a}-{b}: '{w}' runs {va} (bar {a}'s end) into {vb} (bar {b}'s end)")
    dr = drums(bars)
    for f, ws, (b1, b2) in dr:
        prog = " -> ".join(v for _, _, v in ws)
        span = f"bars {b1}-{b2}" + ("  (CROSSES THE BAR LINE)" if b2 > b1 else "")
        print(f"  DRUM syllable frame {f[0]}_{f[1]} x{len(ws)}: {prog}   {span}")
        print(f"       {[(b, s) for b, s, _ in ws]}")
    for f, ws in echoes(bars):
        print(f"  ECHO word frame {f[0]}..{f[1]} ({ws[0][2]}): {[(b, w) for b, w, _ in ws]}")
    for w, (idx, v) in accumulations(bars).items():
        print(f"  ACCUMULATION '{w}' x{len(idx)} at bars {idx}: a new verb each time {v} "
              f"-- the repeat IS the escalation")
    for w, (idx, v) in crutch(bars).items():
        print(f"  CRUTCH '{w}' x{len(idx)} at bars {idx} (verbs: {v or 'none'}) -- same word, no new action")
    print(f"  -> pivots {len(pv)}, drums {len(dr)}, echoes {len(echoes(bars))}, "
          f"accumulations {len(accumulations(bars))}, crutches {len(crutch(bars))}")
    return pv, dr, echoes(bars), crutch(bars)


# --- selftest fixtures. SYNTHETIC on purpose: these exercise the same mechanisms as the original's lines
# without storing those lines in the project (rule 4). The real couplet and quad are checked by
# --check-original, which reads them from the private path and prints counts only.
PIVOT_FIXTURE = ["He paid for the week in Spain",
                 "then the halo went round and the total was low"]
DRUM_FIXTURE = ["The tall one and the tell", "the till and the tool"]
ACCUM_FIXTURE = ["Grab the crate then have the crate",
                 "Boxed the crate up, packaged the crate"]
CRUTCH_FIXTURE = ["Same beds same bunk and the same bar",
                  "Rail pass rail pass and the map goes far",
                  "Bed to bed bed to bed a ticket in the bin"]
FLAT_FIXTURE = ["Port in the glass and a page of totals",
                "Just numbers and dates in folders"]


def selftest():
    ok = True
    pv, dr, ec, cr = report(PIVOT_FIXTURE, "synthetic pivot: a word straddling two rhymes")
    ok &= len(pv) == 1 and pv[0][2] == "halo" and not cr
    print("   pivot on 'halo':", bool(pv) and pv[0][2] == "halo")
    pv2, dr2, ec2, cr2 = report(DRUM_FIXTURE, "synthetic drum: one syllable frame, four moving vowels")
    t_l = [d for d in dr2 if tuple(x.lower() for x in d[0]) == ("t", "l")]
    print(f"   T_L drum: {bool(t_l)}; occurrences {len(t_l[0][1]) if t_l else 0}; "
          f"crosses bars: {t_l[0][2][1] > t_l[0][2][0] if t_l else False}")
    ok &= bool(t_l) and len(t_l[0][1]) >= 4 and t_l[0][2][1] > t_l[0][2][0]
    _, _, _, cr3 = report(ACCUM_FIXTURE, "synthetic accumulation: one referent, a new verb each time")
    print("   caught as accumulation, not a crutch:", bool(accumulations(ACCUM_FIXTURE)) and not cr3)
    ok &= bool(accumulations(ACCUM_FIXTURE)) and not cr3
    _, _, _, cr4 = report(CRUTCH_FIXTURE, "our filler (must be caught as a crutch)")
    ok &= bool(cr4)
    pv5, dr5, ec5, cr5 = report(FLAT_FIXTURE, "our flat bars (must be quiet)")
    ok &= not pv5 and not dr5 and not ec5 and not cr5
    # 15 Oct 2026: a positive control on the four Hook 1-4 bars once called "Joe's approved bars" was removed (Joe:
    # never approved, never a bar or a gate again). The synthetic fixtures above carry the device checks.
    print("\nEAR SELFTEST:", "PASSED" if ok else "FAILED")
    return ok


def check_original(path, couplet_word="suede", quad_word="halogen"):
    """The real lines, read from outside the project. Each block's position is found by searching for a
    keyword, so no line has to be stored here. Prints counts, devices and vowel movements only."""
    allb = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
    def find(word, n):
        idx = [i for i, b in enumerate(allb) if word in b.lower()]
        return allb[idx[0]:idx[0] + 2] if idx else []
    quad_i = next((i for i, b in enumerate(allb) if quad_word in b.lower()), None)
    blocks = []
    c = find(couplet_word, 1)
    if c:
        blocks.append(("the couplet (2 bars ending on the verses' hinge)", c))
    if quad_i is not None:
        blocks.append(("the quad (4 bars)", allb[quad_i - 1:quad_i + 3]))
    for name, bars in blocks:
        print(f"== {name}")
        for i, b in enumerate(bars, 1):
            print(f"  {i}. syllables {len(ff.sylls(b))} stops {stops_report([b])[0]}")
        for a, b, w, va, vb in pivots(bars):
            print(f"  PIVOT bars {a}-{b}: {va} -> {vb} (word is {len(w)} letters)")
        for f, ws, span in drums(bars):
            print(f"  DRUM {f[0]}_{f[1]} x{len(ws)}: {' -> '.join(v for _, _, v in ws)} bars {span[0]}-{span[1]}"
                  + ("  CROSSES" if span[1] > span[0] else ""))
        for w, (idx, v) in accumulations(bars).items():
            print(f"  ACCUMULATION '{w}' x{len(idx)}, verbs {v}")
        for w, (idx, v) in crutch(bars).items():
            print(f"  CRUTCH '{w}' x{len(idx)}, verbs {v or 'none'}")


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    if "--check-original" in sys.argv:
        check_original(sys.argv[sys.argv.index("--check-original") + 1])
        return
    if "--rate" in sys.argv:
        path = sys.argv[sys.argv.index("--rate") + 1]
        lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
        pv, quads_d, quads_e, quads_c = pivots(lines), 0, 0, 0
        for s in range(0, len(lines) - 3, 4):
            q = lines[s:s + 4]
            quads_d += bool(drums(q))
            quads_e += bool(echoes(q))
            quads_c += bool(crutch(q))
        nq = len(range(0, len(lines) - 3, 4))
        print(f"the original: {len(lines)} bars | pivots {len(pv)} | quads with a drum {quads_d}/{nq} | "
              f"with an echo {quads_e}/{nq} | with a crutch {quads_c}/{nq}")
        for a, b, w, va, vb in pv:
            print(f"   pivot between bars {a}-{b}: {va} -> {vb}")
        return
    src = sys.argv[-1]
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf8").read()
    report([l.strip() for l in text.splitlines() if l.strip()], "stdin")


if __name__ == "__main__":
    main()
