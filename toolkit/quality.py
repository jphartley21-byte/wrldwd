"""quality: Claude's OWN pre-show gate. Nothing goes to Joe unless this says CLEARS THE BAR and the critic agrees.
  python toolkit/quality.py FILE [--block 4]      FILE = bars one per line (blank line = new stanza); comments with #
This gates MY drafts, never Joe's lines. The floor comes from Joe's own bars (hook 1-12, V1 1-4), measured with rhyme_tools.quad_stats:
  - length: 6-10 syllables per bar, mean <= 9.5 (Joe: 4-10, mean ~8; rejected v17 ran 11-14)
  - endings: >= half the bars end weak/feminine (Joe: 2-4 of 4)
  - rhyme: <= 1 bar per 4 without a 2-syllable end-tail partner (X-line allowed if marked with a leading '~')
  - density: >= 3 multisyllabic runs and >= 1 bar with an internal rhyme per block
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
        bars = [x.lstrip("~").strip() for x in b]
        probs = []
        q = R.quad_stats(bars)
        syl = q["syl"]
        if any(s < 6 or s > 10 for s in syl): probs.append(f"length {syl} (want 6-10)")
        if sum(syl) / len(syl) > 9.5: probs.append(f"mean length {sum(syl)/len(syl):.1f} > 9.5")
        if q["fem_end"] * 2 < len(bars): probs.append(f"only {q['fem_end']}/{len(bars)} weak endings (want half)")
        sch = q["scheme2"]
        lone = sum(1 for i, c in enumerate(sch) if sch.count(c) == 1 and not xl[i])
        if lone > 1: probs.append(f"{lone} bars have no 2-syllable end-rhyme partner ({sch})")
        if q["multisyl"] < 3: probs.append(f"multisyllabic runs {q['multisyl']} < 3")
        if q["internal_bars"] < 1: probs.append("no internal rhyme")
        ends = [re.findall(r"[a-z']+", x.lower())[-1] for x in bars]
        dup = {e for e in ends if ends.count(e) > 2}
        if dup: probs.append(f"end word used 3+ times {sorted(dup)} (an echo twice is fine)")
        text = " ".join(bars).lower()
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
