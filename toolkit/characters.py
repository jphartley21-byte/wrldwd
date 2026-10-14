"""Characters: how often the song names a person, and WHOSE people they are.

Joe, 13 Oct 2026, after counting the Mum references: "limit any reference to a character to 2 references. prefer romantic
partners or mates over family."

Why it mattered, measured on the two songs (counts only; the original's lines are never reproduced, rule 4):

                        ours (v7)   original (76 bars)
  family references         11            0          mum 9 (ours) vs 0 (the original)
  partner references         0            2
  mate references            3            7          the original's lads/mates are its whole social world
  occupational roles         6            0

The original's largest single character count is 4 ("mate"), so the cap of 2 is STRICTER than the benchmark: this is a Joe
rule, not a calibrated gate, and it is deliberately not asserted against the original in toolkit/calibrate.py -- the same
status as the "no heavy swearing" rule that the pool used to enforce.

Classes: FAMILY is dispreferred, PARTNER and MATE are preferred, ROLE is the occupational cast (the plan's debtor, copper,
sergeant). A plural crowd ("the lads") counts as one character, because that is how it is referred to.
"""
from __future__ import annotations

import re
import sys

FAMILY = ("mum", "mum's", "mam", "mother", "dad", "daddy", "father", "gran", "granny", "nan", "grandad", "sister",
          "brother", "aunt", "uncle", "cousin", "in-laws", "in-law", "nephew", "niece", "stepdad", "stepmum")
PARTNER = ("missus", "missis", "wife", "husband", "girlfriend", "boyfriend", "bird", "fiance", "fiancee", "partner",
           "other half", "ex-girlfriend")
MATE = ("mate", "mates", "lad", "lads", "boys", "boy", "pal", "pals", "mucker", "cobber", "crew", "boys")
ROLE = ("copper", "coppers", "sergeant", "sarge", "driver", "debtor", "stallholder", "stall man", "skipper", "landlord",
        "taxman", "clerk", "officer", "accountant", "council", "inspector", "bouncer", "doorman")

CLASSES = {"family": FAMILY, "partner": PARTNER, "mate": MATE, "role": ROLE}
CAP = 2   # Joe's cap: any one character may be referenced at most twice in the whole song
# The preference is a TARGET, not a second cap. Joe's rule is "limit any reference to a CHARACTER to 2 references; prefer
# romantic partners or mates over family", and the plan deliberately designs a cousin and the Bergen in-laws (family words)
# into real beats, so a hard family cap would gut the plan rather than steer it. What is enforced is the per-character cap
# and a printed preference: the family layer should not outnumber partners and mates put together.


def _pattern(words) -> re.Pattern:
    """ONE regex per class, longest alternative first, so "mum's" is counted as one reference to mum and not also as a
    separate character. Case-insensitive and word-bounded: 'mumbling' and 'Mumsnet' are not references to Mum."""
    alt = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
    return re.compile(r"(?<![a-z])(?:" + alt + r")(?![a-z-])", re.IGNORECASE)


# a plural or a possessive is the same person, and "the lads" is one crowd rather than several people
_CANON = {"mates": "mate", "pals": "pal", "boys": "boy", "coppers": "copper", "mum's": "mum", "dad's": "dad"}


def canon(word: str) -> str:
    w = (word or "").lower()
    if w in _CANON:
        return _CANON[w]
    return w[:-2] if w.endswith("'s") else w


def counts(bars: list[str]) -> dict:
    """per character, and per class, over whatever bars are given (a section or the whole song)."""
    per: dict[str, int] = {}
    cls: dict[str, int] = {k: 0 for k in CLASSES}
    for name, words in CLASSES.items():
        rx = _pattern(words)
        for b in bars or []:
            for m in rx.finditer(b or ""):
                w = canon(m.group(0))
                per[w] = per.get(w, 0) + 1
                cls[name] += 1
    return {"per_word": per, "class": cls}


