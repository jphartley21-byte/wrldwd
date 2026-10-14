"""Flow audit: per-bar violation flags and song-level rhythm structure, from the research synthesis (eval/_flow_research.json, 14 Oct 2026).

Design rules taken from the repo's own history and from the research (benchmark/flow_research.md):
  * The syllable -> 16th-note SLOT map is INHERITED from benchmark/flow_template.json (audio-measured). A bar with the wrong syllable count has no valid
    grid, so every slot feature is only meaningful once the count is right.
  * Per-bar FLAGS with names (never a block total, never an aggregate percentage as a target). A flag is allowed to BLOCK only if the original itself
    fires it at a very low rate (`baseline()` measures that; 'a gate the benchmark fails is a wrong gate').
  * Song-level structure (run lengths of a shared cadence, density curve, drops, monotony) is where a 76-bar song most differs from nine well-fitted
    isolated blocks, and it needs only counts and end shapes.

  python -m ww.cli flow writing/ww_full_draft_v3.md          per-bar flags and song structure, original baseline beside it
"""
from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter

from .. import bridge, config

FUNC = set("a an the of to and in on at for with as is it its it's was were be been am are i me my we our us you your he she him her they them their his this that these those from by or but so if then than up out off do did does not no can will would just he's she's that's there's what's i'm i've i'd i'll you're we're they're isn't wasn't don't didn't can't won't let's who's where's here's how's".split())
BASELINE_PATH = config.BENCHMARK / "flow_baseline.json"


def _rt():
    bridge._pron_ready()
    bridge._toolkit_on_path()
    import rhyme_tools
    return rhyme_tools


def _ff():
    bridge._pron_ready()
    bridge._toolkit_on_path()
    import flow_fit
    return flow_fit


def strength(step: int) -> int:
    return 3 if step % 4 == 0 else (2 if step % 2 == 0 else 1)


def syll_table(bar: str) -> list[dict]:
    """one row per syllable: word, position in word, stress digit (0/1/2), content (not a function word), reduced (AH0/IH0 or unstressed function word)."""
    rt = _rt()
    rows = []
    for w in re.findall(r"[A-Za-z'å]+", bridge.norm(bar)):
        lw = w.lower().replace("å", "a")
        ph = rt.pron(lw)
        func = lw in FUNC
        if not ph:
            n = max(1, len(re.findall(r"[aeiouy]+", lw.rstrip("e"))))
            digs = [1] + [0] * (n - 1)
            vowels = ["?"] * n
        else:
            vs = [p for p in ph if p[-1].isdigit()]
            digs = [int(p[-1]) for p in vs]
            vowels = [p[:-1] for p in vs]
            if len(vs) == 1:
                digs = [0 if func else 1]
        for k, (d, v) in enumerate(zip(digs, vowels)):
            rows.append({"word": lw, "k": k, "n_in_word": len(digs), "stress": d, "content": not func, "v": v, "reduced": (d == 0 and (v in ("AH", "IH", "?") or func))})
    return rows


def laid(slot: str, i: int, bar: str):
    from .slotcheck import SECS
    ff = _ff()
    start = next(s for n, s, e in SECS if n == slot)
    t = ff.T[start + i]
    tab = syll_table(bar)
    n = len(tab)
    if t.get("missing") or not t.get("steps"):
        return tab, None, t
    o = t["steps"]
    steps = [s % 16 for s in (list(o[:n]) + [o[-1] + 1] * max(0, n - len(o)))]
    return tab, steps, t


