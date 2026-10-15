"""swagger: does the song BOAST like a rap song, or shrug like a diary? (15 Oct 2026)

Why it exists. Joe on the claim-first rebuild: "This still reads like a diary not a rap song. The premises ... should be like actual
rap song premises." toolkit/recount.py had stopped the past-tense chains, but it reads tense, not swagger: a present-tense bar that
deflates ("I'm home by ten and I rate it all right") passes it. The three premise hooks of 14 Oct were self-deprecating character
sketches, against Joe's own rule in brief/song_bible.md ("swagger first; the boast leads; mundane comedowns about one bar in eight").

What the original does, measured (counts only, `--calibrate`):
  HOOK   stamps: 9 of its 16 hook bars carry a greeting, a local word or a named place -- the roll-call flex of a man who is everywhere.
  VERSE  menace: 25 of its 60 verse bars (0.42) carry the character's swagger -- an illicit or menacing field (police, violence,
         smuggling and logistics, parcels and hauls), vice (drugs, women, hustles, bribes), a line aimed at "you", a warning, or a
         first-person status claim with a superlative (only, every, nobody, boss, worldwide).
Our drafts, same measure: v5 hook 7/16 and verses 0.17, v6 verses 0.22; the 14 Oct premise hooks 3-4 of 16 stamps.

THE GATE (song level; a section-level share would fail the original, whose V1 25-32 holds 0 of 8 -- its wordplay block):
  hook stamps   >= the original's 9/16 - HOOK_MARGIN
  verse menace  >= the original's 0.42 - VERSE_MARGIN
The lexicon is a proxy. It cannot tell a good boast from a bad one; it only says whether the song is boasting at all.

  python toolkit/swagger.py DRAFT.md               a '== Slot' draft
  python toolkit/swagger.py --calibrate PATH       counts only, asserts the original passes its own par
  python toolkit/swagger.py --negatives            the drafts Joe rejected as diaries must fail
  python toolkit/swagger.py --selftest
"""
import argparse
import functools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# measured with --calibrate (15 Oct 2026), counts only
ORIGINAL_HOOK_STAMPS = 9 / 16
ORIGINAL_VERSE_MENACE = 25 / 60
HOOK_MARGIN = 0.15        # v5's hook (7/16 = 0.44) sits inside it; the 14 Oct premise hooks (0.19-0.25) do not
VERSE_MARGIN = 0.10       # v6 (0.22) and v5 (0.17) sit well below 0.32

ILLICIT_FIELDS = {"violence", "police", "crime-and-logistics", "parcel"}   # toolkit/imagery.py fields
VICE = set("""weed coke gear stash score scored high pills pill shrooms truffles spliff joint skunk powder dealer dealers plug connect
birds bird girls ladies honeys smuggle smuggled smuggling launder laundered hustle hustled hustler hustlers bribe bribed bribes
wanted warrant fugitive outlaw heist loot racket rackets firm crew gang mob boss kingpin empire turf manor""".split())
SUPER = set("""every only nobody no-one best biggest top number first finest most legend legendary worldwide international
famous boss king empire notorious""".split())
FIRST = re.compile(r"\b(i|i'm|i've|i'll|i'd|my|me|mine|we|we're|our|us)\b", re.I)
ADDR = re.compile(r"\b(you|your|you're|ya|yours)\b", re.I)
WARN = re.compile(r"\b(don't|dont|or else|try me|watch it|mind how|careful|back off|step back)\b", re.I)


@functools.lru_cache(maxsize=1)
def _supply():
    import regression as rg
    return rg.load_supply()


def _toks(bar):
    return re.findall(r"[a-z']+", bar.lower())


def stamp(bar):
    """a greeting, a local word or a named place (the roll-call flex)."""
    import regression as rg
    places, loans = _supply()
    w = _toks(bar)
    if any(x in rg.GREET or x in loans for x in w):
        return True
    if rg.is_place(bar, places):
        return True
    return any(t[:1].isupper() and t.lower() in places for t in re.findall(r"[A-Za-z]+", bar)[1:])


def menace(bar):
    """the character's swagger: an illicit field, vice, a line aimed at 'you', a warning, or a first-person superlative claim."""
    import imagery
    import recount
    w = _toks(bar)
    if any(f in ILLICIT_FIELDS for x in w for f in imagery.IDX.get(x, ())) or any(x in VICE for x in w):
        return True
    if ADDR.search(bar) or WARN.search(bar):
        return True
    return bool(FIRST.search(bar)) and recount.bar_features(bar)["stance"] and any(x in SUPER for x in w)


