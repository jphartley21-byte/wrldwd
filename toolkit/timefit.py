"""timefit (15 Oct 2026, report-only): a COUNT-FREE flow fit. Joe: stress, mouth transitions and vowel length matter more than syllable count.

For one bar, lay the bar's syllables on the original's 16th-note grid wherever they fit best (dynamic programming), instead of
demanding one syllable per template step. Costs, all measured on the template (benchmark/flow_template.json, audio steps) and
toolkit/duration.py (Klatt vowel/consonant time, PanPhon + connected-speech mouth joins):
  - a STRONG syllable on a step where the original has a strong one: 0; on a step where it has a weak one: +1.0; off its grid: +0.6
  - a WEAK syllable on a step where the original stresses: +1.0 (weak word on a beat)
  - an original STRONG step nobody fills: +1.0 (a missed stress); an unfilled weak step: +0.2
  - the LAST syllable not on the original's last step: +1.5 per step (the rhyme has to land where the original's lands)
  - a syllable that needs more time than its gap gives (duration.SCALE): +1.0; a hard mouth join on a gap of 1 step: +1.0
So 9 syllables against an original's 10 can score 0 if the missing one was a weak filler, and 10 syllables against 10 can score
badly if a stress lands in the wrong place. UNVALIDATED until calibrated (benchmark/timefit_baseline.json, numbers only).

  python toolkit/timefit.py --selftest
  python toolkit/timefit.py FILE                  ("== Slot" headers, one bar per line; per-bar flags + section verdict)
  python toolkit/timefit.py --calibrate PATH      (PATH = the private original, one line per bar; writes numbers only)
"""
import json, os, re, sys, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import duration as dur
import articulation as art
import flow_fit as ff

TEMPLATE = os.path.join(HERE, "..", "benchmark", "flow_template.json")
BASE = os.path.join(HERE, "..", "benchmark", "timefit_baseline.json")
STEP_MS = 60000 / 140 * 8 / 16
W_STRONG_ON_WEAK, W_STRONG_OFF, W_WEAK_ON_STRONG, W_MISSED, W_MISSED_WEAK, W_LAST, W_NEED, W_JOIN = 1.0, 0.6, 1.0, 1.0, 0.2, 1.5, 1.0, 1.0
SIZES = {"Hook 1-4": 4, "Hook 5-8": 4, "Hook 9-16": 8, "V1 1-8": 8, "V1 9-16": 8, "V1 17-24": 8, "V1 25-32": 8, "V1 33-44": 12, "V2 1-8": 8, "V2 9-16": 8}


def bars_t():
    return json.load(open(TEMPLATE, encoding="utf8"))["bars"]


def sylinfo(line):
    """per syllable: (strong, need_ms, word, first_in_word, last_in_word, onset, coda_list, is_schwa); strength from the same weak test as the template"""
    ds = dur.syllables(line)
    w = ff.sylls(line)
    weak = list(w) if len(w) == len(ds) else [d[1] == "schwa" for d in ds]
    out = []
    for d, wk in zip(ds, weak):
        out.append((not wk, d[2], d[0], d[6], d[7], d[4], d[8], d[1] == "schwa"))
    return out


def fit(line, bar):
    """-> (cost, flags, placement) for one bar; cost 0 = every stress where the original has one, nothing squeezed, rhyme lands"""
    steps = list(bar.get("steps") or [])
    weak_t = list(bar.get("weak") or [])
    if not steps:
        return None
    S = sylinfo(line)
    n = len(S)
    if n == 0:
        return None
    T = {st: (weak_t[i] if i < len(weak_t) else False) for i, st in enumerate(steps)}
    G = max(max(steps), n) + 4
    lo = min(1, min(steps) - 1)
    last_t = steps[-1]
    INF = 1e9

    def place_cost(i, p):
        strong = S[i][0]
        if p in T:
            tw = T[p]
            if strong:
                return W_STRONG_ON_WEAK if tw else 0.0
            return 0.0 if tw else W_WEAK_ON_STRONG
        return W_STRONG_OFF if strong else 0.15

    def gap_cost(i, p, q):
        """cost of syllable i at p with the next at q (q None = last syllable)"""
        g = (q - p) if q is not None else 4
        c = 0.0
        d = S[i]
        if not d[7] and d[1] * dur.SCALE > g * STEP_MS:
            c += W_NEED
        if q is not None:
            a, b = S[i], S[i + 1]
            if a[4] and b[3] and a[6] and b[5]:
                j = art.join_cost(dur.connected(a[6]), b[5])
                if j is not None and dur.connected(a[6]) == "N" and b[5] in dur.ASSIM_N:
                    j = 0.0
                if j is not None and j >= dur.JOIN_T and g <= 1:
                    c += W_JOIN
        return c

    # dp[i][p] = best cost placing syllables 0..i with syllable i at step p (gap cost of i charged when i+1 is placed)
    dp = [dict() for _ in range(n)]
    back = [dict() for _ in range(n)]
    for p in range(lo, G):
        dp[0][p] = place_cost(0, p)
    for i in range(1, n):
        for p in range(lo + i, G):
            best, bq = INF, None
            for q, c0 in dp[i - 1].items():
                if q >= p:
                    continue
                c = c0 + gap_cost(i - 1, q, p)
                if c < best:
                    best, bq = c, q
            if bq is not None:
                dp[i][p] = best + place_cost(i, p)
                back[i][p] = bq
    end, bp = INF, None
    for p, c0 in dp[n - 1].items():
        c = c0 + gap_cost(n - 1, p, None) + W_LAST * abs(p - last_t)
        if c < end:
            end, bp = c, p
    pos = [0] * n
    p = bp
    for i in range(n - 1, -1, -1):
        pos[i] = p
        p = back[i].get(p)
    used = set(pos)
    cost = end
    flags = []
    for st in steps:
        if st not in used:
            cost += W_MISSED if not T[st] else W_MISSED_WEAK
            if not T[st]:
                flags.append("stress missed at step %d" % st)
    for i, p in enumerate(pos):
        d = S[i]
        if p in T:
            if d[0] and T[p]:
                flags.append("%s: strong syllable on the original's weak step %d" % (d[2], p))
            if not d[0] and not T[p]:
                flags.append("%s: weak word on the original's stress at step %d" % (d[2], p))
        elif d[0]:
            flags.append("%s: strong syllable off the original's grid (step %d)" % (d[2], p))
    if abs(pos[-1] - last_t):
        flags.append("rhyme lands %d step(s) from the original's" % abs(pos[-1] - last_t))
    # re-list the need / join flags on the chosen placement
    for i in range(n):
        q = pos[i + 1] if i + 1 < n else None
        g = (q - pos[i]) if q is not None else 4
        if not S[i][7] and S[i][1] * dur.SCALE > g * STEP_MS:
            flags.append("%s: needs more time than %d step(s)" % (S[i][2], g))
        if q is not None:
            a, b = S[i], S[i + 1]
            if a[4] and b[3] and a[6] and b[5] and g <= 1:
                j = art.join_cost(dur.connected(a[6]), b[5])
                if j is not None and not (dur.connected(a[6]) == "N" and b[5] in dur.ASSIM_N) and j >= dur.JOIN_T:
                    flags.append("hard mouth join %s|%s on a 1-step gap" % (a[2], b[2]))
    return cost, flags, pos


