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
    "toolkit/match.py (scheme/length vs original profile)": ("diagnostic", "similarity to the original's audio, not quality: fails Joe's own accepted bars on 3 of 4 sub-checks"),
    "toolkit/flow_fit pattern % / beat grid": ("failed_validation", "ranked Joe's approved bars (50/50/50/33%) below a rejected bar (62%)"),
    "toolkit/flow_fit syllable count + end shape": ("accepted_exact_fact", "measured from the original's audio; hard facts, not quality"),
    "toolkit/meaning_gate inventory rule": ("diagnostic", "catches 6/11 known-dead bars, fires on 0/92 original lines; prefilter only"),
    "toolkit/coherence_gate": ("diagnostic", "calibrated on the original; gibberish passed it"),
    "toolkit/funny.py": ("failed_validation", "89% base rate"),
    "toolkit/attest.py": ("failed_validation", "flags Joe's approved bars as hard as gibberish"),
    "toolkit/ear.py device rate": ("diagnostic", "original 53% of quads; a 60% gate failed the benchmark"),
    "toolkit/imagery.py chains": ("diagnostic", "Joe's approved bars have zero chains"),
    "ml/judge.py (learned)": ("failed_validation", "trained on 1 positive block; 3 of 5 of Joe's rules inverted; word-level coefficients <= 0.014"),
    "ml/meaning_judge.py (llama3 paraphrase)": ("unvalidated", "93% on 14 bars, half authored by the assistant; a sifter, not a gate"),
    "toolkit/forge.py / pipeline.py / tryforms.py": ("failed_validation", "recombine only; best score identical for 14 cycles; crowned a gibberish block"),
    "toolkit/check_all.py as a quality gate": ("failed_validation", "fails Joe's own accepted bars; kept as a ranking readout"),
}


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
        finally:
            REGISTRY = old
    return (not problems, "; ".join(problems) if problems else "pre-registered rule, sealed-look counter and legacy statuses behave")
