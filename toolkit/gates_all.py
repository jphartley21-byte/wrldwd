"""gates_all: EVERY gate in one command, each fired flag printed by bar; hard gates exit non-zero.

  python toolkit/gates_all.py FILE                 a draft in "== Slot" format (any subset of the 10 slots)
  python toolkit/gates_all.py FILE --slot "Hook 5-8"   one section of that draft
  python toolkit/gates_all.py --original PATH      the original, one line per bar (private; prints numbers, never lines)
  python toolkit/gates_all.py --selftest

Built 14 Oct 2026 (Joe's launch brief, point 4): ten separate tools had to be run and read one by one, and a flag that
fired in one of them was easy to lose in a block total (the "two glasses, cold lager" and "numbers on folders" bars both
got through that way). This tool runs them all and prints, PER BAR, every flag that fired, with the gate's name.

WHICH GATES ARE HARD (exit 1) -- the rule is the repo's own: a gate the ORIGINAL fails is a wrong gate, so a gate is hard
only if the original clears it (checked with --original on the pasted original, 14 Oct 2026; see STATE.md):
  HARD  timefit2      strict timing fit vs the original's audio steps (bar limit = the original's p95, section limit =
                      its worst section + half its range; benchmark/timefit2_baseline.json)
  HARD  rhymedepth    end-rhyme depth floor = the original's median for the slot (3-deep in V1 17-24)
  HARD  meaning       meaning_gate per section (only its bar-level and inventory rules; see SOFT_MEANING)
  HARD  coherence     coherence_gate per section (unresolved pronouns, generic bars; bare indefinites and imageless
                      fragments only above the original's own rate, 2 per section)
  HARD  regression    on the HOOK (local word per 4 bars, no admin word in a rhyme slot, no word > 3x)
  HARD  phrase_audit  song: duplicate lines, tic openers, repeated 4-grams, comma flood
  HARD  characters    song: 2 references per person (Joe's cap)
  HARD  songcheck     song: level gates (places, local words, device rate, type/token) -- only when all 10 slots exist,
                      because its song-level counts are meaningless on a partial draft
  RANK  check_all     form problems per section: a RANKING target, not a veto (Joe, 11 Oct 2026); flags printed by bar
  NOTE  frameecho     adjacent bars finishing on one frame (report-only)
Validated on the pasted original (14 Oct 2026, --original): it clears every hard gate EXCEPT two that are Joe's own rules,
stricter than the benchmark on purpose: the timefit2 BAR limit is the original's 95th percentile, so 4 of its own 74 bars sit
over it by construction (Joe: "bar <= ~3.00", now 2.55 after the WWE fix); and the character cap of 2 (the original has
'mate' x4 and 'boy' x3). Everything else the original trips is printed as a NOTE.
"""
import contextlib, io, json, os, re, statistics, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timefit as tf          # noqa: E402
import timefit2 as t2         # noqa: E402

SLOTS = list(tf.SIZES.items())
STARTS, _s = {}, 1
for _n, _k in SLOTS:
    STARTS[_n] = _s
    _s += _k
# meaning_gate rules the ORIGINAL itself trips (its end-word rules fire on two of its own lines, and its
# draft-level caps assume a 16-bar block): reported, never failed.
COH_RATE_MAX = 2   # the original's worst section has 2 bare-indefinite/imageless bars
SOFT_MEANING = ("ends on", "end word", "opener", "bars end on a pronoun", "places in consecutive", "bars name a place")


def _quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


def read_draft(path, text=None):
    text = text if text is not None else open(path, encoding="utf8").read()
    secs, cur = {}, None
    for l in text.lstrip("﻿").splitlines():
        l = l.strip()
        if l.startswith("=="):
            cur = l.strip("= ").strip()
            secs[cur] = []
        elif l and cur and not l.startswith(("[", "#", "(")):
            secs[cur].append(l)
    return {k: v for k, v in secs.items() if k in tf.SIZES}


