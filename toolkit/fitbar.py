"""fitbar: the FIT step, last in the process (claim first, then fit; 14 Oct 2026).

Promoted from the session scripts that took the flow-fitted redraft (writing/detection_test/travel_draft_v5.md) to 74/74 bars on the
original's audio frame and 136/137 by-ear rhyme pairs. It only re-prints what the repo's own instruments say:
  * toolkit/flow_fit.fit per bar (syllables +-1, strong/weak agreement, end shape, rhyme start step, weak-on-beat vs par), plus
    slotcheck's per-bar beat rules: a run of 4+ weak syllables FAILS the bar, a hard mouth-shape join is flagged (J)
  * the by-ear scheme (match.MANUAL_SCHEME) pair by pair: heard if rapfit (>= rapfit.FLOOR) hears it; the old grader is a note
  * rapfit.check_block (the stress-anchored rhyme rule and the three-syllable-tail rule of V1 17-24)
  * toolkit/recount.py per section (the claim-not-diary check), so a fit never hides a recount
  * ww/write/slotcheck.check per section: THE GATE (15 Oct 2026). fitbar used to stop at flow_fit + pairs and reported hooks as
    "15/15, all pass" that slotcheck failed on weak runs, mouth-shape joins, a 12-syllable bar 10 and suffix-carried end words.
    `#cash <bar> | <idiom> | <payoff>` lines inside a '== Slot' section are read as that section's declared cashed idioms.
Song bar 10 has no audio template; it is held to the profile's syllable count (slotcheck.spec), not treated as free.

Use it to try candidates for ONE bar against its frame, then to verify a whole draft:
  python toolkit/fitbar.py bars < candidates.txt        lines "N | text" (N = song bar 1-76); prints the frame check per candidate
  python toolkit/fitbar.py bar 33 "text of a candidate"
  python toolkit/fitbar.py song writing/draft.md        a '== Slot' draft: flow, scheme pairs, rapfit, recount
  python toolkit/fitbar.py --selftest
Runs with ww's pronunciation overrides loaded (the same lexicon the writer and slotcheck use); --clean runs the toolkit alone.
"""
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import flow_fit as ff   # noqa: E402
import match            # noqa: E402

SLOTS = ["Hook 1-4", "Hook 5-8", "Hook 9-16", "V1 1-8", "V1 9-16", "V1 17-24", "V1 25-32", "V1 33-44", "V2 1-8", "V2 9-16"]
SIZES = [4, 4, 8, 8, 8, 8, 8, 12, 8, 8]
STARTS = dict(zip(SLOTS, [1 + sum(SIZES[:i]) for i in range(len(SIZES))]))
GRADER_FLOOR = 0.78   # the old grader: printed as a note only (it credits unstressed tails; registry, 13 Oct 2026)
_WW = False


def use_ww():
    """load ww's persisted pronunciation overrides (what the writer, slotcheck and rapfit read)."""
    global _WW
    if not _WW:
        from ww import bridge
        bridge._pron_ready()
        _WW = True


def pattern(bar, line):
    t = ff.T[bar - 1]
    w = ff.sylls(line)
    st = t.get("steps") or []
    return "".join(("w" if w[k] else "S") + ("'" if k < len(st) and st[k] % 4 == 0 else "") for k in range(len(w)))


def slot_of(bar):
    """song bar 1-76 -> (slot, 0-based index inside the slot)."""
    for s, n in zip(SLOTS, SIZES):
        if STARTS[s] <= bar < STARTS[s] + n:
            return s, bar - STARTS[s]
    raise ValueError(bar)


def beat_rules(bar, line):
    """slotcheck's per-bar beat rules: (longest run of weak syllables, hard mouth-shape joins)."""
    from ww.write import slotcheck, earcheck
    s, k = slot_of(bar)
    run = slotcheck.beat_report(s, k, line, STARTS[s] - 1)["run"] if "steps" in ff.T[bar - 1] else 0
    joins = [j for j in earcheck.word_joins(line) if j["score"] >= 2]
    return run, joins


