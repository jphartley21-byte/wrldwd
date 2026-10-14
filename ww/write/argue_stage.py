"""Argument stage (the layer that was missing): the SECTION'S ARGUMENT AND PAYOFF are the input, not a travel fact.

Why this exists (measured 14 Oct 2026). The 23 slot-rounds in eval/*.json generated candidates from travel FACTS: best-of-N sat 1.0-3.5
points below the reference on the judges' own 0-10 craft axes, and 6x the candidates (7 -> 44, Hook 5-8) moved the best by 0.00. The
failure was not supply: eval/_plan_v3.json had already designed, per section, the argument in one sentence, the mechanisms, the payoff
word and its bar. That layer was never an input to the generator, so the draft implements the plan's SOUND architecture almost perfectly
(0 repeated end words, 73/76 bars within +-1 syllable of the audio frame) and cashes 2 of the 14 payoffs the plan named. The "Gorey"
blocks in eval/_round4.json show the plan-true material existing and being outscored by fact-seeded rivals, because nothing measured it.

What this module provides:
  brief(slot)          the plan's section record: argument, mechanisms (mapped to seed_stage names), planned payoff words (from the
                       concepts), the ledger phrases assigned to that section, the per-bar beats with their syllable counts and end
                       shapes, facts, callbacks, closer.
  seed_request(slot)   a seed prompt whose FACT is the section's ARGUMENT, constrained to the plan's mechanisms and to the plan's own
                       payoff words (the payoff word is chosen from the plan, not invented).
  check_block(slot, bars)  the PLAN GATE: deterministic findings on whether the block does the job the plan gave it. HARD: no planned
                       payoff word closes any bar (the defect that left 13 of 14 payoffs out of the draft); end word repeated inside the
                       block; fewer than a quarter of the bars cashed. SOFT, reported with counts: planned-payoff coverage, first-person
                       share, per-bar end shape vs the plan's, closers, mechanism count.
  guidance(slot)       the closed loop: negatives assembled from eval/failures.jsonl (rule R10/R11), which nothing previously read.

This gate enforces OUR PLAN, not the original. It is therefore switchable (the driver takes --no-plan) and it is not part of
toolkit/calibrate.py, whose benchmark is the original's own numbers. Applying it is the point: a section that ignores its argument is
currently indistinguishable from one that does.
"""
from __future__ import annotations

import io
import json
import re
from dataclasses import dataclass
from typing import Optional

from .. import config, failures
from . import seed_stage

import os as _os
from pathlib import Path as _Path
# WW_PLAN overrides the plan file: a premise plan from ww/write/premise.py (eval/_plan_premise_ID.json), or a migrated private plan
PLAN_PATH = (_Path(_os.environ["WW_PLAN"]) if _os.environ.get("WW_PLAN") else
             next((p for p in (config.EVAL_DIR / "_plan_v5.json", config.EVAL_DIR / "_plan_v4.json") if p.exists()), config.EVAL_DIR / "_plan_v3.json"))   # v5 = claims not events, cadence per block (14 Oct 2026)   # v4 = the story seeds rewritten to Joe's real events (13 Oct 2026)

# the plan's mechanism numbering -> the seed stage's mechanism names (the plan labels them "1 CASHED IDIOM", "8 EUPHEMISM AS LOGISTICS"...)
MECH_BY_NUMBER = {
    "1": "cashed_idiom", "2": "homophone_pun", "3": "loanword_soundalike", "4": "one_word_two_senses",
    "5": "euphemism_as_logistics", "6": "rhyming_slang_swap", "7": "number_ladder", "8": "euphemism_as_logistics",
    "9": "bathos_closer",
}
_PLAN_CACHE = None


def load_plan() -> dict:
    global _PLAN_CACHE
    if _PLAN_CACHE is None:
        _PLAN_CACHE = json.load(io.open(PLAN_PATH, encoding="utf-8"))
        extra = config.EVAL_DIR / "plan_extra_sections.json"          # sections the plan lacks (Hook 1-4), authored later and flagged as such inside the file
        if extra.exists():
            have = {s["slot"] for s in _PLAN_CACHE["plan"]["sections"]}
            add = [s for s in json.load(io.open(extra, encoding="utf-8")) if s["slot"] not in have]
            _PLAN_CACHE["plan"]["sections"] = add + _PLAN_CACHE["plan"]["sections"]
    return _PLAN_CACHE


def slots() -> list[str]:
    return [s["slot"] for s in load_plan()["plan"]["sections"]]


def _section(slot: str) -> dict:
    for s in load_plan()["plan"]["sections"]:
        if s["slot"] == slot:
            return s
    raise KeyError(f"{slot} is not a planned section (planned: {', '.join(slots())})")


def ledger() -> dict:
    """{slot: [stock phrase, ...]} parsed from the spine's own ledger rule. The plan's one-cash-per-phrase discipline, machine-readable."""
    for rule in (load_plan()["plan"].get("spine") or {}).get("voice_rules") or []:   # a premise plan has no spine ledger
        if rule.strip().startswith("Each stock phrase is cashed ONCE"):
            body = rule.split("Ledger:", 1)[-1]
            out = {}
            for phrase, slot in re.findall(r"([a-z][a-z \-']+?)\s*\(([^)]+)\)", body):
                out.setdefault(slot.strip(), []).append(phrase.strip())
            return out
    return {}


