"""Assemble a full draft from the section workflow results.

  python -m ww.write.assemble OUT.md  RESULT.json [RESULT.json ...]

Per section the FINAL block is used when the blind final judges score it at least as high as the incumbent (OLD); otherwise OLD stays.
Hook 1-4 is built like any other section (15 Oct 2026: the hard-coded "Joe's" hook was never approved and is retired).
Writes the draft in project format ('== Slot' headers) with the scores in comments.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "toolkit"))

ORDER = ["Hook 1-4", "Hook 5-8", "Hook 9-16", "V1 1-8", "V1 9-16", "V1 17-24", "V1 25-32", "V1 33-44", "V2 1-8", "V2 9-16"]


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    out, files = argv[0], argv[1:]
    inc = json.load(open("eval/_v3_inputs.json", encoding="utf-8"))["incumbents"]
    res = {}
    for f in files:
        for r in json.load(open(f, encoding="utf-8")):
            res[r["slot"]] = r
    lines = ["# ww full draft v2 (13 Oct 2026): round-3 method (no invented names, suffix/beat gates, wordplay lab, lexicon)",
             "# Project format: '== Slot' headers then that slot's bars. Scores: blind final judges, mean of 3 (original shown for scale).", ""]
    table = []
    for slot in ORDER:
        if slot in res and res[slot].get("final"):
            r = res[slot]
            f = r["final"]["scores"]
            if f.get("FINAL") is not None and f.get("OLD") is not None and f["FINAL"] >= f["OLD"]:
                bars, src = r["final_bars"], f"round 3 (final {f['FINAL']:.2f} vs previous {f['OLD']:.2f}, original {r['final']['ref']:.2f})"
            else:
                bars, src = inc[slot], f"previous draft kept (round 3 {f.get('FINAL')} did not beat {f.get('OLD')})"
            table.append((slot, f.get("FINAL"), f.get("OLD"), r["final"]["ref"]))
        else:
            bars, src = inc.get(slot, []), "previous draft (not re-run)"
        import retired
        bars = retired.strip_retired(bars)
        lines.append(f"== {slot}")
        lines.append(f"# source: {src}")
        lines += bars
        lines.append("")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    for t in table:
        print(f"{t[0]:9s} final {t[1]} previous {t[2]} original {t[3]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
