"""Wordplay supply: homophones, near-homophones and sound-alikes in a BRITISH (non-rhotic) accent.

The original's best sound-play lives here: a word or phrase that sounds like another (a place against a word, a foreign word against an
English phrase, an everyday word against a loaded one). The writers had no supply for it, so they made puns on the idiom's own words.

  python -m ww.cli homophones pause        -> paws, pours, pores ...      (identical British phones)
  python -m ww.cli soundalike porto        -> porno, ...                  (phoneme edit distance <= 2, words and two-word phrases)
  python -m ww.cli soundalike "danke"      -> foreign words are pronounced through the pron chain (cmudict, OVR, compound split, g2p)

Phone distance is computed on British IPA phones from ww.bridge.phones (R-dropped, stress marks removed); a substitution between phones of the
same family (short/long vowel pair, voiced/voiceless pair, schwa/short-i) costs 0.5.
"""
from __future__ import annotations

import re
import sys
from functools import lru_cache

from .. import bridge

_VOWELS = set("aeiouəɪʊɒʌɔɛæɑɜ")
_SIMILAR = [set(p) for p in ("pb", "td", "kg", "fv", "sz", "ʃʒ", "tʃdʒ", "θð", "ɪə", "ɪi", "ʊu", "ɒɔ", "ɑʌ", "ɛe", "æɛ", "ɔːɒ", "ɑːɒ", "uːʊ", "iːɪ")]
_MAXVOCAB = 60000
_GLUE = set("a an the of to in on at for with as is it its and or but so no do go know too two tea row co though low show to be by my me we he she you your i us up out off if than that this them they then there here are was were has have had not can will would".split())


def _strip(ph: list[str]) -> tuple[str, ...]:
    return tuple(p.replace("ˈ", "").replace("ˌ", "") for p in ph)


def _cost(a: str, b: str) -> float:
    if a == b:
        return 0.0
    for s in _SIMILAR:
        if a in s and b in s:
            return 0.5
    return 1.0


def distance(a: tuple[str, ...], b: tuple[str, ...], cap: float = 3.0) -> float:
    n, m = len(a), len(b)
    if abs(n - m) > cap:
        return cap + 1
    prev = [float(j) for j in range(m + 1)]
    for i in range(1, n + 1):
        cur = [float(i)] + [0.0] * m
        best = cur[0]
        for j in range(1, m + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + _cost(a[i - 1], b[j - 1]))
            best = min(best, cur[j])
        if best > cap:
            return cap + 1
        prev = cur
    return prev[m]


@lru_cache(maxsize=1)
def _vocab() -> list[tuple[str, tuple[str, ...], float]]:
    import wordfreq
    out = []
    for w in wordfreq.top_n_list("en", _MAXVOCAB):
        if not w.isalpha() or len(w) < 2:
            continue
        ph = bridge.phones(w)
        if not ph:
            continue
        out.append((w, _strip(ph), wordfreq.zipf_frequency(w, "en")))
    return out


@lru_cache(maxsize=1)
def _exact_index() -> dict:
    idx: dict = {}
    for w, ph, z in _vocab():
        idx.setdefault(ph, []).append((w, z))
    return idx


def phones_of(text: str) -> tuple[str, ...] | None:
    """British phones of a word or phrase, through the pron chain for anything the dictionary lacks."""
    out: list[str] = []
    for tok in re.findall(r"[A-Za-z']+", bridge.norm(text)):
        ph = bridge.phones(tok)
        if not ph:
            from ..lex import pron
            pron.ensure(tok, persist=False)
            ph = bridge.phones(tok)
        if not ph:
            return None
        out += list(_strip(ph))
    return tuple(out) if out else None


def homophones(word: str, min_zipf: float = 2.0) -> list[tuple[str, float]]:
    ph = phones_of(word)
    if not ph:
        return []
    return sorted([(w, z) for w, z in _exact_index().get(ph, []) if w != word.lower() and z >= min_zipf], key=lambda t: -t[1])


def soundalike(text: str, maxd: float = 2.0, limit: int = 60, phrases: bool = True) -> list[tuple[str, float, float]]:
    """[(candidate, distance, zipf)] - single words, and two-word phrases built from the 6000 commonest words."""
    tgt = phones_of(text)
    if not tgt:
        return []
    low = text.lower()
    res: list[tuple[str, float, float]] = []
    for w, ph, z in _vocab():
        if w == low or z < 2.5:
            continue
        d = distance(tgt, ph, maxd)
        if d <= maxd:
            res.append((w, d, z))
    if phrases:
        common = [(w, ph, z) for w, ph, z in _vocab()[:6000] if len(ph) >= 2 and w not in _GLUE]
        for cut in range(2, len(tgt) - 1):
            left, right = tgt[:cut], tgt[cut:]
            L = [(w, z) for w, ph, z in common if distance(left, ph, 1.0) <= 1.0]
            R = [(w, z) for w, ph, z in common if distance(right, ph, 1.0) <= 1.0]
            for a, za in L[:25]:
                for b, zb in R[:25]:
                    cand = f"{a} {b}"
                    ph = [p for w_, p, _ in common if w_ == a][:1], [p for w_, p, _ in common if w_ == b][:1]
                    if not ph[0] or not ph[1]:
                        continue
                    d = distance(tgt, ph[0][0] + ph[1][0], maxd)
                    if d <= maxd and cand != low:
                        res.append((cand, d, min(za, zb)))
    seen, out = set(), []
    for c, d, z in sorted(res, key=lambda t: (t[1], -t[2])):
        if c not in seen:
            seen.add(c)
            out.append((c, d, z))
    return out[:limit]


def report_homophones(word: str) -> str:
    hs = homophones(word)
    return f"HOMOPHONES of '{word}' (identical British phones): " + (", ".join(f"{w}" for w, _ in hs[:40]) or "none among common words")


def report_soundalike(text: str, maxd: float = 2.0) -> str:
    sa = soundalike(text, maxd)
    if not sa:
        return f"no sound-alikes within distance {maxd} for '{text}' (or the word could not be pronounced; try a wider --maxd)"
    words = [t for t in sa if " " not in t[0]]
    phr = [t for t in sa if " " in t[0]]
    L = [f"SOUND-ALIKES of '{text}' (phoneme edit distance <= {maxd}; 0 = identical, 0.5 = one near-miss):",
         "  words: " + (", ".join(f"{c} ({d:.1f})" for c, d, z in words[:25]) or "none"),
         "  two-word phrases: " + (", ".join(f"{c} ({d:.1f})" for c, d, z in phr[:15]) or "none")]
    return "\n".join(L)


def selftest() -> tuple[bool, str]:
    problems = []
    hs = {w for w, _ in homophones("pause")}
    if not ({"paws", "pours"} <= hs):
        problems.append(f"pause should have paws/pours as British homophones: {sorted(hs)[:10]}")
    pl = {w for w, _ in homophones("plane")}
    if "plain" not in pl:
        problems.append(f"plane ~ plain: {sorted(pl)}")
    sa = [c for c, d, z in soundalike("porto", 1.0, 40, phrases=False)]
    if "porno" not in sa:
        problems.append(f"porto should sound within 1 of porno: {sa[:15]}")
    return (not problems, "; ".join(problems) if problems else "British homophones (pause/paws/pours, plane/plain) and sound-alikes (porto~porno) found")
