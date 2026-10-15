"""Score candidate blocks for a slot in ONE call - the fast inner loop.

Measured costs (11 Oct 2026): mine the corpus 0.2 s; judge + features 2 ms/bar;
scheme check 2 ms; check_all 264 ms/bar (it spawns match.py, flow_fit.py and helpers.py
per block). check_all therefore dominates, so it runs once per NEW block and is memoised
to the temp dir, while everything else runs in-process.

usage:
    python toolkit/trybars.py --slot "Hook 9-16" candidates.txt
    python toolkit/trybars.py --slot "Hook 9-16" -            < candidates.txt
    python toolkit/trybars.py --slot "Hook 9-16" - --detail   (per-bar + worst-bar drivers)

Blocks are separated by a blank line. '#' comments and 'N.' / 'N)' bar numbering are stripped.
Blocks are ranked by (form problems, judge risk) - form first because it is measured against
the slot's own frame, while the judge has one positive block and cannot certify a slot.
"""

import argparse
import hashlib
import json
import os
import re
import statistics
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "ml"))

# "3. " / "3) " bar numbering, and a UTF-8 BOM that PowerShell's Set-Content -Encoding UTF8 adds.
NUM_RE = re.compile(r"^\s*\d+[.)]\s+")

import check_all            # noqa: E402
import coherence_gate as cg  # noqa: E402
import craft_scan as cs      # noqa: E402
import devices as dv         # noqa: E402
import funny as fn           # noqa: E402
import features as F         # noqa: E402
import flow_fit as ff        # noqa: E402
import forge                 # noqa: E402
import meaning_gate as mg    # noqa: E402
import vocab as v            # noqa: E402

# The reference block for the worst-bar attribution below. Until 15 Oct 2026 it was the four Hook 1-4 bars once called
# "Joe's locked bars"; Joe: never approved, never a bar or a gate again. It is now the ORIGINAL's Hook 1-4, read at run
# time from the private file (WW_PRIVATE_ORIGINAL, outside the project; never printed). Without that file there is no
# reference and the attribution is skipped.
def _reference():
    p = os.environ.get("WW_PRIVATE_ORIGINAL", os.path.expanduser("~/Documents/WORLDWIDE_PRIVATE/original_lines.txt"))
    try:
        return [l.strip() for l in open(p, encoding="utf8") if l.strip()][:4]
    except OSError:
        return []


def _cache_path():
    return os.path.join(tempfile.gettempdir(), "trybars_cache.json")


def _load_cache():
    try:
        with open(_cache_path(), encoding="utf8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_cache(cache):
    try:
        with open(_cache_path(), "w", encoding="utf8") as fh:
            json.dump(cache, fh)
    except Exception:
        pass


def form_problems(slot, bars, cache=None):
    """check_all's problem list, memoised on (slot, bars)."""
    cache = _load_cache() if cache is None else cache
    key = slot + "|" + hashlib.sha1("\n".join(bars).encode("utf8")).hexdigest()[:16]
    if key not in cache:
        cache[key] = check_all.problems_of(slot, list(bars))[1]
        _save_cache(cache)
    return cache[key]


def parse_blocks(text):
    blocks, cur = [], []
    for raw in text.lstrip("\ufeff").splitlines():
        line = raw.strip()
        if not line:
            if cur:
                blocks.append(cur)
                cur = []
            continue
        if line.startswith("#"):
            continue
        line = NUM_RE.sub("", line).strip()
        if line:
            cur.append(line)
    if cur:
        blocks.append(cur)
    return blocks


def endings(bars, feats):
    tags = [i for i, x in enumerate(feats) if x["features"]["end_tag"]]
    soft = [i for i, x in enumerate(feats) if x["features"]["soft_ending"]]
    return tags, soft


def surname(bars):
    """The bar's tail as rhyme material, from the same reader check_all uses."""
    out = []
    for b in bars:
        vs = (cs.bar_tail(b) or {}).get("vowels") or []
        out.append("-".join(vs[-2:]) if len(vs) > 1 else (vs[-1] if vs else "?"))
    return out


def family_groups(tails):
    """Group bar indexes by their final vowel - the by-ear rhyme families."""
    groups = {}
    for i, t in enumerate(tails):
        groups.setdefault(t.split("-")[-1], []).append(i + 1)
    return {k: v for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))}


