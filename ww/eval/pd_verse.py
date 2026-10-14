"""Public-domain comic verse as NON-ORIGINAL positives (plan 5.1): Belloc's Cautionary Tales (1907), Gilbert's Bab Ballads
(1869-71) and the Gilbert & Sullivan libretti (1870s-90s). Project Gutenberg texts (public domain in the US; Gilbert d.1911,
Belloc d.1953 are public domain in the UK too). Raw files live OUTSIDE the repo (config.PD_RAW); only derived 4-line quads with
provenance are stored in eval/pd_verse/quads.jsonl.

What they are for: dense deadpan wordplay in fluent spoken British English, so the sense/grammar/referent axes have positives
that are not Mr Worldwide and not our own writing. What they are NOT: a model of the target genre or of rap flow.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .. import bridge, config

SOURCES = {
    "belloc_cautionary_tales": ("belloc_cautionary_tales_pg27424.txt", "plain", "Gutenberg #27424"),
    "gilbert_fifty_bab_ballads": ("gilbert_fifty_bab_ballads_pg757.txt", "plain", "Gutenberg #757"),
    "gilbert_more_bab_ballads": ("gilbert_more_bab_ballads_pg933.txt", "plain", "Gutenberg #933"),
    "gilbert_sullivan_complete_plays": ("gilbert_sullivan_complete_plays_pg808.txt", "songs", "Gutenberg #808"),
}
PER_SOURCE_CAP = 120
OUT = config.EVAL_DIR / "pd_verse" / "quads.jsonl"


def _body(text: str) -> list[str]:
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("*** START OF")), 0)
    end = next((i for i, l in enumerate(lines) if l.startswith("*** END OF")), len(lines))
    return lines[start + 1:end]


def _clean(line: str) -> str:
    return re.sub(r"\s+", " ", bridge.norm(line).replace("_", "")).strip()


def _blocks(lines: list[str], kind: str) -> list[list[str]]:
    blocks, cur = [], []
    for raw in lines:
        indented = len(raw) - len(raw.lstrip(" ")) >= 8
        keep = (raw.strip() != "") and (indented if kind == "songs" else True)
        if keep:
            cur.append(_clean(raw))
        else:
            if cur:
                blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def _is_verse(quad: list[str]) -> bool:
    if len(quad) != 4:
        return False
    if any(len(l) < 12 or len(l) > 85 or l.isupper() or l.startswith(("[", "(")) for l in quad):
        return False
    pairs = sum(1 for i in range(4) for j in range(i + 1, 4)
                if bridge.rhyme_score(re.sub(r"[^A-Za-z' ]", "", quad[i]), re.sub(r"[^A-Za-z' ]", "", quad[j])) >= 0.8)
    return pairs >= 2


def extract(raw_dir: Path | None = None) -> list[dict]:
    raw_dir = raw_dir or config.PD_RAW
    rows = []
    for name, (fname, kind, pg) in SOURCES.items():
        path = raw_dir / fname
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        quads = []
        for bi, block in enumerate(_blocks(_body(text), kind)):
            if not 4 <= len(block) <= 16:
                continue
            for k in range(0, len(block) - 3, 4):
                q = block[k:k + 4]
                if _is_verse(q):
                    quads.append({"source": name, "pg": pg, "block": bi, "bars": q, "context": block[max(0, k - 4):k]})
        quads.sort(key=lambda r: hashlib.sha256("\n".join(r["bars"]).encode()).hexdigest())
        rows += quads[:PER_SOURCE_CAP]
    for r in rows:
        r["cluster"] = f"pd:{r['source']}:{r['block']}"
        r["licence"] = "public domain (Project Gutenberg; US PD, author d. before 1955)"
    return rows


def build(raw_dir: Path | None = None) -> int:
    rows = extract(raw_dir)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return len(rows)


def load() -> list[dict]:
    if not OUT.exists():
        return []
    return [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()]
