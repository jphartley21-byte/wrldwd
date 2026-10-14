"""Harvest vocabulary and stock phrases from open sources, for the writers to draw on.

SOURCES AND LICENCES
  en.wiktionary.org  - MediaWiki API, category members. Content is CC BY-SA 4.0; only short
                       headwords and phrases are taken, and the source is recorded per line.
  api.datamuse.com   - related/rhyming words (see research.py, same caching).
Nothing about the song is sent out: the only outbound strings are category names and single
headwords (research.py's _outbound_ok guard applies), and responses are cached so a re-run is
offline and reproducible.

WHY A SEPARATE RAW BANK
Bulk harvests are large and uneven. Curated toolkit/phrases.txt stays the trusted core; this writes
toolkit/phrases_raw.txt, ranked by a recognisability proxy so bank.py can offer the good end of it
first instead of pretending 5,000 entries are all equally usable.

usage:
    python toolkit/harvest.py phrases [--per-cat 3000] [--min-zipf 1.2]
    python toolkit/harvest.py words   [--per-cat 3000]
    python toolkit/harvest.py --selftest        (offline; tests the filters and ranking only)
"""

import argparse
import json
import os
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import craft_scan as cs       # noqa: E402
import rhyme_tools as rt      # noqa: E402
import vocab as vc            # noqa: E402

UA = {"User-Agent": "wrldwd-research/1.0 (personal songwriting project)"}
API = "https://en.wiktionary.org/w/api.php?"
SPARQL = "https://query.wikidata.org/sparql?"
ENTITIES = os.path.join(HERE, "entities.txt")
RAW_PHRASES = os.path.join(HERE, "phrases_raw.txt")
CACHE = os.path.join(tempfile.gettempdir(), "wrldwd_harvest_cache")
SLEEP = 1.0        # Wikimedia asks for a modest request rate; the cache makes re-runs cheap

# Wikidata (CC0): titles and names are facts. Ordering by sitelink count is the popularity proxy,
# so the top of each list is what a 30-something Brit recognises instantly.
ENTITY_QUERIES = {
    "city": ('?item wdt:P31 wd:Q515 .', 600),
    "country": ('?item wdt:P31 wd:Q6256 .', 250),
    "uk-town": ('?item wdt:P31 wd:Q486972 . ?item wdt:P17 wd:Q145 . '
                '?item wdt:P1082 ?pop . FILTER(?pop > 20000)', 500),
    "film-bestpicture": ('?item wdt:P31 wd:Q11424 ; wdt:P166 wd:Q102427 .', 200),
    "film-palme": ('?item wdt:P31 wd:Q11424 ; wdt:P166 wd:Q179808 .', 150),
    "tv": ('?item wdt:P31 wd:Q5398426 .', 600),
    "band": ('?item wdt:P31 wd:Q215380 .', 500),
    # POP CULTURE (Joe, 13 Oct 2026: "all pop culture references"). Every class here was probed before it was added, and
    # only the ones that returned real, correctly-typed items are in. Rejected on that test: video game (Q7889, timed out),
    # album (Q482994, timed out), rapper (Q2252262, timed out), sitcom (Q1511376, returned nothing), footballer (Q937857,
    # returned MATCH REPORTS rather than players) and fictional character (Q95074, returned chemistry terms). A wrong class
    # here is not harmless: it writes nonsense names into the pool that no gate can catch, which is the failure this
    # project has already had twice with substitution.
    "game-series": ('?item wdt:P31 wd:Q7058673 .', 300),
    "brand": ('?item wdt:P31 wd:Q431289 .', 300),
    "meme": ('?item wdt:P31 wd:Q2927074 .', 200),
    # People are an OCCUPATION (P106), not an instance-of: the first attempt used P31 for rapper/footballer/singer and got
    # match reports, albums and chemistry terms. With P106 the same classes return Eminem, Tupac and Will Smith, and
    # Chaplin, Jackie Chan and Robin Williams. Names are TEXTURE for a rhyme slot (rule 5, Joe 11 Oct): never the joke, and
    # never the subject of the menace. footballer/singer/actor time out on this endpoint; they are left out rather than
    # guessed, and the harvest is resumable, so adding them later costs one run.
    "rapper-occ": ('?item wdt:P106 wd:Q2252262 .', 200),
    "comedian-occ": ('?item wdt:P106 wd:Q245068 .', 200),
    "youtuber-occ": ('?item wdt:P106 wd:Q17125263 .', 200),
}

