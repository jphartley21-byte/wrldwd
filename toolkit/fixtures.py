"""Positive controls for the gates' selftests -- and the ONLY reason these bars are still in the repo.

toolkit/canonical.py held the locked Hook 1-4 and six modules imported it, which made it the file every
draft was measured against and effectively a protected list. Joe scrapped it on 12 Oct 2026 ("scrap
canonical.py, let's build the next draft from scratch"): nothing in the song is locked now, and no draft
may be assembled from this file. The bars live in toolkit/tests/joe_hook_1-4.txt so they can be edited
without touching code, and they exist so that the gates keep a positive control -- a block that must pass
the by-ear scheme, the meaning gate, the regression gates and the ear devices. If a gate starts failing
these bars, the gate has changed, not the song.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "tests", "joe_hook_1-4.txt")


def joe_bars():
    """The positive-control bars, in file order, comments and blanks dropped."""
    out = []
    for line in open(PATH, encoding="utf8"):
        line = line.rstrip("\n").strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out
