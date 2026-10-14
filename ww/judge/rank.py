"""Comparative ranker (plan 5.3): forced ranking of 2-6 candidate runs per call, shuffled, repeated over orders and resamples,
aggregated with Bradley-Terry. Comparative judgements are far better behaved than absolute pass/fail (the pilot showed the
absolute reader passing two blocks Joe rejected); this is what SELECTS among candidates. The prompt states what good looks
like in craft terms (benchmark/craft_principles.md) and never quotes the original.

`rank_items(llm, items)` takes {id: bars} and returns BT strengths, mean ranks, and per-call position-flip diagnostics.
Everything numeric is computed here; the model returns an ordering and one-line reasons only.
"""
from __future__ import annotations

import itertools
import random
from collections import defaultdict
from typing import Optional

from ..llm import LLM, Request
from . import stats

RANK_SCHEMA = {
    "type": "object", "required": ["ranking"],
    "properties": {"ranking": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                   "reasons": {"type": "array", "items": {"type": "string"}}},
}

SYSTEM = """You are a strict British editor choosing between candidate runs of comic rap lyrics (consecutive bars of one verse, spoken at pace).
Rank them best to worst for how well each WORKS AS WRITING. Judge, in this order of importance:
1. Does it say something? Every bar should state or do something a listener can follow; a bar you can only understand by inventing meaning is a failure.
2. Is it spoken English? Could a British speaker say it aloud; no word-strings, missing objects, dangling pronouns or words chosen only to rhyme.
3. Is there a character and a payoff? A stable voice (deadpan, nonchalant, boasting) reporting something extraordinary or petty in a flat everyday register, with the run
   landing on its last stressed word - not a list of observations.
4. Is it specific (named place, price, object, brand, action) rather than generic travel talk? Cliche, filler frames, explained jokes and moral endings count against it.
Ignore rhyme density and flow unless they break sense. Do not reward length. Do not reward a run for sounding polished if it says nothing.
Return JSON: {"ranking": [ids from best to worst, every id exactly once], "reasons": [one short clause per id in the same order]}."""


def _fmt(items: list[tuple[str, list[str]]], letters: str) -> str:
    return "\n\n".join(f"CANDIDATE {letters[i]}:\n" + "\n".join(f"  {b}" for b in bars) for i, (_, bars) in enumerate(items))


def rank_batch(llm: LLM, batch: list[tuple[str, list[str]]], model: str = "ds-flash", effort: Optional[str] = None,
               stage: str = "rank", scope: str = "judge", context: Optional[list[str]] = None) -> list[str]:
    """one forced ranking of `batch` (already in the order to present); returns item ids best-first, or [] if the reply was unusable."""
    letters = "ABCDEFGH"[:len(batch)]
    ctx = ("CONTEXT (earlier lines of the same verse, not ranked):\n" + "\n".join(context) + "\n\n") if context else ""
    res = llm.complete(Request(model=model, system=SYSTEM, schema=RANK_SCHEMA, max_tokens=1200, effort=effort,
                               temperature=0.0 if effort is None else None, stage=stage, scope=scope,
                               messages=[{"role": "user", "content": ctx + _fmt(batch, letters) + "\n\nUse ids " + ", ".join(letters) + "."}]))
    order = (res.parsed or {}).get("ranking") or []
    letter_to_id = {letters[i]: batch[i][0] for i in range(len(batch))}
    ids = [letter_to_id.get(str(x).strip().upper()[:1]) for x in order]
    if sorted(i for i in ids if i) != sorted(letter_to_id.values()):
        return []
    return ids


