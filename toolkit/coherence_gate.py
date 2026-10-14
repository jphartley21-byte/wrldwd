"""coherence_gate: the checks that catch "it does not say anything" and "there is no payoff".

meaning_gate asks whether each bar is a sentence with content. This gate asks the harder
question Joe asked: does the section hold together as ONE developing thought, in ONE voice,
and does it PAY OFF? Built from sourced craft principles (benchmark/craft_principles.md):

  X6  full clause per bar         - no telegraphy: dropped subjects/verbs to fit the rhyme.
  P10 no exophoric reference      - a pronoun that never resolves to an entity ("they" with no they).
  P9  cohesion / orphan bars      - every bar must link to the one before it (reference, repeated
                                    word, connective, or the section's repeated frame).
  P11 topic drift                - a bar introducing two unrelated new topics breaks the thread.
  X2  asserts-nothing             - a bar whose content words are all abstract/generic says nothing.
  X5  scene-hopping               - more than one unrelated scene per two bars is a checklist.
  P2  payoff / cashed idiom       - MEASURED and reported, NOT a gate since 11 Oct 2026 (Joe removed
                                    it: his own approved bars 1-4 cash nothing while par there is 3).
                                    X5/P12: the closing bar should call back to an earlier one.
  P8  supertask                   - the caller states the section's one-sentence goal; bars that
                                    do not advance it are orphans (printed for the human to judge).

  python toolkit/coherence_gate.py --goal "one sentence" FILE|-
  python toolkit/coherence_gate.py --selftest      the original's hook must PASS, a known scrapbook must FAIL
"""
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rhyme_tools import FUNC  # noqa: E402

BE = set("is are was were be been being am".split())
AUX = set("have has had will would can could might may must shall should do does did".split())
VERBS = set("""go goes went gone get gets got give gives gave take takes took come comes came
see sees saw seen say says said know knows knew think thinks thought want wants wanted need needs needed
look looks looked feel feels felt find finds found tell tells told ask asks asked work works worked
seem seems seemed try tries tried leave leaves left call calls called keep keeps kept let lets
begin begins began put puts puts mean means meant start starts started stop stops stopped
catch catches caught hold holds held stand stands stood sit sits sat walk walks walked run runs ran
wait waits waited pay pays paid eat eats ate drink drinks drank sleep sleeps slept wake wakes woke
send sends sent buy buys bought sell sells sold ride rides rode drive drives drove fly flies flew
board boards boarded land lands landed queue queues queued cross crosses crossed pass passes passed
miss misses missed book books booked pack packs packed carry carries carried lift lifts lifted
wave waves waved ring rings rang call calls called
sign signs signed stamp stamps stamped check checks checked catch catches caught fill fills filled
lose loses lost win wins won turn turns turned open opens opened close closes closed
hand hands handed point points pointed call calls called meet meets met lose loses lost
say says said wear wears wore wash washes washed cook cooks cooked boil boils boiled
count counts counted spend spends spent cost costs cost owe owes owed borrow borrows borrowed
happen happens happened change changes changed move moves moved stay stays stayed
learn learns learned forget forgets forgot remember remembers remembered
arrive arrives arrived return returns returned travel travels travelled
mustn't can't won't don't didn't doesn't isn't aren't wasn't weren't hasn't haven't hadn't
bought brought thought taught caught fought sought paid made took gave came went
take give make come put hold keep bring think find tell show hear play try
""".split())
PRON = set("he him she her they them it we us you i me his their its our your my".split())
GENERIC = set("""thing things stuff life time world way everything anything nothing something
idea ideas feeling feelings moment moments memory memories place places year years day days
people person reason reasons kind sorts sort part parts side sides bit bits way ways
anyone someone nobody everybody everybody everyone anywhere somewhere nowhere everywhere""".split())
PLURAL_OK = set("boys lads birds chicas blokes mates people police men women girls kids parents"
                " crowds queues hostels ferries boats days nights places years".split())
# stock phrases whose literal reading is a concrete thing (P19/P2): the cashed-idiom check
IDIOMS = ["chips down", "plain clothes", "one eye open", "lights out", "slap on the wrist", "wrist",
          "back shortly", "miss the boat", "on the house", "in the dark", "the long way",
          "out of the blue", "over the moon", "at the end of the day", "hold it down",
          "take the biscuit", "off the rails", "on the nose", "under the radar", "blue in the face",
          "spill the beans", "hit the sack", "in the bag", "on the ball", "the small print",
          "last straw", "cold turkey", "cut corners", "no-go", "no show", "dead end",
          "short notice", "free rein", "safe bet", "big deal", "on the cards", "in the same boat",
          "at sixes and sevens", "run of the mill", "on the ropes", "long way round", "ball park",
          "on a plate", "in the pipeline", "off the hook", "on the level", "the wrong end",
          "under his belt", "under the belt", "small talk", "keep in touch", "a name to a face",
          "put a name to a face", "no show", "hit the road", "the last leg", "check out"]


