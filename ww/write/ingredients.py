"""Ingredients: the travel material as things a CHARACTER can claim, not events to retell (plan step 3, 14 Oct 2026).

Why. Every draft was a recount because the writer was handed stories and facts in time order and asked to "tell or boast this story's
core". toolkit/recount.py measures the result: the original's song recount share is 0.20; v17 is 0.50, the pasted song 0.78, the
flow-fitted v5 0.66. The original never tells its story: it states what the narrator is, has and shrugs off, using places, objects,
prices and local words as stamps. So the material is re-cut here as INGREDIENTS, one record per fact or story:

  objects      concrete things in it (extracted: spaCy nouns that belong to an image field)
  numbers      numbers and prices (extracted)
  places       true places named (extracted, gazetteer)
  local        local words (extracted, toolkit/local_words.txt)
  contradiction the gap between how big it sounds and how small it is -- the joke the bar can cash
  trait        what it reveals about the narrator: the through-line that replaces chronology (brief/persona.md aggregates these)
  admin        an everyday admin register to re-file it in (an id from ww/lex/banks/admin_frames.json, with its phrases)
  transforms   which moves suit it (exaggerate, invert, understate, re-file as admin, hypothetical, boast)

The contradiction / trait / admin fields of the PUBLIC entries were written by the assistant in the main thread (14 Oct 2026, flagged
"(persona)" for Joe to veto, rule 5). Private stories (eval/_stories.json, material/joes_own_stories.md: git-ignored, the repo is public)
go through versebank.essence() -- one cached model call per story -- with `--essence`, and are written to material/ingredients_private.md,
which is git-ignored too.

  python -m ww.write.ingredients                 writes material/ingredients.md (public entries only)
  python -m ww.write.ingredients --essence       also the private stories, via essence() (needs DEEPSEEK_API_KEY)
  python -m ww.write.ingredients --selftest
"""
from __future__ import annotations

import functools
import json
import os
import re
import sys

from .. import config

ROOT = config.ROOT
sys.path.insert(0, str(ROOT / "toolkit"))

OUT = ROOT / "material" / "ingredients.md"
OUT_PRIVATE = ROOT / "material" / "ingredients_private.md"

