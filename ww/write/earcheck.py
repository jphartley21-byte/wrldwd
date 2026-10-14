"""Joe's ear, 14 Oct 2026, encoded as detectors (his own words in the examples below).

His verdict on the two bars  "Cop in whites, he's wrecked my picket" / "Gnome's in good nick, so he says I nicked it":
  1. difficult MOUTH-SHAPE TRANSITIONS: "whites, he's" and "he's wrecked";
  2. the PAUSES do not line up: line 1 is 3 | 5 syllables, line 2 is 4 | 6;
  3. in line 2 the STRESSES BUNCH in the middle, so its rhyme cannot land on the same beat as line 1's.

Each detector is calibrated on the original before it may block (a gate the benchmark fails is a wrong gate): `base_rates()` measures the original's own rate and
`report()` lists, bar by bar, what fired. All three work on the syllables laid on the original's audio-measured 16th-note grid (flowaudit.laid).
"""
from __future__ import annotations

import re

from .. import bridge
from . import flowaudit as fa

SIB = {"S", "Z", "SH", "ZH", "CH", "JH"}
SPREAD = {"IY", "IH", "EY", "EH", "AY", "AE"}
VOW = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}


def _word_phones(w: str):
    rt = fa._rt()
    ph = rt.pron(w.lower().replace("å", "a"))
    return [re.sub(r"\d", "", p) for p in ph] if ph else None


def _runs(ph):
    ini = []
    for p in ph:
        if p in VOW:
            break
        ini.append(p)
    fin = []
    for p in reversed(ph):
        if p in VOW:
            break
        fin.append(p)
    fin.reverse()
    lastv = next((p for p in reversed(ph) if p in VOW), None)
    return ini, fin, lastv


def word_joins(bar: str) -> list[dict]:
    """every word-to-word join in the bar (across commas too) with an articulatory difficulty score and the reasons."""
    words = re.findall(r"[A-Za-z'å]+", bridge.norm(bar))
    out = []
    for a, b in zip(words, words[1:]):
        pa, pb = _word_phones(a), _word_phones(b)
        if not pa or not pb:
            continue
        _, fin, lastv = _runs(pa)
        ini, _, _ = _runs(pb)
        score, why = 0, []
        run = len(fin) + len(ini)
        if run >= 4:
            score += 2; why.append(f"{run}-consonant cluster across '{a} {b}'")
        elif run == 3:
            score += 1; why.append(f"3-consonant cluster across '{a} {b}'")
        if fin and ini and fin[-1] in SIB and (ini[0] in SIB or ini[0] in ("TH", "DH")) and fin[-1] != ini[0]:
            score += 1; why.append(f"hiss into a different hiss or th ('{a}' {fin[-1]} -> '{b}' {ini[0]})")
        if len(fin) >= 2 and ini and ini[0] == "HH":
            score += 1; why.append(f"breathy 'h' straight after the cluster in '{a}' ('{a} {b}')")
        if fin and ini and lastv in SPREAD and ini[0] in ("R", "W") and fin[-1] in ("S", "Z"):
            score += 1; why.append(f"spread lips ({lastv}) through a hiss into a rounded {ini[0]} ('{a} {b}')")
        out.append({"a": a, "b": b, "score": score, "why": why})
    return out


def bar_pause(bar: str):
    """syllables before the first internal comma/dash (None if there is none)"""
    m = re.search(r",|\s-\s|;|:", bridge.norm(bar))
    if not m:
        return None
    return len(fa.syll_table(bar[: m.start()]))


def template_pause(slot: str, i: int):
    """syllables before the widest gap (> 2 sixteenths) between consecutive syllables in the original's bar, else None"""
    from .slotcheck import SECS
    ff = fa._ff()
    start = next(s for n, s, e in SECS if n == slot)
    st = ff.T[start + i].get("steps") or []
    best, at = 2, None
    for k, (a, b) in enumerate(zip(st, st[1:])):
        if b - a > best:
            best, at = b - a, k + 1
    return at


def squeezed(slot: str, i: int, bar: str) -> list[str]:
    """two stressed content syllables of DIFFERENT words that the grid puts under two sixteenths apart ('good nick'): neither has room, so the bar bunches and its rhyme
    lands late. (A stressed syllable followed by an unstressed one in the same step is normal speech and is not flagged.)"""
    tab, steps, t = fa.laid(slot, i, bar)
    if steps is None:
        return []
    out = []
    for k, r in enumerate(tab[:-1]):
        nxt = tab[k + 1]
        if k + 1 < len(steps) and r["stress"] == 1 and r["content"] and nxt["stress"] == 1 and nxt["content"] and nxt["word"] != r["word"] and 0 <= steps[k + 1] - steps[k] < 2:
            out.append(f"{r['word']}+{nxt['word']}")
    return out


def report(slot: str, bars: list[str]) -> list[str]:
    L, pauses = [], []
    for i, b in enumerate(bars):
        for j in word_joins(b):
            if j["score"] >= 2:
                L.append(f"bar {i + 1}: hard mouth-shape transition: " + "; ".join(j["why"]))
        sq = squeezed(slot, i, b)
        if sq:
            L.append(f"bar {i + 1}: two stresses jammed together on the beat grid ({', '.join(sq)}): stresses bunch and the rhyme lands late")
        kc, kt = bar_pause(b), template_pause(slot, i)
        pauses.append(kc)
        if kc is not None and kt is not None and abs(kc - kt) >= 2:
            L.append(f"bar {i + 1}: comma after syllable {kc}, the original pauses after syllable {kt}")
    for i, (a, b) in enumerate(zip(pauses, pauses[1:])):
        if a is not None and b is not None and a != b:
            L.append(f"bars {i + 1}-{i + 2}: pauses do not line up (after syllable {a}, then {b}); neighbouring bars that pause should pause at the same place")
    return L


def rates(sections: dict[str, list[str]]) -> dict:
    nb = hard = sq = pn = pdev = pc = pm = 0
    for n, bars in sections.items():
        for i, b in enumerate(bars):
            nb += 1
            hard += any(j["score"] >= 2 for j in word_joins(b))
            sq += bool(squeezed(n, i, b))
            kc, kt = bar_pause(b), template_pause(n, i)
            if kc is not None and kt is not None:
                pn += 1; pdev += abs(kc - kt) >= 2
        ps = [bar_pause(b) for b in bars]
        for a, b2 in zip(ps, ps[1:]):
            if a is not None and b2 is not None:
                pc += 1; pm += a != b2
    return {"bars": nb, "hard_join_bars": hard / nb, "squeezed_bars": sq / nb, "pause_off_template": (pdev / pn) if pn else 0.0, "pause_pairs_misaligned": (pm / pc) if pc else 0.0,
            "n_pause_bars": pn, "n_pause_pairs": pc}


def selftest() -> tuple[bool, str]:
    problems = []
    if not any(j["score"] >= 1 for j in word_joins("Cop in whites, he's wrecked my picket")):
        problems.append("'whites, he's' / 'he's wrecked' should score as a hard join")
    if not squeezed("Hook 5-8", 1, "Gnome's in good nick, so he says I nicked it"):
        problems.append("'good nick' should be squeezed on the grid")
    return (not problems, "; ".join(problems) if problems else "Joe's three complaints fire on his two flagged bars")
