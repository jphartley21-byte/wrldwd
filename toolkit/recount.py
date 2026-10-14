"""recount: does a section TELL what happened (a holiday diary) or CLAIM something?

Why it exists (14 Oct 2026). Every draft of the travel song so far reads as a diary: one event per bar, in time order, past
tense, "we did X, then Y" -- the v17 itinerary verse ("Stop one is ... Then ... Then ..."), the Hanoi verse ("We left ... We
rode ... We lost ..."), the flow-fitted v5 jeep verse. Joe's words: "a recount of not that interesting stuff I did on holiday",
"they say nothing", "CLAIMS not events". The form tools could not see it: a recounted bar can be perfectly on the audio frame,
rhyme on the by-ear scheme and pass meaning_gate (it states something; it just states the next thing that happened). Nothing in
the repo measured recounting, and several writer prompts actively asked for it.

What it measures, per bar (spaCy tags, deterministic, no model call):
  past      a past-tense finite verb (VBD)
  stance    a modal (might/would/can...), an imperative opener, or a present-tense claim by the speaker ("I'm", "I've got")
  event     past AND no stance marker: something happened, reported, with no attitude taken towards it
  itinerary a sequencing marker (stop one/two, then, next, after that, first, later, by the time, when we...) in a bar that also
            names a place, uses a travel verb or counts stops -- the place list in time order
  recount   event OR itinerary
and per section:
  share     recount bars / bars
  chain     the longest run of consecutive recount bars (the diary: one thing after another)
  itinerary the number of itinerary bars
  we        bars whose subject is "we" (the group holiday voice; reported, not gated)
  overlap   (drafts only) how much of the section's content words, IN ORDER, come straight from one material entry
            (ww/schema/joe_facts.py and material/*.md): high means paraphrase of the source, not a claim built from it.
            Reported only: the original has no material, so there is no benchmark for it.

THE GATE is calibrated on the ORIGINAL, never guessed (a gate the benchmark fails is a wrong gate):
  chain     <= the original's longest chain at that level (hook / verse), floor 1 (one past bar is not a chain)
  share     <= the original's highest section share at that level, plus one bar (SHARE_MARGIN_BARS)
  itinerary <= the original's highest per-section itinerary count at that level
  song      the whole song's recount share <= the original's + SONG_MARGIN
`--calibrate PATH` reads the original from outside the project and prints counts only (rule 4); it asserts the original passes.
The negative controls are the known recounts named above (asserted in calibrate.py when the drafts are present).

  python toolkit/recount.py writing/ww_full_draft_vN.md         a draft with '== Slot' headers
  python toolkit/recount.py --slot "V1 9-16" -                   one section on stdin
  python toolkit/recount.py --calibrate PATH                     counts only, asserts the original passes
  python toolkit/recount.py --selftest
"""
import argparse
import functools
import math
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---- the par, measured from the original with --calibrate (14 Oct 2026). Counts only. ----------------------------------
# The original's per-section values (Hook 1-4 .. V2 9-16):
#   chain     0 0 0 | 0 3 2 1 3 0 1          -> hook 0 (floor 1), verse 3
#   share     .00 .00 .00 | .00 .38 .25 .25 .50 .00 .25   -> hook .00, verse .50
#   itinerary 0 0 0 | 0 0 0 0 0 0 0          -> 0 everywhere: the original never sequences places in time order
#                                               (its "then" is an imperative cadence, not a timetable)
#   song share 15 of 76 = .20
PAR = {
    "hook": {"chain": 1, "share": 0.00, "itinerary": 0},
    "verse": {"chain": 3, "share": 0.50, "itinerary": 0},
}
SHARE_MARGIN_BARS = 1   # a section may carry ONE recounted bar more than the original's busiest section's share allows
#                         (a 4-bar hook block may hold one past-tense bar; the original's hooks hold none)
SONG_MARGIN = 0.10      # the song may run at most this far above the original's whole-song share
OVERLAP_NOTE = 0.45     # report: share of a section's content words found in order in ONE material entry

