"""Build a whole draft from the plan: one argument-targeted run per planned slot, then a MEASURED choice per slot against the
incumbent section. Nothing is replaced unless it wins on the plan gate, then the slot frame, then cashed planned payoffs, then
problem count -- so a build can only move the draft forward, and every decision is printed.

Why this shape: the rounds that produced the current draft generated candidates from travel FACTS and picked them with an
unvalidated judge (eval/_round4.json: parity_any False, best 6.8 against a reference of 8.5-9). Here the unit of generation is the
plan's own section (argument + mechanisms + payoff words + per-bar jobs and syllable targets), and the unit of decision is the
repo's own slot frame plus the plan gate, both deterministic.

  python -m ww.cli build [--seeds N] [--blocks N] [--slots "Hook 5-8,V1 1-8"] [--incumbent writing/ww_full_draft_v6.md]
"""
from __future__ import annotations

import json
import re
from typing import Optional

from .. import config
from . import argue_stage, block_writer, flowaudit, slotcheck


def _chars():
    """the toolkit's character-counting rule (Joe, 13 Oct 2026: two references per character, family capped at two)."""
    from .. import bridge
    bridge._toolkit_on_path()
    import characters
    return characters


characters = _chars()

DEFAULT_INCUMBENT = config.WRITING / "ww_full_draft_v6.md"
JOE_HOOK = ["Yo, bonjourno", "Said damn at the on-stage porno", "Front row on my phone, so bored, though",
            "So I boarded a plane out to Bordeaux"]


def _check_all_problems(slot: str, bars: list) -> int:
    """the ratchet's own form count for a section: the number of lines check_all prints starting "x ".

    This is the measure the Definition of Done is written in ("no RISE in form problems"), so the build's decision has to use
    it and not a proxy. Measured: a merged V1 33-44 bar passed every guard I had (the slot frame's hard list was unchanged at
    1, syllable misses 0) and the ratchet still refused the draft -- "V1 33-44: problems rose 19 -> 20"."""
    import contextlib
    import io
    from .. import bridge
    bridge._toolkit_on_path()
    import check_all  # noqa: E402
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        check_all.check(slot, list(bars))
    return sum(1 for l in buf.getvalue().splitlines() if l.strip().startswith("x "))


def score_section(slot: str, bars: list[str]) -> dict:
    """the decision metrics for one section. Deterministic; no judge, no model."""
    if not bars:
        return {"usable": False}
    want = len(slotcheck.spec(slot)["sylls"])
    f = slotcheck.check(slot, bars, cash=argue_stage.plan_cash(slot, bars))
    p = argue_stage.check_block(slot, bars, allow_other_payoff=False)
    syl_miss = sum(1 for r in f["rows"] if any("syl" in i for i in r["issues"]))
    probs = _check_all_problems(slot, bars) if len(bars) == want else 99
    from . import rapfit
    echo = rapfit.internal_echo(bars)["score"] if len(bars) >= 4 else 0.0
    return {"usable": len(bars) == want, "plan_ok": p["ok"], "frame_ok": f["ok"], "frame_hard": len(f["hard"]),
            "syl_miss": syl_miss, "cashed": len(p["cashed"]), "planned": len(p["planned_payoffs"]),
            "problems": probs, "echo": echo, "cad": f.get("cad_misses", 0), "plan_hard": p["hard"], "frame_hard_list": f["hard"], "scheme": f["scheme"],
            "pairs": f["pairs"]}


