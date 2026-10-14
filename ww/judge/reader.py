"""The semantic reader (plan 5.3): evidence first, verdict second, scores computed in CODE from the model's structured fields.

One call reads a RUN (2-8 consecutive bars, with optional preceding context). For each bar the model must paraphrase before it
types, then say whether a British speaker could say it, what links it to the previous bar, whether it is in persona and whether it is
specific; the run gets an argument sentence and a named payoff bar. The model never emits a score; `summarise` derives every number.

The prompt is written from craft principles (benchmark/craft_principles.md), never from the original's lines. It is a MEASURE:
until ww.registry marks an axis accepted this output is a diagnostic.
"""
from __future__ import annotations

from typing import Iterable, Optional

from ..llm import LLM, Request

TYPES = ["event", "claim", "stance", "greeting", "quote", "pun_licensed", "scene", "list", "filler", "nonsense"]
LINKS = ["cause", "contrast", "escalation", "callback", "parallel", "none"]
PERSONAS = ["boast", "deadpan_report", "menace_in_bland", "none"]
FLAGS = ["explained_joke", "moralising", "cliche"]
SAYS = {"event", "claim", "stance", "greeting", "quote", "pun_licensed"}   # bars that state or do something
DEAD = {"filler", "nonsense", "list"}

READER_SCHEMA = {
    "type": "object", "required": ["bars", "run"],
    "properties": {
        "bars": {"type": "array", "items": {
            "type": "object",
            "required": ["i", "paraphrase", "type", "grammatical_as_spoken", "link_to_previous", "persona_fit", "specific"],
            "properties": {
                "i": {"type": "integer"}, "paraphrase": {"type": "string", "maxLength": 160},
                "type": {"type": "string", "enum": TYPES},
                "grammatical_as_spoken": {"type": "boolean"}, "breaking_words": {"type": "string"},
                "link_to_previous": {"type": "string", "enum": LINKS},
                "persona_fit": {"type": "string", "enum": PERSONAS},
                "specific": {"type": "boolean"}, "specific_detail": {"type": "string"},
                "flags": {"type": "array", "items": {"type": "string", "enum": FLAGS}}}}},
        "run": {"type": "object", "required": ["argument"],
                "properties": {"argument": {"type": "string"}, "payoff_bar": {"type": ["integer", "null"]},
                               "orphans": {"type": "array", "items": {"type": "integer"}}}}},
}

SYSTEM = """You are a British listener and a strict editor of comic rap lyrics. You read a RUN of consecutive bars (lines) from one verse.
Work like an examiner, not a fan. A charitable paraphrase of a nonsense bar is the main failure you must avoid: if you had to INVENT a
meaning that the words do not carry, the bar is nonsense.

For EACH bar, in this order, fill the JSON fields:
1. paraphrase: restate what the bar says as one plain, checkable sentence of at most 15 words (who did what, to whom or what, where),
   using only what the words say. If you cannot, write NONE.
2. type: event (something happens) | claim (a stated fact, price, boast) | stance (the speaker's attitude) | greeting (salutation or sign-off)
   | quote (a line in another language, a catchphrase, a title or a reference used as a line; judge it as what it is, not as English grammar)
   | pun_licensed (the meaning rests on a sound-alike or double reading: give both readings in the paraphrase as "A / B") | scene (a picturable
   noun phrase, no event) | list (things enumerated, nothing claimed) | filler (grammatical, says nothing) | nonsense (not a sentence a person could say and mean).
3. grammatical_as_spoken: lines often CONTINUE a sentence from the previous bar or into the next (enjambment), so judge the sentence the line belongs to,
   read across the run, not the line on its own. Could a British speaker say that sentence aloud? Lyric fragments, enjambment, inversion for effect and a
   dropped "I" are fine; word-strings, missing objects and dangling words are not. If false, put the breaking words in breaking_words.
4. link_to_previous: cause | contrast | escalation | callback | parallel (a deliberate repeated pattern, e.g. one place or greeting per bar) | none.
   Bar 1 of a run is judged against the context lines, if any, else "none".
5. persona_fit: boast | deadpan_report (an extraordinary thing said flatly, in an everyday register) | menace_in_bland | none.
6. specific: true only if the bar contains a concrete detail you could check or picture (a named place, price, object, brand, action).
7. flags: explained_joke (the bar explains its own wordplay) | moralising (a lesson or uplift) | cliche (stock travel or rap phrase).
Then for the run: argument (one sentence stating what the whole run is about, or "NONE"), payoff_bar (the index of the bar where the run lands, or null), orphans
(bars that do not serve the argument). Output JSON only."""


def build_messages(bars: list[str], context: Iterable[str] = (), argument: Optional[str] = None) -> list[dict]:
    ctx = list(context)
    parts = []
    if ctx:
        parts.append("CONTEXT (earlier lines of the same verse, not to be judged):\n" + "\n".join(ctx))
    if argument:
        parts.append(f"INTENDED ARGUMENT (the writer's aim; do not assume it succeeded): {argument}")
    parts.append("RUN TO JUDGE:\n" + "\n".join(f"{i}. {b}" for i, b in enumerate(bars, 1)))
    return [{"role": "user", "content": "\n\n".join(parts)}]