SEQ = re.compile(
    r"\b(stop (one|two|three|four|five|six|seven|eight|nine|ten|\d+)|first stop|next stop|last stop|"
    r"then|next|after that|afterwards|later on|later|finally|by the time|when we|when i got|"
    r"after (a|the|two|three|four|five|six|seven) (day|days|week|weeks|night|nights|hour|hours))\b", re.I)
# The ordinal / stop frames are an itinerary on their own ("Stop one is Zurich", "next stop", "day two").
STRONG = re.compile(r"\b(stop (one|two|three|four|five|six|seven|eight|nine|ten|\d+)|(first|next|last|final) stop|"
                    r"day (one|two|three|four|five|six|seven))\b", re.I)
OFF_TO = re.compile(r"\b(?:[Oo]ff|[Oo]n|[Hh]eaded|[Bb]ack) (?:to|for|in) (?:the )?[A-Z]")
SEQ_WORDS = {"then", "next", "afterwards", "later", "finally"}
# Travel verbs as lemmas; one only counts towards an itinerary when its subject is the speaker or the group and it is not the
# "go on then" cadence (the original's imperative accumulation uses "then" and "go" without moving anywhere).
TRAVEL_LEMMA = {"go", "ride", "fly", "drive", "arrive", "leave", "head", "travel", "cross", "land", "walk", "hike",
                "sail", "board", "depart", "return", "tube", "cycle", "train", "visit", "stay", "book", "move"}
TRAVEL_FRAME = re.compile(r"\b(took|take|takes|caught|catch|got|get) (a|the|my|our) (train|bus|ferry|boat|flight|plane|"
                          r"tram|coach|taxi|tuk-?tuk)\b", re.I)
SPEAKER_PRESENT = re.compile(r"\b(i'm|i am|i've|i have|i got|i'll|imma|i keep|i stay|i need|i want|i own|i'm on|i do)\b",
                             re.I)
CONTENT_STOP = set("""a an the and or but so to of in on at for with from by as is are was were be been it its this that
these those i me my we us our you your he him his she her they them their there here then than not no nor just only very
too up down out off over into onto about all some any one two got get had have has did do does i'm it's that's what's""".split())


@functools.lru_cache(maxsize=1)
def _nlp():
    import spacy
    return spacy.load("en_core_web_sm")


@functools.lru_cache(maxsize=1)
def _places():
    try:
        import regression as rg
        return rg.load_supply()[0]
    except Exception:
        return set()


def _place_tok(t, places):
    return t.text[:1].isupper() and t.lower_ in places and t.lower_ not in ("i", "the", "one", "we", "it", "a")


def _itinerary(doc, toks, bar, places):
    """the place list in time order: an ordinal/stop frame, 'off to PLACE', a sequencing word right next to a place name
    ('Then Vienna', 'Florence next'), or a sequencing word plus a journey verb whose subject is I/we."""
    if STRONG.search(bar) or OFF_TO.search(bar):
        return True
    for k, t in enumerate(toks):
        if t.lower_ in SEQ_WORDS:
            near = toks[max(0, k - 3):k] + toks[k + 1:k + 3]
            if any(_place_tok(x, places) for x in near):
                return True
    if SEQ.search(bar):
        for t in toks:
            if t.lemma_.lower() in TRAVEL_LEMMA and t.pos_ in ("VERB", "AUX"):
                subj = [c for c in t.children if c.dep_.startswith("nsubj")]
                go_on = t.i + 1 < len(doc) and doc[t.i + 1].lower_ == "on"
                if subj and subj[0].lower_ in ("i", "we") and not go_on:
                    return True
        if TRAVEL_FRAME.search(bar):
            return True
    return False


IMPERATIVE_OPENERS = {"don't", "dont", "do", "never", "let", "let's", "lets", "go", "come", "get", "keep", "ask", "tell"}


