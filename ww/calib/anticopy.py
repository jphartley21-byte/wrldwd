"""Local anti-copy check (plan 4.2/6.6): longest shared run of words between a candidate and the ORIGINAL, and which original line.

Runs entirely in memory on this machine - nothing is sent anywhere, nothing is stored - and returns NUMBERS ONLY (never the original's
text). A candidate sharing a run of >= 4 words with the original, or whose bar frame matches the original's instance shapes
(greeting + 'to the boys in' + place, the plane/plain pun), is rejected. Mechanism-level cloning needs the reader and is checked
elsewhere; this is the surface check.
"""
from __future__ import annotations

import re

from . import original

_TOK = re.compile(r"[a-z']+")
FRAMES = [
    re.compile(r"\bto the (boys|lads|birds|girls|gals)\b.{0,20}\b(in|out in)\b", re.I),
    re.compile(r"\b(plain ?clothes)\b.*\b(plane|plain)\b|\b(plane|plain)\b.*\b(plain ?clothes)\b", re.I),
    re.compile(r"\btell her i'?m (out|in)\b.*\bback shortly\b", re.I),
]


def _words(s: str) -> list[str]:
    return _TOK.findall(s.lower().replace("’", "'"))


def check(bars: list[str]) -> dict:
    lines = original._lines()
    owords = [_words(l) for l in lines]
    best = (0, None)
    for bi, b in enumerate(bars):
        bw = _words(b)
        for oi, ow in enumerate(owords):
            for i in range(len(bw)):
                for j in range(len(ow)):
                    k = 0
                    while i + k < len(bw) and j + k < len(ow) and bw[i + k] == ow[j + k]:
                        k += 1
                    if k > best[0]:
                        best = (k, (bi + 1, oi + 1))
    frame = [i for i, p in enumerate(FRAMES) if any(p.search(b) for b in bars)]
    return {"longest_shared_run": best[0], "at": best[1], "frame_clones": frame, "ok": best[0] < 4 and not frame}


def selftest() -> tuple[bool, str]:
    r = check(["Cold beer on the house in Porto", "A glass of port and he knows the waters", "Not the worst pint and last orders", "Might hit the road to Majorca"])
    r2 = check(["Hey boys you know the plan"])
    first = original._lines()[1]
    cp = check([first])
    problems = []
    if not r["ok"]:
        problems.append(f"Joe's V-a block should not clone the original: {r}")
    if cp["ok"] or cp["longest_shared_run"] < 4:
        problems.append("an exact copy of an original line must be caught")
    return (not problems, "; ".join(problems) if problems else "V-a is clean; an exact original line is caught (numbers only)")
