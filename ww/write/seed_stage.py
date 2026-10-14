"""Seed stage (plan 4.1): turn ONE travel fact into bit seeds - persona claim, mechanism with two readings, payoff word.

The writer downstream realises a seed; it does not invent the joke. A seed with no second reading (except the two mechanisms that
need none: euphemism_as_logistics, bathos_closer) is rejected in code. Prompts carry abstract mechanism schemas only - never the
original's lines - plus the burnt-frames list and a cliche list as negatives.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .. import config
from ..llm import LLM, Request

MECHANISMS = {
    "cashed_idiom": "a stock phrase first used figuratively, then its key word taken LITERALLY in the next bar (figurative first, literal last), the literal word landing in the rhyme slot",
    "homophone_pun": "one sound, two spellings or words; the listener hears reading 1 and the second reading arrives on the rhyme word",
    "loanword_soundalike": "a word from the place's own language that sounds like an English word or phrase, answered by a consequence in English",
    "one_word_two_senses": "the same end word used twice in the run with two different meanings",
    "rhyming_slang_swap": "a rhyming-slang style substitution where the unspoken rhyme word is the joke",
    "number_ladder": "a price or number set up early and transformed later (rising, converted, doubled, inflated) with the unit kept",
    "euphemism_as_logistics": "something extraordinary or illicit reported in the vocabulary of an everyday errand, with no wink and no explanation",
    "bathos_closer": "a grand or menacing claim followed by the smallest possible concrete object or admin detail",
    "lore_allusion": "a bar pair that reaches a famous thing (a brand, watch, car, film, character) through TWO or more of its known associations (a part, a nickname, a catchphrase, a rival) without ever naming it; the surface reading is a complete everyday claim, and the association lands in the rhyme slot. Fill `entity` with the thing's name from the POP-CULTURE KIT.",
}
NO_SECOND_READING = {"euphemism_as_logistics", "bathos_closer", "number_ladder"}
CLICHES = ["passport stamps", "jet lag", "wanderlust", "boarding pass", "living my best life", "bucket list", "sun on my skin",
           "chasing sunsets", "from A to B", "memories not things", "the journey not the destination"]

SEED_SCHEMA = {
    "type": "object", "required": ["seeds"],
    "properties": {"seeds": {"type": "array", "minItems": 3, "items": {
        "type": "object",
        "required": ["direction", "frame_id", "persona_claim", "mechanism", "reading_1", "payoff_word", "setup_idea", "bathos_closer"],
        "properties": {
            "direction": {"type": "string", "enum": ["A", "B"]},
            "frame_id": {"type": "string"},
            "persona_claim": {"type": "string", "maxLength": 160},
            "mechanism": {"type": "string", "enum": list(MECHANISMS)},
            "reading_1": {"type": "string"}, "reading_2": {"type": "string"},
            "payoff_word": {"type": "string"}, "setup_idea": {"type": "string"}, "bathos_closer": {"type": "string"},
            "entity": {"type": "string"}}}}},
}

SYSTEM_TMPL = """You are a comedy writer for a deadpan British rap about a world tour, in the tradition of a nonchalant man who reports extraordinary or petty things in the flat vocabulary of an everyday errand. You do not write the song yet. You design BIT SEEDS: the joke engine behind a few bars, built from ONE real travel fact.

PERSONA: {persona}

A travel fact is usually the BLAND half of the joke (an admin or consumer detail). Two directions:
 A (fact-as-frame): invent a grand, illicit or absurd act that can be reported in exactly the fact's own bureaucratic words, using the fact's own noun or number.
 B (fact-as-bathos): the narrator makes a big claim and the fact is the small, concrete anticlimax.
For each seed choose ONE frame from the list given (its stock vocabulary is what the claim is dressed in), ONE mechanism, and pick the PAYOFF WORD FIRST: the word on which the joke lands, which must be able to sit last in a line.

MECHANISMS (abstract):
{mechs}

