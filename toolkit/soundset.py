"""soundset: build a sound set the way the original builds a chain (ADVISORY, offline).
  python toolkit/soundset.py turkey                 # derive the family from a seed word: stressed vowel + any consonants + soft ending
  python toolkit/soundset.py --v ER --end IY       # or give them: stressed vowel(s), final weak vowel
  options: --v ER,AO (allowed stressed vowels, comma list) --end IY --syl 2,3 --zipf 2.6 --max 120 --nophrases
The original's chain: Turkey / certi- / dirty / thirsty / curly / thirty / forty / shortly / quickly = stressed vowel (ER, near AO/IH) + any consonants + soft -ee.
Output: A) single words grouped by consonant skeleton (all different words, no repeats), B) places/names/seeds in the family,
C) bank phrases that END in the family (stiff phrases, idioms, mundane items, slang, wordplay), D) numbers in the family (ladders).
Pick 8-16 DIFFERENT words from A-D, then build lines backwards from them (see research/craft_method.md).
"""
import argparse, csv, glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import rhyme_tools as R
for l in open(os.path.join(ROOT, "bank", "ovr.txt"), encoding="utf8"):
    if l.strip() and not l.startswith("#"):
        w, p = l.rstrip("\n").split("\t"); R.OVR[w] = p
from wordfreq import zipf_frequency

NUMS = {"twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "grand", "monkey", "pony", "score", "tenner", "fiver", "nicker", "quid", "ton", "eight", "seven", "nine", "ten", "eleven", "twelve", "dozen"}
VOW = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}


def shape(word):
    """(stressed_vowel, consonants_between, final_vowel, n_syl) for 'stressed vowel + C* + weak vowel' words, else None."""
    ph = R.pron(word)
    if not ph:
        return None
    ph = R.uk(ph)
    vi = [i for i, p in enumerate(ph) if p[-1] in "012"]
    if len(vi) < 2:
        return None
    last = ph[vi[-1]]
    if last[-1] not in "02":   # must end on a weak (or secondary-stress) vowel, e.g. thirty = TH ER1 D IY2
        return None
    # the primary-stressed vowel must be the penultimate vowel
    pen = ph[vi[-2]]
    if pen[-1] != "1":
        return None
    cons = [p for p in ph[vi[-2] + 1:vi[-1]]]
    return pen.rstrip("012"), tuple(cons), last.rstrip("012"), len(vi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", nargs="?")
    ap.add_argument("--v"); ap.add_argument("--end"); ap.add_argument("--syl", default="2,3")
    ap.add_argument("--zipf", type=float, default=2.6); ap.add_argument("--max", type=int, default=120)
    ap.add_argument("--nophrases", action="store_true")
    a = ap.parse_args()
    vs, end = None, a.end
    if a.seed:
        sh = shape(a.seed.lower().replace(" ", ""))
        if not sh:
            sys.exit(f"'{a.seed}' is not a 'stressed vowel + consonants + weak ending' word (try --v/--end)")
        vs = {sh[0]}; end = end or sh[2]
        print(f"seed '{a.seed}': stressed vowel {sh[0]}, consonants {' '.join(sh[1]) or '-'}, soft ending {sh[2]}")
    if a.v: vs = set(a.v.split(","))
    if not vs or not end: sys.exit("need a seed word or --v and --end")
    sylset = {int(x) for x in a.syl.split(",")}
    words = {}
    for w in list(R.D.keys()) + list(R.OVR.keys()):
        if not w.isalpha() or len(w) > 11:
            continue
        sh = shape(w)
        if not sh or sh[0] not in vs or sh[2] != end or sh[3] not in sylset:
            continue
        z = zipf_frequency(w, "en")
        if z >= a.zipf or w in R.OVR:
            words[w] = (sh, z)
    print(f"\n== A) single words ({len(words)} found; stressed {'/'.join(sorted(vs))} + consonants + soft {end}), grouped by consonant skeleton")
    groups = {}
    for w, (sh, z) in words.items():
        groups.setdefault(" ".join(sh[1]) or "-", []).append((z, w))
    shown = 0
    for sk in sorted(groups, key=lambda k: -len(groups[k])):
        ws = [w for z, w in sorted(groups[sk], reverse=True)][:9]
        print(f"  [{sk}] " + ", ".join(ws))
    fam = set(words)
    print("\n== B) places / names / seeds in the family")
    for p in glob.glob(os.path.join(ROOT, "bank", "seeds.csv")):
        for r in csv.DictReader(open(p, encoding="utf8")):
            lw = re.findall(r"[a-z']+", r["term"].lower())
            if lw and shape(lw[-1]) and (shape(lw[-1])[0] in vs) and shape(lw[-1])[2] == end:
                print(f"  {r['term']} ({r['kind']}, {r['region']})")
    if a.nophrases:
        return
    print("\n== C) bank phrases that END in the family (direct hits for payoff-in-the-rhyme-slot)")
    hits = []
    for p in sorted(glob.glob(os.path.join(ROOT, "bank", "*.csv"))):
        b = os.path.basename(p)
        if b in ("seeds.csv", "rhymes.csv", "wordplay_soundalikes.csv"):
            continue
        for r in csv.DictReader(open(p, encoding="utf8")):
            t = (r.get("text") or "").strip()
            lw = re.findall(r"[A-Za-z']+", t)
            if lw and lw[-1].lower() in fam and len(lw) >= 2:
                hits.append((b.replace(".csv", ""), t))
    for b, t in hits[:60]:
        print(f"  [{b}] {t}")
    print(f"  ({len(hits)} total)")
    print("\n== D) numbers / money words in the family (for a ladder)")
    print("  " + ", ".join(sorted(w for w in fam if w in NUMS)) or "  none")


if __name__ == "__main__":
    main()