def worst_bar_drivers(model, bars, feats, bar_idx):
    """Which features push one bar toward reject, against the reference block."""
    import numpy as np
    import scipy.sparse as sp
    reference = _reference()
    if not reference:
        return []
    ref = F.block_row(reference, "t", "t", "t")
    ref_feats = [x["features"] for x in ref["bars"]]

    def design(bs, fs):
        num = model.num.transform(np.asarray([F.vector({"features": f}) for f in fs], dtype=float))
        return sp.hstack([sp.csr_matrix(num), model.word.transform(bs),
                          model.char.transform(bs)]).tocsr()

    names = model.numeric_features
    coef = model.lr.coef_[0][:len(names)]
    n = len(names)
    zm = design(bars, feats)[bar_idx, :n].toarray().ravel()
    za = design(reference, ref_feats)[:, :n].mean(axis=0).A1
    delta = coef * (zm - za)
    order = np.argsort(delta)[:5]
    return [(names[i], float(delta[i])) for i in order if abs(delta[i]) > 1e-9]


def score_block(slot, bars, model=None, cache=None, detail=False):
    fr = forge.slot_frame(slot)
    row = F.block_row(bars, "t", "t", "t")
    feats = row["bars"]
    risk = None
    if model is not None:
        import numpy as np
        risk = float(np.mean(model.risk(bars, [x["features"] for x in feats])))
    form = form_problems(slot, bars, cache)
    out = {
        "bars": bars,
        "syls": [len(ff.sylls(b)) for b in bars],
        "frame": fr.get("syls"),
        "scheme_ok": forge._scheme_ok(bars, fr),
        "tails": surname(bars),
        "families": family_groups(surname(bars)),
        "tags": endings(bars, feats)[0],
        "soft": endings(bars, feats)[1],
        "meaning_fails": mg.audit(bars, slot).get("fails", []),
        "coh_fails": cg.audit(bars, slot).get("fails", []),
        "form": form,
        "risk": risk,
        "per_bar_risk": [round(float(v), 2) for v in model.risk(bars, [x["features"] for x in feats])] if model else [],
        "feats": feats,
    }
    if detail and model is not None and out["per_bar_risk"]:
        w = int(min(range(len(bars)), key=lambda i: -out["per_bar_risk"][i]))
        out["worst"] = (w, out["per_bar_risk"][w], worst_bar_drivers(model, bars, [x["features"] for x in feats], w))
    return out


