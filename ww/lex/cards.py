"""Lore cards: what an entity (a brand, a watch, a car, an actor, a film, an app, a restaurant) is KNOWN FOR, as typed association edges.

The lexicon holds ~17,000 names, mostly bare. A bare name gives the writer one sound and nothing to say. A card gives it the things that make
wordplay and rhyme possible (see the Potter/Voldemort analysis, 13 Oct 2026):

  aliases     short forms, nicknames, model names, the surname chunk          (Submariner -> Sub; Lambert and Butler -> L&B)
  parts       concrete words the thing is made of or does                       (watch: face, hands, crown, strap)
  figures     stock phrases from the thing's domain + their figurative reading  (up in smoke = ruined)
  hidden      other words/phrases the name sounds like in a British accent
  famous_for  up to 4 facts a listener already knows (signature product, event, catchphrase)
  neighbours  rivals, owner, same-tier, the film/show it is tied to
  ladder      a status/price/size ladder the thing sits on
  living_person   True for a living real person: never the target of violence or crime claims

COST MODEL: depth is compiled LAZILY. Breadth (names) is free; a card is built the first time an entity is retrieved into a kit, cached for
good in ww/lex/banks/cards.jsonl, and costs ~0.1 cent. Cost scales with use, not with the size of the catalogue.

PROVENANCE (CLAUDE.md rule 5, true or flagged): every field of a model-compiled card is UNVERIFIED association, stored with src and
verified=False. A card is a prompt for the writer, never a claim about a real person. Joe promotes a card with `ww card NAME --verify`.

STATUS (ww/registry.py): check_allusion / detect are STRUCTURAL checks (does the text contain the card's triggers?) not quality measures; they
are unvalidated as a quality signal and are used only to reject a seed that CLAIMS the lore_allusion mechanism without having it.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Optional

BANK = Path(__file__).resolve().parent / "banks" / "cards.jsonl"

STOP = set("""a an the of to in on at for with as is it its and or but so no do go my me we he she you your i us up out off if than that this them they
then there here are was were has have had not can will would be by from into over just very more most some any all one two get got""".split())
SWEAR = {"fuck", "fucking", "fucker", "motherfucker", "cunt", "nigger", "nigga", "faggot", "paki", "retard", "retarded"}
_W = re.compile(r"[a-z0-9&']+")

CARD_SCHEMA = {
    "type": "object", "required": ["cards"],
    "properties": {"cards": {"type": "array", "items": {
        "type": "object", "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "aliases": {"type": "array", "items": {"type": "string"}},
            "parts": {"type": "array", "items": {"type": "string"}},
            "figures": {"type": "array", "items": {"type": "object", "properties": {"phrase": {"type": "string"}, "reading": {"type": "string"}}}},
            "hidden": {"type": "array", "items": {"type": "string"}},
            "famous_for": {"type": "array", "items": {"type": "string"}},
            "neighbours": {"type": "array", "items": {"type": "string"}},
            "ladder": {"type": "object", "properties": {"name": {"type": "string"}, "rungs": {"type": "array", "items": {"type": "string"}}}},
            "register": {"type": "string"},
            "living_person": {"type": "boolean"}}}}},
}

SYSTEM = """You compile LORE CARDS for a British rap lyricist: for each named thing, the associations a listener already carries, as SHORT tokens the writer can build wordplay and rhymes from. Audience: British men in their thirties; the register is deadpan everyday-British.