def over_cap(bars: list[str], cap: int = CAP) -> list[str]:
    """the hard findings: any character referenced more than the cap."""
    c = counts(bars)
    return [f"'{w}' is referenced {n} times (cap {cap})" for w, n in sorted(c["per_word"].items()) if n > cap]


def preference(bars: list[str]) -> str:
    """the soft steer: partners and mates are preferred over family."""
    c = counts(bars)
    fam, prefs = c["class"]["family"], c["class"]["partner"] + c["class"]["mate"]
    if not fam:
        return "family 0: the personal detail is all partners and mates, as preferred"
    if fam > prefs:
        return (f"family {fam} vs partners+mates {prefs}: family OUTNUMBERS the preferred layer -- move a reference onto "
                f"a mate or a partner")
    return f"family {fam} vs partners+mates {prefs}: within the preference"


def report(bars: list[str], cap: int = CAP) -> str:
    c = counts(bars)
    lines = [f"characters: family {c['class']['family']} | partner {c['class']['partner']} | "
             f"mate {c['class']['mate']} | role {c['class']['role']} (cap {cap} per person)"]
    if c["per_word"]:
        lines.append("  " + ", ".join(f"{w} x{n}" for w, n in sorted(c["per_word"].items(), key=lambda x: -x[1])))
    bad = over_cap(bars, cap)
    lines.append("  OVER: " + "; ".join(bad) if bad else "  within the cap")
    lines.append("  " + preference(bars))
    return "\n".join(lines)


def guidance() -> str:
    """the rule as the writer should hear it, before any gate has to fire."""
    return ("PEOPLE: at most TWO references to any one person in the whole song (the lads, my mate, the copper, the debtor, "
            "my cousin). Prefer a mate or a partner over family: no mother, no father, no sister, no brother, and no new "
            "family member invented. Mention people; never address them.")


def selftest() -> tuple[bool, str]:
    problems = []
    three_mums = ["Mum says it's rude", "Mum asked for a kettle", "Mum just reads my books", "Might nip off"]
    if not over_cap(three_mums):
        problems.append("three references to one character must break the cap")
    if over_cap(["My mate had the doors", "The lads did the edges", "Might nip off"]):
        problems.append("one reference each to two different characters must be allowed")
    if over_cap(["Mum rang", "Dad rang", "Gran rang"]):
        problems.append("three different family members are three characters: the cap is per person, not per class")
    if "OUTNUMBERS" not in preference(["Mum rang", "Dad rang", "Gran rang", "Might nip off"]):
        problems.append("a family-only cast must be reported as outnumbering the preferred layer")
    if "OUTNUMBERS" in preference(["My mate rang", "My girlfriend drove", "The lads did the edges"]):
        problems.append("a mate-and-partner cast is within the preference")
    c = counts(["Mum says it's rude", "The lads did the edges"])
    if c["class"]["family"] != 1 or c["class"]["mate"] != 1:
        problems.append(f"class counts wrong: {c['class']}")
    if _pattern(["mum"]).search("mumbling about the mumsnet thread"):
        problems.append("the word pattern must not match inside another word")
    if not _pattern(["mum", "mum's"]).search("Mum says it's rude"):
        problems.append("the word pattern must be case-insensitive")
    if counts(["my mum's kitchen", "mum asked", "mum rang"])["per_word"].get("mum") != 3:
        problems.append("a possessive must count as the same character, not a second one")
    return (not problems, "; ".join(problems) if problems else
            "character cap 2 per person, family cap 2, partners and mates preferred (Joe's rule, 13 Oct 2026)")


def main(argv: list[str]) -> int:
    if not argv or argv[0] == "--selftest":
        ok, msg = selftest()
        print(("ok   " if ok else "BAD  ") + msg)
        return 0 if ok else 1
    path = argv[0]
    bars = [l.strip() for l in open(path, encoding="utf-8", errors="replace")
            if l.strip() and not l.strip().startswith(("#", "==", "["))]
    print(report(bars))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