def parse(path):
    secs, cur = {}, None
    for l in open(path, encoding="utf8"):
        l = l.strip()
        if l.startswith("=="):
            cur = l.strip("= ").strip()
            secs[cur] = []
        elif l and cur and not l.startswith(("[", "#")):
            secs[cur].append(l)
    return secs


def section_scores(secs):
    B = bars_t()
    res, i = {}, 0
    for slot, n in SIZES.items():
        rows = []
        for k in range(n):
            line = secs.get(slot, [None] * n)[k] if slot in secs and k < len(secs[slot]) else None
            r = fit(line, B[i]) if line else None
            rows.append((line, r))
            i += 1
        res[slot] = rows
    return res


def means(res):
    out = {}
    for slot, rows in res.items():
        cs = [r[0] for _, r in rows if r]
        out[slot] = statistics.mean(cs) if cs else None
    return out


def calibrate(path):
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()]
    secs, i = {}, 0
    for slot, n in SIZES.items():
        secs[slot] = lines[i:i + n]
        i += n
    res = section_scores(secs)
    m = means(res)
    json.dump({"section_mean_cost": m, "bar_costs": [round(r[0], 2) if r else None for rows in res.values() for _, r in rows]}, open(BASE, "w"), indent=1)
    print("original timefit section means:", {k: round(v, 2) for k, v in m.items() if v is not None})
    bc = [r[0] for rows in res.values() for _, r in rows if r]
    print("bars %d, mean %.2f, p90 %.2f, max %.2f; zero-cost bars %d" % (len(bc), statistics.mean(bc), sorted(bc)[int(.9 * len(bc))], max(bc), sum(1 for c in bc if c == 0)))


def verdict(path, show=True):
    secs = parse(path)
    res = section_scores(secs)
    m = means(res)
    base = json.load(open(BASE))["section_mean_cost"]
    vals = [v for v in base.values() if v is not None]
    hi, lo = max(vals), min(vals)
    thr = hi + 0.5 * (hi - lo)
    bad = 0
    for slot, rows in res.items():
        if show:
            print("== %s  mean cost %.2f (limit %.2f) %s" % (slot, m[slot] if m[slot] is not None else -1, thr, "FAIL" if m[slot] is not None and m[slot] > thr else "ok"))
            for k, (line, r) in enumerate(rows):
                if r and (r[1]):
                    print("   %2d %.1f | %s\n        %s" % (k + 1, r[0], line, "; ".join(r[1][:5])))
        if m[slot] is not None and m[slot] > thr:
            bad += 1
    print("TIMEFIT VERDICT: %s (%d of %d sections over the limit %.2f; original's own range %.2f-%.2f)" % ("FAIL" if bad else "PASS", bad, len(res), thr, lo, hi))
    return bad


def selftest():
    B = bars_t()
    p = []
    r = fit("Cold beer on the house in Porto", B[4])
    if not r:
        p.append("no fit")
    r2 = fit("Cold beer on the house in Porto Oslo Bilbao Madrid Rome Berlin", B[4])
    if r and r2 and not r2[0] > r[0]:
        p.append("a 14-syllable bar did not cost more than an 8-syllable bar on an 8-step frame")
    return (not p, "; ".join(p) if p else "count-free fit runs; overlong bar costs more")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok, m = selftest(); print(("PASSED: " if ok else "FAILED: ") + m); sys.exit(0 if ok else 1)
    if "--calibrate" in sys.argv:
        calibrate(sys.argv[sys.argv.index("--calibrate") + 1])
    else:
        sys.exit(1 if verdict(sys.argv[-1]) else 0)
