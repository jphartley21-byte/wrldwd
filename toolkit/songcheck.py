"""songcheck: the level-allocated gates, for one section or the whole song.

Levels and allocation are specified in benchmark/gate_architecture.md, and every threshold comes from the
original's own 76 bars. THE VALIDATION IS THE POINT: the tool is run against those 76 bars, and any gate
the benchmark itself fails is a WRONG GATE and gets moved to the level where it holds or demoted to a
count. Four gates were corrected this way on 12 Oct 2026:

  * local words were demanded per 4-bar block, but the original clusters them (3 / 0 / 6) -> hook level
  * "no admin word in a rhyme slot" flagged the original's own cashed tally gag -> allowed when cashed
  * a place count and a "one long bar" test were demanded per section, but the original fails both in
    three sections -> both belong to the verse/song level, not the section
  * the required rhyme pairs came from the by-ear scheme alone, and the original's own reading cannot
    confirm 19 of those pairs -> a pair is demanded only when BOTH the by-ear scheme and the original's
    own measured keys agree; the rest are printed as grader limits, never as failures

  python toolkit/songcheck.py --original PATH_TO_ORIGINAL_LINES [--title "..."]     (validation)
  python toolkit/songcheck.py writing/full_draft_vN.md --title "Walk In Each"       (our draft)
  python toolkit/songcheck.py --slot "Hook 9-16" -                                  (one block, stdin)

Draft format: "== Slot" headers then that slot's bars. Prints counts and bar numbers, never the original's
lines.
"""
import os, re, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flow_fit as ff                # noqa: E402
import match as mt                   # noqa: E402
import regression as rg              # noqa: E402

ORIG_SEC = [("Hook 1-4", 0, 4), ("Hook 5-8", 4, 8), ("Hook 9-16", 8, 16), ("V1 1-8", 16, 24),
            ("V1 9-16", 24, 32), ("V1 17-24", 32, 40), ("V1 25-32", 40, 48), ("V1 33-44", 48, 60),
            ("V2 1-8", 60, 68), ("V2 9-16", 68, 76)]
BAND = {"hook": (5, 12), "verse": (5, 15)}   # measured: hook mean 8.2 max 12, verse mean 9.4 max 15
REPEAT_MAX = {"hook": 3, "verse": 4}         # measured: worst repeat 3 in a hook, 4 in a verse
MIN_PLACES_SONG = 8                          # measured with the CORRECTED counter: 11 (the first count of
#                                              18 was inflated by a bug -- it accepted any capitalised word)
MIN_TTR_SONG = 0.70                          # measured: 0.76
ADMIN_PER_16 = 1                             # measured: 1 use in 76 bars, and it is cashed
MIN_HOOK_PLACES = 4                          # measured: 7 of 16 hook bars
LONG_BAR = 12                                # measured: every verse has one bar >= 12

PROFILE = os.path.join(HERE, "..", "benchmark", "original_profile.json")


def level_of(slot):
    return "hook" if slot.lower().startswith("hook") else "verse"


def verse_of(slot):
    return slot.split()[0] if slot and slot[0].upper() == "V" else "HOOK"


def bars_of(text):
    """('== Slot' headers + bars) -> [(slot, [bars])]"""
    out, cur = [], None
    for line in text.lstrip("\ufeff").splitlines():   # a BOM on line 1 would otherwise read as a bar

        s = line.strip()
        if not s or s.startswith(("|", "#", "`")):
            continue
        if s.startswith("== "):
            cur = (s[3:].strip(), [])
            out.append(cur)
        elif cur is None:
            out.append((None, [s]))
        else:
            cur[1].append(s)
    return out


def cashed(bar, word):
    """A deliberate use of an administrative word: another word in the bar shares a stem with it. The
    original does exactly this once in 76 bars ("tally" against the word being tallied), and it is the only
    admin word in the song. A prefix test is not enough -- those two share "tal", not "tot"."""
    for w in rg.words(bar):
        if w == word or len(w) < 3:
            continue
        if any(w[k:k + 3] in word for k in range(len(w) - 2)):
            return True
    return False


def line_gates(slot, bars, fails):
    lvl = level_of(slot)
    lo, hi = BAND[lvl]
    for i, b in enumerate(bars):
        n = len(ff.sylls(b))
        if not (lo <= n <= hi):
            fails.append(f"{slot} bar {i + 1}: {n} syllables, outside the {lvl} band {lo}-{hi}")
    cnt = {}
    for b in bars:
        for w in rg.words(b):
            if w not in rg.STOP:
                cnt[w] = cnt.get(w, 0) + 1
    if cnt:
        w, c = max(cnt.items(), key=lambda kv: kv[1])
        if c > REPEAT_MAX[lvl]:
            fails.append(f"{slot}: '{w}' used {c}x (ceiling for a {lvl} is {REPEAT_MAX[lvl]})")
    for i, b in enumerate(bars):
        ws = rg.words(b)
        if ws and ws[-1] in rg.ADMIN and not cashed(b, ws[-1]):
            fails.append(f"{slot} bar {i + 1}: uncashed administrative word '{ws[-1]}' in the rhyme slot")


