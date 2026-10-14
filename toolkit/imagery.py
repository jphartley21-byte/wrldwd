"""imagery: does the IMAGE develop across the bars, and does it land on the rhyme?

Joe, 12 Oct 2026, on one of the original's quads. Asked what the system picks up, the honest answer was:
nothing follows an image. Every instrument we had was phonetic (vowels, frames) or lexical-class (is this
word a place, is it administrative). So a couplet that sparks a light in one bar and names the bulb in the
rhyme of the next registered as nothing at all, and the same for a murder told entirely in courier
vocabulary. This module measures exactly that.

  A CHAIN exists when two or more words from one image field appear across two or more bars.
  A CHAIN LANDS when one of those words is in the rhyme slot (the last two words of a bar), because that is
  where the original puts the payoff.
  A BRIDGE is a word that belongs to two fields at once. That is not a bug in the data, it is the device:
  one of the original's best bars uses a single verb that means packing a box AND putting a man in one.

  python toolkit/imagery.py -                    (stdin: bars)
  python toolkit/imagery.py --selftest
  python toolkit/imagery.py --rate PATH          (how often the original does it)
  python toolkit/imagery.py --check-original PATH (the real blocks, counts and words only)

Fields come from toolkit/theme_words.txt plus the sensory fields added here. Lyrics never enter the project:
check modes print counts, bar numbers and single words.
"""
import os, re, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# The fields theme_words.txt does not have. The original's chain in that quad runs through LIGHT (one verb
# meaning to spark, then the lights, then the bulb) and through PARCEL (packing, packaging, shipping), and
# its punch lands on the courier comparison. Both fields have to exist for the chain to be visible at all.
#
# DRINK was extended 12 Oct 2026 with the storage half of the image (cellar, barrel, cask, keg) plus the
# verbs of consumption. It listed only what is in the glass (beer, port, vinho, bottle), so a chain running
# beer -> barrel -> cellars was invisible, and that is the chain the Porto material actually offers. Same
# reason as PARCEL carrying depot/warehouse/loads: a chain is the whole picture, not the object.
SENSORY = {
    "light": "spark sparks sparked sparking light lights bulb bulbs halogen lamp lamps flash shine glow "
             "flicker wire fuse current switch torch beam blackout dim dark darkness shut-eye",
    "parcel": "box boxed boxes package packaged packaging parcel parcels ship shipped shipping post postal "
              "courier delivery deliver freight crate crates load loads van depot warehouse label labels "
              "address stamp stamps send sent cargo haul docket manifest sack tape taped wrap wrapped seal",
    "violence": "spark sparked slap slapped tap tapped bang crack bat chain chib shank swing smack punch "
                "lamped tooled drop dropped laid dumped boxed gripped grab grabbed collar",
    "drink": "beer lager pint pints port wine vinho cerveja birra ouzo glass bottle bottles bar pub round "
             "rounds toast cheers skal yamas drank drink drinking drunk sober hangover cellar cellars barrel "
             "barrels cask casks keg kegs brewery vineyard tavern",
    "money": "cash quid dosh dough guap pavos notes coin coins price prices rate rates pay paid tally totals "
             "ledger invoice slate credit debt owed favour favours owe",
    "police": "plod police cops copper federale guardia politi gendarme flics warrant cuffs bribe fine "
              "fifty nick grass plainclothes search stop caution",
    "sleep": "bed beds bunk bunks dorm hostels hostel pillow sheet sheets duvet kip sleep slept nap",
    "trade": "shop counter till receipt order orders stock supply customer buyers fare fares slate",
    "weather": "rain drizzle sleet fog mist cloud clouds grey storm wind sun heat snow frost hail",
    "sea": "sea tide coast beach shingle surf harbour port ferry boat boats deck wave cliff cove sand",
}


def _stem(w):
    """Crude but honest: a token matches a field word if it equals it, drops a plural, or drops -ed/-ing.
    The first version stripped "es", which turned "fares" into "far" and made the word "far" a trade term --
    a false positive caught by running it on our own bars."""
    return w


def _candidates(w):
    out = {w}
    if len(w) >= 4 and w.endswith("s"):
        out.add(w[:-1])
    if len(w) >= 5 and w.endswith("ed"):
        out.update({w[:-2], w[:-1]})
    if len(w) >= 6 and w.endswith("ing"):
        out.update({w[:-3], w[:-3] + "e"})
    return out


NOT_IMAGE = {"places", "verbs-and-states"}   # a gazetteer and a grammar list are not images


