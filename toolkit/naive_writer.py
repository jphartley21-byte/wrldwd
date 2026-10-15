"""naive_writer: are the gates LOCKED IN, or do they only work for a writer who chooses to run them? (15 Oct 2026)

Joe: "Are these gates locked in so a naive writer would produce the same flow?" A naive writer does not read the rules; it
writes a bar and saves the file. This test plays that writer: it swaps each of Joe's flagged bars (toolkit/tests/flow_flagged.txt)
into its own position in a carrier draft (toolkit/tests/naive_carrier.md, frozen, NOT approved) and asserts every path a
draft can take to "done" rejects it:
  fitbar          the per-bar fit a writer uses while fitting (`fitbar.py bars`; its untimed branch once skipped the par)
  slotcheck       a hard issue names the swapped bar
  ww gate         FAIL (the single verdict: definition of done, the save hook)
  songcheck       its slotcheck gate fails the song
  ratchet         slotcheck hard issues rise against the carrier -> REVERT (only where the carrier's bar was clean)
  draft_all.take  refuses the swapped section over the carrier (same frame_hard measure; plan, syllables and cashing held equal)
and that a gate switched off by an environment flag is announced as GATE OFF, never a quiet pass. Joe's block-level RHYME complaints
(toolkit/tests/rhyme_complaints.txt) are swapped in as whole sections the same way.

What it does NOT show: that a writer who passes every gate writes the original's flow. The gates bound the flow (no worse than
the original's bar on each measure); they do not fix the stress pattern position by position.
  python toolkit/naive_writer.py          (exit 0 = PASSED)
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CARRIER = os.path.join(HERE, "tests", "naive_carrier.md")
START = {"Hook 1-4": 1, "Hook 5-8": 5, "Hook 9-16": 9, "V1 25-32": 41}
SIZE = {"Hook 1-4": 4, "Hook 5-8": 4, "Hook 9-16": 8, "V1 25-32": 8}


def _slot_of(bar_no):
    for s, a in START.items():
        if a <= bar_no < a + SIZE[s]:
            return s, bar_no - a
    return None, None


def _swap(text, slot, k, line):
    out, cur, i = [], None, 0
    for l in text.splitlines():
        if l.startswith("=="):
            cur, i = l[2:].strip(), 0
        elif cur == slot and l.strip() and not l.startswith(("#", "[", "(")):
            if i == k:
                l = line
            i += 1
        out.append(l)
    return "\n".join(out) + "\n"


def _swap_block(text, slot, bars):
    """replace a whole section's bars and #cash lines with `bars` (a block-level rhyme complaint has no single bar to swap)."""
    out, cur, done = [], None, False
    for l in text.splitlines():
        if l.startswith("=="):
            cur = l[2:].strip()
            out.append(l)
            if cur == slot:
                out += bars
                done = True
            continue
        if cur == slot and l.strip() and not l.startswith(("[", "(")) and (not l.startswith("#") or l.startswith("#cash")):
            continue
        out.append(l)
    assert done, slot
    return "\n".join(out) + "\n"


def block_cases(text, base, tmp):
    """Joe's rhyme complaints (toolkit/tests/rhyme_complaints.txt) for the carrier's sections: the whole block swapped in must be
    rejected by slotcheck with the named rhyme rule, by ww gate and by songcheck; by the ratchet and take() too where the carrier's
    own section does not already fail that rule (they compare counts)."""
    import fitbar
    from ww.write import slotcheck, gate, draft_all
    import songcheck
    import ratchet
    ok = True
    rows = [l.split("\t") for l in open(os.path.join(HERE, "tests", "rhyme_complaints.txt"), encoding="utf-8").read().splitlines()
            if l.strip() and not l.startswith("#")]
    for slot, rules, bars in ((r[0], r[1], r[2]) for r in rows if r[0] in START):
        p = os.path.join(tmp, f"block_{slot.replace(' ', '_')}.md")
        open(p, "w", encoding="utf-8").write(_swap_block(text, slot, [b.strip() for b in bars.split(" / ")]))
        D2, C2 = fitbar.read_draft(p, with_cash=True)
        hard = slotcheck.check(slot, D2[slot], cash=C2.get(slot) or [])["hard"]
        for rule in rules.split(","):
            tag = f"rhyme: {rule.strip()}:"
            g = gate.run(p)
            fails = []
            songcheck.slot_gates(p, fails, [])
            paths = {"slotcheck": any(h.startswith(tag) for h in hard), "ww gate": not g["ok"], "songcheck": bool(fails)}
            clean = not any(h.startswith(tag) for h in base[slot])
            if clean:
                paths["ratchet"] = ratchet.slot_hard(p)[slot] > len(base[slot])
                inc = {"usable": True, "plan_ok": True, "frame_hard": len(base[slot]), "syl_miss": 0, "cashed": 1}
                paths["take"] = not draft_all.take(dict(inc, frame_hard=len(hard)), inc)
            good = all(paths.values())
            ok &= good
            print(("ok  " if good else "BAD ") + f"{slot} block (Joe's rhyme complaint, rule '{rule.strip()}') rejected by: " +
                  ", ".join(n for n, v in paths.items() if v) + ("" if good else "; NOT by: " + ", ".join(n for n, v in paths.items() if not v)) +
                  ("" if clean else " (the carrier's own block already fails this rule: only the gate verdict applies)"))
    return ok


