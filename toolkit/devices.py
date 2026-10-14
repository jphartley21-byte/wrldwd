"""Identify the figures of speech the style runs on, deterministically and by name.

WHAT THIS ADDS
Plays on words were already measured (cashed idioms, homophone pairs across bars, the payoff word
in the rhyme slot, internal rhyme, alliteration - see craft_scan/coherence_gate). The FIGURES OF
SPEECH were not: nothing in the repo detected a simile, a metaphor, understatement, hyperbole or
anaphora, and the one place anaphora showed up at all was the meaning gate's filler-frame rule,
which scores it as a FAULT. For a deadpan British rap built on bathos - bland setup, deflating
closer - that is the wrong way round.

Detectors, all pattern-based so every hit can be explained and argued with:
  simile      like / as ... as frames, split into plain and cliche
  metaphor    copula + a VEHICLE noun (a van is a coffin), or subject and predicate in different
  candidate   lexical fields, using the theme-word groups as the fields
  bathos      a bland clause followed by a short deflating one landing on a mundane concrete noun;
              also the cross-bar case (long bland bar, then a short payoff bar)
  litotes     negation plus a downgrader (not the worst, hardly, a bit) - distinct from the hedge
  hedge       a modal or softener (might, sort of, probably, should be), which the original's own
              closers use instead of a claim
  hyperbole   absolute quantifiers (a million, never, everyone, forever)
  anaphora    the same opener repeated across bars, or inside one bar
  polysyndeton  and-chains

CALIBRATION
  python toolkit/devices.py --calibrate ORIGINAL_TXT   numbers only, never prints the lyrics
  python toolkit/devices.py --selftest                 fixtures plus the rejected stanzas
The original is deadpan: it is NOT expected to contain similes or metaphors, and claiming a
detector "passes" because it fires on the original would be false comfort. So the positive side is
a labelled fixture file (toolkit/tests/devices_positive.txt) and the negative side is the
Joe-rejected stanzas in toolkit/tests/, which must stay quiet on these six.

usage:
    python toolkit/devices.py FILE|-            per bar, the figures found
    python toolkit/devices.py --calibrate FILE  counts against the original (numbers only)
    python toolkit/devices.py --selftest
"""

import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import craft_scan as cs      # noqa: E402
import rhyme_tools as rt     # noqa: E402

THEME = os.path.join(HERE, "theme_words.txt")

# Nouns that make a comparison a METAPHOR rather than a description when predicated of something
# else: "the van is a coffin". Curated, because precision matters more than recall here.
VEHICLE = set("""coffin grave zoo madhouse circus jungle maze trap prison cell cage machine
factory furnace oven skip tip dump swamp bog minefield battlefield warzone shark wolf dog rat
snake shark leech sponge parrot robot puppet clown joker sponge magnet anchor millstone
lighthouse graveyard museum library filing cabinet carousel treadmill hamster wheel
sausage machine sausage factory""".split())

# Cliché similes: recognisable but worn, so a hit is a warning rather than a win.
CLICHE_SIMILE = set("""glove clockwork kite plague brick baby dream rock feather trooper mule
donkey log stone bear lion mouse lamb sardines""".split())

MUNDANE = set("""kettle bin bins sofa receipt van boot boots carpet chips tea cup mug form forms
ticket bag bags sausage sausages charger remote control milk loaf bread weather rain queue
driveway garage shed hose ladder paint wallpaper drain washing dishes sink toilet bog towel
sock socks pants jumper trainers plaster paracetamol biscuit biscuits crisps beans toast egg
pan pot tray box boxes envelope stamp stamps letter letters leaflet flyer menu bill invoice
coins change trolley bus stop platform timetable lighter biscuit""".split())

NEG_RE = re.compile(r"\b(not|n't|never|hardly|barely|scarcely|no)\b", re.I)
DOWNGRADE_RE = re.compile(
    r"\b(not\s+the\s+\w+est|not\s+bad|not\s+half|not\s+much|not\s+exactly|not\s+the\s+(biggest|"
    r"worst|best|end|start|sharpest|brightest)|hardly|barely|scarcely|only\s+just|a\s+bit|"
    r"a\s+touch|slightly|sort\s+of|kind\s+of|not\s+too\s+\w+)\b", re.I)
