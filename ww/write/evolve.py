"""Evolve: an autonomous, self-improving quad writer (Joe, 14 Oct 2026: "a pipeline that can produce lyrics as good as the original with no human input").

THE UNIT is a 4-bar quad, aligned one-to-one with the original's 19 quads (same slot, same position). For each quad the loop
  1. WRITES a batch of candidate quads (ds-pro): the section's argument and per-bar claims from the plan, the measured frame for exactly these four bars
     (syllables, ending kind, by-ear rhyme pairs), the bars before it (continuity), the previous attempt's gate failures, and in-context EXEMPLARS taken from
     this pipeline's own accepted bars (rejection-sampling distillation; never the original's text);
  2. FILTERS every candidate on the free deterministic gates (syllables, ending kind, rhyme pairs by rapfit, repeated end word, narrator present, anti-copy)
     and then the cached SENSE gate (each bar a sentence, the quad one thread: ww/write/sensecheck.py);
  3. REPAIRS near-misses: the failing bars and their exact complaints go back to the writer (up to 2 rounds) - fix only what failed;
  4. SELECTS by blind duel against the original's matching quad (both presentation orders, private calibration client, no original text stored or logged);
  5. RATCHETS: a candidate replaces the incumbent only if it has no more gate failures AND wins more duels (or ties and wins the head-to-head).
Round statistics (which gate fails most, which quads still lose) feed the next round's prompt, so the pipeline tunes itself between rounds.

HONEST LIMITS. The duel is an LLM opinion (validated only as "prefers real text to its own degraded variant", ww/eval/pairwise.py), the writer is a
2026 DeepSeek model, and "as good as the original" is Joe's ear's call. This loop reports parity numbers; it cannot certify them.
"""
from __future__ import annotations

import io
import itertools
import json
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from .. import bridge, config
from ..calib import anticopy, original
from ..judge import rank
from ..llm import LLM, Ledger, Request
from . import argue_stage, rapfit, sensecheck, seed_stage, slotcheck

LOG = config.EVAL_DIR / "evolve_log.json"
BANK = config.EVAL_DIR / "evolve_bank.json"          # accepted bars by length, and bars of quads that WON their duel (our own text only)
REPORT = config.ROOT / "writing" / "evolve_report.md"
WRITER = "ds-pro"
MAX_MISMATCH_SHAPES = 1


