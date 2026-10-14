"""research.py - one command for the four kinds of material a bar needs, so looking things up is the
default move rather than a last resort. Everything it finds is a CANDIDATE: facts still come from
material/ or get tagged (invented)/(persona), and any line still has to pass the gates.

  python toolkit/research.py word WORD          pronunciation stack: cmudict, britfone, our overrides,
                                                syllable pattern, and whether the file lacks it
  python toolkit/research.py rhymes WORD        perfect / near / assonance candidates from the local
                                                dictionary AND Datamuse (online)
  python toolkit/research.py sounds WORD        Datamuse sounds-like (slang, spellings, homophones)
  python toolkit/research.py mine QUERY         greps Joe's own material: travel history, place
                                                specifics (photo/video descriptions), sound families
  python toolkit/research.py slang WORD         online slang/meaning lookup (Wiktionary)

Finds COMPOUND now: every lookup is written to the vocab ledger (toolkit/vocab.py) with a G2
recognisability verdict, online results are cached so a repeated query costs nothing, and the
candidates are banked for later. `--refresh` forces a fresh network call; `--dry` records nothing.
G2 is a PROXY and biased: wordfreq is US-weighted (it scores "skint", "winnebago" as rare), so the
verdict prompts Joe's ear and never vetoes a word on its own.

ONLINE BOUNDARY: only a headword of <= 3 words ever leaves this machine (a bar is >= 4 words, so a
lyric line cannot be sent even by accident). `mine` is entirely local - that is the path for Joe's
personal material. See toolkit/vocab.py.

Joe's photos and videos are already digested into material/place_specifics.md and
material/travel_history.md - `mine` is how to use them; it is a keyword search over those files.
"""
import io
import os
import private_path
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

import craft_scan as cs          # noqa: E402
import helpers as h              # noqa: E402
import rhyme_tools as rt         # noqa: E402
import vocab as vc               # noqa: E402

MAT = ["travel_history.md", "place_specifics.md", "place_sound_families.md"]

UA = {"User-Agent": "wrldwd-research/1.0 (personal songwriting project)"}
MAX_OUTBOUND_WORDS = 3
DRY = False                      # set by --dry: look things up but record nothing


def _outbound_ok(q):
    q = q.strip()
    return 1 <= len(q.split()) <= MAX_OUTBOUND_WORDS and "\n" not in q and len(q) <= 40


def get_json(url, query=None):
    if query is not None and not _outbound_ok(query):
        sys.exit(f"refusing to send more than {MAX_OUTBOUND_WORDS} words to a third party "
                 f"({len(query.split())} given): only a headword may leave this machine. "
                 f"Use `mine` for local material/ lookups.")
    try:
        req = urllib.request.Request(url, headers=UA)   # Wikimedia answers 403 without a UA
        return json_load(urllib.request.urlopen(req, timeout=20).read())
    except Exception as e:                                     # noqa: BLE001
        return {"_error": str(e)}


def json_load(b):
    import json
    return json.loads(b.decode("utf8", "replace"))


def word(w):
    import flow_fit as ff
    ph = rt.pron(w)
    brit = cs.brit_phones(w)
    pat = "".join("w" if x else "S" for x in ff.sylls(w))
    print(f"{w}: cmudict {ph or 'NOT FOUND'} | british {brit or 'not in britfone'} | "
          f"our overrides {'yes' if w.lower() in rt.OVR or w.lower() in cs.BRIT_OVR else 'no'}")
    if ph or brit:
        print(f"   {len(ff.sylls(w))} syl, pattern {pat}")
    print(f"   in the original's own lines? {'yes' if w.lower() in ORIG_WORDS else 'no'} "
          f"(rule 5: a shared common word is fine, a shared phrase is not)")
    r = vc.info(w)
    print(f"   G2: zipf {r['zipf']} -> {r['g2']} | tail {r['end_tail']} | family {r['family']}")
    if not DRY:
        vc.record(w, source="word", facts=r)


ORIG_WORDS = set()