def mechanisms(slot: str) -> list[str]:
    """the section's mechanisms as seed_stage names, in the plan's order."""
    out = []
    for m in _section(slot).get("mechanisms") or []:
        n = re.match(r"\s*(\d)", m)
        key = MECH_BY_NUMBER.get(n.group(1)) if n else None
        if key and key not in out:
            out.append(key)
    return out


def payoffs(slot: str) -> list[str]:
    """the payoff words the plan designed for this section (concepts first, then the ledger's last words, then any word the
    section's own beats name as a payoff). Never invented here."""
    out = []
    for c in _section(slot).get("concepts") or []:
        w = (c.get("payoff_word") or "").strip().lower()
        if w and w not in out:
            out.append(w)
    for phrase in ledger().get(slot, []):
        w = phrase.split()[-1].lower()
        if w and w not in out:
            out.append(w)
    for r in _beat_rows(slot):
        for m in re.finditer(r"(?:ends? on|payoff|closing on|rhyme word is)[^.;]*?['\"]?([a-z]{3,})['\"]?\s*(?:\(|last|closing|$)", r["content"], re.I):
            w = m.group(1).lower()
            if w not in out:
                out.append(w)
    return out


def named_in_beats(slot: str, word: str) -> bool:
    """a payoff the plan named in the bar's job text but not in its concept list (e.g. Hook 5-8 bar 1's 'garden'), so a
    legitimate seed is not rejected for a bookkeeping gap in the plan."""
    text = " ".join(f"{r['job']} {r['content']}" for r in _beat_rows(slot)).lower()
    return bool(re.search(r"\b" + re.escape(word.lower()) + r"\b", text))


def amendment(slot: str) -> dict:
    """A measured conflict between the plan and the slot, recorded rather than patched silently.

    Found 14 Oct 2026 by running the plan gate and the slot frame on the same candidates: the plan designs Hook 5-8 as two
    rhyme pairs (A: garden/pardon, B: lorry/sorry) and puts 'garden' in bar 1's own job, while the slot's measured carpet is a
    MONORHYME -- the original holds 6 of 6 end-pairs and slotcheck requires 85% of them; the repo's own accepted Hook 5-8
    (Zurich/traffic/panic/Munich) is a monorhyme too. Every plan-true candidate therefore failed the carpet. The resolution is
    a plan amendment: one family per block, chosen as the family with the most planned payoffs; the other planned payoff words
    keep their turn inside bars or in the next block.
    """
    from .. import bridge
    fams = families(slot)
    lock = family_lock(slot)
    if len(fams) < 2 or not lock:
        return {}
    others = [w for g in fams if g != lock for w in g]
    return {"slot": slot, "kind": "carpet_family", "kept_family": lock, "deferred": others,
            "measured": "the slot's original holds 6/6 end pairs; a block mixing two families scores 2/6",
            "change": f"all four end words in one family ({'/'.join(lock)}); {', '.join(others)} may appear inside a bar"}


def amendments() -> dict:
    return {s: amendment(s) for s in slots() if amendment(s)}


def plan_jobs(slot: str) -> list[str]:
    """the plan's per-bar jobs, as the writer prompt's job list. The writer is told what each bar in THIS section must do,
    instead of the generic four hook jobs. Where the plan names an end word from a family the slot's carpet cannot hold, the
    recorded amendment replaces that word with the kept family, and the substitution is printed rather than hidden."""
    rows = _beat_rows(slot)
    lock = family_lock(slot)
    am = amendment(slot)
    out = []
    for r in rows:
        text = f"{r['label']}: {r['job']} -- {r['content']}".strip()
        if am:
            for w in am["deferred"]:
                if re.search(r"\b" + re.escape(w) + r"\b", text, re.I):
                    text = re.sub(r"\b" + re.escape(w) + r"\b", f"[{w}: use one of {', '.join(lock)} instead]",
                                  text, flags=re.I)
            if "[" in text:
                text += ("  (AMENDED: this slot's carpet is a monorhyme, so every end word must come from one family; "
                         "see eval/plan_amendments.json)")
        out.append(text)
    try:
        from . import cadence
        out.append(cadence.describe(slot))
    except Exception:  # noqa: BLE001 - a missing cadence must not stop a build
        pass
    return out or None


# MOVES, not beats (14 Oct 2026). The plan's per-bar `beats` were an itinerary ("the last sight", "the exit", "then the ferry"): the
# writer was handed the trip in time order and wrote it back in time order, which toolkit/recount.py now measures (the original's song
# recount share is 0.20; every draft built from beats measured 0.50-0.78). A move is what a bar DOES to the listener; a true fact is an
# INGREDIENT the move transforms, never a step in a timeline.
MOVES = {
    "claim": "state something about the narrator or the world as plain fact, present tense, no time order",
    "flex": "a boast: something big or illicit said flatly in an everyday register",
    "deflate": "drop the big thing to a small, domestic or admin detail",
    "aside": "a one-bar stamp: a place, a local word, a brand or a greeting, said in passing",
    "callback": "return to an earlier prop or claim with a new verb",
    "cash": "a stock phrase cashed literally, the payoff word in the rhyme slot",
}
TRANSFORMS = ["exaggerate", "invert", "understate", "re-file as admin", "hypothetical", "boast", "as routine", "none"]
_MOVE_KEYS = [("cash", r"idiom|cash|stock phrase|pun|double"), ("aside", r"greet|hello|stamp|place|local word|brand|name"),
              ("callback", r"callback|return|again"), ("deflate", r"clos|exit|small|petty|bathos|deflat|modal|might|admin|detail"),
              ("flex", r"boast|brag|flex|illicit|big|menace|extraordinary")]


