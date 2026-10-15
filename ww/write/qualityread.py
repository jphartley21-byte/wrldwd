"""Quality reader (Joe, 15 Oct 2026: "Do we have any gates that check quality? Character Consistency? Bars that hit on first listen
vs multiple listens? Bars that are forced or don't make sense? Scoring on cleverness?" and "Why do I need an API key? I should be
able to use claude too").

WHY. Every hard gate measures sound, counts or links. None asks whether a bar is any good. The rubric's quality items (28 layers
that reward a rewind, 35 plain beats clever, 38 wordplay, 40 character carried by words alone) were HUMAN-only.

WHAT. Claude reads one section per call (the logged-in `claude` CLI, no API key: ww/llm/client.py ClaudeCLIBackend) and marks
every bar:
  first_listen 0-2  a stranger gets the claim (and the joke, if any) on one hearing at rap speed
  rewind       0-2  a second reading a relisten finds (idiom made literal, pun, double meaning, hidden arithmetic)
  forced       the word or phrase a speaker would not say, picked for the rhyme or the syllable count ("" = none)
  in_character 0-2  against the narrator card (brief/persona.md, with the authoring notes stripped)
  clever       0-2  a turn a rap fan would quote
One more call reads the whole song for CHARACTER CONSISTENCY: bars that contradict each other, each pair named.
The reader is never told who wrote the bars, and the section's argument line is NOT sent (the original has none, and a listener
does not get one), so our marks and the original's par come from the same prompt.

STATUS (registry discipline): REPORT-ONLY. The par is the original's slot means (benchmark/quality_par_<model>.json, numbers only, built by
`python -m ww.calib.quality_par`). An axis becomes HARD only when it agrees with Joe's own marks (writing/quality_labels.md)
on at least 75% of bars. Until then `ww gate` prints the marks as notes.

  python -m ww.write.qualityread FILE            read every section (cached by text hash) and the character call
  python -m ww.write.qualityread FILE --cached   print cached reads only, never call the model
  python -m ww.write.qualityread --negatives     Joe's complaints swapped into the song: do they score below par?
  python -m ww.write.qualityread FILE --labels   write writing/quality_labels.md (Joe's sheet)
  python -m ww.write.qualityread --agree         Joe's filled sheet vs Claude, per axis (HARD needs >= 75% on >= 20 bars)
  python -m ww.write.qualityread FILE --targets  "match the original" per section + character 2/2 (report-only; exit 1 on a miss)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from pathlib import Path
from typing import Optional

from .. import config

PROMPT_VERSION = "q1"
MODEL = os.environ.get("WW_QUALITY_MODEL", "haiku")
RUNS = int(os.environ.get("WW_QUALITY_RUNS", "2"))
AXES = ("first_listen", "rewind", "in_character", "clever")
CACHE = config.EVAL_DIR / "quality_cache.json"
PAR = config.ROOT / "benchmark" / f"quality_par_{MODEL}.json"   # one par per reader model

SYSTEM = """You are a sharp, unsentimental UK rap A&R listening to one section of a deadpan British comedy rap. You hear each bar once at rap speed, then you may relisten.
Mark EVERY bar on its own merits, in the context of the bars around it:
- first_listen: 2 = a stranger gets what is claimed (and the joke, if there is one) on ONE hearing; 1 = they get it after a beat, or only half; 0 = lost: word salad, missing words, or a reference nobody can place.
- rewind: 2 = a relisten finds a second layer that lands (an idiom taken literally, a pun, a double meaning, a hidden sum, a callback); 1 = a small extra (a nod, a sly word); 0 = nothing beyond the surface. Most bars are 0.
- forced: the exact word or short phrase a real speaker would NOT say there, chosen only to make the rhyme or fill the syllables (padding, odd word order, the wrong word, a filler tag like "okay" or "and I'll try"). "" if nothing is forced. Quote it from the bar.
- in_character: 2 = only this narrator would say it, in his voice; 1 = fits but anyone could say it; 0 = breaks the character.
- clever: 2 = a line a rap fan would quote back; 1 = neat; 0 = flat.
- note: the single biggest problem or strength, at most 12 words.
Be harsh and specific. A rhyme alone is not clever. A list of places is not a joke. Return JSON only."""

NO_CARD = "THE NARRATOR: judge in_character against the narrator these bars themselves establish."

SCHEMA = {
    "type": "object",
    "properties": {"bars": {"type": "array", "items": {
        "type": "object",
        "properties": {"n": {"type": "integer"}, "first_listen": {"type": "integer"}, "rewind": {"type": "integer"},
                       "forced": {"type": "string"}, "in_character": {"type": "integer"}, "clever": {"type": "integer"},
                       "note": {"type": "string"}},
        "required": ["n", "first_listen", "rewind", "forced", "in_character", "clever", "note"]}}},
    "required": ["bars"],
}

CHAR_SYSTEM = """You are a script editor checking one rap song for CHARACTER CONSISTENCY. The narrator is one person. You get every bar, numbered, by section.
- contradictions: every pair of bars where the narrator contradicts himself in a way a listener would notice and that is not a deliberate joke or a boast-then-deflation (e.g. broke in one bar and paying for everything in the next with no turn; a lone wolf who works with a crew; a fact about him that changes). Name both bar numbers and say why in at most 15 words.
- off_card: bars where he does something the narrator card says he never does (only when a card is given), with why in at most 12 words.
- consistent: 2 = one clear person throughout; 1 = mostly, with slips; 0 = several people.
Be strict but fair: rap persona exaggerates, and exaggeration is not contradiction. Return JSON only."""

CHAR_SCHEMA = {
    "type": "object",
    "properties": {"consistent": {"type": "integer"},
                   "contradictions": {"type": "array", "items": {"type": "object", "properties": {
                       "a": {"type": "integer"}, "b": {"type": "integer"}, "why": {"type": "string"}}, "required": ["a", "b", "why"]}},
                   "off_card": {"type": "array", "items": {"type": "object", "properties": {
                       "bar": {"type": "integer"}, "why": {"type": "string"}}, "required": ["bar", "why"]}}},
    "required": ["consistent", "contradictions", "off_card"],
}

_CACHE: Optional[dict] = None
_LOCK = threading.Lock()   # sections are read in parallel; one writer at a time


def _load() -> dict:
    """under the lock: five threads starting at once each loaded their own copy, and four sections' reads were lost (15 Oct)."""
    global _CACHE
    with _LOCK:
        if _CACHE is None:
            try:
                _CACHE = json.loads(CACHE.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                _CACHE = {}
        return _CACHE


def _save() -> None:
    """merge with what is on disk first: two processes reading at once (the song and --negatives, 15 Oct) each wrote their own copy
    and the later one wiped the other's reads."""
    if _CACHE is not None:
        with _LOCK:
            try:
                disk = json.loads(CACHE.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                disk = {}
            _CACHE.update({k: v for k, v in disk.items() if k not in _CACHE})
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            tmp = CACHE.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_text(json.dumps(_CACHE, ensure_ascii=False, indent=0), encoding="utf-8")
            os.replace(tmp, CACHE)


def card() -> str:
    """brief/persona.md as the reader sees it: the narrator only. Authoring notes (who wrote it, rule numbers, file paths, the
    flagged-embellishment list) are stripped so the reader cannot tell who wrote the bars."""
    try:
        txt = (config.ROOT / "brief" / "persona.md").read_text(encoding="utf-8")
    except OSError:
        return NO_CARD
    keep, on = [], False
    for ln in txt.splitlines():
        if ln.startswith("## "):
            on = not any(k in ln for k in ("Flagged", "Recurring"))
            if on:
                keep.append(re.sub(r"\s*\([^)]*(?:material/|\.md)[^)]*\)", "", ln))
            continue
        if on and ln.strip() and not re.search(r"Joe|Assistant|rule \d|material/|persona\)|evolve\.|\.md|\.py", ln):
            keep.append(ln)
    return "THE NARRATOR CARD:\n" + "\n".join(keep) if keep else NO_CARD


def _key(*parts) -> str:
    return hashlib.sha256(json.dumps([PROMPT_VERSION, MODEL, *parts], ensure_ascii=False).encode("utf-8")).hexdigest()


def _user(slot: str, bars: list[str], narrator: str) -> str:
    return (f"{narrator}\n\nSECTION: {slot} of the song.\nBARS (in order):\n" + "\n".join(f"{i + 1}. {b}" for i, b in enumerate(bars)))


def _one_read(slot: str, bars: list[str], llm, narrator: str) -> Optional[list[dict]]:
    """one model read; None when the reply is missing a bar (retried once by the caller)."""
    from ..llm import Request
    res = llm.complete(Request(model=MODEL, system=SYSTEM, messages=[{"role": "user", "content": _user(slot, bars, narrator)}],
                               schema=SCHEMA, max_tokens=300 + 140 * len(bars), effort="low", stage="qualityread", scope="quality"),
                       use_cache=False)
    by = {}
    for r in (res.parsed or {}).get("bars", []):
        try:
            by[int(r.get("n", 0))] = r
        except (TypeError, ValueError):
            continue
    if any(i + 1 not in by for i in range(len(bars))):
        return None
    rows = []
    for i in range(len(bars)):
        r = dict(by[i + 1])
        for a in AXES:
            r[a] = max(0, min(2, int(r.get(a, 0) or 0)))
        r["forced"] = (r.get("forced") or "").strip().strip('"')
        rows.append(r)
    return rows


def read_section(slot: str, bars: list[str], llm=None, narrator: Optional[str] = None, cached_only: bool = False,
                 store: bool = True, runs: int = RUNS) -> Optional[list[dict]]:
    """one row per bar, the mean of `runs` reads (one read moves a mark by a point now and then: 15 Oct, "Cross my Noord" read
    first_listen 1 then 0). Row: the AXES as floats, forced (the word most often named, or ""), forced_rate (share of reads naming
    one), note. None when cached_only and not cached. store=False (the original, via ww.calib) caches nothing."""
    narrator = narrator if narrator is not None else card()
    key = _key("sec", slot, narrator, bars, runs)
    cache = _load()
    if store and key in cache:
        return cache[key]
    if cached_only:
        return None
    from ..llm import LLM, Ledger
    llm = llm or LLM(ledger=Ledger(run_id="qualityread"))
    reads = []
    for _ in range(runs):
        rd = _one_read(slot, bars, llm, narrator) or _one_read(slot, bars, llm, narrator)
        if rd is not None:
            reads.append(rd)
    if not reads:
        raise RuntimeError(f"quality read of {slot} came back without every bar, twice")
    rows = []
    for i in range(len(bars)):
        per = [rd[i] for rd in reads]
        named = [x["forced"] for x in per if x["forced"]]
        row = {"n": i + 1, **{a: round(sum(x[a] for x in per) / len(per), 2) for a in AXES},
               "forced": max(set(named), key=named.count) if named else "", "forced_rate": round(len(named) / len(per), 2),
               "note": per[0].get("note", ""), "reads": len(per)}
        rows.append(row)
    if store and len(reads) == runs:
        with _LOCK:
            cache[key] = rows
        _save()
    return rows


def read_character(sections: dict, llm=None, narrator: Optional[str] = None, cached_only: bool = False,
                   store: bool = True) -> Optional[dict]:
    """the song-level character read. sections = {slot: [bars]}; bars are numbered 1..N across the song."""
    narrator = narrator if narrator is not None else card()
    lines, n = [], 0
    for slot, bars in sections.items():
        lines.append(f"[{slot}]")
        for b in bars:
            n += 1
            lines.append(f"{n}. {b}")
    key = _key("char", narrator, lines)
    cache = _load()
    if store and key in cache:
        return cache[key]
    if cached_only:
        return None
    from ..llm import LLM, Ledger, Request
    llm = llm or LLM(ledger=Ledger(run_id="qualityread"))
    res = llm.complete(Request(model=MODEL, system=CHAR_SYSTEM, messages=[{"role": "user", "content": narrator + "\n\nTHE SONG:\n" + "\n".join(lines)}],
                               schema=CHAR_SCHEMA, max_tokens=1500, effort="low", stage="qualityread:char", scope="quality"), use_cache=False)
    r = res.parsed or {}
    if store and r:
        with _LOCK:
            cache[key] = r
        _save()
    return r


def section_means(rows: list[dict]) -> dict:
    n = max(1, len(rows))
    m = {a: round(sum(r[a] for r in rows) / n, 2) for a in AXES}
    m["forced"] = round(sum(r.get("forced_rate", float(bool(r.get("forced")))) for r in rows) / n, 2)
    return m


def par() -> dict:
    try:
        return json.loads(PAR.read_text(encoding="utf-8")).get("slots", {})
    except (OSError, ValueError):
        return {}


def below_par(slot: str, row: dict) -> list[str]:
    """the axes on which one bar sits below the original's slot mean (forced: a named word where the original's slot forces <50%)."""
    p = par().get(slot)
    if not p:
        return []
    out = [a for a in ("first_listen", "rewind", "clever") if row[a] < p[a] - 0.5]
    if row.get("forced_rate", float(bool(row.get("forced")))) >= 0.5 and p.get("forced", 0) < 0.5:
        out.append("forced")
    return out


def _read_file(path: str) -> dict:
    import sys
    sys.path.insert(0, str(config.ROOT / "toolkit"))
    import fitbar
    D = fitbar.read_draft(path)
    return {s: D[s] for s in fitbar.SLOTS if D.get(s)}


def read_file(path: str, cached_only: bool = False, workers: int = 5) -> dict:
    """{'sections': {slot: rows or None}, 'character': dict or None, 'unread': [slots]} - sections read in parallel."""
    from concurrent.futures import ThreadPoolExecutor
    secs = _read_file(path)
    narrator = card()
    out: dict = {}
    if cached_only:
        out = {s: read_section(s, b, narrator=narrator, cached_only=True) for s, b in secs.items()}
    else:
        from ..llm import LLM, Ledger
        llm = LLM(ledger=Ledger(run_id="qualityread"))
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {s: ex.submit(read_section, s, b, llm, narrator) for s, b in secs.items()}
            fut_c = ex.submit(read_character, secs, llm, narrator) if len(secs) >= 5 else None
            for s, f in futs.items():
                try:
                    out[s] = f.result()
                except Exception as e:  # noqa: BLE001 - a failed read is reported, never a pass
                    out[s] = {"error": str(e)[:120]}
            try:
                char = fut_c.result() if fut_c else None
            except Exception as e:  # noqa: BLE001
                char = {"error": str(e)[:120]}
    if cached_only:
        char = read_character(secs, narrator=narrator, cached_only=True) if len(secs) >= 5 else None
    return {"bars": secs, "sections": out, "character": char,
            "unread": [s for s, r in out.items() if r is None or isinstance(r, dict)]}


def notes(r: dict) -> dict:
    """{slot: [note lines]} for ww gate (report-only), plus '_song' for the character read and '_unread'."""
    P = par()
    out: dict = {}
    for s, rows in r["sections"].items():
        if not isinstance(rows, list):
            continue
        m = section_means(rows)
        p = P.get(s)
        head = "QUALITY " + " ".join(f"{a.split('_')[0]} {m[a]:.1f}" + (f"/{p[a]:.1f}" if p else "") for a in ("first_listen", "rewind", "clever")) \
            + f" forced {m['forced']:.0%}" + (f"/{p['forced']:.0%}" if p else "") + f" char {m['in_character']:.1f}" + ("  (ours/original par)" if p else "  (no par yet)")
        L = [head]
        for i, row in enumerate(rows):
            flags = below_par(s, row) if p else [a for a in ("first_listen",) if row[a] == 0] + (["forced"] if row.get("forced") else [])
            if row["in_character"] == 0:
                flags.append("in_character 0")
            if flags:
                L.append(f"QUALITY bar {i + 1}: " + ", ".join(flags) + (f" ('{row['forced']}')" if row.get("forced") else "")
                         + f": {row.get('note', '')[:90]}")
        out[s] = L
    c = r.get("character")
    if isinstance(c, dict) and "consistent" in c:
        out["_song"] = [f"CHARACTER consistent {c['consistent']}/2"] + \
            [f"CHARACTER bars {x['a']} vs {x['b']}: {x['why'][:100]}" for x in c.get("contradictions", [])] + \
            [f"CHARACTER bar {x['bar']} off card: {x['why'][:100]}" for x in c.get("off_card", [])]
    P_ok = {s: section_targets(rows, P.get(s)) for s, rows in r["sections"].items() if isinstance(rows, list)}
    if P_ok:
        cs = c.get("consistent", "?") if isinstance(c, dict) else "?"
        out.setdefault("_song", []).insert(0, f"TARGETS (match the original): {sum(1 for v in P_ok.values() if not v)}/{len(P_ok)} sections, "
                                               f"character {cs}/2 (python -m ww.write.qualityread FILE --targets)")
    if r.get("unread"):
        out["_unread"] = r["unread"]
    return out


TARGET_AXES = ("first_listen", "rewind", "clever")


def section_targets(rows: list[dict], p: Optional[dict]) -> list[str]:
    """what a section misses against "match the original" (Joe, 15 Oct 2026, for draft v2): first_listen / rewind / clever means at or
    above the original's slot means, forced rate at or below the original's, and no bar at first_listen 0 or in_character 0.
    [] = met. Without a par only the per-bar floors apply. REPORT-ONLY: these marks did not separate Joe's rejected bars."""
    m = section_means(rows)
    miss = []
    if p:
        miss += [f"{a} {m[a]:.2f} < {p[a]:.2f}" for a in TARGET_AXES if m[a] < p[a] - 1e-9]
        if m["forced"] > p["forced"] + 1e-9:
            miss.append(f"forced {m['forced']:.0%} > {p['forced']:.0%}")
    miss += [f"bar {i + 1} first_listen 0" for i, r in enumerate(rows) if r["first_listen"] == 0]
    miss += [f"bar {i + 1} in_character 0" for i, r in enumerate(rows) if r["in_character"] == 0]
    return miss


def targets(path: str, cached_only: bool = False) -> dict:
    """{'sections': {slot: [misses]}, 'character': read, 'character_ok', 'met', 'ok'}; character_ok = consistent 2/2, no contradictions."""
    r = read_file(path, cached_only=cached_only)
    P = par()
    secs = {s: (section_targets(rows, P.get(s)) if isinstance(rows, list) else ["not read"]) for s, rows in r["sections"].items()}
    c = r.get("character")
    char_ok = isinstance(c, dict) and c.get("consistent") == 2 and not c.get("contradictions")
    return {"sections": secs, "character": c, "character_ok": char_ok, "met": sum(1 for v in secs.values() if not v),
            "ok": bool(secs) and all(not v for v in secs.values()) and char_ok}


# ---- negatives: Joe's complaints, swapped into the current song, must score below par ------------------------------------------
SLOT_START = {"Hook 1-4": 1, "Hook 5-8": 5, "Hook 9-16": 9, "V1 1-8": 17, "V1 9-16": 25, "V1 17-24": 33, "V1 25-32": 41,
              "V1 33-44": 49, "V2 1-8": 61, "V2 9-16": 69}


def _slot_of(bar_no: int) -> tuple[str, int]:
    s = max((k for k, v in SLOT_START.items() if v <= bar_no), key=lambda k: SLOT_START[k])
    return s, bar_no - SLOT_START[s]


def negative_cases(song: str = "writing/song_know_a_guy.md") -> list[dict]:
    """[{'label', 'slot', 'bars', 'targets': [bar index]}]: each flagged bar swapped into its section of the current song,
    each rhyme-complaint block read whole (every bar a target), and the nonsense set read as one block."""
    from . import sensecheck
    secs = _read_file(str(config.ROOT / song))
    out = []
    for ln in (config.ROOT / "toolkit" / "tests" / "flow_flagged.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        no, bar, why = [x.strip() for x in ln.split("|", 2)]
        slot, i = _slot_of(int(no))
        bars = list(secs[slot])
        bars[i] = bar
        out.append({"label": f"flow bar {no}", "slot": slot, "bars": bars, "targets": [i], "why": why[:80]})
    for ln in (config.ROOT / "toolkit" / "tests" / "rhyme_complaints.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        slot, rules, blob = ln.split("\t")
        bars = [b.strip() for b in blob.split(" / ")]
        out.append({"label": f"rhyme {slot} ({rules})", "slot": slot, "bars": bars, "targets": list(range(len(bars)))})
    out.append({"label": "nonsense set (sensecheck.BAD)", "slot": "V1 9-16", "bars": list(sensecheck.BAD),
                "targets": list(range(len(sensecheck.BAD)))})
    return out


def _auc(bad: list[float], good: list[float]) -> float:
    """P(a good bar outscores a complaint bar), ties half: 0.5 = no separation, 1.0 = perfect."""
    if not bad or not good:
        return float("nan")
    w = sum((g > b) + 0.5 * (g == b) for g in good for b in bad)
    return round(w / (len(good) * len(bad)), 3)


def negatives(cached_only: bool = False) -> dict:
    """hit rate: a complaint bar is caught when it sits below the original's slot par on at least one axis. The same rule run
    on the original's own bars is the false-alarm rate; per-axis AUC (complaint bars vs the original's bars) is the separation."""
    from concurrent.futures import ThreadPoolExecutor
    cases = negative_cases()
    narrator = card()
    if cached_only:
        reads = [read_section(c["slot"], c["bars"], narrator=narrator, cached_only=True) for c in cases]
    else:
        from ..llm import LLM, Ledger
        llm = LLM(ledger=Ledger(run_id="qualityread-neg"))

        def go(c):
            try:
                return read_section(c["slot"], c["bars"], llm, narrator)
            except Exception as e:  # noqa: BLE001 - an unread case is reported, never counted as caught
                return {"error": str(e)[:100]}
        with ThreadPoolExecutor(max_workers=5) as ex:
            reads = list(ex.map(go, cases))
    rows, caught, total, bad_marks = [], 0, 0, []
    for c, rd in zip(cases, reads):
        if not isinstance(rd, list):
            rows.append((c["label"], None, []))
            continue
        hits = []
        for i in c["targets"]:
            total += 1
            b = below_par(c["slot"], rd[i])
            caught += bool(b)
            hits.append((i + 1, c["bars"][i], b, rd[i]))
            bad_marks.append(rd[i])
        rows.append((c["label"], sum(1 for h in hits if h[2]), hits))
    P = par()
    orig = [(s, b) for s, p in P.items() for b in p.get("bars", [])]
    false_alarm = sum(1 for s, b in orig if below_par(s, b | {"forced_rate": b["forced"], "forced": "x" if b["forced"] else ""}))
    auc = {a: _auc([m[a] for m in bad_marks], [b[a] for _, b in orig]) for a in ("first_listen", "rewind", "clever")}
    auc["forced"] = _auc([-m.get("forced_rate", 0) for m in bad_marks], [-b["forced"] for _, b in orig])
    return {"caught": caught, "total": total, "rows": rows, "false_alarm": false_alarm, "orig_bars": len(orig), "auc": auc}


# ---- Joe's marks: the only thing that can make an axis hard ------------------------------------------------------------------
LABELS = config.ROOT / "writing" / "quality_labels.md"
COLS = ("first", "rewind", "forced", "char", "clever")
AXIS_OF = {"first": "first_listen", "rewind": "rewind", "char": "in_character", "clever": "clever"}
AGREE_HARD = 0.75


def write_labels(path: str) -> Path:
    """the sheet: every bar in quads with five blank columns. Joe fills what he hears; --agree compares."""
    secs = _read_file(path)
    L = ["# Quality marks: Joe's ear vs Claude's (fill in, then `python -m ww.write.qualityread --agree`)", "",
         f"Song: `{Path(path).as_posix()}` as of {__import__('datetime').date.today().isoformat()}. Assistant-authored bars. Mark what you hear; leave a cell blank to skip it.",
         "", "- **first** 0-2: 2 = you get the claim (and the joke) on one listen; 1 = after a beat; 0 = lost",
         "- **rewind** 0-2: 2 = a second layer a relisten finds (idiom made literal, pun, double meaning); 0 = nothing more",
         "- **forced**: the word or phrase picked for the rhyme or the count that nobody would say; `-` = nothing forced",
         "- **char** 0-2: 2 = only this narrator would say it; 0 = breaks him",
         "- **clever** 0-2: 2 = a line you'd quote back; 0 = flat", "",
         f"An axis becomes a HARD gate only if Claude agrees with your marks on at least {AGREE_HARD:.0%} of the bars you fill in.", ""]
    for slot, bars in secs.items():
        L += [f"## {slot}", ""]
        for q0 in range(0, len(bars), 4):
            L += ["| # | bar | first | rewind | forced | char | clever |", "|---|---|---|---|---|---|---|"]
            L += [f"| {i + 1} | {bars[i]} |  |  |  |  |  |" for i in range(q0, min(q0 + 4, len(bars)))]
            L.append("")
    LABELS.write_text("\n".join(L), encoding="utf-8")
    return LABELS


def read_labels() -> tuple[dict, dict]:
    """({slot: [bars in sheet order]}, {(slot, bar index): {col: value}} for every filled cell). The sheet carries its own bars, so a
    later rewrite of the song does not orphan Joe's marks: their reads stay cached by text."""
    secs, marks, slot = {}, {}, None
    for ln in LABELS.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            slot = ln[3:].strip()
            secs[slot] = []
        elif slot and ln.startswith("| ") and not ln.startswith(("| # ", "|---")):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 7:
                continue
            secs[slot].append(cells[1])
            m = {c: v for c, v in zip(COLS, cells[2:7]) if v}
            if m:
                marks[(slot, len(secs[slot]) - 1)] = m
    return secs, marks


def agreement(read_missing: bool = False) -> dict:
    """per axis: share of Joe's filled cells where Claude's mean is within 0.5 of his mark (forced: both name something, or neither)."""
    secs, joe = read_labels()
    tally = {c: [0, 0] for c in COLS}
    narrator = card()
    for slot, bars in secs.items():
        if not any(k[0] == slot for k in joe):
            continue
        rows = read_section(slot, bars, narrator=narrator, cached_only=not read_missing)
        if not rows:
            continue
        for i, row in enumerate(rows):
            for c, v in joe.get((slot, i), {}).items():
                if c == "forced":
                    hit = (v not in ("-", "none", "0")) == (row.get("forced_rate", 0) >= 0.5)
                else:
                    try:
                        hit = abs(float(v) - row[AXIS_OF[c]]) <= 0.5
                    except ValueError:
                        continue
                tally[c][0] += hit
                tally[c][1] += 1
    return {c: {"agree": a, "of": n, "rate": round(a / n, 2) if n else None, "hard_ok": bool(n >= 20 and a / n >= AGREE_HARD)}
            for c, (a, n) in tally.items()}


def selftest() -> tuple[bool, str]:
    """offline: the card hides authorship, the schema rows clamp, and the par comparison flags a below-par bar."""
    problems = []
    c = card()
    if re.search(r"Joe|Assistant|rule \d|material/|\.md", c):
        problems.append("the narrator card leaks authorship")
    if "Never" not in c:
        problems.append("the narrator card lost its 'Never' list")
    m = section_means([{"first_listen": 2, "rewind": 0, "in_character": 2, "clever": 1, "forced": ""},
                       {"first_listen": 1, "rewind": 1, "in_character": 1, "clever": 0, "forced": "okay"}])
    if m != {"first_listen": 1.5, "rewind": 0.5, "in_character": 1.5, "clever": 0.5, "forced": 0.5}:
        problems.append(f"section_means: {m}")
    rows = [{"first_listen": 2, "rewind": 1, "in_character": 2, "clever": 1, "forced": ""},
            {"first_listen": 0, "rewind": 0, "in_character": 1, "clever": 0, "forced": "x", "forced_rate": 1.0}]
    miss = section_targets(rows, {"first_listen": 1.0, "rewind": 0.5, "clever": 0.75, "forced": 0.25})
    if miss != ["clever 0.50 < 0.75", "forced 50% > 25%", "bar 2 first_listen 0"]:
        problems.append(f"section_targets: {miss}")
    s, i = _slot_of(42)
    if (s, i) != ("V1 25-32", 1):
        problems.append(f"bar 42 maps to {s} {i}")
    return (not problems, "; ".join(problems) if problems else "card strips authorship, means, targets, bar->slot mapping")


def main(argv=None) -> int:
    import argparse
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(prog="python -m ww.write.qualityread")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--cached", action="store_true", help="print cached reads only; never call the model")
    ap.add_argument("--negatives", action="store_true")
    ap.add_argument("--labels", action="store_true", help="write writing/quality_labels.md for Joe from FILE")
    ap.add_argument("--agree", action="store_true", help="Joe's filled sheet vs Claude's reads of the sheet's own bars, per axis")
    ap.add_argument("--targets", action="store_true", help="FILE against 'match the original' per section + character 2/2; exit 1 on a miss")
    a = ap.parse_args(argv)
    if a.targets:
        t = targets(a.file, cached_only=a.cached)
        for s, miss in t["sections"].items():
            print(f"{s:10s} {'PASS' if not miss else 'MISS: ' + '; '.join(miss)}")
        c = t["character"]
        print(f"CHARACTER  {'PASS' if t['character_ok'] else 'MISS'}: consistent {c.get('consistent') if isinstance(c, dict) else '?'}/2"
              + "".join(f"; bars {x['a']} vs {x['b']}" for x in (c or {}).get("contradictions", [])))
        print(f"TARGETS: {t['met']}/{len(t['sections'])} sections" + (" + character: PASS" if t["ok"] else ": not all met"))
        return 0 if t["ok"] else 1
    if a.labels:
        print(f"wrote {write_labels(a.file).relative_to(config.ROOT)}")
        return 0
    if a.agree:
        for c, v in agreement(read_missing=True).items():
            print(f"{c:7s} agree {v['agree']}/{v['of']}" + (f" = {v['rate']:.0%}" if v["of"] else "") + ("  -> may become HARD" if v["hard_ok"] else ""))
        return 0
    if a.negatives:
        r = negatives(a.cached)
        for label, n, hits in r["rows"]:
            if n is None:
                print(f"{label}: NOT READ")
                continue
            print(f"{label}: {n}/{len(hits)} below par")
            for i, bar, b, row in hits:
                print(f"   {'x' if b else '-'} bar {i}: {bar[:60]:60s} fl {row['first_listen']} rw {row['rewind']} cl {row['clever']} "
                      f"ch {row['in_character']} forced '{row.get('forced', '')}' {('BELOW: ' + ','.join(b)) if b else ''}")
        print(f"\nNEGATIVES: {r['caught']}/{r['total']} complaint bars below the original's par on at least one axis; "
              f"the same rule flags {r['false_alarm']}/{r['orig_bars']} of the original's own bars")
        print("separation, complaint bars vs the original's (AUC, 0.5 = none): " + " ".join(f"{k} {v}" for k, v in r["auc"].items()))
        return 0
    r = read_file(a.file, cached_only=a.cached)
    P = par()
    for s, rows in r["sections"].items():
        if not isinstance(rows, list):
            print(f"\n== {s}: {'NOT READ' if rows is None else rows}")
            continue
        m = section_means(rows)
        p = P.get(s, {})
        print(f"\n== {s}  means " + " ".join(f"{k} {v}" for k, v in m.items()) + (("  | original " + " ".join(f"{k} {p[k]}" for k in m if k in p)) if p else ""))
        for i, (bar, row) in enumerate(zip(r["bars"][s], rows)):
            b = below_par(s, row)
            print(f"  {i + 1:2d} fl {row['first_listen']} rw {row['rewind']} cl {row['clever']} ch {row['in_character']} "
                  f"{'F' if row.get('forced') else ' '} | {bar[:58]:58s} | {('forced: ' + row['forced'] + '; ') if row.get('forced') else ''}{row.get('note', '')[:70]}"
                  + (f"  << {','.join(b)}" if b else ""))
    c = r.get("character")
    if isinstance(c, dict) and "consistent" in c:
        print(f"\nCHARACTER consistent {c['consistent']}/2")
        for x in c.get("contradictions", []):
            print(f"  bars {x['a']} vs {x['b']}: {x['why']}")
        for x in c.get("off_card", []):
            print(f"  bar {x['bar']} off card: {x['why']}")
    elif c:
        print(f"\nCHARACTER: {c}")
    if r["unread"]:
        print(f"\nUNREAD: {r['unread']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