def try_bar(bar, line):
    """(ok, syllables, frame length, agreement 0-1, our end shape, frame end shape, our pattern, frame pattern, why)."""
    from ww.write import slotcheck
    t = ff.T[bar - 1]
    w = ff.sylls(line)
    run, joins = beat_rules(bar, line)
    jtxt = ("J: hard join " + ", ".join(f"{j['a']} {j['b']}" for j in joins)) if joins else ""
    if "steps" not in t:   # no audio template (no vocal detected in the original, e.g. song bar 10): the profile's syllable count
        s, k = slot_of(bar)
        want = slotcheck.spec(s)["sylls"][k]
        ok = abs(len(w) - want) <= 1 and run < 4
        why = "; ".join(x for x in [f"{len(w)} syl, need {want}+-1" if abs(len(w) - want) > 1 else "",
                                    f"{run} weak syllables in a row" if run >= 4 else "", jtxt] if x)
        return (ok, len(w), want, 1.0, ff.end_shape(line)[0], "-", pattern(bar, line), "-", why)
    ow = t["weak"]
    m = min(len(w), len(ow))
    agree = sum(w[i] == ow[i] for i in range(m)) / max(1, len(ow))
    ok, txt = ff.fit(bar, line)
    why = txt.split("FAIL: ")[-1] if "FAIL" in (txt or "") else ""
    why = re.sub(r"strong/weak pattern \S+ vs original \S+ ", "pattern ", why)
    if run >= 4:
        ok, why = False, "; ".join(x for x in [why, f"{run} weak syllables in a row (the original's longest is 3)"] if x)
    ap_ok, ap_k, ap_want = ff.approach(bar, line)
    if ap_ok is False:
        ok, why = False, "; ".join(x for x in [why, f"stress before the rhyme: syllable {ap_k} should be {ap_want}"] if x)
    import flow_par as fp
    pf = fp.check(bar, line)
    if pf:
        ok, why = False, "; ".join(x for x in [why, "PAR " + fp.describe(pf)] if x)
    if jtxt:
        why = "; ".join(x for x in [why, jtxt] if x)
    return (ok, len(w), len(t["steps"]), agree, ff.end_shape(line)[0], t["end_shape"], pattern(bar, line),
            "".join("w" if x else "S" for x in ow), why)


def print_try(bar, line):
    ok, n, nf, ag, es, fes, pat, tgt, why = try_bar(bar, line)
    print(f"{bar:>2} {('PASS' if ok else 'fail') + ('J' if 'J: hard join' in why else ' ')} {n:>2}/{nf:<2} {int(ag * 100):>3}% {es:5s}/{fes:5s} "
          f"{pat:24s} tgt {tgt:16s} | {line}" + (f"\n      {why[:170]}" if why else ""))
    return ok


def read_draft(path, with_cash=False):
    """{slot: [bars]}; with_cash also returns {slot: [cash declarations]} from `#cash <bar> | <idiom> | <payoff>` lines."""
    from ww.write import slotcheck
    out, cash, cur = {}, {}, None
    for l in open(path, encoding="utf-8-sig"):
        l = l.strip()
        if l.startswith("=="):
            cur = l[2:].strip()
            out[cur], cash[cur] = [], []
        elif cur and l.lower().startswith("#cash"):
            cash[cur] += slotcheck.parse_cash(l)[1]
        elif l and not l.startswith(("#", "[", "(")) and cur:
            out[cur].append(l)
    return (out, cash) if with_cash else out


def scheme_pairs(slot, bars):
    """[(i, j, letter, grader, rapfit, heard)] for every pair the by-ear scheme puts in one group."""
    from ww.write import rapfit
    sch = match.MANUAL_SCHEME[slot]
    out = []
    for i, j in itertools.combinations(range(min(len(bars), len(sch))), 2):
        if sch[i] == sch[j]:
            g = match.best_end(bars[i], bars[j])
            rp = rapfit.score(bars[i], bars[j])["score"]
            out.append((i, j, sch[i], g, rp, rp >= rapfit.FLOOR))
    return out


def song(path, quiet=False):
    """verify a whole draft. Returns a dict of the headline numbers."""
    use_ww()
    from ww.write import rapfit, slotcheck
    import recount
    D, C = read_draft(path, with_cash=True)
    tot = ok = 0
    fails = []
    for s in SLOTS:
        for i, b in enumerate(D.get(s, [])):
            r, *_rest, why = try_bar(STARTS[s] + i, b)
            tot += 1
            ok += bool(r)
            if not r:
                fails.append((STARTS[s] + i, b, why[:140]))
    heard = total = 0
    misses = []
    for s in SLOTS:
        for i, j, L, g, rp, h in scheme_pairs(s, D.get(s, [])):
            total += 1
            heard += h
            if not h:
                misses.append(f"{s} {i + 1}-{j + 1} ({L}): rapfit {rp:.2f} (old grader {g:.2f})")
    hard = {s: rapfit.check_block(s, D[s])["hard"] for s in SLOTS if D.get(s)}
    hard = {s: h for s, h in hard.items() if h}
    rfails, rows, share = recount.run([(s, D[s]) for s in SLOTS if D.get(s)], overlap=False, quiet=True)
    full = {s: slotcheck.check(s, D[s], cash=C.get(s) or []) for s in SLOTS if D.get(s)}
    gate = {s: r["hard"] for s, r in full.items()}
    notes = {s: [x for x in slotcheck.report(r).splitlines() if x.startswith(("FLOW bar", "EAR bar"))] + 
                [x for x in r["notes"] if not x.startswith(("recount codes", "cadence"))] for s, r in full.items()}
    if not quiet:
        npass = sum(not h for h in gate.values())
        print(f"slotcheck (THE GATE): {npass}/{len(gate)} sections pass, {sum(len(h) for h in gate.values())} hard issues"
              + ("" if os.environ.get("WW_SENSE", "1") != "0" else "  [sense gate OFF: WW_SENSE=0]"))
        for s, h in gate.items():
            for x in h:
                print(f"   {s}: {x[:220]}")
        nn = sum(len(v) for v in notes.values())
        print(f"slotcheck NOTES (not gates; each must be fixed or listed to Joe with a reason): {nn}")
        for s, v in notes.items():
            for x in v:
                print(f"   {s}: {x[:200]}")
        print(f"per-bar fit (flow_fit + weak runs; bar 10 on the profile count): {ok}/{tot} bars (the original scores 74/76 on flow_fit)")
        for f in fails:
            print("   FAIL", f)
        print(f"by-ear scheme pairs heard by rapfit: {heard}/{total}")
        for m in misses:
            print("   unheard", m)
        for s, h in hard.items():
            print("   rapfit HARD", s, h)
        print(f"recount: song share {share:.0%} (the original 20%); {len(rfails)} problems")
        for f in rfails:
            print("   recount", f)
    return {"flow": (ok, tot), "pairs": (heard, total), "rapfit_hard": sum(len(h) for h in hard.values()),
            "gate_hard": sum(len(h) for h in gate.values()), "gate_pass": sum(not h for h in gate.values()),
            "recount_share": share, "recount_fails": len(rfails)}


