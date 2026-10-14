"""evaluate: the acceptance gate for the ml/ layer, in the same style as toolkit/calibrate.py.

Run this after any change to the features, the lexicons or the model. It must PASS before the judge
is used in the drafting loop. Three tests, in order of how much they are worth:

  1. CONTRACT (the one that matters). Every stanza Joe rejected is flagged; the stanza he locked is
     not. This mirrors toolkit/calibrate.py, where the rejected fixtures must FAIL the form checks.
  2. HELD-OUT SANITY. The "park" stanza (Joe: "not bad, it's a contender") is scored WITHOUT ever
     being trained on, and must land between the accept and reject tiers, not with the rejects.
     With so few labels this is the closest thing to an honest generalisation number.
  3. DISCRIMINATION CHECK. The judge is run over the ~400 never-judged bars. A screen that calls
     everything a reject is useless, so this prints the distribution and fails if the judge has
     collapsed. This is the honest counterweight to an in-sample contract.

  python ml/evaluate.py            # prints the report, exits 1 on any failure
  python ml/evaluate.py --json     # machine-readable summary
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import features as F                 # noqa: E402
import train_judge as T              # noqa: E402
import judge as J                    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    model = J.load_model()
    rows = T.load()

    by_tier = {}
    for r in rows:
        by_tier.setdefault(r["label"], []).append(r)

    # ---- 1. contract -------------------------------------------------------------------------
    blocks = {}
    for r in rows:
        blocks.setdefault(r["block"], []).append(r)
    contract_fail = []
    for blk, items in blocks.items():
        label = items[0]["label"]
        texts = [r["text"] for r in items]
        feats = [r["features"] for r in items]
        mean = float(model.risk(texts, feats).mean())
        if label == "reject" and mean < 0.5:
            contract_fail.append(f"{blk} scored {mean:.2f} (< 0.5)")
        if label == "accept" and mean >= 0.5:
            contract_fail.append(f"{blk} scored {mean:.2f} (>= 0.5)")

    # ---- 2. held-out park sanity -------------------------------------------------------------
    park = by_tier.get("park", [])
    park_mean = float(model.risk([r["text"] for r in park],
                                 [r["features"] for r in park]).mean()) if park else None
    acc_mean = float(np.mean([float(model.risk([r["text"]], [r["features"]])[0])
                              for r in by_tier.get("accept", [])]))
    rej_mean = float(np.mean([float(model.risk([r["text"]], [r["features"]])[0])
                              for r in by_tier.get("reject", [])]))
    park_ok = park_mean is not None and acc_mean <= park_mean <= rej_mean

    # ---- 3. discrimination on the never-judged pool ------------------------------------------
    unl = by_tier.get("unlabel", [])
    unl_scores = model.risk([r["text"] for r in unl], [r["features"] for r in unl]) if unl else []
    share_land = float(np.mean(np.asarray(unl_scores) < 0.5)) if len(unl_scores) else 0.0
    collapsed = share_land < 0.05 or share_land > 0.95 if len(unl_scores) else True

    result = {
        "rows": len(rows),
        "tiers": {k: len(v) for k, v in sorted(by_tier.items())},
        "contract_failures": contract_fail,
        "park_mean_risk": None if park_mean is None else round(park_mean, 3),
        "accept_mean_risk": round(acc_mean, 3),
        "reject_mean_risk": round(rej_mean, 3),
        "park_between_accept_and_reject": bool(park_ok),
        "unlabel_share_scoring_as_land": round(share_land, 3),
        "unlabel_collapsed": bool(collapsed),
    }
    result["passed"] = bool(not contract_fail and park_ok and not collapsed)

    if a.json:
        print(json.dumps(result, indent=1))
        sys.exit(0 if result["passed"] else 1)

    print(f"rows {result['rows']}  tiers {result['tiers']}\n")
    print("1. CONTRACT (rejected stanzas flag, locked stanza does not)")
    print("   PASSED" if not contract_fail else "   FAILED")
    for f in contract_fail:
        print("     x", f)
    print("\n2. HELD-OUT PARK SANITY (never trained on)")
    print(f"   accept {acc_mean:.2f}  <=  park {park_mean if park_mean is not None else float('nan'):.2f}"
          f"  <=  reject {rej_mean:.2f}   {'OK' if park_ok else 'FAILED'}")
    print("\n3. DISCRIMINATION on the never-judged pool")
    print(f"   {share_land*100:.0f}% of {len(unl_scores)} unlabelled bars score as LAND "
          f"({'COLLAPSED - the judge is not discriminating' if collapsed else 'spread OK'})")
    print("\nML EVALUATION", "PASSED" if result["passed"] else "FAILED")
    print("\nHonest limits (see ml/README.md): the contract is nearly in-sample, and there are only "
          f"{len(by_tier.get('accept', [])) + len(by_tier.get('like', []))} positive rows. "
          "A LEARNED judge needs more of Joe's verdicts, not a better model.")
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
