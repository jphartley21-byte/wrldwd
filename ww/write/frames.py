"""Filler-frame ban-list and repetition check (plan 4.3, R4). Seeded from the measured v27 failures, not learned after the fact.

Rule (pre-registered): no 3-word frame occurs more than 2x inside a section or more than 3x in a song. The known v27 filler
frames below are ALSO banned outright as writer-prompt negatives ("do not use these frames") and as candidate rejects.
Hook sections that repeat bar-for-bar (the chorus) are exempt from the song-level count by design.
"""
from __future__ import annotations

import re
from collections import Counter

SEED_BANNED = ("and the whole", "the whole of", "him in", "the lot", "in the room", "the whole thing")  # measured v27 fillers only
SECTION_MAX = 2
SONG_MAX = 3
_TOK = re.compile(r"[a-z']+")


def tokens(bar: str) -> list[str]:
    return _TOK.findall(bar.lower().replace("’", "'"))


def grams(bars: list[str], n: int = 3) -> Counter:
    c: Counter = Counter()
    for b in bars:
        t = tokens(b)
        for i in range(len(t) - n + 1):
            c[" ".join(t[i:i + n])] += 1
    return c


def scan(sections: dict[str, list[str]]) -> dict:
    """{'section': {slot: [(frame, n)]}, 'song': [(frame, n)], 'banned': {slot: [(phrase, n)]}}"""
    out: dict = {"section": {}, "song": [], "banned": {}}
    song: Counter = Counter()
    seen_hook_bars: set[str] = set()
    for slot, bars in sections.items():
        c = grams(bars)
        bad = [(g, n) for g, n in c.items() if n > SECTION_MAX]
        if bad:
            out["section"][slot] = sorted(bad, key=lambda x: -x[1])
        ban: Counter = Counter()
        for b in bars:
            low = " ".join(tokens(b))
            for p in SEED_BANNED:
                if re.search(r"\b" + re.escape(p) + r"\b", low):
                    ban[p] += 1
        if ban:
            out["banned"][slot] = sorted(ban.items(), key=lambda x: -x[1])
        for b in bars:
            if slot.lower().startswith("hook") and b in seen_hook_bars:
                continue
            if slot.lower().startswith("hook"):
                seen_hook_bars.add(b)
            for g, n in grams([b]).items():
                song[g] += n
    out["song"] = sorted([(g, n) for g, n in song.items() if n > SONG_MAX], key=lambda x: -x[1])
    return out


def selftest() -> tuple[bool, str]:
    from ..eval import gold
    from .. import config
    secs = gold.parse_draft(config.WRITING / "full_draft_v27.md")
    r = scan(secs)
    banned_total = sum(n for v in r["banned"].values() for _, n in v)
    ok = banned_total >= 10 and bool(r["song"]) and bool(r["section"])
    clean = scan({"A": ["Hello from the harbour", "Bought a rail pass in Bern"], "B": ["Missed the ferry at noon"]})
    ok = ok and not clean["section"] and not clean["song"] and not clean["banned"]
    return ok, (f"v27: {banned_total} banned-frame hits, {sum(len(v) for v in r['section'].values())} section-repeat frames, "
                f"{len(r['song'])} song-repeat frames; clean text is clean")