For every name give (omit any field you are not sure of; NEVER invent; fewer true items beat many doubtful ones):
- aliases: short forms, nicknames, model names, the surname chunk (<=5)
- parts: concrete words for what the thing is made of, has or does (a watch: face, hands, crown, strap, bezel; a cigarette: filter, tip, ash, drag) (<=10; single words preferred)
- figures: REAL stock phrases or idioms people already say that belong to the thing's domain, with the figurative reading (up in smoke = ruined; on the clock = at work). Never coin a phrase. (<=6)
- famous_for: up to 4 short facts a listener already knows: signature product, event, catchphrase, scandal (only if you are confident they are true)
- neighbours: rivals, owner, same price tier, the film or show it is tied to (<=5)
- ladder: a status / price / size / heat ladder the thing sits on, with its rungs low to high (only if a real one exists)
- register: one phrase, who uses it in the UK (e.g. 'road', 'dad', 'footballer', 'student')
- living_person: true if the name is a living real person
Plain words only. No slurs, no heavy swearing. Return JSON {"cards":[...]} with one card per requested name, name copied exactly."""


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9&' ]+", " ", (t or "").lower().replace("’", "'"))).strip()


def words(t: str) -> list[str]:
    return [w.strip("'") for w in _W.findall((t or "").lower().replace("’", "'")) if w.strip("'")]


def stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s", "ly"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def content_stems(t: str) -> set[str]:
    return {stem(w) for w in words(t) if w not in STOP and len(w) > 2}


# ------------------------------------------------------------------ store

_CACHE: dict = {}


def load(force: bool = False) -> dict[str, dict]:
    """{norm(name): card}"""
    if "cards" in _CACHE and _CACHE.get("stamp") == _stamp() and not force:
        return _CACHE["cards"]
    cards: dict[str, dict] = {}
    if BANK.exists():
        for l in BANK.read_text(encoding="utf-8").splitlines():
            if l.strip():
                c = json.loads(l)
                cards[c["key"]] = c
    _CACHE.update({"stamp": _stamp(), "cards": cards})
    return cards


def _stamp():
    return (BANK.stat().st_mtime_ns, BANK.stat().st_size) if BANK.exists() else None


def save(cards: dict[str, dict]) -> None:
    BANK.parent.mkdir(parents=True, exist_ok=True)
    BANK.write_text("\n".join(json.dumps(c, ensure_ascii=False, sort_keys=True) for c in cards.values()) + "\n", encoding="utf-8", newline="\n")
    _CACHE.clear()


def get(name: str) -> Optional[dict]:
    return load().get(norm(name))


def pending(names: list[str]) -> list[str]:
    have = load()
    return [n for n in names if norm(n) not in have]


# ------------------------------------------------------------------ compile (LLM, lazy, cached)

def _clean_list(xs, cap: int, maxlen: int = 40) -> list[str]:
    out, seen = [], set()
    for x in xs or []:
        s = re.sub(r"\s+", " ", str(x)).strip()
        k = s.lower()
        if not s or len(s) > maxlen or k in seen or any(w in SWEAR for w in words(s)):
            continue
        seen.add(k)
        out.append(s)
        if len(out) >= cap:
            break
    return out


def clean_card(raw: dict, name: str, cat: str, model: str) -> dict:
    figs = []
    for f in raw.get("figures") or []:
        if isinstance(f, dict) and (f.get("phrase") or "").strip():
            p = _clean_list([f["phrase"]], 1, 50)
            if p:
                figs.append({"phrase": p[0], "reading": re.sub(r"\s+", " ", str(f.get("reading") or "")).strip()[:60]})
    lad = raw.get("ladder") or {}
    rungs = _clean_list(lad.get("rungs"), 8)
    return {"key": norm(name), "name": name, "cat": cat,
            "aliases": _clean_list(raw.get("aliases"), 5), "parts": _clean_list(raw.get("parts"), 10),
            "figures": figs[:6], "hidden": _clean_list(raw.get("hidden"), 3), "famous_for": _clean_list(raw.get("famous_for"), 4, 70),
            "neighbours": _clean_list(raw.get("neighbours"), 5), "ladder": {"name": str(lad.get("name") or "")[:30], "rungs": rungs} if len(rungs) >= 2 else {},
            "register": str(raw.get("register") or "")[:40], "living_person": bool(raw.get("living_person")),
            "src": f"llm:{model}", "verified": False, "built": time.strftime("%Y-%m-%d")}


def derive_hidden(name: str, n: int = 3) -> list[str]:
    """sound-alike readings of the NAME from the pronouncing dictionary (ww/write/oronym.py), not from the model: a model asked for sound-alikes
    returned non-words ('Rizzler' for Rizla). Code can hear; the model cannot."""
    try:
        from ..write import oronym
        return [r["reading"] for r in oronym.segmentations(name, n=n * 3)][:n]
    except Exception:    # noqa: BLE001 - optional enrichment
        return []


def compile_cards(llm, items: list[dict], model: str = "ds-flash", batch: int = 8, workers: int = 4) -> dict:
    """items = [{name, cat, gloss}]. Skips names that already have a card. Returns {built, skipped, usd, missing}."""
    from concurrent.futures import ThreadPoolExecutor
    from ..llm import Request
    todo = [i for i in items if norm(i["name"]) not in load()]
    batches = [todo[k:k + batch] for k in range(0, len(todo), batch)]

    def one(b):
        listing = "\n".join(f"- {i['name']} [{i.get('cat', '')}]" + (f": {i['gloss']}" if i.get("gloss") else "") for i in b)
        req = Request(model=model, system=SYSTEM, messages=[{"role": "user", "content": f"Compile cards for these {len(b)} names:\n{listing}"}],
                      schema=CARD_SCHEMA, max_tokens=900 * len(b) // 2 + 600, effort=None, temperature=0.3, stage="lore_cards", scope="write")
        res = llm.complete(req, use_cache=False)
        return b, res

    built, missing, usd = {}, [], 0.0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for b, res in ex.map(one, batches):
            usd += res.usd
            by = {norm(c.get("name", "")): c for c in ((res.parsed or {}).get("cards") or [])}
            for i in b:
                raw = by.get(norm(i["name"]))
                if raw is None:
                    missing.append(i["name"])
                    continue
                card = clean_card(raw, i["name"], i.get("cat", ""), model)
                card["hidden"] = derive_hidden(i["name"])
                built[norm(i["name"])] = card
            if built:     # persist after every batch: a dropped connection must not lose the cards already paid for
                cards = load(force=True)
                cards.update(built)
                save(cards)
    return {"built": len(built), "skipped": len(items) - len(todo), "usd": usd, "missing": missing}


def roster(llm, label: str, n: int = 80, model: str = "ds-flash") -> list[dict]:
    """names only: well-known examples of a category the lexicon lacks (watches, actors). Low-risk breadth; depth comes from cards."""
    from ..llm import Request
    schema = {"type": "object", "required": ["rows"], "properties": {"rows": {"type": "array", "items": {
        "type": "object", "required": ["text"], "properties": {"text": {"type": "string"}, "gloss": {"type": "string"}}}}}}
    req = Request(model=model, system="You list well-known things for a British lyricist. Only real, famous items a British man in his thirties would instantly recognise. "
                  "text = the name as people say it; gloss = at most 8 words saying what it is. No duplicates, no invented items.",
                  messages=[{"role": "user", "content": f"List {n} {label}, most famous first."}], schema=schema, max_tokens=4000, effort=None,
                  temperature=0.3, stage="lore_roster", scope="write")
    res = llm.complete(req, use_cache=False)
    return [{"text": r["text"].strip(), "gloss": (r.get("gloss") or "").strip()} for r in (res.parsed or {}).get("rows") or [] if (r.get("text") or "").strip()]


# ------------------------------------------------------------------ triggers: what in a text points at a card

def triggers(card: dict) -> dict[str, set[str]]:
    """{kind: {phrase}} of everything in the card a text can hit. 'name' = the entity's own name; 'alias' = shorter forms."""
    t: dict[str, set[str]] = {"name": {card["key"]}, "alias": set(), "part": set(), "figure": set(), "hidden": set(), "fact": set(), "neighbour": set(), "rung": set()}
    for a in card.get("aliases") or []:
        t["alias"].add(norm(a))
    for p in card.get("parts") or []:
        t["part"].add(norm(p))
    for f in card.get("figures") or []:
        t["figure"].add(norm(f["phrase"]))
    for h in card.get("hidden") or []:
        t["hidden"].add(norm(h))
    for f in card.get("famous_for") or []:
        t["fact"].update(w for w in words(f) if w not in STOP and len(w) > 3)
    for n in card.get("neighbours") or []:
        t["neighbour"].add(norm(n))
    for r in (card.get("ladder") or {}).get("rungs") or []:
        t["rung"].add(norm(r))
    return {k: {x for x in v if x} for k, v in t.items()}