# Public ingredient records. `text` is what extraction reads; it comes from ww/schema/joe_facts.py (fact:<id>) or from Joe's own pasted
# song (writing/detection_test/travel_draft.md, committed, his words). The judgement fields are the assistant's, flagged (persona).
STORIES = [
    {"id": "song:tubing", "source": "writing/detection_test/travel_draft.md V1 1-8", "place": "a river in Laos (tubing)",
     "text": "tubing down a slow river waiting for the falls that never came; my mate walked into a bar still dripping, with his tube and wet shorts, and kept going",
     "contradiction": "the rapids he braced for never came; the only danger was the bar's dress code",
     "trait": "the mate never stops; the narrator narrates other people's nerve", "admin": "hostel_rules",
     "transforms": ["understate", "re-file as admin"]},
    {"id": "song:jeep", "source": "writing/detection_test/travel_draft.md V1 9-16", "place": "Western Australia, back to Perth",
     "text": "a jeep stuck in white sand, left behind by the second jeep, a flat tyre, no signal on two phones, a bloke with a torch fixed it, back in Perth by ten",
     "contradiction": "a four-wheel drive that cannot drive on sand; rescued by the one bloke with a torch",
     "trait": "gets left behind and calls it a plan", "admin": "garage_quote", "transforms": ["re-file as admin", "boast"]},
    {"id": "song:pool", "source": "writing/detection_test/travel_draft.md V1 25-32", "place": "a beach bar in South East Asia",
     "text": "the lads hustled blokes at pool and won one million, stashed the cash in their shoes, the loser chased them down wet sand; one million dong is thirty quid",
     "contradiction": "a million won is thirty quid: millionaires in the wrong currency",
     "trait": "rich in the wrong currency; brags in numbers, not value", "admin": "bank_letter", "transforms": ["exaggerate", "invert"]},
    {"id": "song:bribe", "source": "writing/detection_test/travel_draft.md V1 25-32", "place": "South East Asia",
     "text": "the police were waiting, wanted cash, both lads paid the bribe on the spot",
     "contradiction": "a bribe handled like a parking fine", "trait": "treats the illicit as admin",
     "admin": "penalty_notice", "transforms": ["re-file as admin", "understate"]},
    {"id": "song:floor", "source": "writing/detection_test/travel_draft.md V1 33-44", "place": "Laos",
     "text": "a weed pizza, no key, slept at the hostel door; paid for a room and slept on the floor; no jabs, bitten red raw by insects",
     "contradiction": "paid for a room, slept on the floor; no jabs, full war with the insects",
     "trait": "pays for things he never uses", "admin": "bnb_rules", "transforms": ["understate", "re-file as admin"]},
    {"id": "song:hanoi", "source": "writing/detection_test/travel_draft.md V2 1-8", "place": "Hanoi to the south, Vietnam",
     "text": "Honda Win motorbikes from Hanoi, biblical rain filled both shoes, lost each other, ditched the bike at the roadside, lost the key, helmets stolen, the rental staff drunk",
     "contradiction": "rode the length of a country and the bike ended in a hedge; the drunkest people were the ones renting the bikes",
     "trait": "abandons things and calls it travelling light", "admin": "insurance_claim", "transforms": ["re-file as admin", "boast"]},
    {"id": "song:wasteland", "source": "writing/detection_test/travel_draft.md V2 9-16", "place": "Wasteland, Amsterdam",
     "text": "turned away at the door for wearing jeans, came back in wearing just a shirt and a hat, the hat stayed on all night",
     "contradiction": "refused for jeans, admitted in less",
     "trait": "obeys the rules to the letter and wins", "admin": "small_print", "transforms": ["re-file as admin", "boast"]},
    {"id": "song:gnome", "source": "writing/detection_test/travel_draft.md Hook 5-8", "place": "Rotterdam",
     "text": "skipped the show at the festival and bought the big gnome instead",
     "contradiction": "a rap festival and the souvenir is a garden gnome", "trait": "buys tat, misses the headliner",
     "admin": "collection_point", "transforms": ["boast", "hypothetical"]},
    {"id": "song:tophat", "source": "writing/detection_test/travel_draft.md Hook 9-16", "place": "Boomtown",
     "text": "lost four days dancing, flooded tent then dust then drought, found a pink floppy top hat and wore it like a crown",
     "contradiction": "three weathers in one weekend and the only kit that survived is a pink top hat",
     "trait": "dresses for none of the weather; crowns himself", "admin": "campsite_rules", "transforms": ["exaggerate", "boast"]},
    {"id": "song:endgame", "source": "writing/detection_test/travel_draft.md V1 17-24", "place": "Amsterdam, King's Day",
     "text": "orange crowds, truffles, the Avengers Endgame premiere, passed out in the cinema aisle, the usher showed us the door",
     "contradiction": "the biggest film ending of the decade and he slept through it in the aisle",
     "trait": "sleeps through the big moments", "admin": "review_site", "transforms": ["understate", "re-file as admin"]},
]