def plain_to_secs(path):
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
    secs, i = {}, 0
    for n, k in SLOTS:
        secs[n] = lines[i:i + k]
        i += k
    return secs


def _bar_no(msg):
    m = re.match(r"\s*(?:bar\s+)?(\d+)[.:]", msg)
    return int(m.group(1)) if m else None


def run_all(secs, only=None, with_check_all=True):
    """-> {"bars": {(slot, i): [(gate, kind, msg)]}, "sections": {slot: [(gate, kind, msg)]}, "song": [...], "summary": {...}}"""
    flags_bar, flags_sec, song, summary = {}, {}, [], {}
    want = [s for s, _ in SLOTS if s in secs and (only is None or s == only)]

    def fb(slot, i, gate, kind, msg):
        flags_bar.setdefault((slot, i), []).append((gate, kind, msg))

    def fs(slot, gate, kind, msg):
        flags_sec.setdefault(slot, []).append((gate, kind, msg))

    # timefit2 -----------------------------------------------------------------------------------------------
    t2.load_params()
    base = json.load(open(t2.BASE2))
    sm = base["section_mean"]
    hi, lo = max(sm.values()), min(sm.values())
    thr = hi + 0.5 * (hi - lo)
    bs = sorted(base["bar_costs"])
    bar_lim = bs[int(len(bs) * 0.95)]
    res = t2.section_scores2(secs)
    summary["timefit2_limits"] = (round(bar_lim, 2), round(thr, 2))
    for slot in want:
        rows = res[slot]
        cs = []
        for k, (line, r) in enumerate(rows, 1):
            if line is None:
                fs(slot, "timefit2", "HARD", "bar %d missing" % k)
            elif r is None:
                fb(slot, k, "timefit2", "NOTE", "no audio steps in the template: judged by ear")
            else:
                cs.append(r[0])
                if r[0] > bar_lim:
                    fb(slot, k, "timefit2", "HARD", "cost %.2f > bar limit %.2f: %s" % (r[0], bar_lim, "; ".join(r[1][:4])))
                elif r[1]:
                    fb(slot, k, "timefit2", "NOTE", "cost %.2f: %s" % (r[0], "; ".join(r[1][:3])))
        mean = statistics.mean(cs) if cs else None
        summary.setdefault("timefit2_mean", {})[slot] = round(mean, 2) if mean is not None else None
        if mean is not None and mean > thr:
            fs(slot, "timefit2", "HARD", "section mean %.2f > limit %.2f" % (mean, thr))

    # rhymedepth ---------------------------------------------------------------------------------------------
    import rhymedepth as rd
    st, _ = _quiet(rd.stats, secs)
    for slot in want:
        v = st.get(slot)
        if not v:
            continue
        summary.setdefault("rhymedepth", {})[slot] = {"depths": v["depths"], "median": v["median"], "target": v["target"],
                                                      "multisyl": v["multisyl"], "multisyl_orig": v["multisyl_orig"],
                                                      "beat": (v["beat_step"], v["beat_beat"], v["beat_half"]), "full": v["full"]}
        for h in v["hard"]:
            fs(slot, "rhymedepth", "HARD", h)
        for w in v["warn"]:
            fs(slot, "rhymedepth", "NOTE", w)
        for k, d in enumerate(v["depths"], 1):
            if d is not None and v["target"] and d < v["target"]:
                fb(slot, k, "rhymedepth", "NOTE", "end depth %d < the slot's median %d" % (d, v["target"]))

    # meaning + coherence, per section -----------------------------------------------------------------------
    import meaning_gate as mg
    import coherence_gate as cg
    for slot in want:
        bars = secs[slot]
        r, _ = _quiet(mg.audit, bars, slot)
        for i, b, hard, issues in r["bars"]:
            for h in hard:
                fb(slot, i, "meaning", "NOTE" if any(s in h for s in SOFT_MEANING) else "HARD", h)
            for x in issues:
                if x not in hard:
                    fb(slot, i, "meaning", "NOTE", x)
        for f in r["fails"]:
            if not f.startswith("bar "):
                fs(slot, "meaning", "NOTE" if any(s in f for s in SOFT_MEANING) else "HARD", f)
        c, _ = _quiet(cg.audit, bars)
        # The ORIGINAL trips the bare-indefinite and imageless-fragment rules itself ("I tell a man ..."): 6 times in 76
        # bars, at most 2 in one section (--original, 14 Oct 2026). So those two are HARD only above that rate.
        rate_kinds = ("bare indefinite", "fragment with no image")
        n_rate = sum(1 for f in c["fails"] if any(k in f for k in rate_kinds))
        for f in c["fails"]:
            n = _bar_no(f)
            kind = "HARD" if not any(k in f for k in rate_kinds) or n_rate > COH_RATE_MAX else "NOTE"
            (fb(slot, n, "coherence", kind, f.split(":", 1)[1].strip()) if n else fs(slot, "coherence", kind, f))
        for w in c.get("warns", []):
            fs(slot, "coherence", "NOTE", w)

    # check_all (RANK) ---------------------------------------------------------------------------------------
    if with_check_all:
        import check_all as ca
        for slot in want:
            ok, problems, waived, rare = ca.problems_of(slot, secs[slot])
            summary.setdefault("check_all", {})[slot] = len(problems)
            for p in problems:
                kind, _, msg = p.partition(": ")
                n = _bar_no(msg)
                if n is not None and kind == "flow":
                    n = n - STARTS[slot] + 1
                (fb(slot, n, "check_all", "RANK", kind + ": " + msg.split("|")[-1].strip()[:150] if kind == "flow" else kind + ": " + msg.split("|")[0][:150])
                 if n and 1 <= n <= len(secs[slot]) else fs(slot, "check_all", "RANK", p[:170]))

    # regression on the hook ---------------------------------------------------------------------------------
    import regression as rg
    hook = [b for s in ("Hook 1-4", "Hook 5-8", "Hook 9-16") if s in want for b in secs[s]]
    if hook:
        places, loans = rg.load_supply()
        rows, fails = rg.check(hook, places, loans)
        for f in fails:
            song.append(("regression", "HARD", "hook: " + f))
        summary["regression_rows"] = [r.strip() for r in rows]

    # song-level gates ---------------------------------------------------------------------------------------
    pairs = [(s, secs[s]) for s in want]
    if only is None:
        import phrase_audit as pa
        counts, fails = pa.audit(pairs)
        full = len(want) == len(SLOTS)
        for f in fails:
            # the comma rate is a SONG rate (the original is 25%); on a 4-bar block one comma is 25%, so it is not gated there
            soft = "carry a comma" in f and not full
            song.append(("phrase_audit", "NOTE" if soft else "HARD", f + (" (partial draft: not gated)" if soft else "")))
        import characters as ch
        allb = [b for _, bb in pairs for b in bb]
        for f in ch.over_cap(allb):
            song.append(("characters", "HARD", f))
        song.append(("characters", "NOTE", ch.preference(allb)))
        import songcheck as sc
        fails, out = _quiet(sc.run, pairs, None)
        for f in fails:
            song.append(("songcheck", "HARD" if full else "NOTE", f + ("" if full else " (partial draft: not gated)")))
        import frameecho as fe
        bl = [b for _, bb in pairs for b in bb]
        for i, j, e in fe.pairs(bl):
            song.append(("frameecho", "NOTE", "song bars %d-%d finish on one frame (%s)" % (i, j, e)))
    return {"bars": flags_bar, "sections": flags_sec, "song": song, "summary": summary, "want": want}


