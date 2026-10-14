"""Frame echo (15 Oct 2026, report-only): adjacent bars that finish on the SAME frame - near-equal stress pattern over the
last 5 syllables AND a repeated content/pronoun word in the last 6 words ("I'm running ..." in both). Joe heard this as the
second bar flowing because it reuses the first bar's shape with one word swapped; no earlier instrument saw it
(flowshape's cross-bar stress agreement is a whole-song average, ear.py echo wants the same consonant frame, anaphora wants 3 bars).

  python toolkit/frameecho.py --selftest
  python toolkit/frameecho.py FILE|-      (one bar per line; blank lines and [..] / == lines ignored; duplicates dropped)
  python toolkit/frameecho.py --calibrate PATH   (counts only: pairs found per 100 adjacent pairs)
"""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from flow_fit import sylls

TAILN, AGREE = 5, 4
STOP = set("a an the and but or so to of in on at for with by from as is it its that this then than be was were are am do did my me we our you your he she they them their his her him us when if not no up out down off over".split())


def words(l):
    return [w.lower() for w in re.findall(r"[A-Za-z'å]+", l)]


def tail_pat(l):
    s = sylls(l)
    return ["w" if x else "S" for x in s][-TAILN:]


def echo(a, b):
    """(agree, shared_words) or None. Needs >= AGREE of TAILN positions equal (aligned from the end) and a shared non-stop word in the last 6 words"""
    pa, pb = tail_pat(a), tail_pat(b)
    n = min(len(pa), len(pb))
    if n < TAILN:
        return None
    ag = sum(x == y for x, y in zip(pa[::-1], pb[::-1]))
    sh = [w for w in set(words(a)[-6:]) & set(words(b)[-6:]) if w not in STOP]
    return (ag, sh) if ag >= AGREE and sh else None


def bars(text):
    out, seen = [], set()
    for l in text.splitlines():
        l = l.strip()
        if not l or l.startswith(("[", "==", "#")) or l in seen:
            continue
        seen.add(l)
        out.append(l)
    return out


def pairs(bs):
    return [(i + 1, i + 2, e) for i, (a, b) in enumerate(zip(bs, bs[1:])) for e in [echo(a, b)] if e]


def selftest():
    p = []
    if not echo("Come and get it when I'm running on my lonesome", "Sawn off nah I'm running with a long one"):
        p.append("shared 'running' frame not found")
    if echo("Cold beer on the house in Porto", "Bought it by the barrel off the sellers"):
        p.append("unrelated bars flagged")
    if echo("Keep the dome bald on top", "Wife in Gibraltar brought that back for me"):
        p.append("unrelated bars flagged (2)")
    return (not p, "; ".join(p) if p else "shared-frame pair found, unrelated pairs quiet")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok, m = selftest()
        print(("PASSED: " if ok else "FAILED: ") + m)
        sys.exit(0 if ok else 1)
    cal = "--calibrate" in sys.argv
    src = sys.argv[sys.argv.index("--calibrate") + 1] if cal else sys.argv[-1]
    bs = bars(sys.stdin.read() if src == "-" else open(src, encoding="utf8").read())
    ps = pairs(bs)
    if cal:
        print("%d adjacent pairs, %d frame echoes (%.1f per 100); bars %s" % (len(bs) - 1, len(ps), 100 * len(ps) / max(1, len(bs) - 1), [(a, b) for a, b, _ in ps]))
    else:
        for a, b, (ag, sh) in ps:
            print("bars %d-%d: tail pattern %d/%d equal, shared %s" % (a, b, ag, TAILN, sh))
        print("%d frame echo(es) in %d bars" % (len(ps), len(bs)))
