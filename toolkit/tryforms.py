"""tryforms: enumerate EVERY block the writer's pools allow, prescreen cheap, then score the shortlist.

This exists because of a real failure: bars 5-8 were "finished" after about a dozen hand-written
candidate lines, which is sampling, not searching. With the supply finally queryable (bank.py) and
trybars able to score a block in half a second warm, the space is small enough to enumerate.

  python toolkit/tryforms.py --slot "Hook 5-8" POOLS_FILE [--top 8] [--keep 40]
  python toolkit/tryforms.py --selftest

POOLS_FILE format: the candidate lines for bar 1, then a line of "---", then bar 2's candidates,
and so on. Every combination is generated; the cartesian product IS the search space.

Two stages, because they cost different amounts:
  * prescreen, in-process and ~1 ms per block: syllable distance to the frame, whether the bars the
    scheme says must rhyme actually do (mt.best_end), the meaning gate, end-word rarity (the payload
    metric from benchmark/gap_analysis.md) and how much of the world the block names.
  * full score, only for the shortlist: trybars.score_block, which runs check_all (3 subprocesses).
The judge is deliberately NOT used to rank: it agrees with Joe 2/5 and is inverted on 3 of those.
"""
import argparse
import itertools
import os
import re
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import forge                 # noqa: E402
import craft_scan as cs      # noqa: E402
import flow_fit as ff        # noqa: E402
import meaning_gate as mg    # noqa: E402
import match as mt           # noqa: E402
import rhyme_tools as rt     # noqa: E402
import trybars as tb         # noqa: E402
import vocab as v            # noqa: E402

# The scheme check's threshold. match.py's own strong-rhyme line; below this the pair is a slant.
RHYME_FLOOR = 0.78


def parse_pools(text):
    """[[bar 1 candidates], [bar 2 candidates], ...] split on lines of ---."""
    pools, cur = [], []
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip() == "---":
            if cur:
                pools.append(cur)
            cur = []
            continue
        if line.strip() and not line.lstrip().startswith("#"):
            cur.append(line.strip())
    if cur:
        pools.append(cur)
    return pools


def rhyme_groups(scheme):
    """{letter: [positions]} from a scheme like ABBA -> {'A': [0, 3], 'B': [1, 2]}."""
    g = defaultdict(list)
    for i, ch in enumerate(scheme.strip().upper()):
        if ch.isalpha():
            g[ch].append(i)
    return dict(g)


def scheme_ok(bars, scheme, floor=RHYME_FLOOR):
    """True if every pair the scheme says must rhyme does, at >= floor.

    The scheme is one letter per bar ("ABBA" for four bars). A scheme whose length does not match
    the bar count is treated as no constraint and returns True, so the selftest asserts that case
    explicitly -- a silent pass is exactly how an off-by-one check disables itself.
    """
    if len(scheme.strip()) != len(bars):
        return True
    for letter, idx in rhyme_groups(scheme).items():
        for a, b in itertools.combinations(idx, 2):
            if a >= len(bars) or b >= len(bars):
                return False
            if (mt.best_end(bars[a], bars[b]) or 0) < floor:
                return False
    return True


def end_words(bars):
    out = []
    for b in bars:
        w = re.findall(r"[A-Za-z']+", b)
        out.append(w[-1] if w else "")
    return out


def payload(bars):
    """Mean zipf of the rhyme-slot words. Lower is rarer, which is the gap we are closing."""
    z = [x for x in (v.zipf(w) for w in end_words(bars)) if x]
    return statistics.mean(z) if z else 9.9


def places(bars):
    """Bars carrying a proper noun, excluding the pronoun I."""
    n = 0
    for b in bars:
        ws = re.findall(r"[A-Za-z']+", b)[1:]
        if any(w[0].isupper() and w.lower() != "i" for w in ws):
            n += 1
    return n


def loanword_hits(bars, words):
    n = 0
    for b in bars:
        low = b.lower()
        if any(w in low for w in words):
            n += 1
    return n


def prescreen(slot, pools, frame, loanwords=()):
    """Every combination, ranked by the cheap measures. Returns a list of dicts, best first."""
    syls = frame.get("syls") or []
    scheme = frame.get("scheme") or ""
    out = []
    for combo in itertools.product(*pools):
        bars = list(combo)
        # MUST be the same counter the verdict uses (flow_fit.sylls via trybars.score_block).
        # The first version of this tool counted with craft_scan.nuclei, so the prescreen ranked on a
        # number the verdict never looked at and both blocks were swept along the wrong axis.
        got = [len(ff.sylls(b)) for b in bars]
        dist = sum(abs(g - t) for g, t in zip(got, syls) if t)
        m = mg.audit(bars, slot)
        out.append({"bars": bars, "syl": got, "syl_dist": dist,
                    "meaning": len(m["fails"]), "scheme_ok": scheme_ok(bars, scheme) if scheme else True,
                    "payload": payload(bars), "world": places(bars),
                    "loan": loanword_hits(bars, loanwords)})
    out.sort(key=lambda r: (r["meaning"], 0 if r["scheme_ok"] else 1, r["syl_dist"], r["payload"]))
    return out