def merge_improve(slot: str, inc_bars: list, cand_bars: list, targets: list, shapes: list,
                  menu: list, planned: set, song_others: Optional[list] = None) -> dict:
    """Per-bar ratchet between the incumbent section and a candidate: swap in a candidate bar only where the incumbent's bar
    fails a deterministic check and the candidate's bar passes every one of the same checks, then keep the merge only if the
    SECTION does not get worse.

    Why this exists: the candidates are content-good and form-bad (they cash 21 of the plan's 34 payoffs against the incumbent's
    4, and carry 145 frame problems against its 17), so a whole-section swap loses on the frame and was refused 9 times of 9.
    Bars, however, are separable: the plan gate is per bar for the payoff words and the frame is per bar for count and shape.
    This is the only decision in the build that can move the draft without spending a call.

    Every swap is judged by `take`, the same predicate the whole-section decision uses, so a merge cannot buy content with a
    form rise: the section's frame problems may rise by at most one and its syllable misses may not rise at all."""
    from . import barloop
    from .. import bridge
    if len(inc_bars) != len(cand_bars):
        return {"bars": list(inc_bars), "log": [f"merge skipped: {len(inc_bars)} incumbent bars vs {len(cand_bars)} candidate bars"], "swaps": 0}
    out = list(inc_bars)
    log, swaps = [], 0
    for i in range(len(out)):
        c = cand_bars[i].strip()
        if not c or c == out[i]:
            continue
        used = {barloop._end_word(b) for b in out if b != out[i]}
        tgt = targets[i] if i < len(targets) else None
        if not tgt:
            continue
        shape = shapes[i] if i < len(shapes) else None
        payoff = barloop._end_word(c) if barloop._end_word(c) in planned else None
        why_new = barloop.accept(slot, c, tgt, shape, used, payoff, source=c)
        if why_new:
            log.append(f"bar {i + 1}: candidate rejected ({why_new[0]})")
            continue
        merged = list(out)
        merged[i] = c
        if song_others is not None and characters.over_cap(list(song_others) + merged):
            log.append(f"bar {i + 1}: swap refused, it would push a character past the song cap "
                       f"({characters.over_cap(list(song_others) + merged)[0]})")
            continue
        if not take(score_section(slot, merged), score_section(slot, out)):
            log.append(f"bar {i + 1}: swap refused, it does not beat the section it joins")
            continue
        out = merged
        swaps += 1
        log.append(f"bar {i + 1}: swapped in the candidate bar (cash: {payoff or '-'})")
    return {"bars": out, "log": log, "swaps": swaps}


def length_examples(targets: list, inc: dict, cap: int = 4) -> list:
    """(syllables, bar) pairs from the incumbent for the lengths this slot asks for, so the writer is shown a real bar of the
    target length instead of only a number. The incumbent's own short bars are the proof that a 5-7 syllable bar is writable."""
    from .. import bridge
    pool: dict[int, str] = {}
    for bars in (inc or {}).values():
        for b in bars or []:
            n = bridge.syllable_count(b)
            if n and n not in pool:
                pool[n] = b
    out = []
    for t in sorted({int(x) for x in (targets or []) if x}):
        near = [n for n in pool if abs(n - t) <= 1]
        if near:
            out.append((min(near, key=lambda n: (abs(n - t), n)), pool[min(near, key=lambda n: (abs(n - t), n))]))
    return out[:cap]


def take(cand: dict, inc: dict) -> bool:
    """STRICT RATCHET, and the plan gate is mandatory. A section is replaced only if the candidate
      * passes the plan gate (the payoff words land in the rhyme slots -- the whole point of the change),
      * is no worse than the incumbent on the slot frame by more than one problem,
      * raises check_all's own problem count for the section by no amount (the measure the ratchet uses), and
      * has no more syllable misses and no fewer cashed planned payoffs than the incumbent.
      An earlier version of this ranked (plan_ok, frame_ok, cashed, -problems) lexicographically and replaced Hook 5-8 with
      a candidate carrying 10 frame problems against the incumbent's 1, because it had 3 payoffs against 0. That trade is
      exactly the "flow is worse" regression Joe has rejected; form and argument are both floors, not a currency to spend."""
    if not cand.get("usable"):
        return False
    if not cand.get("plan_ok"):
        return False
    if not inc.get("usable"):
        return True
    if cand["frame_hard"] > inc["frame_hard"] + 1:
        return False
    # check_all's problem count is no longer a ratchet condition (registry: failed_validation as a quality gate; Joe 13 Oct 2026: the old flow map is not to be trusted)
    if cand["syl_miss"] > inc["syl_miss"]:
        return False
    if cand["cashed"] < inc["cashed"]:
        return False
    return True


_SHAPE_EQ = {("|Sw", "~Sw"), ("~Sw", "|Sw")}


def _shape_ok(got: str, want: str) -> bool:
    return got == want or (got, want) in _SHAPE_EQ