# the judgement fields for the joe_facts cards (assistant-authored, flagged (persona)): {fact id: (contradiction, trait, admin, transforms)}
FACT_JUDGEMENT = {
    "bf_honesty": ("an unmanned stall in a forest trusts a stranger more than his bank does", "pays on trust, takes it as a compliment",
                   "self_checkout", ["invert", "re-file as admin"]),
    "rot_gnome": ("a public sculpture the size of a van is still a garden gnome", "treats public art as merchandise",
                  "collection_point", ["boast", "hypothetical"]),
    "boom_guillotine": ("a wanted poster for having too much energy, and he is the least energetic man there", "low energy, high standing",
                        "penalty_notice", ["invert", "understate"]),
    "ams_cola": ("eight novelty colas on a windowsill as a tasting menu", "treats a campsite like a wine tour", "review_site",
                 ["exaggerate", "re-file as admin"]),
    "moto_ferry": ("three countries on a loaded bike and the hard part was the ferry check-in", "an epic tour done like a commute",
                   "ferry_checkin", ["understate", "re-file as admin"]),
    "interrail_pass": ("an unlimited pass with a form to fill in every day", "does Europe like a paper round", "interrail",
                       ["re-file as admin", "understate"]),
    "bergen_shoes": ("crossed the North Sea to stand in his socks", "domesticated abroad", "bnb_rules", ["understate"]),
    "marrakesh_souk": ("the special price just for you is everyone's price", "thinks he is a haggler", "loyalty_card",
                       ["invert", "boast"]),
    "rl_rotterdam": ("watched the headliner on a stranger's phone", "misses the main event", "festival_wristband",
                     ["understate", "re-file as admin"]),
    "boomtown_all": ("wet, then dusty, then bone dry, and the same hat", "dresses for none of the weather", "campsite_rules",
                     ["exaggerate", "boast"]),
    "kings_day": ("the biggest film of the decade and he slept in the aisle", "sleeps through the big moments", "review_site",
                  ["understate"]),
    "k_gari": ("the only rule on the island is the tide", "gets stuck, calls it a plan", "driving_test", ["re-file as admin", "boast"]),
    "lauterbrunnen": ("seventy-two waterfalls and he is looking at his boot", "misses the view for the detail", "trail_etiquette",
                      ["understate", "invert"]),
    "naples_stag": ("a shrine to a footballer under a volcano, and the three-euro cocktails are the danger", "values price over history",
                    "meal_deal", ["understate", "re-file as admin"]),
    "bilbao_end": ("a bronze spider the size of a house, and he is worried about the ferry time", "the sight is an errand",
                   "ferry_checkin", ["understate", "re-file as admin"]),
}

# the trait FAMILIES the persona is built from (assistant's grouping, flagged): each record's trait is one instance of a family
TRAIT_FAMILY = {
    "sleeps through / misses the main event": ["fact:kings_day", "fact:rl_rotterdam", "song:gnome", "song:endgame", "fact:lauterbrunnen",
                                               "fact:boom_guillotine"],
    "files the epic as an errand": ["fact:moto_ferry", "fact:interrail_pass", "fact:bilbao_end", "song:bribe", "fact:bergen_shoes"],
    "gets left behind or stuck and calls it a plan": ["fact:k_gari", "song:jeep", "song:hanoi"],
    "rich in the wrong currency (price over value)": ["song:pool", "fact:naples_stag", "fact:marrakesh_souk", "fact:ams_cola", "song:floor"],
    "obeys the rules to the letter and wins": ["fact:bf_honesty", "song:wasteland"],
    "buys tat and crowns himself with it": ["fact:rot_gnome", "song:tophat", "fact:boomtown_all"],
    "narrates other people's nerve": ["song:tubing"],
}
_FAMILY_OF = {i: fam for fam, ids in TRAIT_FAMILY.items() for i in ids}

NUM = re.compile(r"\b(\d[\d,.]*\s*(?:%|euro|euros|quid|pounds|baht|dong|mil|million|k|km)?|(?:one|two|three|four|five|six|seven|eight|nine|ten|"
                 r"eleven|twelve|twenty|thirty|forty|fifty|seventy-two|hundred|thousand|million|mil)\b(?:\s+(?:euros?|quid|pounds|dong|baht|"
                 r"mil|million|days|weeks|nights|countries|stops|waterfalls|cans|jeeps|phones|decembers))?)", re.I)


@functools.lru_cache(maxsize=1)
def _admin():
    d = json.load(open(ROOT / "ww" / "lex" / "banks" / "admin_frames.json", encoding="utf-8"))
    return {f["id"]: f for f in d["frames"]}