def beats_to_moves(section: dict) -> list[dict]:
    """migrate a plan section's itinerary `beats` to `moves` (deterministic, keyword-based; the source text is kept as the ingredient).
    The last bar of a block defaults to deflate (the original's runs end on a closer that drops from big to small)."""
    beats = section.get("beats") or []
    out = []
    for k, b in enumerate(beats):
        text = f"{b.get('job', '')} {b.get('content', '')}".lower()
        move = next((m for m, pat in _MOVE_KEYS if re.search(pat, text)), None)
        if move is None:
            move = "deflate" if k == len(beats) - 1 and len(beats) > 1 else "claim"
        transform = {"flex": "exaggerate", "deflate": "understate", "cash": "none", "aside": "none", "callback": "invert"}.get(move)
        if transform is None:
            transform = "re-file as admin" if re.search(r"report|chore|delivery|round|admin|errand", text) else "as routine"
        out.append({"bars": b.get("bars") or b.get("bar") or "", "move": move, "transform": transform,
                    "source": b.get("content", ""), "was_job": b.get("job", "")})
    return out


def migrate_plan(path_in, path_out=None) -> int:
    """write a copy of a plan with `moves` added to every section that has only `beats` (the beats are kept for the record).
    Returns the number of sections migrated. Used for Joe's private eval/_plan_v5.json, which is git-ignored and absent here."""
    d = json.load(io.open(path_in, encoding="utf-8"))
    secs = d["plan"]["sections"] if isinstance(d, dict) and "plan" in d else d
    n = 0
    for sec in secs:
        if sec.get("beats") and not sec.get("moves"):
            sec["moves"] = beats_to_moves(sec)
            n += 1
    io.open(path_out or path_in, "w", encoding="utf-8").write(json.dumps(d, indent=1, ensure_ascii=False))
    return n


def _beat_rows(slot: str) -> list[dict]:
    """one row per planned bar: {label, n, syl, shape, job, content, move, transform} (the plan writes the bar's syllable count and end
    shape in the label). A section with `moves` is read as moves; a section with only `beats` is migrated on the fly, so the writer
    never sees a timeline: `job` is the move and its transform, `content` is the fact as an INGREDIENT."""
    sec = _section(slot)
    moves = sec.get("moves") or beats_to_moves(sec)
    rows = []
    for b in moves:
        label = str(b.get("bars") or b.get("bar") or "")
        m = re.search(r"bar[s]?\s*([\d\-–and ]+)", label)
        rng = m.group(1).strip() if m else ""
        syl = re.search(r"(\d+)\s*(?:syl|,)", label)
        shapes = re.findall(r"\|S+[wS]*|~[wS]+", label)
        mv = b.get("move", "claim")
        tf = b.get("transform", "none")
        job = f"MOVE {mv} ({MOVES.get(mv, mv)})" + (f"; transform the ingredient: {tf}" if tf and tf != "none" else "")
        src = b.get("source", "")
        rows.append({"label": label or rng, "bars": rng, "syl": int(syl.group(1)) if syl else None,
                     "shape": shapes[0] if shapes else None, "job": job, "move": mv, "transform": tf,
                     "content": f"ingredient: {src}" if src else ""})
    return rows


def plan_sylls(slot: str) -> list:
    """per-bar target syllable counts from the plan, expanded to one entry per bar (None where the plan did not state one)."""
    n = _slot_size(slot)
    out = [None] * n
    for r in _beat_rows(slot):
        nums = [int(x) for x in re.findall(r"\d+", r["bars"] or "")]
        for i in nums:
            if 1 <= i <= n:
                out[i - 1] = r["syl"]
    return out


def target_sylls(slot: str) -> list:
    """the per-bar syllable targets the bar loop repairs against: the plan's number where it states one, and the ORIGINAL's
    audio-measured count where it does not. The plan leaves most verse bars blank (V1 33-44 states one number in twelve), so
    using plan_sylls alone left the bar loop touching four bars of a twelve-bar section. The measured frame is the instrument;
    the plan's label is a restatement of it, and is kept where it exists because the plan also states the shape."""
    n = _slot_size(slot)
    out = plan_sylls(slot)
    try:
        from . import slotcheck
        meas = slotcheck.spec(slot)["sylls"]
    except Exception:  # noqa: BLE001 - no frame must not stop a build
        meas = []
    for i in range(n):
        if not out[i] and i < len(meas):
            out[i] = meas[i]
    return out


def target_shapes(slot: str) -> list:
    """the per-bar end shapes from the measured frame (what check_all and the audio template demand)."""
    try:
        from . import slotcheck
        return slotcheck.spec(slot)["shapes"]
    except Exception:  # noqa: BLE001
        return []


def _slot_size(slot: str) -> int:
    from .slotcheck import SECS
    for name, a, b in SECS:
        if name == slot:
            return b - a
    raise KeyError(slot)


