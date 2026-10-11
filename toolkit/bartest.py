"""bartest: per-bar technique test, derived from how the original's best lines work (ADVISORY diagnostics).
  python toolkit/bartest.py FILE        (bars one per line; blank line = new stanza; '=' prefix = Joe's verbatim bar)
Per bar it reports which of these are present:
  INT   internal rhyme / sound-play inside the bar (two linked stressed syllables)
  CONC  a concrete noun, brand, price or number (digit, number word, bank/mundane.csv or seeds term, capitalised name)
  STIFF a stiff/formal/stoic phrase from bank/register_stiff.csv
  CLASH STIFF together with a trivial/mundane item (the bathos device)
  SURG  an idiom from bank/idiom_surgery.csv or bank/wordplay_idioms.csv with its tail changed (prefix present, full phrase not)
  STOCK a stock phrase present in full (cashed literally only if the context makes it literal: judge by eye)
  NUM   a number or price (ladder candidate)
Bars with <= 1 technique are flagged PLAIN. Last word that is a function word or repeats an earlier end word is flagged.
Not a verdict: the original has plain connective bars too. Use it to find bars that can take another technique.
"""
import csv, glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import rhyme_tools as R
for l in open(os.path.join(ROOT, "bank", "ovr.txt"), encoding="utf8"):
    if l.strip() and not l.startswith("#"):
        w, p = l.rstrip("\n").split("\t"); R.OVR[w] = p

NUMW = set("one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty sixty seventy eighty ninety hundred thousand grand monkey pony score tenner fiver quid nicker dozen".split())
FUNC = set("the a an and or but of to in on at for with my me i it is its im so then that this he she we they you was be as up out all just got get like not no yes if when what who how where than too very".split())


def norm(t):
    return re.findall(r"[a-z0-9']+", t.lower().replace("’", "'"))


def load(name, key="text"):
    p = os.path.join(ROOT, "bank", name)
    return [r[key].strip() for r in csv.DictReader(open(p, encoding="utf8"))] if os.path.exists(p) else []


STIFF = [norm(t) for t in load("register_stiff.csv")]
IDIOMS = [norm(t) for t in load("idiom_surgery.csv") + [x for x in load("wordplay_idioms.csv")]]
MUND = set(w for t in load("mundane.csv") for w in norm(t) if len(w) > 3)
SEEDS = set(w for t in load("seeds.csv", "term") for w in norm(t) if len(w) > 3)


def has_seq(words, seq):
    n = len(seq)
    return n and any(words[i:i + n] == seq for i in range(len(words) - n + 1))


def analyse(bar):
    words = norm(bar)
    out = {}
    try:
        q = R.quad_stats([bar])
        out["INT"] = q["internal_bars"] > 0 or q["multisyl"] > 0
    except Exception:
        out["INT"] = False
    caps = re.findall(r"(?<!^)\b[A-Z][a-z]+", bar)
    out["NUM"] = bool(re.search(r"\d", bar)) or any(w in NUMW for w in words)
    out["CONC"] = out["NUM"] or bool(caps) or any(w in MUND or w in SEEDS for w in words)
    stiff = [s for s in STIFF if len(s) >= 2 and has_seq(words, s)] or [s for s in STIFF if len(s) >= 3 and has_seq(words, s[:3])]
    out["STIFF"] = bool(stiff)
    out["CLASH"] = out["STIFF"] and any(w in MUND for w in words)
    full = [i for i in IDIOMS if len(i) >= 3 and has_seq(words, i)]
    prefix = [i for i in IDIOMS if len(i) >= 4 and has_seq(words, i[:-1]) and not has_seq(words, i)]
    out["STOCK"] = bool(full)
    out["SURG"] = bool(prefix)
    out["_stiff"] = " ".join(stiff[0]) if stiff else ""
    out["_idiom"] = " ".join((prefix or full)[0]) if (prefix or full) else ""
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    ends_seen = []
    total = plain = 0
    for raw in open(sys.argv[1], encoding="utf8"):
        s = raw.strip()
        if not s or s.startswith("#"):
            print(); continue
        s = s.lstrip("~=").strip()
        a = analyse(s)
        tech = [k for k in ("INT", "CONC", "CLASH", "SURG", "STOCK", "NUM") if a[k]] + (["STIFF"] if a["STIFF"] and not a["CLASH"] else [])
        score = len([k for k in tech if k not in ("NUM", "STOCK")])
        last = (norm(s) or [""])[-1]
        flag = []
        if last in FUNC: flag.append("ends on function word")
        if last in ends_seen: flag.append("repeats end word")
        ends_seen.append(last)
        total += 1
        if score <= 1: plain += 1; flag.append("PLAIN")
        extra = (f" stiff='{a['_stiff']}'" if a["_stiff"] else "") + (f" idiom='{a['_idiom']}'" if a["_idiom"] else "")
        print(f"[{' '.join(tech) or '-':26}] {s}{extra}" + (f"   <-- {', '.join(flag)}" if flag else ""))
    print(f"\n{plain} of {total} bars PLAIN (<=1 technique)")


if __name__ == "__main__":
    main()