def scheme_gate(slot, bars, fails, notes):
    """Demand a pair only when the by-ear scheme AND the original's own measured keys both say it rhymes."""
    ms = mt.MANUAL_SCHEME.get(slot, "")
    if not ms or len(ms) != len(bars):
        return
    try:
        import json
        orig_keys = json.load(open(PROFILE, encoding="utf8"))[slot]["keys"]
    except Exception:
        orig_keys = None
    _, our_keys = mt.scheme(bars)
    for i in range(len(bars)):
        for j in range(i + 1, len(bars)):
            if ms[i] != ms[j]:
                continue
            if orig_keys and not mt.rhymes(orig_keys[i], orig_keys[j]):
                notes.append(f"{slot}: {ms[i]} pair {i + 1}-{j + 1} claimed by the by-ear scheme but "
                             f"unconfirmed by the original's own keys (grader limit, not a failure)")
                continue
            sc = mt.best_end(bars[i], bars[j])
            if not mt.rhymes(our_keys[i], our_keys[j]):
                if sc < 0.78:
                    fails.append(f"{slot}: {ms[i]} pair {i + 1}-{j + 1} scores {sc:.2f}")
            elif sc < 0.78:
                # the original's own keys rhyme here, so the pair is required; the SCORED grader just reads
                # it as weak (two graders, one metric). Required pair satisfied, weakness noted.
                notes.append(f"{slot}: {ms[i]} pair {i + 1}-{j + 1} key-rhymes but scores {sc:.2f}")


