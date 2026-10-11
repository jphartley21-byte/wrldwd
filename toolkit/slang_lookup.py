"""slang_lookup: on-demand lookup of a slang word from Wiktionary (via kaikki.org per-word data) and Urban Dictionary. HINTS ONLY.
  python toolkit/slang_lookup.py certi plod "federali"       # prints candidates; caches to bank/slang_cache.json
  python toolkit/slang_lookup.py --add certi                  # also appends the best Wiktionary/UD gloss to bank/slang.csv as status 'hint (unverified)'
Order of trust: Joe's own correction > Wiktionary (cited, has UK/slang tags) > Urban Dictionary (crowd-sourced, noisy, vote-weighted).
Urban Dictionary: unofficial public endpoint, per-word only (no bulk scraping, cache 1 entry per word). Wiktionary text is CC BY-SA 4.0 (attribute).
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
CACHE = os.path.join(ROOT, "bank", "slang_cache.json")
UA = {"User-Agent": "wrldwd-lyrics-research/0.1 (private songwriting repo)"}


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def kaikki(word):
    w = word.lower().replace(" ", "_")
    a = w[0]; b = w[:2] if len(w) > 1 else w[0]
    url = f"https://kaikki.org/dictionary/English/meaning/{urllib.parse.quote(a)}/{urllib.parse.quote(b)}/{urllib.parse.quote(w)}.jsonl"
    try:
        txt = get(url)
    except Exception as e:
        return []
    out = []
    for line in txt.splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        for s in d.get("senses", []):
            g = (s.get("glosses") or [""])[-1]
            if g:
                out.append({"gloss": g[:200], "tags": s.get("tags", []), "pos": d.get("pos", "")})
    return out[:6]


def urban(word):
    try:
        d = json.loads(get("https://api.urbandictionary.com/v0/define?term=" + urllib.parse.quote(word)))
    except Exception:
        return []
    items = sorted(d.get("list", []), key=lambda x: -(x.get("thumbs_up", 0) - x.get("thumbs_down", 0)))
    clean = lambda t: re.sub(r"[\[\]]", "", t or "").replace("\r", " ").replace("\n", " ")[:220]
    return [{"definition": clean(x["definition"]), "example": clean(x.get("example", "")), "votes": x.get("thumbs_up", 0) - x.get("thumbs_down", 0)} for x in items[:3]]


def lookup(word, use_cache=True):
    cache = json.load(open(CACHE, encoding="utf8")) if os.path.exists(CACHE) else {}
    key = word.lower()
    if use_cache and key in cache:
        return cache[key]
    res = {"word": word, "wiktionary": kaikki(word), "urban": urban(word), "when": time.strftime("%Y-%m-%d")}
    cache[key] = res
    json.dump(cache, open(CACHE, "w", encoding="utf8"), ensure_ascii=False, indent=0)
    time.sleep(0.5)
    return res


def show(res):
    print(f"== {res['word']}")
    for s in res["wiktionary"][:3]:
        print(f"  [wiktionary{' ' + ','.join(s['tags']) if s['tags'] else ''}] {s['gloss']}")
    for u in res["urban"][:2]:
        print(f"  [urban dictionary, {u['votes']:+d} votes] {u['definition']}")
    if not res["wiktionary"] and not res["urban"]:
        print("  (nothing found: ask Joe)")


def main():
    a = sys.argv[1:]
    add = "--add" in a
    words = [x for x in a if not x.startswith("--")]
    for w in words:
        r = lookup(w); show(r)
        if add:
            gloss = (r["wiktionary"][0]["gloss"] if r["wiktionary"] else (r["urban"][0]["definition"] if r["urban"] else ""))
            if gloss:
                p = os.path.join(ROOT, "bank", "slang.csv")
                rows = list(csv.DictReader(open(p, encoding="utf8"))); f = list(rows[0].keys())
                if not any(x["text"].lower() == w.lower() for x in rows):
                    rows.append({k: "" for k in f} | {"id": "hint_" + w, "type": "slang_hint", "text": w, "items": gloss, "source": "wiktionary/urban dictionary lookup " + r["when"], "status": "hint (unverified)"})
                    with open(p, "w", encoding="utf8", newline="") as fh:
                        wr = csv.DictWriter(fh, f); wr.writeheader(); wr.writerows(rows)
                    print("  -> added as hint to bank/slang.csv")


if __name__ == "__main__":
    main()