def show(secs, R, print_lines=True):
    hard = 0
    lim = R["summary"].get("timefit2_limits")
    print("gates_all | timefit2 limits: bar %.2f, section %.2f (from the original alone)" % lim)
    for slot in R["want"]:
        tm = R["summary"].get("timefit2_mean", {}).get(slot)
        rd_ = R["summary"].get("rhymedepth", {}).get(slot, {})
        ca = R["summary"].get("check_all", {}).get(slot)
        print("\n== %s | timefit2 mean %s | end depth %s (median %s, original %s) | multisyl %s/%s | beat-matched internals %s full %s | check_all %s"
              % (slot, tm, rd_.get("depths"), rd_.get("median"), rd_.get("target"), rd_.get("multisyl"), rd_.get("multisyl_orig"),
                 rd_.get("beat"), rd_.get("full"), ca))
        for k, line in enumerate(secs[slot], 1):
            fl = R["bars"].get((slot, k), [])
            mark = "x" if any(x[1] == "HARD" for x in fl) else ("~" if fl else " ")
            print(" %s %2d %s" % (mark, k, line if print_lines else "(%d words)" % len(line.split())))
            for gate, kind, msg in fl:
                hard += kind == "HARD"
                print("        %-4s %-10s %s" % (kind, gate, (msg if print_lines else msg.split(":")[0])[:190]))
        for gate, kind, msg in R["sections"].get(slot, []):
            hard += kind == "HARD"
            print("   [section] %-4s %-10s %s" % (kind, gate, msg[:190]))
    if R["song"]:
        print("\n== SONG")
        for gate, kind, msg in R["song"]:
            hard += kind == "HARD"
            print("   %-4s %-12s %s" % (kind, gate, msg[:200]))
    print("\nGATES_ALL VERDICT: %s (%d hard flags)" % ("FAIL" if hard else "PASS", hard))
    return hard


