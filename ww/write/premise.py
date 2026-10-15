"""Premises: the song-level idea the sections argue from (plan step 3, 14 Oct 2026).

A premise is one sentence about the narrator (from brief/persona.md) plus, per section, an ARGUMENT, the MOVES its bars make and the
INGREDIENTS (material/ingredients.md ids) it may use in any order. It replaces the plan's itinerary: argue_stage reads the plan file this
module writes, so the writer gets "argue X with these moves from these ingredients" instead of "bar 3: the last sight; bar 4: the exit".

Premises live in brief/premises.json (committed). Joe did not want to pick one up front, so every premise is built to a full hook and he
chooses by ear (writing/premise_hooks.md).

  python -m ww.write.premise --list
  python -m ww.write.premise --plan ID          writes eval/_plan_premise_ID.json; use it with WW_PLAN=that path
  python -m ww.write.premise --request          prints the model request that proposes NEW premises (for a machine with a key)
  python -m ww.write.premise --selftest
"""
from __future__ import annotations

import json
import sys

from .. import config

PREMISES = config.ROOT / "brief" / "premises.json"


def load() -> list[dict]:
    return json.load(open(PREMISES, encoding="utf-8"))["premises"]


def get(pid: str) -> dict:
    for p in load():
        if p["id"] == pid:
            return p
    raise KeyError(pid)


def _bars_label(slot: str, k: int) -> str:
    from .slotcheck import spec
    s = spec(slot)
    return f"bar {k + 1} ({s['sylls'][k]} syl, {s['shapes'][k]})"


def to_plan(pid: str) -> dict:
    """a plan in the shape argue_stage reads: sections with argument, moves (one per bar, each with its ingredient pool), facts_used
    (the ingredient pool as prompt lines, never in time order) and the premise as the song-level frame."""
    from . import ingredients
    p = get(pid)
    secs = []
    for slot, sec in p["sections"].items():
        recs = ingredients.pool(sec["ingredients"])
        moves = []
        for k, mv in enumerate(sec["moves"]):
            moves.append({"bars": _bars_label(slot, k), "move": mv,
                          "transform": {"brag": "boast", "flex_list": "exaggerate", "threat": "boast", "deflate": "understate",
                                        "callback": "invert", "name_drop": "boast", "hater": "boast"}.get(mv, "none"),
                          "source": "any ingredient below, in any order"})
        secs.append({"slot": slot, "argument": sec["argument"], "mechanisms": ["1 CASHED IDIOM"], "moves": moves,
                     "facts_used": [ingredients.as_prompt([r]) for r in recs], "concepts": [],
                     "callbacks_in": "", "callbacks_out": "", "closer": "the last bar deflates: the smallest word lands on the rhyme",
                     "premise": f"{p['title']}: {p['one_line']}"})
    return {"plan": {"premise": p["id"], "title": p["title"], "one_line": p["one_line"], "sections": secs},
            "critic": {"amendments": []}}


def write_plan(pid: str):
    out = config.EVAL_DIR / f"_plan_premise_{pid}.json"
    config.EVAL_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(to_plan(pid), indent=1, ensure_ascii=False), encoding="utf-8")
    return out


def request(n: int = 3, model: str = "ds-flash"):
    """the request that proposes n NEW premises from the persona bible and the ingredient traits (run on a machine with a key)."""
    from ..llm import Request
    from . import ingredients
    persona = (config.ROOT / "brief" / "persona.md").read_text(encoding="utf-8")
    traits = "\n".join(f"- {t} ({len(ids)} ingredients)" for t, ids in ingredients.traits())
    system = ("You design song-level premises for a deadpan British rap about a narrator's travels. A premise is ONE claim about who the "
              "narrator is (never a trip in order). For each premise give a title, a one-line premise, and for each section an argument "
              "(a claim, present tense) and the ingredient ids it may use. Return JSON only.")
    user = f"PERSONA:\n{persona}\n\nTRAIT FAMILIES:\n{traits}\n\nPropose {n} premises, each built on a different trait family."
    return Request(model=model, system=system, messages=[{"role": "user", "content": user}], max_tokens=3000, effort=None,
                   temperature=0.9, stage="premise", scope="write")


ARCHETYPES = config.ROOT / "ww" / "lex" / "banks" / "rap_archetypes.json"
FIRST_PERSON = ("i ", "i'm", "i've", "my ", "me ", "i'd", "i'll")


def archetypes() -> dict:
    return {a["id"]: a for a in json.load(open(ARCHETYPES, encoding="utf-8"))["archetypes"]}


def selftest() -> tuple[bool, str]:
    """a premise must be a rap premise: it names an archetype from the bank, its premise line and every section argument are
    first-person boasts, its moves are rap moves, and deflate stays at or under one bar in eight (song_bible revision 2)."""
    import math
    problems = []
    from . import ingredients
    from .argue_stage import MOVES, DEFLATE_PER_BARS
    known = {r["id"] for r in ingredients.records()}
    arch = archetypes()
    from .slotcheck import spec
    for p in load():
        if p.get("archetype") not in arch:
            problems.append(f"{p['id']}: archetype {p.get('archetype')!r} is not in the rap archetype bank")
        if not any(f in (" " + p["one_line"].lower() + " ") for f in (" " + x for x in FIRST_PERSON)):
            problems.append(f"{p['id']}: the premise line is not a first-person boast")
        for slot, sec in p["sections"].items():
            n = spec(slot)["n"]
            if len(sec["moves"]) != n:
                problems.append(f"{p['id']} {slot}: {len(sec['moves'])} moves for {n} bars")
            bad = [i for i in sec["ingredients"] if i not in known]
            if bad:
                problems.append(f"{p['id']} {slot}: unknown ingredients {bad}")
            if sec["moves"][-1] not in ("punchline", "title_drop", "threat"):
                problems.append(f"{p['id']} {slot}: the last move should land (punchline)")
            bad_mv = [m for m in sec["moves"] if m not in MOVES]
            if bad_mv:
                problems.append(f"{p['id']} {slot}: not rap moves {bad_mv}")
            if sec["moves"].count("deflate") > math.ceil(n / DEFLATE_PER_BARS):
                problems.append(f"{p['id']} {slot}: {sec['moves'].count('deflate')} deflates in {n} bars (cap: one in {DEFLATE_PER_BARS})")
            if not any(f in (" " + sec["argument"].lower() + " ") for f in (" " + x for x in FIRST_PERSON)):
                problems.append(f"{p['id']} {slot}: the argument is not a first-person boast")
        plan = to_plan(p["id"])
        if not plan["plan"]["sections"] or "moves" not in plan["plan"]["sections"][0]:
            problems.append(f"{p['id']}: plan has no moves")
    if len(load()) < 3:
        problems.append("fewer than three premises")
    return (not problems, "; ".join(problems) if problems else
            f"{len(load())} rap premises (archetypes from the bank), first-person boasts, rap moves, deflate capped, ingredients known")


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--plan")
    ap.add_argument("--request", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        ok, msg = selftest()
        print("premise selftest:", "PASSED" if ok else "FAILED", "-", msg)
        return 0 if ok else 1
    if a.plan:
        print(f"wrote {write_plan(a.plan)}  (use: WW_PLAN=<that path> python -m ww.cli argue SLOT)")
        return 0
    if a.request:
        r = request()
        print(r.system, "\n\n", r.messages[0]["content"])
        return 0
    for p in load():
        print(f"{p['id']:12} {p['title']}: {p['one_line']}")
        for slot, sec in p["sections"].items():
            print(f"    {slot:10} {sec['argument']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
