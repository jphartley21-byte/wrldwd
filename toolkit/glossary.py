"""glossary: find words/phrases a reader (or a critic, or a tool) may not know, and show what the repo already knows about them.
  python toolkit/glossary.py FILE [--zipf 3.2] [--lookup]   (bars one per line; --lookup fetches HINTS from Wiktionary + Urban Dictionary for NEEDS GLOSS words)
Flags a word when it is rare (wordfreq Zipf < threshold), missing from the pronunciation dictionary, or capitalised mid-line (names).
For each flagged word it prints any gloss found in bank/slang.csv, mundane.csv, names_culture.csv, places_events.csv, seeds.csv, register_stiff.csv,
or says NEEDS GLOSS. Resolve every NEEDS GLOSS (ask Joe, or look it up: Urban Dictionary / Wiktionary / Green's, see research/slang_sources.md)
BEFORE any critic or reader sees the lines, and paste the glosses into the critic prompt for ALL stanzas equally (original and new).
"""
import csv, glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import rhyme_tools as R
from wordfreq import zipf_frequency
for l in open(os.path.join(ROOT, "bank", "ovr.txt"), encoding="utf8"):
    if l.strip() and not l.startswith("#"):
        w, p = l.rstrip("\n").split("\t"); R.OVR[w] = p

KNOWN = {}
for p in glob.glob(os.path.join(ROOT, "bank", "*.csv")):
    b = os.path.basename(p)
    if b in ("rhymes.csv", "wordplay_soundalikes.csv"):
        continue
    for r in csv.DictReader(open(p, encoding="utf8")):
        t = (r.get("text") or r.get("term") or "").lower().strip()
        g = (r.get("items") or r.get("note") or "").strip()
        if t:
            KNOWN.setdefault(t, (b.replace(".csv", ""), g[:140]))
            for w in re.findall(r"[a-z']+", t):
                if len(w) > 3:
                    KNOWN.setdefault(w, (b.replace(".csv", ""), f"in '{t}': {g[:110]}"))


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    thr = float(a[a.index("--zipf") + 1]) if "--zipf" in a else 3.2
    seen = {}
    for n, raw in enumerate(open(a[0], encoding="utf8"), 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        s = s.lstrip("~=").strip()
        toks = re.findall(r"[A-Za-z][A-Za-z']*", s)
        for i, w in enumerate(toks):
            lw = re.sub(r"(?:'s|'m|'ll|'ve|'d|'re|n't)$", "", w.lower().strip("'"))
            if w.lower() in ("i'm", "i'd", "i've", "i'll"):
                continue
            if len(lw) < 3:
                continue
            reason = None
            z = zipf_frequency(lw, "en")
            if z < thr: reason = f"rare ({z:.1f})"
            elif R.pron(lw) is None: reason = "not in pronunciation dictionary"
            elif i > 0 and w[0].isupper(): reason = "name/proper noun"
            if reason and lw not in seen:
                seen[lw] = (reason, n, s)
    need = 0
    look = "--lookup" in a
    if look:
        import slang_lookup as SL
    for lw, (reason, n, s) in sorted(seen.items()):
        k = KNOWN.get(lw)
        if k:
            print(f"{lw:14} [{reason}] bar {n}: known in {k[0]}: {k[1]}")
        else:
            print(f"{lw:14} [{reason}] bar {n}: NEEDS GLOSS   | {s[:70]}"); need += 1
            if look and not reason.startswith("name"):
                r = SL.lookup(lw)
                for x in r["wiktionary"][:2]: print(f"       hint [wiktionary{' ' + ','.join(x['tags']) if x['tags'] else ''}] {x['gloss']}")
                for x in r["urban"][:2]: print(f"       hint [urban dictionary {x['votes']:+d}] {x['definition'][:150]}")
    print(f"\n{len(seen)} flagged words, {need} NEED GLOSS. Resolve these before any critic or reader sees the lines.")


if __name__ == "__main__":
    main()