# Categories worth pulling. Proverbs are deliberately out: they are full sentences, not cashable.
CATS_PHRASES = ["English idioms", "English slang", "British English", "English informal terms",
                "English reduplications", "English rhyming compounds", "English colloquialisms",
                "English vulgarities", "English swear words", "English minced oaths",
                "British slang", "English military slang", "English prison slang"]
CATS_WORDS = ["English slang", "British English", "English informal terms", "English vulgarities",
              "English swear words",
              # the domains the song actually lives in (Joe, 13 Oct 2026: slang for drugs, guns and weapons, and money
              # must all be available). These are Wiktionary's topical categories, checked live before being added:
              # en:Drugs, en:Recreational drugs, en:Weapons, en:Firearms, en:Money, en:Crime, en:Prison, en:Violence
              # and en:Prostitution all return members; en:Police, en:Alcohol, en:Cannabis and en:Insults return none.
              "en:Drugs", "en:Recreational drugs", "en:Weapons", "en:Firearms", "en:Money", "en:Crime",
              "en:Prison", "en:Violence", "en:Prostitution", "en:Money", "en:Weapons"]

# Swearing and vulgar slang ARE in the pool and are never discouraged (Joe, 13 Oct 2026: "all swear words and vulgar
# slang should be available to use and never discouraged"). This set is kept only as a LABEL, so a caller can ask for
# the vulgar layer on its own or keep it out of a list it does not want; it no longer drops anything from the harvest or
# from the entity list, which is what it used to do (bitch and dick were missing from it, so 23 and 8 entries walked
# straight through while shit and fuck were silently deleted). See toolkit/README.md, rule 5.
VULGAR = set("""fuck fucked fucking fucks shit shits shitty arse arsehole arseholes bastard bastards bitch bitches
bollocks cunt cunts prick pricks wank wanked wanker wankers twat twats piss pissed pissing dick dicks
motherfucker cocksucker dumbass jackass crap crappy bellend knobhead tosser sodding bugger buggered""".split())

# A phrase must be plain words: no digits, no symbols, no "Unsupported titles/..." artefacts.
CLEAN = re.compile(r"^[a-z][a-z' -]*$")
BAD_BITS = ("unsupported titles", "/", "(", ")", ",", ":", ";", "!", "&", "%", "$", "#", '"')

SENSE_HINTS = [
    ("money", "cash money price rate sum packet tab whack change coin pound tenner fiver quid "
              "pocket debt loan pay paid paid-off wage wages ledger takings till cheap dear"),
    ("admin", "book books paper papers diary order receipt address form file form print stamp "
              "sign signed note list ledger desk office queue letter post mail parcel package"),
    ("travel", "road boat ferry train plane flight mile miles way route border map grid leg "
               "journey luggage baggage ticket toll detour"),
    ("menace", "quiet dark know take make counter table radar fiddle game nod wink word "
               "business lorry back door doors"),
    ("law", "rights bail cell charge heat run cover alibi wrist nick time copper police "
            "cops warrant law"),
    ("time", "time hour minute clock light hour early late chance dot"),
    ("domestic", "kettle bin bins tea garden shed room garage washing dinner kitchen bed missus "
                 "laws mum dad"),
    ("booze", "beer pub pint round rounds orders barrel lash wagon snug bar tab drunk sober brewery"),
    ("food", "brew chips chippy spoon kebab roast roll bread bacon milk tea breakfast dinner"),
    ("lark", "laugh joke mickey banter wind carry muck about"),
    ("weather", "rain raining gale sun drizzle storm cloud wind frost snow"),
    ("mood", "moon face blue wall rails biscuit nose straw drain track clear strings light "
             "frame bag grabs shelf shelf level board belt pickle blink odds cards worse"),
]


def _cache_path(key):
    os.makedirs(CACHE, exist_ok=True)
    safe = re.sub(r"[^a-z0-9]+", "_", key.lower())[:80]
    return os.path.join(CACHE, safe + ".json")