def selftest():
    use_ww()
    good = True

    def chk(name, cond):
        nonlocal good
        if not cond:
            good = False
            print("  FAIL", name)

    v5 = os.path.join(ROOT, "writing", "detection_test", "travel_draft_v5.md")
    if os.path.exists(v5):
        r = song(v5, quiet=True)
        # flow_fit alone (the frame this redraft was fitted to); the per-bar count now also applies the rhyme-approach gate
        # (15 Oct 2026), which this rejected diary fails on 11 bars
        D5 = read_draft(v5)
        on = sum(bool(ff.fit(STARTS[s_] + i, b)[0]) for s_ in SLOTS for i, b in enumerate(D5.get(s_, [])))
        chk(f"the v5 redraft stays on the flow_fit frame (got {on})", on >= 72)
        # rapfit alone (no old-grader OR since 15 Oct): it hears 90% of the original's own by-ear pairs at its floor (13 Oct)
        chk(f"the v5 redraft's scheme pairs are heard (got {r['pairs']})", r["pairs"][0] >= 0.9 * r["pairs"][1])
        chk("v5 is still a recount (the measure must see it)", r["recount_fails"] > 0)
    pairs = scheme_pairs("Hook 5-8", ["Hoi Rotterdam beg your pardon", "I've got your gnome and I'm not sorry",
                                      "Fell off the back of a lorry", "Ten feet of it guards my garden"])
    chk("an ABBA of true rhymes is heard pair by pair", pairs and all(p[5] for p in pairs))
    # the old grader passed Zurich ~ Munich at 1.00; the stressed vowels differ, and rapfit (the gate) does not hear it
    zm = scheme_pairs("Hook 5-8", ["Cash back on the bier in Zurich", "Stuck in the black van in all the traffic",
                                   "Sitting back with a real panic", "Might pack the backpack in Munich"])
    chk("a vowel-mismatched pair the old grader passed is not heard", not zm[0][5])
    chk("a candidate bar returns a verdict", try_bar(5, "Cash back on the bier in Zurich")[1] > 0)
    # song bar 10 has no audio template: it is held to the profile's count, never waved through as free (15 Oct 2026)
    chk("a 12-syllable song bar 10 fails", try_bar(10, "Wanted for excessive energy guaranteed")[0] is False)
    chk("a 9-syllable song bar 10 passes the count", "need" not in try_bar(10, "Wanted for too much energy, see")[8])
    chk("a run of 4+ weak syllables fails the bar", try_bar(7, "Picked it up off of a lorry")[0] is False)
    chk("three stresses jammed before the rhyme fail the bar (15 Oct 2026)", try_bar(9, "I'm wanted in Boomtown see")[0] is False)
    import flow_par as fp
    chk("every bar Joe flagged for flow fails the per-bar fit (toolkit/tests/flow_flagged.txt)",
        all(try_bar(b, line)[0] is False for b, line, _ in fp.flagged()))
    print("fitbar selftest:", "PASSED" if good else "FAILED")
    return good


def main():
    args = [a for a in sys.argv[1:] if a != "--clean"]
    if "--clean" not in sys.argv[1:]:
        use_ww()
    if not args or args[0] == "--selftest":
        sys.exit(0 if selftest() else 1)
    if args[0] == "bar":
        sys.exit(0 if print_try(int(args[1]), " ".join(args[2:])) else 1)
    if args[0] == "bars":
        for raw in sys.stdin:
            raw = raw.strip()
            if raw and not raw.startswith("#") and "|" in raw:
                b, line = raw.split("|", 1)
                print_try(int(b), line.strip())
        return
    if args[0] == "song":
        song(args[1])
        return
    print(__doc__)


if __name__ == "__main__":
    main()
