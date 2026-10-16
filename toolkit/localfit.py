"""localfit: a local word must FIT the bar it is in (16 Oct 2026).

Joe: "The original uses words and phrases most UK people know and they fit the bar. The torch bar and servo pie bar have nothing to do
with Australia." The local-word gates (songcheck: the hook code-switches, the verses at a rate) counted ANY word from the supply, so the
writer met the count with an Australian greeting in a bar about a fixer and an Australian shop word in a bar about trains to Spain.

What the original does, measured on its own bars:
  - every place-tied greeting stands next to its place (a Caribbean greeting with Tobago, a Yoruba one with Lagos, "bonjour" with France);
    its one free-standing greeting is a general sign-off that is not tied to one country;
  - a place-tied local word sits in or next to a bar naming its country ("prego" after "Italian suede");
  - a loanword most UK people already know (ouzo) stands on its own;
  - UK slang needs no place at all.
The rule: a word in toolkit/local_words.txt tied to one country (not UK slang, not everyday UK English) must have that country, its
adjective or one of its places in the same bar or the bar either side, unless it is on UK_KNOWN and is not a greeting. A greeting always
needs its place. The original passes by construction of the lists below; Joe's two bars fail (toolkit/tests/local_flagged.txt).

UK_KNOWN and UK_HOME are hand lists (judgement, not measurement: word frequency cannot tell "known in the UK" apart; "wagwan" scores
lower than "servo"). Joe corrects them.

  python toolkit/localfit.py FILE        misplaced local words in a '== Slot' draft (across section breaks too)
  python toolkit/localfit.py --selftest  the original passes (needs the private file), Joe's rows fail, fixtures hold
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LOCAL = os.path.join(HERE, "local_words.txt")
FLAGGED = os.path.join(HERE, "tests", "local_flagged.txt")

# everyday UK English that the supply files under another country's slang: no place needed
UK_HOME = {"cheers", "tinnie", "barbie", "brekkie", "mozzie", "sickie", "chunder", "dunny", "mate"}
# loanwords most UK listeners know without a place beside them (never greetings: a greeting names a place)
UK_KNOWN = {"ouzo", "grazie", "gracias", "merci", "danke", "ciao", "adios", "amigo", "pronto", "vino", "cerveza", "sangria", "tapas",
            "fiesta", "siesta", "prego", "bier", "prost", "pho", "baht", "euro", "euros"}
ANCHORS = {
    "Australian English": "australia australian aussie aussies oz sydney melbourne perth brisbane cairns k'gari kgari whitsundays whitsunday "
                          "byron bondi queensland fraser magnetic darwin adelaide nimbin",
    "Spanish": "spain spanish madrid barcelona bilbao ibiza majorca mallorca magaluf malaga seville valencia tenerife mexico mexican",
    "Italian": "italy italian rome florence milan naples napoli venice pompeii sicily",
    "French": "france french paris bordeaux nantes nice lyon marseille calais saint-omer",
    "Slovene": "slovenia slovenian ljubljana bled",
    "Norwegian": "norway norwegian oslo bergen",
    "German": "germany german berlin munich vienna austria austrian frankfurt mainz hamburg forest",
    "Thai": "thailand thai bangkok koh pai phuket chiang",
    "Portuguese": "portugal portuguese porto lisbon brazil",
    "Greek": "greece greek crete athens corfu zante",
    "Vietnamese": "vietnam vietnamese hanoi saigon hoi nam",
    "Slovak": "slovakia slovak bratislava",
    "Dutch": "dutch holland netherlands amsterdam rotterdam hague",
    "Basque": "basque bilbao sebastian",
    "Irish": "ireland irish dublin donegal cork galway kerry letterkenny bundoran malin",
}
ANCHORS = {k: set(v.split()) for k, v in ANCHORS.items()}


def table():
    out = {}
    for ln in open(LOCAL, encoding="utf-8"):
        if ln.strip() and not ln.startswith("#"):
            p = [x.strip() for x in ln.split("|")]
            if len(p) >= 4:
                out[p[0].lower()] = {"lang": p[1], "places": p[2], "register": p[3]}
    return out


def _words(bar):
    return re.findall(r"[a-z][a-z'\-]*", bar.lower())


def anchors_for(lang, places=""):
    a = set(ANCHORS.get(lang, set()))
    a |= {w for w in _words(places) if len(w) > 3 and not w.isdigit()}
    return a


def misplaced(bars):
    """[(bar index 0-based, word, language, why)] for local words that do not fit where they stand."""
    T = table()
    out = []
    for i, b in enumerate(bars):
        for w in _words(b):
            e = T.get(w)
            if not e or e["lang"].lower() == "slang" or w in UK_HOME:
                continue
            if w in UK_KNOWN and e["register"] != "greeting":
                continue
            near = set()
            for j in (i - 1, i, i + 1):
                if 0 <= j < len(bars):
                    near |= set(_words(bars[j]))
            if not (near & anchors_for(e["lang"], e["places"])):
                why = "a greeting names its place" if e["register"] == "greeting" else "not a word most UK listeners know on its own"
                out.append((i, w, e["lang"], why))
    return out


def fitting(bars, loans=None):
    """the local words that fit (for the songcheck counts): in the supply and not misplaced."""
    bad = {(i, w) for i, w, _, _ in misplaced(bars)}
    T = table()
    return {w for i, b in enumerate(bars) for w in _words(b) if (w in T or (loans and w in loans)) and (i, w) not in bad}


def flagged():
    out = []
    if os.path.exists(FLAGGED):
        for ln in open(FLAGGED, encoding="utf-8"):
            if ln.strip() and not ln.startswith("#"):
                b, w, sec = [x.strip() for x in ln.split("|", 2)]
                out.append((int(b), w, [x.strip() for x in sec.split(" / ")]))
    return out


def selftest(orig_path=None):
    ok = True
    if orig_path is None:
        cand = glob.glob(os.path.expanduser("~/Documents/*/original_lines.txt"))
        orig_path = cand[0] if cand else None
    if orig_path:
        L = [ln.strip() for ln in open(orig_path, encoding="utf8") if ln.strip()][:76]
        m = misplaced(L)
        good = not m
        ok &= good
        print(("ok  " if good else "BAD ") + f"the original's local words all fit their bars ({len(m)} misplaced)" + ("" if good else f": bars {[i + 1 for i, *_ in m]}"))
    rows = flagged()
    miss = [(b, w) for b, w, sec in rows if not any(i + 1 == b and x == w for i, x, *_ in misplaced(sec))]
    good = bool(rows) and not miss
    ok &= good
    print(("ok  " if good else "BAD ") + f"Joe's misplaced local words are caught: {len(rows) - len(miss)} of {len(rows)}" + (f"; missed {miss}" if miss else ""))
    fx = [(["Hoi hoi to the Dutch, they're honest"], []), (["Grazie grazie train drivers! A month and no drama"], []),
          (["G'day from the boys in Perth"], []), (["Up K'gari in the ute where you do or die"], []), (["Cheers! Any issue?"], []),
          (["Got a servo pie for a quid"], ["servo"]), (["Bonjour to the lads"], ["bonjour"]),
          (["We landed in Lyon", "Bonjour to the lads"], [])]
    bad = [(b, want) for b, want in fx if sorted(w for _, w, _, _ in misplaced(b)) != sorted(want)]
    good = not bad
    ok &= good
    print(("ok  " if good else "BAD ") + f"local-word fixtures: {len(fx) - len(bad)} of {len(fx)}" + (f"; wrong {bad}" if bad else ""))
    print("localfit selftest:", "PASSED" if ok else "FAILED")
    return ok


def main():
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        return 0 if selftest(a[1] if len(a) > 1 else None) else 1
    bars = [ln.strip() for ln in open(a[0], encoding="utf-8") if ln.strip() and not ln.startswith(("#", "=="))]
    m = misplaced(bars)
    for i, w, lang, why in m:
        print(f"  x bar {i + 1}: '{w}' ({lang}) has no {lang.replace(' English', '')} place in it or beside it ({why}) | {bars[i]}")
    print(f"LOCALFIT: {'PASS' if not m else f'{len(m)} misplaced'}")
    return 1 if m else 0


if __name__ == "__main__":
    sys.exit(main())
