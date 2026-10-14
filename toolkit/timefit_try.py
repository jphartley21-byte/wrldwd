"""timefit_try: the inner loop for fitting a bar to the original's timing (stress + syllable length + mouth), via timefit2.
  python toolkit/timefit_try.py grid N                       target stress pattern of template bar N (1-76) and its steps
  python toolkit/timefit_try.py bar N "line one" "line two"  cost + flags of each candidate for bar N, best first
  python toolkit/timefit_try.py gen N "a|b" "c|d|" ...       every combination of the slot options (empty option = skip), best first
  python toolkit/timefit_try.py section "Slot name" FILE     per-bar cost of one section of a draft against its bars
Report-only, no model calls. Bar numbers count the 76 unique bars in SIZES order (Hook 1-4 = 1-4, ... V2 9-16 = 69-76).
Stable tie order matters: template syllables on the same step keep their listed order (a sort on (step, weak) mis-built eight targets, 15 Oct 2026).
"""
import itertools, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timefit as tf  # noqa: E402
import timefit2 as t2  # noqa: E402


def target(bar):
    b = tf.bars_t()[bar - 1]
    if not b.get("steps"):
        return None, []
    pairs = sorted(zip(b["steps"], b["weak"]), key=lambda x: x[0])
    return "".join("w" if w else "S" for _, w in pairs), [s for s, _ in pairs]


def pattern(line):
    return "".join("S" if d[0] else "w" for d in tf.sylinfo(line))


def rank(bar, lines):
    t2.load_params()
    b = tf.bars_t()[bar - 1]
    rows = []
    for l in lines:
        r = t2.fit2(l, b)
        if r:
            rows.append((round(r[0], 2), pattern(l), l, r[1]))
    rows.sort(key=lambda x: x[0])
    return rows


def gen(bar, slots):
    opts = [s.split("|") for s in slots]
    return rank(bar, [" ".join(x for x in c if x) for c in itertools.product(*opts)])


def show(bar, rows, top=5, flags=False):
    tp, _ = target(bar)
    print("bar %d target %s%s" % (bar, tp, "" if tp else " (no audio steps: judge by ear)"))
    for c, p, l, f in rows[:top]:
        print("  %.2f %s  %s" % (c, p, l))
        if flags and f:
            print("        " + "; ".join(f[:4]))


def selftest():
    t2.load_params()
    p = []
    tp, st = target(5)
    if not tp or len(tp) != len(st):
        p.append("grid broken")
    rows = rank(5, ["Cold beer on the house in Porto", "Cold beer on the house in Porto Oslo Bilbao Madrid Rome"])
    if len(rows) != 2 or not rows[0][0] <= rows[1][0]:
        p.append("rank order wrong")
    g = gen(5, ["Cold beer|Warm beer", "on the house in Porto"])
    if len(g) != 2:
        p.append("gen should expand 2 x 1 combinations")
    return (not p, "; ".join(p) if p else "grid, rank and gen run; overlong candidate ranks worse")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--selftest"]:
        ok, m = selftest(); print(("PASSED: " if ok else "FAILED: ") + m); sys.exit(0 if ok else 1)
    if a[:1] == ["grid"]:
        tp, st = target(int(a[1])); print(tp, st)
    elif a[:1] == ["bar"]:
        show(int(a[1]), rank(int(a[1]), a[2:]), top=len(a) - 2, flags=True)
    elif a[:1] == ["gen"]:
        show(int(a[1]), gen(int(a[1]), a[2:]), top=8, flags=True)
    elif a[:1] == ["section"]:
        secs = tf.parse(a[2]); t2.load_params()
        i = 0
        for slot, n in tf.SIZES.items():
            if slot == a[1]:
                for k, l in enumerate(secs[slot]):
                    r = t2.fit2(l, tf.bars_t()[i + k])
                    print("%2d %s %s" % (k + 1, ("%.1f" % r[0]) if r else "ear", l))
            i += n
    else:
        print(__doc__)
