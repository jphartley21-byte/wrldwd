"""meaning_gate: the meaning half of the review, mechanised as far as it honestly can be.

Run this BEFORE check_all. check_all measures form (rhyme, rhythm, density); this gate
measures whether each bar SAYS something. It exists because a pool optimised on form
alone fills up with rhyme-shaped noise: bars whose clause never finishes ("And I am off
and he"), bars with no content words at all ("And I am with them"), and device spam.

  python toolkit/meaning_gate.py FILE|-            per-bar findings + VERDICT
  python toolkit/meaning_gate.py --slot "V1 1-8" -  also checks place density for a verse slot
  python toolkit/meaning_gate.py --selftest         must catch known-bad stanzas and leave clean bars clean

What it can decide (G1 partly, G3 mostly):
  * end word: the payoff word must sit in the rhyme slot. A determiner, preposition,
    conjunction or bare auxiliary at the end FAILS (the clause runs off the end). A
    pronoun or a spoken tag (though, then, mate) is ALLOWED but capped, because the
    original enjambs lines on pronouns on purpose.
  * content: a bar needs content words. Zero = FAIL, one = warn, except the opening bar,
    which is deliberately the shortest.
  * filler frames: "and I am", "and it is" and friends are counted as a draft-level tic.
  * device spam: reduplications and repeated 3-grams are counted and capped.
  * place density: in verses, two places in two consecutive bars is flagged (G6).
What it cannot decide, and must stay human: G2 (would a mate get it), the truth flags,
whether a reduplication cashes a real phrase, and Joe's ear.
"""
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coherence_gate as cg  # noqa: E402
from rhyme_tools import FUNC  # noqa: E402

# End words that leave the clause unfinished: determiners, prepositions, conjunctions, bare auxiliaries.
END_DEAD = set("""a an the of to in on at for and or but so if as by with from up into onto upon via per
that this these those there then than is was are am be been being do does did not no too just all out off over
my your his her our their its""".split())
# Deliberate enjambment: the original ends lines on pronouns (and British speech tags on nothing).
END_ENJ = set("""i me him her us you them it we they he she ya yer em 'em""".split())   # ya / yer / em added 16 Oct 2026 (a pronoun-ending cap they escaped)
END_TAG = set("""though mate like nah right mind anyway innit yeah then""".split())
# Subject, object and possessive pronouns: a bar carrying one of these has someone in it, so it is
# not an inventory even when the rest of it is a noun list (see the INVENTORY rule in audit()).
PRON = END_ENJ | set("""my your his her our their its""".split())
# Pictureable things THIS song names in a bar. cg.OBJECTS is curated for the coherence gate and is
# missing half the writer's vocabulary ("rail", "cash", "card", "pass", "map", "plan"), which is what
# let comma-free noun stacks through the inventory rule. Every entry is a thing a bar can point at.
EXTRA_OBJECTS = set("""pass map maps plan plans rail rails cash card cards key keys kit bin bins
tent tents bike bikes ferry boat boats room rooms phone phones gate gates load loads case cases
luggage pannier panniers tyre tyres spanner helmet pack packs ticket tickets tenner fiver notes coins
change receipt ledger stock crate crates van vans train trains tram trams plane planes seat seats
bunk bunks hostel hostels pint pints fag fags gear route routes border borders list lists
name names number numbers mud dust smoke noise door doors window windows month months week weeks day days
country countries walk walks lad lads town towns border borders street streets road roads way ways""".split())

# Qualifiers do not stop a bar being stock-taking: "a packed bag a long rail a whole month" is three
# things with three adjectives on it. Without this set the stack test demanded that EVERY content word
# name an object, so one "long" or one "nine" disarmed it (13 Oct 2026).
MODIFIERS = set("""whole long cold packed same real little last full half all more most other next new old
big small two three four five six seven eight nine ten eleven twelve twenty fifty hundred thousand couple
few many several other another every each""".split())

