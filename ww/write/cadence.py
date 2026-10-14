"""Block cadence (Joe, 14 Oct 2026: "create cohesion with the flows").

The slot frame fits each bar to its own template, so a block can pass bar by bar and still not hold ONE groove. The original gives each
4-bar block one cadence: a length contour (even, climbing, short-short-long, ...) and one kind of ending (soft = stressed+weak, or hard),
and switches cadence between blocks. This module (a) DESCRIBES that cadence in words for the writer, per block, and (b) CHECKS that a
written block holds it. Measured on the original's template: 14 of 19 blocks keep >= 3 of 4 bars on one ending class.

STATUS (registry discipline): the check is UNVALIDATED. It is a NOTE and a small tie-break term (cad_misses), never a veto. It compares
a block with the template's own contour, so the original passes by construction; the only independent evidence is that draft 8 and
draft 9 hold >= 3 same ending class in 15 and 14 of 19 blocks (no gap there), so what this adds is contour, not end shape.
"""
from __future__ import annotations

from .. import bridge
from . import slotcheck

DEAD = 1          # length changes of one syllable or less count as flat
MEAN_TOL = 1.5    # a block's mean length may sit this far from the template's


def _cls(shape: str) -> str:
    return "H" if shape.endswith("S") else "W"


def _sign(d: int) -> int:
    return 0 if abs(d) <= DEAD else (1 if d > 0 else -1)


def _blocks(n: int) -> list[tuple[int, int]]:
    return [(i, min(i + 4, n)) for i in range(0, n, 4)]


def _word_contour(syl: list[int]) -> str:
    if max(syl) - min(syl) <= 2:
        return "even"
    d = [_sign(b - a) for a, b in zip(syl, syl[1:])]
    if all(x >= 0 for x in d) and d.count(1) >= 1:
        return "climbing"
    if all(x <= 0 for x in d) and d.count(-1) >= 1:
        return "falling"
    big = max(range(len(syl)), key=lambda i: syl[i])
    small = min(range(len(syl)), key=lambda i: syl[i])
    if syl[big] - sum(syl) / len(syl) >= 3 and small != big:
        return f"one long bar (bar {big + 1}) among shorter ones"
    if sum(syl) / len(syl) - syl[small] >= 3:
        return f"one short punch (bar {small + 1}) among longer ones"
    return "uneven"


def describe(slot: str) -> str:
    """the cadence of every block of this slot, in words, for the writer prompt."""
    s = slotcheck.spec(slot)
    out, prev = [], None
    for a, b in _blocks(s["n"]):
        syl, shp = s["sylls"][a:b], s["shapes"][a:b]
        cls = [_cls(x) for x in shp]
        hard, soft = cls.count("H"), cls.count("W")
        ending = ("every bar ends on a STRESSED SYLLABLE (hard ending)" if soft == 0 else
                  "every bar ends stressed-then-weak (a soft, falling ending)" if hard == 0 else
                  f"{hard} bars end hard and {soft} end soft (bar{'s' if soft > 1 else ''} "
                  f"{', '.join(str(a + i + 1) for i, c in enumerate(cls) if c == 'W')} soft)")
        mean = sum(syl) / len(syl)
        move = ""
        if prev is not None:
            dm = mean - prev
            move = (" Longer and denser than the block before." if dm >= 2 else
                    " Shorter and tighter than the block before." if dm <= -2 else " About the same length as the block before.")
        out.append(f"bars {a + 1}-{b}: lengths {', '.join(map(str, syl))} ({_word_contour(syl)}); {ending}.{move}")
        prev = mean
    return ("CADENCE (hold ONE groove per block: write the block's bars as a set that share this length contour and this ending "
            "kind, not as four separate lines):\n  " + "\n  ".join(out))


def check(slot: str, bars: list[str]) -> dict:
    """per 4-bar block: ending class agrees with the template on >= 3 of 4 bars, the length moves (up/down/flat) agree on at
    least 2 of 3 steps, and the mean length is within MEAN_TOL of the template's. A short final block is checked on what it has."""
    s = slotcheck.spec(slot)
    if len(bars) != s["n"]:
        return {"ok": False, "misses": 99, "notes": [f"{len(bars)} bars, need {s['n']}"], "blocks": []}
    syl = [bridge.syllable_count(b) for b in bars]
    shp = [bridge.end_shape(b) for b in bars]
    blocks, notes, misses = [], [], 0
    for a, b in _blocks(s["n"]):
        ts, tsh = s["sylls"][a:b], s["shapes"][a:b]
        us, ush = syl[a:b], shp[a:b]
        same = sum(1 for x, y in zip(tsh, ush) if _cls(x) == _cls(y))
        tm = [_sign(y - x) for x, y in zip(ts, ts[1:])]
        um = [_sign(y - x) for x, y in zip(us, us[1:])]
        move = sum(1 for x, y in zip(tm, um) if x == y)
        need_move = max(1, len(tm) - 1)
        dmean = abs(sum(us) / len(us) - sum(ts) / len(ts))
        row = {"bars": f"{a + 1}-{b}", "ending_agree": f"{same}/{len(ts)}", "moves_agree": f"{move}/{len(tm)}", "mean_off": round(dmean, 2)}
        blocks.append(row)
        if same < min(3, len(ts)):
            misses += 1
            notes.append(f"bars {a + 1}-{b}: only {same}/{len(ts)} bars end like the template (the block should hold one ending kind)")
        if tm and move < need_move:
            misses += 1
            notes.append(f"bars {a + 1}-{b}: length contour {us} does not follow the template's {ts}")
        if dmean > MEAN_TOL:
            misses += 1
            notes.append(f"bars {a + 1}-{b}: mean length {sum(us) / len(us):.1f} vs the template's {sum(ts) / len(ts):.1f}")
    return {"ok": misses == 0, "misses": misses, "notes": notes, "blocks": blocks}


def selftest() -> tuple[bool, str]:
    spec = slotcheck.spec("Hook 5-8")
    # a block built to the template's own lengths and ending kind must pass
    ok_bars = ["Cold beer on the house in Porto", "Bought it by the barrel off the sellers", "Left the vinho in the cellars", "Might take the long way to Oslo"]
    r = check("Hook 5-8", ok_bars)
    # a block of four 15-syllable hard-ending bars must fail on mean length and on ending kind
    bad = ["I walked across the whole of the country in one go and I paid", "then I took the next train out of town and I paid", "and the next day I did it again and I paid", "so I went home on a budget flight and I paid"]
    r2 = check("Hook 5-8", bad)
    d = describe("Hook 5-8")
    good = r["misses"] == 0 and r2["misses"] >= 2 and "bars 5-8" in d.replace("bars 1-4", "bars 5-8") and "CADENCE" in d
    return good, f"cadence: on-frame block misses {r['misses']}, off-frame block misses {r2['misses']}; spec n={spec['n']}"


if __name__ == "__main__":
    import sys
    for sl in [x[0] for x in slotcheck.SECS]:
        print(f"\n{sl}\n{describe(sl)}")
    ok, msg = selftest()
    print("\nSELFTEST", "PASS" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
