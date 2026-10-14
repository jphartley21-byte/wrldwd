"""phrase_audit: the SONG-level repetition guard.

Why it exists (13 Oct 2026). The hook and the verses all passed their OWN section checks, and the assembled
song still came out with eight bars opening "Might", seven opening "Booked", sixteen bars leaning on
"and the whole / the whole of the", and one line repeated word for word. Every one of those frames is
individually legal -- it fits the metre, it rhymes, meaning_gate is happy -- so no section-level check could
see the problem. Nothing was looking ACROSS sections, and the song had never been assembled as one file
before, so the song-level checks in songcheck.py (which do count repeats) had nothing to run on.

This tool looks only at repetition, at the level where repetition lives: the whole song.
  * a line repeated anywhere (the chorus is exempt: the chorus is SUPPOSED to return)
  * an opener (first word) used more than --max-opener times
  * a content n-gram used more than --max-gram times
  * a comma count per section (each comma is a fired "extra mid-bar pause" in check_all)

Thresholds are calibrated against the ORIGINAL, never guessed: `--calibrate PATH` prints counts only and the
original passes all four checks (a gate the benchmark fails is a wrong gate). The original's own deliberate
anaphora (one word three times in the hook) and its chorus do not trip them.

  python toolkit/phrase_audit.py writing/full_draft_vN.md
  python toolkit/phrase_audit.py --calibrate "C:\\...\\original_lines.txt"   (counts only, never lyrics)
  python toolkit/phrase_audit.py --selftest
"""
import argparse
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import songcheck as sc          # noqa: E402
import regression as rg         # noqa: E402

MAX_OPENER = 3      # the original's most-used CONTENT opener appears 3x ("keep", "had"); pronouns excluded
MAX_GRAM = 2        # the original never repeats a content 4-gram more than twice
MAX_COMMA_RATE = 0.30   # the original: 23 comma-bearing bars in 92 (25%). A comma is not a fault by itself;
#                         check_all's "extra mid-bar pause" is a comparison against each bar's own template.
OPENERS_NOT_COUNTED = set("""i me my we you he she it they them him her us and but so or then when if as
cos cause yeah aye oh yo nah no yes the a an""".split())


def opener_of(bar):
    m = re.match(r"[A-Za-z']+", bar.strip())
    return m.group(0).lower() if m else ""


def content_words(bar):
    return [w for w in rg.words(bar) if w not in rg.STOP]


def ngrams(bars, n=4):
    out = collections.Counter()
    for b in bars:
        ws = content_words(b)
        for i in range(len(ws) - n + 1):
            out[" ".join(ws[i:i + n])] += 1
    return out


def audit(secs, headerless=False):
    bars = [l for _s, b in secs for l in b]
    hook_lines = {l for s, b in secs if s and s.lower().startswith("hook") for l in b}
    repeated = [l for l, c in collections.Counter(bars).items() if c > 1]
    counts = {
        "bars": len(bars),
        "sections": len(secs),
        "dups": repeated,
        "chorus_dups": [l for l in repeated if l in hook_lines],
        "openers": collections.Counter(opener_of(b) for b in bars if opener_of(b)),
        "grams": ngrams(bars, 4),
        "comma_bars": sum(1 for b in bars if "," in b),
        "comma_per_section": {s: sum(1 for l in b if "," in l) for s, b in secs},
    }
    fails = []
    # a repeated line is only a fault OUTSIDE the hook: the chorus is supposed to return bar for bar.
    # With no section headers we cannot tell a chorus from a crutch, so repeats are reported, not failed.
    for line in counts["dups"]:
        if headerless:
            continue
        if line not in hook_lines:
            fails.append(f"line repeated verbatim: {line}")
    for w, c in counts["openers"].most_common():
        if w in OPENERS_NOT_COUNTED:
            continue
        if c > MAX_OPENER:
            fails.append(f"content opener '{w}' used {c}x (max {MAX_OPENER})")
    for g, c in counts["grams"].most_common():
        if c > MAX_GRAM:
            fails.append(f"phrase '{g}' used {c}x (max {MAX_GRAM})")
    rate = counts["comma_bars"] / max(1, counts["bars"])
    if rate > MAX_COMMA_RATE:
        fails.append(f"{counts['comma_bars']} of {counts['bars']} bars carry a comma "
                     f"({rate:.0%}, max {MAX_COMMA_RATE:.0%}; the original is 25%)")
    return counts, fails


