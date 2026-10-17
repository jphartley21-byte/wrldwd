"""Join read (17 Oct 2026): does each verse section pick up the IDEA the section before it ended on?

Joe: "By pick up, is it just words or ideas. For example in the original [bars 56-57: kicking back in Spoons, then feet up] ... don't
share [a word] but kicking back in spoons and putting your feet up pick up the same idea." Then "Yes": build an idea read at the joins and
fix the V2 opener against it.

WHY. toolkit/cohesion.py counts SURFACE marks at each join between two verse sections: a connective opener or a reused word. Words miss
an idea carried on with no shared word, and a bare connective passes with no idea behind it (Toast of the Town v1, V2 1-8: "So I ride a
Honda from Hanoi" after never finding the Chang).

TWO ABSOLUTE READS FAILED VALIDATION (ds-flash, 17 Oct 2026; counts only): asked "does AFTER follow from BEFORE, or is it a new topic?",
  JOIN1 (2 + 2 bars, strict): the original's real joins 2 of 6 'follows', shuffled joins 2 of 10 'follows', flagged 0 of 3;
  JOIN2 (3 + 3 bars, rap's loose link types spelled out): real 4 of 6, shuffled 6 of 10, flagged 2 of 3 'follows'.
In a travel song any next trip reads as the journey going on, so an absolute question links everything or nothing.

WHAT NOW (JOINFC, forced choice). The question "would AFTER read the same after any other passage" made literal: the model gets the last
three bars before the join and two openings, the real next section and the opening of another verse section of the same song, and is asked
which one comes straight after (or 'neither'). Each pairing is asked in both orders; the real opening wins only when it is chosen both
times. A join faces DISTRACTORS other openings and passes when it wins at least PASS_WINS of them.

VALIDATION (`python -m ww.write.joinread --validate ORIG`, benchmark/join_validation_<model>.json, counts only): the original's real joins
against its own other openings, and the joins in toolkit/tests/join_flagged.txt (our bars) against openings of the current Toast draft.
It passes when at least ORIG_FLOOR of the original's joins pass and every flagged join fails. HARD in `ww gate` only for a model whose
validation passed (then ours must pass at least as many joins as the original did); otherwise every result is a note. The cache is
private (eval/_join_cache.json): validation sends the original's bars to the model and must never put them in the public repo.
WW_JOINREAD=0 switches it off (GATE OFF); WW_JOIN_MODEL picks the model.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

from .. import config

TOOLKIT = config.ROOT / "toolkit"
CACHE = config.EVAL_DIR / "_join_cache.json"
FLAGGED = TOOLKIT / "tests" / "join_flagged.txt"
DRAFT_FOR_DISTRACTORS = config.ROOT / "writing" / "song_toast_of_the_town_v1.md"
WINDOW = (3, 3)        # bars before / after the join (some links land on the third bar)
PROMPT = "JOINFC1"     # in the cache key: a prompt change is a new read, never an old answer
DISTRACTORS = 3
PASS_WINS = 2          # a join passes when the real opening beats at least 2 of its 3 distractors
ORIG_FLOOR = 5         # validation: at least 5 of the original's 6 joins must pass

SYSTEM = """You are a British rap editor. You get the last bars of one section of a rap verse (BEFORE) and the opening bars of two other sections, OPENING 1 and OPENING 2. One of them comes straight after BEFORE in the song; the other comes from somewhere else in the same song.
Say which opening continues BEFORE: it picks up BEFORE's idea or scene, follows from it, answers or reacts to it, turns on it with a contrast or a flashback, or plays on a word or image in it. Judge the ideas: a linking word on its own (so, and, then, now, but) and a shared rhyme sound are not links. If neither opening connects to BEFORE more than the other, say "neither".
Reply with choice ("1", "2" or "neither") and why (at most 15 words). Return JSON only."""

SCHEMA = {"type": "object", "properties": {"choice": {"type": "string"}, "why": {"type": "string"}}, "required": ["choice", "why"]}

_CACHE = None


def model() -> str:
    """ds-flash when DEEPSEEK_API_KEY is set (it runs on Joe's PC); otherwise Claude through the CLI. WW_JOIN_MODEL overrides."""
    m = os.environ.get("WW_JOIN_MODEL")
    if m:
        return m
    return "ds-flash" if config.secret("DEEPSEEK_API_KEY") else "haiku"


def unrunnable(m: str | None = None) -> str | None:
    """why the chosen model cannot run here, or None."""
    from ..llm import pricing
    m = m or model()
    prov = pricing.provider(m)
    if prov == "anthropic" and not shutil.which("claude") and not config.secret("ANTHROPIC_API_KEY"):
        return f"{m}: no `claude` CLI on PATH and no ANTHROPIC_API_KEY"
    if prov == "deepseek" and not config.secret("DEEPSEEK_API_KEY"):
        return f"{m}: no DEEPSEEK_API_KEY"
    return None


def _load() -> dict:
    global _CACHE
    if _CACHE is None:
        try:
            _CACHE = json.loads(CACHE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _CACHE = {}
    return _CACHE


def _save() -> None:
    if _CACHE is None:
        return
    try:
        disk = json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        disk = {}
    _CACHE.update({k: v for k, v in disk.items() if k not in _CACHE})
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(_CACHE, ensure_ascii=False, indent=0), encoding="utf-8")
    os.replace(tmp, CACHE)


def _key(m: str, before: list[str], o1: list[str], o2: list[str]) -> str:
    return f"[{m}] {PROMPT}\n" + "\n".join(before) + "\n|1|\n" + "\n".join(o1) + "\n|2|\n" + "\n".join(o2)


def choice(r: dict) -> str:
    """'1', '2', 'neither' or 'unjudged' from one reply."""
    if not r or "unjudged" in r:
        return "unjudged"
    c = str(r.get("choice", "")).strip().lower().strip('"\' .')
    return c if c in ("1", "2", "neither") else ("1" if c.startswith("1") or c.startswith("opening 1") else
                                                 "2" if c.startswith("2") or c.startswith("opening 2") else
                                                 "neither" if c.startswith("neither") else "unjudged")


def ask(before: list[str], o1: list[str], o2: list[str], llm=None, m: str | None = None) -> dict:
    """one forced-choice read (cached), or {'unjudged': why}."""
    m = m or model()
    c = _load()
    k = _key(m, before, o1, o2)
    if k in c:
        return c[k]
    try:
        from ..llm import LLM, Ledger, Request
        llm = llm or LLM(ledger=Ledger(run_id="joinread"))
        msg = ("BEFORE:\n" + "\n".join(before) + "\n\nOPENING 1:\n" + "\n".join(o1) + "\n\nOPENING 2:\n" + "\n".join(o2))
        res = llm.complete(Request(model=m, system=SYSTEM, messages=[{"role": "user", "content": msg}], schema=SCHEMA, max_tokens=300,
                                   effort=None if m == "ds-flash" else "low", temperature=0.0, stage="joinread", scope="sense"),
                           use_cache=False)
        r = res.parsed or {}
        if choice(r) == "unjudged":
            raise ValueError(f"no choice in the reply: {str(r)[:60]}")
    except Exception as e:  # noqa: BLE001 - a read that did not run is reported as such, never as a pass or a fail
        return {"unjudged": str(e)[:80]}
    c[k] = r
    _save()
    return r


def wins(before: list[str], real: list[str], other: list[str], llm=None, m: str | None = None) -> str:
    """'win' when the real opening is chosen in both orders, 'lose' otherwise, 'unjudged' when a read did not run."""
    a = choice(ask(before, real, other, llm, m))
    b = choice(ask(before, other, real, llm, m))
    if "unjudged" in (a, b):
        return "unjudged"
    return "win" if (a == "1" and b == "2") else "lose"


def _cohesion():
    if str(TOOLKIT) not in sys.path:
        sys.path.insert(0, str(TOOLKIT))
    import cohesion
    return cohesion


def openings(sections: dict) -> dict:
    """{verse slot: its first WINDOW[1] bars}."""
    return {s: sections[s][:WINDOW[1]] for s in _cohesion().VERSE_ORDER if sections.get(s)}


def distractors_for(real: list[str], before_slot: str | None, pool: dict, n: int = DISTRACTORS) -> list[list[str]]:
    """n other openings from the same song, in a fixed order: never the real one and never the section the join leaves."""
    out = [o for s, o in pool.items() if o != real and s != before_slot]
    return out[:n]


def join_result(before: list[str], real: list[str], others: list[list[str]], llm=None, m: str | None = None) -> dict:
    res = [wins(before, real, o, llm, m) for o in others]
    return {"wins": res.count("win"), "n": len(res), "unjudged": res.count("unjudged"),
            "passed": res.count("unjudged") == 0 and res.count("win") >= min(PASS_WINS, len(res))}


def song_results(sections: dict, llm=None, m: str | None = None) -> list[tuple[str, str, dict]]:
    order = [s for s in _cohesion().VERSE_ORDER if sections.get(s)]
    pool = openings(sections)
    return [(a, b, join_result(sections[a][-WINDOW[0]:], pool[b], distractors_for(pool[b], a, pool), llm, m))
            for a, b in zip(order, order[1:])]


def validation(m: str | None = None) -> dict | None:
    p = config.BENCHMARK / f"join_validation_{m or model()}.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def song(sections: dict, llm=None, m: str | None = None) -> dict:
    """{'hard': [...], 'notes': [...], 'off': reason | None}. HARD only for a validated model: ours must pass at least as many joins as
    the original did in validation."""
    m = m or model()
    why = unrunnable(m)
    if why:
        return {"hard": [], "notes": [], "off": why}
    v = validation(m)
    gating = bool(v and v.get("passed"))
    R = song_results(sections, llm, m)
    notes = [f"JOIN {a} > {b}: the real opening beats {r['wins']} of {r['n']} other openings" + (" (pass)" if r["passed"] else " (COLD)")
             for a, b, r in R]
    missed = [f"{a} > {b}" for a, b, r in R if r["unjudged"]]
    hard = []
    if gating and not missed:
        need = v["orig_passed"]
        got = sum(r["passed"] for _, _, r in R)
        if got < need:
            cold = [f"{a} > {b}" for a, b, r in R if not r["passed"]]
            hard.append(f"join read: {got} of {len(R)} section openings are picked out as the real continuation (the original: {need} of "
                        f"{v['orig_joins']}). Cold: {', '.join(cold)}. Make the opening pick up the IDEA the section before ends on "
                        f"(carry it on, a consequence, a reaction, a contrast or a pun on a word in it): another section's opening must not fit as well")
    if not gating:
        notes.append(f"join read is NOT validated for {m} (python -m ww.write.joinread --validate ORIG): report only")
    return {"hard": hard, "notes": notes, "off": f"did not run for {', '.join(missed)}" if missed else None}


def flagged(path=FLAGGED) -> list[tuple[str, list[str], list[str]]]:
    """(case, before bars, after bars) from 'case | before bar / before bar | after bar / after bar | note' lines."""
    out = []
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="utf-8"):
        if l.strip() and not l.startswith("#"):
            case, before, after = [x.strip() for x in l.split("|")[:3]]
            out.append((case, [b.strip() for b in before.split(" / ")], [b.strip() for b in after.split(" / ")]))
    return out