@functools.lru_cache(maxsize=1)
def _local_words():
    out = set()
    for line in open(ROOT / "toolkit" / "local_words.txt", encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            w = line.split("|")[0].strip().lower()
            if w:
                out.add(w)
    return out


def extract(text: str) -> dict:
    """deterministic: objects (nouns in an image field, else concrete nouns), numbers, places, local words."""
    import imagery
    import recount
    places = recount._places()
    doc = recount._nlp()(text)
    objs, seen = [], set()
    for t in doc:
        if t.pos_ == "NOUN":
            w = t.lemma_.lower()
            if w in seen or len(w) < 3:
                continue
            fields = [f for f in imagery.IDX.get(w, ()) if f not in imagery.NOT_IMAGE]
            if fields or t.dep_ in ("dobj", "pobj", "nsubj", "compound"):
                objs.append(w)
                seen.add(w)
    nums = sorted({m.group(0).strip() for m in NUM.finditer(text)}, key=text.lower().find)
    pl, run = [], []
    for t in list(doc) + [None]:   # join adjacent capitalised words into one place ("Black Forest", "Zell am See")
        if t is not None and t.text[:1].isupper() and t.lower_ not in ("i", "the", "a"):
            run.append(t)
            continue
        if run and any(x.lower_ in places for x in run):
            name = " ".join(x.text for x in run)
            if name not in pl:
                pl.append(name)
        run = []
    loc = sorted({w for w in re.findall(r"[a-z'\-]+", text.lower()) if w in _local_words()})
    return {"objects": objs[:10], "numbers": nums, "places": pl, "local": loc}


def records() -> list[dict]:
    """every public ingredient record, fully built."""
    from ..schema.joe_facts import FACTS
    out = []
    for f in FACTS:
        j = FACT_JUDGEMENT.get(f.id)
        rec = {"id": f"fact:{f.id}", "source": "ww/schema/joe_facts.py", "place": f.place, "when": f.trip,
               "text": f.detail, "contradiction": j[0] if j else "", "trait": j[1] if j else "",
               "admin": j[2] if j else "", "transforms": j[3] if j else []}
        out.append(rec)
    out += [dict(s) for s in STORIES]
    for r in out:
        r.update(extract(r["text"] + " " + r.get("place", "")))
        fr = _admin().get(r.get("admin") or "")
        r["admin_phrases"] = (fr["phrases"][:2] + fr["verbs"][:2]) if fr else []
    return out


def traits() -> list[tuple[str, list[str]]]:
    """trait -> ingredient ids, most common first (the input to brief/persona.md)."""
    agg: dict[str, list[str]] = {}
    for r in records():
        fam = _FAMILY_OF.get(r["id"]) or r.get("trait")
        if fam:
            agg.setdefault(fam, []).append(r["id"])
    return sorted(agg.items(), key=lambda kv: -len(kv[1]))


def pool(ids=None) -> list[dict]:
    """records for a section's ingredient pool (all when ids is None)."""
    rs = records()
    return rs if ids is None else [r for r in rs if r["id"] in set(ids)]


def as_prompt(recs: list[dict]) -> str:
    """the ingredient pool as the writer sees it: never a timeline, always objects + the gap + the trait + a register to re-file it in."""
    L = []
    for r in recs:
        L.append(f"- [{r['id']}] objects: {', '.join(r['objects'][:6])}" + (f"; numbers: {', '.join(r['numbers'])}" if r["numbers"] else "")
                 + (f"; places: {', '.join(r['places'])}" if r["places"] else "") + (f"; local: {', '.join(r['local'])}" if r["local"] else "")
                 + f"\n    the gap: {r['contradiction']} | trait: {r['trait']} | re-file as: {r['admin']}"
                 + (f" ({'; '.join(r['admin_phrases'][:2])})" if r["admin_phrases"] else "")
                 + (f" | moves: {', '.join(r['transforms'])}" if r["transforms"] else ""))
    return "\n".join(L)


def render(recs: list[dict]) -> str:
    L = ["# Ingredients (generated by `python -m ww.write.ingredients`; do not edit by hand)", "",
         "Each true fact or story, re-cut as things a CHARACTER can claim. The writer gets these, never the story in time order.",
         "The gap / trait / re-file fields are the assistant's judgement, flagged **(persona)**: Joe vetoes. Places, objects and numbers are",
         "extracted from the source text.", ""]
    for r in recs:
        L += [f"## {r['id']} - {r['place']}", "", f"- source: {r['source']}" + (f", {r['when']}" if r.get("when") else ""),
              f"- objects: {', '.join(r['objects']) or '-'}", f"- numbers: {', '.join(r['numbers']) or '-'}",
              f"- places: {', '.join(r['places']) or '-'}", f"- local words: {', '.join(r['local']) or '-'}",
              f"- the gap (persona): {r['contradiction'] or '-'}", f"- trait (persona): {r['trait'] or '-'}"
              + (f"  [family: {_FAMILY_OF[r['id']]}]" if r["id"] in _FAMILY_OF else ""),
              f"- re-file as: {r['admin'] or '-'}" + (f" -- {'; '.join(r['admin_phrases'])}" if r["admin_phrases"] else ""),
              f"- moves that suit it: {', '.join(r['transforms']) or '-'}", ""]
    L += ["## Traits, aggregated (the input to brief/persona.md)", ""]
    for t, ids in traits():
        L.append(f"- {t}  ({len(ids)}: {', '.join(ids)})")
    return "\n".join(L) + "\n"


def private_records(llm=None) -> list[dict]:
    """private stories through versebank.essence() (cached, one call per story). Returns [] when there is nothing private here."""
    p = config.EVAL_DIR / "_stories.json"
    if not p.exists():
        return []
    from . import versebank
    from ..llm import LLM, Ledger
    llm = llm or LLM(ledger=Ledger(run_id="ingredients"))
    out = []
    for st in json.load(open(p, encoding="utf-8")):
        e = versebank.essence(llm, st)
        rec = {"id": f"story:{st['id']}", "source": "eval/_stories.json (private)", "place": st.get("title", ""), "text": st.get("text", ""),
               "contradiction": e.get("contradiction") or e.get("irony", ""), "trait": e.get("trait") or e.get("mood", ""),
               "admin": "", "transforms": []}
        rec.update(extract(rec["text"]))
        rec["admin_phrases"] = []
        out.append(rec)
    return out


def selftest() -> tuple[bool, str]:
    problems = []
    rs = records()
    if len(rs) < 20:
        problems.append(f"only {len(rs)} records")
    bad_admin = [r["id"] for r in rs if r["admin"] and r["admin"] not in _admin()]
    if bad_admin:
        problems.append(f"unknown admin frames {bad_admin}")
    pool_ = {r["id"]: r for r in rs}
    if "thirty quid" not in " ".join(pool_["song:pool"]["numbers"]).lower() and "thirty" not in " ".join(pool_["song:pool"]["numbers"]).lower():
        problems.append(f"numbers not extracted from the pool story: {pool_['song:pool']['numbers']}")
    if not pool_["fact:rot_gnome"]["objects"]:
        problems.append("no objects extracted for the gnome")
    if any(not r["trait"] for r in rs):
        problems.append("a record has no trait")
    orphan = [r["id"] for r in rs if r["id"] not in _FAMILY_OF]
    if orphan:
        problems.append(f"records with no trait family: {orphan}")
    if "Black Forest" not in pool_["fact:bf_honesty"]["places"]:
        problems.append(f"multi-word place not joined: {pool_['fact:bf_honesty']['places']}")
    return (not problems, "; ".join(problems) if problems else f"{len(rs)} public records, every admin frame known, objects and numbers extracted")


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--essence", action="store_true", help="also build the private stories through essence() (needs a key)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        ok, msg = selftest()
        print("ingredients selftest:", "PASSED" if ok else "FAILED", "-", msg)
        return 0 if ok else 1
    recs = records()
    OUT.write_text(render(recs), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(recs)} records)")
    if a.essence:
        priv = private_records()
        if priv:
            OUT_PRIVATE.write_text(render(priv), encoding="utf-8")
            print(f"wrote {OUT_PRIVATE.relative_to(ROOT)} ({len(priv)} private records; git-ignored)")
        else:
            print("no private stories on this machine (eval/_stories.json absent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