def _present(trig: str, text_norm: str, text_stems: set[str]) -> bool:
    if " " in trig:
        return f" {trig} " in f" {text_norm} "
    return trig in text_norm.split() or stem(trig) in text_stems


def hits(card: dict, text: str) -> list[tuple[str, str]]:
    """[(kind, trigger)] present in text, each trigger once. Generic one-letter/stop triggers never count."""
    tn = norm(text)
    ts = {stem(w) for w in tn.split()}
    out = []
    for kind, ts_ in triggers(card).items():
        for t in sorted(ts_):
            if t in STOP or len(t) < 3:
                continue
            if _present(t, tn, ts):
                out.append((kind, t))
    return out


def check_allusion(entity: str, text: str, bars: Optional[list[str]] = None) -> dict:
    """Is the lore_allusion claim real? STRUCTURAL, not a quality score. The hidden node is the ENTITY; the text must reach it through >=2
    distinct triggers from its card WITHOUT naming it outright (a name-drop is texture, not wordplay; rule 5).
    ok iff card exists, the full name is absent, and >=2 distinct non-name triggers are present. in_rhyme_slot is reported, not required."""
    card = get(entity)
    if card is None:
        return {"ok": False, "reasons": [f"no lore card for '{entity}' (build it: ww card \"{entity}\")"], "hits": [], "in_rhyme_slot": False}
    h = [x for x in hits(card, text) if x[0] != "name"]
    named = any(x[0] == "name" for x in hits(card, text))
    reasons = []
    if named:
        reasons.append(f"names '{card['name']}' outright; the hidden node must stay unstated")
    if len({t for _, t in h}) < 2:
        reasons.append(f"only {len({t for _, t in h})} distinct trigger(s) from the card ({', '.join(t for _, t in h) or 'none'}); need >= 2")
    slot = False
    last = {norm(b).split()[-1] for b in (bars or []) if norm(b)}
    if bars:
        slot = any(t.split()[-1] in last for _, t in h)
    return {"ok": not reasons, "reasons": reasons, "hits": h, "in_rhyme_slot": slot}