def show(slot, res, idx=0, detail=False):
    n = len(res["bars"])
    print(f"== {slot} block {idx + 1}: {n} bars | scheme {'PASS' if res['scheme_ok'] else 'FAIL'}"
          f" | form {len(res['form'])} | meaning {len(res['meaning_fails'])}"
          f" | coh {len(res['coh_fails'])}"
          + (f" | judge {res['risk']:.3f}" if res["risk"] is not None else ""))
    frame = res["frame"] or []
    for i, b in enumerate(res["bars"]):
        tgt = frame[i] if i < len(frame) else None
        got = res["syls"][i]
        flag = "" if tgt in (None, got) else f" ({'over' if got > tgt else 'under'} {abs(got - tgt)})"
        mark = "T" if i in res["tags"] else ("s" if i in res["soft"] else "|")
        r = f" {res['per_bar_risk'][i]:>5.2f}" if res["per_bar_risk"] else ""
        print(f"   {i + 1:>2} {got:>2}syl{flag:<9} {mark} {res['tails'][i]:<8}{r} | {b}")
    print(f"   families by final vowel: " + ", ".join(f"{k}->bars {v_}" for k, v_ in res["families"].items()))
    # The two readouts that measure the gaps in benchmark/gap_analysis.md directly: how rare the
    # rhyme-slot payoff words are, and how much of the world the block names. REPORT ONLY -- they
    # must never reject a bar, since Joe's own approved bars end bar 3 on the spoken tag "though".
    ends = [re.findall(r"[A-Za-z']+", b)[-1] for b in res["bars"] if re.findall(r"[A-Za-z']+", b)]
    zs = [z for z in (v.zipf(w) for w in ends) if z]
    if zs:
        print(f"   rhyme-slot payload: mean zipf {statistics.mean(zs):.2f} (rarer is lower; the "
              f"original's hook measures 4.04), rarest {min(zs):.2f}")
    props = [(i + 1, w) for i, b in enumerate(res["bars"])
             for w in re.findall(r"[A-Za-z']+", b)[1:] if w[0].isupper() and w.lower() != "i"]
    print(f"   world named: {len({i for i, _ in props})} of {len(res['bars'])} bars carry a proper noun"
          + (f" ({', '.join(w for _, w in props[:6])})" if props else "  <- nothing outside the room"))
    devs = [(r["bar"], k, t) for r in dv.inspect(res["bars"]) for k, t, _w in r["devices"]]
    print("   figures of speech: " + (", ".join(f"bar {b} {k}({t})" for b, k, t in devs) if devs else "NONE"))
    least = None
    for b in res["bars"]:
        for w in fn.score_bar(b)["words"]:
            if least is None or w["unexpected"] > least[1]:
                least = (w["word"], w["unexpected"])
    if least:
        print(f"   least obvious word choice: {least[0]} (unexpectedness {least[1]:.1f}/7)")
    for p in res["form"]:
        print(f"   x {str(p)[:150]}")
    if detail and "worst" in res:
        w, r, drivers = res["worst"]
        print(f"   weakest bar {w + 1} (risk {r:.2f}): " + ", ".join(f"{k} {v:+.2f}" for k, v in drivers))


def selftest():
    """Hermetic: no judge model, no disk cache, no subprocess."""
    ok = True
    text = "\ufeff# note\n1. Rain in Bergen, then the bar\n2) Whole coast in a week\n\nFifty kroner, happy days\n"
    blocks = parse_blocks(text)
    checks = [
        ("BOM comment skipped", blocks[0][0] == "Rain in Bergen, then the bar"),
        ("numbering stripped", blocks[0][1] == "Whole coast in a week"),
        ("blank line splits blocks", len(blocks) == 2),
        ("bar starting with a numeral survives", blocks[1] == ["Fifty kroner, happy days"]),
        ("families group by final vowel",
         family_groups(["ə-ɑː", "ɪ-ɑː", "ə-eɪ"]) == {"ɑː": [1, 2], "eɪ": [3]}),
        ("surname reads a tail", surname(["Rain in Bergen, then the bar"])[0].endswith("ɑː")),
    ]
    for name, good in checks:
        if not good:
            ok = False
            print(f"  FAIL {name}")
    cache = {}
    bs = ["Rain in Bergen, then the bar", "Skal from the in-laws, bizarre"]
    a = form_problems("Hook 9-16", bs, cache)
    b = form_problems("Hook 9-16", list(bs), cache)
    if a is not b:
        ok = False
        print("  FAIL memo cache did not reuse the list")
    print("TRYBARS SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot")
    ap.add_argument("path", nargs="?", default="-")
    ap.add_argument("--detail", action="store_true", help="per-bar drivers for the weakest bar")
    ap.add_argument("--top", type=int, default=0, help="only show the best N blocks")
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.slot:
        ap.error("--slot is required (or use --selftest)")

    text = sys.stdin.read() if a.path == "-" else open(a.path, encoding="utf-8-sig").read()
    text = text.lstrip("\ufeff")
    blocks = parse_blocks(text)
    if not blocks:
        print("no blocks found")
        return 1

    model = None if a.no_judge else __import__("judge").load_model()
    cache = _load_cache()
    results = [score_block(a.slot, blk, model=model, cache=cache) for blk in blocks]
    ranked = sorted(range(len(results)),
                    key=lambda i: (len(results[i]["form"]),
                                   results[i]["risk"] if results[i]["risk"] is not None else 9))

    print(f"{len(results)} block(s) for {a.slot}\n")
    for rank, i in enumerate(ranked[:a.top] if a.top else ranked):
        show(a.slot, results[i], idx=i, detail=a.detail and rank == 0)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