@functools.lru_cache(maxsize=4096)
def bar_features(bar):
    doc = _nlp()(bar)
    toks = [t for t in doc if not t.is_punct]
    places = _places()
    past = any(t.tag_ == "VBD" for t in toks)
    modal = any(t.tag_ == "MD" for t in toks)
    first = toks[0] if toks else None
    imperative = bool(first is not None and (
        (first.tag_ == "VB" and first.lower_ != "be" and not any(c.dep_.startswith("nsubj") for c in first.children))
        or (first.lower_ in IMPERATIVE_OPENERS and len(toks) > 1 and toks[1].lower_ in ("n't", "not", "on", "ask", "me",
                                                                                         "your", "it", "him", "them"))))
    speaker_present = bool(SPEAKER_PRESENT.search(bar))
    stance = modal or imperative or speaker_present
    we = any(t.lower_ == "we" and t.dep_.startswith("nsubj") for t in toks)
    event = past and not stance
    itinerary = _itinerary(doc, toks, bar, places)
    return {"past": past, "stance": stance, "seq": bool(SEQ.search(bar)), "we": we,
            "event": event, "itinerary": itinerary, "recount": event or itinerary}


def section_measures(bars):
    fs = [bar_features(b) for b in bars]
    run = best = 0
    for f in fs:
        run = run + 1 if f["recount"] else 0
        best = max(best, run)
    n = len(bars)
    return {"n": n, "recount": sum(f["recount"] for f in fs), "share": (sum(f["recount"] for f in fs) / n) if n else 0.0,
            "chain": best, "itinerary": sum(f["itinerary"] for f in fs), "events": sum(f["event"] for f in fs),
            "we": sum(f["we"] for f in fs), "stance": sum(f["stance"] for f in fs),
            "codes": "".join("I" if f["itinerary"] else "E" if f["event"] else "s" if f["stance"] else "." for f in fs)}


def level_of(slot):
    return "hook" if (slot or "").lower().startswith("hook") else "verse"


def section_fails(slot, m):
    par = PAR[level_of(slot)]
    out = []
    if m["chain"] > par["chain"]:
        out.append(f"{slot}: {m['chain']} recounted bars in a row (the original's longest at this level: {par['chain']})")
    allowed = math.ceil(par["share"] * m["n"] - 1e-9) + SHARE_MARGIN_BARS
    if m["recount"] > allowed:
        out.append(f"{slot}: {m['recount']} of {m['n']} bars recount events (allowed {allowed}: the original's busiest "
                   f"{level_of(slot)} section runs at {par['share']:.0%}, plus {SHARE_MARGIN_BARS} bar)")
    if m["itinerary"] > par["itinerary"]:
        out.append(f"{slot}: {m['itinerary']} itinerary bars (places or moves in time order; the original has "
                   f"{par['itinerary']})")
    return out


# ---- material overlap (drafts only, report) -----------------------------------------------------------------------------
def _content(text):
    return [w for w in re.findall(r"[a-z][a-z']+", text.lower()) if w not in CONTENT_STOP and len(w) > 2]


@functools.lru_cache(maxsize=1)
def material_entries():
    """[(label, [content words])] from joe_facts.FACTS and every paragraph of material/*.md (git-ignored personal files
    included when present on this machine; nothing is written out from them)."""
    out = []
    try:
        sys.path.insert(0, ROOT)
        from ww.schema.joe_facts import FACTS
        for f in FACTS:
            out.append((f"fact:{f.id}", _content(" ".join([f.place, f.trip, f.detail]))))
    except Exception:
        pass
    for p in sorted(glob.glob(os.path.join(ROOT, "material", "*.md"))):
        try:
            text = open(p, encoding="utf8", errors="replace").read()
        except OSError:
            continue
        for k, para in enumerate(re.split(r"\n\s*\n", text)):
            ws = _content(para)
            if len(ws) >= 6:
                out.append((f"{os.path.basename(p)}#{k}", ws))
    return out


