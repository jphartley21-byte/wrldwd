"""flowshape: how bars RELATE to each other, not how each bar scans (15 Oct 2026, Joe: "what's actually important is if the
rhyming syllables land on the same part of the beat across bars, how stress patterns match across bars, and how tension is
built and released using all of these flow elements").

  python toolkit/flowshape.py FILE                  text profile of a draft vs the original's (FILE: "== Slot" sections or 76 plain lines)
  python toolkit/flowshape.py --audio TEMPLATE FILE audio-timed profile: TEMPLATE = a flow_map.py template of FILE's audio (default: the
                                                    original's benchmark/flow_template.json). Needs audio, so only the original has it today.
  python toolkit/flowshape.py --build FILE          write benchmark/flow_shape_baseline.json from the original (numbers only)
  python toolkit/flowshape.py --selftest

Three families, each measured two ways:
 1 RHYME LANDING   text: for rhyme partners (best_end >= 0.78 within 4 bars) how often the rhyme sits the same number of syllables
                   from the bar line (same "tail"); validated on the original: equal tails land within 1 step 62% of the time,
                   unequal tails 19%.  audio: the beat of the bar the rhyme anchor lands on, and how often rhyme partners land
                   on the same beat / the same step.
 2 STRESS ACROSS BARS  text: agreement of the stress pattern, aligned from the END of the bar (where the rhyme is) and from the start,
                   between rhyme partners and between adjacent bars.  audio: shared stressed steps (Jaccard) between adjacent bars.
 3 TENSION         per-bar score from: syllable density, stress clashes (friction), long unstressed runs (slack, weighs negative),
                   an unresolved end rhyme (no partner in the previous 3 bars), a run-on bar (ends on a function word). Components are
                   z-scored on the ORIGINAL, so the scale is the original's. Reported: spread, bar-to-bar change, the range inside
                   each 4-bar group, and how often a group builds then releases. These weights are a priori, not fitted to the original.
FINDING (15 Oct 2026, original vs an AI-written song): the TEXT proxies do NOT show the AI song worse on landing or stress
alignment (it is MORE regular: 89% equal tails vs 71%); the differences are smaller tension swings and fewer clashes and
run-ons. At section level none of these separates the texts under a leave-one-out rule, so they are PROFILE ROWS, never gates.
Whether the AI rhymes land on the same part of the BEAT can only be answered on audio (render, then flow_map.py, then --audio).
"""
import json, os, re, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
BASE = os.path.join(ROOT, "benchmark", "flow_shape_baseline.json")
W = {"n": 1.0, "clash": 1.0, "lapse": -0.5, "open": 1.0, "enj": 1.0}   # a priori tension weights


def _bar(l):
    import flow_check as fc, flow_fit as ff
    p = fc.bar_profile(l); n = p["syl"]; g = set(p["grid"])
    ws = re.findall(r"[A-Za-z']+", l)
    return {"n": n, "vec": [1 if i + 1 in g else 0 for i in range(n)], "clash": p["clash"], "lapse": p["lapse"],
            "tail": ff.tail_len(l), "enj": int(bool(ws) and ws[-1].lower() in fc.FUNC)}


def partners(bars, floor=0.78, win=4):
    import match as m
    P = {i: [] for i in range(len(bars))}
    for i in range(len(bars)):
        for j in range(max(0, i - win), min(len(bars), i + win + 1)):
            if j != i and m.best_end(bars[i], bars[j]) >= floor:
                P[i].append(j)
    return P


def _al(a, b, end=True, k=6):
    k = min(len(a), len(b), k)
    if not k:
        return 0.0
    x, y = (a[-k:], b[-k:]) if end else (a[:k], b[:k])
    return sum(p == q for p, q in zip(x, y)) / k


def comps(bars):
    F = [_bar(b) for b in bars]; P = partners(bars, win=3)
    return F, P, [{"n": f["n"], "clash": f["clash"], "lapse": f["lapse"], "enj": f["enj"],
                   "open": 0 if any(j < i and i - j <= 3 for j in P[i]) else 1} for i, f in enumerate(F)]


