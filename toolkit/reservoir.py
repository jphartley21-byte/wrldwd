"""Rhyme reservoir (14 Oct 2026): the same end-word pool the carpet tool builds, ranked by how LOADED a word
is instead of how common.

WHY. benchmark/carpets_*.json is sorted commonest-first (carpet.py: allowed_words keeps the 150 most common
words, build_sets keeps the top 40 per bar), and ww/write/versebank._menu hands the writer the first 30 of
them. For V2 1-8 (the uːz carpet) that menu starts "new, two, through, use, used, school, group, news, food"
(zipf 5.6-6.3). The original's hook measures a mean end-word zipf of 4.04 and 7 of 16 end words are places
(benchmark/gap_analysis.md gap 4). Eminem keeps rhyme lists collected ahead of any song; this is the
repo's equivalent, built from material the repo already holds (places, local words, theme words, entities).

TIERS, best first:
  0  a documented place, a local/foreign word (headword only), a theme word, or a FAMOUS entity (the head of
     entities.txt per type; given names and surnames excluded), inside the loaded window LO <= zipf < HI
  1  any other word in the loaded window (recognisable but not the commonest)
  2  rare words (zipf < LO): check by ear, G2 never vetoes ("skint" scores 2.0 and is real British slang)
  3  common words (zipf >= HI)
Inside tiers 0, 2 and 3: closest to Joe's world first (place, local, theme, entity), then more syllables
(multisyllabic rhyme is selective but wanted), then rarer first. Inside tier 1 (plain words): most recognisable
first, words of 1-3 syllables before longer ones (a bar cannot end on "reintroduced"). Letter strings with no
vowel (dfw) are dropped.

REPORT ONLY. Nothing here is validated against Joe's ear: it changes WHAT THE WRITER IS OFFERED, and the
measured effect is on the offer (mean zipf, share of proper/local words), not on the bars.

  python toolkit/reservoir.py --slot "V2 1-8" [--n 30]      per-bar offers, current menu vs reservoir
  python toolkit/reservoir.py --compare                     one line per slot
  python toolkit/reservoir.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LO, HI = 2.6, 4.6
SLOTS = ["Hook 9-16", "V1 1-8", "V1 9-16", "V1 17-24", "V1 25-32", "V1 33-44", "V2 1-8", "V2 9-16"]


TAG_ORDER = ("place", "local", "theme", "entity")   # closest to Joe's world first
LOADED_TYPES = ("city", "uk-town", "country", "brand", "tv", "band", "film", "game", "meme", "person")
FAMOUS_PER_TYPE = 120          # entities.txt is ordered by Wikidata sitelinks inside a type: the head is the famous end


def tier(word: str, meta: dict, loaded_sets: dict[str, set]) -> tuple[int, str]:
    """(tier, tag). loaded_sets: {'place':..., 'local':..., 'theme':..., 'entity':...} of lower-case words.
    Tier 0 needs the word to sit INSIDE the loaded window: a name that is also the commonest word of its sound
    (revolution, community) is not loaded."""
    z, lw = meta["zipf"], word.lower()
    tag = next((k for k in TAG_ORDER if lw in loaded_sets.get(k, ())), "")
    if tag and LO <= z < HI:
        return 0, tag
    if LO <= z < HI:
        return 1, "plain"
    return (3, "common") if z >= HI else (2, "rare")


def rank(pool: dict[str, dict], loaded_sets: dict[str, set]) -> list[tuple[str, int, str]]:
    rows = []
    for w, meta in pool.items():
        if not re.search(r"[aeiouy]", w.lower()):
            continue                      # dfw, tv...: letters, not words a rapper can say in a bar
        t, tag = tier(w, meta, loaded_sets)
        tr = TAG_ORDER.index(tag) if tag in TAG_ORDER else 9
        if t == 1:                        # plain window words: the most recognisable first, short ones before long
            rows.append((w, t, tag, (tr, meta["syls"] > 3, -meta["zipf"], w)))
        else:
            rows.append((w, t, tag, (tr, -meta["syls"], meta["zipf"], w)))
    rows.sort(key=lambda r: (r[1], r[3]))
    return [(w, t, tag) for w, t, tag, _k in rows]


def offer(ranked: list[tuple[str, int, str]], n: int = 30) -> list[tuple[str, int, str]]:
    """What the writer is actually shown: 30% tier 0, 30% tier 1, the rest common words then rare ones. The split is
    set so the offer's mean zipf lands near the one benchmark there is (the original's hook, 4.04): an all-loaded
    offer lands near 3.2 and today's all-common one near 5.3, and the original uses both ("home", "though",
    "Lagos"). One hook is a guide, not a fit; Joe's ear decides whether the proportions are right."""
    q0 = q1 = -(-n * 3 // 10)
    by = {t: [r for r in ranked if r[1] == t] for t in (0, 1, 2, 3)}
    out = by[0][:q0] + by[1][:q1]
    for t in (3, 2, 1, 0):
        for r in by[t]:
            if len(out) >= n:
                break
            if r not in out:
                out.append(r)
    return out[:n]


def _first_col(path: str) -> set[str]:
    out = set()
    if os.path.exists(path):
        for line in open(path, encoding="utf-8-sig", errors="replace"):
            line = line.strip()
            if line and not line.startswith("#"):
                w = line.split("|")[0].strip().lower()
                if w and " " not in w:
                    out.add(w)
    return out


def _loaded_sets(carpet, bank) -> dict[str, set]:
    """Only the headword of each row counts as 'local' (the glosses are English), and only the famous head of each
    entity type counts as 'entity' (given names and surnames are not loaded: they belong to nobody in this song)."""
    ent: set[str] = set()
    seen: dict[str, int] = {}
    for r in bank.load_entities(carpet.ENTITIES):
        k = r["type"]
        if k in LOADED_TYPES and r.get("measurable") and " " not in r["name"] and seen.get(k, 0) < FAMOUS_PER_TYPE:
            seen[k] = seen.get(k, 0) + 1
            ent.add(r["name"].lower())
    return {
        "place": {p.lower() for p in carpet.material_places()},
        "local": _first_col(carpet.LOCAL) | _first_col(os.path.join(HERE, "loanwords.txt")),
        "theme": {w.lower() for w in carpet._read_words(carpet.THEME)},
        "entity": ent,
    }


def offers(slot: str, n: int = 30) -> dict:
    """per bar: what the writer is offered today (commonest first, from the carpet JSON) vs the reservoir."""
    import bank
    import carpet
    tgt = carpet.slot_target(slot)
    info = carpet.supply()
    places = carpet.material_places()
    sets = _loaded_sets(carpet, bank)
    path = os.path.join(ROOT, "benchmark", "carpets_" + slot.replace(" ", "_").replace("-", "_") + ".json")
    try:
        current = json.load(open(path, encoding="utf-8"))["per_bar"]
    except OSError:
        current = []
    out = []
    for i, t in enumerate(tgt["targets"]):
        pool = carpet.allowed_words(info, t, places, cap=10 ** 9)
        ranked = offer(rank(pool, sets), n)
        cur = [r["word"] for r in (current[i] if i < len(current) else [])][:n]
        out.append({"bar": i + 1, "pool": len(pool), "reservoir": ranked,
                    "current": [(w, info[w]["zipf"]) for w in cur if w in info]})
    return {"slot": slot, "bars": out, "info": info}


def summary(res: dict) -> dict:
    info = res["info"]
    cur = [z for b in res["bars"] for _w, z in b["current"]]
    new = [(w, t, tag) for b in res["bars"] for w, t, tag in b["reservoir"]]
    newz = [info[w]["zipf"] for w, _t, _g in new]
    loaded = sum(1 for _w, t, _g in new if t == 0)
    return {"slot": res["slot"], "pool": statistics.mean(b["pool"] for b in res["bars"]) if res["bars"] else 0,
            "cur_zipf": statistics.mean(cur) if cur else None, "new_zipf": statistics.mean(newz) if newz else None,
            "loaded_share": loaded / len(new) if new else 0.0}


def show(res: dict) -> None:
    info = res["info"]
    for b in res["bars"]:
        print(f"bar {b['bar']} (pool {b['pool']} words)")
        print("   today :", ", ".join(w for w, _z in b["current"][:14]) or "(no carpet file)")
        print("   loaded:", ", ".join(f"{w}[{g}]" if g not in ("plain", "common") else w for w, _t, g in b["reservoir"][:14]))
    s = summary(res)
    print(f"mean zipf offered: today {s['cur_zipf']:.2f} -> reservoir {s['new_zipf']:.2f} "
          f"(the original's hook end words: 4.04); loaded share of the offer {s['loaded_share']:.0%}")


def selftest() -> tuple[bool, str]:
    problems = []
    pool = {"new": {"zipf": 6.2, "syls": 1}, "Zurich": {"zipf": 3.1, "syls": 2}, "cerveza": {"zipf": 2.9, "syls": 3},
            "lager": {"zipf": 3.9, "syls": 2}, "skint": {"zipf": 2.0, "syls": 1}, "tune": {"zipf": 4.4, "syls": 1}}
    sets = {"place": {"zurich"}, "local": {"cerveza", "skint"}, "theme": set(), "entity": set()}
    r = rank(pool, sets)
    order = [w for w, _t, _g in r]
    if order[:2] != ["Zurich", "cerveza"]:
        problems.append(f"a documented place then a local word must lead: {order}")
    if order.index("lager") > order.index("new"):
        problems.append("a loaded-window plain word must outrank the commonest word")
    if order[-1] != "new" or dict((w, t) for w, t, _g in r)["skint"] != 2:
        problems.append(f"rare words sit before the commonest word, which is last: {r}")
    mix = offer(r, 4)
    if len(mix) != 4 or "new" not in [w for w, _t, _g in offer(r, 6)]:
        problems.append(f"the offer must mix tiers and fall back to common words when short: {mix}")
    if tier("revolution", {"zipf": 4.9, "syls": 4}, {"entity": {"revolution"}})[0] != 3:
        problems.append("a famous-name entity that is also the commonest word of its sound is not loaded")
    if dict((w, t) for w, t, _g in r)["skint"] != 2:
        problems.append("a local word below the recognisability floor is not tier 0")
    return (not problems, "; ".join(problems) if problems else
            "loaded multisyllabic words lead, the commonest words trail, rare words are held back")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        ok, msg = selftest()
        print(("RESERVOIR SELFTEST PASSED: " if ok else "RESERVOIR SELFTEST FAILED: ") + msg)
        return 0 if ok else 1
    if a.compare:
        print("slot        pool  today zipf -> reservoir zipf   loaded share of offer")
        for s in SLOTS:
            m = summary(offers(s, a.n))
            cz = f"{m['cur_zipf']:.2f}" if m["cur_zipf"] is not None else " n/a"
            print(f"{s:<10} {m['pool']:>5.0f}   {cz} -> {m['new_zipf']:.2f}                   {m['loaded_share']:.0%}")
        return 0
    if not a.slot:
        ap.error("--slot or --compare required")
    show(offers(a.slot, a.n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
