"""Rhyme-family bank: pick the family and its END WORDS first, then write the bars (round-2 method).

Round 1 failed because writers rhymed a few bars and let the rest drift, and because the end words that were free to
choose were filler (naysayer, soothsayer, funny, honey, eyes wide). Given a seed word, this lists every PERFECT rhyme of
its last 1, 2 and 3 syllables that is a common real word, split by ending class (hard = stressed last syllable, soft = ends
on a weak syllable), plus places, local words and banked stock phrases whose payoff word is in the family.
Numbers/words only: no lyrics, no original text. All sources are local (cmudict + OVR, wordfreq, toolkit phrase/place banks).
"""
from __future__ import annotations

import sys

from .. import bridge, config


def _tk():
    p = str(config.TOOLKIT)
    if p not in sys.path:
        sys.path.insert(0, p)
    import bank
    import rhyme_tools as rt
    return rt, bank


def _hard(word: str) -> bool | None:
    sp = bridge.stress_pattern(word)
    if not sp:
        return None
    return sp[-1] in "12"


def family(seed: str, n: int = 0, min_zipf: float = 3.0) -> list[dict]:
    """perfect rhymes of `seed` from its last stressed vowel on (n=0), confirmed in BRITISH phones (the ARPAbet index is US-vowelled:
    'market' would otherwise rhyme with 'pocket')."""
    rt, bank = _tk()
    ph, bad = rt.pron_phrase(seed)
    if ph is None:
        bridge.stress_pattern(seed)          # lets ww.lex.pron teach the pronouncer a word it has not met
        ph, bad = rt.pron_phrase(seed)
    if ph is None:
        return []
    kk = rt.key(ph, n, "perfect")
    if not kk:
        return []
    names = {e["name"].lower() for e in bank.load_entities() if e["type"] in ("given-name", "surname")}
    out, seen = [], set()
    for w in rt.index(n, "perfect").get(kk, []):
        if w in names and w not in ("tory", "story", "glory"):    # given names / surnames are not rhyme words (kory, rory, laurie ...)
            continue
        if w in seen or w == seed.lower() or len(w) < 3:
            continue
        seen.add(w)
        z = bank.rt_zipf(w)
        if z < min_zipf and w not in bank.UK_EVERYDAY:
            continue
        if bridge.rhyme_score(seed, w) < 0.95:
            continue
        out.append({"word": w, "zipf": round(z, 2), "syl": (len(bridge.stress_pattern(w) or "")) or None, "hard": _hard(w)})
    out.sort(key=lambda r: -r["zipf"])
    return out


def places_and_local(words: set[str]) -> tuple[list[str], list[str]]:
    rt, bank = _tk()
    pl = sorted({e["name"] for e in bank.load_entities() if e["type"] in ("city", "uk-town", "country") and e["name"].lower() in words})
    lw = sorted({f"{r['word']} ({r['country']}: {r['gloss']})" for r in bank.load_loanwords() if r["word"].lower() in words})
    return pl, lw


def phrases_for(words: set[str], limit: int = 25) -> list[str]:
    rt, bank = _tk()
    rows = [r for r in bank.load_phrases() if r["measurable"] and r["payoff"].lower() in words]
    rows.sort(key=lambda r: (not r.get("curated"), -(r.get("score") or 0)))
    return [f"{r['phrase']} -> {r['payoff']} [{r['sense']}]" for r in rows[:limit]]


def report(seed: str, n: int = 0, limit: int = 45) -> str:
    fam = family(seed, n)
    if not fam:
        return f"no rhyme family for '{seed}' at n={n} (word unknown? try another form)"
    hard = [r for r in fam if r["hard"]]
    soft = [r for r in fam if r["hard"] is False]
    words = {r["word"] for r in fam}
    pl, lw = places_and_local(words)
    ph = phrases_for(words)
    L = [f"FAMILY of '{seed}' (perfect rhyme from the last stressed vowel, British phones); {len(fam)} common words",
         f"HARD endings (last syllable stressed): " + ", ".join(f"{r['word']}" for r in hard[:limit]),
         f"SOFT endings (last syllable weak):   " + ", ".join(f"{r['word']}" for r in soft[:limit])]
    if pl:
        L.append("PLACES in the family: " + ", ".join(pl[:25]))
    if lw:
        L.append("LOCAL WORDS in the family: " + "; ".join(lw[:15]))
    if ph:
        L.append("BANKED STOCK PHRASES whose payoff word is in the family:\n  " + "\n  ".join(ph))
    try:
        from ..lex import lexicon
        fam_rows = lexicon.family(seed)
    except Exception:    # noqa: BLE001 - the lexicon is a supplement; never break the bank report
        fam_rows = {}
    labels = [("brand", "BRANDS / PRODUCTS / SHOPS"), ("media", "TV, MUSIC, FESTIVALS"), ("place", "PLACES"), ("slang", "SLANG / DIALECT / MONEY"), ("role", "ROLES (use these instead of names)"),
              ("local", "LOCAL WORDS"), ("prop", "PROPS / OBJECTS"), ("abbr", "ABBREVIATIONS / ADMIN"), ("pun", "PUN PAIRS"), ("oronym", "ORONYMS (phrases that sound alike)"),
              ("hidden", "NAMES HIDING A LOADED READING (use sparingly: the name first, the dark reading second)"), ("redup", "REDUPLICATIONS / PERCUSSIVE PAIRS"),
              ("onoma", "ONOMATOPOEIA"), ("game", "GAMES / RHYMES whose move can read as a crime (shared-action wordplay)"), ("pop", "FAMOUS NAMES / TITLES"), ("loaded", "LOADED SLANG")]
    for g, label in labels:
        rows = fam_rows.get(g, [])
        if rows:
            L.append(f"{label} ending in this family: " + "; ".join(r["text"] + (f" ({r['gloss']})" if r.get("gloss") else "") for r in rows[:18]))
    idi = fam_rows.get("idiom", [])
    if idi:
        L.append("IDIOMS with a literal reading whose payoff word is in the family:\n  " + "\n  ".join(f"{r['text']} -> {r['extra']}" for r in idi[:15]))
    L.append("Pick the family and 8+ end words BEFORE writing; each end word must be a content word the bar's claim depends on. Also try: python -m ww.cli homophones <word> and  python -m ww.cli soundalike <word>  for sound-play.")
    return "\n".join(L)


def selftest() -> tuple[bool, str]:
    fam = family("pocket")
    ws = {r["word"] for r in fam}
    problems = []
    if not ({"rocket", "socket"} <= ws):
        problems.append(f"pocket family missing rocket/socket: {sorted(ws)[:12]}")
    if "pocket" in ws:
        problems.append("seed must not list itself")
    if not report("pocket").startswith("FAMILY"):
        problems.append("report malformed")
    return (not problems, "; ".join(problems) if problems else f"pocket family has {len(fam)} common words incl. rocket/socket")
