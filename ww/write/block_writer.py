"""Block writer (plan 4.2): realise ONE bit seed as a 4-bar rhyme-chain block, given an end-word MENU (not a mandate).

The writer does not invent the joke: the seed carries the claim, the mechanism, the readings and the payoff word. It chooses the other
end words from the menu (or any real, common word that rhymes), reorders the clause so each lands naturally, and may return
`no_fit` for a bar rather than bend the sentence around a word (the 13 Oct failure). Structured output includes a plain-prose version of
each bar and its claim, so the reader and the fluency check have something to compare.
"""
from __future__ import annotations

from typing import Optional

from ..llm import LLM, Request
from . import seed_stage, sound_plan

# the attitude each bar takes (14 Oct 2026). A bar that only reports the next thing that happened takes no stance; the recount gate
# (toolkit/recount.py) fails blocks made of them, so the writer is asked to name each bar's stance up front.
STANCES = ["brag", "flex_list", "shout_out", "threat", "name_drop", "hater", "punchline", "title_drop", "callback", "deflate"]


def block_schema(nbars: int) -> dict:
    """The writer's schema, sized to the SECTION. It was fixed at exactly 4 bars, so a section-length block could not be asked
    for at all: the verses are 8 bars and V1 33-44 is 12. The bar count now comes from the plan's own per-bar targets."""
    return {
        "type": "object", "required": ["blocks"],
        "properties": {"blocks": {"type": "array", "minItems": 1, "items": {
            "type": "object", "required": ["argument", "bars", "payoff_bar"],
            "properties": {"argument": {"type": "string"}, "payoff_bar": {"type": "integer"},
                           "bars": {"type": "array", "minItems": nbars, "maxItems": nbars, "items": {
                               "type": "object", "required": ["text", "end_word", "claim", "stance", "plain"],
                               "properties": {"text": {"type": "string"}, "end_word": {"type": "string"},
                                              "claim": {"type": "string"}, "plain": {"type": "string"},
                                              "stance": {"type": "string", "enum": STANCES},
                                              "no_fit": {"type": "boolean"}}}}}}}},
    }


BLOCK_SCHEMA = block_schema(4)

JOBS_HOOK = [
    "Bar 1 - sets the scene: names a place, may open with a short local-language greeting. Do NOT use the pattern '[greeting] to the boys/lads/birds in [place]'.",
    "Bar 2 - a flat CLAIM in an errand register (present tense, the frame's own everyday British phrases), setting the seed up. Not what happened next: what the narrator IS, HAS or DOES as a matter of routine.",
    "Bar 3 - the PAYOFF: the seed's payoff word is the LAST word of this bar and the extraordinary thing lands here.",
    "Bar 4 - the closer: a modal understatement ('might ...') or a petty concrete detail naming a different place or object; it must not explain anything.",
]

SYSTEM = """You write four bars of a deadpan British rap (a chorus-style block) for this narrator: {persona}

You are given a BIT SEED - the joke is already designed. Realise it; do not swap in a different joke. A bar is a line spoken at pace: 8 to 10 syllables, one thought, a sentence or a picture a listener can follow on one hearing. Never a list of nouns, never a string of words that only works because it rhymes, never filler like "and the whole", "the lot", "him in". The narrator never explains the joke, never reacts to the extraordinary thing, never addresses anyone directly, and uses only cartoon-level menace (nothing instructional, no named real people). Swearing and vulgar slang are allowed and never softened or bleeped: use them flatly, the way this narrator uses everything else, and only where the bar needs them.

SOUND: every bar must END on a word of exactly two syllables stressed on the first (like favour, ticket, footpath), and all four end words must rhyme with each other. The four end words must be four DIFFERENT words -- an end word may not be used twice in the block (the checker rejects a block where one repeats). The payoff word is bar 3's end word. Pick the other three end words from the MENU of words that rhyme with it (or any real common word that does). Reorder the sentence so the end word falls naturally. If NO natural sentence ends on any menu word for a bar, set no_fit true for that bar and write the best sentence you can, rather than twisting the meaning to fit a word.
WHAT COUNTS AS A RHYME: the stressed syllable and everything after it must sound alike (favours / flavours; Dublin / double it; fox / box). Two words that share only an unstressed ending (audit, biscuit, credit, orbit: only the "it") do NOT rhyme, however the spelling looks; a checker rejects them. Vowels carry the rhyme, so keep the stressed vowel identical and let the consonants after it differ only a little (m / n, p / t / k).
TEMPLATE: in a block, the stressed rhyme syllable sits the same distance from the end in at least 3 of 4 bars (a three-syllable tail such as 'double it / shovel it / covered in' in every bar), and the vowel of that stressed syllable comes back ONCE OR TWICE EARLIER in the bar, at about the same point in the neighbouring bars (grab ... having him / man ... halogen). Repeat the pattern bar after bar rather than varying it.
GRAMMAR: introduce every person and thing before you refer to it. A bar may not open on his, her, him, it, they or them unless the bar before it named that person or thing -- the grammar check rejects an unresolved pronoun.
{length_rule}

JOBS:
{jobs}

A RAP SONG, NOT A DIARY: the bars are BOASTS by a character (status, reach, menace, notoriety), said flat; the comedown is at most one bar in eight. Never chain past-tense events ("we left... we rode... then...") and never sequence places ("stop one... then... next..."). A true event is an ingredient: turn it into a present-tense claim, a boast, a routine, or a flat aside. At most two bars in a row may report a past event.

For each bar also give: claim (what it says in at most 15 words), stance (the rap move the bar makes: brag, flex_list, shout_out, threat, name_drop, hater, punchline, title_drop, callback or deflate; at most one deflate in eight bars) and plain (the same thing said in ordinary speech with no rhyme constraint). Return JSON only."""