def validate(orig_path: str, llm=None, m: str | None = None) -> dict:
    """the original's joins against its own other openings; the flagged joins against openings of the current Toast draft."""
    m = m or model()
    S = _cohesion().sections_of_original(orig_path)
    orig = [r["passed"] for _, _, r in song_results(S, llm, m)]
    if str(TOOLKIT) not in sys.path:
        sys.path.insert(0, str(TOOLKIT))
    import fitbar
    D, _ = fitbar.read_draft(str(DRAFT_FOR_DISTRACTORS), with_cash=True)
    pool = openings(D)
    flag = []
    for case, before, after in flagged():
        others = [o for o in pool.values() if o[:1] != after[:1] and o[:1] != before[-1:]][:DISTRACTORS]
        flag.append(join_result(before, after, others, llm, m))
    res = {"_note": "Join read validation, forced choice (counts only, rule 4): each join's real opening against other openings of the "
                    f"same song, asked in both orders; a join passes on {PASS_WINS} wins of {DISTRACTORS}. Built by python -m ww.write.joinread --validate.",
           "model": m, "prompt": PROMPT, "orig_joins": len(orig), "orig_passed": sum(orig), "orig_verdicts": orig,
           "flagged": len(flag), "flagged_failed": sum(not r["passed"] for r in flag),
           "flagged_wins": [r["wins"] for r in flag],
           "unjudged": sum(1 for r in flag if r["unjudged"])}
    res["passed"] = res["unjudged"] == 0 and res["orig_passed"] >= ORIG_FLOOR and res["flagged_failed"] == res["flagged"]
    (config.BENCHMARK / f"join_validation_{m}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


def selftest() -> tuple[bool, str]:
    """offline parts: the choice parser, the cache key, the flagged file, the distractor pool."""
    pool = {"V1 1-8": ["a"], "V1 9-16": ["b"], "V1 17-24": ["c"], "V1 25-32": ["d"]}
    ok = [choice({"choice": "1"}) == "1", choice({"choice": "Opening 2"}) == "2", choice({"choice": "Neither"}) == "neither",
          choice({"unjudged": "x"}) == "unjudged", choice({}) == "unjudged",
          _key("m", ["a"], ["b"], ["c"]) != _key("m", ["a"], ["c"], ["b"]), len(flagged()) >= 3,
          distractors_for(["b"], "V1 1-8", pool) == [["c"], ["d"]]]
    return all(ok), f"joinread selftest: {sum(ok)} of {len(ok)} offline checks"


def main(argv=None) -> int:
    a = argv if argv is not None else sys.argv[1:]
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a and a[0] == "--selftest":
        good, msg = selftest()
        print(msg + (" PASSED" if good else " FAILED"))
        return 0 if good else 1
    if a and a[0] == "--validate":
        r = validate(a[1])
        print({k: v for k, v in r.items() if k != "_note"})
        print("JOIN READ VALIDATION: " + ("PASSED" if r["passed"] else "FAILED"))
        return 0 if r["passed"] else 1
    if str(TOOLKIT) not in sys.path:
        sys.path.insert(0, str(TOOLKIT))
    import fitbar
    D, _ = fitbar.read_draft(a[0], with_cash=True)
    r = song(D)
    for n in r["notes"]:
        print("  " + n)
    for h in r["hard"]:
        print("x " + h)
    if r["off"]:
        print("JOIN READ OFF: " + r["off"])
    print("JOIN READ: " + ("PASS" if not r["hard"] and not r["off"] else "FAIL" if r["hard"] else "NOT RUN"))
    return 0 if not r["hard"] else 1


if __name__ == "__main__":
    sys.exit(main())
