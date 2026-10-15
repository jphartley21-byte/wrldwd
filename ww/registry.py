"""Measure registry (R3, R6): what each instrument is allowed to do, and the evidence.

Status ladder:  unvalidated -> accepted | demoted ;  legacy instruments start as failed_validation / diagnostic.
Only `accepted` measures may rank or veto; everything else is printed as a diagnostic and nothing else.

PRE-REGISTRATION (written before v27 or any draft is scored by the new judge): the acceptance rule below is hashed into
`prereg_hash` and stored in eval/registry.json with a timestamp; the sealed split is consumed through `spend_look()` which
counts looks. Changing the rule after the fact bumps `prereg_version` and is recorded - it cannot be done silently.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Optional

from . import config

REGISTRY = config.EVAL_DIR / "registry.json"

# plan 5.4. An axis is ACCEPTED only if every clause holds on the sealed test, with cluster-level statistics.
PREREG = {
    "unit_of_resampling": "cluster (quad / block / poem); never bars or pairs",
    "point_accuracy_min": 0.90,
    "cluster_lower_bound_min": 0.65,
    "dev_vs_sealed_gap_max": 0.10,
    "null_edit_tie_rate_min": 0.70,
    "artefact_detector_corr_must_be_below_sense_corr": True,
    "sealed_looks_per_frozen_version": 1,
    "order_flip_rate_max": 0.15,
    "statistics_reported_not_gated": ["AUC", "Cohen kappa (reliability between independent judges, not validity)",
                                      "Joe-accepted-vs-rejected block ranking (k of n smoke check)"],
    "multiple_comparison_correction": "Holm across axes x degradations",
    "assistant_labels": "weight 0.25, dev only, never in sealed test or any exit criterion",
    "exit_floors": "one-sided non-inferiority vs the original per accepted axis; filler/nonsense rate <= original + margin; "
                   ">= 8 of 76 bars verified cashed-payoff; worst-quad rule; claim-share quota; tripwire quiet",
}

# what the audit and the labelled-set tests already established (STATE.md, 11-13 Oct 2026)
LEGACY = {
    "toolkit/phon.best_end (rhyme grader)": ("validated", "refit 12 Oct on 14 by-ear pairs: 4/10 wrong -> 1/14 wrong; assonance at 0.80 still passes as rhyme"),
    "toolkit/match.py (scheme/length vs original profile)": ("diagnostic", "similarity to the original's audio, not quality. The evidence that it 'fails Joe's own accepted bars' was withdrawn 15 Oct 2026: it rested on the four Hook 1-4 bars once called Joe's approved bars, which Joe says were never approved"),
    "toolkit/flow_fit pattern % / beat grid": ("unvalidated", "the 12 Oct failed_validation verdict was withdrawn 15 Oct 2026: it rested on the four Hook 1-4 bars once called Joe's approved bars, which Joe says were never approved. Still not a gate: on 56 round-1 candidates its pattern % had rho 0.09 with the judges' flow scores (ww/write/slotcheck.py)"),
    "toolkit/flow_fit syllable count + end shape": ("accepted_exact_fact", "measured from the original's audio; hard facts, not quality"),
    "toolkit/meaning_gate inventory rule": ("diagnostic", "catches 6/11 known-dead bars, fires on 0/92 original lines; prefilter only"),
    "toolkit/coherence_gate": ("diagnostic", "calibrated on the original; gibberish passed it"),
    "toolkit/funny.py": ("failed_validation", "89% base rate"),
    "toolkit/attest.py": ("failed_validation", "flags good lines as hard as gibberish ('Paid him by the weight', 'Might take the ferry to Bergen'); the part of the evidence that used Joe's 'approved' bars was withdrawn 15 Oct 2026: it rested on the four Hook 1-4 bars once called Joe's approved bars, which Joe says were never approved"),
    "toolkit/ear.py device rate": ("diagnostic", "original 53% of quads; a 60% gate failed the benchmark"),
    "toolkit/imagery.py chains": ("diagnostic", "the original has a chain in 4 of 19 quads; the claim 'Joe's approved bars have zero chains' was withdrawn 15 Oct 2026: it rested on the four Hook 1-4 bars once called Joe's approved bars, which Joe says were never approved"),
    "ml/judge.py (learned)": ("failed_validation", "its one positive block was the four never-approved Hook 1-4 bars; the saved model was deleted 15 Oct 2026; 3 of 5 of Joe's rules inverted; word-level coefficients <= 0.014"),
    "ml/meaning_judge.py (llama3 paraphrase)": ("unvalidated", "93% on 14 bars, half authored by the assistant; a sifter, not a gate"),
    "toolkit/forge.py / pipeline.py / tryforms.py": ("failed_validation", "recombine only; best score identical for 14 cycles; crowned a gibberish block"),
    "toolkit/check_all.py as a quality gate": ("unvalidated", "kept as a ranking readout; the evidence that it 'fails Joe's own accepted bars' was withdrawn 15 Oct 2026: it rested on the four Hook 1-4 bars once called Joe's approved bars, which Joe says were never approved"),
    # 14 Oct 2026: the claim-share quota (PREREG exit floor) is measured by recount.py, deterministically. Calibrated on the original
    # (passes its own par: song recount share 0.20, longest verse chain 3, no itinerary bars) and catches all three named recounts
    # (v17 V1 33-44 itinerary, v17 V2 1-8 Hanoi diary, v5 V1 9-16 jeep). Song shares: original 0.20, v17 0.50, v5 0.66, pasted 0.78.
    "toolkit/recount.py (claim-share quota)": ("validated", "original passes its own par; 3 of 3 named recounts fail; deterministic"),
    # 15 Oct 2026: the original passes (hook stamps 9/16, verse swagger 25/60); v5, v6 and the three 14 Oct premise hooks fail.
    # A lexicon proxy: it says whether the song boasts at all, not whether a boast is good.
    "toolkit/swagger.py (hook stamps + verse menace)": ("validated", "original passes its own par; 5 of 5 drafts Joe rejected as diaries fail"),
    # 15 Oct 2026, Joe: "make the stress check a hard gate". Narrow on purpose: one syllable, the one before the rhyme.
    "toolkit/flow_fit.approach (stress before the rhyme)": ("joe_rule", "HARD in slotcheck on Joe's instruction. The original passes in all 74 templated bars "
                                                           "(by construction: the stress marks come from its own text); both bars Joe heard as jammed fail. No independent "
                                                           "good set exists, and the dictionary stress model reads some secondary stresses as strong (the 'in' of invasion)"),
    "toolkit/flow_par.py (per-bar par: stress run, hard joins, closed-vowel run, restart)": ("joe_rule", "HARD in slotcheck since 15 Oct 2026. "
        "Catches 4 of 4 bars Joe flagged for flow (toolkit/tests/flow_flagged.txt); the original passes by construction (each bar is its own par). "
        "Tolerances (stress +1, joins 0, closed vowels +1, restart +1) fitted in-sample on those 4 and the 15 bars of hook r3 Joe liked; "
        "5 of the 15 still fail and are listed to Joe. toolkit/tests/flow_ok.txt (bars Joe confirms) must all pass"),
    # 15 Oct 2026, Joe: "originals end rhymes are better rn" and the Lagos / favours / flavours / Vegas carpet.
    "ww/write/rapfit.quality_hard (block rhyme: carpet, cheap rime, identical rime)": ("joe_rule", "HARD in slotcheck since 15 Oct 2026. "
        "The original passes every slot by construction (its own counts, benchmark/rhyme_quality_targets.json, +1 slack on cheap and identical); the carpet counts a pair only when the endings chain from the end (chain_best), since a shared stressed vowel alone passed an ABBA Hook 5-8 as AAAA; "
        "Joe's two complaints fail on 7 of 7 sections he heard as worse (toolkit/tests/rhyme_complaints.txt). Cheap threshold (150 words sharing "
        "the rime) and the slack are chosen in-sample on one song; no independent good set exists"),
    "ww/write/rapfit.score (pair: do these rhyme?)": ("unvalidated", "by-ear AUC 0.956 on 274 pairs of the original labelled by rhyme FAMILY "
        "(toolkit/match.MANUAL_SCHEME; Hook 5-8 AAAA), recall 94%, non-rhymes accepted 2%; in-sample, and V2 9-16 is still blind (AUC 0.50). It says whether a "
        "pair rhymes, not how good the rhyme is: a common, identical rime scores 1.0"),
    # 15 Oct 2026, Joe on Hook 9-16 bars 13-14: "How is [ours] the same flow as" the original's. Both rules are per bar, against the original's same bar.
    "toolkit/flow_par fast_jam + cell + barline (16th-note stress jams; repeated cell + internal rhyme; end rhyme landed at the bar line)": ("joe_rule", "HARD in slotcheck via flow_par since 15 Oct 2026. barline: 35 of the original's 74 timed lines run past one musical bar; it lands a rhyme on its own end at the bar line in bars 13, 41, 42, 50, and ours must too. "
        "The original passes by construction. fast_jam (TOL 0) also catches 3 earlier flagged bars for the reason Joe gave for one of them ('stresses bunch "
        "up'); the cell rule applies only at the original's 5 repeated-cell bars (13, 24, 40, 48, 50). One labelled complaint; no independent good set"),
    "ww/judge/reader.py event/claim labels": ("unvalidated", "never run against the original; ww/judge/reader_validate.py is the test "
                                                             "(needs DEEPSEEK_API_KEY, absent in the 14 Oct cloud session)"),
}


def claim_share(sections) -> dict:
    """the PREREG claim-share quota: share of bars that do NOT recount (1 - recount share), song-wide, with recount.py's verdict.
    sections = [(slot, bars)]."""
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "toolkit"))
    import recount
    fails, _rows, song = recount.run(sections, overlap=False, quiet=True)
    return {"claim_share": round(1 - song, 3), "floor": round(1 - recount.ORIGINAL_SONG_SHARE - recount.SONG_MARGIN, 3),
            "fails": fails}


def prereg_hash() -> str:
    return hashlib.sha256(json.dumps(PREREG, sort_keys=True).encode("utf-8")).hexdigest()


def _load() -> dict:
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"prereg_version": 1, "prereg": PREREG, "prereg_hash": prereg_hash(), "locked_at": round(time.time(), 3),
            "legacy": {k: {"status": s, "evidence": e} for k, (s, e) in LEGACY.items()}, "measures": {}, "sealed_looks": {}}


def _save(d: dict) -> None:
    config.EVAL_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def init() -> dict:
    d = _load()
    if d["prereg_hash"] != prereg_hash():
        d["prereg_version"] += 1
        d.setdefault("prereg_history", []).append({"version": d["prereg_version"] - 1, "hash": d["prereg_hash"], "changed_at": round(time.time(), 3)})
        d["prereg"], d["prereg_hash"] = PREREG, prereg_hash()
    for k, (st, ev) in LEGACY.items():   # a legacy instrument added after the file was first written must still be known
        d.setdefault("legacy", {}).setdefault(k, {"status": st, "evidence": ev})
    _save(d)
    return d


def register(name: str, kind: str, code_hash: str = "") -> dict:
    d = init()
    d["measures"].setdefault(name, {"kind": kind, "status": "unvalidated", "evidence": [], "code_hash": code_hash})
    d["measures"][name]["code_hash"] = code_hash or d["measures"][name]["code_hash"]
    _save(d)
    return d["measures"][name]


def spend_look(measure: str, frozen_version: str) -> int:
    """consume one look at the sealed split for (measure, frozen judge version); refuses a second look."""
    d = init()
    key = f"{measure}@{frozen_version}"
    n = d["sealed_looks"].get(key, 0)
    if n >= PREREG["sealed_looks_per_frozen_version"]:
        raise RuntimeError(f"sealed split already looked at for {key}; freeze a new judge version (and move the used clusters to dev)")
    d["sealed_looks"][key] = n + 1
    _save(d)
    return n + 1


def decide(measure: str, *, point: float, cluster_lb: float, dev_point: float, null_tie: float, artefact_ok: bool,
           n_clusters: int, flip_rate: Optional[float] = None) -> dict:
    """apply the pre-registered rule and record the verdict with the numbers behind it."""
    p = PREREG
    checks = {
        "point>=%.2f" % p["point_accuracy_min"]: point >= p["point_accuracy_min"],
        "cluster_lb>=%.2f" % p["cluster_lower_bound_min"]: cluster_lb >= p["cluster_lower_bound_min"],
        "dev_gap<=%.2f" % p["dev_vs_sealed_gap_max"]: abs(dev_point - point) <= p["dev_vs_sealed_gap_max"],
        "null_tie>=%.2f" % p["null_edit_tie_rate_min"]: null_tie >= p["null_edit_tie_rate_min"],
        "artefact_control": bool(artefact_ok),
    }
    if flip_rate is not None:
        checks["flip<=%.2f" % p["order_flip_rate_max"]] = flip_rate <= p["order_flip_rate_max"]
    status = "accepted" if all(checks.values()) else "demoted"
    d = init()
    m = d["measures"].setdefault(measure, {"kind": "reader", "status": "unvalidated", "evidence": [], "code_hash": ""})
    m["status"] = status
    m["evidence"].append({"ts": round(time.time(), 3), "n_clusters": n_clusters, "point": point, "cluster_lb": cluster_lb,
                          "dev_point": dev_point, "null_tie": null_tie, "checks": checks})
    _save(d)
    return {"status": status, "checks": checks}


def may_gate(measure: str) -> bool:
    """True only for an accepted measure (or a legacy exact fact). Everything else is a diagnostic."""
    d = init()
    m = d["measures"].get(measure)
    if m:
        return m["status"] == "accepted"
    l = d["legacy"].get(measure)
    return bool(l and l["status"] in ("validated", "accepted_exact_fact"))


def selftest() -> tuple[bool, str]:
    import tempfile
    from pathlib import Path
    global REGISTRY
    old = REGISTRY
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        REGISTRY = Path(td) / "registry.json"
        try:
            init()
            if may_gate("never-seen"):
                problems.append("unknown measure must not gate")
            r = decide("axis_sense", point=0.95, cluster_lb=0.70, dev_point=0.93, null_tie=0.8, artefact_ok=True, n_clusters=8)
            if r["status"] != "accepted" or not may_gate("axis_sense"):
                problems.append(f"good evidence should accept: {r}")
            r = decide("axis_funny", point=0.70, cluster_lb=0.40, dev_point=0.80, null_tie=0.9, artefact_ok=True, n_clusters=8)
            if r["status"] != "demoted" or may_gate("axis_funny"):
                problems.append(f"weak evidence must demote: {r}")
            spend_look("axis_sense", "v1")
            try:
                spend_look("axis_sense", "v1")
                problems.append("second sealed look must be refused")
            except RuntimeError:
                pass
            if may_gate("toolkit/flow_fit pattern % / beat grid"):
                problems.append("failed legacy instrument must not gate")
            if not may_gate("toolkit/flow_fit syllable count + end shape"):
                problems.append("exact legacy fact should be usable")
            if may_gate("ww/judge/reader.py event/claim labels"):
                problems.append("the unvalidated reader must not gate")
            diary = [("V2 1-8", ["We left the hostel at nine with no clues", "We rode the bikes along the coast for days",
                                 "The rain came down and soaked us to the bone", "We lost each other in the traffic queues"])]
            if not claim_share(diary)["fails"]:
                problems.append("claim-share quota must fail a past-tense diary")
        finally:
            REGISTRY = old
    return (not problems, "; ".join(problems) if problems else "pre-registered rule, sealed-look counter and legacy statuses behave")