def brief(slot: str) -> dict:
    s = _section(slot)
    return {"slot": slot, "argument": s.get("argument") or "", "mechanisms": mechanisms(slot),
            "mechanism_labels": s.get("mechanisms") or [], "payoffs": payoffs(slot), "ledger": ledger().get(slot, []),
            "beats": _beat_rows(slot), "facts": s.get("facts_used") or [], "callbacks_in": s.get("callbacks_in") or "",
            "callbacks_out": s.get("callbacks_out") or "", "closer": s.get("closer") or "",
            "critic_note": _critic_note(slot)}


def _critic_note(slot: str) -> str:
    """the plan's own critic already reviewed the plan; its amendment for this section is the best available negative guidance."""
    for a in load_plan()["critic"].get("amendments") or []:
        if a.get("slot") == slot:
            return f"{a.get('problem','')} FIX: {a.get('change','')}"
    return ""


def families(slot: str) -> list[list[str]]:
    """The planned payoff words grouped by RHYME FAMILY. The slot's measured carpet is a monorhyme (the original's Hook 5-8
    holds 6 of 6 end-pairs; slotcheck requires 85% of them), while the plan designs its payoffs as two pairs (lorry/sorry and
    garden/pardon). A four-bar block can only carry ONE family, so the seed must pick a family, not a word -- that conflict is
    why every plan-true candidate failed the carpet (measured 14 Oct 2026)."""
    from .. import bridge
    out: list[list[str]] = []
    for w in payoffs(slot):
        for grp in out:
            if bridge.rhyme_score("a " + grp[0], "a " + w) >= 0.85:
                grp.append(w)
                break
        else:
            out.append([w])
    return out


def family_lock(slot: str) -> list[str]:
    """the family the seed should aim at: the largest group of planned payoffs that share a rhyme, so the block's carpet can
    hold while every other planned payoff still gets its own section-level turn (they can sit inside bars, or in the next block)."""
    fams = families(slot)
    if not fams:
        return []
    return max(fams, key=lambda g: (len(g), -len(g[0])))


SEED_SCHEMA_ARGS = seed_stage.SEED_SCHEMA

ANTI_RECOUNT = ("NOT A DIARY. The section argues something; it does not tell the trip. Never chain past-tense events ('we left... we rode... "
                "we lost...') and never sequence places ('stop one... then... next...'): the original's longest run of past-tense event bars is "
                "three, and it never lists places in time order (toolkit/recount.py fails a block that does). A true fact may be moved anywhere, "
                "exaggerated, inverted, understated or re-filed as admin; a flagged embellishment (persona) is allowed.")


def seed_request(slot: str, n: int = 6, model: str = "ds-flash", effort: str = "high",
                 temperature: Optional[float] = None, negatives: str = "", kit: str = ""):
    """a seed prompt whose FACT is the section's argument, whose mechanisms are the plan's, and whose payoff word must be the plan's."""
    from ..llm import Request
    b = brief(slot)
    lock = family_lock(slot)
    fams = families(slot)
    fr = seed_stage.load_frames()
    mechs = "\n".join(f"- {k}: {seed_stage.MECHANISMS[k]}" for k in ((b["mechanisms"] or ["euphemism_as_logistics", "bathos_closer"]) + (["lore_allusion"] if kit else [])))
    system = (seed_stage.SYSTEM_TMPL.format(
        persona=seed_stage.PERSONA,
        mechs=mechs,
        burnt="; ".join(fr["burnt"]),
        cliches=", ".join(seed_stage.CLICHES),
        shape_rule=seed_stage.SHAPE_RULES["trochee"]) +
        f"\n\nTHIS SECTION ALREADY HAS AN ARGUMENT. Your seeds do not choose the subject; they find the joke inside it.\n"
        f"ARGUMENT (one sentence, the whole section must serve it): {b['argument']}\n"
        + (f"PAYOFF WORD: it MUST be one of {', '.join(lock or b['payoffs'])}. All four bars of the block end on words that "
           f"RHYME WITH EACH OTHER, so the payoff family has to be one family; the section's other planned payoff words "
           f"({', '.join(w for w in b['payoffs'] if w not in (lock or []))}) may appear INSIDE a bar instead.\n"
           if (lock or b["payoffs"]) else
           "PAYOFF WORD: the plan names none (a premise plan): choose a common word that cashes the ARGUMENT, and the block's end "
           "words must rhyme with it on a stressed syllable.\n")
        + (f"OTHER families available in this section if you need a different pair: "
           f"{'; '.join('/'.join(g) for g in fams if g != lock)}\n" if [g for g in fams if g != lock] else "") +
        f"MECHANISMS: use only the mechanisms listed above, one per seed, at most one pun mechanism in the set.\n"
        f"BAR MOVES (what each bar DOES to the listener -- not a timeline):\n" + "\n".join(f"  - {r['label']}: {r['job']} {r['content']}" for r in b["beats"])
        + "\n\n" + ANTI_RECOUNT)
    if b["critic_note"]:
        system += f"\n\nThe plan's own critic flagged this section before writing: {b['critic_note']}"
    if negatives:
        system += f"\n\nAVOID (measured failures from earlier rounds, rule R10):\n{negatives}"
    if kit:
        allowed = (b["mechanisms"] or ["euphemism_as_logistics", "bathos_closer"]) + ["lore_allusion"]
        system += (f"\n\n{kit}\n\nKIT RULE: at least {max(2, n // 3)} of the {n} seeds MUST use mechanism lore_allusion, with `entity` set to the exact name of "
                   f"one kit item; its parts, figures, aliases and known-for hooks do the work, and the claim must not name the item. "
                   f"Every seed's mechanism must be one of: {', '.join(allowed)}; a seed using any other mechanism is thrown away.")
    user = (f"SECTION: {slot}\nARGUMENT: {b['argument']}\nINGREDIENTS (true facts to TRANSFORM into claims; never retell them in the "
            f"order they happened):\n{chr(10).join(b['facts'])}\n"
            f"CALLBACKS IN: {b['callbacks_in']}\nCALLBACKS OUT: {b['callbacks_out']}\nCLOSER: {b['closer']}\n\n"
            f"Design {n} seeds for THIS section. Every seed's persona_claim must advance the argument above and must be sayable by the narrator.")
    return Request(model=model, system=system, messages=[{"role": "user", "content": user}], schema=seed_stage.SEED_SCHEMA,
                   max_tokens=6000, effort=effort, temperature=temperature, stage="argue_seeds", scope="write")


