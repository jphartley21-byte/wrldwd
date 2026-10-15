"""Deterministic block verifier (plan 4.3): the free checks, run first. Hard failures reject a candidate; soft ones are reported.

Per bar everything is echoed back (R1): syllable count vs target, end shape, end word, grammar flags, and one line of what failed.
Syllables are a hard fact only within +-tol (default 1, the repo's own tolerance); the audio-template stress grid is NOT used (R9).
"""
from __future__ import annotations

from typing import Optional

from .. import bridge
from . import frames, grammar

HOOK_5_8 = {"sylls": [8, 10, 8, 8], "tol": 1, "shape": "|Sw", "carpet_min_pairs": 5, "carpet_floor": 0.78}
# the audio frame is a guide (R9): the first run killed 65 of 90 candidates on count alone, mostly by writing 10 where 8 was asked
HOOK_5_8_SOFT = {"sylls": [9, 10, 9, 9], "tol": 1, "shape": "|Sw", "carpet_min_pairs": 5, "carpet_floor": 0.78}


def check_block(bars: list[str], spec: dict = HOOK_5_8, context: Optional[list[str]] = None) -> dict:
    hard, soft, per = [], [], []
    n = len(bars)
    sylls = [bridge.syllable_count(b) for b in bars]
    shapes = [bridge.end_shape(b) for b in bars]
    gram = grammar.analyse_run(bars, context or [])
    mflags = {i: h for i, _, h in bridge.meaning_flags(bars)}
    for i, b in enumerate(bars):
        issues = []
        target = spec["sylls"][i] if spec.get("sylls") and i < len(spec["sylls"]) else None
        if target is not None and abs(sylls[i] - target) > spec["tol"]:
            issues.append(f"{sylls[i]} syllables (target {target}+-{spec['tol']})")
        last = (bridge.words(b) or [""])[-1]
        shape_ok = shapes[i] == spec["shape"] or (spec.get("shape") == "|Sw" and shapes[i] == "|SS" and bridge.stress_pattern(last) == "12")
        if spec.get("shape") and not shape_ok:
            issues.append(f"ends {shapes[i]} (need {spec['shape']})")
        gf = [f for f in gram[i]["flags"] if f.split(":")[0] in ("verb_string", "transitive_without_object", "unresolved_pronoun")]
        issues += [f"grammar: {f}" for f in gf]
        if (i + 1) in mflags:
            issues += [f"sense: {m[:60]}" for m in mflags[i + 1]]
        inv = bridge.invented_words(b)
        if inv:
            issues.append(f"invented word(s) {inv}")
        oov = bridge.oov_words(b)
        if oov:
            issues.append(f"cannot pronounce {oov}")
        per.append({"bar": i + 1, "text": b, "syllables": sylls[i], "shape": shapes[i], "issues": issues, "kind": gram[i]["kind"]})
        hard += [f"bar {i + 1}: {x}" for x in issues]
    carpet = bridge.carpet(bars) if n >= 2 else {"pairs": 0, "total": 0, "min": 1.0}
    if n >= 2 and carpet["pairs"] < spec.get("carpet_min_pairs", 0):
        hard.append(f"end rhymes: only {carpet['pairs']}/{carpet['total']} pairs reach {spec.get('carpet_floor', 0.78)} (min {carpet['min']})")
    sc = frames.scan({"block": bars})
    if sc["banned"] or sc["section"]:
        hard.append(f"filler frames: {[p for v in sc['banned'].values() for p, _ in v]}")
    return {"ok": not hard, "hard": hard, "soft": soft, "per_bar": per, "carpet": carpet}


def selftest() -> tuple[bool, str]:
    from .. import config  # noqa: F401
    # 15 Oct 2026: the positive block was the four Hook 1-4 bars once called "Joe's accepted hook" (Joe: never approved, never
    # a bar or a gate again). A monorhyme block from this repo stands in.
    good = ["Cash back on the bier in Zurich", "Stuck in the black van in all the traffic", "Sitting back with a real panic",
            "Might pack the backpack in Munich"]
    ok = check_block(good, {"sylls": None, "tol": 9, "shape": None, "carpet_min_pairs": 5})
    bad = check_block(["Paid packed gone the way", "Money in the wallet and forty", "Rest of it goes on the way", "Half of the lads and the whole worst team"], HOOK_5_8)
    problems = []
    if not ok["ok"]:
        problems.append(f"a clean monorhyme block should pass the sound/grammar checks: {ok['hard']}")
    if bad["ok"] or len(bad["hard"]) < 4:
        problems.append(f"v27 dead bars should fail several checks: {bad['hard']}")
    return (not problems, "; ".join(problems) if problems else f"a clean block passes; dead v27 bars fail {len(bad['hard'])} checks")