def bar_flags(slot: str, i: int, bar: str) -> dict:
    tab, steps, t = laid(slot, i, bar)
    n = len(tab)
    f: dict = {"n": n, "flags": [], "gaps": [], "acc_int": []}
    if steps is None:
        return f
    tn = len(t["steps"])
    f["count_err"] = abs(n - tn)
    if f["count_err"] >= 2:
        f["flags"].append(f"count {n} vs template {tn}")
    # stress positions: primary stress of content syllables
    prim = [k for k, r in enumerate(tab) if r["stress"] == 1 and r["content"]]
    # word-stress inversion
    inv = []
    k = 0
    while k < n:
        w = tab[k]["word"]; j = k
        while j < n and tab[j]["word"] == w and tab[j]["k"] == j - k:
            j += 1
        if j - k >= 2:
            ps = [x for x in range(k, j) if tab[x]["stress"] == 1]
            if ps:
                p = ps[0]
                others = [strength(steps[x]) for x in range(k, j) if x != p and x < len(steps)]
                if p < len(steps) and others and max(others) > strength(steps[p]):
                    inv.append(w)
        k = max(j, k + 1)
    f["inversions"] = inv
    if inv:
        f["flags"].append("stress inverted in " + ", ".join(inv))
    # weak on strong
    wos = [tab[x]["word"] for x in range(n) if x < len(steps) and strength(steps[x]) == 3 and tab[x]["reduced"]]
    f["weak_on_strong"] = wos
    if wos:
        f["flags"].append("reduced syllable on a downbeat: " + ", ".join(wos))
    # clash and gaps
    clashes = []
    for a, b in zip(prim, prim[1:]):
        if b < len(steps) and a < len(steps) and (steps[b] - steps[a]) % 16 <= 1:
            clashes.append((tab[a]["word"], tab[b]["word"]))
        f["gaps"].append(b - a - 1)
    f["clashes"] = clashes
    if clashes:
        f["flags"].append("stress clash: " + ", ".join(f"{a}/{b}" for a, b in clashes))
    if f["gaps"] and max(f["gaps"]) >= 4:
        f["flags"].append(f"{max(f['gaps'])} unstressed syllables in a row between stresses")
    # accent intervals (16th steps)
    acc = [steps[x] for x in range(n) if x < len(steps) and ((tab[x]["stress"] == 1 and tab[x]["content"]) or (strength(steps[x]) == 3 and tab[x]["stress"] > 0))]
    f["acc_int"] = [(b - a) % 16 or 16 for a, b in zip(acc, acc[1:])]
    # end slot
    last = prim[-1] if prim else n - 1
    ri = t.get("rhyme_idx")
    f["end_trailing_weak"] = n - 1 - last
    f["end_slot_dev"] = abs(last - ri) if ri is not None else 0
    shape = bridge.end_shape(bar)
    f["end_shape"] = shape
    if t.get("end_shape") and shape != t["end_shape"] and not (shape in ("|Sw", "~Sw") and t["end_shape"] in ("|Sw", "~Sw")):
        f["flags"].append(f"ends {shape}, template {t['end_shape']}")
    # displaced stress share
    f["displaced"] = sum(1 for x in prim if x < len(steps) and strength(steps[x]) == 1) / max(1, len(prim))
    # phrase split
    parts = [p for p in re.split(r"[,;:.!?]|\s-\s", bridge.norm(bar)) if p.strip()]
    f["phrases"] = [len(syll_table(p)) for p in parts]
    f["comma"] = "," in bar
    f["ends_on_function"] = tab[-1]["word"] in FUNC if tab else False
    # mouth-shape transitions: where the mouth must reorganise across a word boundary. The original carries 0
    # of the rare kinds in 78% of its bars, so 2 or more in one bar is out of distribution (measured 14 Oct 2026).
    rj = bridge.rare_joins(bar)
    f["rare_joins"] = rj
    if len(rj) >= 2:
        f["flags"].append("mouth-shape transitions: " + "; ".join(f"{a} {b} ({r})" for a, b, r in rj))
    return f


VOW_CLASS = {"AA": "a", "AO": "o", "AH": "u", "AE": "ae", "EH": "e", "IH": "i", "IY": "ee", "UW": "oo", "UH": "oo", "OW": "oh", "EY": "ay", "AY": "eye", "AW": "ow", "OY": "oy", "ER": "er"}


def parallelism(slot: str, bars: list[str]) -> dict:
    """POSITIONAL PARALLELISM across consecutive bars: when two neighbouring bars both put a stressed content syllable on the same 16th-note step, how often is
    it the SAME vowel (assonance on the same beat), and what share of stressed steps do neighbouring bars share? Measured on the original: vowel match 27%
    (chance, from shuffling bar order, 15%); downbeats only 29% (chance 14%); shared stressed steps 28% (chance ~22%). Ours v3 sat at chance."""
    items = []
    for i, b in enumerate(bars):
        tab, steps, t = laid(slot, i, b)
        if steps is None:
            items.append(None); continue
        d = {}
        for k, r in enumerate(tab):
            if k < len(steps) and r["stress"] > 0 and r["content"]:
                d.setdefault(steps[k], r.get("v"))
        items.append(d)
    m = n = md = nd = shared = union = 0
    for A, B in zip(items, items[1:]):
        if not A or not B:
            continue
        for st in set(A) & set(B):
            same = VOW_CLASS.get(A[st]) is not None and VOW_CLASS.get(A[st]) == VOW_CLASS.get(B[st])
            n += 1; m += same
            if st % 4 == 0:
                nd += 1; md += same
        shared += len(set(A) & set(B)); union += len(set(A) | set(B))
    return {"match": m, "n": n, "match_down": md, "n_down": nd, "shared": shared, "union": union}


