"""Does the semantic reader (ww/judge/reader.py) separate CLAIMS from RECOUNTS? (plan step 1.2, 14 Oct 2026)

The reader labels each bar event / claim / stance / ... It has never been checked against anything, so before any number from it
is used, run it on:
  * the ORIGINAL, section by section (read from outside the project; only counts are printed or saved -- rule 4)
  * the known recounts: v17 V1 33-44 (the itinerary), v17 V2 1-8 (the Hanoi diary), v5 V1 9-16 (the jeep)
and compare the EVENT share (bars typed `event`) with toolkit/recount.py's deterministic recount share on the same sections.

The reader passes this check only if every negative's event share is above the original's busiest verse section. The result
is written to eval/reader_validation.json and decides whether the reader may feed the claim-share quota (ww.registry). Until
then the quota is measured by recount.py, which is deterministic and calibrated.

  python -m ww.judge.reader_validate            (needs DEEPSEEK_API_KEY; about 13 short calls, well under one cent)
"""
from __future__ import annotations

import json
import os
import sys
import time

from .. import config
from ..llm import LLM, Ledger
from . import reader

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "toolkit"))


def run() -> int:
    import recount as rc
    import private_path
    if not config.secret("DEEPSEEK_API_KEY"):
        print("reader_validate: DEEPSEEK_API_KEY is not set -- cannot run here. Nothing recorded.")
        return 2
    llm = LLM(ledger=Ledger(run_id="reader_validate"))
    rows = []

    def measure(label, slot, bars, negative):
        reading = reader.read_run(llm, bars, stage="reader_validate")
        types = [(b or {}).get("type", "nonsense") for b in (reading.get("bars") or [])]
        n = len(bars)
        ev = sum(1 for t in types if t == "event") / n if n else 0.0
        cl = sum(1 for t in types if t in ("claim", "stance")) / n if n else 0.0
        rows.append({"label": label, "slot": slot, "negative": negative, "n": n, "reader_event_share": round(ev, 3),
                     "reader_claim_share": round(cl, 3), "recount_share": round(rc.section_measures(bars)["share"], 3),
                     "usd": reading.get("_usd", 0.0)})

    for slot, bars in rc.original_sections(private_path.original_path()):
        measure("original", slot, bars, False)
    for rel, slot in rc.NEGATIVES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            secs = dict(rc.sections_of(open(p, encoding="utf8").read()))
            if slot in secs:
                measure(rel, slot, secs[slot], True)
    orig_verse = [r["reader_event_share"] for r in rows if not r["negative"] and not r["slot"].lower().startswith("hook")]
    ceiling = max(orig_verse) if orig_verse else 1.0
    negs = [r for r in rows if r["negative"]]
    separates = bool(negs) and all(r["reader_event_share"] > ceiling for r in negs)
    out = {"ts": round(time.time(), 3), "rows": rows, "original_verse_event_ceiling": ceiling, "separates": separates,
           "verdict": "reader may feed the claim-share quota" if separates else "reader stays a diagnostic note"}
    config.EVAL_DIR.mkdir(parents=True, exist_ok=True)
    (config.EVAL_DIR / "reader_validation.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    for r in rows:
        print(f"  {'NEG ' if r['negative'] else 'orig'} {r['slot']:10} reader event {r['reader_event_share']:.2f} "
              f"claim {r['reader_claim_share']:.2f} | recount {r['recount_share']:.2f}")
    print(f"reader_validate: original verse event ceiling {ceiling:.2f}; separates={separates} -> {out['verdict']}")
    return 0 if separates else 1


if __name__ == "__main__":
    sys.exit(run())