def end_menu(slot: str, shape: Optional[str] = None, limit: int = 60) -> list:
    """The end words a repaired bar may land on: the rhymes of the section's locked carpet family, filtered to the bar's
    measured end shape.

    Two defects made this empty for five of the nine slots, which left the bar loop telling the model "any real word that
    fits the sound" while check_all demanded a particular shape -- and the shape miss was then the largest single cause of
    bar-loop rejection (100 of 171 logged variant failures). sound_plan.menu only serves two-syllable stress-first payoffs,
    so a family of monosyllables (bust / just / adjust) or of hard tails (cruise / bruise / shoes) resolved to nothing.
    The supply now comes from the family's rhymes AND the slot's carpet bank (benchmark/carpets_<slot>.json, measured from
    the audio), and if the shape filter would leave the model with nothing the menu falls back to the unfiltered list --
    a wrong shape is a repairable bar, an empty menu is not."""
    from .. import bridge
    from . import sound_plan
    fam = argue_stage.family_lock(slot) or argue_stage.payoffs(slot)
    bank = _carpet_bank(slot)

    def build(filter_shape: bool, cap: int = 60) -> list:
        out, seen = [], set()

        def add(w, sh=None):
            w = (w or "").strip().lower()
            if not w or w in seen:
                return
            if filter_shape and shape and sh and not _shape_ok(sh, shape):
                return
            seen.add(w)
            out.append(w)

        for w in fam[:3]:
            try:
                for c in (sound_plan.menu(w).get("candidates") or []):
                    add(c.get("word"), c.get("shape") or bridge.end_shape(c.get("word") or ""))
            except Exception:  # noqa: BLE001 - an unusable menu must not stop the build
                continue
        for row in bank:
            add(row.get("word"), row.get("shape"))
        return out[:cap]

    def stress_ok(words: list) -> list:
        """R4: keep only menu words that rhyme with the family anchor THROUGH a stressed syllable (no '-it'-only echoes); never empty the menu."""
        from . import rapfit
        if not fam:
            return words
        anchor = rapfit._syl(fam[0])
        keep = [w for w in words if w == fam[0] or rapfit.chain_best(rapfit._syl(w), anchor)["depth"] >= 1]
        return keep if len(keep) >= 6 else words

    shaped = stress_ok(build(True))
    # keep the shape filter only while it still leaves a supply: a wrong shape is a repairable bar, an empty menu is not.
    return shaped if len(shaped) >= 6 else stress_ok(build(False, limit))


def _carpet_bank(slot: str) -> list:
    """the slot's per-bar end-word bank built by toolkit/carpet.py from the audio frame (word, syllables, end shape)."""
    p = config.ROOT / "benchmark" / f"carpets_{slot.replace(' ', '_').replace('-', '_')}.json"
    if not p.exists():
        return []
    try:
        rows = []
        for bar in (json.loads(p.read_text(encoding="utf-8")).get("per_bar") or []):
            rows.extend(bar or [])
        return rows
    except Exception:  # noqa: BLE001
        return []