def api_get(params, key, offline=False, tries=5):
    """Cached GET. Caches each page, so a re-run resumes instead of restarting, and backs off on
    the Wikimedia rate limit (429) rather than hammering it."""
    path = _cache_path(key)
    if os.path.exists(path):
        with open(path, encoding="utf8") as fh:
            return json.load(fh)
    if offline:
        return None
    url = API + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
            with open(path, "w", encoding="utf8") as fh:
                json.dump(data, fh)
            time.sleep(SLEEP)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and attempt < tries - 1:
                wait = 3 * (attempt + 1) ** 2
                print(f"    {exc.code} rate limit, waiting {wait}s ...")
                time.sleep(wait)
                continue
            if exc.code == 429:
                print("    still rate limited; re-run later, cached pages will be reused")
                return None
            raise
        except urllib.error.URLError as exc:
            print(f"    network error {exc}; stopping this category")
            return None
    return None


def category_subcats(cat, offline=False, limit=250):
    d = api_get({"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cat,
                 "cmnamespace": "14", "cmlimit": "500", "format": "json"},
                cat + "_sub", offline=offline)
    return [m["title"].split(":", 1)[1]
            for m in (d or {}).get("query", {}).get("categorymembers", [])][:limit]


def category_members_deep(cat, per_cat=800, offline=False, max_subcats=25):
    """Many Wikipedia categories are containers: 'British films' holds only subcategories. One
    level down reaches the actual pages. Bounded, because a container can hold hundreds of
    subcategories and each one costs a request."""
    out = category_members(cat, per_cat=per_cat, offline=offline)
    if out:
        return out
    for sub in category_subcats(cat, offline=offline)[:max_subcats]:
        out += category_members(sub, per_cat=200, offline=offline)
        if len(out) >= per_cat * 2:
            break
    return out


def category_members(cat, per_cat=3000, offline=False):
    """Every page title in a category, paginated, cached."""
    out, cont = [], None
    while len(out) < per_cat:
        params = {"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cat,
                  "cmlimit": "500", "cmnamespace": "0", "format": "json"}
        if cont:
            params["cmcontinue"] = cont
        data = api_get(params, f"{cat}_{cont or 'start'}", offline=offline)
        if not data:
            break
        out += [m["title"] for m in data.get("query", {}).get("categorymembers", [])]
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            break
    return out[:per_cat]


def _zipf(word):
    try:
        from wordfreq import zipf_frequency
        return zipf_frequency(word, "en")
    except Exception:
        return 0.0


def content_words(text):
    return [w for w in text.split() if w not in rt.FUNC]


def recognisability(phrase):
    """Mean commonness of the content words - the proxy for 'a 30-something Brit gets it at once'."""
    cw = content_words(phrase)
    if not cw:
        return 0.0
    return sum(_zipf(w) for w in cw) / len(cw)


def worst_content_word(phrase):
    """The least common content word. A phrase is only as recognisable as its rarest word, which
    is what keeps one-off Wiktionary coinings ("ai notkilleveryoneism") out of the bank."""
    cw = content_words(phrase)
    return min((_zipf(w) for w in cw), default=0.0)


def sense_of(phrase):
    """Keyword tag. Exact tokens score double, so "the last orders" is booze rather than admin."""
    toks = [t for t in re.split(r"[^a-z]+", phrase) if t]
    exact, stemmed = set(toks), {t[:-1] for t in toks if t.endswith("s") and len(t) > 3}
    best, best_hits = "-", 0
    for sense, keys in SENSE_HINTS:
        kw = set(keys.split())
        hits = 2 * len(exact & kw) + len(stemmed & kw)
        if hits > best_hits:
            best, best_hits = sense, hits
    return best


def clean_phrase(p):
    p = p.strip().lower()
    if any(b in p for b in BAD_BITS) or not CLEAN.match(p):
        return None
    words = p.split()
    if not (2 <= len(words) <= 6):
        return None
    if len(p) > 40:
        return None
    if any(w in rt.BANNED for w in words):
        return None
    if len(set(words)) < 2:                   # "last last": degenerate, and it scores high
        return None
    if not content_words(p):                  # a phrase must carry at least one real word
        return None
    return p


def payoff_of(phrase):
    """The last content word that the toolkit can actually measure - it must sit in the rhyme slot."""
    for w in reversed(content_words(phrase)):
        if cs.nuclei(w):
            return w
    return None


