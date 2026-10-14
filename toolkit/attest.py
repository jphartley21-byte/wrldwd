"""attest: does this phrase actually exist in real English? -- MEASURED AND REJECTED AS A GATE.

The gates cannot see sense. meaning_gate asks whether a bar HAS content (a noun list supplies images,
so "Two glasses, cold lager, back road corners" passed it) and whether its end word is a function
word, not whether the words belong together.

So this tool was built to catch exactly that, by counting exact occurrences of a bar's head and tail
four-word phrases on Wikipedia (insource, cached, rate-limit aware). It was then measured on known
material, and it does not discriminate:

  * flags the gibberish: "None of the names on the quarters" 0 hits, "A page of the orders and the
    corners" 0 hits, "Hallo and the boat in Oslo" 0 hits
  * flags good lines just as hard: Joe's approved "Front row at the on-stage porno" 0 hits (tail),
    "Paid him by the weight" 0 hits, "Might take the ferry to Bergen" 0 hits

Reason: the tail of a bar is usually a clause boundary, not an idiom, so a legitimate line scores
zero, while a common filler head such as "a page of the" scores in the hundreds. The score tracks
whether the phrase is a dictionary idiom, not whether the bar means anything.

Kept because the negative result is worth as much as a positive one, and because the CLI is a cheap
way to settle a phrase by hand. REPORT ONLY, and not to be trusted in either direction.

  python toolkit/attest.py "a page of the orders"
  python toolkit/attest.py --bars FILE [--offline]
  python toolkit/attest.py --selftest
"""
import argparse
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "wrldwd-research/1.0 (personal songwriting project)"}
API = "https://en.wikipedia.org/w/api.php"
CACHE = os.path.join(tempfile.gettempdir(), "wrldwd_attest_cache")
SLEEP = 0.6
N = 4


def _cache_path(key):
    os.makedirs(CACHE, exist_ok=True)
    return os.path.join(CACHE, re.sub(r"[^a-z0-9]+", "_", key.lower())[:90] + ".json")


def hits(phrase, offline=False, tries=3):
    """Exact-occurrence count for a phrase on Wikipedia, cached, with backoff."""
    phrase = phrase.strip().lower()
    if not phrase:
        return None
    path = _cache_path("hr_" + phrase)
    if os.path.exists(path):
        with open(path, encoding="utf8") as fh:
            return json.load(fh).get("hits")
    if offline:
        return None
    url = API + "?" + urllib.parse.urlencode({
        "action": "query", "list": "search", "srsearch": f'insource:"{phrase}"',
        "srlimit": "1", "format": "json", "formatversion": "2"})
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
            got = ((data.get("query") or {}).get("searchinfo") or {}).get("totalhits")
            with open(path, "w", encoding="utf8") as fh:
                json.dump({"phrase": phrase, "hits": got}, fh)
            time.sleep(SLEEP)
            return got
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and attempt < tries - 1:
                time.sleep(3 * (attempt + 1) ** 2)
                continue
            return None
        except urllib.error.URLError:
            return None
    return None


def key_phrases(bar, n=N):
    """The n-grams worth asking about: the opening phrase and the tail (the rhyme slot)."""
    words = re.findall(r"[A-Za-z']+", bar.lower())
    if not words:
        return []
    if len(words) <= n:
        return [" ".join(words)]
    head, tail = " ".join(words[:n]), " ".join(words[-n:])
    return [head] if head == tail else [head, tail]


def check(bars, offline=False):
    rows = []
    for b in bars:
        ph = key_phrases(b)
        hs = [hits(p, offline) for p in ph]
        known = [h for h in hs if h is not None]
        rows.append({"bar": b, "phrases": ph, "hits": hs,
                     "worst": min(known) if known else None})
    return rows


def report(bars, offline=False, floor=1):
    rows = check(bars, offline)
    print(f"{'hits':>7}  bar")
    for r in rows:
        mark = "  <-- not attested" if (r["worst"] is not None and r["worst"] < floor) else ""
        print(f"{(r['worst'] if r['worst'] is not None else '?'):>7}  {r['bar']}{mark}")
        if r["worst"] is not None and r["worst"] < floor:
            for p, h in zip(r["phrases"], r["hits"]):
                print(f"         {h if h is not None else '?'} hits: \"{p}\"")
    bad = [r for r in rows if r["worst"] is not None and r["worst"] < floor]
    print(f"\n{len(bad)} of {len(rows)} bars contain a phrase with no attestation on Wikipedia")
    return rows


def selftest():
    """Offline: the phrase picker and the cache key, which is all that can be tested without network.

    The expectations here are the actual n-grams, not the ones I assumed: a bar's tail is often a
    clause boundary, which is why this tool can only ever report and never veto.
    """
    ok = True
    checks = [
        ("head and tail are both tested",
         key_phrases("a page of the orders and the corners") == ["a page of the", "orders and the corners"]),
        ("a bar of four words or fewer is tested whole", key_phrases("Paid him the weight") == ["paid him the weight"]),
        ("the tail is the rhyme slot",
         key_phrases("None of the names on the quarters")[-1] == "names on the quarters"),
        ("punctuation does not break the key", key_phrases("Ola, and the lot on the spot")[0] == "ola and the lot"),
        ("an empty bar yields nothing", key_phrases("   ") == []),
        ("the cache key is filesystem safe", "/" not in _cache_path("hr_a b/c")),
    ]
    for name, good in checks:
        if not good:
            ok = False
            print(f"  FAIL {name}")
    print("ATTEST SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phrase", nargs="?")
    ap.add_argument("--bars")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--floor", type=int, default=1)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.bars:
        bars = [l.strip() for l in open(a.bars, encoding="utf-8-sig")
                if l.strip() and not l.startswith(("#", "-", "["))]
        report(bars, a.offline, a.floor)
        return 0
    if a.phrase:
        for p in key_phrases(a.phrase):
            print(f"{hits(p, a.offline)} hits: \"{p}\"")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