FILLER = [re.compile(p) for p in (    r"\band i (?:am|is|was|are)\b", r"\band it (?:is|was|are)\b", r"\band he (?:is|was)\b",
    r"\band that (?:is|was)\b", r"\bnobody (?:knows|asked|said)\b", r"\bbloke at the\b",
)]
BAD_OPENERS = set("and so then but nobody bloke and-i".split())

# Places from material/travel_history.md and material/place_sound_families.md (Joe's real trips).
PLACES = set("""bordeaux porto oslo padstow bilbao koh tao barcelona bratislava ljubljana vienna zurich bern
interlaken lauterbrunnen florence zell munich augsburg amsterdam dublin donegal larrau vittoria vitoria burgos
fermoselle calais portsmouth bergen askoy nore marrakesh naples pompeii byron hervey proserpine townsville
magnetic cairns brisbane noosa k'gari kgari fraser whitsundays sydney melbourne perth bali gili trawangan
christchurch bangkok laos vietnam sydney amsterdam nantes domme laruns arbeost ainsa snowdon fan cornwall
padstow polzeath bodelva sennen dawlish ilfracombe scourie groats manchester reading bristol horfield boomtown
vitoria ljubljana bratislava zagreb mainz spain france italy turkey dubai gibraltar vegas lagos tobago jamaica""".split())


def words(text):
    return re.findall(r"[A-Za-z']+", text)


def content_words(text):
    return [w for w in words(text) if w.lower() not in FUNC]


def _objects_in(text):
    """How many of a phrase's words name a pictureable object, matching simple plurals.

    cg.OBJECTS is curated in the singular ("glass", not "glasses"), so a bare membership test
    misses the very words an inventory bar is made of. EXTRA_OBJECTS adds the things THIS song
    actually names in a bar -- cg.OBJECTS has "road" but not "rail", "bag" but not "cash" or "card".
    """
    n = 0
    for w in (x.lower() for x in words(text)):
        if (w in cg.OBJECTS or w in EXTRA_OBJECTS
                or (w.endswith("es") and (w[:-2] in cg.OBJECTS or w[:-2] in EXTRA_OBJECTS))
                or (w.endswith("s") and (w[:-1] in cg.OBJECTS or w[:-1] in EXTRA_OBJECTS))):
            n += 1
    return n


def _verbish(bar):
    """A conservative verb test, for the INVENTORY rule only.

    cg.has_verb() is too broad here: its VERBS set holds noun/verb homographs ("back", "glass"),
    which are precisely the words an inventory bar is built from, so it reports "Two glasses, cold
    lager, back road corners" as a sentence. This counts only auxiliaries, the verb BE, and the
    -ed/-ing forms, so it errs towards treating a bar as verbless (the safe direction for a rule
    that fires on verbless bars).
    """
    raw = words(bar)
    ws = [w.lower().strip("'") for w in raw]
    # A contraction implies a verb or auxiliary ("it's", "he's", "don't", "they'll"). The possessive
    # 's is the exception, but erring this way only makes the rule quieter, which is the safe
    # direction: without it, "Count to ten, mate, then it's home" reads as a verbless inventory.
    if any("'" in w for w in raw):
        return True
    if any(w in cg.AUX or w in cg.BE for w in ws):
        return True
    # An -ed/-ing word is the bar's verb only where a clause would put it: at the front, or after
    # somebody doing it ("and paid"). Elsewhere it is a modifier -- and counting "A packed bag a long
    # rail" as a sentence was the last hole in the stack test (13 Oct 2026).
    for i, w in enumerate(ws):
        if re.fullmatch(r"[a-z]+(ed|ing)", w) and len(w) > 4:
            if i == 0 or ws[i - 1] in PRON or ws[i - 1] in ("and", "then", "so", "but", "when", "to"):
                return True
    return False


