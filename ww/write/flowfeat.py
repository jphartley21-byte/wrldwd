"""Text-side FLOW features of a block, laid on the original's audio-measured syllable grid, and their validation against judges.

Everything here is computable from the bars alone plus the slot's template (benchmark/flow_template.json: the 16th-note step of every syllable
of the reference, from audio) and the CMU stress model. Nothing reads the reference's words. The point of the module is not to add gates by
assertion: `validate()` rank-correlates every feature with the judges' 'flow' score INSIDE each judge call (so the judge's own scale and the slot
cancel out) over eval/flow_dataset.jsonl (mined from the judge transcripts), and a feature is only allowed to become a gate or a writer rule if
it survives (consistent sign, |rho| >= 0.2, sign-test across calls).
"""
from __future__ import annotations

import json
import math
import os
import re
import statistics
from collections import defaultdict

from .. import bridge, config

_FF = None


def _ff():
    global _FF
    if _FF is None:
        bridge._pron_ready()
        bridge._toolkit_on_path()
        import flow_fit
        _FF = flow_fit
    return _FF


def _slot_start(slot: str) -> int:
    from .slotcheck import SECS
    return next(s for n, s, e in SECS if n == slot)


def _syll_words(bar: str) -> list[tuple[str, bool]]:
    """per syllable: (word, weak)"""
    ff = _ff()
    out = []
    for w in re.findall(r"[A-Za-z'å]+", bridge.norm(bar)):
        sy = ff.sylls(w)
        out += [(w.lower(), bool(x)) for x in sy]
    return out


def bar_features(slot: str, i: int, bar: str) -> dict:
    ff = _ff()
    t = ff.T[_slot_start(slot) + i]
    sw = _syll_words(bar)
    weak = [w for _, w in sw]
    n = len(weak)
    f: dict = {"n": n}
    if t.get("missing") or not t.get("steps"):
        return f
    o = t["steps"]
    steps = list(o[:n]) + [o[-1] + 1] * max(0, n - len(o))
    on = [k for k, st in enumerate(steps) if st % 4 == 0 and k < n]
    off = [k for k, st in enumerate(steps) if st % 4 != 0 and k < n]
    f["len_dev"] = abs(n - len(o))
    f["stress_on_beat"] = (sum(1 for k in on if not weak[k]) / len(on)) if on else 1.0
    f["weak_on_beat"] = sum(1 for k in on if weak[k])
    f["strong_off_beat"] = sum(1 for k in off if not weak[k]) / max(1, len(off))
    strong_idx = [k for k in range(n) if not weak[k]]
    gaps = [b - a for a, b in zip(strong_idx, strong_idx[1:])]
    f["stress_gap_sd"] = statistics.pstdev(gaps) if len(gaps) > 1 else 0.0           # regularity of the stress pattern (low = sing-song)
    f["stress_gap_mean"] = statistics.mean(gaps) if gaps else float(n)
    run = best = 0
    for w in weak:
        run = run + 1 if w else 0
        best = max(best, run)
    f["max_weak_run"] = best
    # accent mass: stresses per bar
    f["stresses"] = len(strong_idx)
    # syncopation: strong syllables on the weakest grid positions (16th offbeats = step % 2 == 1)
    f["strong_on_e_and_a"] = sum(1 for k in strong_idx if k < len(steps) and steps[k] % 2 == 1)
    words = [w for w, _ in sw]
    toks = re.findall(r"[A-Za-z']+", bridge.norm(bar))
    f["mono_share"] = sum(1 for w in toks if len(_ff().sylls(w)) == 1) / max(1, len(toks))
    f["words"] = len(toks)
    f["commas"] = bar.count(",")
    f["stops"] = len(re.findall(r"[.;:!?]", bar.rstrip(".!? ")))      # mid-bar resets
    f["ends_on_function"] = 1 if (toks and toks[-1].lower() in ff.WEAKFN) else 0
    # where the last stressed syllable sits relative to the bar's rhyme step
    ri = t.get("rhyme_idx")
    last_strong = max(strong_idx) if strong_idx else None
    f["rhyme_pos_dev"] = abs((last_strong if last_strong is not None else n - 1) - (ri if ri is not None else n - 1))
    return f


def block_features(slot: str, bars: list[str]) -> dict:
    per = [bar_features(slot, i, b) for i, b in enumerate(bars)]
    per = [p for p in per if "len_dev" in p]
    if not per:
        return {}
    keys = [k for k in per[0] if k != "n"]
    f = {k: statistics.mean(p[k] for p in per) for k in keys}
    ns = [p["n"] for p in per]
    f["len_sd"] = statistics.pstdev(ns) if len(ns) > 1 else 0.0
    f["len_steps"] = statistics.mean(abs(a - b) for a, b in zip(ns, ns[1:])) if len(ns) > 1 else 0.0
    f["bars"] = len(ns)
    return f


# ---------------------------------------------------------------- validation against the judges

def _spearman(x, y):
    from scipy.stats import spearmanr
    r = spearmanr(x, y)
    return r.correlation if r.correlation == r.correlation else 0.0


def validate(dataset: str | None = None, target: str = "flow", min_n: int = 3) -> list[dict]:
    path = dataset or os.path.join(os.path.dirname(__file__), "..", "..", "eval", "flow_dataset.jsonl")
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    calls = defaultdict(list)
    for r in rows:
        calls[(r["wf"], r["agent"], r["slot"])].append(r)
    feats = {}
    for r in rows:
        k = (r["slot"], tuple(r["bars"]))
        if k not in feats:
            try:
                feats[k] = block_features(r["slot"], r["bars"])
            except Exception:    # noqa: BLE001
                feats[k] = {}
    names = sorted({k for v in feats.values() for k in v if k != "bars"})
    res = []
    for nm in names:
        rhos = []
        for _, cs in calls.items():
            if len(cs) < min_n:
                continue
            xs = [feats[(c["slot"], tuple(c["bars"]))].get(nm) for c in cs]
            ys = [c["scores"].get(target) for c in cs]
            pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
            if len(pairs) < min_n or len({y for _, y in pairs}) < 2 or len({x for x, _ in pairs}) < 2:
                continue
            rhos.append(_spearman([p[0] for p in pairs], [p[1] for p in pairs]))
        if len(rhos) >= 8:
            pos = sum(1 for r in rhos if r > 0)
            neg = sum(1 for r in rhos if r < 0)
            from scipy.stats import binomtest
            p = binomtest(max(pos, neg), pos + neg, 0.5).pvalue if pos + neg else 1.0
            res.append({"feature": nm, "mean_rho": round(statistics.mean(rhos), 3), "calls": len(rhos), "pos": pos, "neg": neg, "sign_p": round(p, 4)})
    return sorted(res, key=lambda r: -abs(r["mean_rho"]))


def selftest() -> tuple[bool, str]:
    f = block_features("V1 1-8", ["Turned up late and the crew held my ferry", "I paid the deckhand in one crate of perry", "I keep my berth in Port St Mary", "Gateau's mine first bite of the cherry",
                                  "Ciao, nothing to bury", "Waved through by carabinieri", "Zell am See, never off the rails", "To Mum I'm in IT, the Bergen in-laws think sherry"])
    problems = []
    if not f or f.get("bars") != 8:
        problems.append(f"block_features should cover 8 bars: {f}")
    elif not (0.0 <= f["stress_on_beat"] <= 1.0):
        problems.append("stress_on_beat out of range")
    return (not problems, "; ".join(problems) if problems else "flow features computed on a block")