HEDGE_RE = re.compile(
    r"\b(might|may|maybe|perhaps|possibly|probably|should\s+be|ought\s+to|i\s+reckon|i\s+fancy|"
    r"apparently|seemingly|as\s+such|more\s+or\s+less)\b", re.I)
HYPERBOLE_RE = re.compile(
    r"\b(a\s+million|a\s+thousand|a\s+hundred\s+times|never|always|forever|endless|"
    r"never-ending|everyone|everybody|everything|nothing|no\s+one|tonnes?|loads|"
    r"a\s+tonne\s+of|bucket\s*loads|thousands)\b", re.I)
SIMILE_AS_RE = re.compile(r"\bas\s+\w+\s+as\b", re.I)
SIMILE_LIKE_RE = re.compile(r"\b(like|as|feels?\s+like|looks?\s+like|tastes?\s+like|went\s+like)\s+"
                            r"(a|an|the|his|her|your|my|their|some|it)\b", re.I)
# "like Amazon" -- a bare PROPER NOUN as the vehicle, no determiner, and the original lands a punchline on
# it. Measured 12 Oct: the determiner-only pattern missed that simile entirely, so one of the densest quads
# in the song scored no devices at all. A capitalised vehicle is required, so "like me/it/that" stays out.
SIMILE_PROPER_RE = re.compile(r"\b(like|as)\s+([A-Z][a-zA-Z]{2,})\b")
# "went like clockwork" has no determiner, and "like" is also a verb, so the bare form needs a
# verb cue in front of it or a word from the cliche list.
SIMILE_VERB_RE = re.compile(
    r"\b(?:went|goes|ran|runs|fought|fights|slept|sits|sat|stood|fell|falls|rose|shot|worked|"
    r"blazed|poured|chucked|chucked\s+it|sweat|swore|lay|lies)\s+(?:like|as)\s+([a-z][a-z'-]{2,})\b",
    re.I)
CLICHE_BARE_RE = re.compile(r"\b(?:like|as)\s+(" + "|".join(sorted(CLICHE_SIMILE)) + r")\b", re.I)
SIMILE_AS_NOT = re.compile(r"\bas\s+a\s+(rule|matter|whole|result|minimum|maximum)\b", re.I)
COPULA_RE = re.compile(r"\b(is|was|are|were|'s)\s+(a|an|the)\s+([a-z][a-z'-]*)", re.I)
AND_CHAIN_RE = re.compile(r"\band\b", re.I)
CLAUSE_SPLIT = re.compile(r"\s*(?:,|;|\band\b|\bthen\b|\bbut\b|\bso\b)\s*", re.I)


def _fields():
    """The lexical fields, from the theme-word sections. Missing file -> a minimal field map."""
    out = {}
    if os.path.exists(THEME):
        name = None
        with open(THEME, encoding="utf-8-sig") as fh:
            for raw in fh:
                line = raw.strip()
                if line.startswith("#"):
                    name = line.lstrip("# ").strip()
                elif line and name:
                    out.setdefault(name, set()).update(line.split())
    return out


FIELDS = _fields()


def field_of(word):
    w = word.lower().strip(".,!?")
    for name, ws in FIELDS.items():
        if w in ws:
            return name
    return None


def clauses(bar):
    return [c.strip() for c in CLAUSE_SPLIT.split(bar) if c.strip()]


def content_words(text):
    return [w for w in re.findall(r"[a-z][a-z'-]*", text.lower()) if w not in rt.FUNC]


def find_simile(bar):
    """Simile by name, marked CLICHE when the vehicle is a worn one (like clockwork)."""
    if SIMILE_AS_NOT.search(bar):
        return []
    cl = {m.group(1).lower() for m in CLICHE_BARE_RE.finditer(bar)}

    def kind(text):
        low = text.lower()
        return "simile-cliche" if any(w in low for w in cl) else "simile"

    out = []
    for m in SIMILE_AS_RE.finditer(bar):
        out.append((kind(m.group(0)), m.group(0), "as ... as"))
    for m in SIMILE_LIKE_RE.finditer(bar):
        out.append((kind(m.group(0)), m.group(0), "like/as a ..."))
    for m in SIMILE_PROPER_RE.finditer(bar):
        out.append((kind(m.group(0)), m.group(0), "like/as + name"))
    for m in SIMILE_VERB_RE.finditer(bar):
        out.append((kind(m.group(0)), m.group(0), f"{m.group(1)} is the vehicle"))
    for w in sorted(cl):
        if not any(w in t.lower() for _k, t, _x in out):
            out.append(("simile-cliche", "like " + w, "worn comparison"))
    return out


