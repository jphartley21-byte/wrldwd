"""rhymedepth: how DEEP the rhymes are and whether the INTERNAL rhymes sit on MATCHED BEATS (Joe, 15 Oct 2026: both are important).
  python toolkit/rhymedepth.py FILE                 per section, per bar (FILE = "== Slot" format or 76 plain bars)
  python toolkit/rhymedepth.py --calibrate PATH     write benchmark/rhymedepth_baseline.json from the original (numbers only; Joe's PC)
  python toolkit/rhymedepth.py --selftest
Three measures, all reported per bar, none collapsed into a total:
 1. END DEPTH   syllables matched between a bar's end and its by-ear scheme mates (rapfit.chain_best). More is better. FLOOR (fails): the
                slot's median depth in the original (benchmark/rhyme_depth_targets.json), and the 3-syllable block rule for V1 17-24.
 2. MULTISYL    multisyllabic rhyme runs (match.quiet_quad) against the original's count for the slot (benchmark/original_profile.json).
                Ranking score + ratchet; below 50% of the original is a named warning.
 3. BEAT-MATCHED INTERNAL RHYME  a stressed syllable that rhymes (same vowel; 'full' if the next consonant matches too) with another stressed syllable
                in the same bar or the next, where BOTH sit on the same 16th step (cross-bar) or exactly half a bar/a bar apart (within a bar), using the
                step each syllable is aligned to by timefit2. 'beat' = same beat (step // 4) but not same step. Two adjacent syllables matching two
                adjacent syllables = an internal MULTI run. The final syllable of every bar is excluded (end rhyme is measure 1).
Report-only for 3 until a baseline from the original exists (the original text is not in the cloud); the ratchet forbids a fall.
"""
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
import timefit as tf  # noqa: E402
import timefit2 as t2  # noqa: E402
import duration as dur  # noqa: E402
import match as mt  # noqa: E402

BASE = os.path.join(HERE, "..", "benchmark", "rhymedepth_baseline.json")
TARGETS = os.path.join(HERE, "..", "benchmark", "rhyme_depth_targets.json")
PROFILE = os.path.join(HERE, "..", "benchmark", "original_profile.json")


def _vowels(line):
    """base vowel (ARPAbet, stress stripped) per syllable, in the SAME order as duration.syllables / timefit.sylinfo, plus the following consonant."""
    out = []
    for w in re.findall(r"[A-Za-z'å]+", line):
        ph = dur.pron(w.lower().replace("å", "a")) or []
        vi = [i for i, p in enumerate(ph) if dur.is_v(p)]
        for k, i in enumerate(vi):
            nxt = dur.strip(ph[i + 1]) if i + 1 < len(ph) and not dur.is_v(ph[i + 1]) else None
            out.append((dur.strip(ph[i]), nxt))
    return out


def syl_table(line, bar):
    """[(vowel, next_consonant, step or None, strong)] per syllable, step from the timefit2 alignment."""
    S = tf.sylinfo(line)
    V = _vowels(line)
    if len(S) != len(V):
        return []
    r = t2.fit2(line, bar)
    step = {}
    if r and r[2].get("pairs"):
        st = r[2]["st"]
        for i, j in r[2]["pairs"]:
            step[i] = st[j]
    return [(V[i][0], V[i][1], step.get(i), S[i][0]) for i in range(len(S))]


