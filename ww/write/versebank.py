"""Verse bank (Joe, 14 Oct 2026: "the writer should try writing as many verses as possible, different stories, different angles, different rhyme schemes and flows, then that will give us a bank to choose from").

  python -m ww.write.versebank [--stories id,id] [--frames "V2 1-8,V1 25-32"] [--n 3] [--workers 6] [--min-balance 0.5]

For every (story, frame) pair the writer produces n verses at different ANGLES; each is checked (the cached sense gate per bar and across bars is HARD; the form checks
are graded) and saved with its story, frame, rhyme scheme and issues. GRADE A = sense clean, syllables within 1 on all but one bar, rhyme pairs all rhyme, at most two
ending-kind mismatches, no repeated end word. GRADE B = sense clean, form flawed (the flaws are listed). Anything that fails sense is dropped.
Stories live in eval/_stories.json (git-ignored: the repo is public and the stories are personal); the bank is eval/_verse_bank.json and writing/verse_bank.md (both git-ignored).
Nothing here uses the original's text.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .. import bridge, config
from ..llm import LLM, Ledger, Request
from . import evolve, rapfit, sensecheck, seed_stage, slotcheck

STORIES = config.EVAL_DIR / "_stories.json"
BANK = config.EVAL_DIR / "_verse_bank.json"
OUT = config.ROOT / "writing" / "verse_bank.md"
FRAMES = ["V2 1-8", "V1 25-32", "V1 1-8", "V1 9-16", "Hook 9-16"]
ANGLES = [
    "DEADPAN REPORT: tell it as a flat itinerary or a form being filled in; the absurd thing is said in the voice of an errand, no reaction.",
    "BOAST AND BATHOS: open with the biggest claim of the story and let each bar get smaller and more petty until the last stressed word lands the smallest detail.",
    "CASHED PHRASE: build the verse around ONE real stock phrase taken literally, with its payoff word in the rhyme slot of the closing bar (the phrase can come from the story's objects).",
    "CHARACTER FIRST: a narrator who is slightly bored, a bit proud and never explains; one running object or number from the story recurs and changes meaning each time.",
]
SYSTEM = """You are the lyricist of a deadpan British rap, 140 BPM, for the narrator: {persona}
You write ONE 8-bar verse (twelve if the frame says so) built on the ESSENCE of a real story. You are a poet, not a reporter: do NOT retell the events in order. Pick the two or three moments that carry the irony, drop the rest, compress, reorder, exaggerate, use image, metaphor, simile and wordplay, and let the rhyme word bring the joke. Keep the story's truth (its irony and key objects) but you may paraphrase freely and add small cartoon embellishments; do not invent new named people or places. Swearing and vulgar slang are allowed; sex and drugs stay innuendo and aftermath, never explicit, never instructional.
CRAFT: every bar is a complete spoken English sentence a stranger follows on one hearing (no dropped articles or verbs to save syllables, nothing ending on a dangling in/on/out/up); the bars are ONE thread and each follows from the one before; the comedy is a flat voice reporting something big or petty; the payoff lands on the last stressed word; real names (artists, brands, places, local words) are welcome for specificity; cash a stock phrase literally where it fits; no moral, no summary, no explaining the joke.
SOUND: the frame lists which bars rhyme (same letter): they must rhyme on a STRESSED syllable (not a shared -ing/-ly/-ed/-er/-ation suffix); all end words different. Count syllables: a machine counts with a UK pronouncer and rejects a bar more than 2 out; write short plain words.
{exemplars}
Return JSON only: {{"verses": [{{"angle": "...", "end_words": [...], "idiom": "stock phrase cashed or ''", "bars": [strings]}}]}}"""


def _balance() -> float:
    try:
        out = subprocess.run([sys.executable, "-X", "utf8", "-m", "ww.cli", "balance"], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(config.ROOT), timeout=60).stdout
        m = re.search(r'total_balance":"([0-9.]+)', out)
        return float(m.group(1)) if m else 99.0
    except Exception:  # noqa: BLE001
        return 99.0


def _frame_text(slot: str) -> tuple[str, dict]:
    s = slotcheck.spec(slot)
    n = s["n"]
    u = {"slot": slot, "off": 0, "n": n}
    f = evolve.frame(u)
    lines = "\n".join(f"  bar {i + 1}: {f['sylls'][i]} syllables; the LAST WORD must be {evolve.KIND.get(f['shapes'][i], f['shapes'][i])}" for i in range(n))
    groups = {}
    for i, c in enumerate(f["letters"], 1):
        groups.setdefault(c, []).append(i)
    pairs = "; ".join(f"bars {', '.join(map(str, v))} rhyme together" for v in groups.values() if len(v) > 1) or "no end rhymes required"
    return (f"FRAME ({slot}, {n} bars, scheme {f['letters']}):\n{lines}\n{pairs}.{_menu(slot, groups)}", {"u": u, "frame": f})


def _menu(slot: str, groups: dict) -> str:
    """Real end words per rhyme group from the measured carpet bank, so the writer builds toward the story's words instead of padding to force a rhyme."""
    try:
        d = json.loads((config.ROOT / "benchmark" / ("carpets_" + slot.replace(" ", "_").replace("-", "_") + ".json")).read_text(encoding="utf-8"))
        pb = d["per_bar"]
    except Exception:  # noqa: BLE001
        return ""
    out = []
    for letter, bars in groups.items():
        if len(bars) < 2:
            continue
        seen: list[str] = []
        for b in bars:
            for w in (pb[b - 1][:40] if b - 1 < len(pb) else []):
                if w["word"] not in seen:
                    seen.append(w["word"])
        if seen:
            out.append(f"  group {letter} (bars {', '.join(map(str, bars))}) rhyme-family words to choose from: {', '.join(seen[:30])}")
    return ("\nEND-WORD MENU (pick the ones your story lands naturally; build each sentence TOWARD its end word, never pad):\n" + "\n".join(out)) if out else ""


