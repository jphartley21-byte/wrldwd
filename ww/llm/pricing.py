"""USD per million tokens. Sources: Anthropic pricing page and api-docs.deepseek.com/quick_start/pricing, both read on
12 Oct 2026 by research agents / this session. Re-verify before trusting dollar figures; token counts are always exact.

Anthropic rows: (input, output, cache_read); cache WRITE billed at 1.25x input; Batch halves input and output.
DeepSeek rows: ((hit, miss, out) off-peak, (hit, miss, out) peak). Peak = 01:00-04:00 and 06:00-10:00 UTC, Mon-Fri; off-peak is
half. Chinese public holidays are off-peak all day - ignored here, so the ledger can only OVER-estimate DeepSeek spend.
For DeepSeek, `in_tokens` is the cache-MISS prompt tokens and `cache_read` the cache-HIT tokens (usage fields
prompt_cache_miss_tokens / prompt_cache_hit_tokens). Reasoning tokens are part of completion_tokens (billing basis not
stated on the page; assumed output rate).
"""
from __future__ import annotations

import datetime as _dt
from typing import Optional

PRICES = {
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10),
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-fable-5-1": (10.00, 50.00, 0.25),
}
DEEPSEEK = {
    "deepseek-flash": ((0.003, 0.15, 0.60), (0.006, 0.30, 1.20)),
    "deepseek-v4-pro": ((0.022, 0.66, 1.98), (0.044, 1.32, 3.96)),
}
ALIASES = {
    "haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5", "fable": "claude-fable-5-1",
    "ds-flash": "deepseek-flash", "ds-pro": "deepseek-v4-pro",
    "deepseek-v4-flash": "deepseek-flash",  # retired name, still served and billed as Flash
}
CACHE_WRITE_FACTOR = 1.25


def resolve(model: str) -> str:
    return ALIASES.get(model, model)


def provider(model: str) -> str:
    m = resolve(model)
    if m.startswith("claude"):
        return "anthropic"
    if m.startswith("deepseek"):
        return "deepseek"
    if m.startswith("stub"):
        return "stub"
    return "ollama"


def is_deepseek_peak(when: Optional[_dt.datetime] = None) -> bool:
    w = (when or _dt.datetime.now(_dt.timezone.utc)).astimezone(_dt.timezone.utc)
    return w.weekday() < 5 and (1 <= w.hour < 4 or 6 <= w.hour < 10)


def cost_usd(model: str, in_tokens: int, out_tokens: int, cache_read: int = 0, cache_write: int = 0,
             batch: bool = False, when: Optional[_dt.datetime] = None) -> float:
    """Unknown models (local Ollama, stub) cost 0."""
    m = resolve(model)
    if m in DEEPSEEK:
        hit, miss, out = DEEPSEEK[m][1 if is_deepseek_peak(when) else 0]
        return (cache_read * hit + in_tokens * miss + out_tokens * out) / 1e6
    p = PRICES.get(m)
    if p is None:
        return 0.0
    pin, pout, pcache = p
    usd = (in_tokens * pin + out_tokens * pout + cache_read * pcache + cache_write * pin * CACHE_WRITE_FACTOR) / 1e6
    return usd * (0.5 if batch else 1.0)