def find_metaphor(bar):
    """A vehicle noun predicated of something, or subject and predicate in different fields."""
    out = []
    for m in COPULA_RE.finditer(bar):
        pred = m.group(3).lower()
        if pred in VEHICLE:
            out.append(("metaphor", m.group(0), f"vehicle noun '{pred}'"))
            continue
        before = content_words(bar[:m.start()])
        if not before:
            continue
        subj = before[-1]
        f1, f2 = field_of(subj), field_of(pred)
        if f1 and f2 and f1 != f2:
            out.append(("metaphor", m.group(0), f"field switch {f1} -> {f2}"))
    return out


def find_litotes(bar):
    out = []
    m = DOWNGRADE_RE.search(bar)
    if m and NEG_RE.search(bar):
        out.append(("litotes", m.group(0), "negation + downgrader"))
    return out


def find_hedge(bar):
    out = []
    m = HEDGE_RE.search(bar)
    if m:
        out.append(("hedge", m.group(0), "modal / softener"))
    return out


def find_hyperbole(bar):
    out = []
    for m in HYPERBOLE_RE.finditer(bar):
        out.append(("hyperbole", m.group(0), "absolute quantifier"))
    return out


def find_bathos(bar):
    """A bland setup clause followed by a SHORT clause landing on something mundane."""
    out = []
    cl = clauses(bar)
    if len(cl) >= 2:
        last = cl[-1]
        if len(last.split()) <= 5 and any(w in MUNDANE for w in content_words(last)):
            if not NEG_RE.search(last) and not HEDGE_RE.search(last):
                setup = " ".join(cl[:-1])
                if len(setup.split()) >= 4:
                    out.append(("bathos", last, "bland setup -> deflating mundane closer"))
    return out


def find_anaphora(bars):
    """One bar repeating its own opener, or two or more bars opening on the same word.

    Anaphora repeats the first MEANINGFUL word, not the first word: "And it is all in the boot,
    and it is all on the slate" repeats "all", while "and" alone is just a conjunction.
    """
    out = []

    def opener(clause):
        """First two words after a leading conjunction - the repeated unit, not its stopwords."""
        words = re.findall(r"[a-z']+", clause.lower())
        while words and words[0] in {"and", "then", "so", "but", "well", "now", "cos", "cause"}:
            words.pop(0)
        unit = " ".join(words[:2]) if len(words) >= 2 else (words[0] if words else None)
        if not unit:
            return None
        if all(w in rt.FUNC for w in unit.split()):
            return None                    # "in the" repeated is prose, not anaphora
        return unit

    out = []
    for i, b in enumerate(bars):
        cl = clauses(b)
        if len(cl) >= 2:
            heads = [opener(c) for c in cl]
            heads = [h for h in heads if h]
            if len(heads) >= 2 and len(set(heads)) == 1:
                out.append((i, "anaphora", heads[0], "same opener inside one bar"))
    # Cross-bar anaphora needs THREE bars, not two: over a whole song, two bars sharing an opener
    # is a coincidence, while the original's own repeated frame is a real pattern.
    openers = {}
    for i, b in enumerate(bars):
        o = opener(b)
        if o:
            openers.setdefault(o, []).append(i)
    for word, idxs in openers.items():
        if len(idxs) >= 3:
            for i in idxs:
                out.append((i, "anaphora", word, f"{len(idxs)} bars open on '{word}'"))
    return out


def find_polysyndeton(bar):
    out = []
    cl = clauses(bar)
    ands = len(AND_CHAIN_RE.findall(bar))
    if ands >= 3 or (len(cl) >= 3 and ands >= 2):
        out.append(("polysyndeton", f"{ands} and", "and-chain"))
    return out


