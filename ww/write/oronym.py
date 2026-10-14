"""Oronyms: re-segment a name or phrase into OTHER words that sound identical in a British accent, preferring readings that hide loaded slang.

  python -m ww.cli oronym "Captain America" --loaded     ->  capped in America  [capped = shot]
  python -m ww.cli oronym "ice cream"                    ->  I scream
  python -m ww.cli puns --q america                      ->  the mined bank of names that hide a loaded reading

How it works: the target's British phones (stress marks removed) are cut into every sequence of dictionary words whose phones match exactly
(wordfreq's 40,000 commonest words plus the loaded-slang list), scored by word commonness, with a bonus for each loaded word and a penalty per word.
Why it matters: the original's best sound-play hides a second, darker or cheekier reading inside a well-known sound (a place against a word, a
name against a phrase). The listener hears the NAME first and the loaded phrase a beat later, so it only works when the name is famous, the
loaded reading is something the narrator's world could say (shot, nicked, banged up, bribed, done), and the bar gives no hint. Use one per section.
"""
from __future__ import annotations

import re
from functools import lru_cache

from .. import bridge
from . import wordplay

# loaded slang the narrator's world can say (single words and short phrases); the lexicon's 'loaded' group adds hundreds more
SEED_LOADED = """capped merked nicked bagged shot stabbed killed dead banged jailed robbed mugged shanked grassed cuffed fined bust busted bribed bribe
bang bangs done dusted sorted stitched jacked clipped cooked burnt peeled cut lifted slammed sent down brown bread bundled rinsed shook strapped
tooled wedge graft grafting dibble plod peeler pinched collared fitted framed nabbed snitched ratted squealed topped offed whacked smacked slapped
smashed trashed rolled robbed fenced laundered scammed conned fleeced diddled swindled rumbled twoc nick nicking inside bird porridge stir bang up
cash dosh bread bees funds skint broke owed owe debt cheque bounced bounce bail fine jail cell warrant arrest caution charge charged""".split()


STRONG_KINDS = {"violence", "theft", "drugs", "police", "threat", "prison", "death"}
# everyday words that read as loaded only in context: they would fire on half the dictionary
WEAK_LOADED = set("""owe cut cash bread done sorted cell charge fine bang dust nick inside bird stir bail bust cook cooked burnt cut lifted rolled
funds broke owed debt bounce cheque warrant caution arrest bees dosh wedge graft stitched rinsed shook bang bangs""".split())


@lru_cache(maxsize=1)
def _loaded() -> dict[str, float]:
    words = {w.lower(): 1.0 for w in SEED_LOADED if w.lower() not in WEAK_LOADED}
    try:
        from ..lex import lexicon
        for r in lexicon.load():
            if r["group"] == "loaded" and not r.get("avoid") and r.get("kind") in STRONG_KINDS:
                t = re.sub(r"[^a-z' ]", "", r["text"].lower()).strip()
                if t and len(t.split()) <= 3 and t not in WEAK_LOADED and len(t) >= 4:
                    words[t] = 1.0
    except Exception:    # noqa: BLE001 - lexicon is optional
        pass
    return words


@lru_cache(maxsize=1)
def _index() -> tuple[dict, int]:
    """exact phone-sequence index: tuple(phones) -> [(word, zipf, loaded)] over common words and loaded slang."""
    import wordfreq
    from .. import bridge as _b
    _b._toolkit_on_path()
    import rhyme_tools as rt
    idx: dict = {}
    longest = 1
    junk = set("mm hmm hm er um uh ah ahh oh ohh eh ai aye au kr yr ir ar el en em es ex ed ll ve re nt opp ou ay sh ee ess ell jay kay dee gee tee bee pee cue are ewe".split())
    two_ok = set("am an as at be by do go he hi if in is it me my no of oh ok on or so to up us we".split())
    words = list(wordplay._vocab()) + [("a", wordplay._strip(_b.phones("a") or []), 7.0), ("i", wordplay._strip(_b.phones("i") or []), 7.0)]
    for w, ph, z in words:
        if len(ph) == 0 or w in junk or z < 3.3 or (len(w) == 1 and w not in ("a", "i")) or (len(w) == 2 and w not in two_ok):
            continue
        if w not in ("a", "i") and w not in rt.D:     # real dictionary words only: no fragments, initials or names that merely have a spelling
            continue
        idx.setdefault(ph, []).append((w, z, False))
        longest = max(longest, len(ph))
    for lw in _loaded():
        ph = wordplay.phones_of(lw)
        if not ph:
            continue
        # a loaded single word or phrase is indexed as ONE unit, so its words stay together in the reading
        z = wordfreq.zipf_frequency(lw, "en") or 2.5
        idx.setdefault(ph, []).append((lw, max(z, 2.6), True))
        longest = max(longest, len(ph))
    return idx, longest


