"""timefit2 (15 Oct 2026, report-only): timefit v1 only ever scored STRESS PLACEMENT (its vowel-time and mouth-join terms never fired on the finished
song: 0 of 74 bars). v2 pins our syllables to the original's in order (an alignment, not a slide) and scores three things per bar:
  STRESS   ours strong/weak against the original's at the aligned step (a skipped original stress costs 1.0, an extra strong syllable of ours 0.6)
  LENGTH   the original's syllable gets a time (its gap to the next onset); our syllable has an inherent length (Klatt, toolkit/duration.py).
           Measured on the original: syllable length tracks its gap (per-bar correlation mean 0.29, 79% of bars positive; with the gaps
           shuffled 0.06). Cost = how far log(need/gap) sits from the original's median beyond the original's own spread.
  MOUTH    a hard join (PanPhon + connected speech) on a gap of one step or less
Baselines (numbers only) come from the original and from Joe's approved bars 1-4 (benchmark/timefit2_baseline.json).

  python toolkit/timefit2.py --selftest
  python toolkit/timefit2.py FILE                 ("== Slot" headers; per bar flags; ACCOUNTED line; verdict)
  python toolkit/timefit2.py --calibrate PATH     (PATH = the private original; writes numbers only)
"""
import json, math, os, sys, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import timefit as tf
import duration as dur
import articulation as art

BASE2 = os.path.join(HERE, "..", "benchmark", "timefit2_baseline.json")
MS_STEP = 60000 / 140 / 4  # a true 16th at 140 BPM = 107 ms
R0, TOL = 1.45, 0.7         # overwritten from the baseline file when present
LF0, LF_W = 0.3, 2.0        # length-follows-gap: the original's median per-bar correlation of syllable length with its gap
W_D = 1.0
SUB_BAD, SKIP_T_S, SKIP_T_W, SKIP_O_S, SKIP_O_W = 1.0, 1.0, 0.3, 0.6, 0.25


def load_params():
    global R0, TOL, LF0
    if os.path.exists(BASE2):
        j = json.load(open(BASE2))
        R0, TOL, LF0 = j.get("R0", R0), j.get("TOL", TOL), j.get("LF0", LF0)


