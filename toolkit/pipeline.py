"""pipeline: run the writing pipeline continuously until Joe says STOP.

Joe (11 Oct 2026): "run the writing pipeline continuously non stop. Do not stop until i manually say STOP."

So this loops forever. Each cycle it runs the exhaustive forge over every open slot, keeps the best
new quad it finds, appends it to a growing pool, and writes a heartbeat. Because the pool file lives in
writing/, the NEXT cycle mines it - so the corpus grows and the search feeds itself: quads found in
cycle N become bars available for recombination in cycle N+1. That is the improvement loop.

It stops on exactly two conditions:
  * the sentinel file writing/PIPELINE_STOP exists (created by Joe, or by the assistant on his word), or
  * the process is killed.

Artifacts it maintains:
  writing/pipeline_pool.md       the growing pool, one quad per line (the forge re-mines this)
  writing/pipeline_results.jsonl one JSON row per (cycle, slot): the best quad + its metrics
  writing/pipeline_log.md        a human-readable heartbeat, one line per slot per cycle
  writing/pipeline_status.json   current iteration, slot, best score, timestamp (machine-readable)

  python toolkit/pipeline.py                 # run (this is what the background job runs)
  python toolkit/pipeline.py --once          # a single pass over all slots, then exit
  python toolkit/pipeline.py --cycles 3      # a bounded number of full cycles
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (HERE, os.path.join(ROOT, "ml")):
    if p not in sys.path:
        sys.path.insert(0, p)

import forge                      # noqa: E402
from check_all import SLOTS, SIZES  # noqa: E402

WR = os.path.join(ROOT, "writing")
POOL = os.path.join(WR, "pipeline_pool.md")
LOG = os.path.join(WR, "pipeline_log.md")
RESULTS = os.path.join(WR, "pipeline_results.jsonl")
STATUS = os.path.join(WR, "pipeline_status.json")
STOP = os.path.join(WR, "PIPELINE_STOP")

# Hook 1-4 is Joe's locked section: never a target, and never regenerated.
SLOT_ORDER = [s for s in ("Hook 5-8", "Hook 9-16", "V1 1-8", "V1 9-16", "V1 17-24", "V1 25-32",
                          "V1 33-44", "V2 1-8", "V2 9-16") if s in SLOTS]
CAP, TOPK, CONFIRM_K = 12, 6, 12          # per-cycle search budget: keeps a cycle to a few minutes
KEEP_MAX_RISK = 0.45                      # only pool a quad the judge does not flag. Pooling every
#                                           best-so-far would rot the corpus with bad bars, and the
#                                           corpus is what the next cycle recombines.


def budget(cycle):
    """Widen the search as the loop runs: more candidate bars per position and more form checks."""
    return (min(20, CAP + (cycle - 1) // 3),
            TOPK,
            min(40, CONFIRM_K + (cycle - 1) * 2))


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def log(line, echo=True):
    if echo:
        print(line, flush=True)
    with open(LOG, "a", encoding="utf8") as fh:
        fh.write(line + "\n")


def load_kept():
    """Quads already in the pool, so the loop only ever ADDS something new."""
    if not os.path.exists(POOL):
        return set()
    out = set()
    for line in open(POOL, encoding="utf8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cells = [c.strip() for c in line.split("\t") if c.strip()]
        if len(cells) >= 2:
            out.add(tuple(c.lower() for c in cells))
    return out


def keep(slot, rec, cycle):
    with open(POOL, "a", encoding="utf8") as fh:
        fh.write("\t".join(rec["bars"]) + "\n")
        fh.write(f"# slot {slot} | cycle {cycle} | score {rec['score']} | judge risk {rec['risk']} "
                 f"| form {rec.get('form_n', '-')} | cash {rec['cash']}/{rec['need']} "
                 f"| orphans {rec['orphans']} | coh-fails {rec['coh_fails']} | {now()}\n")


def write_status(d):
    tmp = STATUS + ".tmp"
    with open(tmp, "w", encoding="utf8") as fh:
        json.dump(d, fh, indent=1)
    os.replace(tmp, STATUS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="one pass over all slots, then exit")
    ap.add_argument("--cycles", type=int, default=0, help="max full cycles (0 = forever)")
    a = ap.parse_args()
    if a.once:
        a.cycles = 1

    os.makedirs(WR, exist_ok=True)
    model = None
    try:
        import judge as J
        model = J.load_model()
        log(f"[{now()}] pipeline START - judge loaded, {len(SLOT_ORDER)} open slots "
            f"(Hook 1-4 is locked and never targeted)")
    except Exception as e:                                # noqa: BLE001
        log(f"[{now()}] pipeline START - WARNING no judge model ({e}); ranking on gates alone")
    if not model:
        log("   run `python ml/build_dataset.py && python ml/train_judge.py` to enable the judge")
    log(f"   stop with: create {os.path.relpath(STOP, ROOT)}  (or kill the process)")

    kept = load_kept()
    log(f"   pool starts with {len(kept)} kept quads")

    it, added, best_ever = 0, 0, None
    best_by_slot = {}
    while True:
        if os.path.exists(STOP):
            log(f"[{now()}] STOP sentinel found ({os.path.relpath(STOP, ROOT)}) - exiting cleanly "
                f"after {it} cycles, {added} new quads")
            break
        if a.cycles and it >= a.cycles:
            log(f"[{now()}] reached --cycles {a.cycles}; exiting after {it} cycles, {added} new quads")
            break
        it += 1
        log(f"\n[{now()}] ===== cycle {it} =====")
        for slot in SLOT_ORDER:
            if os.path.exists(STOP):
                log(f"[{now()}] STOP requested mid-cycle - finishing now")
                break
            t0 = time.time()
            cap, topk, confirm_k = budget(it)
            try:
                # variants=True is available and measured NOT to help (823 extra bars, best score
                # unchanged at 1.52 on Hook 5-8), so the loop searches the real corpus only.
                top, stats = forge.run(slot, cap=cap, topk=topk, confirm_k=confirm_k, model=model)
            except Exception as e:                        # noqa: BLE001
                log(f"  {slot:<10} ERROR {type(e).__name__}: {str(e)[:80]}")
                continue
            took = time.time() - t0
            if not top:
                log(f"  {slot:<10} explored {stats['explored']:<5} no quad passed the meaning gate "
                    f"({took:.0f}s)")
                write_status({"cycle": it, "slot": slot, "iteration": it, "updated": now()})
                continue
            rec = top[0]
            key = tuple(b.lower() for b in rec["bars"])
            fresh = key not in kept
            improved = rec["score"] < best_by_slot.get(slot, float("inf"))
            best_by_slot[slot] = min(best_by_slot.get(slot, float("inf")), rec["score"])
            # pool it only if it is NEW and the judge does not flag it - the pool is the next cycle's
            # raw material, so a bad quad in it makes the whole search worse
            worth = rec["risk"] is not None and rec["risk"] < KEEP_MAX_RISK
            if fresh and worth:
                kept.add(key)
                keep(slot, rec, it)
                added += 1
            with open(RESULTS, "a", encoding="utf8") as fh:
                fh.write(json.dumps({"cycle": it, "slot": slot, "fresh": fresh, "pooled": fresh and worth,
                                     "improved": improved, "taken": now(),
                                     **{k: v for k, v in rec.items() if k != "form"}},
                                    ensure_ascii=False) + "\n")
            if best_ever is None or rec["score"] < best_ever:
                best_ever = rec["score"]
            tag = ("NEW+POOLED" if (fresh and worth) else
                   ("new but below the pooling bar" if fresh else "already in pool"))
            log(f"  {slot:<10} explored {stats['explored']:<5} kept {stats['meaning_pass']:<4} "
                f"| pool {stats.get('bar_pool', '?')} bars ({stats.get('variants', 0)} variants) "
                f"| best score {rec['score']:<7} risk {rec['risk']} form {rec.get('form_n', '-')} "
                f"| {tag}{' | IMPROVED' if improved else ''} | {took:.0f}s")
            log(f"      {rec['bars'][0]} / {rec['bars'][-1]}")
            write_status({"cycle": it, "slot": slot, "added": added, "best_score": best_ever,
                          "pool_size": len(kept), "cap": cap, "confirm_k": confirm_k,
                          "updated": now()})

    log(f"[{now()}] pipeline ENDED - {it} cycles, {added} new quads, pool {len(kept)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