def load_fields():
    fields = {}
    path = os.path.join(HERE, "theme_words.txt")
    if os.path.exists(path):
        cur = None
        for line in open(path, encoding="utf8"):
            line = line.strip()
            if line.startswith("#"):
                cur = line[1:].strip().replace(" ", "-")
                fields.setdefault(cur, set())
            elif line and cur:
                fields[cur].update(line.split())
    for name, words in SENSORY.items():
        fields.setdefault(name, set()).update(words.split())
    idx = {}
    for name, words in fields.items():
        if name in NOT_IMAGE:
            continue
        for w in words:
            idx.setdefault(w.lower(), set()).add(name)
            for c in _candidates(w.lower()):
                idx.setdefault(c, set()).add(name)
    return fields, idx


FIELDS, IDX = load_fields()


def toks(bar):
    return re.findall(r"[A-Za-z']+", bar.lower())


def hits(bars):
    """field -> [(bar, word, position_from_end)] for every word belonging to that field."""
    out = {}
    for i, b in enumerate(bars):
        w = toks(b)
        for j, word in enumerate(w):
            for f in IDX.get(word, ()):
                out.setdefault(f, []).append((i + 1, word, len(w) - j))
    return out


def chains(bars, land_within=2):
    """Chains that DEVELOP (2+ words, 2+ bars). Returns (field, occ, (first,last), lands)."""
    out = []
    for f, occ in hits(bars).items():
        if len({w for _, w, _ in occ}) < 2:
            continue
        bars_hit = sorted({b for b, _, _ in occ})
        if len(bars_hit) < 2 and len(bars) > 2:
            continue
        lands = [(b, w) for b, w, pos in occ if pos <= land_within]
        out.append((f, occ, (bars_hit[0], bars_hit[-1]), lands))
    return out


def bridges(bars):
    """Words that belong to two or more fields at once: the pivot of a metaphor, not an error."""
    out = {}
    for b in bars:
        for w in toks(b):
            fs = IDX.get(w) or set()
            if len(fs) > 1:
                out.setdefault(w, set()).update(fs)
    return out


def report(bars, label):
    print(f"== {label} ({len(bars)} bars)")
    ch = chains(bars)
    for f, occ, span, lands in ch:
        words = [(b, w) for b, w, _ in occ]
        tag = "LANDS ON THE RHYME" if lands else "does not reach the rhyme"
        print(f"  CHAIN {f}: {words} bars {span[0]}-{span[1]} -- {tag}")
    for w, fs in bridges(bars).items():
        print(f"  BRIDGE '{w}' belongs to {sorted(fs)}")
    no_land = [f for f, _, _, lands in ch if not lands]
    print(f"  -> chains {len(ch)} ({len(ch) - len(no_land)} landing on the rhyme), "
          f"bridges {len(bridges(bars))}")
    return ch


def selftest():
    ok = True
    chain = ["Boxed it up and taped it flat", "Stuck a label on the crate",
             "Sent it off next day, no slack", "Signed for by the courier"]
    ch = report(chain, "synthetic parcel chain that lands on the rhyme")
    lands = [c for c in ch if c[0] == "parcel" and c[3]]
    print("   parcel chain lands:", bool(lands))
    ok &= bool(lands)
    flat = ["Just numbers and dates in folders", "Might take the long way to Oslo"]
    ch2 = report(flat, "our flat bars (no chain should land)")
    ok &= not [c for c in ch2 if c[3]]
    bridge = ["Boxed him up nice and packaged him", "Shipped a man next day, no doubt"]
    br = bridges(bridge)
    print(f"   bridge words: { {k: sorted(v) for k, v in br.items()} }")
    ok &= any("box" in k for k in br)
    print("\nIMAGERY SELFTEST:", "PASSED" if ok else "FAILED")
    return ok


def rate(path, window=4):
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
    nq = land = anyc = 0
    for s in range(0, len(lines) - window + 1, window):
        q = lines[s:s + window]
        nq += 1
        ch = chains(q)
        anyc += bool(ch)
        land += bool([c for c in ch if c[3]])
    print(f"the original: {nq} quads | any chain {anyc} | chain landing on the rhyme {land}")
    print("  (words and fields only; no lyric text)")


def check_original(path, marker="halogen"):
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
    i = next((k for k, b in enumerate(lines) if marker in b.lower()), None)
    blocks = []
    if i is not None:
        blocks.append(("the quad", lines[i - 1:i + 3]))
    for name, bars in blocks:
        report(bars, name)


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    if "--rate" in sys.argv:
        rate(sys.argv[sys.argv.index("--rate") + 1])
        return
    if "--check-original" in sys.argv:
        check_original(sys.argv[sys.argv.index("--check-original") + 1])
        return
    src = sys.argv[-1]
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf8").read()
    report([l.strip() for l in text.splitlines() if l.strip()], "stdin")


if __name__ == "__main__":
    main()
