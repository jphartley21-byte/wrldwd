"""PRIVATE calibration (plan section 1 decision, extended to DeepSeek by Joe on 13 Oct 2026).

The ONLY place that reads the original's lines and the only place allowed to build a private (`private=True`) LLM client. Rules:
  - the text exists in memory only: nothing from it is written to the repo, the cache, the ledger (hashes only) or logs;
  - it is used for calibration/benchmark runs, never for generation prompts (writer code may not import this package - enforced
    by `python -m ww.cli selftest` source guards);
  - results leave this package as numbers (scores per quad id), never as text.
"""
from .original import ORIGINAL_QUADS, quads, private_llm, selftest  # noqa: F401