ESS = config.EVAL_DIR / "_essence.json"


def essence(llm: LLM, story: dict) -> dict:
    """one cheap call per story (cached): the irony, the central image, what to drop, figurative handles. The verse writer sees this, not the teller's wording."""
    try:
        cache = json.loads(ESS.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        cache = {}
    if story["id"] in cache:
        return cache[story["id"]]
    req = Request(model=evolve.WRITER, system="You are a comedy editor for a deadpan British rap. Given a true anecdote, find its ESSENCE the way a good lyricist would: not the sequence of events but what makes it funny or striking. Return JSON only.",
                  messages=[{"role": "user", "content": story["title"] + "\n" + story["text"] + "\n\nReturn JSON with keys: irony (one sentence on the real joke or turn), image (the single most vivid concrete image), drop (details a lyric should leave out), handles (5 figurative or wordplay handles: similes, double meanings, stock phrases taken literally, sound-alikes), punchline (the best last-bar landing), mood (the narrator's attitude in a few words)."}],
                  max_tokens=1200, effort=None, temperature=0.7, stage="versebank_essence", scope="write",
                  schema={"type": "object", "properties": {k: {"type": ("array" if k == "handles" else "string"), **({"items": {"type": "string"}} if k == "handles" else {})} for k in ("irony", "image", "drop", "handles", "punchline", "mood")}})
    try:
        e = (llm.complete(req, use_cache=True).parsed or {})
    except Exception:  # noqa: BLE001
        e = {}
    if e:
        cache[story["id"]] = e
        ESS.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")
    return e


def writer_request(story: dict, slot: str, n: int, ess: dict | None = None) -> Request:
    ft, _ = _frame_text(slot)
    angles = "\n".join(f"  {i + 1}. {a}" for i, a in enumerate(ANGLES[:n]))
    if ess:
        body = (f"ESSENCE ({story['level']}): {story['title']}\nThe turn: {ess.get('irony', '')}\nThe image: {ess.get('image', '')}\nLeave out: {ess.get('drop', '')}\n"
                f"Handles you may use: " + "; ".join(ess.get("handles", [])) + f"\nBest landing: {ess.get('punchline', '')}\nNarrator's mood: {ess.get('mood', '')}")
    else:
        body = f"STORY ({story['level']}): {story['title']}\n{story['text']}"
    user = (f"{body}\n\n{ft}\n\nWrite {n} DIFFERENT verses, one per angle, in this order:\n{angles}\n"
            f"Each verse is exactly {slotcheck.spec(slot)['n']} bars and must tell or boast this story's core in its own way.")
    sylls = slotcheck.spec(slot)["sylls"]
    return Request(model=evolve.WRITER, system=SYSTEM.format(persona=seed_stage.PERSONA, exemplars=evolve.exemplars(sylls)),
                   messages=[{"role": "user", "content": user}], max_tokens=7000, effort="medium", temperature=None, stage="versebank", scope="write",
                   schema={"type": "object", "required": ["verses"], "properties": {"verses": {"type": "array", "items": {
                       "type": "object", "required": ["bars"], "properties": {"angle": {"type": "string"}, "end_words": {"type": "array", "items": {"type": "string"}},
                                                                              "idiom": {"type": "string"}, "bars": {"type": "array", "items": {"type": "string"}}}}}}})


def grade(slot: str, bars: list[str]) -> tuple[str, list[str]]:
    """returns ('A'|'B'|'X', issues). X = fails sense (dropped)."""
    n = slotcheck.spec(slot)["n"]
    if len(bars) != n or not all(bars):
        return "X", [f"{len(bars)} bars, need {n}"]
    f = evolve.frame({"slot": slot, "off": 0, "n": n})
    issues = []
    syl_miss = [i for i, b in enumerate(bars) if abs(bridge.syllable_count(b) - f["sylls"][i]) > 1]
    syl_bad = [i for i, b in enumerate(bars) if abs(bridge.syllable_count(b) - f["sylls"][i]) > 2]
    shape_bad = [i for i, b in enumerate(bars) if not evolve._shape_ok(slot, f["shapes"][i], b)]
    pair_bad = [(i, j) for i, j in f["pairs"] if rapfit.score(bars[i], bars[j])["score"] < rapfit.FLOOR]
    ends = [(bridge.words(b) or [""])[-1].lower() for b in bars]
    dup = [w for w, c in Counter(ends).items() if c > 1 and w]
    names = [w for b in bars for w in re.findall(r"(?<=[a-z,] )[A-Z][a-zA-Z'\-]+", b) if w.lower() not in evolve.known_names()]
    if syl_miss:
        issues.append(f"{len(syl_miss)} bars off the syllable count: " + ", ".join(f"{i + 1}({bridge.syllable_count(bars[i])} vs {f['sylls'][i]})" for i in syl_miss))
    if shape_bad:
        issues.append(f"{len(shape_bad)} bars with the wrong ending kind: {[i + 1 for i in shape_bad]}")
    if pair_bad:
        issues.append(f"{len(pair_bad)} required rhyme pairs do not rhyme: {[(i + 1, j + 1) for i, j in pair_bad]}")
    if dup:
        issues.append(f"repeated end words {dup}")
    if names:
        issues.append(f"proper nouns not in Joe's material: {sorted(set(names))}")
    sc = sensecheck.check(bars)
    bc = sensecheck.block_check(bars)
    sense_fail = [(k, w) for k, w in sc["fails"]]
    if sense_fail or not bc["ok"]:
        for k, w in sense_fail[:3]:
            issues.append(f"SENSE bar {k}: {w}")
        if not bc["ok"]:
            issues.append(f"SENSE across bars: {bc.get('issue') or bc.get('thread', '')[:70]}")
        return "X", issues
    if names:
        return "X", issues
    a = (len(syl_miss) <= 1 and not syl_bad and len(shape_bad) <= 2 and not pair_bad and not dup)
    if a:
        return "A", issues
    if len(syl_bad) <= 3 and len(pair_bad) <= max(1, len(f["pairs"]) // 4):
        return "B", issues
    return "X", issues


def _clean(b: str) -> str:
    return evolve._clean(b)


def one(llm: LLM, story: dict, slot: str, n: int) -> list[dict]:
    try:
        res = llm.complete(writer_request(story, slot, n, essence(llm, story)), use_cache=False)
    except Exception as e:  # noqa: BLE001
        return [{"story": story["id"], "frame": slot, "grade": "ERR", "issues": [str(e)[:100]], "bars": []}]
    out = []
    for v in (res.parsed or {}).get("verses", []):
        bars = [_clean(x) for x in v.get("bars", [])]
        g, iss = grade(slot, bars)
        out.append({"story": story["id"], "title": story["title"], "frame": slot, "scheme": slotcheck.spec(slot)["scheme"], "angle": (v.get("angle") or "")[:60],
                    "idiom": v.get("idiom", ""), "grade": g, "issues": iss, "bars": bars, "t": int(time.time())})
    return out


def render(bank: list[dict]) -> str:
    keep = [v for v in bank if v["grade"] in ("A", "B")]
    lines = ["# Verse bank (generated; git-ignored; personal stories)", "",
             f"{len(keep)} verses kept (A = clean on sense and form, B = sense clean, form flawed), from {len(bank)} written. Pick by story, angle and flow; the grade says what is wrong, not what is funny.", ""]
    by = {}
    for v in keep:
        by.setdefault(v["story"], []).append(v)
    for sid, vs in by.items():
        lines.append(f"## {vs[0]['title']}  ({len(vs)} kept)")
        for v in sorted(vs, key=lambda x: (x["grade"], x["frame"])):
            lines.append(f"\n**{v['grade']} | frame {v['frame']} ({v['scheme']}) | {v['angle']}**" + (f" | cashes: {v['idiom']}" if v.get("idiom") else ""))
            lines += [f"    {b}" for b in v["bars"]]
            if v["issues"]:
                lines.append("    (" + "; ".join(v["issues"])[:300] + ")")
        lines.append("")
    return "\n".join(lines)


def run(stories: list[str] | None, frames: list[str], n: int, workers: int, min_balance: float) -> list[dict]:
    llm = LLM(ledger=Ledger(run_id="versebank"))
    ss = json.loads(STORIES.read_text(encoding="utf-8"))
    if stories:
        ss = [s for s in ss if s["id"] in stories]
    try:
        bank = json.loads(BANK.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        bank = []
    jobs = [(s, f) for s in ss for f in frames]
    done = 0
    t0 = time.time()

    def work(job):
        if _balance() < min_balance:
            return []
        return one(llm, job[0], job[1], n)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for rows in ex.map(work, jobs):
            bank += rows
            done += 1
            BANK.write_text(json.dumps(bank, ensure_ascii=False, indent=0), encoding="utf-8")
            if done % 5 == 0 or done == len(jobs):
                c = Counter(v["grade"] for v in bank)
                print(f"{done}/{len(jobs)} jobs  grades {dict(c)}  {round((time.time() - t0) / 60, 1)} min", flush=True)
    OUT.write_text(render(bank), encoding="utf-8")
    return bank


if __name__ == "__main__":
    import argparse
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--stories", default="")
    ap.add_argument("--frames", default=",".join(FRAMES))
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--min-balance", type=float, default=0.5)
    a = ap.parse_args()
    run([x for x in a.stories.split(",") if x] or None, [x.strip() for x in a.frames.split(",") if x.strip()], a.n, a.workers, a.min_balance)
