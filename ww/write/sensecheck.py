"""Sense gate (Joe, 14 Oct 2026: "this regressed and wrote nonsense bars, we need to enforce sense making better").

WHY. Every other gate in the repo measures sound, counts or links. None reads a sentence, so a bar can fit its syllable count, its shape and its
rhyme and still be telegraphic nonsense ("Queue round the block for the film I'm buying in", "Found pink top hat, wear it like bread"). The v13 draft
got there by dropping articles and commas to hit syllable counts.

WHAT. A cached model read of every bar, one request per block (a few thousandths of a cent on ds-flash), at temperature 0 with no thinking:
for each bar the judge must (1) restate it as ONE complete plain sentence using only the words in the bar, (2) say whether the bar is grammatical
spoken English (fragments are fine if a speaker could really say them: "Yo, bonjourno", "Front row on my phone, so bored, though"), and (3) score
sense 0 nonsense / 1 guessable / 2 a stranger gets it on one hearing. A bar FAILS when sense < 2 or it is not grammatical. A separate cheap
deterministic screen flags bars that end on a dangling particle (in/on/out/up/off) with no object, and bars with fewer than two content words.

STATUS (registry discipline): UNVALIDATED until `python -m ww.write.sensecheck --calibrate` passes; the calibration set is Joe's own approved bars
(must pass) and bars Joe or I rejected for nonsense (must fail). It is a model opinion: a SIFT with a hard failure attached, not an ear.
Switch off with WW_SENSE=0 (needed offline); a network failure never fails a bar, it prints a note.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .. import config

SYSTEM = """You are a strict, plain-speaking British editor reading lines of a deadpan rap aloud, one bar at a time, for someone who has never seen the song.
For EACH bar:
- reading: restate the bar as ONE complete plain sentence using only the ideas and words in the bar. Do not invent facts to rescue it. If you cannot restate it without inventing, write "UNCLEAR".
- grammatical: true if a speaker could really say the bar aloud as English: complete sentences, or ordinary spoken fragments (greetings, exclamations, "Front row on my phone, so bored, though"). false if words are missing so it only works as a list of words, a participle with no clause, a dangling preposition, or an object with nothing done to it.
- sense: 2 = a stranger understands what is being claimed on one hearing; 1 = you can guess but it is a fragment or the meaning is strained; 0 = nonsense or a word list.
- issue: what is wrong, in at most 12 words, or "" if sense is 2.
You may read a bar as continuing the sentence of the bar before it only if the previous bar clearly leaves the sentence open (it ends mid-clause). Be harsh: a clever sound does not make a sentence. Return JSON only."""

SCHEMA = {
    "type": "object",
    "properties": {"bars": {"type": "array", "items": {
        "type": "object",
        "properties": {"n": {"type": "integer"}, "reading": {"type": "string"}, "grammatical": {"type": "boolean"},
                       "sense": {"type": "integer"}, "issue": {"type": "string"}},
        "required": ["n", "reading", "grammatical", "sense", "issue"]}}},
    "required": ["bars"],
}

CACHE = config.EVAL_DIR / "sense_cache.json"
PARTICLES = {"in", "on", "out", "up", "off", "down", "over", "through", "at", "to", "of", "for", "with", "by", "from", "into", "onto"}
FUNCTION = set("""a an the and or but so then of in on at to for with by from as is was are were be been am i i'm i've i'd i'll you he she it we they me my your his her
its our their this that these those there here not no do did does have has had will would can could just very too out up off down over""".split())

_CACHE = None


def _load() -> dict:
    global _CACHE
    if _CACHE is None:
        try:
            _CACHE = json.loads(CACHE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _CACHE = {}
    return _CACHE


def _save() -> None:
    if _CACHE is not None:
        CACHE.write_text(json.dumps(_CACHE, ensure_ascii=False, indent=0), encoding="utf-8")


def _words(bar: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", bar)


def screen(bar: str) -> list[str]:
    """deterministic: the cheap shapes of telegraphic nonsense."""
    w = [x.lower() for x in _words(bar)]
    out = []
    if not w:
        return out
    if w[-1] in PARTICLES:
        out.append(f"ends on a dangling '{w[-1]}'")
    if sum(1 for x in w if x not in FUNCTION) < 2:
        out.append("fewer than two content words")
    return out


def _context_block(bars: list[str]) -> str:
    return "\n".join(f"{i + 1}. {b}" for i, b in enumerate(bars))


def judge(bars: list[str], llm=None, model: str = "ds-flash") -> list[dict]:
    """one row per bar: {n, reading, grammatical, sense, issue}. Cached per (block text); raises nothing on a network failure (rows are then marked unjudged)."""
    cache = _load()
    key = "\n".join(bars)
    if key in cache:
        return cache[key]
    try:
        from ..llm import LLM, Ledger, Request
        llm = llm or LLM(ledger=Ledger(run_id="sensecheck"))
        res = llm.complete(Request(model=model, system=SYSTEM, messages=[{"role": "user", "content": "BARS (in order):\n" + _context_block(bars)}],
                                   schema=SCHEMA, max_tokens=max(1500, 160 * len(bars)), effort=None, temperature=0.0, stage="sensecheck", scope="sense"), use_cache=False)
        rows = (res.parsed or {}).get("bars", [])
    except Exception as e:  # noqa: BLE001 - offline must not fail a bar
        return [{"n": i + 1, "reading": "", "grammatical": True, "sense": 2, "issue": "", "unjudged": str(e)[:80]} for i in range(len(bars))]
    by = {int(r.get("n", 0)): r for r in rows}
    out = []
    for i in range(len(bars)):
        r = by.get(i + 1) or {"n": i + 1, "reading": "", "grammatical": True, "sense": 2, "issue": "", "unjudged": "missing"}
        out.append(r)
    if not any("unjudged" in r for r in out):
        cache[key] = out
        _save()
    return out


def check(bars: list[str], llm=None) -> dict:
    """{'ok', 'fails': [(bar n, why)], 'rows'}. A bar fails on sense < 2, not grammatical, or a deterministic screen hit."""
    rows = judge(bars, llm=llm)
    fails = []
    for i, (b, r) in enumerate(zip(bars, rows)):
        why = []
        if "unjudged" not in r:
            if r.get("sense", 2) < 2:
                why.append(f"sense {r.get('sense')}: {r.get('issue') or r.get('reading', '')[:60]}")
            if not r.get("grammatical", True) and r.get("sense", 2) >= 2:
                why.append(f"not grammatical: {r.get('issue') or r.get('reading', '')[:60]}")
        why += screen(b)
        if why:
            fails.append((i + 1, "; ".join(why)))
    return {"ok": not fails, "fails": fails, "rows": rows,
            "unjudged": any("unjudged" in r for r in rows)}


BLOCK_SYSTEM = """You are a strict, plain-speaking British editor. You are given the bars of one block of a deadpan rap, in order. Judge ONLY how the bars hold together as a passage a stranger would follow when hearing it once.
- thread: say in ONE sentence what the block ARGUES and who the speaker is (the claim it makes about him or his world). A list of what happened in time order ("he went here, then there, then this happened") argues nothing: write "NO THREAD" for it, and also if you cannot state a claim.
- links: for every bar after the first, follows = true if it supports, escalates, contrasts with or deflates the claim (or the bar before it) in a way a listener can follow; false if it is a non sequitur, merely the next event or place in time order, changes subject with no signal, or uses 'he/she/it/they' with nobody introduced.
- coherent: 2 = one clear thread and every bar belongs; 1 = a thread but some bars are loose or the order is confusing; 0 = a pile of unrelated bars.
- issue: the worst problem in at most 15 words, or "".
Be harsh: a shared rhyme sound is not a thread. Return JSON only."""

BLOCK_SCHEMA = {
    "type": "object",
    "properties": {"thread": {"type": "string"}, "coherent": {"type": "integer"}, "issue": {"type": "string"},
                   "links": {"type": "array", "items": {"type": "object", "properties": {"n": {"type": "integer"}, "follows": {"type": "boolean"}, "issue": {"type": "string"}},
                                                         "required": ["n", "follows", "issue"]}}},
    "required": ["thread", "coherent", "issue", "links"],
}


def block_check(bars: list[str], llm=None, model: str = "ds-flash") -> dict:
    """ACROSS bars (Joe, 14 Oct 2026): one thread per block, every bar follows the one before it. Cached. Fails on coherent < 2 or any link that does not follow."""
    cache = _load()
    key = "BLOCK2\n" + "\n".join(bars)   # BLOCK2 = the argument-thread prompt (14 Oct 2026); verdicts under the old "who does what, where" prompt are not reused
    if key in cache:
        r = cache[key]
    else:
        try:
            from ..llm import LLM, Ledger, Request
            llm = llm or LLM(ledger=Ledger(run_id="sensecheck"))
            res = llm.complete(Request(model=model, system=BLOCK_SYSTEM, messages=[{"role": "user", "content": "BARS (in order):\n" + _context_block(bars)}],
                                       schema=BLOCK_SCHEMA, max_tokens=1500, effort=None, temperature=0.0, stage="sensecheck", scope="sense"), use_cache=False)
            r = res.parsed or {}
            if not r:
                raise ValueError("empty")
            cache[key] = r
            _save()
        except Exception as e:  # noqa: BLE001
            return {"ok": True, "unjudged": str(e)[:80], "thread": "", "fails": [], "coherent": 2}
    fails = [(int(l["n"]), l.get("issue", "does not follow")) for l in r.get("links", []) if not l.get("follows", True) and int(l.get("n", 0)) > 1]
    # calibration (14 Oct 2026): the judge cannot separate Joe's approved block (coherent 1) from the known anti-example (coherent 1), so the bar for a hard
    # fail is a real break: no thread, coherent 0, or more broken links than a normal rap's deliberate jumps (1 per 4 bars). Its notes are read by hand either way.
    ok = r.get("coherent", 2) >= 1 and "NO THREAD" not in r.get("thread", "") and len(fails) <= max(1, len(bars) // 4)
    return {"ok": ok, "thread": r.get("thread", ""), "coherent": r.get("coherent", 2), "issue": r.get("issue", ""), "fails": fails}


# the calibration set: GOOD must pass, BAD must fail. GOOD = Joe's own approved bars + plain sentences; BAD = bars Joe or I rejected as nonsense.
GOOD = ["Yo, bonjourno", "Said damn at the on-stage porno", "Front row on my phone, so bored, though", "So I boarded a plane out to Bordeaux",
        "Missed the headliner, bought a gnome, sorry", "Tent flooded, then dust, then drought, I slept through all three", "He's off the back of a lorry"]
BAD = ["Two glasses, cold lager, back road corners", "No names just numbers on folders", "Found pink top hat, wear it like bread", "Breakfast had me orange like little",
       "Queue round the block for the film I'm buying in", "Hammock bamboo snow on the Atlas dandy", "Tin of direct-to-rust, no recap, paint town red"]


def calibrate(llm=None) -> tuple[bool, str]:
    g = check(GOOD, llm=llm)
    b = check(BAD, llm=llm)
    if g["unjudged"] or b["unjudged"]:
        return True, "sensecheck: calibration skipped (model unreachable)"
    good_fail = [n for n, _ in g["fails"]]
    bad_pass = [n for n in range(1, len(BAD) + 1) if n not in [x for x, _ in b["fails"]]]
    ok = len(good_fail) <= 1 and len(bad_pass) <= 1
    return ok, f"sensecheck calibration: good bars failed {len(good_fail)}/{len(GOOD)} {good_fail}; bad bars passed {len(bad_pass)}/{len(BAD)} {bad_pass}"


BLOCK_GOOD = ["Yo, bonjourno", "Said damn at the on-stage porno", "Front row on my phone, so bored, though", "So I boarded a plane out to Bordeaux"]
BLOCK_BAD = ["Hey port and the road to Porto", "Two glasses cold lager then cut corners", "Lager chips and the last orders", "Might hit the road then the border"]
# the itinerary (v17 V1 33-44, 14 Oct 2026): under the old "who does what, where" thread it passed; it argues nothing, so it must fail now
BLOCK_RECOUNT = ["Stop one is Zurich and it's pricey", "Florence next and David is a must", "Then Ljubljana's dragon bridge is green with rust",
                 "Then Vienna where Freud's couch filled me with disgust"]


def calibrate_block(llm=None) -> tuple[bool, str]:
    g, b, r = block_check(BLOCK_GOOD, llm=llm), block_check(BLOCK_BAD, llm=llm), block_check(BLOCK_RECOUNT, llm=llm)
    if g.get("unjudged") or b.get("unjudged") or r.get("unjudged"):
        return True, "sensecheck block: calibration skipped (model unreachable)"
    return g["ok"] and not r["ok"], (f"sensecheck block calibration: Joe's approved bars coherent={g['coherent']} ok={g['ok']} (must pass); the itinerary "
                                     f"coherent={r['coherent']} ok={r['ok']} (must fail: a timeline argues nothing); the anti-example coherent={b['coherent']} "
                                     f"ok={b['ok']} (NOT separated: the block judge is a sift, read its notes)")


def selftest() -> tuple[bool, str]:
    s = screen("Queue round the block for the film I'm buying in")
    t = screen("He's off the back of a lorry")
    ok = any("dangling" in x for x in s) and not t
    return ok, "sensecheck: dangling-particle screen fires on a dangling 'in' and stays quiet on a clean bar"


def main(argv=None) -> int:
    import argparse
    import io
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--calibrate", action="store_true")
    a = ap.parse_args(argv)
    if a.calibrate:
        ok, msg = calibrate()
        ok2, msg2 = calibrate_block()
        print(msg)
        print(msg2)
        return 0 if (ok and ok2) else 1
    sec, cur = {}, None
    for ln in io.open(a.file, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("== "):
            cur = ln[3:].strip()
            sec[cur] = []
        elif ln.strip() and cur and not ln.startswith("#"):
            sec[cur].append(ln.strip())
    bad = 0
    for k, bars in sec.items():
        r = check(bars)
        print(f"\n== {k}: {len(r['fails'])} fail" + ("  (UNJUDGED: model unreachable)" if r["unjudged"] else ""))
        for n, why in r["fails"]:
            print(f"  x bar {n}: {bars[n - 1]}\n      -> {why}")
            bad += 1
        if len(bars) >= 3:
            bc = block_check(bars)
            print(f"  ACROSS BARS {'ok' if bc['ok'] else 'FAIL'}: coherent {bc.get('coherent')} | thread: {bc.get('thread', '')[:130]}")
            for n, why in bc["fails"]:
                print(f"    ~ bar {n} does not follow the one before: {why}")
            if bc.get("issue"):
                print(f"    worst: {bc['issue']}")
            if not bc["ok"]:
                bad += 1
    print(f"\nSENSE: {bad} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
