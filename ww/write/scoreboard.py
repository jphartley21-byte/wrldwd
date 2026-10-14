"""Scoreboard: one table, draft vs the original, level by level (Joe, 14 Oct 2026: "check the flow, rhymes and quality against the original, see what's missing").

  python -m ww.write.scoreboard DRAFT [--duel]

Every row is a NUMBER against the original's own value or against zero (the original passes every gate it is held to). The duel row is the blind LLM comparison
(private calibration client; numbers only). Nothing here quotes the original.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import Counter

from .. import bridge, config
from . import cadence, evolve, rapfit, sensecheck, slotcheck


def _run(cmd: list[str]) -> str:
    p = subprocess.run([sys.executable, "-X", "utf8"] + cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(config.ROOT))
    return (p.stdout or "") + (p.stderr or "")


def board(path: str, duel: bool = False) -> str:
    os.environ["WW_SENSE"] = "0"                       # sense is its own row
    draft = evolve.parse_draft(path)
    rows = []
    # 1 SENSE
    nb = nbl = 0
    for name, bars in draft.items():
        r = sensecheck.check(bars)
        nb += len(r["fails"])
        if len(bars) >= 3 and not sensecheck.block_check(bars)["ok"]:
            nbl += 1
    rows.append(("1 sense: bars that are not sentences", nb, 0))
    rows.append(("1 sense: blocks without one thread", nbl, 0))
    # 2 FRAME (syllables +-1, ending kinds, scheme pairs) per quad
    c = Counter()
    for u in evolve.units():
        for k, _, _ in evolve.check_free(u, evolve.quad_bars(draft, u)):
            c[k] += 1
    rows.append(("2 frame: bars off their syllable count (+-1)", c["syl"], 0))
    rows.append(("2 frame: bars with the wrong ending kind", c["shape"], 0))
    rows.append(("3 rhyme: required pairs that do not rhyme on a stressed syllable", c["rhyme"], 0))
    rows.append(("3 rhyme: repeated end words inside a quad", c["endword"], 0))
    # 3 stress-anchor / depth per slot
    hard = 0
    for name, bars in draft.items():
        try:
            hard += len(rapfit.check_block(name, bars)["hard"])
        except Exception:  # noqa: BLE001
            pass
    rows.append(("3 rhyme: stress-anchor / 3-syllable block failures", hard, 0))
    # 4 FLOW cadence
    cm = sum(cadence.check(n, b)["misses"] for n, b in draft.items() if len(b) == slotcheck.spec(n)["n"])
    rows.append(("4 flow: cadence misses (length contour / ending kind per block)", cm, 0))
    # 5 DEVICES + SONG LEVEL (the toolkit's own song gates, which are calibrated on the original)
    sc = _run(["toolkit/songcheck.py", path])
    m = re.search(r"SONGCHECK: (\d+) PROBLEMS", sc)
    rows.append(("5 song: songcheck problems (devices, places, local words, repeats)", int(m.group(1)) if m else -1, 0))
    pa = _run(["toolkit/phrase_audit.py", path])
    m = re.search(r"PHRASE AUDIT: (\d+) PROBLEMS", pa)
    rows.append(("5 song: repeated openers / phrases / duplicate lines / comma flood", int(m.group(1)) if m else 0, 0))
    ie = [rapfit.internal_echo(b)["score"] for b in draft.values() if len(b) >= 4]
    rows.append(("5 sound: mean internal-echo score (original is about 0.42)", round(sum(ie) / max(1, len(ie)), 2), 0.42))
    out = [f"SCOREBOARD for {path}", f"{'level / measure':<78}{'ours':>8}{'original':>10}"]
    for name, ours, orig in rows:
        out.append(f"{name:<78}{ours!s:>8}{orig!s:>10}")
    if duel:
        m_ = evolve.measure(path)
        out.append(f"{'7 quality: blind duels won vs the original (both orders; tie = 0.5)':<78}{m_['duel']!s:>8}{(m_['of'] / 2)!s:>10}   of {m_['of']}")
        out.append("   losing quads: " + ", ".join(f"q{r['q']}({r['slot']})" for r in m_["rows"] if r["duel"] < 1.0))
    return "\n".join(out)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    print(board(sys.argv[1], duel="--duel" in sys.argv))