def measure(sections):
    hook = [b for s, bs in sections if s and s.lower().startswith("hook") for b in bs]
    verse = [b for s, bs in sections if s and not s.lower().startswith("hook") for b in bs]
    per = {s: (sum(map(stamp, bs)) if s.lower().startswith("hook") else sum(map(menace, bs)), len(bs)) for s, bs in sections if s}
    return {"hook_stamps": (sum(map(stamp, hook)), len(hook)), "verse_menace": (sum(map(menace, verse)), len(verse)), "per": per}


def fails_of(m):
    out = []
    hs, hn = m["hook_stamps"]
    if hn and hs / hn < ORIGINAL_HOOK_STAMPS - HOOK_MARGIN - 1e-9:
        out.append(f"HOOK: {hs} of {hn} bars carry a stamp (greeting, local word or place); the original {ORIGINAL_HOOK_STAMPS:.0%} "
                   f"- {HOOK_MARGIN:.0%} margin. The hook is not flexing where he has been.")
    vs, vn = m["verse_menace"]
    if vn and vs / vn < ORIGINAL_VERSE_MENACE - VERSE_MARGIN - 1e-9:
        out.append(f"VERSES: {vs} of {vn} bars carry swagger (menace, vice, 'you', a warning or a superlative claim; "
                   f"{vs / vn:.0%}); the original {ORIGINAL_VERSE_MENACE:.0%} - {VERSE_MARGIN:.0%} margin. A diary, not a boast.")
    return out


def report(m, label):
    hs, hn = m["hook_stamps"]
    vs, vn = m["verse_menace"]
    print(f"swagger {label}: hook stamps {hs}/{hn}" + (f" ({hs / hn:.0%})" if hn else "") +
          f" | verse swagger {vs}/{vn}" + (f" ({vs / vn:.0%})" if vn else ""))
    print("  per section: " + "  ".join(f"{s} {a}/{n}" for s, (a, n) in m["per"].items()))


def calibrate(path):
    import recount
    m = measure(recount.original_sections(path))
    report(m, "ORIGINAL (counts only)")
    hs, hn = m["hook_stamps"]
    vs, vn = m["verse_menace"]
    drift = abs(hs / hn - ORIGINAL_HOOK_STAMPS) > 0.005 or abs(vs / vn - ORIGINAL_VERSE_MENACE) > 0.005
    if drift:
        print(f"  ! constants are stale: measured hook {hs}/{hn}, verse {vs}/{vn}")
    f = fails_of(m)
    for x in f:
        print("  ! " + x)
    ok = not f and not drift
    print("swagger CALIBRATION:", "PASSED (the original clears its own par)" if ok else "FAILED")
    return ok


NEGATIVES = [  # Joe's verdicts: "reads like a diary" (v5, v6) and "the premises don't sound like rap songs" (the 14 Oct hooks)
    "writing/detection_test/travel_draft_v5.md", "writing/detection_test/travel_draft_v6_moves.md",
    "writing/premises/hook_shoestring.md", "writing/premises/hook_missed_it.md", "writing/premises/hook_errand.md",
]


def negatives_check():
    import recount
    out = []
    for rel in NEGATIVES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            out.append((rel, fails_of(measure(recount.sections_of(open(p, encoding="utf8").read())))))
    return out


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print("  FAIL", name)

    chk("a bribe is menace", menace("Paid the copper a bribe and kept the change"))
    chk("a line at 'you' is swagger", menace("Ask about me, you know the name"))
    chk("a superlative claim is swagger", menace("I'm the only boss with a rail pass"))
    chk("a shrug is not", not menace("I'm home by ten and I rate it all right"))
    chk("a greeting is a stamp", stamp("Hola, the lads are in Madrid"))
    chk("a plain bar is not a stamp", not stamp("The tent was wet and so was I"))
    diary = [("V1 1-8", ["We left the hostel at nine", "The rain came down all day", "I lost the key again", "The shop was shut"])]
    chk("a diary verse fails", any("VERSES" in f for f in fails_of(measure(diary))))
    print("swagger selftest:", "PASSED" if ok else "FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--calibrate")
    ap.add_argument("--negatives", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.calibrate:
        sys.exit(0 if calibrate(a.calibrate) else 1)
    if a.negatives:
        res = negatives_check()
        missed = [r for r, f in res if not f]
        for r, f in res:
            print(f"  {'caught' if f else 'MISSED'}  {r}: " + ("; ".join(x.split(';')[0] for x in f) if f else "passes"))
        print("swagger NEGATIVES:", "PASSED" if res and not missed else "FAILED")
        sys.exit(0 if res and not missed else 1)
    import recount
    m = measure(recount.sections_of(open(a.path, encoding="utf8").read()))
    report(m, os.path.basename(a.path))
    f = fails_of(m)
    for x in f:
        print("  x " + x)
    print("SWAGGER:", "PASS" if not f else f"{len(f)} PROBLEMS")
    sys.exit(0 if not f else 1)


if __name__ == "__main__":
    main()
