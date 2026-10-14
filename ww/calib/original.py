from __future__ import annotations

import os
from typing import Optional

from .. import config
from ..eval import degrade, gold
from ..llm import LLM, Ledger

ORIGINAL_QUADS = 19  # first 76 lines in 4-line quads, the same slicing toolkit/calibrate.py uses
SECTIONS = [("Hook 1-4", 0, 4), ("Hook 5-8", 4, 8), ("Hook 9-16", 8, 16), ("V1 1-8", 16, 24), ("V1 9-16", 24, 32), ("V1 17-24", 32, 40),
            ("V1 25-32", 40, 48), ("V1 33-44", 48, 60), ("V2 1-8", 60, 68), ("V2 9-16", 68, 76)]


def _lines() -> list[str]:
    if not config.PRIVATE_ORIGINAL.exists():
        raise FileNotFoundError(f"private original not found at {config.PRIVATE_ORIGINAL} (set WW_PRIVATE_ORIGINAL)")
    with open(config.PRIVATE_ORIGINAL, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()][:76]


def quads(split: Optional[str] = None) -> list[dict]:
    """[{'cluster','bars','context','slot','split','private': True}] - IN MEMORY ONLY; callers must not persist `bars`."""
    lines = _lines()
    sp = gold.original_split(ORIGINAL_QUADS)
    out = []
    for q in range(ORIGINAL_QUADS):
        a = 4 * q
        slot = next(n for n, s, e in SECTIONS if s <= a < e)
        sec_start = next(s for n, s, e in SECTIONS if s <= a < e)
        out.append({"cluster": f"orig:q{q}", "bars": lines[a:a + 4], "context": lines[max(sec_start, a - 4):a], "slot": slot,
                    "split": sp[q], "private": True})
    return [u for u in out if split is None or u["split"] == split]


def degraded(kinds: list[str], split: Optional[str] = None, seed: int = 0) -> list[dict]:
    """degradations of the original's quads, in memory; the pool for D3/D16 is the other quads."""
    units = quads(split)
    pool = [u["bars"] for u in quads()]
    res = []
    for u in units:
        for k in kinds:
            v = degrade.degrade(k, u["bars"], seed, pool)
            if v is not None:
                res.append({"cluster": u["cluster"], "kind": k, "bars": v, "context": u["context"], "split": u["split"], "private": True})
    return res


def private_llm(run_id: str = "calib") -> LLM:
    """the one constructor of a private client: no cache, no bodies, hashes only; ledger rows are flagged private."""
    return LLM(ledger=Ledger(run_id=run_id), private=True)


def selftest() -> tuple[bool, str]:
    import tempfile
    from pathlib import Path
    problems: list[str] = []
    before = {p for p in config.ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    qs = quads()
    if len(qs) != ORIGINAL_QUADS or any(len(u["bars"]) != 4 for u in qs):
        problems.append("expected 19 quads of 4 bars")
    split_counts = {s: sum(1 for u in qs if u["split"] == s) for s in ("dev", "sealed")}
    if split_counts["sealed"] < 3 or split_counts["dev"] < 8:
        problems.append(f"split looks wrong: {split_counts}")
    if not degraded(["D2", "D4"], "dev"):
        problems.append("in-memory degradations of the original did not build")
    after = {p for p in config.ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    if after != before:
        problems.append(f"calibration touched the repo: {sorted(str(p) for p in after - before)[:3]}")
    llm = private_llm("calib-selftest")
    if not llm.private:
        problems.append("private_llm must be private")
    # ledger for a private client persists hashes only; creating the client alone writes nothing
    return (not problems, "; ".join(problems) if problems else f"19 quads in memory (dev {split_counts['dev']} / sealed {split_counts['sealed']}); repo untouched")