def validate_seed(slot: str, seed: dict, allow_other_payoff: bool = False) -> list[str]:
    """seed_stage's own rules, plus the plan's: the payoff word must be one the section planned, inside the family the carpet can hold."""
    why = []
    if seed.get("mechanism") not in seed_stage.NO_SECOND_READING and not (seed.get("reading_2") or "").strip():
        why.append("no second reading")
    if len(re.findall(r"[A-Za-z']+", seed.get("payoff_word") or "")) != 1:
        why.append("payoff must be a single word")
    low = (seed.get("persona_claim") or "").lower()
    if any(c in low for c in seed_stage.CLICHES):
        why.append("cliche")
    why += seed_stage.lore_reasons(seed)
    mech = seed.get("mechanism")
    planned = mechanisms(slot) + (["lore_allusion"] if mech == "lore_allusion" else [])
    if mech and mech not in planned:
        why.append(f"mechanism {mech} is not one of the plan's for {slot} ({', '.join(planned)})")
    pay = (seed.get("payoff_word") or "").lower()
    lock = family_lock(slot)
    if not allow_other_payoff and lock and pay not in lock and not named_in_beats(slot, pay):
        why.append(f"payoff '{pay}' is outside the section's carpet family ({'/'.join(lock)}); "
                   f"the block's four end words must all rhyme, so a word from another family cannot hold the carpet")
    return why


def run_seeds(llm, slot: str, n: int = 6, model: str = "ds-flash", effort: str = "high",
              temperature: Optional[float] = None, allow_other_payoff: bool = False, kit: str = "") -> dict:
    """seeds targeted at the section's argument. Rejections are logged (R10) so the same failure is not re-generated."""
    res = llm.complete(seed_request(slot, n, model, effort, temperature, negatives=guidance(slot), kit=kit), use_cache=temperature is None)
    seeds = (res.parsed or {}).get("seeds") or []
    kept, dropped = [], []
    for s in seeds:
        why = validate_seed(slot, s, allow_other_payoff)
        if why:
            dropped.append({**s, "_why": why})
            failures.log("gate", s.get("persona_claim", ""), detail="; ".join(why), source=f"argue:{slot}")
        else:
            kept.append(s)
    return {"slot": slot, "argument": brief(slot)["argument"], "kept": kept, "dropped": dropped,
            "usd": res.usd, "schema_errors": res.schema_errors}


# ------------------------------------------------------------------ the plan gate

def plan_cash(slot: str, bars: list[str]) -> list[dict]:
    """The plan DECLARES its own cashes: for each planned payoff word that closes a bar, the idiom the plan assigned to that
    section is declared as `{bar, idiom, payoff}` in slotcheck.verify_cash's shape. The writer is not asked to self-report
    (round 1 self-reported cashes that did not exist); the plan's ledger is the authority and the verifier still checks the
    payoff is the bar's last word and the idiom's words are in that bar or the one before."""
    out = []
    idioms = list(ledger().get(slot, [])) + [c.get("idiom_or_pair", "") for c in _section(slot).get("concepts") or []]
    for i, bar in enumerate(bars, 1):
        last = (_words(bar) or [""])[-1].lower()
        for w in payoffs(slot):
            if last == w:
                idiom = next((x for x in idioms if x and x.split()[-1].lower() == w), w)
                out.append({"bar": i, "idiom": idiom, "payoff": w})
                break
    return out


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text)


