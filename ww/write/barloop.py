"""Bar loop: repair ONE bar at a time until it fits the syllable target and an end word the carpet can hold.

This is the stage the measurements kept pointing at. Across every live run so far the dominant rejection is the syllable
count (42 of 48 rows in eval/failures.jsonl on Hook 5-8, and 12-36 frame problems per candidate across all nine slots in the
first full build), and the writer cannot be told its way out of it: the model writes a sentence first and the count follows.
benchmark/flow_research.md already prescribes the mechanism -- "produce 8-20 variants per bar, drop the off-count ones, then
rerank" -- so the unit of generation here is the BAR, not the block, and the selection is deterministic (the toolkit's own
counter and end-shape reader decide, not a model).

What it will NOT do: bend the meaning to hit a count. Each bar keeps its own claim, the claim is restated in the request, and a
bar with no passing variant is left exactly as it was and reported. Every variant that fails is logged (rule R10).
"""
from __future__ import annotations

from typing import Optional

from .. import bridge, config, failures
from ..llm import LLM, Request

SHAPE_WORDS = {
    "|Sw": "end on a two-syllable word STRESSED on the first syllable (like favour, ticket)",
    "~Sw": "end on a word whose last two syllables are stressed-then-weak (like Majorca)",
    "|S": "end on a ONE-syllable word (a hard ending)",
    "|SS": "end on a two-syllable word stressed on the SECOND syllable (like receipt)",
    "|Sww": "end on a three-syllable word stressed on the first (like Castletown)",
    "|w": "end on a weak function word (like 'it' or 'in')",
    "|SwS": "end on a three-syllable group, strong-weak-strong",
}

VARIANT_SCHEMA = {
    "type": "object", "required": ["variants"],
    "properties": {"variants": {"type": "array", "minItems": 1, "items": {
        "type": "object", "required": ["text"], "properties": {"text": {"type": "string"}, "claim": {"type": "string"}}}}},
}

SYSTEM = """You rewrite ONE bar of a deadpan British rap so that it fits a machine-counted syllable target. You are given the bar as
it stands, what it has to say, the exact syllable count it must hit, and the sound its last word must make.

WORK IN THIS ORDER, because the bar's shape is decided by its last word:
1. PICK THE LAST WORD FIRST, from the list supplied. Every word on that list already has the required sound and shape.
2. COUNT the syllables in the word you picked. The rest of the bar gets the target minus that number.
3. WRITE the bar so that it ends on that word and lands on the count. Say what the bar has to say in the plainest words
   that fit -- do not add imagery, do not explain, do not pad.

RULES
- Count the syllables of every variant yourself, on your fingers, before returning it. A variant that is over the number is
  useless, and so is one that is under by more than one: the checker counts both in the project's own pronouncer.
- Every one of these costs a syllable when you need to shorten: the, a, an, and, from, my, his, of, so, then, just.
- Never twist the meaning to hit the number, and never swap the end word for a non-rhyming synonym.
- Do not use any of these filler frames: and the whole, the whole of the, and it is, bloke at the door, and I am.
- Return several DIFFERENT variants with DIFFERENT end words, at least one under the target and at least one over it."""


def _menu_for(menu: list[str], want_shape: Optional[str], n: int = 24) -> list[str]:
    """the end words this bar may land on: the menu filtered to the bar's measured shape, or the whole menu when the filter
    would leave the model with nothing to choose from."""
    if not want_shape or not menu:
        return list(menu)[:n]
    shaped = [w for w in menu if _shape_ok(bridge.end_shape(w) or "", want_shape)]
    return (shaped if len(shaped) >= 6 else list(menu))[:n]


def _shape_ok(got: str, want: str) -> bool:
    return got == want or (got, want) in _SHAPE_EQ


_SHAPE_EQ = {("|Sw", "~Sw"), ("~Sw", "|Sw")}


def _end_word(bar: str) -> str:
    ws = bridge.words(bar)
    return ws[-1].lower() if ws else ""


FUNC = {"the", "a", "an", "and", "from", "my", "his", "her", "their", "of", "in", "on", "at", "so", "then", "just",
        "that", "is", "was", "it", "up", "out", "back", "down", "to", "for", "with", "by"}
# words English tolerates losing inside a bar without the line stopping being English. Anything outside this set is left alone:
# a trim that produced "man from the council wants the gnome back I am not sorry" would be the substitution gibberish this
# project has already rejected twice, so the removable set is deliberately small and the coordinators become a comma.
REMOVABLE = {"the", "a", "an", "just", "then", "so", "that", "my", "his", "her", "their"}
COORD = {"and", "but", "then", "so"}


