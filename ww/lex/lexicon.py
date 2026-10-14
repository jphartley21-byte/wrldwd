"""The writers' lexicon: brands, slang, dialect, places, local words, roles, props, idioms with literal readings, pun pairs.

A dictionary does not carry most of what a British rap needs (Greggs, Wetherspoons, wagwan, Horfield, gert lush, "the man from the council").
Rows live in ww/lex/banks/lexicon.jsonl; every token is run through the pronunciation chain (cmudict, OVR, compound split, g2p without nltk) so
the rhyme tools can measure them and the checker never says "cannot pronounce" about a real brand.

  python -m ww.cli lex                       group counts
  python -m ww.cli lex brand --q tesco       search
  python -m ww.cli bank lorry                the rhyme-family report includes brands, slang, places, roles, local words, idioms in the family
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from .. import bridge

BANK = Path(__file__).resolve().parent / "banks" / "lexicon.jsonl"

GROUPS = {
    "brand": ["supermarkets", "highstreet", "grocery", "snacks", "softdrinks", "alcohol", "restaurants", "travelbrands", "vehicles", "techfinance", "clothing", "household", "vice", "worldfood", "watches"],
    "media": ["tv", "music"],
    "slang": ["slang1", "slang2", "dialect", "cockney", "money"],
    "abbr": ["abbreviations"],
    "place": ["ukplaces1", "ukplaces2", "europeplaces", "worldplaces"],
    "local": ["localwords1", "localwords2"],
    "role": ["roles"],
    "prop": ["props"],
    "idiom": ["idioms1", "idioms2"],
    "pun": ["homophones"],
    "redup": ["redup"],
    "onoma": ["onoma"],
    "pop": ["pop", "actors"],
    "loaded": ["loaded"],
    "oronym": ["oronym"],
    "hidden": ["hidden"],
    "game": ["games"],
    "chain": ["chains"],
    "bridge": ["bridges"],
}
KEY2GROUP = {k: g for g, ks in GROUPS.items() for k in ks}
_TOK = re.compile(r"[A-Za-z']+")


def norm_text(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip()).lower()


def load() -> list[dict]:
    if not BANK.exists():
        return []
    return [json.loads(l) for l in BANK.read_text(encoding="utf-8").splitlines() if l.strip()]


def save(rows: list[dict]) -> None:
    BANK.parent.mkdir(parents=True, exist_ok=True)
    BANK.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8", newline="\n")


def ingest(result: list[dict]) -> dict:
    """result = the lexicon workflow's return: [{key, rows:[{text, kind, country, gloss, say, extra}]}]. Deduplicates on (group, text)."""
    have = {(r["group"], norm_text(r["text"])) for r in load()}
    rows = load()
    added = {}
    for cat in result:
        key = cat["key"]
        grp = KEY2GROUP.get(key, "misc")
        for r in cat.get("rows", []):
            text = (r.get("text") or "").strip()
            if not text or len(text) > 90:
                continue
            k = (grp, norm_text(text))
            if k in have:
                continue
            have.add(k)
            rec = {"text": text, "group": grp, "cat": key, "kind": r.get("kind", ""), "country": r.get("country", ""), "gloss": r.get("gloss", ""),
                   "say": r.get("say", ""), "extra": r.get("extra", "")}
            rows.append(rec)
            added[grp] = added.get(grp, 0) + 1
    save(rows)
    return added


def tokens(text: str) -> list[str]:
    return [t.lower().strip("'") for t in _TOK.findall(bridge.norm(text)) if len(t.strip("'")) >= 1]


def pronounce_all(rows: Optional[list[dict]] = None, verbose: bool = False) -> dict:
    """run every token of every row through the pron chain; persist new overrides once."""
    from . import pron
    rows = rows if rows is not None else load()
    seen: set[str] = set()
    stats = {"known": 0, "compound": 0, "g2p": 0, "none": 0, "tokens": 0}
    d = pron._load()
    for r in rows:
        for t in tokens(r["text"]):
            w = re.sub(r"[^a-z]", "", t)
            if not w or w in seen:
                continue
            seen.add(w)
            stats["tokens"] += 1
            rec = pron.ensure(w, persist=False)
            src = rec["source"] or "none"
            stats[src] = stats.get(src, 0) + 1
            if src in ("compound", "g2p"):
                d[w] = {k: v for k, v in rec.items() if k != "word"}
                d[w]["lexicon"] = True          # the lexicon vouches that this is a real word/name, so it is not an 'invented word'
                pron.GUESSED.discard(w)
            elif w in d and src == "known":
                d[w]["lexicon"] = True
    pron._save(d)
    return stats


def end_token(r: dict) -> Optional[str]:
    if r["group"] in ("idiom", "game"):
        m = re.search(r"payoff:\s*([A-Za-z']+)", r.get("extra", ""))
        if m:
            return m.group(1).lower()
    if r["group"] == "pun":
        parts = [p.strip() for p in r["text"].split("/")]
        return tokens(parts[-1])[-1] if parts and tokens(parts[-1]) else None
    tk = tokens(r["text"])
    return tk[-1] if tk else None


_INDEX: dict = {}


def _index() -> dict:
    if _INDEX:
        return _INDEX
    import rhyme_tools as rt
    bridge._toolkit_on_path()
    idx: dict = {}
    for r in load():
        if r.get("avoid"):
            continue
        e = end_token(r)
        if not e:
            continue
        ph = rt.pron(e)
        if not ph:
            continue
        kk = rt.key(ph, 0, "perfect")
        if kk:
            idx.setdefault(kk, []).append((e, r))
    _INDEX.update(idx)
    return _INDEX


def family(seed: str, min_score: float = 0.9) -> dict:
    """{group: [row, ...]} for rows whose last word perfectly rhymes with `seed` (British phones)."""
    import rhyme_tools as rt
    bridge._toolkit_on_path()
    ph, _bad = rt.pron_phrase(seed)
    if ph is None:
        bridge.stress_pattern(seed)
        ph, _bad = rt.pron_phrase(seed)
    if ph is None:
        return {}
    kk = rt.key(ph, 0, "perfect")
    out: dict = {}
    for e, r in _index().get(kk, []):
        if e == seed.lower():
            continue
        if bridge.rhyme_score(seed, e) >= min_score:
            out.setdefault(r["group"], []).append(r)
    return out


def search(group: Optional[str] = None, q: str = "", limit: int = 60) -> list[dict]:
    q = q.lower()
    rows = [r for r in load() if not r.get("avoid") and (not group or r["group"] == group) and (not q or q in r["text"].lower() or q in r.get("gloss", "").lower() or q in r.get("kind", "").lower() or q in r.get("extra", "").lower())]
    return rows[:limit]


def counts() -> dict:
    c: dict = {}
    for r in load():
        c[r["group"]] = c.get(r["group"], 0) + 1
    return c


def selftest() -> tuple[bool, str]:
    problems = []
    if KEY2GROUP.get("alcohol") != "brand" or KEY2GROUP.get("roles") != "role":
        problems.append("group map wrong")
    if tokens("Wetherspoons' B&Q") != ["wetherspoons", "b", "q"]:
        problems.append(f"tokens: {tokens('Wetherspoons B&Q')}")
    if end_token({"group": "idiom", "text": "off the back of a lorry", "extra": "literal: a lorry | payoff: lorry"}) != "lorry":
        problems.append("idiom end token should be the payoff word")
    return (not problems, "; ".join(problems) if problems else f"lexicon module ok ({sum(counts().values())} rows banked)")