def text_profile(secs, scale=None):
    """song-level text profile. scale = {'mu':..,'sd':..} for the tension z-scores (the original's); built from `secs` if None"""
    per = {s: comps(b) for s, b in secs.items()}
    allc = [c for _, _, cs in per.values() for c in cs]
    if scale is None:
        mu = {k: st.mean(c[k] for c in allc) for k in W}
        sd = {k: (st.pstdev([c[k] for c in allc]) or 1.0) for k in W}
        scale = {"mu": mu, "sd": sd}
    T = lambda c: sum(w * (c[k] - scale["mu"][k]) / scale["sd"][k] for k, w in W.items())
    pair_eq, len_eq, e_pair, e_adj, s_adj, cover, curve, qs = [], [], [], [], [], [], [], []
    for s, (F, P, cs) in per.items():
        bars_n = len(F)
        pairs = sorted({(min(i, j), max(i, j)) for i in P for j in P[i]})
        cover += [bool(P[i]) for i in P]
        pair_eq += [F[i]["tail"] == F[j]["tail"] for i, j in pairs]
        len_eq += [abs(F[i]["n"] - F[j]["n"]) <= 1 for i, j in pairs]
        e_pair += [_al(F[i]["vec"], F[j]["vec"]) for i, j in pairs]
        e_adj += [_al(F[i]["vec"], F[i + 1]["vec"]) for i in range(bars_n - 1)]
        s_adj += [_al(F[i]["vec"], F[i + 1]["vec"], end=False) for i in range(bars_n - 1)]
        t = [T(c) for c in cs]; curve += t
        for a in range(0, bars_n - 3, 4):
            q = t[a:a + 4]
            qs.append({"rng": max(q) - min(q), "peak": q.index(max(q)) + 1, "rise_fall": q.index(max(q)) in (1, 2) and q[3] < max(q[:3]) - 0.5})
    adj = [abs(a - b) for a, b in zip(curve, curve[1:])]
    prof = {"bars": len(curve), "rhyme_cover": st.mean(cover), "tail_eq": st.mean(pair_eq) if pair_eq else None,
            "len_eq": st.mean(len_eq) if len_eq else None, "stress_end_pair": st.mean(e_pair) if e_pair else None,
            "stress_end_adj": st.mean(e_adj), "stress_start_adj": st.mean(s_adj),
            "clash_per_bar": st.mean(c["clash"] for c in allc), "run_on_share": st.mean(c["enj"] for c in allc),
            "tension_sd": st.pstdev(curve), "tension_step": st.mean(adj), "group_range": st.mean(q["rng"] for q in qs),
            "build_release": st.mean(q["rise_fall"] for q in qs),
            "peak_at_bar3": st.mean(q["peak"] == 3 for q in qs), "peak_at_bar1": st.mean(q["peak"] == 1 for q in qs)}
    return prof, scale, curve


