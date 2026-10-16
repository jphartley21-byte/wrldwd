"""The original's quality par for ww/write/qualityread.py (15 Oct 2026). PRIVATE: the original's sections go to Claude through a
private client (no cache, hashes only in the ledger; anthropic approved by Joe on 13 Oct 2026), read with the SAME prompt and
narrator card as our bars, and only NUMBERS leave: benchmark/quality_par_<model>.json holds per-bar marks and per-slot means, never a
word of the original (rule 4). The reader's notes and forced words are discarded; `forced` is stored as 0/1.

in_character is recorded but is not a par: the card describes our narrator, not the original's.

  python -m ww.calib.quality_par [--runs 2]
  python -m ww.calib.quality_par --sense     the sense gate run on the original (positive control), counts only
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from .. import config
from ..write import qualityread as qr
from .original import SECTIONS, _lines, private_llm

AXES = qr.AXES


def build(runs: int = 2) -> dict:
    lines = _lines()
    narrator = qr.card()
    llm = private_llm("quality-par")
    jobs = [(name, lines[s:e]) for name, s, e in SECTIONS]
    with ThreadPoolExecutor(max_workers=5) as ex:
        reads = list(ex.map(lambda j: qr.read_section(j[0], j[1], llm, narrator, store=False, runs=runs), jobs))
    slots: dict = {}
    for (name, bars), rows in zip(jobs, reads):
        per = [{a: r[a] for a in AXES} | {"forced": r["forced_rate"]} for r in rows]   # numbers only: the forced WORD is dropped
        slots[name] = {"bars": per, **{k: round(sum(b[k] for b in per) / len(per), 2) for k in (*AXES, "forced")}}
    out = {"what": "the original's quality marks from ww/write/qualityread.py (Claude, same prompt and card as ours); numbers only",
           "model": qr.MODEL, "prompt": qr.PROMPT_VERSION, "runs": runs, "slots": slots,
           "song": {k: round(sum(s[k] for s in slots.values()) / len(slots), 2) for k in (*AXES, "forced")}}
    qr.PAR.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--sense", action="store_true", help="the sense gate's fail count on the original instead")
    ap.add_argument("--carried-only", action="store_true", help="with --sense: re-read only slots with a sentence over the bar line")
    a = ap.parse_args(argv)
    if a.sense:
        r = sense_par(only_carried=a.carried_only)
        for n, v in r["slots"].items():
            print(f"{n:10s} sense fails {v['fail']}/{v['bars']} {v['fail_bars']}  block ok {v['block_ok']} coherent {v['coherent']} broken links {v['links_broken']}")
        print(f"ORIGINAL: the sense gate ({r['model']}) fails {r['fail']}/{r['of']} of the original's bars")
        return 0
    out = build(a.runs)
    for name, s in out["slots"].items():
        print(f"{name:10s} " + " ".join(f"{k} {s[k]:.2f}" for k in (*AXES, "forced")))
    print("song       " + " ".join(f"{k} {v:.2f}" for k, v in out["song"].items()))
    print(f"wrote {qr.PAR.relative_to(config.ROOT)} (numbers only)")
    return 0



def sense_par(reads: int = 2, only_carried: bool = False) -> dict:
    """the sense gate (ww/write/sensecheck.py, Claude) run on the original: per slot, how many bars it would fail. The original is the
    positive control (rule 9): a per-bar HARD sense rule is only right if the original passes it. Numbers only; nothing cached.
    16 Oct 2026: read the way the gate now reads a draft, a sentence that runs over the bar line as ONE item (sensecheck.units).
    only_carried=True re-reads only the slots holding such a sentence and keeps the stored numbers for the rest (a fresh read of an
    unchanged slot would only re-roll the judge's noise)."""
    from ..write import sensecheck as sc
    lines = _lines()
    llm = private_llm("sense-par")
    model = sc.model()
    path = config.ROOT / "benchmark" / f"sense_par_{model}.json"
    old = {}
    if only_carried:
        try:
            old = json.loads(path.read_text(encoding="utf-8")).get("slots", {})
        except (OSError, ValueError):
            old = {}

    def one(job):
        name, bars = job
        U = sc.units(bars)
        if only_carried and name in old and all(len(u) == 1 for u in U):
            return name, old[name]
        rows = sc.read_units(bars, llm, model, reads=1 if model == "ds-flash" else reads)
        fl = sc.fails_of(bars, rows)
        fails = [n for n, _ in fl]
        bv = sc.block_units(bars, sc._block_read(sc.unit_texts(bars, U), llm, model), U)
        # "fail" = failing SENTENCES (the gate compares sensecheck.fail_units); in a slot with no run-on sentence that is the bar count
        return name, {"bars": len(bars), "fail": sc.fail_units(bars, fl), "fail_bars": fails, "block_ok": bv["ok"], "coherent": bv["coherent"],
                      "links_broken": len(bv["fails"]), "sentences_over_bar_line": [[i + 1 for i in u] for u in U if len(u) > 1]}
    with ThreadPoolExecutor(max_workers=5) as ex:
        out = dict(ex.map(one, [(n, lines[s:e]) for n, s, e in SECTIONS]))
    tot = sum(v["fail"] for v in out.values())
    res = {"what": "bars of the original the sense gate fails, per slot (bar numbers within the slot; no text)", "model": model,
           "reads": reads, "slots": out, "fail": tot, "of": sum(v["bars"] for v in out.values())}
    path.write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    raise SystemExit(main())