def song_gates(sections, title, fails, notes):
    bars = [b for _, bs in sections for b in bs]
    hooks = [b for s, bs in sections if level_of(s) == "hook" for b in bs]
    reprises = [s for s, _ in sections if "reprise" in (s or "").lower()]
    if reprises and hooks:
        first = [b for s, bs in sections if level_of(s) == "hook" and "reprise" not in (s or "").lower()
                 for b in bs]
        for rs, rbs in sections:
            if "reprise" in (rs or "").lower():
                n = min(len(first), len(rbs))
                diff = sum(1 for a, b in zip(first, rbs) if a != b)
                if diff:
                    fails.append(f"SONG: the chorus does not return unchanged ({diff} of {n} bars differ)")
    seen = {}
    for i, b in enumerate(bars):
        seen.setdefault(re.sub(r"[^a-z ]", "", b.lower()).strip(), []).append(i + 1)
    for b, idx in seen.items():
        if len(idx) > 1 and b not in {re.sub(r"[^a-z ]", "", h.lower()).strip() for h in hooks}:
            fails.append(f"SONG: line reused outside the chorus (bars {idx})")
    places, loans = rg.load_supply()
    pl = {p for b in bars if (p := rg.is_place(b, places))}
    if len(pl) < MIN_PLACES_SONG:
        fails.append(f"SONG: {len(pl)} named places, need >= {MIN_PLACES_SONG}")
    if hooks:
        hp = [i + 1 for i, b in enumerate(hooks) if rg.is_place(b, places)]
        if len(hp) < MIN_HOOK_PLACES:
            fails.append(f"SONG: the hook names a place in {len(hp)} of {len(hooks)} bars, need >= {MIN_HOOK_PLACES}")
        loc = {w for b in hooks for w in rg.words(b) if w in loans or w in rg.GREET}
        if len(loc) < (len(hooks) + 3) // 4:
            fails.append(f"SONG: the hook has {len(loc)} local/foreign words; it is the level that code-switches most")
    # Verses code-switch too, at a lower rate: measured, five local words across the original's 60 verse bars,
    # and one whole verse has none -- so this is a SONG-level rate, not a per-verse one.
    verses = [b for s, bs in sections if level_of(s) == "verse" for b in bs]
    if verses:
        vloc = {w for b in verses for w in rg.words(b) if w in loans}
        need = max(1, len(verses) // 12)
        if len(vloc) < need:
            fails.append(f"SONG: {len(vloc)} local words across {len(verses)} verse bars, need >= {need}")
        else:
            notes.append(f"SONG: verse local words {sorted(vloc)} ({len(vloc)} in {len(verses)} bars)")
    cw = [w for b in bars for w in rg.words(b) if w not in rg.STOP]
    ttr = len(set(cw)) / max(1, len(cw))
    if ttr < MIN_TTR_SONG:
        fails.append(f"SONG: lexical variety {ttr:.2f}, need >= {MIN_TTR_SONG}")
    admin = [w for b in bars for w in rg.words(b) if w in rg.ADMIN and not cashed(b, w)]
    if len(admin) > ADMIN_PER_16 * max(1, len(bars) // 16):
        fails.append(f"SONG: {len(admin)} uncashed administrative words ({sorted(set(admin))})")
    if title:
        t = re.sub(r"[^a-z ]", "", title.lower())
        hits = [i + 1 for i, b in enumerate(bars) if t in re.sub(r"[^a-z ]", "", b.lower())]
        if len(hits) != 1:
            fails.append(f"SONG: the title appears {len(hits)} times, expected exactly once (bars {hits})")
        elif hooks and hits[0] <= len(hooks):
            fails.append("SONG: the title is inside the hook; the original lands it in a verse")
    if notes:
        pass


def imagery_gates(sections, fails, notes):
    """QUAD level, the image: does the picture DEVELOP across the bars, and does it LAND on the rhyme?

    HONEST STATUS (12 Oct): a diagnostic, not a gate. Measured, the original carries an image chain in 5 of
    its 19 quads and one that lands on the rhyme in 3; Joe's own approved bars carry NONE, because they are
    sound-led (sound-alike puns) rather than image-led. So a chain requirement would fail the benchmark.
    What it is good for is telling the two kinds of bar apart while writing, and giving a target: roughly one
    landing chain per six quads, as the original does."""
    import imagery
    total = landed = 0
    for s, bs in sections:
        for i in range(0, len(bs), 4):
            quad = bs[i:i + 4]
            if len(quad) < 2:
                continue
            ch = imagery.chains(quad)
            total += bool(ch)
            landing = [c for c in ch if c[3]]
            if landing:
                landed += 1
                notes.append(f"{s} bars {i + 1}-{i + len(quad)}: image chain lands on the rhyme "
                             f"({', '.join(c[0] for c in landing)})")
    notes.append(f"SONG: image chains in {total} quads, landing on the rhyme in {landed} "
                 f"(the original: 5 and 3 of 19)")


def device_gates(sections, fails, notes):
    """QUAD level, the sound devices: a DRUM (one syllable frame with the vowels moving, which can cross a
    bar line) or an ECHO (one word-level frame, one vowel, different words).

    HONEST STATUS (12 Oct, after Joe corrected the drum's unit from word to syllable): this is a DIAGNOSTIC,
    not a veto. Measured with the corrected unit, the original carries a device in 10 of its 19 quads (53%)
    and a crutch in 3, so no threshold on it can separate the benchmark from our weak blocks -- our own 5-8
    block passes it, because the Porto/port pun is a genuine echo. The gate below is only a floor that
    catches a section with NO device at all; the per-quad notes are the actionable part, and they are what
    showed that our 5-8 has no drum while our 9-16 leans on a repeated word."""
    import ear
    dev = []
    for s, bs in sections:
        for i in range(0, len(bs), 4):
            quad = bs[i:i + 4]
            if len(quad) < 2:
                continue
            n = len(ear.drums(quad)) + len(ear.echoes(quad))
            dev.append(bool(n))
            if not n:
                notes.append(f"{s} bars {i + 1}-{i + len(quad)}: no drum and no echo in this quad")
    if dev:
        rate = sum(dev) / len(dev)
        if rate < 0.40:
            fails.append(f"SONG: {sum(dev)} of {len(dev)} quads carry a sound device ({rate:.0%}); "
                         f"the original carries one in 10 of its 19 (53%)")
        notes.append(f"SONG: sound devices in {sum(dev)} of {len(dev)} quads ({rate:.0%})")


def verse_gate(sections, fails, notes):
    """Verse level: one long bar, and code-switching at a verse rate. Places are NOT gated here: measured,
    the original's V2 names a place in only 1 of its 16 bars, so a per-verse place gate would fail the
    benchmark. Places are gated at HOOK and SONG level and counted per verse.

    Verse code-switching IS gated, and this corrects a claim of mine from earlier the same day. I had
    concluded that code-switching was hook-only because the count showed 0 local words in the verses. The
    count was wrong: the supply was missing the words. Counted by hand against a known-words list, the
    original's 60 verse bars carry five local words -- a shop word, a drink, police slang, money slang, and
    a slang plural. The supply now includes them (local_words.txt, built by REGISTER: shop, bill, cheers,
    police, money) so the engine can supply them and the gate can demand them."""
    groups = {}
    for s, bs in sections:
        groups.setdefault(verse_of(s), []).extend(bs)
    places, loans = rg.load_supply()
    for vslot, bars in groups.items():
        if vslot == "HOOK":
            continue
        pl = [i + 1 for i, b in enumerate(bars) if rg.is_place(b, places)]
        notes.append(f"{vslot}: {len(pl)} of {len(bars)} bars name a place (count only, not a gate)")
        loc = {w for b in bars for w in rg.words(b) if w in loans}
        if loc:
            notes.append(f"{vslot}: local words {sorted(loc)}")
        if not any(len(ff.sylls(b)) >= LONG_BAR for b in bars):
            fails.append(f"{vslot}: no bar >= {LONG_BAR} syllables; every verse has one")


def recount_gates(sections, fails, notes):
    """Section and song level: does the song CLAIM or does it tell a holiday diary (toolkit/recount.py, 14 Oct 2026)?
    Par is the original's own: longest run of recounted bars (3 in a verse), the busiest section's recount share plus one bar,
    no itinerary bars, and a song-wide recount share within 10 points of the original's 0.20. Only full songs are judged at
    song level (a single section cannot carry the song's share)."""
    try:
        import recount
    except Exception as e:   # spaCy missing: say so rather than pass silently
        notes.append(f"recount not measured ({e.__class__.__name__})")
        return
    named = [(s, b) for s, b in sections if s and b]
    if not named:
        return
    rf, _rows, song = recount.run(named, overlap=False, quiet=True)
    if len(named) < 5:
        rf = [f for f in rf if not f.startswith("SONG")]
    fails.extend("recount: " + f for f in rf)
    notes.append(f"recount share {song:.0%} (the original 20%)")


def swagger_gates(sections, fails, notes):
    """Song level: hook stamps and verse menace at the original's par (toolkit/swagger.py, 15 Oct 2026). Judged only on a full
    song (hook + verses), because the original's own sections vary from 0 to 6 of 8."""
    try:
        import swagger
    except Exception as e:  # noqa: BLE001
        notes.append(f"swagger not measured ({e.__class__.__name__})")
        return
    named = [(s, b) for s, b in sections if s and b]
    if len(named) < 5:
        return
    m = swagger.measure(named)
    fails.extend("swagger: " + f for f in swagger.fails_of(m))
    hs, hn = m["hook_stamps"]
    vs, vn = m["verse_menace"]
    notes.append(f"swagger: hook stamps {hs}/{hn}, verse swagger {vs}/{vn} (original 9/16, 25/60)")


def run(sections, title):
    fails, notes = [], []
    for slot, bars in sections:
        if not bars:
            continue
        line_gates(slot, bars, fails)
        scheme_gate(slot, bars, fails, notes)
    verse_gate(sections, fails, notes)
    recount_gates(sections, fails, notes)
    swagger_gates(sections, fails, notes)
    device_gates(sections, fails, notes)
    imagery_gates(sections, fails, notes)
    song_gates(sections, title, fails, notes)
    print(f"  {len(sections)} sections, {sum(len(b) for _, b in sections)} bars")
    for f in fails:
        print("  XX", f)
    for n in notes[:6]:
        print("  ~ ", n)
    if len(notes) > 6:
        print(f"  ~  ... and {len(notes) - 6} more grader-limit notes")
    print(f"SONGCHECK: {'PASS' if not fails else f'{len(fails)} PROBLEMS'}")
    return fails


def _positional():
    """The first argument that is not a flag and not a flag's value (the file, or '-' for stdin)."""
    skip = {sys.argv.index(f) + 1 for f in ("--slot", "--title", "--original") if f in sys.argv}
    for i in range(1, len(sys.argv)):
        if i not in skip and not sys.argv[i].startswith("--"):
            return sys.argv[i]
    return "-"


def main():
    if "--original" in sys.argv:
        path = sys.argv[sys.argv.index("--original") + 1]
        lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
        sections = [(s, lines[a:b]) for s, a, b in ORIG_SEC]
    else:
        src = _positional()
        text = sys.stdin.read() if src == "-" else open(src, encoding="utf8").read()
        if "--slot" in sys.argv:
            sections = [(sys.argv[sys.argv.index("--slot") + 1],
                         [l.strip() for l in text.splitlines() if l.strip()])]
        else:
            sections = bars_of(text)
    title = sys.argv[sys.argv.index("--title") + 1] if "--title" in sys.argv else None
    print(f"songcheck (title={title!r}):")
    sys.exit(0 if not run(sections, title) else 1)


if __name__ == "__main__":
    main()