def harvest_phrases(per_cat=3000, min_zipf=1.2, offline=False, out=RAW_PHRASES):
    curated = set()
    curated_path = os.path.join(HERE, "phrases.txt")
    if os.path.exists(curated_path):
        with open(curated_path, encoding="utf-8-sig") as fh:
            for line in fh:
                if line.strip() and not line.startswith("#"):
                    curated.add(line.split("|")[0].strip().lower())

    rows, seen = [], set()
    stats = {}
    for cat in CATS_PHRASES:
        titles = category_members(cat, per_cat=per_cat, offline=offline)
        kept = 0
        for t in titles:
            p = clean_phrase(t)
            if not p or p in seen or p in curated:
                continue
            pay = payoff_of(p)
            if not pay:
                continue
            score = recognisability(p)
            if score < min_zipf or worst_content_word(p) < min_zipf:
                continue
            seen.add(p)
            rows.append((p, pay, sense_of(p), cat, round(score, 2)))
            kept += 1
        stats[cat] = (len(titles), kept)
        print(f"  {cat:<28} {len(titles):>5} fetched, {kept:>5} kept")

    rows.sort(key=lambda r: (-r[4], r[0]))
    with open(out, "w", encoding="utf8") as fh:
        fh.write("# Harvested stock phrases. phras|payoff|sense|source category|recognisability\n")
        fh.write("# Source: en.wiktionary.org category members, CC BY-SA 4.0 (short headwords only).\n")
        fh.write("# Ranked by mean wordfreq zipf of the content words - the good end is at the top.\n")
        fh.write("# Curated toolkit/phrases.txt is the trusted core and is NOT duplicated here.\n")
        for r in rows:
            fh.write(" | ".join(str(x) for x in r) + "\n")
    print(f"\nwrote {len(rows)} phrases to {os.path.basename(out)}")
    return rows


def harvest_words(per_cat=3000, offline=False, record=True):
    """Single-word entries -> the vocabulary ledger (the 'grow the vocabulary' mechanism).

    Recorded PER CATEGORY, so the ledger remembers which domain a word came from ("wiktionary:en:Money"): Joe asked for
    the slang of drugs, guns, weapons and money to be available (13 Oct 2026), and a single lumped source tag cannot answer
    "what money words do we have". The ledger merges sources, so a word in two domains keeps both."""
    found, by_cat = [], {}
    for cat in CATS_WORDS:
        kept = []
        for t in category_members(cat, per_cat=per_cat, offline=offline):
            w = t.strip().lower()
            if not re.match(r"^[a-z][a-z' -]*$", w) or " " in w or len(w) < 3 or len(w) > 20:
                continue
            if w in rt.BANNED:
                continue
            found.append(w)
            kept.append(w)
        by_cat[cat] = sorted(set(kept))
        print(f"  {cat:<28} running total {len(found)}")
    found = sorted(set(found))
    print(f"single-word entries: {len(found)}")
    if record:
        for cat, words in by_cat.items():
            vc.record_many(words, source=f"wiktionary:{cat}")
        print("recorded to the vocab ledger")
    return found


def sparql(query, key, offline=False, tries=4):
    """Wikidata SPARQL, cached, with backoff. CC0 data: titles, names and places."""
    path = _cache_path("wd_" + key)
    if os.path.exists(path):
        with open(path, encoding="utf8") as fh:
            return json.load(fh)
    if offline:
        return None
    url = SPARQL + urllib.parse.urlencode({"query": query, "format": "json"})
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.load(resp)
            with open(path, "w", encoding="utf8") as fh:
                json.dump(data, fh)
            time.sleep(SLEEP)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503, 502) and attempt < tries - 1:
                wait = 5 * (attempt + 1) ** 2
                print(f"    {exc.code}, waiting {wait}s ...")
                time.sleep(wait)
                continue
            print(f"    HTTP {exc.code} for {key}; skipping")
            return None
        except Exception as exc:
            # The endpoint drops connections under load (RemoteDisconnected) as well as on
            # genuinely slow queries, so retry a couple of times before giving up.
            if attempt < tries - 1:
                wait = 4 * (attempt + 1)
                print(f"    {type(exc).__name__} on {key}, retry in {wait}s ...")
                time.sleep(wait)
                continue
            print(f"    {type(exc).__name__} for {key}; skipping")
            return None
    return None