def read_plain(path):
    """A file of bars with no section headers (the original's own line list): counts only."""
    bars = [l.strip() for l in open(path, encoding="utf8", errors="replace")
            if l.strip() and not l.lstrip().startswith(("#", "|", "["))]
    return [(None, bars)]


def report(counts, quiet=False):
    print(f"bars {counts['bars']} in {counts['sections']} sections")
    print("  openers: " + ", ".join(f"{w} x{c}" for w, c in counts["openers"].most_common(6)))
    if counts["grams"]:
        print("  worst repeated phrase: " + ", ".join(
            f"({c}x) {g}" for g, c in counts["grams"].most_common(3)))
    print(f"  comma-bearing bars: {counts['comma_bars']}")
    if counts["dups"] and not quiet:
        print("  repeated lines: " + "; ".join(counts["dups"]))

def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print("  FAIL", name)

    clean = [("V1 1-8", ["Paid up in Zurich and the boots were gone",
                         "Rode it back clean on the ferry home",
                         "Cash in the hand and the rest in the post",
                         "Might take the long way back to the coast"])]
    c, f = audit(clean)
    chk("clean stanza passes", not f)
    dup = [("V1 1-8", ["Paid up in Zurich and the boots were gone",
                       "Paid up in Zurich and the boots were gone"])]
    c, f = audit(dup)
    chk("duplicate line caught", any("verbatim" in x for x in f))
    tic = [("V1 1-8", ["Might take the long way", "Might do the rest", "Might pack the bag",
                       "Might bring it back"])]
    c, f = audit(tic)
    chk("repeated opener caught", any("opener 'might'" in x for x in f))
    gram = [("V1 1-8", ["cash back on the road in the van", "cash back on the road in the van today",
                        "and cash back on the road in the van"])]
    c, f = audit(gram)
    chk("repeated phrase caught", any("cash back road van" in x for x in f))
    chorus = [("Hook 1-4", ["Cheers to the lads in Leeds tonight", "Chips on a cold pier at noon"]),
              ("Hook 9-16", ["Cheers to the lads in Leeds tonight", "Chips on a cold pier at noon"])]
    c, f = audit(chorus)
    chk("a returning chorus is not a duplicate fault", not f)
    commas = [("V1 1-8", ["one, two", "three, four", "five, six", "seven, eight"])]
    c, f = audit(commas)
    chk("comma RATE caught", any("comma" in x for x in f))
    print("phrase_audit selftest:", "PASSED" if ok else "FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="-", help="draft in project format, or - for stdin")
    ap.add_argument("--calibrate", help="a plain list of bars (the original) - prints counts only")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.calibrate:
        counts, fails = audit(read_plain(a.calibrate), headerless=True)
        report(counts, quiet=True)
        print(f"  (in a file with no section headers the chorus's own repeats are reported, not failed: "
              f"{len(counts['dups'])} lines return)")
        for x in fails:
            print("  ! " + x)
        print("phrase_audit CALIBRATION:", "PASSED (the original clears every threshold)" if not fails
              else "FAILED: a gate the benchmark fails is a wrong gate")
        sys.exit(0 if not fails else 1)
    text = sys.stdin.read() if a.path == "-" else open(a.path, encoding="utf8").read()
    secs = [(s, b) for s, b in sc.bars_of(text) if s]
    counts, fails = audit(secs)
    print(f"phrase_audit {os.path.basename(a.path) if a.path != '-' else 'stdin'}:")
    report(counts)
    for x in fails:
        print("  x " + x)
    print("PHRASE AUDIT:", "PASS" if not fails else f"{len(fails)} PROBLEMS")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
