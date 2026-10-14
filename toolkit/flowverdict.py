"""flowverdict: one PASS/FAIL on FLOW for a whole draft, thresholds taken from the ORIGINAL'S OWN spread (15 Oct 2026).

  python toolkit/flowverdict.py FILE            FILE = "== Slot" sections (as check_all --song) or 76 plain lines
  python toolkit/flowverdict.py --build FILE    (re)write benchmark/flow_verdict_baseline.json from the original (numbers only)
  python toolkit/flowverdict.py --calibrate FILE   leave-one-section-out on the original: no section may fail

WHY: check_all was reporting ALL PASS for anything when a sub-check crashed, and once it ran, the original and an AI-written
song sat 3 vs 138 problems apart. The question left was a defensible threshold, not a fitted one. Per section it measures
five template-laid flow numbers (all from instruments the repo already trusts):
  form   check_all form problems (rhyme scheme the grader can confirm, syllables, ending, flow_fit vs the audio template)
  count  share of bars off the template's syllable count by 2 or more         (flowaudit)
  shape  share of bars whose end shape differs from the template              (flowaudit)
  flags  flow flags per bar                                                   (flowaudit)
  gap    share of bars with a run of 4+ unstressed syllables                  (flowaudit)
A section FAILS a metric when it is worse than the original's worst section by half the original's own range
(hi + 0.5 * (hi - lo)); a section FAILS when 2 or more metrics fail; the draft passes when no section fails.
VALIDATION is leave-one-section-out on the original, so the threshold never sees the section it judges: 0 of 10 original
sections fail (--calibrate asserts it). HONEST LIMITS: every number is measured against the original's own audio template,
so this says "does the draft move like the original", not "is it good"; n is one song and one AI draft, so it is a
calibration of the instruments, not proof of a general quality gate. Joe's ear decides.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
BASE = os.path.join(ROOT, "benchmark", "flow_verdict_baseline.json")
METRICS = ("form", "count", "shape", "flags", "gap")
MARGIN, NEED = 0.5, 2


def sections_of(path):
    from ww.write import flowaudit as fa
    import check_all as ca
    raw = [l.strip() for l in open(path, encoding="utf8") if l.strip()]
    if any(l.startswith("==") for l in raw):
        return fa.parse_draft(path)
    lines = [l for l in raw if not l.startswith(("[", "#", "("))]
    out, i = {}, 0
    for slot, n in ca.SIZES.items():
        out[slot] = lines[i:i + n]; i += n
    return out


def measure(secs):
    from ww.write import flowaudit as fa
    import check_all as ca
    out = {}
    for slot, bars in secs.items():
        r = fa.rates({slot: fa.section_audit(slot, bars)})
        ok, problems, waived, rare = ca.problems_of(slot, bars)
        out[slot] = {"form": len(problems), "count": r["count_err_ge2"], "shape": r["end_shape_mismatch"],
                     "flags": r["flags_per_bar"], "gap": r["gap_ge4"]}
    return out


def threshold(vals, margin=MARGIN):
    lo, hi = min(vals), max(vals)
    return hi + margin * (hi - lo)


def judge(m, base):
    """{slot: [failed metrics]} against baseline sections `base` ({slot: {metric: value}})"""
    th = {k: threshold([b[k] for b in base.values()]) for k in METRICS}
    return {s: [k for k in METRICS if v[k] > th[k]] for s, v in m.items()}, th


def loo(base):
    """leave-one-section-out on the baseline itself: {slot: failed metrics}"""
    res = {}
    for s in base:
        others = {t: v for t, v in base.items() if t != s}
        th = {k: threshold([v[k] for v in others.values()]) for k in METRICS}
        res[s] = [k for k in METRICS if base[s][k] > th[k]]
    return res


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return 0
    if a[0] == "--build":
        json.dump(measure(sections_of(a[1])), open(BASE, "w"), indent=1)
        print("baseline written:", BASE); return 0
    if a[0] == "--calibrate":
        m = measure(sections_of(a[1]))
        bad = {s: f for s, f in loo(m).items() if len(f) >= NEED}
        cells = sum(len(f) for f in loo(m).values())
        print(f"flowverdict leave-one-out on the original: {len(bad)} of {len(m)} sections fail ({cells} metric cells over)")
        return 1 if bad else 0
    base = json.load(open(BASE))
    m = measure(sections_of(a[0]))
    res, th = judge(m, base)
    print("threshold (original's worst section + half its range): " + "  ".join(f"{k} {th[k]:.2f}" for k in METRICS))
    nfail = 0
    for s, v in m.items():
        f = res[s]; bad = len(f) >= NEED; nfail += bad
        print(f"  {s:10s} " + "  ".join(f"{k} {v[k]:5.2f}{'*' if k in f else ' '}" for k in METRICS) + ("   FAIL" if bad else "   ok"))
    print(f"FLOW VERDICT: {'PASS' if not nfail else 'FAIL'} ({nfail} of {len(m)} sections fail; * = worse than the original's own spread)")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