def _wd_quick(query, key, offline=False, tries=2):
    """One attempt only, short timeout: this endpoint hangs, and a failed type is not fatal.

    The cache is keyed on the QUERY, not the type name, so correcting a query does not resurrect
    the results of the broken version.
    """
    import hashlib
    qid = hashlib.sha1(query.encode("utf8")).hexdigest()[:10]
    path = _cache_path(f"wd_{key}_{qid}")
    if os.path.exists(path):
        with open(path, encoding="utf8") as fh:
            return json.load(fh)
    if offline:
        return None
    for attempt in range(tries):
        try:
            url = SPARQL + urllib.parse.urlencode({"query": query, "format": "json"})
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.load(resp)
            with open(path, "w", encoding="utf8") as fh:
                json.dump(data, fh)
            return data
        except Exception as exc:
            if attempt < tries - 1:
                time.sleep(5)
                continue
            print(f"    wikidata {key}: {type(exc).__name__} (skipped; other sources cover this type)")
            return None
    return None


# Types the category API covers more reliably than the Wikidata endpoint, which drops connections.
CATS_ENTITIES = {
    "given-name": ["English given names", "English male given names", "English female given names"],
    "surname": ["English surnames", "English-language surnames"],
    "band": ["English rock music groups", "English musical groups", "British music groups"],
    "singer": ["English singers", "English male singers", "English female singers"],
    "uk-town": ["Towns in England", "Towns in Wales", "Towns in Scotland"],
    "film": ["British films", "English-language films"],
    "tv": ["British television series", "English-language television shows"],
}


def _load_entities(path):
    rows, seen = [], set()
    if not os.path.exists(path):
        return rows, seen
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and parts[0] not in seen:
                seen.add(parts[0])
                rows.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return rows, seen


def _ok_name(name, seen=None):
    name = (name or "").strip()
    if not name or len(name) > 28:
        return None
    if seen is not None and name in seen:
        return None
    if not re.match(r"^[A-Za-z][A-Za-z' .-]*$", name):
        return None
    return name


# Wikidata query keys that are all one type of thing for the writers.
TYPE_OF = {"film-bestpicture": "film", "film-palme": "film", "rapper-occ": "person", "comedian-occ": "person",
           "youtuber-occ": "person", "game-series": "game", "meme": "meme"}


def harvest_entities(offline=False, out=ENTITIES):
    """Merges into entities.txt: never throws away a name an earlier run got."""
    rows, seen = _load_entities(out)
    print(f"  {len(rows)} names already banked")

    # Fetch FIRST, replace only on success: deleting before fetching loses a whole type when the
    # endpoint times out (which it does). A re-harvest then also cleans up rows a corrected query
    # previously wrote (the film award query used to return producers, not titles).
    fresh = {}
    for kind, (body, limit) in ENTITY_QUERIES.items():
        q = ("SELECT ?item ?itemLabel WHERE { " + body + " ?item wikibase:sitelinks ?n . "
             "SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". } } "
             f"ORDER BY DESC(?n) LIMIT {limit}")
        data = _wd_quick(q, kind, offline=offline)
        names = []
        if data:
            for b in data.get("results", {}).get("bindings", []):
                nm = _ok_name(b.get("itemLabel", {}).get("value", ""), None)
                if nm:
                    names.append(nm)
        if names:
            fresh[kind] = names

    # Drop the stale rows ONCE per type, not once per query: two queries share a type ("film"),
    # and dropping inside the loop let the second wipe the first.
    stale_types = {TYPE_OF.get(k, k) for k in fresh}
    drop = {r[0] for r in rows if r[1] in stale_types and r[2] == "wikidata-sitelinks"}
    if drop:
        rows = [r for r in rows if r[0] not in drop]
        seen -= drop                       # or the re-add below is skipped as a duplicate

    for kind, names in fresh.items():
        typ = TYPE_OF.get(kind, kind)
        kept = 0
        for nm in names:
            if _ok_name(nm, seen):
                seen.add(nm)
                rows.append((nm, typ, "wikidata-sitelinks"))
                kept += 1
        print(f"  {typ:<12} +{kept:<5} from wikidata" + (f" [{kind}]" if kind != typ else ""))

    for kind, cats in CATS_ENTITIES.items():
        kept = 0
        for cat in cats:
            for title in category_members_deep(cat, per_cat=800, offline=offline):
                nm = _ok_name(title, seen)
                if nm:
                    seen.add(nm)
                    rows.append((nm, kind, cat))
                    kept += 1
        if kept:
            print(f"  {kind:<12} +{kept:<5} from categories")

    measurable = [r for r in rows if cs.nuclei(r[0])]
    with open(out, "w", encoding="utf8") as fh:
        fh.write("# Names for rap: places, given names, surnames, films, TV, music.\n")
        fh.write("# Sources: Wikidata (CC0) ordered by sitelink count, and Wiktionary/Wikipedia\n")
        fh.write("# category members (CC BY-SA 4.0). Format: name | type | source note\n")
        for nm, kind, note in rows:
            fh.write(f"{nm} | {kind} | {note}\n")
    print(f"\nwrote {len(rows)} names to {os.path.basename(out)}; "
          f"{len(measurable)} measurable, {len(rows) - len(measurable)} need an OVR entry")
    return rows


