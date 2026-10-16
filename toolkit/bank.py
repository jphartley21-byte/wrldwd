"""Query the writer's supply: words by sound, and stock phrases whose payoff can sit in the rhyme slot.

The gap this fills: `rhyme_tools.py` answers "what rhymes with X", but a writer working to a frame
needs the reverse - "I have 8 bars ending ɑː eɪ ɑː aɪ, what can go there?" - and needs PHRASES, not
just words, because cashing a stock phrase is the core technique (rule 1).

Supply it draws on:
  cmudict (126k words) + rhyme_tools.OVR (place names, slang)   -> anything measurable
  toolkit/phrases.txt                                            -> stock phrases + their payoff word
  toolkit/theme_words.txt                                        -> the song's own material
  UK_EVERYDAY below                                              -> British words wordfreq under-rates

usage:
    python toolkit/bank.py phrases ɑː                 # cashed-phrase candidates for a ɑː end
    python toolkit/bank.py phrases eɪ --sense money   # ... filtered to one register
    python toolkit/bank.py words ɑː --syl 1 --limit 40
    python toolkit/bank.py slot --ends "ɑː ɑː eɪ ɑː aɪ eɪ əʊ eɪ"   # per bar: words + phrases
    python toolkit/bank.py check                      # payoff words the toolkit cannot measure
    python toolkit/bank.py uk                         # everyday British words, for a G2 sanity check
    python toolkit/bank.py --selftest
"""

import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import craft_scan as cs      # noqa: E402
import rhyme_tools as rt     # noqa: E402

PHRASES = os.path.join(HERE, "phrases.txt")
RAW = os.path.join(HERE, "phrases_raw.txt")
THEME = os.path.join(HERE, "theme_words.txt")
ENTITIES = os.path.join(HERE, "entities.txt")
LOANWORDS = os.path.join(HERE, "loanwords.txt")

# ARPAbet vowel -> the British IPA the rest of the repo reports (craft_scan.nuclei gives British
# vowels for words it knows; this table is for the rhyme_tools key index, which is ARPAbet).
ARP2IPA = {"AA": "ɑː", "AE": "æ", "AH": "ʌ", "AO": "ɔː", "AW": "aʊ", "AY": "aɪ", "EH": "ɛ",
           "ER": "ɜː", "EY": "eɪ", "IH": "ɪ", "IY": "iː", "OW": "əʊ", "OY": "ɔɪ", "UH": "ʊ",
           "UW": "uː"}

# Everyday British words and slang that wordfreq, being US-weighted, scores as rare: skint 2.42,
# knackered 2.64, chuffed 2.70, naff 2.20, bevvy 1.59, sarnie 1.62, butty 1.99, scran 1.70,
# trollied 1.25. A low zipf on one of these is not evidence the word is obscure to Joe or his mates.
UK_EVERYDAY = set("""skint knackered chuffed naff dodgy blag blagged faff faffing doss skive skiving
kip kipping bevvy bevvies bevvied sarnie butty scran gaff trollied mullered legless wazzock numpty
plonker pillock muppet tosser git sod berk wally div divvy mardy narky gormless doolally barmy
buzzin hench chav scally cushdy chocker chocka stonking caff cuppa innit baccy brolly wellies cagoule
anorak offy chippy chippies kebab brew scoff grub nosebag dosh wedge readies tenner fiver quid snide
moody hooky nicked nicking grassed rozzer plod nick bent graft grafting earner earner's
fortnight pavement crisps biscuit courgette aubergine nappy plaster trainers jumper hoover biro
sellotape lolly takeaway fizzy roundabout motorway caravan chipolata bap sarnie bangers mash
weatherspoons wetherspoons bish bosh sorted mate lads bird sarnie""".split())
UK_EVERYDAY |= set(rt.UKLEX)    # 16 Oct 2026: the UK rap lexicon (toolkit/uk_rap_lexicon.txt) is exempt from the US-weighted filter too


_PHRASE_CACHE = None
_ENTITY_CACHE = None
_LOAN_CACHE = None


def phrase_info(row):
    """End vowel, syllable counts and whether the payoff is measurable at all."""
    info = dict(row)
    nuclei = cs.nuclei(row["payoff"])
    info["measurable"] = bool(nuclei)
    info["end"] = nuclei[-1][4] if nuclei else None
    info["payoff_syl"] = len(nuclei) if nuclei else 0
    info["phrase_syl"] = len(cs.nuclei(row["phrase"].replace("-", " ")))
    return info


