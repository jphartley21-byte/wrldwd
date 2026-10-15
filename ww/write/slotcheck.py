"""Slot checker: does a draft block hit the ORIGINAL'S measured structure for that slot? Numbers only (never the original's words).

Targets come from benchmark/original_profile.json + benchmark/flow_template.json + toolkit/match.MANUAL_SCHEME (the by-ear scheme):
  FLOW   syllables per bar (+-tol, exact count reported) and the end SHAPE per bar (|Sw soft ending that starts a word, ~Sw rhyme lands
         mid-word, |S hard ending)                                   -> the facts that survived the labelled-set tests (R9)
  SCHEME every pair of bars the by-ear scheme puts under one letter must rhyme (ww.bridge.rhyme_score >= 0.78; perfect pairs reported)
  SENSE  grammar/referent flags, invented words, unpronounceable words, inventory-of-things bars, filler frames (all from the verifiers)
  COPY   longest word run shared with the original and frame clones (local, numbers only)
Round-2 HARD checks (13 Oct 2026, from the judges' repeated complaints about round 1; numbers from benchmark/slot_targets.json):
  ENDS    no end word repeats inside the block (round 1: pocket x2, wrong x2, tin x3, side x3, remedy x2)
  CARPET  the end-rhyme carpet must reach 85% of the original's pair count for the slot (round 1 V1 25-32: 12 vs 18 -> unrhymed middle)
  VOICE   at least (original's first-person bars - 1) bars contain I / my / me / we ... (round 1: the narrator was an onlooker, 1-2 bars of 8)
  CASH    the writer declares >= n_bars//4 cashed idioms with `#cash <bar> | <idiom> | <payoff word>` trailer lines; the payoff word must be
          the LAST word of that bar and the idiom's words must appear in that bar or the one before
Round-3 HARD checks (13 Oct 2026, after Joe asked why the draft had so many names and why rhyme and flow were far off):
  NAMES   no invented named person (the original names ONE person in 76 bars; round 2 named one in 20 of 76): everyone is a role (the lads,
          my mate, the copper, the in-laws, Mum). `--allow Keith:2` licenses a name for that many bars.
  SUFFIX  end words carried by a suffix (-ing -ed -er -ary -ly ...) are capped at the original's rate (4 of 76): at most 2 per 8 bars, and at
          most 2 sharing one suffix. Round 2 had 19 of 76 (prompt payer / player / bricklayer / naysayer / soothsayer).
  BEAT    the bar's syllables are laid on the ORIGINAL's audio-measured steps; a lexically weak syllable on a downbeat is a stumble. At most one
          per bar, a block mean no more than the original's slot mean + 0.5, and no run of 4+ weak syllables. (Validated against the judges'
          flow scores on 56 round-1 candidates: weak-on-beat rho -0.29, weak-run rho -0.31; the template's spelling-based pattern % had rho 0.09.)
Soft TARGETS (reported, never block): internal-rhyme total >= 70% of the original's, multisyllabic runs >= 50%, narrator-as-subject bars.
Soft, reported against the original's own numbers: internal-rhyme count per bar, the carpet (how many end-pairs rhyme).
An agent runs this on every candidate and fixes the HARD lines before submitting.
"""
from __future__ import annotations

import os

import json
import re
import statistics
import sys

from .. import bridge, config
from . import frames, grammar

SECS = [("Hook 1-4", 0, 4), ("Hook 5-8", 4, 8), ("Hook 9-16", 8, 16), ("V1 1-8", 16, 24), ("V1 9-16", 24, 32), ("V1 17-24", 32, 40),
        ("V1 25-32", 40, 48), ("V1 33-44", 48, 60), ("V2 1-8", 60, 68), ("V2 9-16", 68, 76)]
SCHEME_FLOOR = 0.78
_STEM_STRIP = ("ing", "ed", "es", "s")
_IDIOM_STOP = {"the", "a", "an", "of", "to", "in", "on", "and", "it", "his", "her", "your", "my", "one"}


_SUFFIXES = ("ing", "ings", "ed", "ly", "ers", "er", "ier", "ies", "ary", "ory", "ery", "ation", "ations", "ness", "ful", "able", "ment", "ments", "ous", "ive", "ity", "ish", "est", "less")


def _targets() -> dict:
    p = config.BENCHMARK / "slot_targets.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _stem(w: str) -> str:
    w = w.lower().strip("'")
    for suf in _STEM_STRIP:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def _first_person(bar: str) -> bool:
    import re
    return bool(re.search(r"\b(i|i'm|i've|i'd|i'll|my|me|mine|myself|we|we're|we've|our|us|ours)\b", bridge.norm(bar), re.I))


def _subject_i(bar: str) -> bool:
    import re
    return bool(re.search(r"\b(i|i'm|i've|i'd|i'll|we|we're|we've)\b", bridge.norm(bar), re.I))


_NAME_STRICT = set("""keith dave gaz barry hugh colin terry kev kevin steve dan danny tom tommy mick micky tony gary bob bobby jim jimmy john johnny paul pete peter mike
nigel derek brian clive alan ian martin rob robbie sam ben jack dean craig wayne darren lee ryan liam shaun stuart neil phil gavin graham trevor malcolm
reg ron ronnie ray norman stan sid fred freddie ted teddy norm vince vinnie lenny len alf alfie ollie oliver harry george charlie jamie james andy
andrew nick nicky chris simon richard dick rich rick rod roger ross russ sean scott tim timmy tel tez baz bez wez shaz jaz kez nan nana gran""".split())
_PLACE_TOKENS = set("""douglas hervey fraser bay laxey castletown donegal boomtown ahoy larrau bilbao burgos fermoselle porto bordeaux vitoria gasteiz
lauterbrunnen zurich bern florence ljubljana bratislava vienna zell see munich augsburg amsterdam noord rotterdam bergen oslo marrakesh perth
sydney bali melbourne noosa cairns whitsundays townsville christchurch laos vietnam bangkok koh tao gili trawangan brisbane byron snowdon pen fan
scourie groats dublin mallorca crete cornwall padstow polzeath naples pompeii portsmouth calais dover reading bristol gorey jersey""".split())