# --- loanwords: the word a place uses for a common idea --------------------------------------
# The original's engine is a word in each place's own language or slang, and this repo had no supply
# for it at all: probing phrases.txt, phrases_raw.txt and entities.txt for the words that engine runs
# on returned only English (cheers, birds, quid, whip, chips). Source: the translations tables of a
# handful of anchor pages on English Wiktionary (CC BY-SA), which carry every language's word in one
# fetch per anchor. Output feeds bank.py, which needs a pronunciation for each word before it can be
# used in the rhyme slot -- see the measurable count harvest_loanwords() prints.
LOANWORDS = os.path.join(HERE, "loanwords.txt")
ANCHORS = ["hello", "goodbye", "thank you", "cheers", "please", "yes", "no", "friend", "brother",
           "man", "woman", "money", "police", "beer", "wine", "water", "dance", "party", "city",
           "road", "love", "good", "food", "beautiful"]
# Wiktionary language codes for the places in material/travel_history.md (Joe's real trips).
LANGS = {"es": "Spain", "pt": "Portugal", "fr": "France", "it": "Italy", "de": "Germany",
         "nl": "Netherlands", "no": "Norway", "sv": "Sweden", "da": "Denmark", "sk": "Slovakia",
         "sl": "Slovenia", "hr": "Croatia", "ar": "Morocco", "th": "Thailand", "vi": "Vietnam",
         "lo": "Laos", "id": "Indonesia", "ga": "Ireland", "jam": "Jamaica", "tr": "Turkey"}
T_TMPL = re.compile(r"\{\{t{1,2}[+*]?\|([a-zA-Z-]+)\|([^}|]+)")
LATIN_WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ'\- ]{2,}")


def wikitext(page, offline=False):
    """The raw wikitext of one page, through api_get so it is cached and rate-limit aware."""
    d = api_get({"action": "query", "prop": "revisions", "rvslots": "main", "rvprop": "content",
                 "titles": page, "format": "json", "formatversion": "2"}, "wt_" + page, offline)
    pages = ((d or {}).get("query") or {}).get("pages") or []
    if not pages or "revisions" not in pages[0]:
        return ""
    slots = pages[0]["revisions"][0].get("slots") or {}
    return (slots.get("main") or {}).get("content") or ""


def parse_translations(text, langs=None):
    """{(lang code, word)} from a Wiktionary translations table, filtered to wanted languages.

    Only the FIRST translation entry per language is kept: Wiktionary ranks the everyday word first
    and then lists synonyms, so taking them all harvests thesaurus entries (the first pass returned
    "means of payment" instead of "money"). Latin script only: a word we cannot write in English
    letters is a word we cannot rhyme.
    """
    langs = LANGS if langs is None else langs
    out, taken = set(), set()
    for line in text.splitlines():
        if not line.lstrip().startswith("*"):
            continue
        for m in T_TMPL.finditer(line):
            code = m.group(1)
            if code in taken:
                continue
            word = m.group(2).split("[")[0].strip().strip(".")
            if code in langs and LATIN_WORD.fullmatch(word) and len(word) > 2:
                taken.add(code)
                out.add((code, word.lower()))
    return out