def align(S, tstr, tw):
    """Needleman-Wunsch of our syllables S (strong flags) against the template (weak flags tw). Last pairs with last. -> pairs [(i,j)], cost"""
    n, T = len(S), len(tw)
    INF = 1e9
    dp = [[INF] * (T + 1) for _ in range(n + 1)]
    bk = [[None] * (T + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(T + 1):
            c = dp[i][j]
            if c >= INF:
                continue
            if i < n and j < T:  # pair
                strong_o = S[i][0]
                strong_t = not tw[j]
                sc = 0.0 if strong_o == strong_t else SUB_BAD
                if dp[i + 1][j + 1] > c + sc:
                    dp[i + 1][j + 1] = c + sc; bk[i + 1][j + 1] = (i, j, "p")
            if j < T:  # template step unfilled
                sc = SKIP_T_S if not tw[j] else SKIP_T_W
                if dp[i][j + 1] > c + sc:
                    dp[i][j + 1] = c + sc; bk[i][j + 1] = (i, j, "t")
            if i < n:  # extra syllable of ours
                sc = SKIP_O_S if S[i][0] else SKIP_O_W
                if dp[i + 1][j] > c + sc:
                    dp[i + 1][j] = c + sc; bk[i + 1][j] = (i, j, "o")
    # force the last syllable onto the last step: require final move to be a pair
    best, last = INF, None
    if n and T:
        c = dp[n - 1][T - 1]
        if c < INF:
            sc = 0.0 if S[n - 1][0] == (not tw[T - 1]) else SUB_BAD
            best, last = c + sc, (n - 1, T - 1)
    pairs = []
    if last is None:
        return [], INF
    pairs.append(last)
    i, j = last
    while (i, j) != (0, 0):
        pi, pj, mv = bk[i][j]
        if mv == "p":
            pairs.append((pi, pj))
        i, j = pi, pj
    pairs.reverse()
    return pairs, best


def fit2(line, bar):
    steps = list(bar.get("steps") or [])
    wk = list(bar.get("weak") or [])
    if not steps:
        return None
    wk = wk + [False] * (len(steps) - len(wk))
    pr = sorted(zip(steps, wk), key=lambda x: x[0])
    st = [a for a, _ in pr]
    tw = [b for _, b in pr]
    S = tf.sylinfo(line)
    if not S:
        return None
    pairs, ac = align(S, st, tw)
    flags = []
    cost = ac
    if not pairs:
        return 99.0, ["cannot align"], {}
    # stress flags
    matched_t = set(j for _, j in pairs)
    for j in range(len(st)):
        if j not in matched_t and not tw[j]:
            flags.append("stress missed at step %d" % st[j])
    matched_o = set(i for i, _ in pairs)
    for i in range(len(S)):
        if i not in matched_o and S[i][0]:
            flags.append("%s: extra strong syllable with no step" % S[i][2])
    for i, j in pairs:
        if S[i][0] and tw[j]:
            flags.append("%s: strong on the original's weak step %d" % (S[i][2], st[j]))
        if (not S[i][0]) and (not tw[j]):
            flags.append("%s: weak word on the original's stress at step %d" % (S[i][2], st[j]))
    # length
    dcost = 0.0
    xs, ys = [], []
    for i, j in pairs:
        gp = max((st[j + 1] - st[j]) if j + 1 < len(st) else 4, 0.5)
        xs.append(S[i][1]); ys.append(gp)
    corr = None
    if len(xs) >= 4 and len(set(xs)) > 1 and len(set(ys)) > 1:
        corr = statistics.correlation(xs, ys)
        if corr < LF0:
            dcost += LF_W * (LF0 - corr)
            flags.append("length does not follow the original's timing (correlation %.2f; the original's median is %.2f)" % (corr, LF0))
    for i, j in pairs:
        gap = (st[j + 1] - st[j]) if j + 1 < len(st) else 4
        gap = max(gap, 0.5)
        r = S[i][1] / (gap * MS_STEP)
        lr = abs(math.log(max(r, 1e-3) / R0))
        if lr > TOL and not S[i][7]:
            c = (lr - TOL) * W_D
            dcost += c
            flags.append("%s: %s (needs ~%dms, original gives ~%dms)" % (S[i][2], "too long for its slot" if r > R0 else "too short for its slot", S[i][1], gap * MS_STEP))
    cost += dcost
    # mouth
    for a in range(len(pairs) - 1):
        (i, j), (i2, j2) = pairs[a], pairs[a + 1]
        if i2 != i + 1:
            continue
        A, Bs = S[i], S[i2]
        if A[4] and Bs[3] and A[6] and Bs[5]:
            c = art.join_cost(dur.connected(A[6]), Bs[5])
            if c is not None and not (dur.connected(A[6]) == "N" and Bs[5] in dur.ASSIM_N):
                g = max(st[j2] - st[j], 0.5)
                if c >= dur.JOIN_T and g <= 1:
                    cost += 1.0
                    flags.append("hard mouth join %s|%s (travel %.1f) on a %s-step gap" % (A[2], Bs[2], c, "1" if g >= 1 else "<1"))
    return cost, flags, {"pairs": pairs, "S": S, "st": st, "tw": tw, "corr": corr}


def section_scores2(secs):
    B = tf.bars_t()
    res, i = {}, 0
    for slot, n in tf.SIZES.items():
        rows = []
        for k in range(n):
            line = secs[slot][k] if slot in secs and k < len(secs[slot]) else None
            r = fit2(line, B[i]) if line else None
            rows.append((line, r))
            i += 1
        res[slot] = rows
    return res


def calibrate(path):
    global R0, TOL, LF0
    B = tf.bars_t()
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()]
    ratios = []
    for i, l in enumerate(lines):
        b = B[i]
        if not b.get("steps"):
            continue
        st = sorted(b["steps"])
        ds = dur.syllables(l)
        if len(ds) != len(st):
            continue
        for k, d in enumerate(ds):
            gap = max((st[k + 1] - st[k]) if k + 1 < len(ds) else 4, 0.5)
            if not d[1] == "schwa":
                ratios.append(d[2] / (gap * MS_STEP))
    cs0 = []
    for i, l in enumerate(lines):
        b = B[i]
        if not b.get('steps'):
            continue
        st0 = sorted(b['steps']); ds0 = dur.syllables(l)
        if len(ds0) != len(st0) or len(ds0) < 4:
            continue
        gs = [max((st0[k + 1] - st0[k]) if k + 1 < len(ds0) else 4, 0.5) for k in range(len(ds0))]
        xs0 = [d[2] for d in ds0]
        if len(set(xs0)) > 1 and len(set(gs)) > 1:
            cs0.append(statistics.correlation(xs0, gs))
    LF0v = statistics.median(cs0)
    lr = sorted(math.log(r) for r in ratios if r > 0)
    R0 = math.exp(statistics.median(lr))
    dev = sorted(abs(x - math.log(R0)) for x in lr)
    TOL = dev[int(len(dev) * 0.90)]  # the original's own 90th percentile: 10% of its syllables flag
    json.dump({"R0": round(R0, 3), "TOL": round(TOL, 3), "LF0": round(LF0v, 3)}, open(BASE2, "w"), indent=1)
    LF0 = LF0v
    secs, i = {}, 0
    for slot, n in tf.SIZES.items():
        secs[slot] = lines[i:i + n]
        i += n
    res = section_scores2(secs)
    bc = [r[0] for rows in res.values() for _, r in rows if r]
    jl = [l.strip() for l in open(os.path.join(HERE, "tests", "joe_hook_1-4.txt"), encoding="utf8") if l.strip() and not l.startswith(("=", "#"))][:4]
    jc = [fit2(l, B[i])[0] for i, l in enumerate(jl)]
    m = {s: statistics.mean([r[0] for _, r in rows if r]) for s, rows in res.items()}
    out = json.load(open(BASE2))
    out.update({"section_mean": {k: round(v, 3) for k, v in m.items()}, "bar_costs": [round(x, 2) for x in bc],
                "joe_hook_bar_costs": [round(x, 2) for x in jc], "joe_hook_mean": round(statistics.mean(jc), 2), "joe_bar_max": round(max(jc), 2)})
    json.dump(out, open(BASE2, "w"), indent=1)
    bs = sorted(bc)
    print("R0 %.2f TOL %.2f | original: %d bars, mean %.2f, p50 %.2f p90 %.2f p95 %.2f max %.2f | section means %s | Joe's bars %s" % (
        R0, TOL, len(bc), statistics.mean(bc), bs[len(bs) // 2], bs[int(len(bs) * .9)], bs[int(len(bs) * .95)], bs[-1], {k: round(v, 2) for k, v in m.items()}, [round(x, 2) for x in jc]))


def verdict(path, show=True):
    load_params()
    secs = tf.parse(path)
    res = section_scores2(secs)
    bj = json.load(open(BASE2))
    sm = bj["section_mean"]
    hi, lo = max(sm.values()), min(sm.values())
    thr = max(hi + 0.5 * (hi - lo), bj["joe_hook_mean"] + 0.1)
    bs = sorted(bj["bar_costs"])
    bar_lim = max(bs[int(len(bs) * 0.95)], bj["joe_bar_max"])
    bad, over, scored, nostep, missing, n_all = 0, [], 0, [], [], 0
    for slot, rows in res.items():
        cs = [r[0] for _, r in rows if r]
        mean = statistics.mean(cs) if cs else None
        if show:
            print("== %s  mean %.2f (limit %.2f) %s" % (slot, mean if mean is not None else -1, thr, "FAIL" if mean is not None and mean > thr else "ok"))
        for k, (line, r) in enumerate(rows):
            n_all += 1
            if line is None:
                missing.append((slot, k + 1))
            elif r is None:
                nostep.append((slot, k + 1))
            else:
                scored += 1
                if r[0] > bar_lim:
                    over.append((slot, k + 1, r[0]))
                if show and r[1]:
                    print("   %2d %.1f | %s\n        %s" % (k + 1, r[0], line, "; ".join(r[1][:6])))
        if mean is not None and mean > thr:
            bad += 1
    print("ACCOUNTED: %d expected, %d scored, %d no-steps (by ear: %s), %d missing %s" % (n_all, scored, len(nostep), ", ".join("%s #%d" % x for x in nostep) or "-", len(missing), missing or ""))
    print("BARS OVER %.2f: %d %s" % (bar_lim, len(over), ["%s #%d %.1f" % x for x in over]))
    fail = bad or over or missing
    print("TIMEFIT2 VERDICT: %s (%d of %d sections over %.2f; %d bars over %.2f)" % ("FAIL" if fail else "PASS", bad, len(res), thr, len(over), bar_lim))
    return 1 if fail else 0


def selftest():
    load_params()
    B = tf.bars_t()
    p = []
    a = fit2("Cold beer on the house in Porto", B[4])
    b = fit2("Cold beer on the house in Porto Oslo Bilbao Madrid Rome Berlin", B[4])
    if not a or not b or not b[0] > a[0]:
        p.append("overlong bar not costlier")
    return (not p, "; ".join(p) if p else "aligned stress + length + mouth fit runs; overlong bar costs more")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok, m = selftest(); print(("PASSED: " if ok else "FAILED: ") + m); sys.exit(0 if ok else 1)
    if "--calibrate" in sys.argv:
        calibrate(sys.argv[sys.argv.index("--calibrate") + 1])
    else:
        sys.exit(1 if verdict(sys.argv[-1]) else 0)