def audit(bars, slot=None):
    """Per-bar and draft-level findings. Returns a dict; `fails` is the blocking list."""
    res = {"bars": [], "fails": [], "warns": []}
    n = len(bars)
    for i, b in enumerate(bars, 1):
        ws = words(b)
        lw = ws[-1].lower() if ws else ""
        cw = content_words(b)
        issues, hard = [], []
        if lw in END_DEAD:
            hard.append(f"end word '{lw}' is a function word: the clause runs off the end")
        elif lw in END_ENJ:
            issues.append(f"ends on the pronoun '{lw}' (enjambment: fine if the next bar finishes it)")
        elif lw in END_TAG:
            issues.append(f"ends on the spoken tag '{lw}' (fine once or twice)")
        if len(cw) == 0:
            hard.append("no content words at all: the bar says nothing")
        elif len(cw) == 1 and i != 1:
            issues.append(f"only one content word ('{cw[0]}')")
        # INVENTORY: a fragment is allowed (the original's bars are fragments), but three or more
        # comma-separated noun chunks naming concrete things is stock-taking, not a statement.
        # Added after Joe rejected "Two glasses, cold lager, back road corners" (12 Oct 2026) as
        # "a nothing line" -- it passed every other check here, because a noun list supplies the
        # images this gate asks for and never claims anything.
        # Deliberately narrow, because a bare comma count fires on three of the ORIGINAL's own
        # lines (a one-word greeting, a repeated-word refrain): on top of the
        # comma count, all but one chunk must name a pictureable object, and the bar must carry no
        # verb and no pronoun. Validated quiet on all 92 original lines and on Joe's approved bars.
        chunks = [c.strip() for c in b.split(",") if c.strip()]
        named = sum(1 for c in chunks if _objects_in(c))
        comma_case = (len(chunks) >= 3 and not _verbish(b)
                      and not any(w.lower() in PRON for w in ws)
                      and named >= len(chunks) - 1)
        # THE COMMA-FREE CASE (13 Oct 2026). The rule above needs commas to exist -- and the writer
        # stopped using them, because every comma fires check_all's mid-bar-pause flag. The result was
        # that the exact class of bar this rule exists to catch walked through it:
        # "Pass maps plans and the road the rail going" is the rejected line with its commas removed.
        # A bar whose CONTENT words are all but one pictureable objects, with no verb and nobody in it,
        # is stock-taking however it is punctuated. Validated: quiet on all 92 original lines, quiet on
        # Joe's approved bars, and it catches both comma and comma-free versions of the rejected lines.
        objs = _objects_in(b)
        # The tail word is excluded from the verb test, because the bars in this song END on the
        # -ing/-ed form ("going", "holding") -- the rhyme family for whole sections. To _verbish()
        # that tag reads as a verb, which silently disabled the comma-free case: every fitted bar
        # ends in one. So the rule asks whether the bar is a noun stack UP TO its tail.
        head = " ".join(ws[:-1]) if ws else ""
        cw_head = [w for w in cw if w.lower() != lw]
        # Modifiers are stripped before the object test, so a qualifier cannot disarm it. See MODIFIERS.
        stack_w = [w for w in cw_head if w.lower() not in MODIFIERS]
        objs_head = _objects_in(" ".join(stack_w))
        stack_case = (len(cw) >= 4 and len(stack_w) >= 3 and not _verbish(head)
                      and not any(w.lower() in PRON for w in ws)
                      and objs_head >= 3 and objs_head >= len(stack_w) - 1)
        if comma_case or stack_case:
            hard.append(f"inventory of {len(cw)} things and no claim "
                        f"({b}): names things, states nothing")
        for p in FILLER:
            if p.search(b.lower()):
                hard.append(f"filler frame /{p.pattern}/: the bar is scaffolding, not a sentence")
                break
        res["bars"].append((i, b, hard, issues))
    ends = [words(b)[-1].lower() for b in bars if words(b)]
    n_enj = sum(1 for w in ends if w in END_ENJ)
    # 16 Oct 2026: the cap was n // 19 (4 in 76 bars) and the ORIGINAL ends 8 of its 76 bars on a pronoun, most of them its two-word rhymes
    # ('for me', a word + 'him'). It is now the original's rate, so it still stops 'X me' being stacked but no longer forbids what it does.
    cap_enj = max(2, round(n * 8 / 76))
    if n_enj > cap_enj:
        res["fails"].append(f"{n_enj} bars end on a pronoun (cap {cap_enj}): enjambment is a technique, not a habit")
    openers = Counter(w.lower() for w in (words(b)[0] for b in bars if words(b)))
    for w, c in openers.items():
        if w in BAD_OPENERS and c > 2:
            res["fails"].append(f"opener '{w.title()}' x{c}: template opener (cap 2)")
        elif c > 3:
            res["warns"].append(f"opener '{w.title()}' x{c}")
    red = []
    for b in bars:
        red += re.findall(r"\b(\w+)-\1\b", b.lower())
    cap_red = max(2, n // 25)
    if len(red) > cap_red:
        res["fails"].append(f"{len(red)} reduplications {red} (cap {cap_red} for {n} bars): "
                            f"the original uses 2 in 76, both cashing a real phrase")
    elif red:
        res["warns"].append(f"reduplications to justify as real phrases: {red}")
    ng = Counter()
    for b in bars:
        w = [x.lower() for x in words(b)]
        for i in range(len(w) - 2):
            ng[" ".join(w[i:i + 3])] += 1
    rep = [(g, c) for g, c in ng.most_common(8) if c > 2]
    if rep:
        res["fails"].append("repeated 3-grams: " + ", ".join(f"'{g}' x{c}" for g, c in rep))
    elif any(c > 1 for _, c in ng.most_common(3)):
        res["warns"].append("3-grams used twice: " + ", ".join(f"'{g}'" for g, c in ng.most_common(3) if c > 1))
    # place density: only meaningful in verses; the hook is a roll call by design
    if slot and slot.startswith("V"):
        hits = [i for i, b in enumerate(bars, 1) if any(w.lower() in PLACES for w in words(b))]
        res["places"] = hits
        crowded = [(a, b) for a, b in zip(hits, hits[1:]) if b - a == 1]
        if crowded:
            res["fails"].append(f"two places in consecutive bars {crowded} (G6: one place per two bars in verses)")
        elif len(hits) > max(2, n // 3):
            res["warns"].append(f"{len(hits)} bars name a place of {n}")
    for i, b, hard, issues in res["bars"]:
        for h in hard:
            res["fails"].append(f"bar {i}: {h}")
    return res


def report(bars, slot=None):
    r = audit(bars, slot)
    print(f"== meaning gate: {len(bars)} bars" + (f", slot {slot}" if slot else "") + " ==\n")
    for i, b, hard, issues in r["bars"]:
        if hard:
            print(f"  x bar {i:>2}: {b[:64]}\n      -> {hard[0]}")
        elif issues:
            print(f"  ? bar {i:>2}: {b[:64]}\n      -> {issues[0]}")
    if not any(hard for _, _, hard, _ in r["bars"]):
        print("  (no bar-level hard failures)")
    for w in r["warns"]:
        print(f"  ~ {w}")
    for f in r["fails"]:
        if not f.startswith("bar "):
            print(f"  x {f}")
    verdict = "PASS" if not r["fails"] else f"NOT YET ({len(r['fails'])} fails)"
    print(f"\nMEANING GATE: {verdict}")
    print("  Human only: G2 would a mate get it, truth flags, does each reduplication cash a real phrase, Joe's ear.")
    return r


def selftest():
    bad = ["Beep-beep for the ferry", "Nobody asked and it is all very", "Bar on the deck is getting merry",
           "And I am off with the lot and I am with them", "And I am off and he", "Hop-hop and I am with them",
           "I said they are as sweet as the"]
    ok = True
    # 15 Oct 2026: the positive control used to be the four Hook 1-4 bars once called "Joe's approved bars". Joe: they
    # were never approved and must never be a bar or a gate again. The original is the positive control
    # (meaning_gate --calibrate PATH, asserted in calibrate.py); the clean-bar check below stays.
    r2 = audit(bad, "V1 1-8")
    good = bool(r2["fails"])
    ok &= good
    print(("ok  " if good else "BAD ") + f"a known-bad stanza is caught: {len(r2['fails'])} fails, "
                                          f"e.g. {r2['fails'][0][:60] if r2['fails'] else 'none'}")
    # The inventory rule (added 12 Oct 2026): the line Joe rejected must fail, while the bar before
    # it and the bar after it must not, so the rule cannot be passing by flagging the whole block.
    inv = ["Cold beer on the house in Porto", "Two glasses, cold lager, back road corners",
           "Not the worst pint and last orders", "Might hit the road to Majorca"]
    r3 = audit(inv, "Hook 5-8")
    inv_fails = [f for f in r3["fails"] if "inventory" in f]
    good = len(inv_fails) == 1
    ok &= good
    print(("ok  " if good else "BAD ") + f"the inventory line Joe rejected is caught, and only that bar: "
                                          f"{inv_fails[0][:70] if inv_fails else 'not caught'}")
    # The 13 Oct 2026 tightening. Four more bars Joe rejected as saying nothing ("nothing verses")
    # used to walk through this rule: one qualifier ("long", "nine") disarmed it, and one participle
    # in the middle of a list ("packed") read as the bar's verb. Each of these must be caught; each
    # of the clean bars below must stay clean.
    stack = ["A packed bag a long rail a whole month a road going",
             "Nine countries four walks cash going",
             "Got a pass and a rail the road going",
             "Took a month of the lads and bikes and bins and kit"]
    r4 = audit(stack, "V1 1-8")
    caught = sum(1 for f in r4["fails"] if "inventory" in f)
    good = caught == len(stack)
    ok &= good
    print(("ok  " if good else "BAD ") +
          f"the four claimless lists are caught too: {caught} of {len(stack)}")
    keep = ["Cash back on the bier in Zurich", "Stuck in the black van in all the traffic",
            "Sitting back with a real panic", "Might pack the backpack in Munich"]
    r5 = audit(keep, "Hook 5-8")
    kf = [f for f in r5["fails"] if "inventory" in f]
    good = not kf
    ok &= good
    print(("ok  " if good else "BAD ") + f"and clean bars stay clean: {kf or 'no inventory flags'}")
    return ok


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if a and a[0] == "--selftest":
        print("MEANING GATE SELFTEST", "PASSED" if selftest() else "FAILED")
        return
    slot = None
    if a and a[0] == "--slot":
        slot, a = a[1], a[2:]
    if a and a[0] == "--calibrate":
        # Counts only, never the lyrics (rule 4). What must hold: the INVENTORY rule -- the one
        # tightened on 13 Oct 2026 -- fires on none of the ORIGINAL's own lines, because a gate the
        # benchmark fails is a wrong gate. The other categories are printed for information: the
        # end-word rules DO fire on two of the original's lines, which is a known weakness of those
        # rules rather than of this one, and it is visible here rather than hidden.
        bars = [l.strip() for l in open(a[1], encoding="utf8") if l.strip()]
        r = audit(bars)
        kinds = {}
        for _i, _b, hard, _iss in r["bars"]:
            for f in hard:
                k = "INVENTORY" if f.startswith("inventory") else f.split(":")[0].split(" (")[0]
                kinds[k] = kinds.get(k, 0) + 1
        inv = kinds.get("INVENTORY", 0)
        print(f"meaning gate vs the original: {len(bars)} lines, {len(r['fails'])} fails, "
              f"{len(r['warns'])} warns")
        for k, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>3}  {k}")
        print(f"the inventory rule (13 Oct 2026) fires on the original {inv} times")
        print("CALIBRATION:", "PASSED" if inv == 0 else "FAILED")
        return
    if not a:
        print(__doc__)
        return
    src = a[0]
    from rhyme_tools import read_bars
    bars = read_bars(src)
    r = report(bars, slot)
    sys.exit(1 if r["fails"] else 0)


if __name__ == "__main__":
    main()