def beat_items(slot: str, bars: list[str], drop_last: bool = True):
    """per bar: {step: vowel class} for stressed content syllables on the inherited grid (None if the bar has no template).
    drop_last=True leaves out each bar's final stressed syllable (the rhyme syllable): end-rhyme alignment is already enforced by the carpet and end-shape
    gates, so the REWARD is for the mid-bar parallelism that nothing else asks for."""
    out = []
    for i, b in enumerate(bars):
        tab, steps, t = laid(slot, i, b)
        if steps is None:
            out.append(None); continue
        d = {}
        for k, r in enumerate(tab):
            if k < len(steps) and r["stress"] > 0 and r["content"]:
                d.setdefault(steps[k], VOW_CLASS.get(r.get("v")))
        if drop_last and d:
            d.pop(max(d, key=lambda st: [k for k in range(len(tab)) if k < len(steps) and steps[k] == st and tab[k]["stress"] > 0 and tab[k]["content"]][-1]), None)
        out.append(d)
    return out


def parallel_raw(items) -> dict:
    """counts for the BEAT-PARALLELISM REWARD over consecutive bars: same vowel on a shared DOWNBEAT (weight 2), same vowel on another shared step (1),
    shared stressed step with a different vowel (0.25)."""
    pairs = md = mo = so = 0
    for A, B in zip(items, items[1:]):
        if not A or not B:
            continue
        pairs += 1
        for st in set(A) & set(B):
            if A[st] is not None and A[st] == B[st]:
                if st % 4 == 0:
                    md += 1
                else:
                    mo += 1
            else:
                so += 1
    return {"pairs": pairs, "m_down": md, "m_other": mo, "s_only": so}


def parallel_points(raw: dict) -> float:
    return (2 * raw["m_down"] + raw["m_other"] + 0.25 * raw["s_only"]) / max(1, raw["pairs"])


def parallel_index(slot: str, bars: list[str], base: dict | None = None) -> dict:
    """the reward: points per bar pair, and an INDEX where 0 = chance (bar order shuffled) and 1 = the original's own level for this kind of section.
    Capped at 1.5 so the reward cannot push the writer into sing-song."""
    import random
    base = base or load_baseline()
    items = beat_items(slot, bars)
    raw = parallel_raw(items)
    pts = parallel_points(raw)
    chance = base.get("pp_chance", 0.9)
    orig = base.get("pp_original", 1.5)
    idx = (pts - chance) / max(0.05, orig - chance)
    return {"points": round(pts, 3), "index": round(max(-1.0, min(1.5, idx)), 2), "raw": raw}


def section_audit(slot: str, bars: list[str]) -> dict:
    fl = [bar_flags(slot, i, b) for i, b in enumerate(bars)]
    ns = [x["n"] for x in fl]
    shapes = [bridge.end_shape(b) for b in bars]
    drops = sum(1 for a, b in zip(ns, ns[1:]) if a >= 11 and b <= 0.6 * a)
    runs, cur = [], 1
    for (a, sa), (b, sb) in zip(zip(ns, shapes), list(zip(ns, shapes))[1:]):
        if abs(a - b) <= 1 and sa == sb:
            cur += 1
        else:
            runs.append(cur); cur = 1
    runs.append(cur)
    ident = 1; best = 1
    for (a, sa), (b, sb) in zip(zip(ns, shapes), list(zip(ns, shapes))[1:]):
        ident = ident + 1 if (a == b and sa == sb) else 1
        best = max(best, ident)
    par = parallelism(slot, bars)
    return {"slot": slot, "parallel": par, "bars": fl, "n": ns, "mean_n": statistics.mean(ns), "sd_n": statistics.pstdev(ns) if len(ns) > 1 else 0.0,
            "mean_abs_step": statistics.mean(abs(a - b) for a, b in zip(ns, ns[1:])) if len(ns) > 1 else 0.0, "drops": drops,
            "shortest_at": ns.index(min(ns)) + 1, "longest_at": ns.index(max(ns)) + 1, "last_vs_mean": ns[-1] - statistics.mean(ns),
            "template_runs": runs, "longest_run": max(runs), "max_identical": best,
            "enjambed": sum(1 for x in fl if x.get("ends_on_function")) / len(fl)}


def audit_song(sections: dict[str, list[str]]) -> dict:
    return {s: section_audit(s, b) for s, b in sections.items()}


# ---------------------------------------------------------------- baseline from the original (counts only)