def check_block(slot: str, bars: list[str], allow_other_payoff: bool = False) -> dict:
    """does the block do the job the plan gave this section? HARD findings block; the rest are reported with counts."""
    from .. import bridge
    b = brief(slot)
    planned = payoffs(slot)
    hard, soft, per = [], [], []
    n = len(bars)
    ends = [(w[-1].lower() if (w := _words(x)) else "") for x in bars]
    cashed = [p for p in planned if p in ends]
    if not cashed and not allow_other_payoff:
        hard.append(f"plan payoff: none of this section's planned payoff words ({', '.join(planned)}) closes any bar "
                    f"(the plan designed the joke to land on one of them, in the rhyme slot)")
    if len(set(ends)) != len(ends):
        dup = sorted({e for e in ends if ends.count(e) > 1})
        hard.append(f"end word repeated inside the block: {', '.join(dup)}")
    idioms = sum(1 for x in bars if _cashes(x))
    need = max(1, n // 4)
    # Joe's character rule (13 Oct 2026): at most two references to any one person in the whole song, and family capped at
    # two because partners and mates are preferred. Checked per block here, which is the strictest form of it: a section
    # that names one character three times cannot be part of a song that stays inside the cap.
    try:
        bridge._toolkit_on_path()
        import characters as chars
        for msg in chars.over_cap(bars):
            hard.append(f"characters: {msg}")
    except Exception:  # noqa: BLE001 - a missing tool must not block the gate
        pass

    # the plan gate counts cashes the way the slot frame does: the plan DECLARES the idiom for each planned payoff word that
    # closes a bar, and verify_cash checks the payoff really is the bar's last word with the idiom's words nearby. The old
    # heuristic (banked phrase or article+noun) missed a plan-true bar whose words are terse ("Four-foot bronze gnome on
    # tailgate, lorry") and failed a candidate that was in fact cashing its planned payoff.
    from . import slotcheck
    verified, _issues = slotcheck.verify_cash(bars, plan_cash(slot, bars))
    if not verified and idioms < need:
        hard.append(f"cashes {idioms} and declares {len(verified)} of the plan's own; the plan's rate for a {n}-bar section is {need}")
    # reported, never blocking
    if planned:
        soft.append(f"planned payoffs cashed: {len(cashed)} of {len(planned)} ({', '.join(planned)})")
    for i, x in enumerate(bars):
        shape = bridge.end_shape(x)
        first = _words(x)[0].lower() if _words(x) else ""
        per.append({"bar": i + 1, "ends": ends[i], "shape": shape, "first_person": _first_person(x), "words": len(_words(x))})
        want = next((r["shape"] for r in b["beats"] if str(i + 1) in re.findall(r"\d+", r["bars"] or "")), None)
        if want and shape != want:
            per[-1]["shape_vs_plan"] = f"{shape} vs plan {want}"
    fp = sum(1 for p in per if p["first_person"])
    if fp < (n + 1) // 2:
        soft.append(f"first person in {fp} of {n} bars (the plan's voice rule wants at least half)")
    shapes_off = [p["bar"] for p in per if p.get("shape_vs_plan")]
    if shapes_off:
        soft.append(f"end shape differs from the plan on bars {shapes_off}")
    if b["closer"] and not any(re.search(r"\b[Mm]ight\b", x) for x in bars):
        soft.append("closer: the plan's closer bar is a modal understatement ('might ...'); none found")
    return {"ok": not hard, "hard": hard, "soft": soft, "per_bar": per, "planned_payoffs": planned, "cashed": cashed}


_HEDGE = re.compile(r"\b(might|may|could|would|should)\b")


def _cashes(bar: str) -> bool:
    """a bar 'cashes' only if the repo's own cash measure finds a banked stock phrase in it (coherence_gate.craft_idioms, the same
    fuzzy matcher over toolkit/phrases.txt the coherence gate uses). Until 14 Oct 2026 any '(the|a|my) + noun' also counted, so every
    bar that reported an object ("a flat", "the bike") was a 'cash' -- a recount scored as wordplay. A double reading the plan declares
    is verified separately (slotcheck.verify_cash), not guessed here."""
    try:
        import coherence_gate
        return bool(coherence_gate.craft_idioms(bar))
    except Exception:  # noqa: BLE001 - the phrase ledger is a refinement, never a crash
        return False


def _first_person(bar: str) -> bool:
    return bool(re.search(r"\b(I|I'm|I've|I'd|I'll|my|me|we|our|us)\b", bar))


def guidance(slot: str, limit: int = 12) -> str:
    """the closed loop: rejections logged for this slot (R10/R11) become negatives for the next generation. Nothing read this before."""
    rows = [r for r in failures.read("gate") if slot in (r.get("source") or "")] + [r for r in failures.read("joe") if slot in (r.get("source") or "")]
    if not rows:
        return ""
    out = []
    for r in rows[-limit:]:
        txt = r.get("text", "")[:90]
        out.append(f"- {txt}  ->  {r.get('detail','')[:90]}")
    b = brief(slot)
    if b["critic_note"]:
        out.append(f"- (the plan's own critic) {b['critic_note'][:200]}")
    am = amendment(slot)
    if am:
        out.append(f"- (recorded plan amendment) end words must stay in one family: {'/'.join(am['kept_family'])}; "
                   f"deferred words: {', '.join(am['deferred'])}")
    try:
        from .. import bridge
        bridge._toolkit_on_path()
        import characters as chars
        out.append("- " + chars.guidance())
    except Exception:  # noqa: BLE001 - guidance is advisory; a missing tool must not stop a run
        pass
    return "\n".join(out)


# ------------------------------------------------------------------ driver

def run(llm, slot: str, seeds: int = 6, blocks_per_seed: int = 2, model: str = "ds-flash", rank: bool = True,
        allow_other_payoff: bool = False, write_effort=None, examples=None, syllables=None, kit: bool = False) -> dict:
    """argument -> seeds -> blocks -> plan gate + deterministic verifier -> (optional) comparative ranking. Rejections are logged.

    write_effort defaults to None (no thinking) for the block stage on purpose: the seed stage has already done the thinking, and
    the writer is a schema-constrained realisation. With effort set, the client adds 6000-40000 thinking tokens to the cap
    (ww/llm/client.py), and a 5000-token block request then becomes 11000 tokens of which the model spends all of it thinking and
    returns EMPTY content ("finish_reason=length") -- every seed lost, silently, until the failure log recorded it (14 Oct 2026).
    """
    from . import block_writer, slotcheck, verify_det
    b = brief(slot)
    y = {"slot": slot, "argument": b["argument"]}
    kit_text = ""
    if kit:
        from ..lex import graph
        lazy = graph.ensure_cards(slot, llm)          # depth is bought only for the entities this section can use
        y["cards_built"] = {"built": lazy["built"], "usd": lazy["usd"]}
        kit_text = graph.kit_text(slot)
    sd = run_seeds(llm, slot, n=seeds, model=model, allow_other_payoff=allow_other_payoff, kit=kit_text)
    y["seeds"] = {"kept": len(sd["kept"]), "dropped": len(sd["dropped"]), "usd": sd["usd"]}
    fact = _plan_fact(slot)
    cands = []
    for s in sd["kept"]:
        n = blocks_per_seed
        while n >= 1:
            try:
                cands += block_writer.run(llm, s, fact, n=n, model=model, effort=write_effort,
                                          sylls=syllables or plan_sylls(slot), jobs=plan_jobs(slot),
                                          negatives=guidance(slot), examples=examples)
                break
            except Exception as e:  # noqa: BLE001 - one failed seed must not sink the run
                # A long answer can overrun the token cap and come back empty in JSON mode ("finish_reason=length");
                # halve the batch and try once more before giving up, and never swallow the reason silently --
                # the first version of this driver lost whole seeds to that and reported "0 candidates".
                y.setdefault("errors", []).append(f"{s.get('payoff_word')}: n={n} {type(e).__name__}: {str(e)[:110]}")
                failures.log("gate", str(s.get("persona_claim"))[:120], detail=f"block write failed: {type(e).__name__}",
                             source=f"argue:{slot}")
                n = n // 2
    y["blocks"] = {"generated": len(cands)}
    # record the plan/slot conflicts this run had to resolve, so they are reviewable data and not a hidden prompt edit
    try:
        if amendments():
            (config.EVAL_DIR / "plan_amendments.json").write_text(
                json.dumps(amendments(), indent=1, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    # the FRAME is the repo's own slot checker: it knows the by-ear scheme for the slot (Hook 5-8 is ABBA -- bars 1&4 rhyme and
    # bars 2&3 rhyme -- which the plan's A/B payoff design follows exactly). verify_det's carpet spec demands all six pairs and
    # therefore rejects a plan-true A/B block; it is kept as a secondary reading only.
    pool = []
    for c in cands:
        bars = [x["text"] for x in c["bars"]]
        c["frame"] = slotcheck.check(slot, bars, cash=plan_cash(slot, bars))
        c["det"] = verify_det.check_block(bars, dict(verify_det.HOOK_5_8_SOFT, sylls=plan_sylls(slot)))
        c["plan"] = check_block(slot, bars, allow_other_payoff=allow_other_payoff)
        c["passed"] = bool(c["frame"]["ok"] and c["plan"]["ok"])
        if not c["passed"]:
            failures.log("gate", " | ".join(bars),
                         detail="; ".join(c["frame"]["hard"] + c["plan"]["hard"])[:300], source=f"argue:{slot}")
        pool.append(c)
    keep = [c for c in pool if c["passed"]]
    y["blocks"]["passed_both_gates"] = len(keep)
    # A run that yields nothing is useless, so the shortlist falls back to the best-effort pool with every fired flag
    # printed next to the line (the same rule the repo settled on for check_all: a ranking target, not a veto).
    ranked_pool = keep or pool
    y["blocks"]["ranked"] = len(ranked_pool)
    if rank and len(ranked_pool) > 1:
        from ..judge import rank as ranker
        items = {str(i): [x["text"] for x in c["bars"]] for i, c in enumerate(ranked_pool)}
        out = ranker.rank_items(llm, items, batch_size=4, rounds=3, seed=3, model=model, stage="argue_rank", workers=4)
        for i, c in enumerate(ranked_pool):
            c["rank"] = {"bt": round(out["bt"].get(str(i), -9.0), 3), "mean_rank": round(out["mean_rank"].get(str(i), 1.0), 3)}
        ranked_pool.sort(key=lambda c: -c["rank"]["bt"])
    y["final"] = len(ranked_pool)
    return {"yield": y, "blocks": ranked_pool, "seeds_all": sd, "strict_pass": len(keep)}


def _plan_fact(slot: str):
    """the section's argument dressed as a Fact so the existing writer path works unchanged (the writer never reads the fact's place)."""
    b = brief(slot)
    return seed_stage.Fact(id=f"plan:{slot}", place=slot, trip=PLAN_PATH.stem, detail=b["argument"],
                           kind="argument", source=PLAN_PATH.stem, tags=b["mechanisms"])


def report(res: dict, path=None) -> str:
    """markdown for writing/argue_<slot>.md: the argument first, then each survivor with its per-bar readings and flags."""
    y = res["yield"]
    L = [f"# argue {y['slot']} (argument-targeted run)", "", f"**Argument (the plan's, the input to this run):** {y['argument']}", "",
         f"seeds kept {y['seeds']['kept']} / dropped {y['seeds']['dropped']} | blocks generated {y['blocks']['generated']} | "
         f"passed the plan gate + the frame {y['blocks']['passed_both_gates']} | ranked {y['blocks'].get('ranked', y['final'])}", ""]
    if not y["blocks"]["passed_both_gates"]:
        L += ["> No candidate passed both gates on this run, so the list below is RANKED BEST-EFFORT with every fired flag",
              "> printed next to its line. The flags are the work list: they are what the next pass has to fix.", ""]
    if y.get("errors"):
        L += ["## stage errors (never swallowed)", ""] + [f"- {e}" for e in y["errors"]] + [""]
    seeds_all = (res.get("seeds_all") or {}).get("kept") or []
    if seeds_all:
        L += ["## the seeds this argument produced (each is a planned payoff word)", ""]
        for s in seeds_all:
            L.append(f"- **{s.get('payoff_word')}** ({s.get('mechanism')}): {s.get('persona_claim')}")
            if s.get("reading_2"):
                L.append(f"     second reading: {s['reading_2']}")
        L.append("")
    for i, c in enumerate(res["blocks"], 1):
        L.append(f"## candidate {i}" + (f"  (BT {c['rank']['bt']:+.2f})" if c.get("rank") else "") +
                 ("  [passed the plan gate + the slot frame]" if c.get("passed") else "  [flags fired]"))
        for k, bar in enumerate(c["bars"], 1):
            row = next((r for r in c["frame"]["rows"] if r["bar"] == k), None)
            issues = (row or {}).get("issues") or []
            L.append(f"{k}. {bar['text']}" + ("  <-- " + "; ".join(issues) if issues else ""))
            L.append(f"     claim: {bar.get('claim','')}")
        L.append("")
        for s in c["plan"]["soft"]:
            L.append(f"- {s}")
        if c["plan"]["cashed"]:
            L.append(f"- cashed the planned payoff in the rhyme slot: {', '.join(c['plan']['cashed'])}")
        if c["frame"].get("pairs"):
            L.append("- scheme pairs: " + ", ".join(f"{a}&{b}={s}" for a, b, s in c["frame"]["pairs"]))
        if c["frame"]["hard"]:
            L.append("- frame: " + "; ".join(c["frame"]["hard"])[:400])
        L.append("")
    text = "\n".join(L)
    if path:
        config.WRITING.mkdir(parents=True, exist_ok=True)
        open(path, "w", encoding="utf-8").write(text)
    return text


def selftest() -> tuple[bool, str]:
    problems = []
    # the plan is read, not invented
    b = brief("Hook 5-8")
    if "gnome" not in b["argument"].lower():
        problems.append(f"brief() lost the plan's argument: {b['argument'][:60]}")
    if "lorry" not in b["payoffs"] or "pardon" not in b["payoffs"]:
        problems.append(f"planned payoffs missing: {b['payoffs']}")
    if b["mechanisms"] != ["cashed_idiom", "one_word_two_senses"]:
        problems.append(f"mechanisms not mapped from the plan's labels: {b['mechanisms']}")
    if not ledger().get("Hook 5-8"):
        problems.append("the ledger did not parse")
    if plan_sylls("Hook 5-8") != [8, 10, 8, 8]:
        problems.append(f"plan_sylls: {plan_sylls('Hook 5-8')}")
    # the gate must pass a plan-faithful block and fail a block that ignores the argument
    good = ["Hoi Rotterdam, I own the quarry", "Council want the gnome back, I am not sorry",
            "Gnome off the back of a lorry", "Might lie low over in Gorey"]
    if not check_block("Hook 5-8", good)["ok"]:
        problems.append(f"a plan-faithful block failed the plan gate: {check_block('Hook 5-8', good)['hard']}")
    cur = ["Cop in whites, he's wrecked my picket", "Gnome's in good nick so he says I nicked it",
           "Mum says it's rude, it's not cricket", "Might nip off, Oslo's the ticket"]
    if check_block("Hook 5-8", cur)["ok"]:
        problems.append("the draft's Hook 5-8 (no lorry, no pardon, no council) passed the plan gate")
    # a rejection must reach the guidance block, and the log must not write to the repo during a test
    import tempfile
    from pathlib import Path
    real = config.FAILURES
    try:
        config.FAILURES = Path(tempfile.mkdtemp()) / "f.jsonl"
        failures.log("gate", "test bar", detail="test reason", source="argue:Hook 5-8")
        if "test reason" not in guidance("Hook 5-8"):
            problems.append("guidance() did not read back a logged rejection")
    finally:
        config.FAILURES = real
    return (not problems, "; ".join(problems) if problems else
            "the plan is the input: argument/payoffs/mechanisms/syllables read, the gate passes a plan-true block and fails an argument-blind one, "
            "and a logged rejection reaches the next prompt")
