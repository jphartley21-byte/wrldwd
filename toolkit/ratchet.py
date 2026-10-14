"""ratchet: accept a new draft only if NOTHING got worse.
  python toolkit/ratchet.py OLD_DRAFT NEW_DRAFT
Fails (exit 1) if: a section that passed check_all now fails; a section's problem count rose; a keeper phrase or place
(toolkit/keepers.json) disappeared; a locked line changed; a section that passed the timefit2 fit (stress + syllable length + mouth vs the original) now fails, its bars over the limit rose, or its mean cost rose by 0.25+. Use it after every pass: if it fails, revert that change.
"""
import io, json, os, sys, contextlib
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_all  # noqa: E402
import timefit as _tf  # noqa: E402
import timefit2 as _t2  # noqa: E402
import rhymedepth as _rd  # noqa: E402


def lines_of(path):
    # "==" section headers were counted as BARS, so every slot window was shifted by the number of headers
    # before it and the ratchet reported problem counts for the wrong block ("Hook 9-16 rose 15 -> 16" with
    # no bar changed, 12 Oct 2026). blockcheck and songcheck already skip them.
    return [l.strip() for l in open(path, encoding="utf8")
            if l.strip() and not l.startswith(("[", "#", "(", "=="))]


def section_status(lines):
    out, i = {}, 0
    for slot, size in check_all.SIZES.items():
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = check_all.check(slot, lines[i:i + size])
        out[slot] = (ok, sum(1 for l in buf.getvalue().splitlines() if l.strip().startswith("x ")))
        i += size
    return out


def timefit_status(lines):
    """per section: (mean cost, bars over the original-only bar limit). timefit2 = stress + syllable length + mouth joins vs the original's timing."""
    import json, statistics
    _t2.load_params()
    base = json.load(open(_t2.BASE2))
    bs = sorted(base["bar_costs"]); lim = bs[int(len(bs) * 0.95)]
    sm = base["section_mean"]; thr = max(sm.values()) + 0.5 * (max(sm.values()) - min(sm.values()))
    secs, i = {}, 0
    for slot, n in _tf.SIZES.items():
        secs[slot] = lines[i:i + n]; i += n
    out = {}
    for slot, rows in _t2.section_scores2(secs).items():
        cs = [r[0] for _, r in rows if r]
        out[slot] = (statistics.mean(cs) if cs else 0.0, sum(1 for c in cs if c > lim), thr)
    return out


def rhyme_status(lines):
    secs, i = {}, 0
    for slot, n in _tf.SIZES.items():
        secs[slot] = lines[i:i + n]; i += n
    return _rd.stats(secs)


def keepers_report(text, K):
    t = text.lower()
    return [p for p in K["phrases"] + K["places"] if p.lower() not in t]


if __name__ == "__main__":
    old, new = sys.argv[1], sys.argv[2]
    K = json.load(open(os.path.join(HERE, "keepers.json"), encoding="utf8"))
    lo, ln = lines_of(old), lines_of(new)
    so, sn = section_status(lo), section_status(ln)
    bad = []
    for slot in so:
        (ok_o, n_o), (ok_n, n_n) = so[slot], sn[slot]
        if ok_o and not ok_n:
            bad.append(f"{slot}: passed before, fails now")
        elif n_n > n_o:
            bad.append(f"{slot}: problems rose {n_o} -> {n_n}")
    to, tn = timefit_status(lo), timefit_status(ln)
    for slot in to:
        (m_o, b_o, thr), (m_n, b_n, _) = to[slot], tn[slot]
        if m_o <= thr < m_n:
            bad.append(f"{slot}: timefit2 passed before, fails now ({m_o:.2f} -> {m_n:.2f}, limit {thr:.2f})")
        elif b_n > b_o:
            bad.append(f"{slot}: timefit2 bars over the limit rose {b_o} -> {b_n}")
        elif m_n > m_o + 0.25:
            bad.append(f"{slot}: timefit2 mean cost rose {m_o:.2f} -> {m_n:.2f}")
    print("timefit2 sections over limit: before", [s for s in to if to[s][0] > to[s][2]] or "none", "| after", [s for s in tn if tn[s][0] > tn[s][2]] or "none")
    ro, rn = rhyme_status(lo), rhyme_status(ln)
    for slot in ro:
        o, n = ro[slot], rn[slot]
        if not o or not n:
            continue
        if n["hard"] and not o["hard"]:
            bad.append(f"{slot}: rhyme depth floor now fails ({n['hard'][0]})")
        if (n["median"] or 0) < (o["median"] or 0):
            bad.append(f"{slot}: end rhyme depth median fell {o['median']} -> {n['median']}")
        if (n["multisyl"] or 0) < 0.75 * (o["multisyl"] or 0):
            bad.append(f"{slot}: multisyllabic runs fell {o['multisyl']} -> {n['multisyl']}")
        bo, bn = o["beat_step"] + o["beat_beat"] + o["beat_half"], n["beat_step"] + n["beat_beat"] + n["beat_half"]
        if bn < bo - 1:
            bad.append(f"{slot}: internal rhymes on matched beats fell {bo} -> {bn}")
    lost = [k for k in keepers_report(open(new, encoding="utf8").read(), K) if k not in keepers_report(open(old, encoding="utf8").read(), K)]
    if lost:
        bad.append("keepers lost: " + ", ".join(lost))
    for l in K["locked_lines"]:
        if l not in ln:
            bad.append(f"locked line changed: {l}")
    gained = [s for s in so if not so[s][0] and sn[s][0]]
    print("gained:", gained or "nothing")
    print("RATCHET:", "OK (nothing got worse)" if not bad else "REVERT: " + " | ".join(bad))
    missing_now = keepers_report(open(new, encoding="utf8").read(), K)
    if missing_now:
        print("keepers already missing (win back if possible):", ", ".join(missing_now))
    sys.exit(0 if not bad else 1)