def rates(aud: dict) -> dict:
    bars = [b for s in aud.values() for b in s["bars"] if "count_err" in b]
    n = len(bars)
    gaps = [g for b in bars for g in b["gaps"]]
    acc = [x for b in bars for x in b["acc_int"]]
    hist = Counter(min(x, 5) for x in acc)
    tot = max(1, sum(hist.values()))
    secs = list(aud.values())
    return {
        "bars": n,
        "count_err_ge2": sum(1 for b in bars if b["count_err"] >= 2) / n,
        "inversion": sum(1 for b in bars if b["inversions"]) / n,
        "weak_on_strong": sum(1 for b in bars if b["weak_on_strong"]) / n,
        "clash": sum(1 for b in bars if b["clashes"]) / n,
        "gap_ge4": sum(1 for b in bars if b["gaps"] and max(b["gaps"]) >= 4) / n,
        "gap_hist": {k: round(sum(1 for g in gaps if min(g, 4) == k) / max(1, len(gaps)), 3) for k in range(5)},
        "acc_int_hist": {k: round(hist.get(k, 0) / tot, 3) for k in range(1, 6)},
        "end_shape_mismatch": sum(1 for b in bars if any(f.startswith("ends ") for f in b["flags"])) / n,
        "end_trailing_weak_gt1": sum(1 for b in bars if b["end_trailing_weak"] > 1) / n,
        "rare_joins": sum(1 for b in bars if b["rare_joins"]) / n,
        "rare_joins_ge2": sum(1 for b in bars if len(b["rare_joins"]) >= 2) / n,
        "displaced": statistics.mean(b["displaced"] for b in bars),
        "comma_bars": sum(1 for b in bars if b["comma"]) / n,
        "ends_on_function": sum(1 for b in bars if b["ends_on_function"]) / n,
        "flags_per_bar": statistics.mean(len(b["flags"]) for b in bars),
        "mean_abs_step": statistics.mean(s["mean_abs_step"] for s in secs),
        "drops_per_section": statistics.mean(s["drops"] for s in secs),
        "longest_run": statistics.mean(s["longest_run"] for s in secs),
        "max_identical": max(s["max_identical"] for s in secs),
        "sd_n": statistics.mean(s["sd_n"] for s in secs),
        "shortest_late": sum(1 for s in secs if s["shortest_at"] > len(s["n"]) / 2) / len(secs),
        "pos_assonance": sum(s["parallel"]["match"] for s in secs) / max(1, sum(s["parallel"]["n"] for s in secs)),
        "pos_assonance_down": sum(s["parallel"]["match_down"] for s in secs) / max(1, sum(s["parallel"]["n_down"] for s in secs)),
        "shared_stress_steps": sum(s["parallel"]["shared"] for s in secs) / max(1, sum(s["parallel"]["union"] for s in secs)),
    }


def _pp_chance(sections: dict[str, list[str]], reps: int = 30) -> float:
    import random
    r = random.Random(7)
    vals = []
    for _ in range(reps):
        raw = {"pairs": 0, "m_down": 0, "m_other": 0, "s_only": 0}
        for slot, bars in sections.items():
            items = beat_items(slot, bars)
            idx = list(range(len(items)))
            r.shuffle(idx)
            c = parallel_raw([items[i] for i in idx])
            for k in raw:
                raw[k] += c[k]
        vals.append(parallel_points(raw))
    return statistics.mean(vals)


def baseline(save: bool = True) -> dict:
    """measure the ORIGINAL (laid on its own template; numbers only, never its words) and store to benchmark/flow_baseline.json"""
    from ..calib import original as o
    from .slotcheck import SECS
    lines = o._lines()
    aud = audit_song({n: lines[a:b] for n, a, b in SECS})
    r = rates(aud)
    secs_o = {n: lines[a:b] for n, a, b in SECS}
    raw = {"pairs": 0, "m_down": 0, "m_other": 0, "s_only": 0}
    for slot, bars in secs_o.items():
        c = parallel_raw(beat_items(slot, bars))
        for k in raw:
            raw[k] += c[k]
    r["pp_original"] = parallel_points(raw)
    r["pp_chance"] = _pp_chance(secs_o)
    if save:
        BASELINE_PATH.write_text(json.dumps(r, indent=1), encoding="utf-8")
    return r


def load_baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8")) if BASELINE_PATH.exists() else {}