def _banked_phrases():
    """The shared phrase bank (toolkit/phrases.txt) - one list for writers and for this check.

    Writers pick stock phrases from bank.py; without this the cashed-idiom count would not see
    what they used. Report-only metric (P2, not a gate), so widening the list can only make the
    reported count more honest.
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phrases.txt")
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if line and not line.startswith("#"):
                out.append(line.split("|")[0].strip().lower())
    return out


IDIOMS = sorted(set(IDIOMS) | set(_banked_phrases()))
CONNECT = set("and then so but because if when while when and-so which that where as".split())
ABSTRACT_ONLY_MAX = 0   # bars whose content words are ALL generic


def words(t):
    return re.findall(r"[A-Za-z']+", t)


def content(t):
    return [w.lower() for w in words(t) if w.lower() not in FUNC]


def has_verb(bar):
    ws = [w.lower().strip("'") for w in words(bar)]
    if any(w in VERBS or w in BE or w in AUX for w in ws):
        return True
    # morphological fallback: -ed / -ing / -s forms next to a subject pronoun
    return any(re.fullmatch(r"[a-z]+(ed|ing)", w) and len(w) > 4 for w in ws)


# A bar may legitimately be a fragment (the original's is: a concrete noun phrase, no verb).
# What a fragment may NOT be is imageless: it must still give the listener something to picture.
OBJECTS = set("""bag bags rucksack case suitcase pack tent stove boot boots trainer shoes jacket
coat hat shirt trousers jeans socks kettle mug pint glass bottle plate food pasta banana bread
chips wallet ticket tickets passport paper papers receipt envelope map phone charger cable plug
socket photo camera bike motorbike van car train bus coach boat ferry plane bike helmet lock padlock
bed bunk pillow sheet towel key door window wall floor road lane pass hill mountain sea beach sand
guard officer gendarme copper bloke fella mate waiter porter driver ticket inspector
water rain snow sun towel kettle stove tin can tin bowl spoon knife fork cup tea coffee beer wine
photo picture folder box drive screen wire lead strap rope nail hammer tent peg peg
hand arm leg foot feet head face eye eyes ear mouth tooth hair elbow knee back chest
dog cat bird snake monkey horse cow fish kid child man woman boy girl mate mate
number numbers two three four five six seven eight nine ten twenty thirty forty fifty hundred
""".split())


def is_fragment_ok(bar):
    """A verbless bar is fine if the listener can picture something: an object, a place, a person."""
    from meaning_gate import PLACES
    lows = [w.lower() for w in words(bar)]
    if any(w in OBJECTS or w in PLACES for w in lows):
        return True
    # a proper noun (capitalised mid-bar) or a definite reference also gives an image
    return any(w[0].isupper() for w in words(bar)[1:]) or bool(re.search(r"\b(the|his|her|my|their)\b", bar.lower()))


BARE = re.compile(r"\b(?:a|an|another)\s+(place|day|week|thing|way|time|year|life|bit|lot|"
                  r"part|kind|sort|man|one|somewhere|anywhere)\b", re.I)


def imageless_fragments(bars):
    """Verbless bars with nothing to picture. Exempt: the opening bar (by design the barest), and
    non-English bars (a greeting or a borrowed line), which are checked by hand instead."""
    from rhyme_tools import pron
    out = []
    for i, b in enumerate(bars, 1):
        if i == 1 or has_verb(b) or is_fragment_ok(b):
            continue
        oov = [w for w in words(b) if pron(w.lower()) is None]
        if len(oov) >= 2:      # a foreign phrase, not our problem to parse
            continue
        out.append((i, b))
    return out


def links(prev, cur, frame_of):
    """Name the link from `cur` back to `prev`, or None. Order matters: strongest first."""
    pc, cc = set(content(prev)), set(content(cur))
    if pc & cc:
        return "repeated word: " + ", ".join(sorted(pc & cc))
    if any(w in PRON for w in [x.lower() for x in words(cur)]) and pc:
        return "reference (pronoun back to the previous bar)"
    if words(cur) and words(cur)[0].lower() in CONNECT:
        return "conjunction: " + words(cur)[0].lower()
    if frame_of(prev) and frame_of(prev) == frame_of(cur):
        return "repeated frame: " + frame_of(cur)
    return None


def frame_of(bar):
    """A crude structural frame: the greeting+place shape, or the first two words."""
    if re.search(r"\b(ola|ahoj|g'day|hei|ciao|kaixo|servus|bonjour|bonjourno|hasta|ese|wagwan|salam|zivjo)\b",
                 bar.lower()):
        return "greeting frame"
    ws = [w.lower() for w in words(bar)]
    return " ".join(ws[:2]) if len(ws) >= 2 else None


SLOT_CASH = None


def _orig_bars():
    import os
    p = os.path.join(os.path.expanduser("~"), "Documents", "Worldwide_private", "original_lines.txt")
    if not os.path.exists(p):
        return []
    return [l.strip() for l in open(p, encoding="utf8") if l.strip()]


def craft_idioms(bar):
    """Idiom names in one bar, tolerant of words inside the phrase (see craft_scan.idioms_in)."""
    low = bar.lower()
    out = []
    import re
    for k in IDIOMS:
        pat = r"\b" + r"\W+(?:\w+\W+){0,2}?".join(re.escape(w) + r"\w{0,4}" for w in k.split()) + r"\b"
        if re.search(pat, low):
            out.append((k, "idiom"))
    return out


def craft_pun_pairs(bars, max_gap=3):
    """Cross-bar homophone pairs (plain/plane), the second way a bar can pay something off."""
    try:
        import craft_scan
        return craft_scan.homophone_pairs(bars, max_gap=max_gap)
    except Exception:
        return []


def cash_par(goal, n):
    """How many cash events (cashed idiom + cross-bar pun) the original itself has in the same
    lines. The requirement is the original's own count, scaled to the block length and floored, so
    the original only just passes at every position and any block that cashes less fails."""
    global SLOT_CASH
    if SLOT_CASH is None:
        SLOT_CASH = {}
        try:
            import rubric_score as rs
            blocks = rs.orig_blocks(rs.ORIG)
        except Exception:
            blocks = {}
        for name, bars in blocks.items():
            k = len([x for x in IDIOMS if x in " ".join(b.lower() for b in bars)]) \
                + len(craft_pun_pairs(bars))
            SLOT_CASH[name] = (k, len(bars))
    if goal and goal in SLOT_CASH:
        k, nb = SLOT_CASH[goal]
        return int(k * n / nb)
    # unknown position: use the hook's own rate (the densest part of the original)
    k, nb = SLOT_CASH.get("Hook 1-16", (4, 16))
    return int(k * n / nb)


def audit(bars, goal=None):
    res = {"fails": [], "warns": [], "orphans": [], "links": []}
    n = len(bars)
    for i, b in enumerate(bars, 1):
        cw = content(b)
        if cw and all(w in GENERIC or w in FUNC for w in cw):
            res["fails"].append(f"bar {i}: content is all generic/abstract, it asserts nothing: {b[:52]}")
        lows = [w.lower() for w in words(b)]
        for p in ("they", "them"):
            if p in lows:
                prev = " ".join(bars[max(0, i - 3):i - 1]).lower()
                plural = any(w in PLURAL_OK for w in words(prev)) or bool(
                    re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|both|they|them)\b", prev))
                # any plural noun in the previous bars is a legitimate antecedent
                plural = plural or any(w.endswith("s") and len(w) > 3 for w in words(prev))
                if not plural:
                    res["fails"].append(f"bar {i}: '{p}' has no antecedent in the bars before it: {b[:52]}")
        m = BARE.search(b)
        if m:
            res["fails"].append(f"bar {i}: bare indefinite '{m.group(0)}' - nothing to picture "
                                f"(exophoric, P10): {b[:52]}")
        if i > 1:
            lk = links(bars[i - 2], b, frame_of)
            res["links"].append((i, lk))
            if lk is None:
                res["orphans"].append((i, b))
    frag = imageless_fragments(bars)
    for i, b in frag:
        res["fails"].append(f"bar {i}: fragment with no image (no object, place or person to picture): {b[:52]}")
    # orphan bars are a warning, not a failure: the original's cohesion is carried by the repeated
    # frame and the fixed persona, which a link test cannot see.
    if len(res["orphans"]) > max(1, n // 2):
        res["warns"].append(f"{len(res['orphans'])} bars do not link word-wise to the one before "
                            f"(the original has 9 of 16; its cohesion is the repeated frame and the fixed "
                            f"persona). Check the frame and the voice, not the words.")
    # X5: unrelated scenes. One place per two bars.
    from meaning_gate import PLACES
    ph = [(i, [w.lower() for w in words(b) if w.lower() in PLACES]) for i, b in enumerate(bars, 1)]
    hits = [(i, p) for i, p in ph if p]
    crowded = [(a, b) for (a, _), (b, _) in zip(hits, hits[1:]) if b - a == 1]
    if len(crowded) > max(1, n // 6):
        res["warns"].append(f"{len(crowded)} consecutive place pairs {crowded}: check it is a deliberate "
                            f"roll call and not scene-hopping (X5)")
    # P2 cash events: MEASURED, no longer a GATE (Joe, 11 Oct 2026: "remove the cash event gate").
    # Why: Joe's own APPROVED bars 1-4 cash nothing while the par at that position is 3, so the gate
    # failed his own locked section. A gate that rejects the standard it is calibrated against is
    # measuring the wrong thing. The count is still returned, and still printed, as a quality signal.
    # The scrapbook calibration is unaffected: it fails on two bare indefinites as well.
    low = " ".join(b.lower() for b in bars)
    found = sorted({n for b in bars for n, _reg in craft_idioms(b)})
    if found:
        res["idioms"] = found
    puns = craft_pun_pairs(bars)
    res["cash_events"] = len(found) + len(puns)
    res["cash_par"] = cash_par(goal, n)
    # P12: a callback from the closing bar to the first half is a bonus, not a requirement
    # (the original's own closer does not echo its opening - its bookend is the repeated chorus).
    if n >= 6:
        early = set()
        for b in bars[:n // 2]:
            early |= set(content(b))
        last = set(content(bars[-1]))
        if early & last:
            res["payoff"] = sorted(early & last)
        else:
            res["warns"].append("the closing bar echoes nothing from the first half: no local callback "
                                "(the original does not either - fine for a hook, but a verse closer should land)")
    if goal:
        res["goal"] = goal
    return res


def report(bars, goal=None):
    r = audit(bars, goal)
    print(f"== coherence gate: {len(bars)} bars ==")
    if goal:
        print(f"  SUPERTASK (P8): {goal}")
        print("  Every bar must advance that one sentence; a bar that does not is an orphan to cut.\n")
    for i, b in enumerate(bars, 1):
        lk = dict(r["links"]).get(i)
        print(f"  {i:>2}. {b[:62]:<62} {'<- ' + lk if lk else '<- ORPHAN'}")
    if r.get("idioms"):
        print(f"\n  cashed idioms present (P2, reported not gated): {', '.join(r['idioms'])}")
    if "cash_events" in r:
        print(f"  cash events {r['cash_events']} (par for this position {r.get('cash_par')}) "
              f"- reported, NOT a gate since 11 Oct 2026")
    if r.get("payoff"):
        print(f"  closing bar calls back to the first half (P12): {', '.join(r['payoff'])}")
    for w in r["warns"]:
        print(f"  ~ {w}")
    for f in r["fails"]:
        print(f"  x {f}")
    v = "PASS" if not r["fails"] else f"NOT YET ({len(r['fails'])} fails)"
    print(f"\nCOHERENCE GATE: {v}")
    if r["fails"]:
        print("  Rule: a bar that fails a gate is REWRITTEN, not scored.")
    return r


SCRAPBOOK = ["He was out on the water at the Whitsundays",
             "Then Byron Bay for the surfing he never did",
             "Three nights in a hostel in Ljubljana",
             "A place he cannot pronounce and a plate of pasta",
             "They stop him again before the border",
             "He lost a whole day",
             "Same bag same bus same banana",
             "Might do another week in Zell am See"]


def selftest():
    ok = True
    r = audit(SCRAPBOOK, "a scrapbook of unrelated travel facts")
    bad = bool(r["fails"])
    ok &= bad
    print(("ok  " if bad else "BAD ") + f"a scrapbook stanza is caught: {len(r['fails'])} fails"
          + (f" e.g. {r['fails'][0][:64]}" if r["fails"] else ""))
    # the benchmark's own hook must pass this gate (the original is the standard) - checked quad by
    # quad, because a per-quad cash rule that the original's own back half fails is mis-calibrated
    orig = os.path.join(os.path.expanduser("~"), "Documents", "Worldwide_private", "original_lines.txt")
    if os.path.exists(orig):
        bars = [l.strip() for l in open(orig, encoding="utf8") if l.strip()][:16]
        for a, nm in ((0, "Hook 1-4"), (4, "Hook 5-8"), (8, "Hook 9-16")):
            r2 = audit(bars[a:a + 4], nm)
            good = not r2["fails"]
            ok &= good
            print(("ok  " if good else "BAD ") + f"the original's own {nm} PASSES the gate"
                  + ("" if good else ": " + "; ".join(r2["fails"])[:110]))
        r3 = audit(bars, "the original's own hook")
        good = not r3["fails"]
        ok &= good
        print(("ok  " if good else "BAD ") + "the original's 16-bar hook PASSES the gate"
              + ("" if good else ": " + "; ".join(r3["fails"])[:110]))
    return ok


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if a and a[0] == "--selftest":
        print("COHERENCE GATE SELFTEST", "PASSED" if selftest() else "FAILED")
        return
    goal = None
    if a and a[0] == "--goal":
        goal, a = a[1], a[2:]
    src = a[0] if a else "-"
    from rhyme_tools import read_bars
    bars = read_bars(src)
    r = report(bars, goal)
    sys.exit(1 if r["fails"] else 0)


if __name__ == "__main__":
    main()
