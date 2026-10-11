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
UKCORE = {"UK", "British", "Cockney", "Britain", "Multicultural London English", "London", "England", "Northern England", "Scotland", "Wales"}
SLANG = {"slang", "informal", "colloquial", "dialectal", "idiomatic", "jargon"}
DROP = {"vulgar", "offensive", "derogatory", "ethnic slur", "slur", "obsolete", "archaic", "rare", "pejorative"}
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
        if not (t & UKCORE) or not (t & SLANG) or (t & DROP):
            continue
        g = (s.get("glosses") or [""])[-1] if s.get("glosses") else ""
        if g and not g.lower().startswith(("alternative", "misspelling", "plural of", "abbreviation of", "initialism of")):
            gl.append(g[:140]); tagset |= (t & (UKCORE | SLANG))
    if gl:
        seen.add(word); n += 1
        w.writerow({"id": f"wik{n}", "type": "slang_wiktionary", "text": word, "items": " | ".join(gl[:3]), "tags": ";".join(sorted(tagset)),
                    "source": f"https://en.wiktionary.org/wiki/{word.replace(' ', '_')} (CC BY-SA 4.0; via kaikki.org)", "status": "wiktionary"})
print(f"# rows: {n}", file=sys.stderr)