_NUC = {}


def _nuclei(text):
    if text not in _NUC:
        _NUC[text] = cs.nuclei(text)
    return _NUC[text]


def full_score(slot, cand, cache=None):
    r = tb.score_block(slot, cand["bars"], model=None, cache=cache)
    cand["syl"] = r["syls"]          # the authoritative count, not the prescreen's
    cand["form"] = len(r["form"])
    cand["meaning"] = len(r["meaning_fails"])
    cand["coh"] = len(r["coh_fails"])
    cand["scheme_pass"] = bool(r["scheme_ok"])
    return cand


def report(scored, top=8):
    scored.sort(key=lambda r: (r["meaning"], 0 if r["scheme_pass"] else 1, r["form"], r["payload"]))
    print(f"{len(scored)} block(s) fully scored; best by (meaning, scheme, form, payload):\n")
    print("READ EVERY LINE BELOW BEFORE USING IT. Nothing in this tool reads for sense: it can and")
    print("does rank word-salad top (see the 12 Oct 2026 case: 'A page of the orders and the")
    print("corners' won a 6,480-combination sweep). Meaning is the writer's job, and the only")
    print("instrument that has ever caught nonsense here is Joe's ear.\n")
    for i, r in enumerate(scored[:top], 1):
        print(f"{i}. scheme {'PASS' if r['scheme_pass'] else 'FAIL'} | form {r['form']} | "
              f"meaning {r['meaning']} | coh {r['coh']} | syl {r['syl']} (off {r['syl_dist']}) | "
              f"payload {r['payload']:.2f} | world {r['world']} | loanwords {r['loan']}")
        for b in r["bars"]:
            print("     " + b)
    return scored[:top]


def run(slot, pools_file, top=8, keep=40, cache=None):
    frame = forge.slot_frame(slot)
    with open(pools_file, encoding="utf-8-sig") as fh:
        pools = parse_pools(fh.read())
    if not frame.get("n"):
        print(f"unknown slot {slot}")
        return []
    if len(pools) != frame["n"]:
        print(f"pool count {len(pools)} does not match the slot's {frame['n']} bars")
        return []
    words = ()
    try:
        import bank
        words = tuple(r["word"].lower() for r in bank.loanwords_for(limit=999))
    except Exception:
        pass
    total = 1
    for p in pools:
        total *= len(p)
    print(f"{total} combination(s) from pools of " + ", ".join(str(len(p)) for p in pools))
    cands = prescreen(slot, pools, frame, words)
    print(f"prescreened; scoring the top {keep}\n")
    scored = [full_score(slot, c, cache) for c in cands[:keep]]
    return report(scored, top)


def selftest():
    """Offline: pool parsing, scheme groups, the scheme test and the world counter."""
    ok = True
    pools = parse_pools("# note\nBom dia the boat to Porto\n---\norders here\n# skip\nborders here\n---\nend")
    checks = [
        ("pools split on ---", [len(p) for p in pools] == [1, 2, 1]),
        ("comments are skipped", all(not l.startswith("#") for p in pools for l in p)),
        ("scheme groups", rhyme_groups("ABBA") == {"A": [0, 3], "B": [1, 2]}),
        ("scheme_ok true on a real rhyme", scheme_ok(["a page of the orders", "down on the borders"],
                                                    "AA", floor=0.5)),
        ("scheme_ok false when the ends do not rhyme",
         not scheme_ok(["a boat to Porto", "the price of the weight"], "AA", floor=0.9)),
        ("a scheme of the wrong length checks nothing (and that is asserted, not silent)",
         scheme_ok(["a boat to Porto", "the price of the weight"], "A", floor=0.9)),
        ("world counts a place", places(["a boat to Porto", "nothing here"]) == 1),
        ("world ignores the pronoun I", places(["nothing here at all", "I did that"]) == 0),
        ("payload is finite", payload(["a boat to Porto"]) < 9.9),
    ]
    for name, good in checks:
        if not good:
            ok = False
            print(f"  FAIL {name}")
    print("TRYFORMS SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot")
    ap.add_argument("pools", nargs="?")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--keep", type=int, default=40)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.slot and a.pools):
        ap.print_help()
        return 0
    run(a.slot, a.pools, a.top, a.keep, cache=tb._load_cache())
    return 0


if __name__ == "__main__":
    sys.exit(main())
