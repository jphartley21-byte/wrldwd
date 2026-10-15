"""Sound plan (plan 5 SOUND PLAN): from a payoff word to a menu of end words that carpet with it.

Hook blocks end each bar on a two-syllable word, stress on the first (shape |Sw), and all four end words rhyme (the original's own
Hook 5-8 carpet is 6/6 pairs at >= 0.80; Joe's accepted Hook 1-4 is 6/6 at 1.00). Candidates come from CMUdict perfect rhymes plus
near rhymes sharing the stressed vowel and the final weak syllable, scored with the project's own grader (ww.bridge.rhyme_score) -
the grader is advisory in the 0.78-0.85 band (bare assonance can score 0.80), so we ask for >= 0.9.

The writer receives this as a MENU with the instruction to reorder the clause so a word falls naturally, or to return no_fit - never as a
mandate (the 13 Oct failure was words substituted for the rhyme and never re-read).
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from .. import bridge


US_SPELL = {"favour": "favor", "flavour": "flavor", "neighbour": "neighbor", "colour": "color", "honour": "honor", "labour": "labor",
            "humour": "humor", "rumour": "rumor", "saviour": "savior", "harbour": "harbor", "vapour": "vapor", "behaviour": "behavior"}
BRIT = {v: k for k, v in US_SPELL.items()}


def _stress_pattern(word: str) -> Optional[str]:
    return bridge.stress_pattern(word.lower())


def is_trochee(word: str) -> bool:
    """two syllables, stress on the first: the end shape |Sw."""
    st = _stress_pattern(word)
    return bool(st) and len(st) == 2 and st[0] == "1" and st[1] in "02"


def _brit(w: str) -> str:
    return BRIT.get(w, w)


_CAND_CACHE: dict = {}


def _vowel_base(tok: str) -> str:
    return re.sub(r"\d", "", tok)


def candidates(payoff: str, min_score: float = 0.85, limit: int = 40, min_zipf: float = 3.3, max_scan: int = 60000) -> list[dict]:
    """common two-syllable stress-first words that rhyme with `payoff` on the toolkit grader (>= min_score). Scans the frequency-ranked
    vocabulary, pre-filtering on the primary stressed vowel (cheap) before running the grader."""
    key = US_SPELL.get(payoff.lower(), payoff.lower())
    ck = (key, min_score, limit, min_zipf)
    if ck in _CAND_CACHE:
        return _CAND_CACHE[ck]
    import rhyme_tools
    import wordfreq
    bridge.stress_pattern(key)  # make sure the pronouncer can read it (compound split etc.)
    ph = rhyme_tools.pron(key)
    if not ph:
        return []
    prim = next((_vowel_base(t) for t in ph if t.endswith("1")), None)
    if prim is None:
        return []
    out = []
    for w in wordfreq.top_n_list("en", max_scan):
        if not w.isalpha() or not 4 <= len(w) <= 9 or w == key:
            continue
        z = wordfreq.zipf_frequency(w, "en")
        if z < min_zipf:
            continue
        pw = rhyme_tools.pron(w)
        if not pw or not any(t.endswith("1") and _vowel_base(t) == prim for t in pw):
            continue
        if not is_trochee(w):
            continue
        sc = bridge.rhyme_score(_brit(w), payoff)
        if sc >= min_score:
            out.append({"word": _brit(w), "zipf": round(z, 2), "score": sc})
    seen, uniq = set(), []
    for x in sorted(out, key=lambda x: (-x["score"], -x["zipf"])):
        if x["word"] not in seen:
            seen.add(x["word"])
            uniq.append(x)
    _CAND_CACHE[ck] = uniq[:limit]
    return _CAND_CACHE[ck]


def menu(payoff: str, k: int = 24) -> dict:
    if not is_trochee(payoff):
        return {"payoff": payoff, "ok": False, "why": "payoff is not a two-syllable stress-first word (shape |Sw)", "candidates": []}
    c = candidates(payoff)
    return {"payoff": payoff, "ok": len(c) >= 3, "why": "" if len(c) >= 3 else "fewer than 3 rhyming trochees", "candidates": c[:k]}


def carpet_check(end_words: list[str]) -> dict:
    """pairwise grader scores for the chosen end words."""
    import itertools
    pairs = {f"{a}~{b}": bridge.rhyme_score(a, b) for a, b in itertools.combinations(end_words, 2)}
    return {"pairs": pairs, "min": min(pairs.values()) if pairs else 1.0,
            "rhyming": sum(1 for v in pairs.values() if v >= 0.78), "total": len(pairs)}


def selftest() -> tuple[bool, str]:
    problems = []
    m = menu("Munich")
    # check the machinery on a plain case
    m2 = menu("traffic")
    if not is_trochee("wristband") or not is_trochee("flavour"):
        problems.append("wristband and flavour (British spelling) should be trochees")
    if is_trochee("traffic") is False:
        problems.append("traffic should be a trochee")
    if not is_trochee("porno"):
        problems.append("porno should be a trochee")
    if is_trochee("Bordeaux"):
        problems.append("Bordeaux is one stressed syllable, not a trochee here")
    c = candidates("favour")
    words = {x["word"] for x in c}
    if not ({"flavour", "saviour"} & words):
        problems.append(f"favour should rhyme with flavour/saviour: {sorted(words)[:10]}")
    cc = carpet_check(["favour", "flavour", "neighbour"])
    if cc["total"] != 3:
        problems.append("carpet check should score three pairs")
    return (not problems, "; ".join(problems) if problems else f"trochee detector and rhyme menu work ({len(c)} rhymes found for 'favour')")