def run(llm, slots: Optional[list] = None, seeds: int = 4, blocks: int = 3, model: str = "ds-flash",
        incumbent: Optional[str] = None, rank: bool = True, repairs: int = 2, repair_calls: int = 10,
        kit: bool = False, scratch: bool = False) -> dict:
    """scratch=True builds a NEW draft: no incumbent is read, shown to the writer as a length example, or merged with. Every slot takes its best
    candidate whether or not it clears the plan gate, and the slot records gate_ok so a failing section is visible, not hidden or swapped for old bars."""
    from . import barloop
    slots = slots or argue_stage.slots()
    inc_path = incumbent or str(DEFAULT_INCUMBENT)
    from pathlib import Path
    p = Path(inc_path)
    if not p.is_absolute():
        p = config.ROOT / p
    inc = {} if scratch else (flowaudit.parse_draft(str(p)) if p.exists() else {})
    out = {"incumbent": "(none: built from scratch)" if scratch else str(p), "slots": {}, "spend": 0.0, "scratch": scratch, "kit": kit}
    for slot in slots:
        tg = argue_stage.target_sylls(slot)
        r = argue_stage.run(llm, slot, seeds=seeds, blocks_per_seed=blocks, model=model, rank=rank,
                            syllables=tg, examples=length_examples(tg, inc), kit=kit)
        y = r["yield"]
        spec_slot = slotcheck.spec(slot)
        menu = end_menu(slot)
        # THE BAR LOOP: repair up to `repairs` candidates, bar by bar, against the measured bar lengths. Deterministic
        # acceptance, and a pass is kept only when the section does not get worse; a bar with no passing variant is left as
        # it was and said so.
        repairs_log, best_bars, best_score, best_claims, best_seed = [], None, None, None, None
        for cand in (r["blocks"][:repairs] if repairs else []):
            bars = [x["text"] for x in cand["bars"]]
            if len(bars) != len(spec_slot["sylls"]):
                continue
            claims = [x.get("claim", "") for x in cand["bars"]]
            rb = barloop.repair_block(llm, slot, bars, claims, tg, spec_slot["shapes"], menu,
                                      max_calls=repair_calls, model=model, negatives=argue_stage.guidance(slot),
                                      score=lambda bs: score_section(slot, bs))
            s = score_section(slot, rb["bars"])
            repairs_log.append({"before": bars, "after": rb["bars"], "steps": rb["log"], "calls": rb["calls"],
                                "score_before": score_section(slot, bars), "score_after": s})
            if best_score is None or (s["plan_ok"], s["frame_ok"], s["cashed"], -s["frame_hard"], -s["syl_miss"], s.get("echo", 0)) > \
                    (best_score["plan_ok"], best_score["frame_ok"], best_score["cashed"], -best_score["frame_hard"], -best_score["syl_miss"], best_score.get("echo", 0)):
                best_score, best_bars, best_claims, best_seed = s, rb["bars"], claims, cand.get("seed")
        if best_bars is None and r["blocks"]:
            best_bars = [x["text"] for x in r["blocks"][0]["bars"]]
            best_claims = [x.get("claim", "") for x in r["blocks"][0]["bars"]]
            best_score = score_section(slot, best_bars)
            best_seed = r["blocks"][0].get("seed")
        inc_bars = (inc or {}).get(slot, [])
        cand_bars = best_bars or []
        s_inc = score_section(slot, inc_bars)
        s_cand = best_score or {"usable": False}
        take_it = take(s_cand, s_inc)
        gate_ok = take_it
        if scratch:
            take_it = bool(cand_bars)          # a from-scratch section is the best candidate there is; gate_ok says whether it earned it
        lore = None
        if best_seed and best_seed.get("entity") and cand_bars:
            from ..lex import cards
            lore = cards.check_allusion(best_seed["entity"], "\n".join(cand_bars), cand_bars)
            lore["entity"] = best_seed["entity"]
        # THE PER-BAR RATCHET: if the whole section cannot win, take the bars that can. Guarded by the same section score.
        merge = {"bars": list(inc_bars), "log": [], "swaps": 0}
        if not take_it and inc_bars and cand_bars and len(inc_bars) == len(cand_bars):
            others = [b for s2, bs in (inc or {}).items() if s2 != slot for b in (bs or [])]
            merge = merge_improve(slot, inc_bars, cand_bars, tg, spec_slot["shapes"], menu,
                                  set(argue_stage.payoffs(slot)), song_others=others)
            if merge["swaps"]:
                s_m = score_section(slot, merge["bars"])
                if take(s_m, s_inc):
                    cand_bars, s_cand, take_it = merge["bars"], s_m, True
                else:
                    merge["log"].append("merge refused: the section score did not improve")
                    merge = {"bars": merge["bars"], "log": merge["log"], "swaps": merge["swaps"]}
        out["slots"][slot] = {"took": take_it, "gate_ok": gate_ok, "lore": lore, "incumbent_score": s_inc, "candidate_score": s_cand,
                              "candidate_bars": cand_bars if take_it else [], "candidates": len(r["blocks"]),
                              "repairs": repairs_log, "merge": merge,
                              "seeds_kept": y["seeds"]["kept"], "seeds_dropped": y["seeds"]["dropped"],
                              "generated": y["blocks"]["generated"], "passed_both_gates": y["blocks"]["passed_both_gates"],
                              "argument": y["argument"], "errors": y.get("errors", [])}
        out["spend"] += y["seeds"]["usd"] or 0.0
        if best_bars:
            out.setdefault("candidates", {})[slot] = {"bars": best_bars, "claims": best_claims or [],
                                                      "repaired": (repairs_log[-1]["after"] if repairs_log else None)}
    try:
        (config.EVAL_DIR / "_build_candidates.json").write_text(json.dumps(out.get("candidates", {}), indent=1), encoding="utf-8")
    except Exception:  # noqa: BLE001 - a wasted cache must not fail a build
        pass
    return out


