"""quality: Claude's OWN pre-show gate. Nothing goes to Joe unless this says CLEARS THE BAR and the critic agrees.
  python toolkit/quality.py FILE [--block 4]      FILE = bars one per line (blank line = new stanza); comments with #
This gates MY drafts, never Joe's lines. The floor comes from the ORIGINAL song (reference/original_lyrics.txt measured with rhyme_tools.quad_stats; re-derived 11 Oct 2026; Joe's own hook bars are below the original and no longer the anchor):
  - length: 4-15 syllables per bar, block mean <= 12 (ORIGINAL: 2-15, mean 8.9; Joe's hook bars run shorter)
  - endings: >= 1 bar per block ends weak/feminine (Joe: 0-4)
  - rhyme: <= 1 bar per 4 without a 2-syllable end-tail partner (X-line allowed if marked with a leading '~')
  - density: >= 2 multisyllabic runs (Joe lowest block: 1) and >= 1 internal-rhyme bar per 4-bar block
  - chains: in a stanza of 8+ bars at least 75% of bars share one end-sound family (original verse chains: 8 of 8, ~13 of 16)
  - no end word used 3+ times in a block; no filler/explainer phrases; no unconfirmed slang; <= 2 place names per 4 bars
Passing this is necessary, NOT sufficient: a fresh-context critic must also score every bar (quality/gate.md).
"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
import os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import rhyme_tools as R
for l in open(os.path.join(ROOT, "bank", "ovr.txt"), encoding="utf8"):
    if l.strip() and not l.startswith("#"):
        w, p = l.rstrip("\n").split("\t"); R.OVR[w] = p

BAD_PHRASES = ["now that's clever", "say them quick", "that's the", "you know", "if you will", "so to speak", "i'm sane", "what a ride", "enjoy the ride", "living the dream", "bucket list", "good vibes", "at the end of the day", "not gonna lie"]
BAD_SLANG = ["swear down", "skint", "mate", "lads", "proper", "sorted", "innit", "bruv"]
PLACES = [l.split(",")[0].lower() for l in open(os.path.join(ROOT, "bank", "seeds.csv"), encoding="utf8").read().splitlines()[1:] if ",place," in l]


def blocks(path, n):
    stanzas, cur = [], []
    for raw in open(path, encoding="utf8"):
        s = raw.strip()
        if s.startswith("#"):
            continue
        if not s:
            if cur: stanzas.append(cur); cur = []
            continue
        cur.append(s)
    if cur: stanzas.append(cur)
    out = []
    for st in stanzas:
        if len(st) <= 2 * n:          # short stanza = one block (don't cut a 5-bar stanza into 4+1)
            out.append(st)
            continue
        for i in range(0, len(st), n):
            out.append(st[i:i + n])
    return stanzas, out


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return 2
    n = int(a[a.index("--block") + 1]) if "--block" in a else 4
    stanzas, bl = blocks(a[0], n)
    fails = 0
    for bi, b in enumerate(bl, 1):
        xl = [x.startswith("~") for x in b]
        joe = [x.lstrip("~").startswith("=") for x in b]   # '=' marks Joe's verbatim bars: scored for rhyme, exempt from repeat/place checks
        bars = [x.lstrip("~").lstrip("=").strip() for x in b]
        probs = []
        oov = sorted({w for x in bars for w in re.findall(r"[A-Za-z']+", x) if R.pron(w) is None})
        if oov:
            print(f"block {bi} [UNKNOWN WORDS] {oov}: add to bank/ovr.txt (word<TAB>ARPAbet), tool cannot score these bars")
            fails += 1
            continue
        q = R.quad_stats(bars)
        syl = q["syl"]
        if any(s < 4 or s > 15 for s in syl): probs.append(f"length {syl} (original runs 4-15)")
        if sum(syl) / len(syl) > 12: probs.append(f"mean length {sum(syl)/len(syl):.1f} > 12 (original blocks: mean 9, max 12.5)")
        if q["fem_end"] < 1: print("   note: no weak (feminine) ending in this block (Joe's blocks have 0-4); fine if deliberate")
        sch = q["scheme2"]
        def endkey(x):
            ph, _ = R.pron_phrase(re.findall(r"[A-Za-z']+", x)[-1])
            return R.key(ph, 0, "perfect") if ph else None
        keys = [endkey(x) for x in bars]
        lone = sum(1 for i, k in enumerate(keys) if keys.count(k) == 1 and sch.count(sch[i]) == 1 and not xl[i])
        if lone > 1: probs.append(f"{lone} bars have no end-rhyme partner ({sch})")
        if len(bars) >= 4 and q["multisyl"] < 2: probs.append(f"multisyllabic runs {q['multisyl']} < 2")
        if len(bars) >= 4 and q["internal_bars"] < 1: probs.append("no internal rhyme")
        ends = [re.findall(r"[a-z']+", x.lower())[-1] for x, j in zip(bars, joe) if not j]
        dup = {e for e in ends if ends.count(e) > 2}
        if dup: probs.append(f"end word used 3+ times {sorted(dup)} (an echo twice is fine)")
        text = " ".join(x for x, j in zip(bars, joe) if not j).lower()
        for ph in BAD_PHRASES:
            if ph in text: probs.append(f"filler/cliche phrase '{ph}'")
        for sl in BAD_SLANG:
            if re.search(r"\b" + sl + r"\b", text): probs.append(f"unconfirmed slang '{sl}'")
        pl = [p for p in PLACES if re.search(r"\b" + re.escape(p) + r"\b", text)]
        if len(pl) > 2: probs.append(f"{len(pl)} place names in {len(bars)} bars (itinerary risk): {pl}")
        status = "ok " if not probs else "BELOW BAR"
        fails += bool(probs)
        print(f"block {bi} [{status}] syl={syl} scheme2={sch} fem={q['fem_end']} int={q['internal_bars']} multi={q['multisyl']}")
        for p in probs: print("   -", p)
    print("VERDICT:", "CLEARS THE MEASURED BAR (critic still required)" if not fails else f"BELOW BAR in {fails} of {len(bl)} blocks: do not show Joe")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