def selftest():
    import fitbar
    fitbar.use_ww()
    from ww.write import slotcheck, gate, draft_all
    import songcheck
    import ratchet
    import flow_par
    text = open(CARRIER, encoding="utf-8").read()
    D, C = fitbar.read_draft(CARRIER, with_cash=True)
    base = {s: slotcheck.check(s, D[s], cash=C.get(s) or [])["hard"] for s in D}
    ok = True
    tmp = tempfile.mkdtemp(prefix="naive_")
    for b, line, _ in flow_par.flagged():
        slot, k = _slot_of(b)
        if slot is None:
            print(f"BAD  bar {b}: no carrier section holds it (extend toolkit/tests/naive_carrier.md)")
            ok = False
            continue
        p = os.path.join(tmp, f"bar{b}.md")
        open(p, "w", encoding="utf-8").write(_swap(text, slot, k, line))
        D2, C2 = fitbar.read_draft(p, with_cash=True)
        hard = slotcheck.check(slot, D2[slot], cash=C2.get(slot) or [])["hard"]
        named = [h for h in hard if h.startswith(f"bar {k + 1}:")]
        g = gate.run(p)
        fails = []
        songcheck.slot_gates(p, fails, [])
        clean = not any(h.startswith(f"bar {k + 1}:") for h in base[slot])
        rise = ratchet.slot_hard(p)[slot] > len(base[slot])
        inc = {"usable": True, "plan_ok": True, "frame_hard": len(base[slot]), "syl_miss": 0, "cashed": 1}
        took = draft_all.take(dict(inc, frame_hard=len(hard)), inc)
        paths = {"fitbar": fitbar.try_bar(b, line)[0] is False, "slotcheck": bool(named), "ww gate": not g["ok"],
                 "songcheck": bool(fails)}
        if clean:
            paths["ratchet"] = rise
            paths["take"] = not took
        good = all(paths.values())
        ok &= good
        print(("ok  " if good else "BAD ") + f"bar {b} ({slot} bar {k + 1}) rejected by: " +
              ", ".join(n for n, v in paths.items() if v) +
              ("" if good else "; NOT by: " + ", ".join(n for n, v in paths.items() if not v)) +
              ("" if clean else " (carrier's bar already fails here: ratchet/take compare counts, so only the gate verdict applies)") +
              (f" | {named[0][:110]}" if named else ""))
    ok &= block_cases(text, base, tmp)
    saved = os.environ.get("WW_RAPFIT_GATE")
    os.environ["WW_RAPFIT_GATE"] = "0"
    try:
        off = gate.gates_off()
        rep = gate.report(gate.run(CARRIER), quiet=True)
    finally:
        if saved is None:
            os.environ.pop("WW_RAPFIT_GATE", None)
        else:
            os.environ["WW_RAPFIT_GATE"] = saved
    good = any("WW_RAPFIT_GATE" in x for x in off) and rep.startswith("GATE OFF") and "gate(s) OFF" in rep
    ok &= good
    print(("ok  " if good else "BAD ") + "a gate switched off by an environment flag is announced as GATE OFF in the verdict")
    print("NAIVE WRITER:", "PASSED" if ok else "FAILED")
    return ok


if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)