def _names_in(bar: str) -> list[str]:
    found = []
    toks = re.findall(r"[A-Za-z']+", bridge.norm(bar))
    for i, t in enumerate(toks):
        lo = t.lower().strip("'")
        if lo.endswith("'s"):
            lo = lo[:-2]
        if not t[0].isupper() or lo in _PLACE_TOKENS:
            continue
        if lo in _NAME_STRICT:
            found.append(lo)
    return found


def _word_of_syllables(bar: str) -> list[str]:
    import flow_fit as ff
    out = []
    for w in re.findall(r"[A-Za-z'å]+", bar):
        out += [w] * len(ff.sylls(w))
    return out


def beat_report(slot: str, bar_index: int, bar: str, start: int) -> dict:
    """lay the bar's syllables on the original's measured steps: which syllables land on downbeats and are weak."""
    import flow_fit as ff
    t = ff.T[start + bar_index]
    weak = ff.sylls(bar)
    n = len(weak)
    if t.get("missing"):
        return {"beat_weak": [], "run": 0}
    o = t["steps"]
    steps = list(o[:n]) + [o[-1] + 1] * max(0, n - len(o))
    words = _word_of_syllables(bar)
    bad = [(k + 1, words[k] if k < len(words) else "?") for k, st in enumerate(steps) if st % 4 == 0 and k < n and weak[k]]
    run = best = 0
    for w in weak:
        run = run + 1 if w else 0
        best = max(best, run)
    return {"beat_weak": bad, "run": best}


def beat_map(slot: str) -> list[list[int]]:
    """per bar: the 1-based syllable positions that land on a downbeat in the original (a stressed syllable belongs there)."""
    import flow_fit as ff
    a = next(s for n, s, e in SECS if n == slot)
    b = next(e for n, s, e in SECS if n == slot)
    out = []
    for i in range(a, b):
        t = ff.T[i]
        out.append([k + 1 for k, st in enumerate(t["steps"]) if st % 4 == 0] if not t.get("missing") else [])
    return out


_PERC = None


def _percussive_vocab() -> set:
    """reduplications and onomatopoeia from the lexicon (lower-case, hyphens as spaces)."""
    global _PERC
    if _PERC is None:
        _PERC = set()
        try:
            from ..lex import lexicon
            for r in lexicon.load():
                if r["group"] in ("redup", "onoma") and not r.get("avoid"):
                    t = re.sub(r"[-\s]+", " ", r["text"].lower()).strip()
                    if t and len(t) <= 24:
                        _PERC.add(t)
        except Exception:    # noqa: BLE001 - optional
            pass
    return _PERC


def sound_devices(bars: list[str]) -> dict:
    """percussive and sound-play devices in a block: reduplicated/onomatopoeic words from the bank, consonant-frame drums, echoes, hidden-name puns."""
    import ear
    vocab = _percussive_vocab()
    perc = []
    for i, b in enumerate(bars):
        txt = " " + re.sub(r"[-\s]+", " ", bridge.norm(b).lower()) + " "
        txt = re.sub(r"[^a-z' ]", "", txt)
        for t in vocab:
            if f" {t} " in txt:
                perc.append((i + 1, t))
                break
    try:
        dr = len(ear.drums(bars))
        ec = len(ear.echoes(bars))
    except Exception:    # noqa: BLE001
        dr = ec = 0
    return {"percussive": perc, "drums": dr, "echoes": ec, "total": len(perc) + dr + ec}


def tag_punches(bars: list[str]) -> list[int]:
    """bars shaped 'clause, <one tag word>' where the tag is a three-syllable stress-first word: the CHAIN-TAG PUNCH (1-based bar numbers)."""
    out = []
    for i, b in enumerate(bars):
        m = re.search(r",\s*([A-Za-z']+)\s*[.!?]?\s*$", bridge.norm(b))
        if m:
            sp = bridge.stress_pattern(m.group(1)) or ""
            if len(sp) == 3 and sp[0] == "1":
                out.append(i + 1)
    return out


def parse_cash(text: str) -> tuple[list[str], list[dict]]:
    """splits a candidate file into bars and `#cash <bar> | <idiom> | <payoff>` declarations."""
    bars, cash = [], []
    for l in text.splitlines():
        t = l.strip()
        if not t:
            continue
        if t.lower().startswith("#cash"):
            parts = [x.strip() for x in t[5:].split("|")]
            try:
                cash.append({"bar": int(parts[0].strip(" :")), "idiom": parts[1], "payoff": parts[2]})
            except (ValueError, IndexError):
                cash.append({"bar": -1, "idiom": t, "payoff": ""})
            continue
        if t.startswith(("#", "=")):
            continue
        bars.append(t)
    return bars, cash


def verify_cash(bars: list[str], cash: list[dict]) -> tuple[list[dict], list[str]]:
    """each declared cash must put its payoff word LAST in its bar and show the idiom's words in that bar or the one before."""
    ok, issues = [], []
    for c in cash:
        b = c["bar"]
        if not (1 <= b <= len(bars)):
            issues.append(f"cash declaration '{c['idiom'][:40]}' names bar {b}, outside 1-{len(bars)}")
            continue
        last = (bridge.words(bars[b - 1]) or [""])[-1].lower()
        pay = (bridge.words(c["payoff"]) or [""])[-1].lower()
        if not pay or _stem(last) != _stem(pay):
            issues.append(f"cash on bar {b}: payoff '{c['payoff']}' is not the bar's last word ('{last}')")
            continue
        text = bridge.norm(" ".join(bars[max(0, b - 2):b])).lower()
        toks = {_stem(w) for w in bridge.words(text)}
        content = [w for w in bridge.words(c["idiom"]) if w.lower() not in _IDIOM_STOP]
        miss = [w for w in content if _stem(w) not in toks]
        if content and len(miss) > len(content) * 0.4:
            issues.append(f"cash on bar {b}: idiom '{c['idiom'][:40]}' does not appear in bars {max(1, b - 1)}-{b} (missing {miss})")
            continue
        ok.append(c)
    return ok, issues