def inspect(bars):
    """Per-bar figures plus the block-level ones. Returns a list of dicts, one per bar."""
    ana = {}
    for i, kind, tok, why in find_anaphora(bars):
        ana.setdefault(i, []).append((kind, tok, why))
    rows = []
    for i, b in enumerate(bars):
        hits = (find_simile(b) + find_metaphor(b) + find_litotes(b) + find_hedge(b)
                + find_hyperbole(b) + find_bathos(b) + find_polysyndeton(b) + ana.get(i, []))
        rows.append({"bar": i + 1, "text": b, "devices": hits})
    return rows


def summarise(bars):
    counts = {}
    for r in inspect(bars):
        for kind, tok, why in r["devices"]:
            counts[kind] = counts.get(kind, 0) + 1
    return counts


def selftest():
    ok = True
    pos = os.path.join(HERE, "tests", "devices_positive.txt")
    if not os.path.exists(pos):
        print("  FAIL missing toolkit/tests/devices_positive.txt")
        return 1
    misfires, missed = [], []
    with open(pos, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            want, text = [p.strip() for p in line.split("|", 1)]
            got = [k for k, _t, _w in inspect([text])[0]["devices"]]
            if want == "hedge":
                if "hedge" not in got:
                    missed.append((want, text, got))
            elif want == "no-device":
                if got:
                    misfires.append((want, text, got))
            elif want not in got:
                missed.append((want, text, got))
    if missed:
        ok = False
        for want, text, got in missed[:6]:
            print(f"  FAIL {want} not found in {text!r} (got {got})")
    if misfires:
        ok = False
        for want, text, got in misfires[:6]:
            print(f"  FAIL fired on plain reportage {text!r} (got {got})")

    rejected = sorted(glob.glob(os.path.join(HERE, "tests", "rejected_*.txt")))
    noisy = 0
    for path in rejected:
        try:
            bars = [l.strip() for l in open(path, encoding="utf-8-sig")
                    if l.strip() and not l.startswith("#")]
        except Exception:
            continue
        if len(bars) > 1:
            bars = bars[1:]
        hits = sum(len(r["devices"]) for r in inspect(bars))
        noisy += hits
    print(f"  figures found across {len(rejected)} Joe-rejected stanzas: {noisy}")
    if noisy > max(2, len(rejected)):
        ok = False
        print("  FAIL the detectors fire too often on stanzas Joe rejected")

    # Block-level anaphora: three bars sharing an opener is a device, two is a coincidence.
    three = ["Same box in the boot", "Same box on the slate", "Same box up at the border"]
    two = ["Same box in the boot", "Same box on the slate", "Then it is all on the slate"]
    if not any(k == "anaphora" for k, _t, _w in inspect(three)[0]["devices"]):
        ok = False
        print("  FAIL three bars on the same opener is not called anaphora")
    if any(k == "anaphora" for k, _t, _w in inspect(two)[2]["devices"]):
        ok = False
        print("  FAIL two bars on the same opener is wrongly called anaphora")
    print("DEVICES SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def cmd_calibrate(path):
    """Counts only. The original's lyrics must never be printed."""
    lines = [l.strip() for l in open(path, encoding="utf-8-sig")
             if l.strip() and not l.strip().startswith("#")]
    counts = summarise(lines)
    print(f"figures in the original ({len(lines)} lines): numbers only")
    if not counts:
        print("  none of the six fire on the original at all")
    for kind, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {kind:<14} {n}")
    print("\nexpected: the original is deadpan, so simile/metaphor/bathos should be absent or rare;"
          "\nwhat it does use is the hedge and, per the map, the modal-understatement closer.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--calibrate")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.calibrate:
        return cmd_calibrate(a.calibrate)
    text = sys.stdin.read() if (not a.path or a.path == "-") else open(
        a.path, encoding="utf-8-sig").read()
    bars = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    for r in inspect(bars):
        if r["devices"]:
            names = ", ".join(f"{k}({t})" for k, t, _w in r["devices"])
            print(f"{r['bar']:>2}. {r['text'][:52]:<52} {names}")
        else:
            print(f"{r['bar']:>2}. {r['text'][:52]:<52} -")
    print("\ntotals:", summarise(bars))
    return 0


if __name__ == "__main__":
    sys.exit(main())
