"""Retired bars: lines that must never be used as a bar, a positive control or a gate again.

Joe, 15 Oct 2026: the four Hook 1-4 bars the repo called "Joe's approved bars" (and their earlier spellings, 9 lines in all) (toolkit/tests/joe_hook_1-4.txt,
before that toolkit/canonical.py) were never approved: "These bars are not approved. They should be removed now
and never used as a bar or gate again." Every selftest, calibration, training row and reference block that used
them as the known-good example was removed the same day.

Only a hash of each normalised line is kept, so the text itself is not stored. Old drafts in writing/ still contain
the lines as history; anything that reads bars out of a file (miners, assemblers, the slot checker) calls
is_retired() so they cannot come back as a bar.

  python toolkit/retired.py FILE|-     prints the line numbers of retired bars in a file
  python toolkit/retired.py --selftest
"""
import hashlib
import re
import sys

RETIRED = {
    "2678ced7e7b6e24f04ad4487fbc2d8cfdfab461c",
    "2d94d3352193e27e6e36cb56e10398cc5ddcc3af",
    "b072f733ad8d0299dfd89c750b7d0b39a19e79be",
    "b9527b2663075a5a0edc741371bc875a22e82cb9",
    "d0a6644a3901e2a546e93642fc39f917363c5e54",
    "d34f441eb0430a66c3ec459408fe05ed4de4e78a",
    "e524ce6e7a75fd352d5bb9610e64a49d096bd316",
    "ec85abe566a25ee495f8e21260dc68c048b7ff83",
    "ed17353771705c580960a847cfc59f0b999292be",
}


def norm(bar: str) -> str:
    """lowercase letters and spaces only, so punctuation or casing cannot smuggle a line back in."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]+", " ", bar.lower())).strip()


def digest(bar: str) -> str:
    return hashlib.sha1(norm(bar).encode("utf-8")).hexdigest()


def is_retired(bar: str) -> bool:
    return digest(bar) in RETIRED


def strip_retired(bars):
    return [b for b in bars if not is_retired(b)]


def scan(text: str):
    """[(line number, line)] for every retired bar in a text."""
    return [(i + 1, l.strip()) for i, l in enumerate(text.splitlines()) if l.strip() and is_retired(l)]


def selftest() -> bool:
    ok = len(RETIRED) == 9 and all(len(h) == 40 for h in RETIRED)
    ok &= norm("Yo, Hey -- there!") == "yo hey there"
    ok &= not is_retired("Hoi Rotterdam beg your pardon")
    print("retired selftest:", "PASSED" if ok else "FAILED", f"({len(RETIRED)} retired hashes)")
    return ok


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        sys.exit(0 if selftest() else 1)
    txt = sys.stdin.read() if a[0] == "-" else open(a[0], encoding="utf-8-sig").read()
    hits = scan(txt)
    for n, _ in hits:
        print(f"retired bar on line {n}")
    sys.exit(1 if hits else 0)