def _toolkit_match():
    import match
    return match


def spec(slot: str) -> dict:
    prof = json.loads((config.BENCHMARK / "original_profile.json").read_text(encoding="utf-8"))[slot]
    tpl = json.loads((config.BENCHMARK / "flow_template.json").read_text(encoding="utf-8"))["bars"]
    a, b = next((s, e) for n, s, e in SECS if n == slot)
    bars = tpl[a:b]
    m = _toolkit_match()
    # a few template bars carry no syllable count (e.g. Hook 9-16 bar 2): fall back to the profile's count, then to the step count
    sylls = [x.get("syl") or prof["bars"][i]["syl"] or len(x.get("steps") or []) for i, x in enumerate(bars)]
    shapes = [x.get("end_shape") or "|S" for x in bars]
    return {"slot": slot, "n": b - a, "sylls": sylls, "shapes": shapes,
            "scheme": m.MANUAL_SCHEME[slot], "internal": prof["internal"], "quad": prof["quad"], "carpet": prof["carpet"],
            "bookends": prof["bookends"]}


def flow_targets(slot: str) -> list[dict]:
    """per bar, the numbers a bar must hit to pass the flow gates: exact syllables, end shape, strong/weak before the rhyme,
    and the most stressed syllables in a row, hard joins, closed-vowel run and restarts the original's same bar allows
    (plus toolkit/flow_par.TOL). Numbers only; the original's words never appear."""
    import flow_fit as ff
    import flow_par as fp
    s = spec(slot)
    a = next(s0 for nm0, s0, e0 in SECS if nm0 == slot)
    tab = fp.par_table() or []
    out = []
    for i in range(s["n"]):
        t = ff.T[a + i]
        par = tab[a + i] if a + i < len(tab) else {}
        timed = "steps" in t
        ri = t.get("rhyme_idx")
        pre = None
        if timed and t.get("weak") and ri is not None and ri >= 1:
            pre = "weak" if t["weak"][ri - 1] else "strong"
        out.append({"bar": i + 1, "song_bar": a + i + 1, "syllables": (par.get("syl") if timed else None) or s["sylls"][i],
                    "exact": timed, "end_shape": s["shapes"][i], "before_rhyme": pre,
                    "max_stress_run": par.get("stress_run", 9) + fp.TOL["stress_run"] if par else None,
                    "max_hard_joins": par.get("hard_joins", 9) + fp.TOL["hard_joins"] if par else None,
                    "max_closed_run": par.get("closed_run", 9) + fp.TOL["closed_run"] if par else None,
                    "max_restarts": par.get("restart", 9) + fp.TOL["restart"] if par else None})
    return out


def targets_text(slot: str) -> str:
    """the flow targets as prompt text for a writer (15 Oct 2026: the writer used to be told syllables and rhyme only, so it
    wrote blind and the gates could only reject)."""
    L = [f"FLOW TARGETS, HARD, bar by bar (a machine rejects the block if any bar misses one):"]
    for t in flow_targets(slot):
        L.append(f"  bar {t['bar']}: {t['syllables']} syllables{' exactly' if t['exact'] else ' (+-1)'}; ends {t['end_shape']}"
                 + (f"; the syllable just before the rhyme is {t['before_rhyme']}" if t["before_rhyme"] else "")
                 + (f"; at most {t['max_stress_run']} stressed syllables in a row, {t['max_hard_joins']} hard word joins "
                    f"(3+ consonants across a gap, an h straight after a cluster, a hiss into a hiss), {t['max_closed_run']} short "
                    f"closed vowels (i as in 'him', u as in 'foot') in a row, {t['max_restarts']} sentence restarts mid-bar"
                    if t["max_stress_run"] is not None else ""))
    return "\n".join(L)


def describe(slot: str) -> str:
    """the target in words, for a writer's brief (no lyrics, no vowel sounds: rhyme PATTERN and strength only)."""
    s = spec(slot)
    groups = {}
    for i, c in enumerate(s["scheme"], 1):
        groups.setdefault(c, []).append(i)
    pairs = "; ".join(f"bars {' & '.join(map(str, v))} rhyme" for v in groups.values() if len(v) > 1)
    shape_words = {"|Sw": "a two-or-more-syllable word ending: strong syllable then weak, the rhyme starting at a word start",
                   "~Sw": "strong then weak, the rhyme landing inside a word/phrase", "|S": "a hard stressed ending"}
    lines = [f"SLOT {slot}: {s['n']} bars. By-ear rhyme scheme {s['scheme']} ({pairs or 'no end rhymes required'}).",
             "Per bar: syllables / ending: " + "; ".join(f"{i + 1}: {n} syl, {sh}" for i, (n, sh) in enumerate(zip(s["sylls"], s["shapes"]))),
             ("END SHAPES MUST MATCH the template on all but a quarter of the bars: |S = the last syllable is the stressed one; |Sw = stressed then ONE weak syllable; |Sww = stressed then TWO weak syllables (a three-syllable tail such as 'carburettor', 'audited'); |w = the rhyme starts on a weak syllable ('... him in'); |SwS = stressed, weak, stressed ('Castletown'). " if slot.startswith("V") else "") +
             "Ending shapes: |Sw = " + shape_words["|Sw"] + "; |S = " + shape_words["|S"] + "; ~Sw = " + shape_words["~Sw"] + ".",
             "BEAT MAP (the original's audio-measured downbeats; put a STRESSED syllable on each listed syllable position, and a weak word like of/the/and/to/a must not sit there): " +
             "; ".join(f"bar {i + 1}: syllables {', '.join(map(str, bm)) if bm else '-'}" for i, bm in enumerate(beat_map(slot))) +
             ". Tools: the checker lists any weak word that lands on a downbeat and caps the block average.",
             f"The original's internal-rhyme count per bar here: {s['internal']}; multisyllabic rhyme pairs: {s['quad'].get('multisyl')}; alliterating bars: {s['quad'].get('allit_bars')}."]
    return "\n".join(lines)