def _phrase_rows(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                continue
            score = None
            if len(parts) > 4:
                try:
                    score = float(parts[4])
                except ValueError:
                    score = None
            rows.append({"phrase": parts[0], "payoff": parts[1],
                         "sense": parts[2] if len(parts) > 2 else "-",
                         "source": parts[3] if len(parts) > 3 else "curated",
                         "score": score})
    return rows


def load_phrases(paths=None):
    """Curated phrases.txt first, then the harvested phrases_raw.txt. Cached: this is called per
    bar position, and there are thousands of rows now."""
    global _PHRASE_CACHE
    if paths is None and _PHRASE_CACHE is not None:
        return _PHRASE_CACHE
    if paths is None:
        paths = [PHRASES, RAW]
    elif isinstance(paths, str):
        paths = [paths]
    out = []
    for p in paths:
        for r in _phrase_rows(p):
            r["curated"] = (os.path.abspath(p) == os.path.abspath(PHRASES))
            out.append(phrase_info(r))
    if paths == [PHRASES, RAW]:
        _PHRASE_CACHE = out
    return out


def theme_words(path=THEME):
    out = []
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if line and not line.startswith("#"):
                out += line.split()
    return sorted(set(out))


_ZIPF = {}


def load_entities(path=ENTITIES):
    """Names for rap: places, given names, surnames, films, TV, music (Wikidata, CC0)."""
    global _ENTITY_CACHE
    if _ENTITY_CACHE is not None and path == ENTITIES:
        return _ENTITY_CACHE
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                continue
            nuc = cs.nuclei(parts[0])
            rows.append({"name": parts[0], "type": parts[1], "measurable": bool(nuc),
                         "end": nuc[-1][4] if nuc else None, "syl": len(nuc)})
    if path == ENTITIES:
        _ENTITY_CACHE = rows
    return rows


def entities_for(kind=None, end=None, limit=40, measurable_only=False):
    rows = load_entities()
    if kind:
        rows = [r for r in rows if r["type"] == kind]
    if end:
        rows = [r for r in rows if r["end"] == end]
    if measurable_only:
        rows = [r for r in rows if r["measurable"]]
    return rows[:limit]


def cmd_entities(kind, end, limit, measurable_only, types):
    if types:
        c = collections.Counter(r["type"] for r in load_entities())
        print("entity types in the pool:")
        for t, n in c.most_common():
            print(f"  {t:<12} {n}")
        return
    rows = entities_for(kind, end, limit, measurable_only)
    if not rows:
        print("no names match")
        return
    print(f"{len(rows)} name(s)" + (f" type {kind}" if kind else "")
          + (f" ending {end}" if end else "") + ":")
    for r in rows:
        flag = "" if r["measurable"] else "  (no pronunciation yet - add to OVR)"
        print(f"  {r['name']:<28} {r['type']:<11} {str(r['end'] or '?'):<4} {r['syl']} syl{flag}")


def load_loanwords(path=LOANWORDS):
    """The word a place uses for a common idea (Wiktionary translations, CC BY-SA).

    This is the supply for the original's actual engine -- a word in each place's own language -- and
    the repo had none of it. Only some of these are pronounceable by the rhyme engine yet, so
    `measurable` matters: an unmeasurable word cannot go in the rhyme slot until OVR knows it.
    """
    global _LOAN_CACHE
    if _LOAN_CACHE is not None and path == LOANWORDS:
        return _LOAN_CACHE
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4:
                continue
            nuc = cs.nuclei(parts[0])
            rows.append({"word": parts[0], "lang": parts[1], "country": parts[2], "gloss": parts[3],
                         "measurable": bool(nuc and rt_pron(parts[0])),
                         "end": nuc[-1][4] if nuc else None, "syl": len(nuc)})
    if path == LOANWORDS:
        _LOAN_CACHE = rows
    return rows


def rt_pron(word):
    try:
        return rt.pron(word)
    except Exception:
        return None


def loanwords_for(country=None, end=None, gloss=None, limit=60, measurable_only=True):
    rows = load_loanwords()
    if country:
        rows = [r for r in rows if r["country"].lower().startswith(country.lower())]
    if end:
        rows = [r for r in rows if r["end"] == end]
    if gloss:
        rows = [r for r in rows if gloss.lower() in r["gloss"].lower()]
    if measurable_only:
        rows = [r for r in rows if r["measurable"]]
    return rows[:limit]


def slang_rows(domain=None, end=None, limit=60, rare=False):
    """The harvested slang vocabulary, by DOMAIN: the ledger records which Wiktionary category each word came from, so
    "what money words do we have" is answerable. Joe, 13 Oct 2026: all swearing and vulgar slang, and the slang of drugs,
    guns, weapons and money, must be available and never discouraged.

    Domains: money, drugs, weapons, firearms, crime, prison, violence, vulgar, swear, slang, british, informal.
    """
    import vocab as vc
    key = (domain or "").lower()
    out = []
    for rec in vc._load().values():
        srcs = " ".join(rec.get("sources") or []).lower()
        if key and key not in srcs:
            continue
        if rare and (rec.get("zipf") or 0) >= 3.0:
            continue
        out.append({"word": rec.get("word"), "sources": rec.get("sources") or [], "zipf": rec.get("zipf"),
                    "g2": rec.get("g2"), "end": rec.get("end_tail"), "syl": rec.get("syllables"),
                    "oov": rec.get("oov")})
    if end:
        out = [r for r in out if r["end"] == end]
    out.sort(key=lambda r: (-(r["zipf"] or 0), r["word"] or ""))
    return out[:limit]


def cmd_slang(domain, end, limit, rare, report):
    rows = slang_rows(domain, end, limit, rare)
    if not rows:
        print(f"no banked slang for domain '{domain}'" + (f" ending {end}" if end else ""))
        print("  domains: money drugs weapons firearms crime prison violence vulgar swear slang british informal")
        return
    print(f"{len(rows)} word(s) from the '{domain or 'any'}' layer" + (f" ending {end}" if end else "")
          + " (commonest first; the ledger's recognisability proxy is US-weighted, so treat G2 RISK as a prompt, not a veto):")
    for r in rows:
        flag = "  OOV (needs an OVR entry to rhyme)" if r["oov"] else ""
        print(f"  {r['word']:<16} {str(r['end'] or '?'):<5} {str(r['syl'] or '?'):>2} syl  zipf "
              f"{(r['zipf'] if r['zipf'] is not None else 0):.2f}  g2 {r['g2']}{flag}")
    if report:
        print("\nsources: " + "; ".join(sorted({s for r in rows for s in r["sources"]})))


def cmd_loanwords(country, end, gloss, limit, show_all):
    rows = loanwords_for(country, end, gloss, limit, measurable_only=not show_all)
    if not rows:
        print("no loanwords match")
        if not show_all:
            print("  (only words the rhyme engine can already pronounce are shown; --all lists the rest)")
        return
    print(f"{len(rows)} loanword(s)" + (f" from {country}" if country else "")
          + (f" ending {end}" if end else "") + (f" for '{gloss}'" if gloss else "")
          + (" [all, including unpronounceable]" if show_all else " [pronounceable only]") + ":")
    for r in rows:
        flag = "" if r["measurable"] else "  (needs an OVR entry before it can rhyme)"
        print(f"  {r['word']:<16} {r['country']:<12} {r['gloss']:<12} {str(r['end'] or '?'):<4} "
              f"{r['syl']} syl{flag}")


def rt_zipf(word):
    if word not in _ZIPF:
        try:
            from wordfreq import zipf_frequency
            _ZIPF[word] = zipf_frequency(word, "en")
        except Exception:
            _ZIPF[word] = 9.0
    return _ZIPF[word]


def words_by_vowel(vowel, n=1, limit=60, min_zipf=1.6, syllables=None):
    """Words whose final n-syllable tail starts on `vowel` (IPA), commonest first.

    cmudict holds a lot of fragments and abbreviations ("ar", "da", "flynt"), so a word is kept
    only if it is common enough or on the UK_EVERYDAY list, and results are ordered by commonness
    rather than by length.
    """
    idx = rt.index(n, "perfect", "any")
    want = {a for a, i in ARP2IPA.items() if i == vowel}
    seen = set()
    for key, words in idx.items():
        head = key[0] if isinstance(key, tuple) else str(key).split("-")[0]
        if head.rstrip("012") not in want:
            continue
        for w in words:
            if len(w) > 1 and (w not in seen):
                seen.add(w)
    out = []
    for w in seen:
        nv = cs.nuclei(w)
        if len(nv) < n or nv[-n][4] != vowel:
            continue                      # the ARPAbet index is US-vowelled; this is the UK check
        if rt_zipf(w) >= min_zipf or w in UK_EVERYDAY:
            out.append(w)
    if syllables:
        keep = []
        for w in out:
            ph = rt.pron(w)
            if ph and rt.nsyl(ph) in syllables:
                keep.append(w)
        out = keep
    out.sort(key=lambda w: (-rt_zipf(w), len(w), w))
    return out[:limit]


def print_phrases(vowel, sense=None, limit=40, show_rhymes=False, min_score=2.0, curated_only=False):
    rows = [r for r in load_phrases() if r["measurable"] and r["end"] == vowel]
    if curated_only:
        rows = [r for r in rows if r["curated"]]
    else:
        rows = [r for r in rows if r["curated"] or (r.get("score") or 0) >= min_score]
    if sense:
        rows = [r for r in rows if r["sense"] == sense]
    if not rows:
        print(f"no phrases end on {vowel}" + (f" in sense {sense}" if sense else ""))
        return []
    n_cur = len([r for r in rows if r["curated"]])
    rows.sort(key=lambda r: (0 if r["curated"] else 1, -(r.get("score") or 9), r["phrase"]))
    print(f"{len(rows)} cashed-phrase candidates ending {vowel} "
          f"({n_cur} curated, {len(rows) - n_cur} harvested)"
          + (f", sense {sense}" if sense else "") + f" - showing {min(limit, len(rows))}:")
    for r in rows[:limit]:
        mark = " " if r["curated"] else "*"
        sc = "" if r["curated"] else f" score {r.get('score')}"
        print(f" {mark}{r['phrase']:<34} payoff {r['payoff']:<10} {r['phrase_syl']:>2} syl  <- {r['sense']}{sc}")
    return rows


def cmd_slot(ends, limit, senses):
    print("per bar: the end sound the frame needs, then what can fill it\n")
    for i, vowel in enumerate(ends, 1):
        print(f"== bar {i}: {vowel}")
        ws = words_by_vowel(vowel, n=1, limit=limit, min_zipf=1.6)
        uk = [w for w in ws if w in UK_EVERYDAY]
        print("   words: " + ", ".join(ws))
        if uk:
            print("   (everyday-British among them, wordfreq may under-rate: " + ", ".join(uk) + ")")
        rows = [r for r in load_phrases() if r["measurable"] and r["end"] == vowel]
        if senses:
            rows = [r for r in rows if r["sense"] in senses]
        rows.sort(key=lambda r: (0 if r["curated"] else 1, -(r.get("score") or 9), r["phrase"]))
        cur = [r for r in rows if r["curated"]]
        har = [r for r in rows if not r["curated"]][:8]
        if cur:
            print("   phrases: " + " | ".join(f"{r['phrase']} [{r['sense']}]" for r in cur[:12]))
        if har:
            print("   also:    " + " | ".join(f"{r['phrase']} [{r['sense']}]" for r in har))
        print()


def cmd_check():
    rows = load_phrases()
    bad = [r for r in rows if not r["measurable"]]
    print(f"phrases.txt: {len(rows)} phrases, {len(rows) - len(bad)} measurable")
    if bad:
        print("payoff words with no pronunciation (add to OVR in rhyme_tools.py):")
        for r in bad:
            print(f"  {r['payoff']:<14} ({r['phrase']})")
    counts = collections.Counter(r["end"] for r in rows if r["measurable"])
    print("\nending sounds covered:")
    for v, c in counts.most_common():
        print(f"  {v:<4} {c}")
    return bad


def selftest():
    ok = True
    rows = load_phrases()
    checks = [
        ("phrases.txt loads", len(rows) > 150),
        ("on the house -> aʊ", any(r["phrase"] == "on the house" and r["end"] == "aʊ" for r in rows)),
        ("on the slate -> eɪ", any(r["phrase"] == "on the slate" and r["end"] == "eɪ" for r in rows)),
        ("cut corners -> ə", any(r["phrase"] == "cut corners" and r["end"] == "ə" for r in rows)),
        ("theme_words loads", len(theme_words()) > 300),
        ("words_by_vowel ɑː puts real words first",
         {"bar", "car", "far", "star"} & set(words_by_vowel("ɑː", n=1, limit=30)) != set()),
        ("UK_EVERYDAY has the words wordfreq under-rates", {"skint", "knackered", "chuffed"} <= UK_EVERYDAY),
        ("entities load with a type and an end sound",
         all(("type" in r and "end" in r) for r in load_entities()[:20]) if load_entities() else True),
        ("entities_for filters by type",
         all(r["type"] == "city" for r in entities_for(kind="city", limit=10))),
        ("loanwords load with country, gloss and end sound",
         all(("country" in r and "gloss" in r and "end" in r) for r in load_loanwords()[:20])
         if load_loanwords() else True),
        ("loanwords: a known greeting is pronounceable",
         any(r["word"] == "hola" and r["measurable"] for r in load_loanwords())),
        ("loanwords_for filters by country",
         all(r["country"] == "Italy" for r in loanwords_for(country="Italy", limit=5))),
        ("loanwords_for filters by end sound",
         all(r["end"] == "əʊ" for r in loanwords_for(end="əʊ", limit=5))),
        ("the unpronounceable loanwords are held back by default",
         len(loanwords_for(limit=999)) < len(loanwords_for(limit=999, measurable_only=False))),
    ]
    for name, good in checks:
        if not good:
            ok = False
            print(f"  FAIL {name}")
    print("BANK SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("phrases")
    p.add_argument("vowel")
    p.add_argument("--sense")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--rhymes", action="store_true")
    w = sub.add_parser("words")
    w.add_argument("vowel")
    w.add_argument("--syl", type=int, default=None)
    w.add_argument("--n", type=int, default=1)
    w.add_argument("--limit", type=int, default=60)
    w.add_argument("--min-zipf", type=float, default=1.6)
    s = sub.add_parser("slot")
    s.add_argument("--ends", required=True)
    s.add_argument("--limit", type=int, default=24)
    s.add_argument("--sense", action="append")
    sub.add_parser("check")
    sub.add_parser("uk")
    en = sub.add_parser("entities")
    en.add_argument("--type")
    en.add_argument("--end")
    en.add_argument("--limit", type=int, default=40)
    en.add_argument("--measurable-only", action="store_true")
    en.add_argument("--types", action="store_true", help="list the types and their sizes")
    lw = sub.add_parser("loanwords")
    lw.add_argument("--country")
    lw.add_argument("--end")
    lw.add_argument("--gloss")
    lw.add_argument("--limit", type=int, default=60)
    lw.add_argument("--all", action="store_true",
                    help="include words the rhyme engine cannot pronounce yet")
    sl = sub.add_parser("slang", help="the harvested slang layers by domain: money, drugs, weapons, firearms, crime, "
                                      "prison, violence, vulgar, swear, slang, british, informal")
    sl.add_argument("domain", nargs="?", default=None)
    sl.add_argument("--end", help="filter by end sound (as the ledger records it, e.g. ɒ, aɪ)")
    sl.add_argument("--limit", type=int, default=60)
    sl.add_argument("--rare", action="store_true", help="only the rarer end of the layer (zipf < 3.0)")
    sl.add_argument("--report", action="store_true", help="also print which source categories the words came from")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.cmd == "phrases":
        print_phrases(a.vowel, a.sense, a.limit, a.rhymes)
    elif a.cmd == "words":
        syl = {a.syl} if a.syl else None
        print(", ".join(words_by_vowel(a.vowel, a.n, a.limit, a.min_zipf, syl)))
    elif a.cmd == "slot":
        cmd_slot(a.ends.split(), a.limit, set(a.sense or []))
    elif a.cmd == "check":
        return 1 if cmd_check() else 0
    elif a.cmd == "uk":
        print(f"{len(UK_EVERYDAY)} everyday British words wordfreq may under-rate:\n")
        print(", ".join(sorted(UK_EVERYDAY)))
    elif a.cmd == "entities":
        cmd_entities(a.type, a.end, a.limit, a.measurable_only, a.types)
    elif a.cmd == "loanwords":
        cmd_loanwords(a.country, a.end, a.gloss, a.limit, a.all)
    elif a.cmd == "slang":
        cmd_slang(a.domain, a.end, a.limit, a.rare, a.report)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