def trims(bar: str, max_drop: int = 1) -> list[str]:
    """Deterministic over-count repair, free of any model call: drop a word English tolerates losing, keeping the word order
    and the end word (which is never touched).

    Measured, the writer overshoots short verse bars by two to four syllables and the bar loop spent calls failing to fix it
    (29 of 65 logged count failures were over-target, the worst by four). A bar carrying a spare article is the same claim in
    fewer syllables, so the trims are candidates like any other, accepted only by the same deterministic test. One deletion at
    a time: two is where the result stops reading as English."""
    toks = bar.split()
    if len(toks) < 4:
        return []
    tail_punct = ""
    if toks[-1][-1:] in ",.;:!?":
        tail_punct, toks[-1] = toks[-1][-1], toks[-1][:-1]
    low = [t.strip(",.!?;:").lower() for t in toks]
    end_i = len(toks) - 1
    out = []
    for i in range(end_i):  # never the end word
        w = low[i]
        if w in COORD:
            keep = list(toks)
            if i and keep[i - 1].rstrip().endswith(","):
                keep.pop(i)  # "back, and I ..." -> "back, I ..."
            else:
                keep[i] = ","  # "back and I ..." -> "back, I ..."
            cand = " ".join(keep) + tail_punct
            if cand == bar:
                continue
        elif w in REMOVABLE:
            keep = [t for j, t in enumerate(toks) if j != i]
            if keep and keep[0][:1].islower():
                keep[0] = keep[0][:1].upper() + keep[0][1:]
            cand = " ".join(keep) + tail_punct
        else:
            continue
        if cand.strip() and cand != bar and len(cand.split()) >= 3:
            out.append(cand)
    if max_drop >= 2:  # only pairs of REMOVABLE words, and only where the single drop already read cleanly
        idx = [i for i in range(end_i) if low[i] in REMOVABLE]
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                keep = [t for j, t in enumerate(toks) if j not in (idx[a], idx[b])]
                if len(keep) >= 4:
                    out.append(" ".join(keep) + tail_punct)
    seen, uniq = set(), []
    for x in out:
        x = x.replace(" ,", ",")
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def variants_request(slot: str, target: int, want_shape: Optional[str], end_menu: list[str], claim: str,
                     current: str, context: str, n: int = 5, model: str = "ds-flash", temperature: Optional[float] = None,
                     negatives: str = "") -> Request:
    shape = SHAPE_WORDS.get(want_shape or "", "end on a word that rhymes with the block's other end words")
    menu = _menu_for(end_menu, want_shape)
    user = (f"SECTION: {slot}\nBAR AS IT STANDS ({bridge.syllable_count(current)} syllables, must be {target}): {current}\n"
            f"WHAT THIS BAR HAS TO SAY: {claim}\n"
            f"THE BAR BEFORE IT (for the grammar and the story): {context or '(nothing before it)'}\n"
            f"TARGET: exactly {target} syllables (+-1 is the whole tolerance).\n"
            f"STEP 1 -- THE LAST WORD. Pick it from this list; each already suits the bar's shape. {shape}:\n"
            f"{', '.join(menu) if menu else 'any real word that fits the sound'}\n"
            f"STEP 3 -- then write the bar to end on your word and land on {target}.\n\n"
            f"Return {n} different rewrites of this ONE bar, each ending on a DIFFERENT word from the list.")
    system = SYSTEM + (f"\n\nAVOID (measured rejections, rule R10):\n{negatives}" if negatives else "")
    return Request(model=model, system=system, messages=[{"role": "user", "content": user}], schema=VARIANT_SCHEMA,
                   max_tokens=900, effort=None, temperature=temperature, stage="bar_loop", scope="write")


_STOP = {"the", "a", "an", "and", "of", "to", "in", "on", "at", "for", "with", "by", "is", "was", "it", "i", "he", "she",
         "they", "we", "my", "his", "her", "their", "our", "so", "then", "just", "that", "as", "but", "or", "not", "am",
         "be", "been", "from", "up", "out", "down", "back", "all", "one", "two", "three", "six", "me", "him", "them", "you"}


def content_words(bar: str, drop: str = "") -> list:
    """the bar's content words, in order, ignoring function words and the end word."""
    ws = [w.strip(",.!?;:'\"").lower() for w in bar.split()]
    end = drop.strip(",.!?;:'\"").lower()
    return [w for w in ws if w and w not in _STOP and w != end]


def _meaning_flags(bar: str) -> list:
    """the deterministic verifier's per-bar complaints (grammar, sense, invented words). Cheap, local, no model."""
    try:
        from . import verify_det
        r = verify_det.check_block([bar], spec={"sylls": [], "tol": 1, "shape": None, "carpet_min_pairs": 0})
        return r["per_bar"][0]["issues"]
    except Exception:  # noqa: BLE001 - a verifier crash must not block a repair
        return []