def harvest_loanwords(offline=False, out=LOANWORDS):
    rows, seen = {}, set()
    for anchor in ANCHORS:
        got = parse_translations(wikitext(anchor, offline))
        for code, word in got:
            if (word, code) in seen:
                continue
            seen.add((word, code))
            rows[(word, code)] = anchor
        print(f"  {anchor}: {len(got)} words in {len(LANGS)} wanted languages")
    with open(out, "w", encoding="utf8") as fh:
        fh.write("# Loanwords for the rhyme slot: the word a place uses for a common idea.\n")
        fh.write("# Sources: English Wiktionary translation tables (CC BY-SA). Rebuilt by\n")
        fh.write("#   python toolkit/harvest.py loanwords [--offline]\n")
        fh.write("# Format:  word | lang code | country | the English idea it renders\n")
        fh.write("# A word is only usable in the rhyme slot once cmudict or OVR knows how to say it;\n")
        fh.write("# run  python toolkit/bank.py check  to list the ones that need a pronunciation.\n#\n")
        for (word, code) in sorted(rows, key=lambda k: (LANGS[k[1]], k[0])):
            fh.write(f"{word} | {code} | {LANGS[code]} | {rows[(word, code)]}\n")
    by_lang = {}
    for (word, code) in rows:
        by_lang[LANGS[code]] = by_lang.get(LANGS[code], 0) + 1
    print("\nloanwords.txt:", len(rows), "words across", len(by_lang), "countries")
    print("  ", ", ".join(f"{c} {n}" for c, n in sorted(by_lang.items(), key=lambda kv: -kv[1])[:10]))
    return rows


def selftest():
    """Offline: the filters, the payoff picker and the sense tagger."""
    ok = True
    cases = [
        ("clean_phrase accepts a real phrase", clean_phrase("On The Slate") == "on the slate"),
        ("clean_phrase drops digits", clean_phrase("$100 hamburger") is None),
        ("clean_phrase drops ampersands", clean_phrase("&c") is None),
        ("clean_phrase drops artefacts", clean_phrase("Unsupported titles/`num`MeToo") is None),
        ("clean_phrase drops one-word entries", clean_phrase("007") is None),
        ("clean_phrase drops banned words", clean_phrase("neon dreams") is None),
        ("payoff skips function words", payoff_of("in the know") == "know"),
        ("payoff is None when nothing is measurable", payoff_of("zzz qqq") is None),
        ("sense: money", sense_of("cash in hand") == "money"),
        ("sense: booze", sense_of("the last orders") == "booze"),
        ("recognisability ranks a common phrase above a rare one",
         recognisability("on the house") > recognisability("ultracrepidarian floccinaucity")),
    ]
    fixture = ("* Spanish: {{t+|es|hola}}, {{t|es|buenas noches}}\n"
               "* French: {{t+|fr|bonjour}}\n"
               "* English: {{t+|en|hello}}\n"
               "* Russian: {{t+|ru|privet}}\n"
               "* Jamaican Creole: {{t|jam|wah gwaan}}\n"
               "* Spanish: {{t+|es|a}}\n")
    got = parse_translations(fixture)
    cases += [
        ("loanwords: the wanted language is picked", ("es", "hola") in got),
        ("loanwords: only the first word per language is kept", ("es", "buenas noches") not in got),
        ("loanwords: a multi-word greeting is kept", ("jam", "wah gwaan") in got),
        ("loanwords: English is not a loanword", not any(c == "en" for c, _ in got)),
        ("loanwords: a one-letter word is dropped", not any(w == "a" for _, w in got)),
        ("loanwords: unknown languages are dropped", not any(c == "ru" for c, _ in got)),
    ]
    for name, good in cases:
        if not good:
            ok = False
            print(f"  FAIL {name}")
    print("HARVEST SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("phrases")
    p.add_argument("--per-cat", type=int, default=3000)
    p.add_argument("--min-zipf", type=float, default=1.2)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--out", default=RAW_PHRASES)
    w = sub.add_parser("words")
    w.add_argument("--per-cat", type=int, default=3000)
    w.add_argument("--offline", action="store_true")
    e = sub.add_parser("entities")
    e.add_argument("--offline", action="store_true")
    e.add_argument("--out", default=ENTITIES)
    lw = sub.add_parser("loanwords")
    lw.add_argument("--offline", action="store_true")
    lw.add_argument("--out", default=LOANWORDS)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.cmd == "phrases":
        harvest_phrases(a.per_cat, a.min_zipf, a.offline, a.out)
    elif a.cmd == "words":
        harvest_words(a.per_cat, a.offline)
    elif a.cmd == "entities":
        harvest_entities(a.offline, a.out)
    elif a.cmd == "loanwords":
        harvest_loanwords(a.offline, a.out)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