def internal(lines, bars):
    """-> per bar list of events {kind: step|beat|half, full: bool, with: bar index, multi: bool}; counted once, at the earlier bar."""
    T = [syl_table(l, b) for l, b in zip(lines, bars)]
    ev = [[] for _ in lines]
    for i, ti in enumerate(T):
        body_i = [k for k in range(len(ti) - 1) if ti[k][3]]
        for j in (i, i + 1):
            if j >= len(T):
                continue
            tj = T[j]
            body_j = [k for k in range(len(tj) - 1) if tj[k][3]]
            for a in body_i:
                for b in body_j:
                    if j == i and b <= a:
                        continue
                    va, vb = ti[a], tj[b]
                    if va[0] != vb[0] or va[2] is None or vb[2] is None:
                        continue
                    d = abs(va[2] - vb[2])
                    if j == i:
                        kind = "half" if d in (8, 16) or (d % 8 == 0 and d) else None
                    else:
                        kind = "step" if d == 0 else ("beat" if va[2] // 4 == vb[2] // 4 else None)
                    if kind is None:
                        continue
                    multi = (a + 1 < len(ti) - 1 and b + 1 < len(tj) - 1 and ti[a + 1][0] == tj[b + 1][0] and (j != i or b + 1 != a))
                    ev[i].append({"kind": kind, "full": va[1] == vb[1], "with": j, "multi": bool(multi), "w": (a, b)})
    return ev


def end_depths(slot, lines):
    from ww.write import rapfit, rhymeview
    sch = mt.MANUAL_SCHEME.get(slot, "")
    n = min(len(lines), len(sch))
    syl = [rapfit._syl(rhymeview.tail_text(l.split())) for l in lines[:n]]
    out = []
    for i in range(n):
        mates = [j for j in range(n) if j != i and sch[j] == sch[i]]
        out.append(max((rapfit.chain_best(syl[i], syl[j])["depth"] for j in mates), default=None))
    return out


def section_report(slot, lines, bars):
    tg = json.load(open(TARGETS)).get(slot, {})
    prof = json.load(open(PROFILE)).get(slot, {})
    depths = end_depths(slot, lines)
    ev = internal(lines, bars)
    ms = mt.quiet_quad(lines).get("multisyl")
    base_ms = (prof.get("quad") or {}).get("multisyl")
    vals = [d for d in depths if d is not None]
    med = sorted(vals)[len(vals) // 2] if vals else None
    hard, warn = [], []
    tm = tg.get("median_depth")
    if tm and med is not None and med < tm:
        hard.append("end rhyme depth median %s is below the original's %s for %s" % (med, tm, slot))
    if tm and tm >= 3:
        for k in range(0, len(lines) - 3, 4):
            blk = [d for d in depths[k:k + 4] if d is not None]
            if sum(1 for d in blk if d >= 3) < 3:
                hard.append("bars %d-%d: %s is a 3-syllable slot; only %d of 4 bars rhyme 3 syllables deep" % (k + 1, k + 4, slot, sum(1 for d in blk if d >= 3)))
    if base_ms and ms is not None and ms < 0.5 * base_ms:
        warn.append("multisyllabic runs %s vs the original's %s (below 50%%)" % (ms, base_ms))
    flat = [e for es in ev for e in es]
    return {"depths": depths, "median": med, "target": tm, "multisyl": ms, "multisyl_orig": base_ms,
            "beat_step": sum(1 for e in flat if e["kind"] == "step"), "beat_beat": sum(1 for e in flat if e["kind"] == "beat"),
            "beat_half": sum(1 for e in flat if e["kind"] == "half"), "full": sum(1 for e in flat if e["full"]),
            "multi_internal": sum(1 for e in flat if e["multi"]), "per_bar": [len(es) for es in ev], "hard": hard, "warn": warn}


def stats(path_or_secs):
    secs = tf.parse(path_or_secs) if isinstance(path_or_secs, str) else path_or_secs
    t2.load_params()
    allb = tf.bars_t()
    out, i = {}, 0
    for slot, n in tf.SIZES.items():
        lines = secs.get(slot, [])[:n]
        out[slot] = section_report(slot, lines, allb[i:i + len(lines)]) if lines else None
        i += n
    return out


def calibrate(path):
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
    secs, i = {}, 0
    for slot, n in tf.SIZES.items():
        secs[slot] = lines[i:i + n]; i += n
    st = stats(secs)
    keep = {s: {k: v[k] for k in ("median", "multisyl", "beat_step", "beat_beat", "beat_half", "full", "multi_internal")} for s, v in st.items() if v}
    json.dump(keep, open(BASE, "w"), indent=1)
    print("wrote", BASE, "(numbers only)")
    for s, v in keep.items():
        print(" ", s, v)


def verdict(path):
    st = stats(path)
    base = json.load(open(BASE)) if os.path.exists(BASE) else {}
    bad = 0
    for slot, v in st.items():
        if not v:
            print("== %s  (missing)" % slot); bad += 1; continue
        b = base.get(slot, {})
        print("== %s  end depth %s (median %s, original %s) | multisyl %s (original %s) | internal on matched beats: step %d beat %d half-bar %d, full %d, multi-run %d%s" % (
            slot, v["depths"], v["median"], v["target"], v["multisyl"], v["multisyl_orig"], v["beat_step"], v["beat_beat"], v["beat_half"], v["full"], v["multi_internal"],
            (" | original: step %s beat %s half %s" % (b.get("beat_step"), b.get("beat_beat"), b.get("beat_half"))) if b else " | original baseline: not yet measured"))
        for h in v["hard"]:
            print("   FAIL", h)
        for w in v["warn"]:
            print("   warn", w)
        bad += bool(v["hard"])
    print("RHYMEDEPTH VERDICT: %s (%d sections fail the depth floor)" % ("FAIL" if bad else "PASS", bad))
    return 1 if bad else 0


def selftest():
    t2.load_params()
    p = []
    bars = tf.bars_t()
    L = ["Slow raft down and in a hard loud flowing", "Every bend the roar of falls growing"]
    ev = internal(L, bars[16:18])
    if not isinstance(ev, list) or len(ev) != 2:
        p.append("internal shape")
    tb = syl_table(L[0], bars[16])
    if not tb or len(tb) != 10:
        p.append("syl_table length %s" % len(tb))
    d = end_depths("V1 1-8", ["Slow raft down and in a hard loud flowing", "Every bend the roar of falls growing"] + ["x"] * 6)
    if d[0] is None or d[0] < 2:
        p.append("flowing/growing should be depth >= 2, got %s" % d[:2])
    return (not p, "; ".join(p) if p else "syllable table, matched-beat internal rhyme and end depth run; flowing/growing is depth >= 2")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--selftest"]:
        ok, m = selftest(); print(("PASSED: " if ok else "FAILED: ") + m); sys.exit(0 if ok else 1)
    elif a[:1] == ["--calibrate"]:
        calibrate(a[1])
    elif a:
        sys.exit(verdict(a[-1]))
    else:
        print(__doc__)