def segmentations(text: str, loaded_only: bool = False, n: int = 12, max_words: int | None = None) -> list[dict]:
    tgt = wordplay.phones_of(text)
    if not tgt:
        return []
    idx, longest = _index()
    orig = [t.lower() for t in re.findall(r"[A-Za-z']+", bridge.norm(text))]
    cap = max_words or (len(orig) + 3)
    L = len(tgt)
    # best[i] = list of (score, words, nloaded) for prefixes ending at i
    best: list[list] = [[] for _ in range(L + 1)]
    best[0] = [(0.0, [], 0)]
    K = 40
    for i in range(L):
        if not best[i]:
            continue
        for ln in range(1, min(longest, L - i) + 1):
            seg = tgt[i:i + ln]
            hits = idx.get(seg)
            if not hits:
                continue
            for w, z, ld in hits:
                for sc, ws, nl in best[i]:
                    if len(ws) + (len(w.split()) if ld else 1) > cap + 2:
                        continue
                    add = (z - 3.0) * 0.35 - 0.8 + (2.5 if ld else 0.0)
                    best[i + ln].append((sc + add, ws + [w], nl + (1 if ld else 0)))
        for j in range(i + 1, min(L, i + longest) + 1):
            if len(best[j]) > K:
                best[j] = sorted(best[j], key=lambda t: -t[0])[:K]
    out, seen = [], set()
    for sc, ws, nl in sorted(best[L], key=lambda t: -t[0]):
        reading = " ".join(ws)
        flat = reading.split()
        if flat == orig or reading in seen:
            continue
        if loaded_only and nl == 0:
            continue
        if loaded_only:
            lw = [w for w in _loaded() if w in reading and w not in orig and not any(w in o or o in w for o in orig)]
            if not lw:        # the loaded word must be NEW: a name that already contains the word hides nothing
                continue
        # skip readings that are just the original words (possibly with a loaded synonym): need at least one word not in the original
        if all(w in orig for w in flat):
            continue
        seen.add(reading)
        out.append({"reading": reading, "loaded": nl, "score": round(sc, 2)})
        if len(out) >= n:
            break
    return out


def report(text: str, loaded_only: bool = False, n: int = 12) -> str:
    res = segmentations(text, loaded_only, n)
    if not res:
        return f"no {'loaded ' if loaded_only else ''}re-segmentation of '{text}' found (exact British phones; try without --loaded)"
    return f"READINGS that sound like '{text}' (British accent, exact phones):\n" + "\n".join(f"  {r['reading']:40s} {'[loaded x%d]' % r['loaded'] if r['loaded'] else ''}" for r in res)


def scan(texts: list[str], loaded_only: bool = True, per: int = 2) -> list[dict]:
    rows = []
    for t in texts:
        if len(t) > 40 or len(re.findall(r"[A-Za-z']+", t)) > 4:
            continue
        for r in segmentations(t, loaded_only, per):
            rows.append({"name": t, **r})
    return rows


def selftest() -> tuple[bool, str]:
    problems = []
    r = [x["reading"] for x in segmentations("Captain America", loaded_only=True, n=20)]
    if not any("capped in" in x for x in r):
        problems.append(f"'Captain America' should hide 'capped in America': {r[:8]}")
    r2 = [x["reading"] for x in segmentations("ice cream", n=20)]
    if not any(x == "i scream" for x in r2):
        problems.append(f"'ice cream' should read as 'I scream': {r2[:8]}")
    return (not problems, "; ".join(problems) if problems else "Captain America -> capped in America and ice cream -> I scream both found")


def build_bank(groups=("brand", "media", "place", "pop", "role", "prop", "slang", "pun"), limit_words: int = 4) -> dict:
    """scan every lexicon name and the entity bank for a loaded hidden reading; write them back as lexicon rows of group 'hidden'."""
    import sys
    from .. import config
    from ..lex import lexicon
    rows = lexicon.load()
    texts = {}
    for r in rows:
        if r["group"] in groups and not r.get("avoid"):
            texts[r["text"]] = r["group"]
    sys.path.insert(0, str(config.TOOLKIT))
    import bank
    for e in bank.load_entities():
        if e["type"] in ("city", "uk-town", "country", "tv", "band", "film"):
            texts.setdefault(e["name"], e["type"])
    found = []
    for t, g in texts.items():
        if len(re.findall(r"[A-Za-z']+", t)) > limit_words or len(t) > 36:
            continue
        for r in segmentations(t, loaded_only=True, n=1):
            found.append({"text": t, "reading": r["reading"], "src": g})
    have = {(r["group"], lexicon.norm_text(r["text"])) for r in rows if r["group"] == "hidden"}
    new = []
    for f in found:
        k = ("hidden", lexicon.norm_text(f["text"]))
        if k in have:
            continue
        have.add(k)
        new.append({"text": f["text"], "group": "hidden", "cat": "hidden", "kind": f["src"], "country": "", "gloss": "sounds like: " + f["reading"], "say": "",
                    "extra": f"reading: {f['reading']}", "avoid": False})
    lexicon.save(rows + new)
    return {"scanned": len(texts), "found": len(found), "added": len(new)}