def _length_rule(sylls, examples=None) -> str:
    """The bar lengths the WRITER must hit. They were computed and then never reached the prompt: build_request passed
    sylls= to str.format while SYSTEM had no placeholder for it, so the plan's own per-bar targets (8/10/8/8 for Hook 5-8)
    were dropped and the model wrote 10-syllable opening bars against an 8-syllable frame (14 Oct 2026).

    The worked examples are the same instrument one step further. Measured on the full build, every short target was missed
    (V1 33-44 asks for 6, 7, 7 and 5 syllables on its first bars and the writer returned 10, 9, 13 and 14; the bar loop then
    tried up to 23 variants and shrank none of them). A number is not a length to a language model; a real bar of that length
    is, so each distinct target is shown with a counted bar of exactly that length."""
    vals = [s for s in (sylls or []) if s]
    if not vals:
        return "Length: 8 to 10 syllables per bar (bar 2 may run to 11). Shorter is better than padding."
    per = " / ".join(str(s) for s in sylls)
    total = sum(vals)
    rule = (f"Length, HARD, bar by bar and in this order: {per} syllables (block total {total}). A machine counts every bar "
            f"in the toolkit's own pronouncer and REJECTS the whole block if any bar is more than one syllable out, so "
            f"deliberately write SHORT: 8 syllables is about five or six words, so drop articles ('the', 'a'), 'from', 'my', "
            f"'and' until the bar is at or under its number. Count the syllables of each bar before you return it, and if a "
            f"bar is over, rewrite that bar shorter rather than keeping it. Never pad and never twist the meaning to fit.")
    ex = [(int(n), b) for n, b in (examples or []) if n]
    if ex:
        rule += ("\nLENGTH CALIBRATION (real bars from this song, each with its counted syllables -- copy this feel, not the "
                 "words):\n" + "\n".join(f"  {n} syllables: {b}" for n, b in ex[:6]))
    return rule


def build_request(seed: dict, fact: seed_stage.Fact, n: int, model: str, effort: Optional[str], temperature: Optional[float],
                  sylls=(8, 10, 8, 8), jobs=JOBS_HOOK, scope: str = "write", negatives: str = "", examples=None) -> Request:
    menu = sound_plan.menu(seed["payoff_word"])
    frames = seed_stage.load_frames()["frames"]
    fr = frames.get(seed["frame_id"], {})
    nbars = len(list(sylls)) or 4
    system = SYSTEM.format(persona=seed_stage.PERSONA, jobs="\n".join(jobs), length_rule=_length_rule(sylls, examples))
    if negatives:
        system += f"\n\nAVOID (measured rejections from earlier rounds, rule R10):\n{negatives}"
    lore = ""
    if seed.get("mechanism") == "lore_allusion" and seed.get("entity"):
        from ..lex import cards
        card = cards.get(seed["entity"])
        hooks = []
        if card:
            hooks = ([f"parts: {', '.join(card['parts'][:8])}"] if card.get("parts") else []) + \
                    ([f"figures: {'; '.join(f['phrase'] for f in card['figures'][:4])}"] if card.get("figures") else []) + \
                    ([f"aliases: {', '.join(card['aliases'][:4])}"] if card.get("aliases") else []) + \
                    ([f"known for: {'; '.join(card['famous_for'][:3])}"] if card.get("famous_for") else [])
        lore = (f"- LORE: this seed reaches '{seed['entity']}' without naming it. NEVER write '{seed['entity']}' in any bar. Keep at least TWO of its "
                f"associations in the bars ({' | '.join(hooks)}), the second reading landing in the end word where the sound allows. The bar must still read as a "
                f"complete everyday claim to someone who has never heard of it.\n")
    user = (f"BIT SEED\n- real fact: {fact.place}, {fact.trip}: {fact.detail}\n- direction {seed['direction']}, mechanism {seed['mechanism']}, frame '{seed['frame_id']}'\n"
            f"- narrator's claim (the engine of the joke): {seed['persona_claim']}\n- reading 1: {seed['reading_1']}\n- reading 2: {seed.get('reading_2') or '(none)'}\n"
            f"- payoff word (its bar ends on it): {seed['payoff_word']}\n- small closing detail: {seed['bathos_closer']}\n" + lore +
            f"- the frame's own phrases (dress the claim in these): {'; '.join(fr.get('phrases', [])[:4])} | {', '.join(fr.get('nouns', [])[:6])}\n\n"
            f"END-WORD MENU (rhyme with '{seed['payoff_word']}', two syllables, stress first): "
            f"{', '.join(c['word'] for c in menu['candidates'][:30])}\n\n"
            f"Write {n} different blocks, each EXACTLY {nbars} bars.")
    return Request(model=model, system=system,
                   messages=[{"role": "user", "content": user}], schema=block_schema(nbars),
                   max_tokens=max(5000, 900 * nbars), effort=effort,
                   temperature=temperature, stage="blocks", scope=scope)


def run(llm: LLM, seed: dict, fact: seed_stage.Fact, n: int = 6, model: str = "ds-flash", effort: Optional[str] = "high",
        temperature: Optional[float] = None, sylls=(8, 10, 8, 8), jobs=None, negatives: str = "", examples=None) -> list[dict]:
    res = llm.complete(build_request(seed, fact, n, model, effort, temperature, sylls=sylls, jobs=jobs, negatives=negatives,
                                    examples=examples), use_cache=temperature is None)
    out = []
    for b in (res.parsed or {}).get("blocks", []):
        b["seed"] = {k: seed[k] for k in ("persona_claim", "mechanism", "frame_id", "payoff_word")}
        if seed.get("entity"):
            b["seed"]["entity"] = seed["entity"]
        b["fact"] = fact.id
        out.append(b)
    return out