def check(slot: str, bars: list[str], context: list[str] | None = None, tol: int = 1, cash: list[dict] | None = None, allow: dict | None = None) -> dict:
    s = spec(slot)
    m = _toolkit_match()
    hard, rows = [], []
    notes: list = []
    legacy = os.environ.get("WW_LEGACY_FLOW", "0") == "1"      # 1 restores the old gates (beat grid, grader pair floor, carpet share) for comparison
    if len(bars) != s["n"]:
        hard.append(f"expected {s['n']} bars, got {len(bars)}")
    import retired      # toolkit/retired.py (Joe, 15 Oct 2026): the never-approved Hook 1-4 lines are never a bar again
    hard += [f"bar {i + 1}: a retired bar (never approved; Joe 15 Oct 2026: never a bar or a gate again)"
             for i, b in enumerate(bars) if retired.is_retired(b)]
    n = min(len(bars), s["n"])
    gram = grammar.analyse_run(bars, context or [])
    mflags = {i: h for i, _, h in bridge.meaning_flags(bars)}
    import flow_fit as _ffx
    import flow_par as _fpx
    _start = next(s0 for nm0, s0, e0 in SECS if nm0 == slot)
    for i in range(n):
        b = bars[i]
        syl = bridge.syllable_count(b)
        shape = bridge.end_shape(b)
        last = (bridge.words(b) or [""])[-1]
        want = s["shapes"][i]
        ok_shape = shape == want or (want in ("|Sw", "~Sw") and shape in ("|Sw", "~Sw")) or (want == "|Sw" and shape == "|SS" and bridge.stress_pattern(last) == "12")
        if slot.startswith("V"):   # verse templates carry exotic shapes (|Sww, ~w, |SwS): compare HARD (ends on a strong syllable) vs SOFT (ends weak)
            ok_shape = shape.endswith("S") == want.endswith("S") or (not want.endswith("S") and shape == "|SS" and bridge.stress_pattern(last) == "12")
        issues = []
        # EXACT on every bar the original's audio timed (15 Oct 2026): the +-1 allowance rested on the retired "approved" bars.
        # Compared with the original's own TEXT count (same counter), so the original passes by construction. Bars with no
        # audio template (song bars 10 and 60) keep +-tol against the profile.
        timed = "steps" in _ffx.T[_start + i]
        want_syl = (_fpx.par_syl(_start + i + 1) if timed else None) or s["sylls"][i]
        t_ = 0 if timed else tol
        if abs(syl - want_syl) > t_:
            issues.append(f"{syl} syl (need {want_syl}" + (")" if t_ == 0 else f"+-{t_})"))
        if not ok_shape:
            issues.append(f"ends {shape} (need {want})")
        issues += [f"grammar {f}" for f in gram[i]["flags"] if f.split(":")[0] in ("verb_string", "transitive_without_object", "unresolved_pronoun")]
        issues += [f"sense: {x[:50]}" for x in mflags.get(i + 1, [])]
        inv = bridge.invented_words(b)
        if inv:
            issues.append(f"invented word {inv}")
        oov = bridge.oov_words(b)
        if oov:
            issues.append(f"cannot pronounce {oov}")
        rows.append({"bar": i + 1, "text": b, "syl": syl, "want_syl": s["sylls"][i], "shape": shape, "want_shape": want, "end": last, "issues": issues})
        hard += [f"bar {i + 1}: {x}" for x in issues]
    pairs = []
    sc = s["scheme"]
    for i in range(n):
        for j in range(i + 1, n):
            if sc[i] == sc[j]:
                r = bridge.rhyme_score(bars[i], bars[j])
                pairs.append((i + 1, j + 1, r))
                if legacy:
                    if r < SCHEME_FLOOR:
                        hard.append(f"scheme {sc}: bars {i + 1} & {j + 1} must rhyme but score {r}")
                else:
                    # the frozen grader both credits unstressed tails and misses assonant carpets; a scheme pair must rhyme by rapfit (stress-anchored, assonance-aware)
                    from . import rapfit
                    rs_ = rapfit.score(bars[i], bars[j])["score"]
                    if rs_ < rapfit.FLOOR:
                        # a NOTE, not a gate: the pair score cannot see the original's own three-syllable tails (it scores V1 17-24 bars 5-8 at 0.06); the bar-level
                        # stress-anchor rule below (rapfit.check_block, syllable by syllable, ambisyllabic) is the gate and the original passes it with 0 failures
                        notes.append(f"scheme {sc}: bars {i + 1} & {j + 1} score {rs_} on rapfit's pair score (old grader {r}); check by ear")
    rapfit_report = None
    if os.environ.get("WW_RAPFIT_GATE", "1") != "0" and n >= 2:
        # R1 (benchmark/rhyme_theory.md): a rhyme must start on a stressed or long-vowel syllable; an unstressed tail echo is not a rhyme
        from . import rapfit
        rapfit_report = rapfit.check_block(slot, bars[:n])
        hard += [f"rhyme: {x}" for x in rapfit_report["hard"]]
    carpet = bridge.carpet(bars[:n]) if n >= 2 else None
    internal = m.internal_density(bars[:n]) if n else []
    tg = _targets().get(slot)
    targets_missed, extra = [], {}
    allow = {k.lower(): v for k, v in (allow or {}).items()}
    named = {}
    for i in range(n):
        for nm in _names_in(bars[i]):
            named.setdefault(nm, []).append(i + 1)
    for nm, where in sorted(named.items()):
        if len(where) > allow.get(nm, 0):
            hard.append(f"named person '{nm.title()}' on bars {where}: invented people are not allowed (the original names one in 76 bars). Use a role: the lads, my mate, the copper, the driver, the in-laws, Mum" + (f" (licence: {allow.get(nm, 0)} bar(s))" if nm in allow else ""))
    extra["names"] = {k: v for k, v in named.items()}
    start = next(s0 for nm0, s0, e0 in SECS if nm0 == slot)
    bw_total, bw_bars = 0, 0
    for i in range(n):
        br = beat_report(slot, i, bars[i], start)
        bw_total += len(br["beat_weak"])
        bw_bars += 1
        if len(br["beat_weak"]) >= 2:
            msg = f"weak syllables on the beat: {', '.join(f'{w}({k})' for k, w in br['beat_weak'])} (put a stressed syllable on each downbeat)"
            rows[i]["issues"].append(msg)
            # the beat-grid match is registry status failed_validation (it ranked Joe's approved bars below a rejected one): a note, not a gate
            (hard if legacy else notes).append(f"bar {i + 1}: {msg}")
        if br["run"] >= 4:
            msg = f"{br['run']} weak syllables in a row (the original's longest run is 3): it mumbles"
            rows[i]["issues"].append(msg)
            hard.append(f"bar {i + 1}: {msg}")
        # RHYME APPROACH, HARD (Joe, 15 Oct 2026): the syllable before the rhyme is strong/weak as in the original's bar
        import flow_fit as _ff
        ap_ok, ap_k, ap_want = _ff.approach(start + i + 1, bars[i])
        if ap_ok is False:
            wd = _word_of_syllables(bars[i])
            w_ = wd[ap_k - 1] if ap_k - 1 < len(wd) else "?"
            msg = (f"stress before the rhyme: syllable {ap_k} ('{w_}') is {'strong' if ap_want == 'w' else 'weak'}, the original's bar has a "
                   f"{'weak' if ap_want == 'w' else 'strong'} syllable there " + ("(the rhyme must push off a weak syllable, not jam three stresses)"
                   if ap_want == "w" else "(the rhyme needs a stressed syllable to push off)"))
            rows[i]["issues"].append(msg)
            hard.append(f"bar {i + 1}: {msg}")
        # FLOW PAR, HARD (15 Oct 2026): no worse than the original's own bar on stress runs, hard joins, closed-vowel runs and
        # mid-bar restarts (toolkit/flow_par.py; Joe's flagged bars in toolkit/tests/flow_flagged.txt are its test set)
        import flow_par as _fp
        pf = _fp.check(start + i + 1, bars[i])
        if pf:
            msg = "flow worse than the original's bar: " + _fp.describe(pf)
            rows[i]["issues"].append(msg)
            hard.append(f"bar {i + 1}: {msg}")
        rows[i]["beat_weak"] = br["beat_weak"]
    if tg and bw_bars:
        mean_bw = bw_total / bw_bars
        extra["beat_weak_mean"] = round(mean_bw, 2)
        extra["beat_weak_cap"] = round(tg.get("beat_weak_mean", 0.6) + 0.5, 2)
        if mean_bw > extra["beat_weak_cap"]:
            (hard if legacy else notes).append(f"flow: {mean_bw:.2f} weak syllables per bar land on a downbeat, the original's slot average is {tg.get('beat_weak_mean')} (cap {extra['beat_weak_cap']}); see the beat map in slotspec")
    if tg and n:
        ends_ = [(bridge.words(b) or [""])[-1] for b in bars[:n]]
        sfx = [(e, x) for e in ends_ for x in [next((q for q in sorted(_SUFFIXES, key=len, reverse=True) if e.lower().endswith(q) and len(e) > len(q) + 1), None)] if x]
        fam = {"ers": "er", "ier": "er", "ings": "ing", "ations": "ation", "ments": "ment", "ies": "y"}
        grp = {}
        for e, x in sfx:
            grp.setdefault(fam.get(x, x), []).append(e)
        cap = max(1, round(n / 4))
        extra["suffix_ended"] = len(sfx)
        if len(sfx) > cap:
            hard.append(f"{len(sfx)} end words are carried by a suffix ({', '.join(e for e, _ in sfx)}): at most {cap} per {n} bars (the original has 4 in 76). Rhyme different roots on a stressed syllable, not one suffix")
        for f_, ws in grp.items():
            if len(ws) > 2:
                hard.append(f"{len(ws)} end words share the suffix -{f_} ({', '.join(ws)}): at most 2")
    if tg and n:
        ends = [_stem((bridge.words(b) or [""])[-1]) for b in bars[:n]]
        for e in sorted({e for e in ends if e and ends.count(e) > 1}):
            hard.append(f"end word '{e}' repeats on bars {[i + 1 for i, x in enumerate(ends) if x == e]} (no end word may repeat in a block)")
        if carpet and tg["carpet_total"] == carpet["total"]:
            need = int(0.85 * tg["carpet_pairs"])
            extra["carpet_need"] = need
            # 15 Oct 2026: the carpet is HARD on rapfit (rapfit.quality_hard); this old-grader count only runs under WW_LEGACY_FLOW, because
            # as a note it contradicted the gate (posse / solid / wallet / profit: rapfit 6/6, the old grader 3/6)
            if carpet["pairs"] < need and legacy:
                hard.append(f"end-rhyme carpet {carpet['pairs']}/{carpet['total']} rhyme; the original holds {tg['carpet_pairs']}/{tg['carpet_total']} (need >= {need}): too many bars fall off the rhyme family")
        fp = sum(_first_person(b) for b in bars[:n])
        need_fp = max(0, tg["first_person_bars"] - 1)
        extra["fp"], extra["fp_need"] = fp, need_fp
        if fp < need_fp:
            hard.append(f"narrator present in {fp} bars, need >= {need_fp} (the original has {tg['first_person_bars']}): the narrator must be IN the bars (I / my / me / we), not an onlooker")
        subj = sum(_subject_i(b) for b in bars[:n])
        extra["subj"] = subj
        if subj < max(0, tg["subject_bars"] - 2):
            targets_missed.append(f"narrator is the subject (I / I'm / we) in {subj} bars, the original has {tg['subject_bars']}")
        if sum(internal) < 0.7 * tg["internal_total"]:
            targets_missed.append(f"internal rhymes total {sum(internal)}, the original {tg['internal_total']} (aim >= {int(0.7 * tg['internal_total'])})")
        try:
            mq = m.quiet_quad(bars[:n])["multisyl"]
        except Exception:    # noqa: BLE001 - a measure failing must not block a block
            mq = None
        extra["multisyl"] = mq
        if mq is not None and mq < 0.5 * tg["multisyl"]:
            targets_missed.append(f"multisyllabic rhyme runs {mq}, the original {tg['multisyl']} (aim >= {int(0.5 * tg['multisyl'])})")
    if n:
        dv = sound_devices(bars[:n])
        extra["devices"] = dv
        if dv["total"] < max(1, n // 4):
            targets_missed.append(f"sound-play devices {dv['total']} (percussive words {len(dv['percussive'])}, drums {dv['drums']}, echoes {dv['echoes']}); the original has about one per four bars: add a reduplication or onomatopoeic word (ping-pong, click-clack, dot-dot, bish-bosh, thud), a consonant-frame drum, or a homophone echo")
    if n >= 8:
        try:
            import imagery
            ch = imagery.chains(bars[:n])
            br = imagery.bridges(bars[:n])
            extra["chains"] = {"chains": len(ch), "bridges": len(br)}
            if not ch:
                targets_missed.append("image chain: no one picture runs through 3+ consecutive bars (the original's best quads run a chain such as violence or parcel through 3 bars with a bridging verb that belongs to two fields, and land it on a rhyme word); give the block one running conceit instead of a new field per bar")
        except Exception:    # noqa: BLE001 - diagnostic only
            pass
    if n:
        tp = tag_punches(bars[:n])
        extra["tag_punches"] = tp
        if len(tp) > max(1, n // 4):
            hard.append(f"tag punches (clause, comma, one rare three-syllable tag) on bars {tp}: at most {max(1, n // 4)} per {n} bars, the trick announces itself when repeated")
    if n:
        try:
            from . import flowaudit
            sa = flowaudit.section_audit(slot, bars[:n])
            base = flowaudit.load_baseline()
            fb = sa["bars"]
            extra["flow_flags"] = {i + 1: b["flags"] for i, b in enumerate(fb) if b.get("flags")}
            mism = [i + 1 for i, b in enumerate(fb) if any(f.startswith("ends ") for f in b.get("flags", []))]
            gap4 = [i + 1 for i, b in enumerate(fb) if b.get("gaps") and max(b["gaps"]) >= 4]
            extra["end_shape_mismatch"], extra["gap4"] = mism, gap4
            if len(mism) > max(1, n // 4):
                hard.append(f"end shape differs from the template on bars {mism} (the original matches on 97% of bars; allowed: {max(1, n // 4)} per {n}). Check the shape each bar must end on in slotspec: |Sw = stressed syllable then ONE weak syllable, |Sww = then TWO weak syllables, |S = hard")
            if len(gap4) > max(1, n // 8):
                hard.append(f"bars {gap4} have 4+ unstressed syllables in a row between stresses (the original almost never does, 1 bar in 74): they rush and mumble")
            fpb = statistics.mean(len(b.get("flags", [])) for b in fb)
            extra["flow_flags_per_bar"] = round(fpb, 2)
            if base and fpb > base.get("flags_per_bar", 1.6) + 0.5:
                targets_missed.append(f"flow flags per bar {fpb:.2f}, the original {base.get('flags_per_bar', 0):.2f} (stress inversions, reduced syllables on downbeats, stress clashes, end-shape mismatches; see the FLOW lines)")
            par = sa.get("parallel") or {}
            if par.get("n", 0) >= 8:
                rate = par["match"] / par["n"]
                extra["pos_assonance"] = round(rate, 2)
                if base and rate < base.get("pos_assonance", 0.27) - 0.08:
                    targets_missed.append(f"positional assonance {rate:.2f}: where neighbouring bars both stress the same beat, the same vowel lands only {rate:.0%} of the time (the original {base.get('pos_assonance', 0.27):.0%}, chance about 15%). Put the same stressed vowel on the same beat in consecutive bars (e.g. the same vowel on beat 2 of bars 1 and 2), hold it for 2-4 bars, then move to a new vowel")
            if n >= 4:
                pi = flowaudit.parallel_index(slot, bars[:n], base)
                extra["parallel"] = pi
                if pi["index"] < 0.5:
                    targets_missed.append(f"BEAT-PARALLELISM index {pi['index']} (0 = chance, 1 = the original; it is rewarded in selection): put the same stressed vowel on the same beat in consecutive bars. Run  python -m ww.cli beats <file> --slot \"{slot}\"  to see each bar's stressed vowels by step and where neighbouring bars match")
            from . import earcheck
            ear = earcheck.report(slot, bars[:n])
            extra["ear"] = ear
            hardj = [i + 1 for i, b in enumerate(bars[:n]) if any(j["score"] >= 2 for j in earcheck.word_joins(b))]
            extra["hard_join_bars"] = hardj
            # 15 Oct 2026: the per-block allowance let a bad bar hide inside it; the per-bar par in flow_par is the gate now
            if len(hardj) > max(1, n // 4):
                notes.append(f"hard mouth-shape transitions on bars {hardj} (the original has them in 18% of bars, allowed here: {max(1, n // 4)} per {n}): consonant clusters of three or more across a word join, a hiss into a different hiss or th, a breathy h straight after a cluster ('whites, he's'), spread lips through a hiss into r or w ('he's wrecked'). Say each bar aloud at speed; reword the join")
            runon = [i + 1 for i, b in enumerate(fb) if b.get("ends_on_function")]
            extra["run_on_bars"] = runon
            if n >= 8 and not runon:
                targets_missed.append("no run-on bar: every bar closes its own clause. About 1 bar in 7 of the original ends mid-clause (on a function word) so the sentence crosses the bar line; plan one at a group change (bar 4 to 5 or 8 to 9)")
        except Exception:    # noqa: BLE001 - flow audit is advisory unless it fires hard
            pass
    need_cash = max(1, n // 4) if n else 0
    cash_ok, cash_issues = verify_cash(bars[:n], cash or [])
    extra["cash_ok"], extra["cash_need"] = len(cash_ok), need_cash
    hard += cash_issues
    if n and len(cash_ok) < need_cash:
        hard.append(f"cashed idioms: {len(cash_ok)} verified, need >= {need_cash}. Declare each as a line `#cash <bar> | <idiom> | <payoff word>` with the payoff word LAST in its bar")
    fr = frames.scan({"s": bars})
    if fr["banned"] or fr["section"]:
        hard.append(f"filler frames {[p for v in fr['banned'].values() for p, _ in v]}")
    try:
        from ..calib import anticopy
        ac = anticopy.check(bars)
        if not ac["ok"]:
            hard.append(f"too close to the original: shared run of {ac['longest_shared_run']} words / frame clone {ac['frame_clones']}")
    except FileNotFoundError:
        ac = None
    # SENSE (Joe, 14 Oct 2026): every bar must read as a sentence a stranger follows, and each block must hold one thread. HARD. A model read, cached;
    # WW_SENSE=0 switches it off (offline); a network failure never fails a bar (see ww/write/sensecheck.py).
    if os.environ.get("WW_SENSE", "1") != "0":
        try:
            from . import sensecheck
            sc_ = sensecheck.check(bars)
            par_ = sensecheck.slot_par(slot)   # Claude judge: per-slot par from the original (it fails 37/76 of the original's bars per bar)
            for n_, why_ in sc_["fails"]:
                (hard if par_ is None else notes).append(f"sense: bar {n_}: {why_}")
                rows[n_ - 1]["issues"].append(f"sense: {why_}") if n_ - 1 < len(rows) else None
            if par_ is not None and len(sc_["fails"]) > par_["fail"] + sensecheck.SENSE_SLACK:
                hard.append(f"sense: {len(sc_['fails'])} bars fail the sense read {[n for n, _ in sc_['fails']]}; the original's {slot} fails "
                            f"{par_['fail']} (+{sensecheck.SENSE_SLACK} slack): make the worst ones plain sentences")
            if len(bars) >= 3:
                bc_ = sensecheck.block_check(bars)
                if not bc_["ok"]:
                    hard.append(f"sense ACROSS bars: {bc_.get('issue') or bc_.get('thread', '')[:80]} (bars that do not follow: {[n for n, _ in bc_['fails']]})")
        except Exception as e:  # noqa: BLE001
            notes.append(f"sense gate unavailable: {str(e)[:60]}")
    # RECOUNT (14 Oct 2026): a block that tells what happened in time order (past-tense event runs, "stop one / then / next" place lists)
    # instead of claiming something. HARD, par from the original (toolkit/recount.py; registry: validated). WW_RECOUNT=0 switches it off.
    if os.environ.get("WW_RECOUNT", "1") != "0":
        try:
            import recount as _rc
            _m = _rc.section_measures(bars)
            hard += [f"recount: {x.split(': ', 1)[-1]}" for x in _rc.section_fails(slot, _m)]
            notes.append(f"recount codes {_m['codes']} (E event, I itinerary, s stance)")
        except Exception as e:  # noqa: BLE001  (spaCy missing: say so, never pass silently as if measured)
            notes.append(f"recount unavailable: {str(e)[:60]}")
    try:
        from . import cadence
        cad = cadence.check(slot, bars)
        notes += [f"cadence: {x}" for x in cad["notes"]]
    except Exception:  # noqa: BLE001
        cad = {"misses": 0}
    return {"slot": slot, "ok": not hard, "hard": hard, "rows": rows, "scheme": sc, "pairs": pairs, "carpet": carpet, "rapfit": rapfit_report, "notes": notes, "cad_misses": cad["misses"],
            "internal": internal, "internal_orig": s["internal"], "copy": ac, "targets_missed": targets_missed, "extra": extra}


def report(r: dict) -> str:
    L = [f"== {r['slot']}  by-ear scheme {r['scheme']}"]
    for x in r["rows"]:
        flag = "OK  " if not x["issues"] else "FIX "
        L.append(f"{flag}{x['bar']}  {x['text'][:58]:58s} {x['syl']:2d} syl (want {x['want_syl']})  ends {x['shape']} (want {x['want_shape']})  [{x['end']}]" +
                 (("   <- " + "; ".join(x["issues"])) if x["issues"] else ""))
    if r["pairs"]:
        L.append("rhyme pairs required by the scheme: " + ", ".join(f"{a}&{b}={s}" for a, b, s in r["pairs"]) + f"  (need >= {SCHEME_FLOOR}; 1.0 is perfect)")
    if r["carpet"]:
        L.append(f"end-rhyme carpet {r['carpet']['pairs']}/{r['carpet']['total']} pairs rhyme (min {r['carpet']['min']})")
    L.append(f"internal rhymes per bar: yours {r['internal']}  original {r['internal_orig']}")
    if r["copy"]:
        L.append(f"anti-copy: longest word run shared with the original {r['copy']['longest_shared_run']}; frame clones {r['copy']['frame_clones']}")
    ex = r.get("extra") or {}
    if ex:
        L.append(f"narrator bars {ex.get('fp')} (need {ex.get('fp_need')}), as subject {ex.get('subj')}; cashed idioms verified {ex.get('cash_ok')} (need {ex.get('cash_need')}); carpet need {ex.get('carpet_need')}; multisyllabic runs {ex.get('multisyl')}")
    if ex.get("devices"):
        dv = ex["devices"]
        L.append(f"sound-play devices {dv['total']}: percussive words {[w for _, w in dv['percussive']]}, drums {dv['drums']}, echoes {dv['echoes']}")
    if ex.get("flow_flags"):
        for bi, fl in ex["flow_flags"].items():
            L.append(f"FLOW bar {bi}: " + "; ".join(fl))
        if ex.get("parallel"):
            pr = ex["parallel"]["raw"]
            L.append(f"BEAT-PARALLELISM INDEX {ex['parallel']['index']} ({ex['parallel']['points']} points per bar pair; same-vowel matches on shared downbeats {pr['m_down']}, on other shared steps {pr['m_other']}, shared stressed steps with different vowels {pr['s_only']}, over {pr['pairs']} pairs)  [0 = chance, 1 = the original, cap 1.5]")
        L.append(f"flow flags per bar {ex.get('flow_flags_per_bar')} (original ~1.5); run-on bars {ex.get('run_on_bars')}; same-vowel-on-same-beat rate {ex.get('pos_assonance')} (original ~0.27)")
    for ln in ex.get("ear", []):
        L.append("EAR " + ln)
    if ex.get("tag_punches"):
        L.append(f"tag punches on bars {ex['tag_punches']}")
    if ex.get("chains"):
        L.append(f"image chains {ex['chains']['chains']}, bridging words {ex['chains']['bridges']}")
    if ex.get("names"):
        L.append("named people: " + ", ".join(f"{k.title()} bars {v}" for k, v in ex["names"].items()))
    if "beat_weak_mean" in ex:
        L.append(f"weak syllables on downbeats {ex['beat_weak_mean']}/bar (cap {ex['beat_weak_cap']}); end words carried by a suffix {ex.get('suffix_ended')}")
    for t in r.get("targets_missed", []):
        L.append("TARGET MISSED (not blocking, try to fix): " + t)
    tm = f"; {len(r['targets_missed'])} target(s) missed" if r.get("targets_missed") else ""
    L.append("VERDICT: " + (f"PASS (all hard checks{tm})" if r["ok"] else f"FAIL - {len(r['hard'])} hard issue(s): " + " | ".join(r["hard"][:8])))
    return "\n".join(L)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="ww check")
    ap.add_argument("--slot", required=True)
    ap.add_argument("--tol", type=int, default=1)
    ap.add_argument("--context", default="", help="earlier bars of the same verse, '|' separated (for pronoun antecedents)")
    ap.add_argument("--allow", default="", help="licensed names, e.g. Keith:2 (bars)")
    ap.add_argument("file", nargs="?", default="-")
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    bars, cash = parse_cash(text)
    allow = {}
    for part in [x for x in a.allow.split(",") if x.strip()]:
        nm, _, cnt = part.partition(":")
        allow[nm.strip()] = int(cnt or 1)
    r = check(a.slot, bars, [c.strip() for c in a.context.split("|") if c.strip()], a.tol, cash, allow)
    print(report(r))
    return 0 if r["ok"] else 1


def selftest() -> tuple[bool, str]:
    import retired
    problems = []
    s = spec("Hook 5-8")
    if s["n"] != 4 or s["scheme"] != "AAAA" or len(s["sylls"]) != 4:
        problems.append(f"Hook 5-8 spec wrong: {s}")
    d = describe("Hook 9-16")
    if "AABACBDB" not in d or "bars 1 & 2" not in d:
        problems.append("describe() should state the Hook 9-16 by-ear scheme and its pairs")
    # 15 Oct 2026: this used to require the four Hook 1-4 bars once called "Joe's accepted bars" to pass. Joe: never
    # approved, never a bar or a gate again. Now: a retired bar is a hard failure (tested with a stand-in hash).
    probe = "Stand in line for the retired bar test"
    retired.RETIRED.add(retired.digest(probe))
    try:
        r = check("Hook 1-4", ["Hoi Rotterdam beg your pardon", probe, "Look it fell off of a lorry", "Ten feet of it guards my garden"])
    finally:
        retired.RETIRED.discard(retired.digest(probe))
    if not any("retired bar" in h for h in r["hard"]):
        problems.append(f"a retired bar must fail the slot check: {r['hard']}")
    # the flow par gate (15 Oct 2026): every bar Joe flagged for flow fails it
    import flow_par as _fp
    if _fp.par_table() and any(not _fp.check(b, line) for b, line, _ in _fp.flagged()):
        problems.append("every bar in toolkit/tests/flow_flagged.txt must fail the flow par gate")
    # the rhyme-approach gate (15 Oct 2026): three stresses jammed before the rhyme fail; a weak push-off passes
    import flow_fit as _ff
    if _ff.approach(9, "I'm wanted in Boomtown see")[0] is not False or _ff.approach(9, "I'm wanted in Zell am See")[0] is not True:
        problems.append("the rhyme-approach rule must fail 'Boomtown see' and pass a weak syllable before the rhyme")
    # round-2 gates: a cash declaration must end on its payoff word; repeated end words and an absent narrator fail
    bars, cash = parse_cash("I sold the lot, worth a fortune, off the back of a lorry\n#cash 1 | off the back of a lorry | lorry\n#cash 1 | off the back | back\n")
    ok, bad = verify_cash(bars, cash)
    if len(ok) != 1 or len(bad) != 1:
        problems.append(f"verify_cash should accept the payoff-last declaration and reject the other: ok={ok} bad={bad}")
    rr = check("Hook 5-8", ["Hey Rotterdam I own the quarry", "Council want the gnome back, I am not sorry", "Gnome off the back of a lorry", "Might lie low over in lorry"],
               cash=[{"bar": 3, "idiom": "off the back of a lorry", "payoff": "lorry"}])
    if not any("repeats" in h for h in rr["hard"]):
        problems.append("a repeated end word (lorry twice) should be a hard failure")
    nn = check("V1 9-16", ["Bunk with a bike", "Bank replied", "Keith had a word", "Keith as guide", "Paint on the van", "Gaz asks", "Gaz runs", "Keith updates"])
    if not any("narrator present" in h for h in nn["hard"]):
        problems.append("a block with no I/my/me bars should fail the narrator gate")
    return (not problems, "; ".join(problems) if problems else "specs read from the profile; a retired bar fails; cash/ends/narrator gates fire")


if __name__ == "__main__":
    raise SystemExit(main())
