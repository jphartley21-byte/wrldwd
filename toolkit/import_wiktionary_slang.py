"""import_wiktionary_slang: stream-filter the kaikki.org English Wiktionary dump for UK/British slang and informal senses.
  curl -s https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl | python3 toolkit/import_wiktionary_slang.py > bank/slang_wiktionary.csv
Keeps senses whose tags include a UK marker (UK, British, England, Cockney, Scotland...) AND a slang marker (slang, informal, colloquial, dialectal).
Drops senses tagged vulgar/offensive/derogatory/slur/obsolete. One CSV row per word (first 3 glosses). Schema = bank schema.
LICENCE: Wiktionary text is CC BY-SA 4.0; data via kaikki.org (Tatu Ylonen, Wiktextract; cite Ylonen 2022 LREC). See bank/SLANG_WIKTIONARY_ATTRIBUTION.md.
Nothing is stored except the filtered rows; the 3 GB dump is streamed.
"""
import csv, json, sys
sys.stdout.reconfigure(encoding="utf-8")
UK = {"UK", "British", "England", "English", "Cockney", "Scotland", "Scottish", "Wales", "Welsh", "Ireland", "Irish", "Northern England", "Britain", "Australia", "New Zealand", "Multicultural London English", "London"}
UKCORE = {"UK", "British", "Cockney", "Britain", "Multicultural London English", "Multicultural-London-English", "London", "England", "Northern England", "Northern-England", "Scotland", "Wales", "Jamaica", "Jamaican-Patois", "Ireland", "Geordie", "Scouse", "Estuary-English"}
UKCAT = ("British English", "Multicultural London English", "English slang", "UK slang", "Cockney", "Scottish English", "Welsh English", "Irish English", "Geordie", "Scouse")
UKREFS = ("ukdrill", "r/unitedkingdom", "r/CasualUK", "r/AskUK", "BBC", "Guardian", "Daily Mail", "Mirror", "Independent", "Telegraph", "Metro", "Time Out", "London", "UK", "British", "Gangster", "grime", "Skepta", "Stormzy", "Dave", "Wiley")
SLANG = {"slang", "informal", "colloquial", "dialectal", "idiomatic", "jargon", "mildly", "usually"}
DROP = {"vulgar", "offensive", "ethnic", "slur", "ethnic slur", "obsolete", "archaic", "rare"}
FIELDS = ["id", "type", "text", "items", "sound", "places", "tags", "source", "joe_says_it", "status"]
w = csv.DictWriter(sys.stdout, FIELDS); w.writeheader()
n = 0
seen = set()
for line in sys.stdin:
    try:
        d = json.loads(line)
    except Exception:
        continue
    word = d.get("word", "")
    if not word or len(word) > 40 or word in seen:
        continue
    if d.get("lang_code") != "en":
        continue
    gl = []
    tagset = set()
    for s in d.get("senses", []):
        t = set(s.get("tags", [])) | set(d.get("tags", []))
        cats = [c.get("name", "") if isinstance(c, dict) else str(c) for c in s.get("categories", [])]
        catset = " ".join(cats)
        region = bool(t & UKCORE) or any(k in catset for k in ("British English", "Multicultural London English", "UK slang", "Cockney", "Scottish English", "Welsh English", "Irish English", "Geordie", "Scouse"))
        slangy = bool(t & SLANG) or "English slang" in catset or "English informal" in catset
        if (t & DROP) or not slangy:
            continue
        if not region:
            # slang with no region tag: keep only if its quotations come from UK-flavoured sources
            refs = " ".join((e.get("ref", "") + " " + e.get("text", "")) for e in s.get("examples", [])[:6])
            if not any(k in refs for k in UKREFS):
                continue
        g = (s.get("glosses") or [""])[-1] if s.get("glosses") else ""
        if g and not g.lower().startswith(("alternative", "misspelling", "plural of", "abbreviation of", "initialism of")):
            gl.append(g[:140]); tagset |= (t & (UKCORE | SLANG))
    if gl:
        seen.add(word); n += 1
        w.writerow({"id": f"wik{n}", "type": "slang_wiktionary", "text": word, "items": " | ".join(gl[:3]), "tags": ";".join(sorted(tagset)),
                    "source": f"https://en.wiktionary.org/wiki/{word.replace(' ', '_')} (CC BY-SA 4.0; via kaikki.org)", "status": "wiktionary"})
print(f"# rows: {n}", file=sys.stderr)