def read_run(llm: LLM, bars: list[str], context: Iterable[str] = (), argument: Optional[str] = None,
             model: str = "ds-flash", stage: str = "reader", scope: str = "judge", max_tokens: int = 2500) -> dict:
    res = llm.complete(Request(model=model, system=SYSTEM, messages=build_messages(bars, context, argument), schema=READER_SCHEMA,
                               max_tokens=max_tokens, effort=None, temperature=0.0, stage=stage, scope=scope))
    reading = res.parsed or {}
    reading["_schema_errors"] = res.schema_errors
    reading["_n_bars"] = len(bars)
    reading["_usd"] = res.usd
    return reading


def summarise(reading: dict) -> dict:
    """every number derived in code. Missing/short readings count against the text, never for it."""
    bars = reading.get("bars") or []
    n = reading.get("_n_bars") or len(bars)
    byi = {b.get("i"): b for b in bars if isinstance(b, dict)}
    typed = [byi.get(i + 1) for i in range(n)]
    types = [(t or {}).get("type", "nonsense") for t in typed]
    links = [(t or {}).get("link_to_previous", "none") for t in typed]
    flags = [f for t in typed for f in ((t or {}).get("flags") or [])]
    return {
        "n": n,
        "says_share": sum(1 for t in types if t in SAYS) / n if n else 0.0,
        "dead_bars": [i + 1 for i, t in enumerate(types) if t in DEAD],
        "nonsense_bars": [i + 1 for i, t in enumerate(types) if t == "nonsense"],
        "ungrammatical_bars": [i + 1 for i, t in enumerate(typed) if t and not t.get("grammatical_as_spoken", True)],
        "link_none": sum(1 for i, l in enumerate(links) if l == "none" and i > 0),
        "persona_none": sum(1 for t in typed if (t or {}).get("persona_fit", "none") == "none"),
        "specific_share": (sum(1 for t in typed if (t or {}).get("specific")) / n) if n else 0.0,
        "flags": sorted(set(flags)),
        "argument": (reading.get("run") or {}).get("argument", ""),
        "payoff_bar": (reading.get("run") or {}).get("payoff_bar"),
        "invalid": bool(reading.get("_schema_errors")) or len(bars) != n,
    }


def empty_flags(summary: dict) -> list[str]:
    """the 'fluent but empty' signal, kept SEPARATE from the sense floor: the reader's own flags (cliche, moralising, explained_joke).
    Measured on dev: catches the cliche rewrite, explained-joke and moral-ending degradations (91-100%) with ~13% false alarms."""
    return list(summary.get("flags") or [])


def passes(summary: dict, min_says: float = 0.6, max_link_none: int = 1) -> tuple[bool, list[str]]:
    """the run-level SENSE FLOOR, in code (nonsense / dead bars / not sayable / unlinked). Thresholds are placeholders until
    calibrated on the dev split (plan 5.3/5.5). It deliberately does NOT use flags: see empty_flags."""
    why = []
    if summary["invalid"]:
        why.append("reader output invalid or incomplete")
    if summary["nonsense_bars"]:
        why.append(f"nonsense bars {summary['nonsense_bars']}")
    if summary["says_share"] < min_says:
        why.append(f"only {summary['says_share']:.0%} of bars say or do anything (need {min_says:.0%})")
    if summary["ungrammatical_bars"]:
        why.append(f"not sayable aloud: bars {summary['ungrammatical_bars']}")
    if summary["link_none"] > max_link_none:
        why.append(f"{summary['link_none']} bars unlinked to the previous bar")
    if summary["argument"].strip().upper() in ("", "NONE"):
        why.append("no argument")
    return (not why, why)


def selftest() -> tuple[bool, str]:
    import tempfile
    from pathlib import Path
    from ..llm import Ledger, StubBackend
    problems: list[str] = []
    good = {"bars": [
        {"i": 1, "paraphrase": "Narrator hands a parcel to a courier.", "type": "event", "grammatical_as_spoken": True,
         "link_to_previous": "none", "persona_fit": "deadpan_report", "specific": True},
        {"i": 2, "paraphrase": "He signs for it at the desk.", "type": "event", "grammatical_as_spoken": True,
         "link_to_previous": "cause", "persona_fit": "deadpan_report", "specific": True}],
        "run": {"argument": "A parcel is handled like normal post.", "payoff_bar": 2, "orphans": []}}
    bad = {"bars": [
        {"i": 1, "paraphrase": "NONE", "type": "nonsense", "grammatical_as_spoken": False, "breaking_words": "paid packed gone",
         "link_to_previous": "none", "persona_fit": "none", "specific": False},
        {"i": 2, "paraphrase": "NONE", "type": "filler", "grammatical_as_spoken": True,
         "link_to_previous": "none", "persona_fit": "none", "specific": False}],
        "run": {"argument": "NONE", "payoff_bar": None, "orphans": [1, 2]}}
    import json
    with tempfile.TemporaryDirectory() as td:
        for name, payload, expect in (("good", good, True), ("bad", bad, False)):
            llm = LLM(ledger=Ledger(run_id="rs", persist=False), stub=StubBackend({"reader": lambda r, p=payload: json.dumps(p)}),
                      cache_dir=Path(td) / name)
            rd = read_run(llm, ["a", "b"], model="stub-1")
            ok, why = passes(summarise(rd))
            if ok != expect:
                problems.append(f"{name}: expected pass={expect}, got {ok} {why}")
    short = summarise({"bars": good["bars"][:1], "run": good["run"], "_n_bars": 2})
    if not short["invalid"]:
        problems.append("a reading that omits a bar must be invalid")
    return (not problems, "; ".join(problems) if problems else "good run passes, nonsense/filler run fails, short reading is invalid")
