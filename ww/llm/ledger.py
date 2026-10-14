"""Append-only call ledger and loop budgets (plan 4.4). Every model call in ww goes through here.

A row never contains a prompt body: only hashes, sizes, usage and cost. Bodies (when allowed) live in the cache dir.
Budgets bound runaway loops; Joe set no dollar cap, so max_usd defaults to None, but call/token ceilings per scope
(run, section) are enforced and raise BudgetExceeded - the caller aborts with a report and never continues.
"""
from __future__ import annotations

import json
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .. import config


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    max_calls: Optional[int] = None
    max_usd: Optional[float] = None
    max_out_tokens: Optional[int] = None

    def check(self, totals: dict, scope: str) -> None:
        if self.max_calls is not None and totals["calls"] >= self.max_calls:
            raise BudgetExceeded(f"scope '{scope}': call ceiling {self.max_calls} reached")
        if self.max_usd is not None and totals["usd"] >= self.max_usd:
            raise BudgetExceeded(f"scope '{scope}': spend ceiling ${self.max_usd:.2f} reached (${totals['usd']:.2f})")
        if self.max_out_tokens is not None and totals["out_tokens"] >= self.max_out_tokens:
            raise BudgetExceeded(f"scope '{scope}': output-token ceiling {self.max_out_tokens} reached")


def _empty() -> dict:
    return {"calls": 0, "usd": 0.0, "in_tokens": 0, "out_tokens": 0, "cache_read": 0, "cached_hits": 0, "errors": 0}


@dataclass
class Ledger:
    run_id: str
    directory: Path = field(default_factory=lambda: config.LEDGER_DIR)
    persist: bool = True
    budgets: dict = field(default_factory=dict)  # scope -> Budget ; "*" applies to every scope
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _by_scope: dict = field(default_factory=lambda: defaultdict(_empty), repr=False)
    _by_stage: dict = field(default_factory=lambda: defaultdict(_empty), repr=False)
    _by_model: dict = field(default_factory=lambda: defaultdict(_empty), repr=False)

    def __post_init__(self):
        if self.persist:
            self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self.directory / f"{self.run_id}.jsonl"

    def preflight(self, scope: str) -> None:
        """called BEFORE a billable call; raises if the scope's ceiling is already reached."""
        with self._lock:
            for key in (scope, "*"):
                b = self.budgets.get(key)
                if b:
                    b.check(self._by_scope[scope] if key == scope else self.totals(), key)

    def record(self, *, scope: str, stage: str, model: str, in_tokens: int = 0, out_tokens: int = 0,
               cache_read: int = 0, usd: float = 0.0, cached_hit: bool = False, error: str = "",
               prompt_sha: str = "", response_sha: str = "", private: bool = False, extra: Optional[dict] = None) -> dict:
        row = {"ts": round(time.time(), 3), "run": self.run_id, "scope": scope, "stage": stage, "model": model,
               "in": in_tokens, "out": out_tokens, "cache_read": cache_read, "usd": round(usd, 6),
               "cached_hit": cached_hit, "error": error, "prompt_sha": prompt_sha, "response_sha": response_sha,
               "private": private}
        if extra:
            row["extra"] = extra
        with self._lock:
            for agg in (self._by_scope[scope], self._by_stage[stage], self._by_model[model]):
                agg["calls"] += 0 if cached_hit else 1
                agg["usd"] += usd
                agg["in_tokens"] += in_tokens
                agg["out_tokens"] += out_tokens
                agg["cache_read"] += cache_read
                agg["cached_hits"] += 1 if cached_hit else 0
                agg["errors"] += 1 if error else 0
            if self.persist:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row

    def totals(self) -> dict:
        t = _empty()
        for agg in self._by_scope.values():
            for k in t:
                t[k] += agg[k]
        return t

    def report(self) -> str:
        t = self.totals()
        lines = [f"ledger {self.run_id}: {t['calls']} calls, {t['cached_hits']} cache hits, {t['errors']} errors, "
                 f"in {t['in_tokens']:,} / out {t['out_tokens']:,} tokens, ${t['usd']:.4f}"]
        for name, table in (("stage", self._by_stage), ("model", self._by_model)):
            for k, a in sorted(table.items(), key=lambda kv: -kv[1]["usd"]):
                lines.append(f"  {name} {k}: {a['calls']} calls, out {a['out_tokens']:,}, ${a['usd']:.4f}")
        return "\n".join(lines)