def rank_items(llm: LLM, items: dict[str, list[str]], *, batch_size: int = 4, rounds: int = 3, seed: int = 0,
               model: str = "ds-flash", effort: Optional[str] = None, context: Optional[list[str]] = None,
               stage: str = "rank", scope: str = "judge", workers: int = 8) -> dict:
    """shuffled batches, `rounds` repetitions with fresh shuffles (and each batch also presented reversed, to expose position bias).
    Returns {'bt': {id: log-strength}, 'mean_rank': {id: float}, 'calls': n, 'flips': position-flip rate, 'unusable': n}."""
    from concurrent.futures import ThreadPoolExecutor
    rng = random.Random(seed)
    ids = sorted(items)
    jobs: list[list[str]] = []
    for _ in range(rounds):
        order = ids[:]
        rng.shuffle(order)
        chunks = [order[i:i + batch_size] for i in range(0, len(order), batch_size)]
        if len(chunks) > 1 and len(chunks[-1]) < 2:  # never a batch of one
            tail = chunks.pop()
            chunks[-1] = chunks[-1] + tail
        for ch in chunks:
            if len(ch) >= 2:
                jobs.append(ch)
                jobs.append(list(reversed(ch)))      # same batch, opposite presentation order
    def run(job):
        return job, rank_batch(llm, [(i, items[i]) for i in job], model, effort, stage, scope, context)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(run, jobs))
    wins: dict[tuple[str, str], float] = defaultdict(float)
    ranks: dict[str, list[float]] = defaultdict(list)
    unusable = 0
    for job, order in results:
        if not order:
            unusable += 1
            continue
        for pos, i in enumerate(order):
            ranks[i].append(pos / (len(order) - 1))
        for a, b in itertools.combinations(order, 2):   # a ranked above b
            wins[(a, b)] += 1.0
    flips = pairs = 0
    byb: dict[frozenset, list] = defaultdict(list)
    for job, order in results:
        if order:
            byb[frozenset(job)].append(order)
    for orders in byb.values():
        for o1, o2 in itertools.combinations(orders, 2):
            for a, b in itertools.combinations(sorted(o1), 2):
                pairs += 1
                flips += 1 if (o1.index(a) < o1.index(b)) != (o2.index(a) < o2.index(b)) else 0
    return {"bt": stats.bradley_terry(dict(wins)) if wins else {}, "mean_rank": {i: sum(v) / len(v) for i, v in ranks.items()},
            "calls": len(jobs), "flip_rate": (flips / pairs) if pairs else 0.0, "unusable": unusable}


def selftest() -> tuple[bool, str]:
    import json
    import tempfile
    from pathlib import Path
    from ..llm import Ledger, StubBackend
    problems: list[str] = []

    def handler(req):
        # a stub 'judge' that ranks by candidate length of the first line (longer = better), consistently
        txt = req.messages[0]["content"]
        cands = {}
        cur = None
        for line in txt.splitlines():
            if line.startswith("CANDIDATE "):
                cur = line.split()[1].rstrip(":")
                cands[cur] = ""
            elif cur and line.startswith("  "):
                cands[cur] += line.strip()
        order = sorted(cands, key=lambda k: -len(cands[k]))
        return json.dumps({"ranking": order, "reasons": ["x"] * len(order)})
    with tempfile.TemporaryDirectory() as td:
        llm = LLM(ledger=Ledger(run_id="rk", persist=False), stub=StubBackend({"rank": handler}), cache_dir=Path(td))
        items = {"a": ["short"], "b": ["a bit longer line here"], "c": ["the longest line of all of them, honestly"], "d": ["mid length line"],
                 "e": ["x"]}
        out = rank_items(llm, items, model="stub-1", rounds=2, workers=2)
        order = sorted(out["bt"], key=lambda k: -out["bt"][k])
        if order[0] != "c" or order[-1] != "e":
            problems.append(f"BT order should put longest first and shortest last: {order}")
        if out["flip_rate"] != 0.0 or out["unusable"]:
            problems.append(f"consistent judge should have 0 flips: {out['flip_rate']}, unusable {out['unusable']}")
    return (not problems, "; ".join(problems) if problems else "batched forced ranking, reversed presentation, BT aggregation behave on a stub judge")
