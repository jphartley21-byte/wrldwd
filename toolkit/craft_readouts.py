"""Report-only craft readouts (14 Oct 2026), from the writing-process research in STATE.md.

Three numbers that measure what a bar is MADE OF, not how it sounds. None of them is a gate: each
must pass a labelled-set test (Joe's approved bars vs his rejected ones) before it may rank or
veto anything, and the cash readout is a proxy that cannot tell a literal use from a figurative
one, so every hit has to be read.

  voice     share of bars that open in the first person (I, I'm, we, my...). A song of 76 bars
            that opens 34 of them this way (writing/ww_full_draft_v17.md) is one register.
  others    bars per window of 8 where somebody other than the narrator is present (a mate, a
            partner, a role such as the copper, or a he/she/they). Joe's rule 6 caps characters
            at 2 references each; this counts how many bars HAVE one at all.
  cash      bars where a banked stock phrase has its payoff word in the rhyme slot (the count the
            draft's #cash tags report), and how many of those also name a concrete thing outside
            the phrase. Candidate literalisations (rule 1): the phrase may be cashed (a kettle
            "off the back of a lorry") or merely used ("nothing to hide"). The thing lists are
            finite (coherence_gate.OBJECTS + PLACES), so a bare "no known thing" is not proof.

  python toolkit/craft_readouts.py FILE|-        (a draft with '== Slot' headers, or bare bars)
  python toolkit/craft_readouts.py --selftest
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FIRST_PERSON = {"i", "i'm", "i'd", "i've", "i'll", "we", "we're", "we've", "we'd", "my", "me", "our"}
THIRD = {"he", "she", "they", "him", "her", "them", "he's", "she's", "they're", "his", "their"}
WINDOW = 8


def _words(bar: str) -> list[str]:
    return [w.lower().strip("'") for w in re.findall(r"[A-Za-z][A-Za-z']*", bar or "")]


def voice(bars: list[str]) -> dict:
    opens = [(_words(b) or [""])[0] for b in bars]
    fp = sum(1 for o in opens if o in FIRST_PERSON)
    return {"bars": len(bars), "first_person": fp, "share": fp / len(bars) if bars else 0.0,
            "top": Counter(o for o in opens if o).most_common(4)}


def others(bars: list[str], window: int = WINDOW) -> list[dict]:
    """per window of `window` bars: how many bars have somebody other than the narrator in them."""
    import characters
    out = []
    for s in range(0, len(bars), window):
        chunk = bars[s:s + window]
        has = 0
        for b in chunk:
            c = characters.counts([b])
            if sum(c["class"].values()) or set(_words(b)) & THIRD:
                has += 1
        out.append({"from": s + 1, "to": s + len(chunk), "bars": len(chunk), "with_other": has})
    return out


_BY_PAYOFF: dict[str, list[str]] | None = None


def _by_payoff() -> dict[str, list[str]]:
    global _BY_PAYOFF
    if _BY_PAYOFF is None:
        import bank
        _BY_PAYOFF = {}
        for r in bank.load_phrases():
            if r.get("payoff") and len(r["phrase"].split()) >= 2:
                _BY_PAYOFF.setdefault(r["payoff"].lower(), []).append(r["phrase"].lower())
    return _BY_PAYOFF


def cash(bars: list[str]) -> list[dict]:
    """every banked phrase whose payoff word ends the bar (what the draft's #cash tags count), with the first
    concrete thing elsewhere in the bar (None when the word lists know none: a figurative use, or a noun they lack)."""
    import coherence_gate as cg
    from meaning_gate import PLACES
    out = []
    for i, b in enumerate(bars):
        ws = _words(b)
        if not ws:
            continue
        last = ws[-1]
        cands = set(_by_payoff().get(last, []))
        hits = [k for k, _t in cg.craft_idioms(b) if k in cands or k.split()[-1] == last]
        for k in hits:
            inside = set(k.split())
            things = [w for w in ws if w not in inside and (w in cg.OBJECTS or w in PLACES)]
            out.append({"bar": i + 1, "phrase": k, "thing": things[0] if things else None, "text": b})
    return out


def parse(text: str) -> list[tuple[str, list[str]]]:
    """[(section, bars)] from a draft with '== Slot' headers; bare bars fall in one section."""
    secs: list[tuple[str, list[str]]] = []
    name, cur = "all", []
    for raw in text.lstrip("﻿").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("=="):
            if cur:
                secs.append((name, cur))
            name, cur = line.strip("= ").strip(), []
            continue
        cur.append(re.sub(r"^\s*\d+[.)]\s+", "", line))
    if cur:
        secs.append((name, cur))
    return secs


def report(bars: list[str]) -> str:
    v = voice(bars)
    lines = [f"voice: {v['first_person']} of {v['bars']} bars open in the first person ({v['share']:.0%}); "
             f"openers " + ", ".join(f"{w} x{n}" for w, n in v["top"])]
    oth = others(bars)
    lines.append("others present: " + ", ".join(f"bars {o['from']}-{o['to']}: {o['with_other']}/{o['bars']}" for o in oth)
                 + ("  <- one narrator, no company" if oth and not sum(o["with_other"] for o in oth) else ""))
    c = cash(bars)
    with_thing = [x for x in c if x["thing"]]
    lines.append(f"stock phrases with the payoff word in the rhyme slot: {len(c)}; of those, with a concrete thing in the bar "
                 f"(candidate literalisation, READ each): {len(with_thing)}")
    lines += [f"  bar {x['bar']}: '{x['phrase']}' + {x['thing'] or '(no known concrete thing)'}  | {x['text']}" for x in c]
    return "\n".join(lines)


def selftest() -> tuple[bool, str]:
    problems = []
    v = voice(["I did Spain", "I'm at the bar", "We went home", "The lads left"])
    if (v["first_person"], v["bars"]) != (3, 4):
        problems.append(f"voice count wrong: {v}")
    if voice([])["share"] != 0.0:
        problems.append("an empty block must not divide by zero")
    o = others(["I went", "My mate paid", "She said no", "I left", "I sat", "I ate", "I slept", "I woke"])
    if o[0]["with_other"] != 2:
        problems.append(f"others should find the mate and the pronoun: {o}")
    if others(["I went"] * 8)[0]["with_other"] != 0:
        problems.append("a solo narrator must read 0 company")
    c = cash(["The kettle fell off the back of a lorry"])
    if not c or c[0]["thing"] != "kettle":
        problems.append(f"a banked phrase ending the bar with a concrete thing must carry that thing: {c}")
    if cash(["Off the back of a lorry went the kettle and the rest"]):
        problems.append("a phrase whose payoff word is not in the rhyme slot must not be counted")
    c2 = cash(["I have nothing to hide"])
    if c2 and c2[0]["thing"]:
        problems.append("a phrase with no concrete thing in the bar must report thing=None")
    s = parse("== Hook\nI did Spain\n# note\n2. We went\n== V1\nThe lads left\n")
    if [(n, len(b)) for n, b in s] != [("Hook", 2), ("V1", 1)]:
        problems.append(f"parse wrong: {s}")
    return (not problems, "; ".join(problems) if problems else
            "report-only craft readouts: voice, company, cash candidates (14 Oct 2026)")


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    if "--selftest" in argv:
        ok, msg = selftest()
        print(("CRAFT READOUTS SELFTEST PASSED: " if ok else "CRAFT READOUTS SELFTEST FAILED: ") + msg)
        return 0 if ok else 1
    path = next((a for a in argv if not a.startswith("--")), "-")
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8-sig").read()
    secs = parse(text)
    allbars = [b for _n, bs in secs for b in bs]
    print(f"craft readouts (REPORT ONLY, not a gate) - {len(allbars)} bars")
    print(report(allbars))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