# ------------------------------------------------------------------ units and the draft
def units() -> list[dict]:
    out = []
    for name, a, b in slotcheck.SECS:
        for k in range((b - a + 3) // 4):
            s, e = a + 4 * k, min(a + 4 * k + 4, b)
            out.append({"q": s // 4, "slot": name, "off": 4 * k, "n": e - s, "start": s, "end": e})
    return out


def parse_draft(path) -> dict[str, list[str]]:
    sec, cur = {}, None
    for ln in io.open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("== "):
            cur = ln[3:].strip()
            sec[cur] = []
        elif ln.strip() and cur and not ln.startswith("#"):
            sec[cur].append(ln.strip())
    return sec


def quad_bars(draft: dict, u: dict) -> list[str]:
    return draft.get(u["slot"], [])[u["off"]:u["off"] + u["n"]]


def put_quad(draft: dict, u: dict, bars: list[str]) -> None:
    cur = draft.setdefault(u["slot"], [])
    cur[u["off"]:u["off"] + u["n"]] = bars


def write_draft(draft: dict, path) -> None:
    lines = []
    for name, _, _ in slotcheck.SECS:
        lines.append(f"== {name}")
        lines += draft.get(name, [])
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ the frame of one quad
def frame(u: dict) -> dict:
    s = slotcheck.spec(u["slot"])
    a, b = u["off"], u["off"] + u["n"]
    letters = s["scheme"][a:b]
    pairs = [(i, j) for i in range(len(letters)) for j in range(i + 1, len(letters)) if letters[i] == letters[j]]
    return {"sylls": s["sylls"][a:b], "shapes": s["shapes"][a:b], "letters": letters, "pairs": pairs}


def _shape_ok(slot: str, want: str, bar: str) -> bool:
    got = bridge.end_shape(bar)
    last = (bridge.words(bar) or [""])[-1]
    if slot.startswith("V"):
        return got.endswith("S") == want.endswith("S") or (not want.endswith("S") and got == "|SS" and bridge.stress_pattern(last) == "12")
    return got == want or (want in ("|Sw", "~Sw") and got in ("|Sw", "~Sw")) or (want == "|Sw" and got == "|SS" and bridge.stress_pattern(last) == "12")


_KNOWN = None


def known_names() -> set:
    """capitalised words that appear in Joe's material, the plan or the local-word list: the only proper nouns a bar may use (rule 5: true or flagged)."""
    global _KNOWN
    if _KNOWN is None:
        k = set()
        for p in list((config.ROOT / "material").glob("*.md")) + [config.EVAL_DIR / "_plan_v5.json", config.ROOT / "toolkit" / "local_words.txt"]:
            try:
                k |= {w.lower() for w in re.findall(r"[A-Z][a-zA-Z'\-]+", p.read_text(encoding="utf-8"))}
            except OSError:
                pass
        k |= set("""i i'm i've i'd i'll hoi kaixo ciao hola oui obrigado shukran prost napoli corrie vespa limoncello k'gari jemaa el-fna fna""".split())
        _KNOWN = k
    return _KNOWN


def check_free(u: dict, bars: list[str], tol: int = 1) -> list[tuple[str, int, str]]:
    """deterministic gates: [(kind, bar index 0-based or -1, message)]. No model calls."""
    f = frame(u)
    iss = []
    if len(bars) != u["n"]:
        return [("count", -1, f"need {u['n']} bars, got {len(bars)}")]
    ends = []
    for i, b in enumerate(bars):
        n = bridge.syllable_count(b)
        if abs(n - f["sylls"][i]) > tol:
            iss.append(("syl", i, f"bar {i + 1}: {n} syllables, need {f['sylls'][i]} (+-{tol})"))
        ends.append((bridge.words(b) or [""])[-1].lower())
    bad_shape = [i for i, b in enumerate(bars) if not _shape_ok(u["slot"], f["shapes"][i], b)]
    if len(bad_shape) > MAX_MISMATCH_SHAPES:
        for i in bad_shape:
            iss.append(("shape", i, f"bar {i + 1} ends {bridge.end_shape(bars[i])}, the frame wants {f['shapes'][i]}"))
    for i, j in f["pairs"]:
        sc = rapfit.score(bars[i], bars[j])["score"]
        if sc < rapfit.FLOOR:
            iss.append(("rhyme", j, f"bars {i + 1} and {j + 1} must rhyme on a stressed syllable (rapfit {sc:.2f})"))
    # THE CARPET (Joe, 14 Oct 2026: "why is our draft so far off the original's rhyme scheme"): in the original's hook blocks all FOUR end words share one stressed
    # vowel and tail, so all 6 pairs rhyme (two perfect couplets that also rhyme with each other). Detection was fixed on 13 Oct; enforcement while writing was not.
    car = slotcheck.spec(u["slot"])["carpet"]
    if u["n"] == 4 and car["share"] >= 0.5:
        need = 6 if car["share"] >= 0.99 else int(0.85 * car["share"] * 6 + 0.5)
        got = sum(1 for i, j in itertools.combinations(range(4), 2) if rapfit.score(bars[i], bars[j])["score"] >= rapfit.FLOOR)
        if got < need:
            iss.append(("carpet", -1, f"only {got}/6 end-pairs rhyme; the original holds {need}/6 here: this quad is ONE rhyme family, so ALL FOUR end words must share the same stressed vowel and ending sound"))
    for i, b in enumerate(bars):
        for w in re.findall(r"(?<=[a-z,] )[A-Z][a-zA-Z'\-]+", b):
            if w.lower() not in known_names():
                iss.append(("place", i, f"bar {i + 1}: '{w}' is not in Joe's material (no invented places or names)"))
    for w, c in Counter(e for e in ends if e).items():
        if c > 1:
            iss.append(("endword", -1, f"end word '{w}' used {c} times in the quad"))
    if not any(re.search(r"\b(i|i'm|i've|i'd|i'll|my|me|we)\b", b.lower()) for b in bars):
        iss.append(("narrator", -1, "no bar has the narrator in it (I / my / me / we)"))
    try:
        ac = anticopy.check(bars)
        if not ac["ok"]:
            iss.append(("copy", -1, "too close to the original's wording"))
    except Exception:  # noqa: BLE001
        pass
    return iss


def check_sense(bars: list[str]) -> list[tuple[str, int, str]]:
    r = sensecheck.check(bars)
    iss = [("sense", n - 1, f"bar {n}: {why}") for n, why in r["fails"]]
    bc = sensecheck.block_check(bars)
    if not bc["ok"]:
        iss.append(("thread", -1, f"the four bars do not hold together: {bc.get('issue') or bc.get('thread', '')[:80]} (non-sequiturs at bars {[n for n, _ in bc['fails']]})"))
    return iss


# ------------------------------------------------------------------ exemplars (our own accepted bars)
def _bank() -> dict:
    try:
        return json.loads(BANK.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"winners": [], "by_len": {}}


def _bank_save(b: dict) -> None:
    BANK.write_text(json.dumps(b, ensure_ascii=False, indent=0), encoding="utf-8")


def remember(bars: list[str], won: bool) -> None:
    b = _bank()
    for x in bars:
        n = bridge.syllable_count(x)
        lst = b["by_len"].setdefault(str(n), [])
        if x not in lst:
            lst.append(x)
            del lst[:-6]
    if won:
        blk = list(bars)
        if blk not in b["winners"]:
            b["winners"].append(blk)
            del b["winners"][:-8]
    _bank_save(b)


def exemplars(sylls: list[int]) -> str:
    b = _bank()
    out = []
    for n in sorted(set(sylls)):
        ex = b["by_len"].get(str(n), [])
        if ex:
            out.append(f"  {n} syllables: {ex[-1]}")
    win = b["winners"][-2:]
    txt = ""
    if out:
        txt += "LENGTH CALIBRATION (counted bars already accepted in this song; copy the length, not the words):\n" + "\n".join(out) + "\n"
    if win:
        txt += "BLOCKS THAT BEAT A PROFESSIONAL QUAD IN A BLIND DUEL (our own; study what they do, do not copy):\n" + "\n\n".join("\n".join("  " + x for x in w) for w in win) + "\n"
    return txt


# ------------------------------------------------------------------ the writer
SYSTEM = """You are the lyricist of a deadpan British rap, 140 BPM, for the narrator: {persona}
You write ONE quad (four consecutive bars). The craft that wins:
- SAY SOMETHING. Every bar is a complete spoken English sentence (or a real spoken fragment like a greeting) that a stranger understands on one hearing. Never drop articles, verbs or objects to save syllables. Never end a bar on a dangling 'in/on/out/up'.
- ONE THREAD. The four bars are one little scene or one argument; each bar follows from the one before (use 'then', 'so', 'while', 'but', a pronoun with a clear antecedent). Pronouns need someone introduced.
- CHARACTER AND PAYOFF. The comedy is a flat, nonchalant voice reporting something big, illicit or petty in an everyday British register (queues, tickets, prices, telling-offs). The last stressed word of the final bar (and of any bar that cashes a phrase) carries the payoff: a stock phrase taken literally, a pun, a sound-alike, or a deflating small detail. Do not explain the joke. No moral, no summary, no 'and that is why'.
- SPECIFIC. Named places, prices, objects, brands, local words, real British slang, and real artists, films and festival lineups by NAME (artist names are fine in lyrics; the festival and event lineups in the brief are fair game), but never aim menace or an accusation at a real person. Swearing and vulgar slang are allowed if the bar needs them.
- RHYME FAMILY FIRST. Before writing, pick the end words. In a hook-type quad the original rhymes ALL FOUR bars on one family (same stressed vowel AND same ending sound, e.g. porter / shorter / daughter / water): choose four different real common words (or places) that share it, then write each sentence to land on its word. Two couplets on different vowels (garden/pardon + sorry/lorry) is a FAIL.
- SOUND. The bars that your FRAME says rhyme must rhyme on a STRESSED syllable (favours/flavours; Lagos/Vegas), not on a shared unstressed ending such as -ing, -ly, -ed, -er, -ation. Hold ONE vowel sound through the rhyme group; repeat internal vowel echoes between neighbouring bars. End words must all be different words.
- LENGTH. A machine counts syllables with a UK pronouncer and rejects a bar more than {tol} syllable out. Count aloud before you answer. Short, plain words. {exemplars}
- No invented named people (roles only: the lads, my mate, the driver, the copper). No more than two references to any one person. Nothing instructional about drugs or violence; cartoon deadpan only.
Return JSON only: {{"candidates": [{{"end_words": [the four end words you chose first], "bars": [four strings], "idiom": "the stock phrase cashed, or ''", "plain": "the quad as 2 plain sentences"}}]}}"""


def _context_bars(draft: dict, u: dict, k: int = 4) -> list[str]:
    sec = draft.get(u["slot"], [])
    return sec[max(0, u["off"] - k):u["off"]]


def _section_brief(u: dict) -> str:
    try:
        sec = argue_stage._section(u["slot"])
    except KeyError:
        return ""
    rows = argue_stage._beat_rows(u["slot"])
    lines = [f"SECTION '{u['slot']}': {sec.get('argument', '')}"]
    for r in rows:
        nums = [int(x) for x in re.findall(r"\d+", r["bars"] or "")]
        if any(u["off"] < x <= u["off"] + u["n"] for x in nums) or not nums:
            lines.append(f"  bars {r['bars']} ({r['job']}): {r['content']}")
    return "\n".join(lines)


KIND = {"|S": "ONE stressed syllable at the very end: a one-syllable word or a word stressed on its last syllable (bread, ride, Bordeaux, worldwide)",
        "|Sw": "a stressed syllable then ONE weak one: the last word has two syllables stressed on the FIRST (garden, lorry, Porto, Lagos, ferry)",
        "~Sw": "like |Sw but the rhyme sits inside the last phrase, then one weak syllable follows (e.g. '...ciao for now', '...the plane to Oslo')",
        "|SS": "two stressed syllables at the end (worldwide, outside, Bordeaux?)",
        "|w": "a weak final syllable that carries the rhyme with the stress earlier (tails like 'him in', 'stumbled in', 'it')",
        "~S": "ends on a stressed syllable that is part of a longer phrase",
        "|Sww": "stressed then TWO weak syllables (tumbling, carburettor, Amsterdam, Heysham)",
        "~w": "ends on a weak syllable after an earlier stressed rhyme",
        "|SwS": "stressed, weak, stressed (Castletown, Cairns Town)"}


def writer_request(u: dict, draft: dict, feedback: str, n: int, tol: int = 1) -> Request:
    f = frame(u)
    frame_txt = "\n".join(f"  bar {i + 1}: {f['sylls'][i]} syllables, ending {f['shapes'][i]}" for i in range(u["n"]))
    pairs = "; ".join(f"bars {i + 1} & {j + 1}" for i, j in f["pairs"]) or "none (free endings)"
    ctx = _context_bars(draft, u)
    cur = quad_bars(draft, u)
    user = (f"{_section_brief(u)}\n\nFRAME FOR THESE FOUR BARS:\n{frame_txt}\nBars that must rhyme with each other: {pairs}. Rhyme letters: {f['letters']}.\n"
            + (("\nTHE BARS JUST BEFORE (continue from them, do not repeat them):\n" + "\n".join("  " + x for x in ctx) + "\n") if ctx else "")
            + (("\nTHE CURRENT VERSION (it loses a blind duel to a professionally written quad; beat it, do not just reword it):\n" + "\n".join("  " + x for x in cur) + "\n") if cur else "")
            + (f"\nWHAT WAS WRONG LAST TIME (fix these, keep what worked):\n{feedback}\n" if feedback else "")
            + f"\nWrite {n} DIFFERENT candidate quads. Vary the idea, not just the words.")
    return Request(model=WRITER, system=SYSTEM.format(persona=seed_stage.PERSONA, tol=tol, exemplars=exemplars(f["sylls"])),
                   messages=[{"role": "user", "content": user}], max_tokens=6000, effort="high", temperature=None, stage="evolve", scope="write",
                   schema={"type": "object", "required": ["candidates"], "properties": {"candidates": {"type": "array", "items": {
                       "type": "object", "required": ["bars"], "properties": {"bars": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 4},
                                                                              "end_words": {"type": "array", "items": {"type": "string"}}, "idiom": {"type": "string"}, "plain": {"type": "string"}}}}}})


def _clean(b: str) -> str:
    b = re.sub(r"^\s*(\d+[.)]|bar\s*\d+[:.)])\s*", "", b.strip(), flags=re.I)
    return b.strip().strip('"').strip()


def write_candidates(llm: LLM, u: dict, draft: dict, feedback: str, n: int = 8) -> list[list[str]]:
    res = llm.complete(writer_request(u, draft, feedback, n), use_cache=False)
    out = []
    for c in (res.parsed or {}).get("candidates", []):
        bars = [_clean(x) for x in c.get("bars", [])]
        if len(bars) == u["n"] and all(bars):
            out.append(bars)
    return out


def repair(llm: LLM, u: dict, bars: list[str], issues: list[tuple[str, int, str]], draft: dict) -> list[str]:
    f = frame(u)
    why = "\n".join(f"  - {m}" for _, _, m in issues)
    user = (f"{_section_brief(u)}\n\nFRAME: syllables {f['sylls']}, endings {f['shapes']}, rhyme letters {f['letters']} (same letter = rhymes on a stressed syllable).\n"
            f"THE QUAD:\n" + "\n".join(f"  {i + 1}. {b}" for i, b in enumerate(bars)) + f"\n\nGATE FAILURES:\n{why}\n\n"
            f"Rewrite ONLY what is needed to fix every failure. Keep a bar unchanged if it has no failure and the others still follow from it. Every bar must stay a complete sentence. Return 3 different repaired quads.")
    req = Request(model=WRITER, system=SYSTEM.format(persona=seed_stage.PERSONA, tol=1, exemplars=exemplars(f["sylls"])), messages=[{"role": "user", "content": user}],
                  max_tokens=4000, effort="high", stage="evolve", scope="repair", schema=writer_request(u, draft, "", 1).schema)
    res = llm.complete(req, use_cache=False)
    out = []
    for c in (res.parsed or {}).get("candidates", []):
        b = [_clean(x) for x in c.get("bars", [])]
        if len(b) == u["n"] and all(b):
            out.append(b)
    return out


# ------------------------------------------------------------------ critique and revise (own text only)
CRITIC = """You are a ruthless British comedy-rap editor. You are given a quad (four bars) of deadpan rap that LOSES a blind head-to-head against a professionally written quad.
Say exactly why in craft terms, using the standard the judges use: (1) does every bar say something concrete; (2) is it spoken English; (3) is there a stable character
and a payoff landing on the last stressed word, with a flat everyday register reporting something big or petty; (4) specificity (named place, price, object, local word)
versus generic travel talk or cliche. Then give THREE concrete rewrite directions (an idea, a sharper payoff word or phrase to cash, a cut). Be specific to these bars.
Return JSON: {"weaknesses": [up to 4 short strings], "directions": [3 short strings]}."""


def critique(llm: LLM, bars: list[str], u: dict) -> dict:
    quad_txt = "\n".join(f"  {i + 1}. {b}" for i, b in enumerate(bars))
    res = llm.complete(Request(model="ds-flash", system=CRITIC, messages=[{"role": "user", "content": _section_brief(u) + "\n\nTHE QUAD:\n" + quad_txt}],
                               max_tokens=900, effort=None, temperature=0.3, stage="evolve", scope="critic",
                               schema={"type": "object", "required": ["weaknesses", "directions"], "properties": {"weaknesses": {"type": "array", "items": {"type": "string"}},
                                                                                                                "directions": {"type": "array", "items": {"type": "string"}}}}), use_cache=False)
    return res.parsed or {"weaknesses": [], "directions": []}


def refine(llm: LLM, pllm: LLM, u: dict, draft: dict, bars: list[str], cur_duel: float, orig: dict, stats: Optional[Counter] = None) -> tuple[list[str], float]:
    """one critique -> rewrite -> gates -> duel step on a quad that still loses; returns (best bars, its duel)."""
    cr = critique(llm, bars, u)
    weak = "\n".join("  - " + w for w in cr.get("weaknesses", []))
    dirs = "\n".join("  - " + d for d in cr.get("directions", []))
    fb = "An editor's verdict on the current quad:\n" + weak + "\nRewrite directions to try (one per candidate, then your own):\n" + dirs
    best, best_d = bars, cur_duel
    for c in write_candidates(llm, u, draft, fb, 6):
        if check_free(u, c) or check_sense(c):
            continue
        d = duel(pllm, u, c, orig)
        if stats is not None:
            stats["refine_tried"] += 1
        if d > best_d:
            best, best_d = c, d
    return best, best_d


# ------------------------------------------------------------------ the duel against the original
def duel(pllm: LLM, u: dict, bars: list[str], orig: dict) -> float:
    """1.0 if ours beats the original's matching quad in both presentation orders, 0.0 if it loses both, 0.5 otherwise. Returns a number only."""
    ctx = orig.get("context") or None
    a = rank.rank_batch(pllm, [("ours", bars), ("orig", orig["bars"])], context=ctx, stage="duel", scope="calib")
    b = rank.rank_batch(pllm, [("orig", orig["bars"]), ("ours", bars)], context=ctx, stage="duel", scope="calib")
    if not a or not b:
        return 0.5
    wa, wb = a[0] == "ours", b[0] == "ours"
    return 1.0 if (wa and wb) else 0.0 if (not wa and not wb) else 0.5


def head_to_head(llm: LLM, bars_a: list[str], bars_b: list[str], ctx: list[str]) -> float:
    """1.0 if a beats b in both orders (own text only, ordinary client)."""
    a = rank.rank_batch(llm, [("a", bars_a), ("b", bars_b)], context=ctx or None, stage="h2h", scope="judge")
    b = rank.rank_batch(llm, [("b", bars_b), ("a", bars_a)], context=ctx or None, stage="h2h", scope="judge")
    if not a or not b:
        return 0.5
    wa, wb = a[0] == "a", b[0] == "a"
    return 1.0 if (wa and wb) else 0.0 if (not wa and not wb) else 0.5


# ------------------------------------------------------------------ improve one quad
def total_issues(u, bars):
    free = check_free(u, bars)
    return free, (check_sense(bars) if not free else [])


def improve_unit(llm: LLM, pllm: LLM, u: dict, draft: dict, orig: dict, feedback: str, n: int, repairs: int = 2, stats: Optional[Counter] = None, final: bool = False) -> dict:
    inc = quad_bars(draft, u)
    inc_free, inc_sense = total_issues(u, inc) if inc else ([("count", -1, "empty")], [])
    inc_bad = len(inc_free) + len(inc_sense)
    inc_duel = duel(pllm, u, inc, orig) if inc else 0.0
    pool = write_candidates(llm, u, draft, feedback, n)
    if stats is not None:
        stats["candidates"] += len(pool)
    scored = []
    for c in pool:
        free = check_free(u, c)
        for kind, _, _ in free:
            if stats is not None:
                stats[f"fail_{kind}"] += 1
        scored.append((len(free), c, free))
    scored.sort(key=lambda x: x[0])
    clean = [c for k, c, _ in scored if k == 0]
    # sense on the clean ones (cached, cheap)
    passed = []
    for c in clean[:8]:
        s = check_sense(c)
        for kind, _, _ in s:
            if stats is not None:
                stats[f"fail_{kind}"] += 1
        if not s:
            passed.append(c)
    # repair near-misses when nothing passes
    tries = 0
    pending = [(c, free) for k, c, free in scored if 0 < k <= 3][:3] + [(c, check_sense(c)) for c in clean if c not in passed][:2]
    while not passed and tries < repairs and pending:
        tries += 1
        nxt = []
        for c, iss in pending[:3]:
            for r in repair(llm, u, c, iss, draft):
                free = check_free(u, r)
                s = check_sense(r) if not free else []
                if stats is not None:
                    stats["repaired"] += 1
                if not free and not s:
                    passed.append(r)
                else:
                    nxt.append((r, free + s))
        pending = sorted(nxt, key=lambda x: len(x[1]))
    # duel the finalists
    best, best_duel = None, -1.0
    seen = set()
    for c in passed[:6]:
        key = tuple(c)
        if key in seen:
            continue
        seen.add(key)
        d = duel(pllm, u, c, orig)
        if d > best_duel:
            best, best_duel = c, d
    took = False
    if best is not None:
        # the objective is the duel, subject to every gate: a gate-clean candidate replaces a gate-dirty incumbent when it duels at least as well,
        # and always in the final round (the delivered draft must be gate-clean); against a clean incumbent it must duel better or win the head-to-head
        better = best_duel > inc_duel or (inc_bad and (best_duel == inc_duel or final))
        if not better and best_duel == inc_duel and inc and not inc_bad and best != inc:
            better = head_to_head(llm, best, inc, orig.get("context") or []) == 1.0
        if better:
            put_quad(draft, u, best)
            took = True
            remember(best, best_duel == 1.0)
    # a quad that still loses its duel gets critique-and-revise steps (own text only; the original is never shown to the critic or the writer)
    cur = quad_bars(draft, u)
    cur_d = best_duel if took else inc_duel
    if cur and not (check_free(u, cur) or check_sense(cur)):
        for _ in range(2 if cur_d < 1.0 else 0):
            nb, nd = refine(llm, pllm, u, draft, cur, cur_d, orig, stats)
            if nd > cur_d:
                put_quad(draft, u, nb)
                cur, cur_d, took = nb, nd, True
                remember(nb, nd == 1.0)
                if stats is not None:
                    stats["refined_up"] += 1
            if cur_d >= 1.0:
                break
    final = quad_bars(draft, u)
    best_duel = cur_d if took else best_duel
    return {"q": u["q"], "slot": u["slot"], "off": u["off"], "took": took, "duel": (cur_d if took else inc_duel), "inc_duel": inc_duel,
            "n_candidates": len(pool), "n_clean": len(clean), "n_passed": len(passed), "final": final}


# ------------------------------------------------------------------ the driver
def feedback_for(stats: Counter, lost: bool) -> str:
    msgs = []
    if stats.get("fail_syl", 0) > stats.get("candidates", 1) * 0.5:
        msgs.append("Most candidates missed the syllable counts: write SHORT plain words, count every bar, and cut a word rather than pad.")
    if stats.get("fail_rhyme", 0) > stats.get("candidates", 1) * 0.3:
        msgs.append("Many candidates failed the rhyme: the rhyming bars must share a STRESSED vowel plus the sound after it; choose the end words FIRST (a real common word each), then write the sentence to land on it.")
    if stats.get("fail_sense", 0) + stats.get("fail_thread", 0) > 0:
        msgs.append("Some candidates read as fragments or did not follow from bar to bar: complete sentences, and each bar must follow the last.")
    if lost:
        msgs.append("The current version loses a blind duel to a professionally written quad: it needs a sharper character and a better payoff on the last stressed word.")
    return "\n".join(msgs)


def measure(draft_in: str, workers: int = 6) -> dict:
    """parity snapshot: blind duel of every quad against the original's matching quad + gate failures. Numbers only."""
    pllm = original.private_llm("evolve-measure")
    origs = {u["cluster"]: u for u in original.quads()}
    draft = parse_draft(draft_in)
    us = units()
    def one(u):
        bars = quad_bars(draft, u)
        free = check_free(u, bars)
        return {"q": u["q"], "slot": u["slot"], "duel": duel(pllm, u, bars, origs[f"orig:q{u['q']}"]), "free": [k for k, _, _ in free]}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(one, us))
    return {"duel": sum(r["duel"] for r in rows), "of": len(rows), "rows": rows}


def run(draft_in: str, draft_out: str, rounds: int = 3, n: int = 8, only: Optional[set] = None, workers: int = 6) -> dict:
    llm = LLM(ledger=Ledger(run_id="evolve"))
    pllm = original.private_llm("evolve-duel")
    origs = {u["cluster"]: u for u in original.quads()}
    draft = parse_draft(draft_in)
    us = [u for u in units() if (only is None or u["q"] in only)]
    log = []
    stats = Counter()
    for r in range(1, rounds + 1):
        t0 = time.time()
        rs = Counter()
        fb = feedback_for(stats, True)
        def work(u):
            try:
                return improve_unit(llm, pllm, u, draft, origs[f"orig:q{u['q']}"], fb, n, stats=rs, final=(r == rounds))
            except Exception as e:  # noqa: BLE001 - one quad failing must not stop the night
                return {"q": u["q"], "slot": u["slot"], "off": u["off"], "took": False, "duel": 0.0, "inc_duel": 0.0, "error": str(e)[:120], "final": quad_bars(draft, u)}
        with ThreadPoolExecutor(max_workers=workers) as ex:
            res = list(ex.map(work, us))
        write_draft(draft, draft_out)
        wins = sum(x["duel"] for x in res)
        entry = {"round": r, "minutes": round((time.time() - t0) / 60, 1), "taken": sum(1 for x in res if x["took"]), "duel_score": round(wins, 1), "of": len(res),
                 "stats": dict(rs), "per_quad": {x["q"]: {"took": x["took"], "duel": x["duel"], "clean": x.get("n_clean"), "passed": x.get("n_passed"), "err": x.get("error")} for x in res}}
        log.append(entry)
        LOG.write_text(json.dumps(log, indent=1), encoding="utf-8")
        stats = rs
        print(f"ROUND {r}: duel {entry['duel_score']}/{entry['of']}  replaced {entry['taken']}  stats {dict(rs)}  {entry['minutes']} min", flush=True)
    return {"log": log, "draft": draft}


if __name__ == "__main__":
    import argparse
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("draft_in")
    ap.add_argument("draft_out")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    only = {int(x) for x in a.only.split(",") if x} or None
    run(a.draft_in, a.draft_out, a.rounds, a.n, only, a.workers)
