"""Rebuild loop (Joe, 13 Oct 2026: "rebuild a new draft from scratch ... keep improving until improvement plateaus").

  python -m ww.cli rebuild --rounds 6 --out writing/ww_full_draft_v10

ROUND 1 is fully from scratch (draft_all scratch=True: no incumbent read, shown or merged; every slot including Hook 1-4 is written from the plan and the pop-culture kit).
ROUNDS 2+ rebuild against the BEST draft so far with the strict ratchet (draft_all.take / merge_improve): a section or bar is replaced only if it wins, so a round can only move the draft forward.
Each round uses a different number of seeds, so its prompts differ from the last (the LLM cache is keyed on the prompt) and the failure log from earlier rounds feeds the next round's negatives (rule R10).

SCORE (deterministic, higher is better; it is NOT a quality measure, only a plateau detector): per slot  10*plan_ok + 6*frame_ok - 2*min(frame_hard,15) - 1.5*syllable_misses
+ 4*internal_echo + 2*cashed.  frame_hard includes the rapfit scheme-pair floor, the stress-anchor gate and the 3-syllable block rule; the beat-grid match, the
old grader's pair floor and carpet share, and check_all's problem count are NOT in it (failed validation / demoted).
PLATEAU: the loop stops after `patience` consecutive rounds that raise the total by <= `eps`, or after `rounds` rounds.
It cannot judge sense or wit: the finished draft must be READ before it is shown (rule 2 of the project), and only Joe's ear decides.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from .. import config
from . import argue_stage, draft_all, flowaudit


def total_score(path: str) -> dict:
    sec = flowaudit.parse_draft(path)
    per, total = {}, 0.0
    for slot in argue_stage.slots():
        bars = sec.get(slot, [])
        if not bars:
            per[slot] = {"value": -20.0, "usable": False}
            total -= 20.0
            continue
        s = draft_all.score_section(slot, bars)
        v = (10 * bool(s.get("plan_ok")) + 6 * bool(s.get("frame_ok")) - 2 * min(s.get("frame_hard", 0), 15) - 1.5 * s.get("syl_miss", 0)
             + 4 * s.get("echo", 0) + 2 * s.get("cashed", 0) - 1.5 * min(s.get("cad", 0), 4))
        per[slot] = {"value": round(v, 2), "plan_ok": s.get("plan_ok"), "frame_ok": s.get("frame_ok"), "frame_hard": s.get("frame_hard"),
                     "syl_miss": s.get("syl_miss"), "problems": s.get("problems"), "echo": s.get("echo"), "cashed": s.get("cashed")}
        total += v
    return {"total": round(total, 2), "per_slot": per}


def run(rounds: int = 6, seeds: int = 4, blocks: int = 3, model: str = "ds-flash", out_prefix: str = "writing/ww_full_draft_v10",
        patience: int = 2, eps: float = 1.0, repairs: int = 2, repair_calls: int = 10) -> dict:
    from ..llm import LLM, Ledger
    llm = LLM(ledger=Ledger(run_id="rebuild"))
    root = config.ROOT
    log, best_path, best, stale = [], None, None, 0
    logp = config.EVAL_DIR / "rebuild_log.json"
    for r in range(1, rounds + 1):
        t0 = time.time()
        res = draft_all.run(llm, slots=None, seeds=seeds + (r - 1), blocks=blocks, model=model, incumbent=best_path, rank=False,
                            repairs=repairs, repair_calls=repair_calls, kit=True, scratch=(r == 1))
        path = str(root / f"{out_prefix}_r{r}.md")
        draft_all.assemble(res, path)
        draft_all.report(res, str(root / f"{out_prefix}_r{r}_report.md"))
        sc = total_score(path)
        gain = None if best is None else round(sc["total"] - best["total"], 2)
        improved = best is None or sc["total"] > best["total"] + eps
        entry = {"round": r, "path": path, "total": sc["total"], "gain_vs_best": gain, "replaced": [s for s, v in res["slots"].items() if v.get("took")],
                 "minutes": round((time.time() - t0) / 60, 1), "per_slot": {k: v["value"] for k, v in sc["per_slot"].items()}}
        log.append(entry)
        logp.write_text(json.dumps(log, indent=1), encoding="utf-8")
        print(f"ROUND {r}: total {sc['total']} (gain {gain}) replaced {entry['replaced']} in {entry['minutes']} min -> {path}", flush=True)
        if best is None or sc["total"] > best["total"]:
            best_path, best = path, sc
        stale = 0 if improved else stale + 1
        if stale >= patience:
            print(f"PLATEAU: {patience} rounds in a row without a gain above {eps}", flush=True)
            break
    final = root / f"{out_prefix}.md"
    final.write_text(Path(best_path).read_text(encoding="utf-8"), encoding="utf-8")
    print(f"BEST: {best_path} (total {best['total']}) copied to {final}", flush=True)
    return {"best": best_path, "total": best["total"], "log": log}