def selftest():
    import fixtures
    p = []
    good = {"Hook 1-4": list(fixtures.joe_bars())[:4]}
    R = run_all(good, with_check_all=False)
    if "Hook 1-4" not in R["summary"].get("timefit2_mean", {}):
        p.append("timefit2 did not score the positive control")
    if not R["summary"].get("rhymedepth", {}).get("Hook 1-4"):
        p.append("rhymedepth did not run")
    if any(k == "HARD" for g, k, m in R["song"] if g in ("phrase_audit", "characters")):
        p.append("the positive control tripped a song gate: %s" % R["song"])
    bad = {"V2 9-16": ["My mate is in Bilbao again", "My mate is in Bilbao again", "My mate said go and my mate said no", "Bag map pass rail kit"]}
    R2 = run_all(bad, with_check_all=False)
    gates = {g for g, k, m in R2["song"] if k == "HARD"} | {g for v in R2["bars"].values() for g, k, m in v if k == "HARD"}
    for need in ("phrase_audit", "characters"):
        if need not in gates:
            p.append("%s did not fire on a duplicate line / a 4x mate" % need)
    hard, _ = _quiet(show, bad, R2)
    if not hard:
        p.append("the bad block printed no hard flags")
    if _bar_no("bar 3: x") != 3 or _bar_no("11. FAIL | x") != 11:
        p.append("bar-number parser")
    return (not p, "; ".join(p) if p else "every gate runs, the positive control clears the song gates, a duplicate line and a 4x mate fail hard")


def main():
    a = sys.argv[1:]
    if a[:1] == ["--selftest"]:
        ok, m = selftest()
        print(("PASSED: " if ok else "FAILED: ") + m)
        sys.exit(0 if ok else 1)
    if a[:1] == ["--original"]:
        secs = plain_to_secs(a[1])
        R = run_all(secs)
        sys.exit(1 if show(secs, R, print_lines=False) else 0)
    if not a:
        print(__doc__)
        return
    only = a[a.index("--slot") + 1] if "--slot" in a else None
    path = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--slot")][-1]
    secs = read_draft(path)
    R = run_all(secs, only=only)
    sys.exit(1 if show(secs, R) else 0)


if __name__ == "__main__":
    main()
