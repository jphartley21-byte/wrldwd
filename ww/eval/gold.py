"""eval/gold.jsonl - the labelled set every judge/measure is validated against (plan 5.1, 5.4).

One row per labelled UNIT (a block, or a single bar with its section as context). Fields:
  id, kind (joe_accepted | joe_rejected | joe_contender | joe_inventory | assistant_v27 | pd_verse | original_slot),
  label (pos | neg | neutral), bars, context (section bars for single-bar units), labelled_by (joe | assistant | none),
  weight, axes (which failure axes this label speaks to), joe_quote, quote_exact, source, cluster, split (dev | sealed).

Rules: assistant-made labels are weight 0.25 and ALWAYS dev (R14). Split = hash of the cluster id (60% dev / 40% sealed) so a
whole block or poem lands on one side; nothing is re-split after the pre-registration is written. The original's text is never
here: `original_split()` returns only the quad-index -> split map; ww.calib reads the private file at run time.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Optional

from .. import config
from . import assistant_labels, joe_verdicts, pd_verse

GOLD = config.EVAL_DIR / "gold.jsonl"
DEV_SHARE = 60  # percent of clusters in dev


# With only two Joe-positive blocks (three until 15 Oct 2026) a hash split is a coin toss that can leave the sealed side with none. These are placed by
# hand BEFORE the pre-registration is locked: V-a is the Hook 5-8 rediscovery target, so it must never be seen while tuning.
FORCED_SPLIT = {"joe_hook_5-8_V-a": "sealed", "joe_majorca_v5": "dev"}   # joe_hook_1-4 removed 15 Oct 2026 (never approved)


def split_of(cluster: str) -> str:
    if cluster in FORCED_SPLIT:
        return FORCED_SPLIT[cluster]
    h = int(hashlib.sha256(("ww-split-v1:" + cluster).encode()).hexdigest()[:8], 16) % 100
    return "dev" if h < DEV_SHARE else "sealed"


def original_split(n_quads: int = 19) -> dict:
    """quad index (0-based, 4-bar quads over the original's first 76 lines) -> dev | sealed. No text."""
    return {i: split_of(f"orig:q{i}") for i in range(n_quads)}


def parse_draft(path) -> dict[str, list[str]]:
    """'== Slot' headers then bars; '#' comment lines and blanks skipped (the project format)."""
    sections: dict[str, list[str]] = {}
    cur = None
    text = path.read_text(encoding="utf-8").lstrip("﻿")
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("=="):
            cur = line.lstrip("= ").strip()
            sections[cur] = []
        elif line and not line.startswith("#") and cur is not None:
            sections[cur].append(line)
    return sections


def _row(**kw) -> dict:
    kw.setdefault("context", [])
    kw.setdefault("joe_quote", "")
    kw.setdefault("quote_exact", False)
    kw["split"] = "dev" if kw["labelled_by"] == "assistant" else split_of(kw["cluster"])
    return kw


def build_rows(draft_path=None) -> list[dict]:
    rows: list[dict] = []
    for vid, label, bars, quote, exact, axes, source, strength in joe_verdicts.VERDICTS:
        kind = {"accept": "joe_accepted", "reject": "joe_rejected", "contender": "joe_contender"}[label]
        rows.append(_row(id=vid, kind=kind, label={"accept": "pos", "reject": "neg", "contender": "pos"}[label],
                         bars=bars, labelled_by="joe", weight=1.0 if label != "contender" else 0.5, axes=axes,
                         joe_quote=quote, quote_exact=exact, source=source, cluster=vid, strength=strength))
    for stem, (quote, exact, axes) in joe_verdicts.REJECTED_FILES.items():
        path = config.TOOLKIT / "tests" / f"{stem}.txt"
        if not path.exists():
            continue
        bars = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        rows.append(_row(id=f"rej_{stem}", kind="joe_rejected", label="neg", bars=bars, labelled_by="joe", weight=1.0,
                         axes=axes, joe_quote=quote, quote_exact=exact, source=f"toolkit/tests/{stem}.txt", cluster=f"rej_{stem}",
                         strength="rejected"))
    for i, bar in enumerate(joe_verdicts.INVENTORY_BARS):
        rows.append(_row(id=f"inv_{i}", kind="joe_inventory", label="neg", bars=[bar], labelled_by="mixed", weight=0.5,
                         axes=["sense"], source="ml/meaning_judge.py LABELLED; STATE.md 13 Oct", cluster=f"inv_{i}",
                         strength="listed_as_nothing"))
    draft = parse_draft(draft_path or config.WRITING / "full_draft_v27.md")
    for slot, letters in assistant_labels.V27_LABELS.items():
        bars = draft.get(slot, [])
        if len(bars) != len(letters):
            raise ValueError(f"v27 '{slot}' has {len(bars)} bars but the label string has {len(letters)}")
        for i, (bar, c) in enumerate(zip(bars, letters), 1):
            if c in assistant_labels.NEGATIVE:
                lab, why = "neg", assistant_labels.NEGATIVE[c]
            elif c in assistant_labels.POSITIVE:
                lab, why = "pos", assistant_labels.POSITIVE[c]
            else:
                continue  # F = neutral fragment: not used for accuracy
            rows.append(_row(id=f"v27:{slot}:{i}", kind="assistant_v27", label=lab, bars=[bar], context=bars,
                             labelled_by="assistant", weight=0.25, axes=["sense"], source="writing/full_draft_v27.md",
                             cluster=f"v27:{slot}", strength=why))
    for r in pd_verse.load():
        rows.append(_row(id=f"pd:{r['source']}:{r['block']}:{hashlib.sha256(chr(10).join(r['bars']).encode()).hexdigest()[:8]}",
                         kind="pd_verse", label="pos",
                         bars=r["bars"], context=r.get("context", []), labelled_by="none", weight=0.5,
                         axes=["sense", "grammar", "referent"], source=r["pg"],
                         cluster=r["cluster"], licence=r["licence"], strength="published_comic_verse"))
    return rows


def write(draft_path=None) -> list[dict]:
    rows = build_rows(draft_path)
    config.EVAL_DIR.mkdir(parents=True, exist_ok=True)
    GOLD.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return rows


def load(split: Optional[str] = None, kind: Optional[str] = None) -> list[dict]:
    if not GOLD.exists():
        return []
    rows = [json.loads(l) for l in GOLD.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if (split is None or r["split"] == split) and (kind is None or r["kind"] == kind)]


def stats(rows: Optional[list[dict]] = None) -> str:
    rows = rows if rows is not None else load()
    by = Counter((r["kind"], r["label"], r["split"]) for r in rows)
    lines = [f"gold set: {len(rows)} units, {len({r['cluster'] for r in rows})} clusters"]
    for k, v in sorted(by.items()):
        lines.append(f"  {k[0]:16s} {k[1]:8s} {k[2]:7s} {v}")
    sealed = [r for r in rows if r["split"] == "sealed"]
    lines.append(f"  sealed: {len(sealed)} units in {len({r['cluster'] for r in sealed})} clusters; "
                 f"sealed NEGATIVES by Joe: {sum(1 for r in sealed if r['label'] == 'neg' and r['labelled_by'] == 'joe')} "
                 f"(clusters: {len({r['cluster'] for r in sealed if r['label'] == 'neg' and r['labelled_by'] == 'joe'})})")
    o = Counter(original_split().values())
    lines.append(f"  original (private, not stored): 19 quads -> dev {o['dev']} / sealed {o['sealed']}")
    return "\n".join(lines)


def selftest() -> tuple[bool, str]:
    problems: list[str] = []
    rows = build_rows()
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    if any(r["labelled_by"] == "assistant" and r["split"] != "dev" for r in rows):
        problems.append("assistant label outside dev")
    if any(re.search(r"original", r["source"], re.I) and r["kind"] == "original_slot" for r in rows):
        problems.append("original text must not be in gold")
    if not any(r["kind"] == "joe_accepted" for r in rows) or not any(r["kind"] == "joe_rejected" for r in rows):
        problems.append("need Joe positives and negatives")
    if split_of("x") != split_of("x") or set(original_split().values()) != {"dev", "sealed"}:
        problems.append("split not deterministic or one-sided")
    return (not problems, "; ".join(problems) if problems else f"{len(rows)} units build cleanly; splits deterministic")