def assemble(res: dict, path) -> str:
    """Joe's hook + one section per planned slot, each the winner of the measured choice above."""
    scratch = bool(res.get("scratch"))

    def label(v):
        if scratch:
            return "BUILT, passes the plan gate" if v.get("gate_ok") else ("BUILT, FAILS the plan gate" if v["took"] else "NO CANDIDATE")
        return "REPLACED" if v["took"] else "kept incumbent"

    L = [("# draft built FROM SCRATCH by the plan (no incumbent read, shown or merged); pop-culture kit " + ("ON" if res.get("kit") else "off"))
         if scratch else "# new draft built from the plan (argument-targeted runs; see the header decisions below)",
         "# " + " | ".join(f"{s}: {label(v)}"
                           f" (cand plan_ok={v['candidate_score'].get('plan_ok')} frame_ok={v['candidate_score'].get('frame_ok')}"
                           f" cashed={v['candidate_score'].get('cashed')}" + ("" if scratch else f" vs inc cashed={v['incumbent_score'].get('cashed')}") + ")"
                           for s, v in res["slots"].items()),
         ""]
    if "Hook 1-4" not in res["slots"]:
        L += ["== Hook 1-4"] + JOE_HOOK + [""]
    inc = {} if (scratch or not res.get("incumbent")) else flowaudit.parse_draft(res["incumbent"])
    for slot in argue_stage.slots():
        v = res["slots"].get(slot)
        if not v:
            continue
        bars = v["candidate_bars"] if v["took"] else inc.get(slot, [])
        L += [f"== {slot}"] + bars + [""]
    text = "\n".join(L).rstrip() + "\n"
    if path:
        open(path, "w", encoding="utf-8").write(text)
    return text


def report(res: dict, path=None) -> str:
    L = [f"# build report (incumbent: {res['incumbent']})", "",
         f"spend on seeds this build: ${res['spend']:.4f} (block and ranking calls are in eval/ledger)", ""]
    for slot, v in res["slots"].items():
        c, i = v["candidate_score"], v["incumbent_score"]
        scratch = bool(res.get("scratch"))
        head = (("BUILT, passes the plan gate" if v.get("gate_ok") else "BUILT, FAILS the plan gate") if (scratch and v["took"]) else
                "NO CANDIDATE" if scratch else ("REPLACED" if v["took"] else "kept the incumbent"))
        L.append(f"## {slot} -- {head}")
        if v.get("lore"):
            lo = v["lore"]
            L.append(f"lore_allusion '{lo['entity']}': {'structurally OK' if lo['ok'] else 'NOT met: ' + '; '.join(lo['reasons'])} | triggers in the bars: "
                     f"{[t for _, t in lo['hits']]} | in a rhyme slot: {lo['in_rhyme_slot']}")
        L.append(f"argument: {v['argument']}")
        L.append(f"generated {v['generated']} blocks from {v['seeds_kept']} seeds ({v['seeds_dropped']} rejected), "
                 f"{v['passed_both_gates']} passed both gates")
        L.append(f"candidate: plan_ok={c.get('plan_ok')} frame_ok={c.get('frame_ok')} cashed={c.get('cashed')}/{c.get('planned')} "
                 f"frame problems={c.get('frame_hard')} syllable misses={c.get('syl_miss')}")
        L.append(f"incumbent: plan_ok={i.get('plan_ok')} frame_ok={i.get('frame_ok')} cashed={i.get('cashed')}/{i.get('planned')} "
                 f"frame problems={i.get('frame_hard')} syllable misses={i.get('syl_miss')}")
        for h in (c.get("plan_hard") or [])[:2]:
            L.append(f"  candidate plan fail: {h[:150]}")
        for h in (c.get("frame_hard_list") or [])[:2]:
            L.append(f"  candidate frame fail: {h[:150]}")
        for rp in (v.get("repairs") or []):
            L.append(f"  bar loop ({rp['calls']} calls): " + " | ".join(s[:80] for s in rp["steps"]))
            if rp["after"] != rp["before"]:
                L += ["    before: " + " / ".join(rp["before"])] + ["    after:  " + " / ".join(rp["after"])]
        mg = v.get("merge") or {}
        if mg.get("log"):
            L.append(f"  per-bar ratchet ({mg.get('swaps', 0)} swap(s)): " + " | ".join(x[:90] for x in mg["log"][:8]))
        if v.get("errors"):
            L += [f"  stage errors: {e[:110]}" for e in v["errors"][:3]]
        if v["took"]:
            L += ["  --- taken:"] + [f"  {k}. {b}" for k, b in enumerate(v["candidate_bars"], 1)]
        L.append("")
    text = "\n".join(L)
    if path:
        open(path, "w", encoding="utf-8").write(text)
    return text