PREFERENCE: the comedy comes from CHARACTER, not gags. Strongly prefer euphemism_as_logistics (an extraordinary act reported as an ordinary errand, in the frame's own phrases) and bathos_closer; cashed_idiom only when the idiom is natural to the frame. Pun mechanisms (homophone_pun, rhyming_slang_swap, loanword_soundalike) are allowed for AT MOST ONE seed in the set and only if the pun is not announced and the second reading arrives on its own - a pun that groans is a failed seed. Never use a made-up or forced sound-alike.
{shape_rule}
HARD RULES: persona_claim is ONE flat first-person sentence, at most 18 words, containing a concrete noun or number from the fact; cartoon-level menace only, never instructional, never about a named real person or business; swearing and vulgar slang are allowed and never softened; do not explain the joke; the narrator never reacts to the extraordinary thing. 
 reading_1 and reading_2 must be written in plain words, reading_2 being the second meaning of the payoff (omit reading_2 only for euphemism_as_logistics, bathos_closer, number_ladder). Do NOT use any of these frames or tropes: {burnt}. Avoid these stock phrases: {cliches}. Each seed must differ in mechanism or frame from the others.Return JSON only."""


@dataclass
class Fact:
    id: str
    place: str
    trip: str
    detail: str            # the concrete, checkable thing (a sign, a price, a rule, an object)
    kind: str = "custom"   # price | word | custom | landmark | food | police | currency | number
    source: str = "material"
    tags: list = field(default_factory=list)


def load_frames() -> dict:
    d = json.loads((config.ROOT / "ww" / "lex" / "banks" / "admin_frames.json").read_text(encoding="utf-8"))
    return {"burnt": d["burnt"], "frames": {f["id"]: f for f in d["frames"]}}


def pick_frames(fact: Fact, k: int = 6) -> list[dict]:
    """frames whose vocabulary overlaps the fact's words; padded with random-but-deterministic others so a seed can use an unexpected frame."""
    fw = set(re.findall(r"[a-z]{4,}", (fact.detail + " " + fact.place + " " + fact.trip + " " + " ".join(fact.tags)).lower()))
    fr = load_frames()["frames"]
    scored = []
    for f in fr.values():
        vocab = set(re.findall(r"[a-z]{4,}", " ".join(f["verbs"] + f["nouns"] + f["phrases"] + [f["name"]]).lower()))
        scored.append((len(fw & vocab), f["id"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    top = [i for s, i in scored[: k - 2] if s > 0]
    rest = [i for s, i in sorted(scored, key=lambda x: hash_key(fact.id + x[1]))]
    out = top + [i for i in rest if i not in top][: k - len(top)]
    return [fr[i] for i in out]


def hash_key(s: str) -> int:
    import hashlib
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


PERSONA = ("a deadpan British man in his thirties from Bristol, nonchalant and slightly bored, who treats a world tour like a series of errands; "
           "he never raises his voice, never explains, never reacts to the extraordinary, mentions other people rather than addressing them, "
           "and uses ordinary British consumer and admin phrases for everything.")


SHAPE_RULES = {
    "trochee": "PAYOFF SHAPE: payoff_word must be a word of exactly TWO syllables stressed on the FIRST (like favour, ticket, footpath, wristband, tattoo is NOT allowed, receipt is NOT allowed), because it must close a rap bar and rhyme with three other such words. It must be a real, common English word or a well-known place name.",
    "any": "",
}


def build_request(fact: Fact, n: int, model: str, effort: Optional[str], temperature: Optional[float], persona: str = PERSONA, scope: str = "seed",
                  shape: str = "any") -> Request:
    fr = load_frames()
    frames = pick_frames(fact)
    flist = "\n".join(f"- {f['id']}: {f['name']} | verbs: {', '.join(f['verbs'][:5])} | nouns: {', '.join(f['nouns'][:5])} | stock phrases: {'; '.join(f['phrases'][:3])}"
                      for f in frames)
    system = SYSTEM_TMPL.format(persona=persona, mechs="\n".join(f"- {k}: {v}" for k, v in MECHANISMS.items()),
                                burnt="; ".join(fr["burnt"]), cliches=", ".join(CLICHES), shape_rule=SHAPE_RULES[shape])
    user = (f"FACT (real, from the traveller's own history): place {fact.place}; trip {fact.trip}; detail: {fact.detail}\n\n"
            f"FRAMES YOU MAY USE:\n{flist}\n\nWrite {n} seeds.")
    return Request(model=model, system=system, messages=[{"role": "user", "content": user}], schema=SEED_SCHEMA, max_tokens=6000,
                   effort=effort, temperature=temperature, stage="seeds", scope=scope)


def lore_reasons(seed: dict) -> list[str]:
    """STRUCTURAL check for the one mechanism that claims a hidden entity: the claim must reach it through >= 2 triggers from its card and must
    not name it. Not a quality score (ww/lex/cards.py); it only rejects a seed that is mislabelled."""
    if seed.get("mechanism") != "lore_allusion":
        return []
    from ..lex import cards
    # only the BAR-BOUND fields: setup_idea / reading_2 are the model's explanation and legitimately name the entity, so reading them would
    # both fire the no-name rule falsely and let a self-report stand in for evidence
    text = " ".join(str(seed.get(k) or "") for k in ("persona_claim", "bathos_closer", "payoff_word"))
    r = cards.check_allusion(seed.get("entity") or "", text)
    return [] if r["ok"] else ["lore_allusion: " + "; ".join(r["reasons"])]


def validate(seed: dict, fact: Fact) -> list[str]:
    """code-side rejection reasons (an empty list = keep)."""
    why = []
    if seed["mechanism"] not in NO_SECOND_READING and not (seed.get("reading_2") or "").strip():
        why.append("no second reading")
    if len(seed["persona_claim"].split()) > 22:
        why.append("claim too long")
    if len(re.findall(r"[A-Za-z']+", seed["payoff_word"])) != 1:
        why.append("payoff must be a single word")
    low = seed["persona_claim"].lower()
    if any(c in low for c in CLICHES):
        why.append("cliche")
    if seed["frame_id"] not in load_frames()["frames"]:
        why.append("unknown frame")
    why += lore_reasons(seed)
    return why


def validate_shape(seed: dict) -> list[str]:
    """payoff word must pass the sound planner: a stress-first two-syllable word with >= 3 rhyming trochee partners."""
    from . import sound_plan
    m = sound_plan.menu(seed["payoff_word"])
    return [] if m["ok"] else [f"payoff '{seed['payoff_word']}': {m['why']}"]


def run(llm: LLM, fact: Fact, n: int = 6, model: str = "ds-flash", effort: Optional[str] = "high", temperature: Optional[float] = None,
        shape: str = "any") -> dict:
    res = llm.complete(build_request(fact, n, model, effort, temperature, shape=shape), use_cache=temperature is None)
    seeds = (res.parsed or {}).get("seeds") or []
    kept, dropped = [], []
    for s in seeds:
        w = validate(s, fact) + (validate_shape(s) if shape == "trochee" else [])
        (dropped if w else kept).append({**s, "_why": w} if w else s)
    return {"fact": fact.id, "model": model, "kept": kept, "dropped": dropped, "usd": res.usd, "schema_errors": res.schema_errors}


def selftest() -> tuple[bool, str]:
    problems = []
    f = Fact("t1", "Black Forest", "Interrail 2019", "honesty drinks stall on the trail with a carved gateway and a payment box", tags=["trail", "box"])
    fr = pick_frames(f)
    if len(fr) != 6 or "trail_etiquette" not in [x["id"] for x in fr]:
        problems.append(f"frame picker should surface trail_etiquette for an honesty box: {[x['id'] for x in fr]}")
    good = {"direction": "A", "frame_id": "trail_etiquette", "persona_claim": "I left the money in the box and took the lot.", "mechanism": "cashed_idiom",
            "reading_1": "paid honestly", "reading_2": "took everything", "payoff_word": "box", "setup_idea": "x", "bathos_closer": "y"}
    if validate(good, f):
        problems.append(f"good seed rejected: {validate(good, f)}")
    bad = dict(good, reading_2="", payoff_word="two words")
    if len(validate(bad, f)) < 2:
        problems.append("bad seed should fail on missing reading and multi-word payoff")
    lore = dict(good, mechanism="lore_allusion", entity="No Such Thing Ltd")
    if not any(w.startswith("lore_allusion") for w in validate(lore, f)):
        problems.append("a lore_allusion seed whose entity has no card must be rejected")
    if lore_reasons(good):
        problems.append("lore checks must not touch other mechanisms")
    return (not problems, "; ".join(problems) if problems else "frame picker finds the honesty-box frame; seed validation rejects missing readings, multi-word payoffs and lore_allusion claims with no card")