def load_orig_words():
    p = private_path.original_path()
    if os.path.exists(p):
        for line in io.open(p, encoding="utf8"):
            ORIG_WORDS.update(w.lower().strip(",.?!") for w in line.split())


def rhymes(w, mode="rhy", refresh=False):
    key = {"rhy": "rel_rhy", "near": "rel_nry", "sounds": "sl"}[mode]
    url = f"https://api.datamuse.com/words?{key}={urllib.request.quote(w)}&md=fs&max=60"
    cached = None if refresh else vc.cached_online(w, mode)
    data = None
    if cached:
        print(f"online ({mode}) for '{w}': (from the ledger - {len(cached)} cached, no network call)")
        for item in cached:
            if isinstance(item, list):
                print(f"   {item[0]:<18} score {item[1]}")
    else:
        data = get_json(url, w)
        print(f"online ({mode}) for '{w}':")
        if isinstance(data, dict):
            print("   offline or error:", data.get("_error", "?"))
        else:
            for d in data[:25]:
                print(f"   {d.get('word'):<18} score {d.get('score')}")
        if not DRY and not isinstance(data, dict):
            vc.cache_online(w, mode, [[d.get("word"), d.get("score")] for d in data[:25]])
    if not DRY:
        # bank the candidates so research compounds; structural junk is dropped, real words are kept
        if not isinstance(data, dict) and data:
            n = vc.record_many([d.get("word") for d in data[:25]], source=f"rhyme-cand:{mode}")
            if n:
                print(f"   banked {n} candidates in the vocab ledger "
                      f"(`python toolkit/vocab.py show`)")
        vc.record(w, source=f"rhymes:{mode}")
    print(f"local dictionary ({mode}) for '{w}':")
    ph = rt.pron(w)
    if not ph:
        print("   not in cmudict or the overrides - add it to OVR to use it in a rhyme")
        return
    try:
        mode2 = {"rhy": "perfect", "near": "near", "sounds": "near"}[mode]
        k = rt.key(ph, n=2, mode=mode2)
        hits = []
        for item in rt.index(2, mode2):
            x = item if isinstance(item, str) else (item[0] if item else "")
            if not isinstance(x, str):
                continue
            px = rt.pron(x)
            if px and rt.key(px, n=2, mode=mode2) == k and x != w:
                hits.append(x)
        print("   " + ", ".join(hits[:20]) if hits else "   no local candidates")
    except Exception as e:                                     # noqa: BLE001
        print("   local lookup skipped:", e)


def mine(q):
    pat = re.compile(re.escape(q), re.I)
    for f in MAT:
        p = os.path.join(REPO, "material", f)
        if not os.path.exists(p):
            continue
        for i, line in enumerate(io.open(p, encoding="utf8"), 1):
            if pat.search(line):
                print(f"{f}:{i}: {line.strip()[:180]}")


def slang(w):
    url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{urllib.request.quote(w)}"
    data = get_json(url, w)
    if not isinstance(data, dict) or "_error" in data:
        print("lookup failed:", data.get("_error") if isinstance(data, dict) else data)
        return
    for lang, senses in list(data.items())[:1]:
        for s in senses[:1]:
            for d in s.get("definitions", [])[:4]:
                txt = re.sub("<[^>]+>", "", d.get("definition", ""))
                print(f"   {txt[:160]}")
    if not DRY:
        vc.record(w, source="slang")


def main():
    global DRY
    load_orig_words()
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    if "--dry" in a:
        DRY = True
        a = [x for x in a if x != "--dry"]
    refresh = "--refresh" in a
    a = [x for x in a if x != "--refresh"]
    cmd = a[0]
    if cmd == "word":
        word(a[1])
    elif cmd == "rhymes":
        rhymes(a[1], "rhy", refresh)
    elif cmd == "near":
        rhymes(a[1], "near", refresh)
    elif cmd == "sounds":
        rhymes(a[1], "sounds", refresh)
    elif cmd == "mine":
        mine(" ".join(a[1:]))
    elif cmd == "slang":
        slang(" ".join(a[1:]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