def report(sections: dict[str, list[str]], show_bars: bool = True) -> str:
    aud = audit_song(sections)
    r = rates(aud)
    base = load_baseline()
    L = []
    if show_bars:
        for s, a in aud.items():
            for i, b in enumerate(a["bars"]):
                if b.get("flags"):
                    L.append(f"{s} bar {i + 1}: " + sections[s][i][:60] + "  <-  " + "; ".join(b["flags"]))
    L.append("")
    L.append(f"{'rate (per bar unless noted)':34s} {'this':>8s} {'original':>9s}")
    for k in ("count_err_ge2", "inversion", "weak_on_strong", "clash", "gap_ge4", "end_shape_mismatch", "end_trailing_weak_gt1", "displaced", "comma_bars", "ends_on_function", "flags_per_bar", "mean_abs_step", "drops_per_section", "longest_run", "max_identical", "sd_n", "shortest_late", "pos_assonance", "pos_assonance_down", "shared_stress_steps"):
        L.append(f"{k:34s} {r[k]:8.2f} {base.get(k, float('nan')):9.2f}")
    L.append("gap histogram (unstressed syllables between stresses 0,1,2,3,4+): " + " ".join(f"{r['gap_hist'][k]:.2f}" for k in range(5)) + "   original " + " ".join(f"{base.get('gap_hist', {}).get(str(k), float('nan')):.2f}" for k in range(5)))
    L.append("accent interval histogram (16ths 1,2,3,4,5+): " + " ".join(f"{r['acc_int_hist'][k]:.2f}" for k in range(1, 6)) + "   original " + " ".join(f"{base.get('acc_int_hist', {}).get(str(k), float('nan')):.2f}" for k in range(1, 6)))
    return "\n".join(L)


def parse_draft(path: str) -> dict[str, list[str]]:
    sec, cur = {}, None
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("== "):
            cur = l[3:].strip(); sec[cur] = []
        elif cur and l.strip() and not l.startswith("#"):
            sec[cur].append(l.strip())
    return sec


def scan(line: str, slot: str | None = None, bar: int | None = None) -> str:
    """scansion of one line: syllables, stress string (S = stressed content syllable, s = secondary, . = unstressed or reduced), end shape, and with a slot/bar
    the original's downbeat syllable positions for that bar. Use it on ANY line (ours or the reference's) so flow is judged from the same numbers."""
    tab = syll_table(line)
    st = "".join("S" if (r["stress"] == 1 and r["content"]) else ("s" if r["stress"] in (1, 2) else ".") for r in tab)
    words = []
    for r in tab:
        if r["k"] == 0:
            words.append(r["word"])
        else:
            words[-1] += "-"
    out = f"{len(tab)} syllables | stress {st} | ends {bridge.end_shape(line)}"
    rj = bridge.rare_joins(line)
    if rj:
        out += " | mouth-shape: " + "; ".join(f"{a} {b} ({r})" for a, b, r in rj)
    if slot and bar:
        tab2, steps, t = laid(slot, bar - 1, line)
        if steps is not None:
            dn = [k + 1 for k, x in enumerate(steps) if x % 4 == 0]
            bad = [k + 1 for k in range(len(tab2)) if k < len(steps) and steps[k] % 4 == 0 and tab2[k]["reduced"]]
            out += f" | template {len(t['steps'])} syllables, downbeats at syllables {dn}, reduced syllables on them: {bad or 'none'}"
    return out


def beats_grid(slot: str, bars: list[str]) -> str:
    """for each bar: the stressed vowel (class) on each 16th-note step the bar uses, and where it matches the previous bar on the SAME step (marked =)."""
    items = beat_items(slot, bars)
    L = []
    prev = None
    for i, (b, it) in enumerate(zip(bars, items)):
        if it is None:
            L.append(f"{i + 1}: (no template)  {b}"); prev = None; continue
        cells = []
        for st in sorted(it):
            mark = "="  if (prev and st in prev and prev[st] is not None and prev[st] == it[st]) else (":" if (prev and st in prev) else " ")
            cells.append(f"{st}{'D' if st % 4 == 0 else ''}{mark}{it[st]}")
        L.append(f"{i + 1}: {' '.join(cells)}   <- {b}")
        prev = it
    L.append("legend: step number, D = downbeat; '=' same vowel as the previous bar on that step (rewarded), ':' stressed on the same step with a different vowel, blank = no stress there in the previous bar")
    return "\n".join(L)


def selftest() -> tuple[bool, str]:
    problems = []
    f = bar_flags("V1 1-8", 0, "Turned up late and the crew held my ferry")
    if "count_err" not in f or f["n"] != 10:
        problems.append(f"bar_flags should lay a 10-syllable bar on the template: {f}")
    f2 = bar_flags("V1 1-8", 0, "The a of to and in on at for with as is it its")   # nonsense weak string must fire
    if not f2["flags"]:
        problems.append("a string of function words should fire at least one flag")
    return (not problems, "; ".join(problems) if problems else "bar flags computed on the template grid")