def audio_profile(tpl_bars, secs):
    """audio-timed: where rhyme anchors land in the bar and how bar-to-bar stress steps agree. tpl_bars is a template list
    (flow_template.json 'bars') aligned with the draft's bars in order."""
    bars = [b for s in secs.values() for b in s]
    P = partners(bars)
    pairs = sorted({(min(i, j), max(i, j)) for i in P for j in P[i]})

    def land(i):
        if i >= len(tpl_bars):
            return None
        b = tpl_bars[i]; s = b.get("steps"); ri = b.get("rhyme_idx")
        return s[ri] if s and ri is not None and ri < len(s) and 1 <= s[ri] <= 32 else None

    beat = {}
    for i in range(len(bars)):
        s = land(i)
        if s:
            k = ((s - 1) % 16) // 4 + 1; beat[k] = beat.get(k, 0) + 1
    same_b, same_s = [], []
    for i, j in pairs:
        a, b = land(i), land(j)
        if a and b:
            same_b.append(((a - 1) % 16) // 4 == ((b - 1) % 16) // 4)
            same_s.append(abs((a - 1) % 16 - (b - 1) % 16) <= 1)

    def stressed(i):
        b = tpl_bars[i] if i < len(tpl_bars) else {}
        s, w = b.get("steps"), b.get("weak")
        return {(x - 1) % 16 for x, wk in zip(s, w) if not wk} if s and w and len(s) == len(w) else None
    js = [len(a & b) / len(a | b) for a, b in ((stressed(i), stressed(i + 1)) for i in range(len(bars) - 1)) if a and b]
    tot = sum(beat.values()) or 1
    return {"bars_timed": sum(beat.values()), "rhyme_on_beat4": beat.get(4, 0) / tot, "rhyme_beat_hist": dict(sorted(beat.items())),
            "pairs_timed": len(same_b), "pairs_same_beat": st.mean(same_b) if same_b else None,
            "pairs_same_step": st.mean(same_s) if same_s else None, "adjacent_shared_stress": st.mean(js) if js else None}


def _fmt(v):
    return "  n/a" if v is None else (f"{v:5.2f}" if isinstance(v, float) else f"{v}")


def selftest():
    secs = {"t": ["I went to the shop for a loaf of bread", "And got a bit lost on the way instead", "Then bought a big pie from a man named Fred", "Now I am home and I'm in my bed"]}
    prof, scale, curve = text_profile(secs)
    p = []
    if len(curve) != 4 or abs(st.mean(curve)) > 1e-6:
        p.append("tension curve is not centred on its own scale")
    if prof["rhyme_cover"] < 0.99 or prof["tail_eq"] is None or prof["tail_eq"] < 0.99:
        p.append(f"a four-line -ed rhyme should cover every bar with equal tails: {prof['rhyme_cover']}, {prof['tail_eq']}")
    a = audio_profile([{"steps": [1, 5, 9, 13], "weak": [False, True, False, True], "rhyme_idx": 3}] * 4, secs)
    if a["rhyme_on_beat4"] != 1.0 or a["pairs_same_beat"] != 1.0:
        p.append(f"audio profile should put identical landings on beat 4: {a}")
    return (not p, "; ".join(p) if p else "landing, stress alignment, tension curve and audio profile hold on a toy block")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return 0
    if a[0] == "--selftest":
        ok, msg = selftest(); print(("PASSED: " if ok else "FAILED: ") + msg); return 0 if ok else 1
    import flowverdict as fv, duration as d
    if a[0] == "--build":
        secs = fv.sections_of(a[1])
        prof, scale, _ = text_profile(secs)
        aud = audio_profile(d.load_bars(), secs)
        json.dump({"text": prof, "scale": scale, "audio": aud}, open(BASE, "w"), indent=1)
        print("baseline written:", BASE); return 0
    base = json.load(open(BASE))
    if a[0] == "--audio":
        tpl = json.load(open(a[1]))["bars"] if os.path.exists(a[1]) else d.load_bars()
        prof = audio_profile(tpl, fv.sections_of(a[2]))
        print(f"{'audio measure':26s}{'this':>8s}{'original':>10s}")
        for k, v in prof.items():
            if k.endswith("hist"):
                print(f"  {k:24s}{v}    original {base['audio'][k]}")
            else:
                print(f"  {k:24s}{_fmt(v):>8s}{_fmt(base['audio'].get(k)):>10s}")
        return 0
    secs = fv.sections_of(a[0])
    prof, _, _ = text_profile(secs, base["scale"])
    print(f"{'text measure':24s}{'this':>8s}{'original':>10s}   ratio")
    for k, v in prof.items():
        o = base["text"].get(k)
        r = f"{v / o:6.2f}" if isinstance(v, float) and isinstance(o, float) and o else ""
        print(f"  {k:22s}{_fmt(v):>8s}{_fmt(o):>10s}   {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