def detect(text: str, min_hits: int = 2) -> list[dict]:
    """which compiled cards does a text converge on? Diagnostic: entities hit by >= min_hits distinct non-name triggers (or the name plus one)."""
    out = []
    tn = norm(text)
    ts = {stem(w) for w in tn.split()}
    for card in load().values():
        h = hits(card, text)
        distinct = {t for _, t in h}
        named = any(k == "name" for k, _ in h)
        if len(distinct) >= min_hits and (len(distinct) - (1 if named else 0)) >= 1:
            out.append({"entity": card["name"], "named": named, "hits": h})
    return sorted(out, key=lambda r: -len(r["hits"]))


def selftest() -> tuple[bool, str]:
    problems = []
    if norm("Nando's  Peri-Peri") != "nando's peri peri":
        problems.append(f"norm: {norm('Nando’s  Peri-Peri')}")
    if stem("lighting") != "light" or stem("smoke") != "smoke":
        problems.append("stem")
    c = clean_card({"aliases": ["Sub", "fuck", "Sub"], "parts": ["face", "hands", "crown", "x" * 60], "figures": [{"phrase": "on the clock", "reading": "at work"}],
                    "famous_for": ["worn by a fictional spy"], "neighbours": ["Omega"], "ladder": {"name": "tier", "rungs": ["Casio", "Seiko", "Rolex"]}}, "Submariner", "watches", "stub")
    if c["aliases"] != ["Sub"] or "x" * 60 in c["parts"] or not c["ladder"]:
        problems.append(f"clean_card: {c}")
    # an in-memory card: two triggers without the name pass; the name-drop and the single trigger fail
    old = dict(_CACHE)
    _CACHE.update({"stamp": _stamp(), "cards": {"submariner": c}})
    try:
        ok = check_allusion("Submariner", "Left a mark on his face, hands up, clock stopped")
        if not ok["ok"]:
            problems.append(f"two-trigger text should pass: {ok}")
        nd = check_allusion("Submariner", "Wore a Submariner in the car")
        if nd["ok"]:
            problems.append("a bare name-drop must fail")
        one = check_allusion("Submariner", "a mark on his face")
        if one["ok"]:
            problems.append("a single trigger must fail")
        named = check_allusion("Submariner", "face and hands on a Submariner")
        if named["ok"]:
            problems.append("naming the hidden node outright must fail")
        slot = check_allusion("Submariner", "Left a mark on his face\nPut his hands up", bars=["Left a mark on his face", "Put his hands up"])
        if not slot["in_rhyme_slot"]:
            problems.append("a trigger ending a bar should report in_rhyme_slot")
        if not any(d["entity"] == "Submariner" for d in detect("face and hands and the crown")):
            problems.append("detect should find the card from three parts")
    finally:
        _CACHE.clear()
        _CACHE.update(old)
    return (not problems, "; ".join(problems) if problems else "norm/stem, card cleaning, 2-trigger rule, name-drop and single-trigger rejection, rhyme-slot report, detect")
