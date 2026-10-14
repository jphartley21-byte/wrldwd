"""The failure log (rule R10/R11, plan section 4 closing stage): every rejection becomes data.

One JSON object per line in eval/failures.jsonl. kinds:
  oov          a word the sound tools cannot pronounce (candidate rejected; word queued for the pronunciation chain)
  gate         a deterministic verifier fired on a bar (gate name, bar text, detail)
  reader       the semantic reader flagged a bar
  joe          a verdict from Joe, WITH his verbatim words in `joe_quote` (the only human label there is)
  frame        a filler frame to add to the ban-list
"""
from __future__ import annotations

import json
import time
from typing import Optional

from . import config


def log(kind: str, text: str, detail: str = "", source: str = "", joe_quote: Optional[str] = None, **extra) -> dict:
    row = {"ts": round(time.time(), 3), "kind": kind, "text": text, "detail": detail, "source": source}
    if joe_quote is not None:
        row["joe_quote"] = joe_quote
    row.update(extra)
    config.EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.FAILURES, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read(kind: Optional[str] = None) -> list[dict]:
    if not config.FAILURES.exists():
        return []
    rows = [json.loads(l) for l in config.FAILURES.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if kind is None or r["kind"] == kind]
