"""Pairwise validation of the comparative ranker (plan 5.3/5.4): does it prefer the real text to its own degraded variant?

For each positive unit and each degradation kind it shows the pair in BOTH orders. Outcomes: correct (real text wins both orders),
wrong (degraded wins both), tie (the order flips the verdict - position bias, counted as 0.5 and reported as the flip rate). Null edits
(meaning-preserving) should come out as ties or coin-flips, never as a confident preference. Resampling is by cluster.
"""
from __future__ import annotations

import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from ..judge import rank, stats
from ..llm import LLM
from . import axes, degrade


def _duel(llm: LLM, a: list[str], b: list[str], ctx: list[str], model: str, effort: Optional[str]) -> float:
    """1.0 if `a` wins both presentation orders, 0.0 if `b` does, 0.5 on disagreement or an unusable reply."""
    o1 = rank.rank_batch(llm, [("a", a), ("b", b)], model, effort, context=ctx or None)
    o2 = rank.rank_batch(llm, [("b", b), ("a", a)], model, effort, context=ctx or None)
    if not o1 or not o2:
        return 0.5
    w1, w2 = o1[0] == "a", o2[0] == "a"
    return 1.0 if (w1 and w2) else 0.0 if (not w1 and not w2) else 0.5


def run(llm: LLM, kinds: list[str], split: str = "dev", axis: str = "sense", limit: Optional[int] = None, seed: int = 0,
        model: str = "ds-flash", effort: Optional[str] = None, workers: int = 16, pos_kinds: Optional[set] = None) -> dict:
    rows = axes._positives(split, axis, pos_kinds)
    if limit:
        rows = random.Random(seed).sample(rows, min(limit, len(rows)))
    pool = [r["bars"] for r in rows]
    jobs = []
    for r in rows:
        ctx = r.get("context") or []
        for k in kinds:
            v = degrade.degrade(k, r["bars"], seed, pool)
            if v is not None and v != r["bars"]:
                jobs.append((r["cluster"], k, r["bars"], v, ctx))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        scores = list(ex.map(lambda j: _duel(llm, j[2], j[3], j[4], model, effort), jobs))
    per_kind: dict[str, list] = defaultdict(list)
    for (cl, k, *_), sc in zip(jobs, scores):
        per_kind[k].append((cl, sc, 1.0))
    out = {"split": split, "n_positives": len(rows), "model": model, "effort": effort, "kinds": {}}
    for k, units in per_kind.items():
        ci = stats.cluster_bootstrap(units, B=500, seed=seed)
        ties = sum(1 for _, s, _ in units if s == 0.5) / len(units)
        wrong = sum(1 for _, s, _ in units if s == 0.0) / len(units)
        out["kinds"][k] = {"accuracy": round(ci["point"], 3), "lo": round(ci["lo"], 3), "hi": round(ci["hi"], 3), "tie_rate": round(ties, 3),
                           "wrong_rate": round(wrong, 3), "n_clusters": ci["n_clusters"]}
    return out


def fmt(r: dict) -> str:
    lines = [f"pairwise [{r['split']}] model={r['model']} effort={r['effort']} positives={r['n_positives']} (tie = order flips the verdict, counted 0.5)"]
    for k, v in sorted(r["kinds"].items()):
        lines.append(f"  {k:4s} acc {v['accuracy']:.2f} (CI {v['lo']:.2f}-{v['hi']:.2f}) tie {v['tie_rate']:.2f} wrong {v['wrong_rate']:.2f} clusters {v['n_clusters']}")
    return "\n".join(lines)
