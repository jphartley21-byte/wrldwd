"""Pop-culture graph + kit + join-yield probe.

THE IDEA (13 Oct 2026, Joe): the deeper the lore, the more connections, the easier the bar. The repo had the BREADTH (6,050 brands, 1,481 TV and
music, 866 pop; ww/lex/lexicon.py) but reached it only by END SOUND (rhymebank), and only through each entity's NAME. This module indexes every
entity by every word that can CARRY it into a bar, so a section can ask "what in the world of pop culture fits my sound family AND my scene":

  tier 0  the name alone                         carrier: the name's last word
  tier 1  + the one-line gloss / kind / country  carriers: gloss words (a hero 'web-slinging', a firm 'haulage')
  tier 2  + the lore card (ww/lex/cards.py)      carriers: parts, aliases, figures, hidden readings, neighbours, rungs

Two edge types make a JOIN with a section:
  SOUND  a carrier IS one of the section's payoff words ('is'), or perfectly rhymes with one ('rhyme', >= 0.9 in British phones)
  SCENE  the entity's vocabulary at that tier shares a content word with the section's argument/beats/facts (never the payoff word itself)
JOIN = SOUND and SCENE. The probe counts joins per tier on the SAME entities, so any rise is depth, not volume.

EFFICIENCY: nothing here goes into a prompt wholesale. kit() returns <= ~24 ranked entities (~1,500 tokens) for ONE section; the LLM only dresses
what the kit lists. Built once per process (about two seconds); lore cards are compiled lazily and cached (cards.py).
STATUS: kit ranking and the probe are DIAGNOSTIC (unvalidated as a quality signal; ww/registry.py). They count connections; they do not judge them.
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from .. import bridge
from . import cards as C
from . import lexicon

POP_GROUPS = ("brand", "media", "pop")
# categories a rap lyricist actually name-drops; the pilot samples these so it is not 6,000 supermarket own-brands
RAP_CATS = ("restaurants", "vehicles", "vice", "techfinance", "clothing", "alcohol", "highstreet", "travelbrands", "supermarkets", "snacks",
            "softdrinks", "tv", "music", "pop", "watches", "actors")
DF_MAX = 25      # a scene word shared with more than this many of ~7,800 entities (new, word, top, red ...) is noise, not a scene link
GENERIC = set("new word top flat city week day time way thing people show world good best big little old first last long high low next part".split())
EDGE_W = {"name": 3.0, "part": 2.5, "alias": 2.5, "figure": 2.5, "hidden": 2.5, "rung": 2.0, "neighbour": 1.2, "fact": 1.2, "gloss": 1.0}


def _rt():
    bridge._toolkit_on_path()
    import rhyme_tools as rt
    return rt


@lru_cache(maxsize=None)
def _key(word: str):
    rt = _rt()
    try:
        ph = rt.pron(word)
        return rt.key(ph, 0, "perfect") if ph else None
    except Exception:    # noqa: BLE001 - an unpronounceable carrier is simply not a carrier
        return None


@lru_cache(maxsize=None)
def _rhymes(a: str, b: str) -> float:
    try:
        return bridge.rhyme_score(a, b)
    except Exception:    # noqa: BLE001
        return 0.0


@lru_cache(maxsize=None)
def audience(text: str) -> float:
    """recognisability PROXY in 0..1 (wordfreq zipf; US-weighted, so it under-rates real British names; it ranks, it never vetoes)."""
    try:
        from wordfreq import zipf_frequency
        z = zipf_frequency(text.lower(), "en")
    except Exception:    # noqa: BLE001
        z = 0.0
    return round(max(0.05, min(1.0, (z - 2.0) / 3.0)), 2) if z > 0 else 0.15


def _last(t: str) -> Optional[str]:
    w = C.words(t)
    return w[-1] if w else None


class Graph:
    def __init__(self):
        self.ents: list[dict] = []
        seen: dict[str, int] = {}
        for r in lexicon.load():
            if r["group"] not in POP_GROUPS or r.get("avoid") or not r["text"].strip() or len(r["text"]) > 40:
                continue
            k = C.norm(r["text"])
            if k in seen:
                prev = self.ents[seen[k]]
                if not prev["gloss"] and r.get("gloss"):
                    prev.update(gloss=r["gloss"], kind=r.get("kind", "") or prev["kind"])
                continue
            seen[k] = len(self.ents)
            self.ents.append({"i": len(self.ents), "text": r["text"].strip(), "key": k, "group": r["group"], "cat": r["cat"], "kind": r.get("kind", ""),
                              "gloss": r.get("gloss", ""), "extra": r.get("extra", ""), "country": r.get("country", "")})
        self.by_key = {e["key"]: e["i"] for e in self.ents}
        self.cards = C.load()
        self.df: dict = {}
        self.vocab: list[tuple[set, set, set]] = []
        self.carriers: list[list[tuple[str, str, int]]] = []
        self.index: dict = {}
        for e in self.ents:
            card = self.cards.get(e["key"])
            v0 = C.content_stems(e["text"]) | {C.stem(e["cat"])}
            v1 = v0 | C.content_stems(" ".join((e["gloss"], e["kind"], e["extra"], e["country"])))
            v2 = set(v1)
            cs: list[tuple[str, str, int]] = []
            nm = lexicon.end_token({"group": e["group"], "text": e["text"], "extra": ""})
            if nm:
                cs.append((nm, "name", 0))
            for w in C.words(e["gloss"]):
                if w not in C.STOP and len(w) > 3 and "'" not in w:
                    cs.append((w, "gloss", 1))
            if card:
                for p in card.get("parts") or []:
                    v2 |= C.content_stems(p)
                    w = _last(p)
                    cs.append((w, "part", 2)) if w else None
                for a in card.get("aliases") or []:
                    v2 |= C.content_stems(a)
                    w = _last(a)
                    cs.append((w, "alias", 2)) if w else None
                for f in card.get("figures") or []:
                    v2 |= C.content_stems(f["phrase"] + " " + f.get("reading", ""))
                    w = _last(f["phrase"])
                    cs.append((w, "figure", 2)) if w else None
                for h in card.get("hidden") or []:
                    v2 |= C.content_stems(h)
                    w = _last(h)
                    cs.append((w, "hidden", 2)) if w else None
                for n in card.get("neighbours") or []:
                    v2 |= C.content_stems(n)
                    w = _last(n)
                    cs.append((w, "neighbour", 2)) if w else None
                for f in card.get("famous_for") or []:
                    v2 |= C.content_stems(f)
                    w = _last(f)
                    cs.append((w, "fact", 2)) if w else None
                for rung in (card.get("ladder") or {}).get("rungs") or []:
                    w = _last(rung)
                    cs.append((w, "rung", 2)) if w else None
                v2 |= C.content_stems(card.get("register", "") + " " + (card.get("ladder") or {}).get("name", ""))
            cs = [(w, k, t) for w, k, t in cs if w and len(w) >= 3 and w not in C.STOP]
            self.vocab.append((v0, v1, v2))
            for st in v2:
                self.df[st] = self.df.get(st, 0) + 1
            self.carriers.append(cs)
            for w, k, t in cs:
                kk = _key(w)
                if kk:
                    self.index.setdefault(kk, []).append((e["i"], w, k, t))

    # -------------------------------------------------------------- queries
    def reach(self, targets: list[str], tier: int, only: Optional[set] = None, min_rhyme: float = 0.9) -> dict[int, list[dict]]:
        """{entity: [edge]} for entities with a SOUND edge to any target at <= tier."""
        out: dict[int, list[dict]] = {}
        for t in targets:
            kt = _key(t)
            if not kt:
                continue
            for i, w, kind, ct in self.index.get(kt, []):
                if ct > tier or (only is not None and i not in only):
                    continue
                if w == t:
                    typ = "is"
                elif _rhymes(w, t) >= min_rhyme:
                    typ = "rhyme"
                else:
                    continue
                out.setdefault(i, []).append({"type": typ, "word": w, "kind": kind, "target": t, "tier": ct})
        return out

    def scene_overlap(self, i: int, tier: int, scene: set, targets: list[str]) -> set:
        banned = {C.stem(t) for t in targets}
        return {w for w in (self.vocab[i][tier] & scene) - banned if len(w) >= 4 and w not in GENERIC and self.df.get(w, 0) <= DF_MAX}

    def joins(self, targets: list[str], scene: set, tier: int, only: Optional[set] = None) -> tuple[dict, dict]:
        r = self.reach(targets, tier, only)
        j = {i: ed for i, ed in r.items() if self.scene_overlap(i, tier, scene, targets)}
        return r, j


@lru_cache(maxsize=1)
def _graph_cached(stamp):
    return Graph()


def graph() -> Graph:
    return _graph_cached((C._stamp(), lexicon.BANK.stat().st_mtime_ns))


# ------------------------------------------------------------------ the section's side

def section(slot: str) -> dict:
    """targets (the plan's payoff words) and scene vocabulary (argument + beats + facts + closer) for a planned slot."""
    from ..write import argue_stage as A
    b = A.brief(slot)
    text = " ".join([b["argument"], b["closer"], " ".join(b["facts"])] + [f"{r['job']} {r['content']}" for r in b["beats"]])
    return {"slot": slot, "targets": [w.lower() for w in b["payoffs"]], "scene": C.content_stems(text), "scene_text": text, "argument": b["argument"]}


# ------------------------------------------------------------------ ranking and the kit

def _edges_score(edges: list[dict]) -> float:
    if not edges:
        return 0.0
    ws = sorted((EDGE_W.get(e["kind"], 1.0) * (1.15 if e["type"] == "is" else 1.0) + (1.0 if e["type"] == "is" else 0.0) for e in edges), reverse=True)
    return ws[0] + 0.3 * min(2, len(ws) - 1)


def kit(slot: str, n: int = 24, tier: int = 2, per_cat: int = 4) -> list[dict]:
    g = graph()
    s = section(slot)
    r, j = g.joins(s["targets"], s["scene"], tier)
    rows = []
    for i, ed in j.items():
        e = g.ents[i]
        ov = sorted(g.scene_overlap(i, tier, s["scene"], s["targets"]))
        card = g.cards.get(e["key"])
        score = _edges_score(ed) + 0.8 * min(3, len(ov)) + 1.0 * audience(e["text"]) + (0.3 if card else 0.0) + (0.5 if e["group"] == "hidden" else 0.0)
        rows.append({"entity": e["text"], "cat": e["cat"], "score": round(score, 2), "edges": ed, "scene": ov, "card": bool(card), "i": i})
    rows.sort(key=lambda x: -x["score"])
    out, used = [], {}
    for x in rows:                       # diversity: no category fills the kit (a kit of 24 Vauxhall models helps nobody)
        if used.get(x["cat"], 0) >= per_cat:
            continue
        used[x["cat"]] = used.get(x["cat"], 0) + 1
        out.append(x)
        if len(out) >= n:
            break
    return out


def hooks(e: dict, g: Graph) -> str:
    card = g.cards.get(e["key"])
    if not card:
        return e["gloss"][:70]
    bits = []
    if card.get("parts"):
        bits.append("parts " + "/".join(card["parts"][:6]))
    if card.get("figures"):
        bits.append("figs " + "; ".join(f"{f['phrase']}" + (f"={f['reading']}" if f.get("reading") else "") for f in card["figures"][:2]))
    if card.get("aliases"):
        bits.append("aka " + "/".join(card["aliases"][:3]))
    if card.get("famous_for"):
        bits.append("known for " + "; ".join(card["famous_for"][:2]))
    return " | ".join(bits)


def format_kit(slot: str, rows: list[dict]) -> str:
    g = graph()
    s = section(slot)
    L = [f"POP-CULTURE KIT for {slot}: names ranked by how many connections they have to THIS section's sound ({', '.join(s['targets'])}) and scene. "
         "Hooks are model-compiled associations, not verified facts: use them for sound, double meaning and character, never as a claim about a real person. "
         "An item that is a person is never the target of violence or a crime. Use at most two items; a name that does no work is texture, not the joke."]
    for x in rows:
        e = g.ents[x["i"]]
        ed = x["edges"][0]
        why = (f"IS payoff '{ed['word']}'" if ed["type"] == "is" else f"{ed['kind']} '{ed['word']}' rhymes '{ed['target']}'")
        card = g.cards.get(e["key"])
        flag = " [real person]" if card and card.get("living_person") else ""
        L.append(f"- {e['text']} [{e['cat']}]{flag}: {why}; scene {','.join(x['scene'][:3])}" + (f" | {hooks(e, g)}" if hooks(e, g) else ""))
    return "\n".join(L)


def candidates_to_card(slot: str, n: int = 30) -> list[dict]:
    """the uncarded entities most worth a card for THIS section: sound-reached at tier <= 1 (a name or gloss word already rhymes with, or is,
    a payoff), best-known first. Depth is bought only where a section can use it."""
    g = graph()
    s = section(slot)
    r = g.reach(s["targets"], 1)
    rows = [(audience(g.ents[i]["text"]) + 0.2 * _edges_score(ed), i) for i, ed in r.items() if g.ents[i]["key"] not in g.cards]
    rows.sort(reverse=True)
    return [{"name": g.ents[i]["text"], "cat": g.ents[i]["cat"], "gloss": g.ents[i]["gloss"]} for _, i in rows[:n]]


def ensure_cards(slot: str, llm, n: int = 30, model: str = "ds-flash") -> dict:
    """LAZY depth: compile cards for the section's best uncarded candidates (about $0.005 for 30), cached forever. Returns the compile summary."""
    items = candidates_to_card(slot, n)
    if not items:
        return {"built": 0, "skipped": 0, "usd": 0.0, "missing": []}
    return C.compile_cards(llm, items, model=model)


def kit_text(slot: str, n: int = 24) -> str:
    rows = kit(slot, n)
    return format_kit(slot, rows) if rows else ""


# ------------------------------------------------------------------ the join-yield probe

def pilot_set(per_cat: int = 20) -> list[int]:
    """the same entities at every tier: the best-known per rap category (audience proxy). Unbiased with respect to any slot."""
    g = graph()
    by: dict[str, list] = {}
    for e in g.ents:
        if e["cat"] not in RAP_CATS or e["group"] not in POP_GROUPS:
            continue
        if len(C.words(e["text"])) > 3 or any(ch.isdigit() for ch in e["text"]):
            continue
        by.setdefault(e["cat"], []).append((audience(e["text"]), e["i"]))
    out = []
    for cat, xs in by.items():
        xs.sort(key=lambda t: (-t[0], len(g.ents[t[1]]["text"])))
        out += [i for _, i in xs[:per_cat]]
    return out


def probe(only: Optional[set] = None, slots: Optional[list] = None) -> dict:
    from ..write import argue_stage as A
    g = graph()
    res = {}
    for slot in slots or A.slots():
        s = section(slot)
        row = {}
        for t in (0, 1, 2):
            r, j = g.joins(s["targets"], s["scene"], t, only)
            row[t] = {"reach": len(r), "joins": len(j), "ids": sorted(j)}
        res[slot] = row
    return res


def format_probe(res: dict, only: Optional[set], examples: int = 8) -> str:
    g = graph()
    n = len(only) if only is not None else len(g.ents)
    carded = sum(1 for i in (only if only is not None else range(len(g.ents))) if g.ents[i]["key"] in g.cards)
    L = [f"JOIN-YIELD PROBE over {n} entities ({carded} carded). reach = entities with a SOUND edge to the section's payoff family; joins = sound AND scene.",
         f"{'slot':10} | tier0 reach/join | tier1 reach/join | tier2 reach/join"]
    tot = {0: [0, 0], 1: [0, 0], 2: [0, 0]}
    for slot, row in res.items():
        L.append(f"{slot:10} | " + " | ".join(f"{row[t]['reach']:6}/{row[t]['joins']:<8}" for t in (0, 1, 2)))
        for t in tot:
            tot[t][0] += row[t]["reach"]
            tot[t][1] += row[t]["joins"]
    L.append(f"{'TOTAL':10} | " + " | ".join(f"{tot[t][0]:6}/{tot[t][1]:<8}" for t in (0, 1, 2)))
    new = []
    for slot, row in res.items():
        s = section(slot)
        gained = set(row[2]["ids"]) - set(row[1]["ids"])
        for i in sorted(gained):
            r = g.reach(s["targets"], 2, {i}).get(i, [])
            ov = sorted(g.scene_overlap(i, 2, s["scene"], s["targets"]))
            ed = r[0] if r else {}
            new.append(f"  {slot}: {g.ents[i]['text']} [{g.ents[i]['cat']}] via {ed.get('kind')} '{ed.get('word')}' ~ '{ed.get('target')}' ({ed.get('type')}); scene {','.join(ov[:3])}")
    if new:
        L.append(f"JOINS THAT EXIST ONLY BECAUSE OF THE CARD ({len(new)}; READ THEM, a count is not a verdict):")
        L += new[:examples * 3]
    return "\n".join(L)


def selftest() -> tuple[bool, str]:
    problems = []
    g = Graph()
    if len(g.ents) < 5000:
        problems.append(f"only {len(g.ents)} entities loaded")
    t0 = g.reach(["lorry"], 0)
    if not t0:
        problems.append("tier-0 reach for 'lorry' is empty (no name rhymes with lorry?)")
    # carrier mechanics on a synthetic card, in-memory
    fake = {"key": "watchco", "name": "WatchCo", "cat": "watches", "parts": ["face", "hands", "crown"], "aliases": [], "figures": [], "hidden": [],
            "famous_for": [], "neighbours": [], "ladder": {}, "register": "", "living_person": False}
    old = dict(C._CACHE)
    g2 = Graph.__new__(Graph)
    try:
        g2.ents = [{"i": 0, "text": "WatchCo", "key": "watchco", "group": "brand", "cat": "watches", "kind": "", "gloss": "", "extra": "", "country": ""}]
        g2.cards = {"watchco": fake}
        g2.carriers = [[("watchco", "name", 0), ("crown", "part", 2)]]
        g2.vocab = [({"watchco", "watch"}, {"watchco", "watch"}, {"watchco", "watch", "crown", "face", "hand"})]
        g2.index = {}
        g2.df = {}
        for w, k, t in g2.carriers[0]:
            kk = _key(w)
            if kk:
                g2.index.setdefault(kk, []).append((0, w, k, t))
        if g2.reach(["crown"], 1):
            problems.append("a tier-2 carrier must not count at tier 1")
        r2 = g2.reach(["crown"], 2)
        if not r2 or r2[0][0]["type"] != "is":
            problems.append(f"a part equal to the payoff word should be an 'is' edge: {r2}")
        if g2.joins(["crown"], {"head", "crown"}, 2)[1]:
            problems.append("the payoff word must not count as the scene overlap")
        if not g2.joins(["crown"], {"head", "face"}, 2)[1]:
            problems.append("part 'crown' + scene 'face' should be a join at tier 2")
    finally:
        C._CACHE.clear()
        C._CACHE.update(old)
    return (not problems, "; ".join(problems) if problems else f"{len(g.ents)} entities indexed; carrier tiers, is/rhyme edges, payoff-not-scene rule")
