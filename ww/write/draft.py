"""First end-to-end draft of ONE block (plan section 5 funnel), with every stage's yield reported (R10).

facts -> seeds (shape-aware) -> top seeds per fact (comparative ranker on the claims) -> candidate blocks -> deterministic verifier
-> reader floor + empty-flags -> comparative ranking of survivors -> best blocks with per-bar flags.
This is a FIRST-LOOK pipeline: its judge is validated on dev (pairwise 87-100% against damage) but its notion of 'funny' is not.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from ..judge import rank, reader
from ..llm import LLM
from . import block_writer, seed_stage, sound_plan, verify_det
from .seed_stage import Fact


def pick_seeds(llm: LLM, facts: list[Fact], per_fact_seeds: int = 8, keep_per_fact: int = 2, model: str = "ds-flash") -> tuple[list[tuple], dict]:
    """returns [(fact, seed)] and the stage yield."""
    y = {"facts": len(facts), "seeds_generated": 0, "seeds_valid": 0, "seeds_kept": 0}

    def gen(f):
        r = seed_stage.run(llm, f, n=per_fact_seeds, model=model, effort="high", shape="trochee")
        return f, r
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(gen, facts))
    chosen = []
    for f, r in res:
        y["seeds_generated"] += len(r["kept"]) + len(r["dropped"])
        y["seeds_valid"] += len(r["kept"])
        if not r["kept"]:
            continue
        items = {str(i): [s["persona_claim"]] for i, s in enumerate(r["kept"])}
        if len(items) > keep_per_fact:
            out = rank.rank_items(llm, items, batch_size=4, rounds=3, seed=1, model=model, stage="rank_seeds", workers=4)
            order = sorted(out["bt"], key=lambda k: -out["bt"][k])
            top = [r["kept"][int(i)] for i in order[:keep_per_fact]]
        else:
            top = r["kept"]
        chosen += [(f, s) for s in top]
    y["seeds_kept"] = len(chosen)
    return chosen, y


def write_blocks(llm: LLM, chosen: list[tuple], n: int = 6, model: str = "ds-flash", effort: str = "low") -> list[dict]:
    def go(fs):
        f, s = fs
        try:
            return block_writer.run(llm, s, f, n=n, model=model, effort=effort)
        except Exception as e:  # noqa: BLE001 - one failed seed must not sink the run
            return []
    with ThreadPoolExecutor(4) as ex:
        return [b for bl in ex.map(go, chosen) for b in bl]


def filter_blocks(blocks: list[dict], spec: dict = verify_det.HOOK_5_8_SOFT) -> tuple[list[dict], dict]:
    y = {"candidates": len(blocks), "pass_det": 0, "rejects": {}}
    keep = []
    for b in blocks:
        bars = [x["text"] for x in b["bars"]]
        c = verify_det.check_block(bars, spec)
        b["det"] = c
        if c["ok"]:
            y["pass_det"] += 1
            keep.append(b)
        else:
            for h in c["hard"]:
                k = h.split(": ", 1)[1].split(" (")[0][:30] if ": " in h else h[:30]
                y["rejects"][k] = y["rejects"].get(k, 0) + 1
            # R10: every rejection becomes data. Nothing wrote this log before 14 Oct 2026, so the same defect was
            # re-generated round after round with no record of it.
            from .. import failures
            failures.log("gate", " | ".join(bars), detail="; ".join(c["hard"])[:300], source="draft:filter")
    return keep, y


def read_blocks(llm: LLM, blocks: list[dict], model: str = "ds-flash", max_persona_none: int = 2) -> tuple[list[dict], dict]:
    def go(b):
        rd = reader.read_run(llm, [x["text"] for x in b["bars"]], model=model, stage="reader", scope="judge")
        return reader.summarise(rd), rd
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(go, blocks))
    keep = []
    y = {"read": len(blocks), "pass_floor": 0, "clean_of_empty_flags": 0}
    for b, (s, rd) in zip(blocks, res):
        ok, why = reader.passes(s)
        b["reader"] = {"summary": s, "floor_ok": ok, "why": why, "empty_flags": reader.empty_flags(s), "bars": rd.get("bars", [])}
        y["pass_floor"] += ok
        y["clean_of_empty_flags"] += (not b["reader"]["empty_flags"])
        persona_ok = s["persona_none"] <= max_persona_none
        b["reader"]["persona_ok"] = persona_ok
        y["persona_ok"] = y.get("persona_ok", 0) + persona_ok
        if ok and not b["reader"]["empty_flags"] and persona_ok:
            keep.append(b)
    return keep, y


def rank_blocks(llm: LLM, blocks: list[dict], rounds: int = 3, model: str = "ds-flash") -> list[dict]:
    if len(blocks) < 2:
        return blocks
    items = {str(i): [x["text"] for x in b["bars"]] for i, b in enumerate(blocks)}
    out = rank.rank_items(llm, items, batch_size=4, rounds=rounds, seed=2, model=model, stage="rank_blocks", workers=6)
    for i, b in enumerate(blocks):
        b["rank"] = {"bt": round(out["bt"].get(str(i), -9), 3), "mean_rank": round(out["mean_rank"].get(str(i), 1.0), 3)}
    blocks.sort(key=lambda b: -b["rank"]["bt"])
    return blocks


def shortlist(blocks: list[dict], k: int = 6, per_payoff: int = 1, per_fact: int = 2) -> list[dict]:
    """top-k by rank with a diversity cap, so six variants of one idea cannot fill the list (the first two runs were dominated by one seed)."""
    out, by_payoff, by_fact = [], {}, {}
    for b in blocks:
        p, f = b["seed"]["payoff_word"], b["fact"]
        if by_payoff.get(p, 0) >= per_payoff or by_fact.get(f, 0) >= per_fact:
            continue
        by_payoff[p] = by_payoff.get(p, 0) + 1
        by_fact[f] = by_fact.get(f, 0) + 1
        out.append(b)
        if len(out) == k:
            break
    return out


def draft_block(llm: LLM, facts: list[Fact], n_per_seed: int = 6, per_fact_seeds: int = 8, keep_per_fact: int = 2, model: str = "ds-flash",
                write_effort: str = "low") -> dict:
    chosen, y1 = pick_seeds(llm, facts, per_fact_seeds, keep_per_fact, model)
    cands = write_blocks(llm, chosen, n_per_seed, model, write_effort)
    det_ok, y2 = filter_blocks(cands)
    read_ok, y3 = read_blocks(llm, det_ok, model)
    ranked = rank_blocks(llm, read_ok, model=model)
    return {"yield": {"seeds": y1, "blocks": y2, "reader": y3, "final": len(ranked)}, "ranked": ranked, "chosen_seeds": [(f.id, s) for f, s in chosen],
            "det_rejected_sample": [b for b in cands if not b.get("det", {}).get("ok", True)][:8]}
