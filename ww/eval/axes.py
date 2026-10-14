"""Two-sided evaluation of a measure on one axis, with the pre-registered rule (plan 5.4). Works for deterministic measures
(flag_fn is code) and, later, for LLM readers (flag_fn calls the reader).

A measure is `flag_fn(bars: list[str]) -> bool`, True meaning "this text FAILS on the axis". For every positive unit that carries the
axis (public-domain verse, Joe's accepted bars) it builds degraded variants of the kinds expected to move the axis; a PAIR is correct
iff the positive is NOT flagged and the degraded variant IS. The unit of resampling is the cluster (the source quad/poem); the
cluster count is returned with every number. Null edits (meaning-preserving) must leave the verdict unchanged (tie rate).
Dev is free to use; the sealed split is consumed through `evaluate_sealed`, which spends the one look.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Optional

from .. import registry
from ..judge import stats
from . import degrade, gold

FlagFn = Callable[..., bool]  # flag_fn(bars, context=()) -> bool ; True = FAILS the axis


def _positives(split: str, axis: str, kinds: Optional[set] = None) -> list[dict]:
    return [r for r in gold.load(split=split)
            if r["label"] == "pos" and axis in r["axes"] and r["labelled_by"] != "assistant" and (kinds is None or r["kind"] in kinds)]


def variant_items(rows: list[dict], neg_kinds: list[str], seed: int = 0) -> list[tuple]:
    """every (bars, context) a run over `rows` will ask the measure about - lets an expensive (LLM) measure be filled in parallel."""
    pool = [r["bars"] for r in rows]
    items = []
    for r in rows:
        ctx = r.get("context") or []
        items.append((tuple(r["bars"]), tuple(ctx)))
        for kind in list(neg_kinds) + sorted(degrade.NULL):
            v = degrade.degrade(kind, r["bars"], seed, pool)
            if v is not None:
                items.append((tuple(v), tuple(ctx)))
    return items


def prefill(flag_fn: FlagFn, cache: dict, items: list[tuple], workers: int = 24) -> None:
    from concurrent.futures import ThreadPoolExecutor
    todo = [it for it in dict.fromkeys(items) if it not in cache]
    if not todo:
        return
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for it, res in zip(todo, ex.map(lambda it: bool(flag_fn(list(it[0]), list(it[1]))), todo)):
            cache[it] = res


def run(flag_fn: FlagFn, axis: str, neg_kinds: list[str], split: str = "dev", seed: int = 0, B: int = 1000,
        pos_kinds: Optional[set] = None, cache: Optional[dict] = None, workers: int = 0) -> dict:
    rows = _positives(split, axis, pos_kinds)
    pool = [r["bars"] for r in rows]
    cache = cache if cache is not None else {}
    if workers:
        prefill(flag_fn, cache, variant_items(rows, neg_kinds, seed), workers)

    def flag(bars, context=()):
        k = (tuple(bars), tuple(context))
        if k not in cache:
            cache[k] = bool(flag_fn(list(bars), list(context)))
        return cache[k]

    pairs, per_kind = [], defaultdict(list)
    false_pos, null_same, null_n = [], 0, 0
    for r in rows:
        ctx = r.get("context") or []
        pf = flag(r["bars"], ctx)
        false_pos.append((r["cluster"], 0.0 if pf else 1.0, 1.0))
        for kind in neg_kinds:
            v = degrade.degrade(kind, r["bars"], seed, pool)
            if v is None:
                continue
            ok = (not pf) and flag(v, ctx)
            pairs.append((r["cluster"], 1.0 if ok else 0.0, 1.0))
            per_kind[kind].append(1.0 if flag(v, ctx) else 0.0)
        for k in sorted(degrade.NULL):
            v = degrade.degrade(k, r["bars"], seed, pool)
            if v is not None:
                null_n += 1
                null_same += 1 if flag(v, ctx) == pf else 0
    ci = stats.cluster_bootstrap(pairs, B=B, seed=seed)
    return {"axis": axis, "split": split, "n_pos_units": len(rows), "n_pairs": len(pairs), **ci,
            "positive_pass_rate": stats.cluster_accuracy(false_pos),
            "caught_by_kind": {k: round(sum(v) / len(v), 3) for k, v in per_kind.items()},
            "null_tie": (null_same / null_n) if null_n else 1.0, "null_n": null_n}


def evaluate_sealed(measure: str, version: str, flag_fn: FlagFn, axis: str, neg_kinds: list[str], seed: int = 0) -> dict:
    """spends the ONE sealed look for (measure, version), then applies the pre-registered rule and records the verdict."""
    dev = run(flag_fn, axis, neg_kinds, "dev", seed)
    registry.spend_look(measure, version)
    sealed = run(flag_fn, axis, neg_kinds, "sealed", seed)
    verdict = registry.decide(measure, point=sealed["point"], cluster_lb=sealed["lo"], dev_point=dev["point"],
                              null_tie=sealed["null_tie"], artefact_ok=sealed["null_tie"] >= 0.7,
                              n_clusters=sealed["n_clusters"])
    return {"dev": dev, "sealed": sealed, "verdict": verdict}


def fmt(r: dict) -> str:
    kinds = ", ".join(f"{k}={v:.2f}" for k, v in sorted(r["caught_by_kind"].items()))
    return (f"[{r['split']}] axis={r['axis']}: pair accuracy {r['point']:.3f} (95% CI {r['lo']:.3f}-{r['hi']:.3f}) over "
            f"{r['n_clusters']} clusters / {r['n_pairs']} pairs; positives passing {r['positive_pass_rate']:.2f}; "
            f"null-edit tie {r['null_tie']:.2f} (n={r['null_n']}); degradation flagged: {kinds}")