def _lcs(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def material_overlap(bars):
    words = _content(" ".join(bars))
    if not words:
        return 0.0, None
    best = (0.0, None)
    for label, src in material_entries():
        r = _lcs(words, src) / len(words)
        if r > best[0]:
            best = (r, label)
    return best


# ---- running -----------------------------------------------------------------------------------------------------------
def run(sections, overlap=True, quiet=False):
    """sections = [(slot, bars)]. Returns (fails, per-section rows, song share)."""
    fails, rows = [], []
    total = rec = 0
    for slot, bars in sections:
        if not bars:
            continue
        m = section_measures(bars)
        total += m["n"]
        rec += m["recount"]
        if overlap:
            m["overlap"], m["overlap_src"] = material_overlap(bars)
        rows.append((slot, m))
        fails += section_fails(slot, m)
    song = rec / total if total else 0.0
    song_par = ORIGINAL_SONG_SHARE + SONG_MARGIN
    if song > song_par + 1e-9:
        fails.append(f"SONG: {rec} of {total} bars recount events ({song:.0%}; the original {ORIGINAL_SONG_SHARE:.0%} "
                     f"+ {SONG_MARGIN:.0%} margin)")
    if not quiet:
        for slot, m in rows:
            ov = (f"  overlap {m['overlap']:.0%} ({m['overlap_src']})" if m.get("overlap_src") else "")
            flag = "  <- paraphrase of the source?" if m.get("overlap", 0) >= OVERLAP_NOTE else ""
            print(f"  {slot:10} {m['codes']:12} recount {m['recount']:2}/{m['n']:<2} chain {m['chain']} "
                  f"itin {m['itinerary']} we {m['we']} stance {m['stance']}{ov}{flag}")
        print(f"  song recount share {song:.0%} ({rec}/{total}); codes: E event, I itinerary, s stance, . other")
    return fails, rows, song


ORIGINAL_SONG_SHARE = 0.20   # measured with --calibrate (15 of 76 bars)


def sections_of(text):
    import songcheck as sc
    return [(s, b) for s, b in sc.bars_of(text) if s]


def original_sections(path):
    import songcheck as sc
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
    return [(s, lines[a:b]) for s, a, b in sc.ORIG_SEC]


def calibrate(path):
    """counts only (rule 4). Prints the measured par so the constants above can be checked, and asserts the original passes."""
    secs = original_sections(path)
    by_level = {"hook": {"chain": 0, "share": 0.0, "itinerary": 0}, "verse": {"chain": 0, "share": 0.0, "itinerary": 0}}
    for slot, bars in secs:
        m = section_measures(bars)
        lv = by_level[level_of(slot)]
        lv["chain"], lv["share"], lv["itinerary"] = (max(lv["chain"], m["chain"]), max(lv["share"], m["share"]),
                                                     max(lv["itinerary"], m["itinerary"]))
        print(f"  {slot:10} recount {m['recount']:2}/{m['n']:<2} chain {m['chain']} itin {m['itinerary']} "
              f"events {m['events']} stance {m['stance']} we {m['we']}")
    fails, _rows, song = run(secs, overlap=False, quiet=True)
    print(f"  measured par: hook {by_level['hook']}, verse {by_level['verse']}, song share {song:.2f}")
    drift = []
    for lv in ("hook", "verse"):
        if max(1, by_level[lv]["chain"]) != PAR[lv]["chain"] or by_level[lv]["itinerary"] != PAR[lv]["itinerary"] \
                or abs(by_level[lv]["share"] - PAR[lv]["share"]) > 0.005:
            drift.append(lv)
    if abs(song - ORIGINAL_SONG_SHARE) > 0.005:
        drift.append("song")
    for f in fails:
        print("  ! " + f)
    if drift:
        print(f"  ! PAR constants are stale for {drift}: update PAR / ORIGINAL_SONG_SHARE from the line above")
    ok = not fails and not drift
    print("recount CALIBRATION:", "PASSED (the original clears its own par)" if ok else "FAILED")
    return ok


NEGATIVES = [  # the recounts Joe and I named (14 Oct 2026): each must FAIL the gate
    ("writing/ww_full_draft_v17.md", "V1 33-44"),            # the itinerary: stop one / then / then / next
    ("writing/ww_full_draft_v17.md", "V2 1-8"),              # the Hanoi diary: we left / we rode / we lost
    ("writing/detection_test/travel_draft_v5.md", "V1 9-16"),  # the jeep: stuck / pushed / got left / found / waited
]


def negatives_check():
    """[(label, fails)] for every negative present on disk."""
    out = []
    for rel, slot in NEGATIVES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        secs = dict(sections_of(open(p, encoding="utf8").read()))
        if slot in secs:
            out.append((f"{rel} {slot}", section_fails(slot, section_measures(secs[slot]))))
    return out


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print("  FAIL", name)

    diary = ["We left the hostel at nine with no clues", "We rode the bikes along the coast for days",
             "The rain came down and soaked us to the bone", "We lost each other in the traffic queues",
             "I ditched the bike beside the road at night", "I lost the key and someone nicked the lids"]
    m = section_measures(diary)
    chk("a past-tense diary is a chain", m["chain"] >= 5)
    chk("the diary fails the verse gate", bool(section_fails("V1 1-8", m)))
    itin = ["Stop one is Zurich and the beer is dear", "Then Munich where the trains are always late",
            "Vienna next and the cake is the size of a plate", "Then Prague and the bridge with the statues on"]
    mi = section_measures(itin)
    chk("an itinerary is caught", mi["itinerary"] >= 3)
    chk("the itinerary fails", any("itinerary" in f for f in section_fails("V1 33-44", mi)))
    claims = ["I might sell the gnome back to the council", "Keep your receipts, I keep a ledger for the lads",
              "I'm the only tourist with a pension in Peru", "Don't ask how the hat got through customs"]
    mc = section_measures(claims)
    chk("claims are not recount", mc["recount"] == 0 and not section_fails("V1 1-8", mc))
    flat = ["Paid a man in Lagos for a favour", "Then I tell him thanks and hang up"]   # past fact + present attitude
    chk("one flat past bar is not a chain", section_measures(flat)["chain"] <= 1)
    chk("hook par allows a single past bar", not section_fails("Hook 1-4", section_measures(["I bought the gnome",
                                                                                            "Might sell it on"])))
    chk("lcs counts in order", _lcs(list("abcde"), list("axcye")) == 3)
    print("recount selftest:", "PASSED" if ok else "FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="-")
    ap.add_argument("--slot", help="the section name when the input is one section without headers")
    ap.add_argument("--calibrate", help="the original's lines (outside the project); prints counts only")
    ap.add_argument("--negatives", action="store_true", help="assert the known recounts fail")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-overlap", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.calibrate:
        sys.exit(0 if calibrate(a.calibrate) else 1)
    if a.negatives:
        res = negatives_check()
        bad = [lab for lab, f in res if not f]
        for lab, f in res:
            print(f"  {'caught' if f else 'MISSED'}  {lab}: " + ("; ".join(f) if f else "passes the gate"))
        print("recount NEGATIVES:", "PASSED" if res and not bad else "FAILED")
        sys.exit(0 if res and not bad else 1)
    text = sys.stdin.read() if a.path == "-" else open(a.path, encoding="utf8").read()
    secs = [(a.slot, [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")])] \
        if a.slot else sections_of(text)
    print(f"recount {os.path.basename(a.path) if a.path != '-' else 'stdin'}:")
    fails, _rows, _song = run(secs, overlap=not a.no_overlap)
    for f in fails:
        print("  x " + f)
    print("RECOUNT:", "PASS" if not fails else f"{len(fails)} PROBLEMS")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
