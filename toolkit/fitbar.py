"""fitbar: the FIT step, last in the process (claim first, then fit; 14 Oct 2026).

Promoted from the session scripts that took the flow-fitted redraft (writing/detection_test/travel_draft_v5.md) to 74/74 bars on the
original's audio frame and 136/137 by-ear rhyme pairs. It only re-prints what the repo's own instruments say:
  * toolkit/flow_fit.fit per bar (syllables +-1, strong/weak agreement, end shape, rhyme start step, weak-on-beat vs par)
  * the by-ear scheme (match.MANUAL_SCHEME) pair by pair: heard if the grader (match.best_end >= 0.78) OR rapfit (>= 0.50) hears it
  * rapfit.check_block (the stress-anchored rhyme rule and the three-syllable-tail rule of V1 17-24)
  * toolkit/recount.py per section (the claim-not-diary check), so a fit never hides a recount

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
GRADER_FLOOR, RAPFIT_FLOOR = 0.78, 0.50
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


def try_bar(bar, line):
    """(ok, syllables, frame length, agreement 0-1, our end shape, frame end shape, our pattern, frame pattern, why)."""
    t = ff.T[bar - 1]
    if "steps" not in t:   # a bar with no audio template (no vocal detected in the original, e.g. song bar 10): free
        w = ff.sylls(line)
        return (None, len(w), 0, 1.0, ff.end_shape(line)[0], "-", pattern(bar, line), "-", "")
    ow = t["weak"]
    w = ff.sylls(line)
    m = min(len(w), len(ow))
    agree = sum(w[i] == ow[i] for i in range(m)) / max(1, len(ow))
    ok, txt = ff.fit(bar, line)
    why = txt.split("FAIL: ")[-1] if "FAIL" in (txt or "") else ""
    why = re.sub(r"strong/weak pattern \S+ vs original \S+ ", "pattern ", why)
    return (ok, len(w), len(t["steps"]), agree, ff.end_shape(line)[0], t["end_shape"], pattern(bar, line),
            "".join("w" if x else "S" for x in ow), why)


def print_try(bar, line):
    ok, n, nf, ag, es, fes, pat, tgt, why = try_bar(bar, line)
    print(f"{bar:>2} {'PASS' if ok else ('free' if ok is None else 'fail')} {n:>2}/{nf:<2} {int(ag * 100):>3}% {es:5s}/{fes:5s} "
          f"{pat:24s} tgt {tgt:16s} | {line}" + (f"\n      {why[:170]}" if why else ""))
    return ok


def read_draft(path):
    out, cur = {}, None
    for l in open(path, encoding="utf-8-sig"):
        l = l.strip()
        if l.startswith("=="):
            cur = l[2:].strip()
            out[cur] = []
        elif l and not l.startswith(("#", "[", "(")) and cur:
            out[cur].append(l)
    return out


def scheme_pairs(slot, bars):
    """[(i, j, letter, grader, rapfit, heard)] for every pair the by-ear scheme puts in one group."""
    from ww.write import rapfit
    sch = match.MANUAL_SCHEME[slot]
    out = []
    for i, j in itertools.combinations(range(min(len(bars), len(sch))), 2):
        if sch[i] == sch[j]:
            g = match.best_end(bars[i], bars[j])
            rp = rapfit.score(bars[i], bars[j])["score"]
            out.append((i, j, sch[i], g, rp, g >= GRADER_FLOOR or rp >= RAPFIT_FLOOR))
    return out


def song(path, quiet=False):
    """verify a whole draft. Returns a dict of the headline numbers."""
    use_ww()
    from ww.write import rapfit
    import recount
    D = read_draft(path)
    tot = ok = 0
    fails = []
    for s in SLOTS:
        for i, b in enumerate(D.get(s, [])):
            r, txt = ff.fit(STARTS[s] + i, b)
            if r is None:
                continue
            tot += 1
            ok += bool(r)
            if not r:
                fails.append((STARTS[s] + i, b, (txt or "").split("FAIL: ")[-1][:140]))
    heard = total = 0
    misses = []
    for s in SLOTS:
        for i, j, L, g, rp, h in scheme_pairs(s, D.get(s, [])):
            total += 1
            heard += h
            if not h:
                misses.append(f"{s} {i + 1}-{j + 1} ({L}): grader {g:.2f} rapfit {rp:.2f}")
    hard = {s: rapfit.check_block(s, D[s])["hard"] for s in SLOTS if D.get(s)}
    hard = {s: h for s, h in hard.items() if h}
    rfails, rows, share = recount.run([(s, D[s]) for s in SLOTS if D.get(s)], overlap=False, quiet=True)
    if not quiet:
        print(f"flow_fit: {ok}/{tot} bars on the original's audio frame (the original scores 74/76 on its own)")
        for f in fails:
            print("   FAIL", f)
        print(f"by-ear scheme pairs heard by the grader or rapfit: {heard}/{total}")
        for m in misses:
            print("   unheard", m)
        for s, h in hard.items():
            print("   rapfit HARD", s, h)
        print(f"recount: song share {share:.0%} (the original 20%); {len(rfails)} problems")
        for f in rfails:
            print("   recount", f)
    return {"flow": (ok, tot), "pairs": (heard, total), "rapfit_hard": sum(len(h) for h in hard.values()),
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
        chk(f"the v5 redraft stays on the frame (got {r['flow']})", r["flow"][0] >= 72)
        chk(f"the v5 redraft's scheme pairs are heard (got {r['pairs']})", r["pairs"][0] >= r["pairs"][1] - 2)
        chk("v5 is still a recount (the measure must see it)", r["recount_fails"] > 0)
    pairs = scheme_pairs("Hook 5-8", ["Cash back on the bier in Zurich", "Stuck in the black van in all the traffic",
                                      "Sitting back with a real panic", "Might pack the backpack in Munich"])
    chk("a perfect carpet is heard pair by pair", pairs and all(p[5] for p in pairs))
    chk("a candidate bar returns a verdict", try_bar(5, "Cash back on the bier in Zurich")[1] > 0)
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