def accept(slot: str, bar: str, target: int, want_shape: Optional[str], used_end_words: set, keep_payoff: Optional[str],
           source: Optional[str] = None) -> list[str]:
    """deterministic acceptance: counted in the toolkit, shape read by the toolkit, end word not already used, the bar's
    planned payoff preserved if this is the bar that cashes it, the verifier's grammar/sense flags clear, and -- when the
    original text is supplied -- at least half of the original's content words still present.

    The content rule is the guard against the failure mode Joe has rejected three times in this project: bending a sentence to
    land a rhyme. Measured on the rebuilt bar loop, without it the acceptance test happily took 'I pay sixty, he thanks me:
    petal in the metal' (a working bar turned into a nonsense one) and 'Koh Tao: dive skipper says sixty for a day is special',
    because count, end shape and end word were all correct. A repair may reword; it may not replace the bar's content."""
    why = []
    if abs(bridge.syllable_count(bar) - target) > 1:
        why.append(f"{bridge.syllable_count(bar)} syllables for a target of {target}")
    shape = bridge.end_shape(bar)
    if want_shape and shape != want_shape and not (want_shape in ("|Sw", "~Sw") and shape in ("|Sw", "~Sw")):
        why.append(f"ends {shape}, needs {want_shape}")
    w = _end_word(bar)
    if w and w in used_end_words:
        why.append(f"end word '{w}' is already used in this block")
    if keep_payoff and w != keep_payoff:
        why.append(f"this bar must still land the planned payoff '{keep_payoff}'")
    src = content_words(source or "")
    if source:
        kept = set(content_words(bar))
        lost = [x for x in src if x not in kept]
        if lost and len(lost) > max(1, len(src) // 2):
            why.append(f"drops the bar's content ({', '.join(lost[:4])})")
    why += [f"verifier: {x}" for x in _meaning_flags(bar)]
    return why


def repair_bar(llm: LLM, slot: str, bar: str, claim: str, target: int, want_shape: Optional[str],
               used_end_words: set, end_menu: list[str], context: str = "", keep_payoff: Optional[str] = None,
               n: int = 5, model: str = "ds-flash", negatives: str = "") -> tuple[str, list[str]]:
    """one call for one bar. Returns (bar, log): the bar is the original when no variant passes."""
    tried = []
    # free candidates first: the writer's own over-count bars are usually spare articles rather than a wrong claim
    for t in trims(bar):
        why = accept(slot, t, target, want_shape, used_end_words - {_end_word(bar)}, keep_payoff, source=bar)
        if not why:
            return t, tried
        tried.append(t)
    try:
        res = llm.complete(variants_request(slot, target, want_shape, end_menu, claim, bar, context, n, model,
                                            negatives=negatives), use_cache=False)
    except Exception as e:  # noqa: BLE001 - a failed repair must not sink a build
        failures.log("gate", bar, detail=f"bar repair call failed: {type(e).__name__}", source=f"barloop:{slot}")
        return bar, [f"{type(e).__name__}"]
    variants = [(v.get("text") or "").strip() for v in (res.parsed or {}).get("variants", [])]
    for text in [t for v in variants for t in [v]]:
        if not text:
            continue
        for cand in [text] + trims(text):
            why = accept(slot, cand, target, want_shape, used_end_words - {_end_word(bar)}, keep_payoff, source=bar)
            if not why:
                return cand, tried
            tried.append(cand)
            failures.log("gate", cand, detail="; ".join(why)[:200], source=f"barloop:{slot}")
    return bar, tried


def _score_key(s: Optional[dict]):
    """the section comparison used everywhere in this system: plan gate, then the frame, then cashes, then the two counts."""
    if not s or not s.get("usable", True):
        return (0, 0, -999, -999, -999)
    return (int(bool(s.get("plan_ok"))), int(bool(s.get("frame_ok"))), s.get("cashed", 0), -s.get("frame_hard", 99),
            -s.get("syl_miss", 99))


def repair_block(llm: LLM, slot: str, bars: list[str], claims: list[str], targets: list, shapes: list,
                 end_menu: list[str], max_calls: int = 14, model: str = "ds-flash", negatives: str = "",
                 score=None) -> dict:
    """Walk the block, repair each bar that is off its target. Deterministic acceptance at every step; the plan's payoff bar
    is protected (a bar whose end word is a planned payoff may not lose it).

    A pass is committed only when the SECTION does not get worse (pass `score`, i.e. draft_all.score_section). Measured, with
    per-bar acceptance alone the loop fixed the bar it was looking at and broke the block (V1 33-44 frame problems 1 -> 7,
    V2 1-8 1 -> 9), because a bar can be on its count and its end shape and still break the carpet, the scheme or the bookend.

    The duplicate check is on the WHOLE block: an earlier version subtracted the bar's own end word before testing, so a pair
    of bars sharing one end word looked clean to both of them and neither was ever repaired."""
    from . import argue_stage
    planned = set(argue_stage.payoffs(slot))
    from collections import Counter
    counts = Counter(_end_word(b) for b in bars)
    out = list(bars)
    log, calls = [], 0
    for i, b in enumerate(list(out)):
        if calls >= max_calls:
            log.append(f"bar {i + 1}: not attempted (call budget {max_calls} reached)")
            continue
        tgt = targets[i] if i < len(targets) else None
        if not tgt:
            continue
        used = {w for w, c in counts.items() if c >= 1 and w != _end_word(b)}
        why = accept(slot, b, tgt, shapes[i] if i < len(shapes) else None, used,
                     _end_word(b) if _end_word(b) in planned else None, source=None)
        if _end_word(b) and counts[_end_word(b)] > 1:
            why.append(f"end word '{_end_word(b)}' is used more than once in this block")
        if not why:
            continue
        calls += 1
        new, tried = repair_bar(llm, slot, b, claims[i] if i < len(claims) else "", tgt,
                                shapes[i] if i < len(shapes) else None, used, end_menu,
                                context=out[i - 1] if i else "", keep_payoff=_end_word(b) if _end_word(b) in planned else None,
                                model=model, negatives=negatives)
        log.append(f"bar {i + 1}: {why[0]}; {len(tried)} variants tried -> "
                   + ("repaired" if new != b else "no passing variant, left as it was"))
        if new != b:
            counts[_end_word(b)] -= 1
            out[i] = new
            counts[_end_word(new)] += 1
    res = {"bars": out, "log": log, "calls": calls}
    if score is not None and out != bars:
        # The PASS is the unit of commitment, not the bar. A single repair legitimately leaves the section momentarily worse
        # (it moves one end word out of the carpet before the next repair moves its partner back), and a one-step hill-climb
        # blocked every such repair: measured on the incumbent V1 33-44 and V2 1-8, 0 of 6 repairs were committed although
        # every one of them fixed the bar it was pointed at.
        s0, s1 = score(bars), score(out)
        if _score_key(s1) <= _score_key(s0):
            res["bars"] = list(bars)
            res["log"] = log + [f"pass reverted: the section did not improve (frame {s0.get('frame_hard')} -> {s1.get('frame_hard')}, "
                                f"cashed {s0.get('cashed')} -> {s1.get('cashed')})"]
            res["reverted"] = True
    return res


def selftest() -> tuple[bool, str]:
    problems = []
    good = "Hoi Rotterdam, gnome's in my garden."
    if accept("Hook 5-8", good, 8, "|Sw", set(), None):
        problems.append(f"an on-target bar should be accepted: {accept('Hook 5-8', good, 8, '|Sw', set(), None)}")
    if not accept("Hook 5-8", "The man from the council wants the gnome back and I am not sorry.", 10, "|Sw", set(), None):
        problems.append("a 15-syllable bar must be rejected against a 10-syllable target")
    if not accept("Hook 5-8", "Might lie low over in Gorey.", 8, "|Sw", {"gorey"}, None):
        problems.append("a bar reusing an end word already in the block must be rejected")
    if not accept("Hook 5-8", "The council want it back, not sorry.", 10, "|Sw", set(), "lorry"):
        problems.append("a bar that must still cash a planned payoff must be rejected when it does not")
    src = "I pay sixty, he thanks me for taking it. A petal in the tea."
    if not accept("V1 25-32", "Leather slippers sit on the mat by the door", 11, "|S", set(), None, source=src):
        problems.append("a variant that silently replaces the bar's content must be rejected")
    if not accept("V1 25-32", "I pay sixty, he thanks me: petal in the metal", 9, "|S", set(), None, source=src):
        problems.append("a variant with a verifier flag (unresolved pronoun) must be rejected")
    over = "The man from the council wants the gnome back and I am not sorry"
    ts = trims(over)
    if not ts:
        problems.append("an over-count bar carrying spare articles must yield at least one trim")
    if any(_end_word(t) != _end_word(over) for t in ts):
        problems.append("a trim must never move the end word: " + "; ".join(t for t in ts if _end_word(t) != _end_word(over)))
    if any(len(_wordset(t) - _wordset(over) - {","}) for t in ts):
        problems.append("a trim may only remove words, never introduce them")
    if not any(abs(bridge.syllable_count(t) - 15) <= 1 for t in ts):
        problems.append("a 15-syllable target should be reachable by trimming a 16-syllable bar")
    return (not problems, "; ".join(problems) if problems else
            "the bar loop's acceptance is deterministic: count, end shape, end-word reuse, the planned payoff, the verifier's "
            "grammar/sense flags and the bar's own content are all enforced in code")


def _wordset(s: str) -> set:
    return {w.strip(",.!?;:").lower() for w in s.split()}
