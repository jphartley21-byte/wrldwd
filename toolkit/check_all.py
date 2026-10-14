"""check_all: every automated check for one slot (or the whole song) in one go, with one verdict.
  python toolkit/check_all.py --slot "V1 17-24" -      (stdin: our bars for that slot)
  python toolkit/check_all.py --song writing/full_draft_vN.md
Runs: match.py (by-ear rhyme scheme of the original, rhyme-strength map incl. slant and opening-to-end, bookends,
internal rhyme density, syllables, endings, multis/alliteration) + flow_fit.py (rhythm measured from the original
audio: exact line length, end rhyme landing on the original's step, strong/weak pattern, weak syllables on beats)
+ helpers freq (rare words for gate G2). A text stress-grid flag is waived automatically when the measured flow
passes that bar (the audio is the better witness). Meaning gates G1-G6 and the job check stay human: see /review.
"""
import os, subprocess, sys
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = {"Hook 1-4": 1, "Hook 5-8": 5, "Hook 9-16": 9, "V1 1-8": 17, "V1 9-16": 25, "V1 17-24": 33,
         "V1 25-32": 41, "V1 33-44": 49, "V2 1-8": 61, "V2 9-16": 69}
SIZES = {"Hook 1-4": 4, "Hook 5-8": 4, "Hook 9-16": 8, "V1 1-8": 8, "V1 9-16": 8, "V1 17-24": 8,
         "V1 25-32": 8, "V1 33-44": 12, "V2 1-8": 8, "V2 9-16": 8}


def run(args, text):
    return subprocess.run([sys.executable] + args, input=text, capture_output=True, text=True, encoding="utf8").stdout


def problems_of(slot, lines):
    """The raw form verdict: (ok, problems, waived, rare).

    Exposed because the pass/fail is not always the right thing to act on. check_all measures
    SIMILARITY TO THE ORIGINAL'S AUDIO-MEASURED RHYTHM, and Joe's own approved bars 1-4 fail it
    (bar 2 is 8 syllables vs the original's 9; stress grid and end shape miss). So a caller may
    legitimately want the PROBLEM COUNT as a ranking signal rather than a veto - that is what
    ml/generate.py does, and what the Definition of Done now says. See CLAUDE.md.
    """
    start = SLOTS[slot]
    text = "\n".join(l.replace("å", "a") for l in lines)
    m = run([os.path.join(HERE, "match.py"), "--slot", slot, "-"], text).splitlines()
    f = run([os.path.join(HERE, "flow_fit.py"), str(start), "-"], text).splitlines()
    r = run([os.path.join(HERE, "helpers.py"), "freq", "-"], text).splitlines()
    flow_fail = {int(l.split(".")[0]) for l in f if " FAIL |" in l}
    problems, waived = [], []
    for l in m:
        if "FAIL" not in l or l.startswith("VERDICT"):
            continue
        if l[:3].strip().rstrip(".").isdigit():
            bar = start + int(l.split(".")[0]) - 1
            only_stress = all(p.strip().startswith(("stress grid", "ending")) for p in l.split("FAIL:")[1].split("|")[0].split(";"))
            if only_stress and bar not in flow_fail:
                waived.append(f"bar {bar}: {l.split('FAIL:')[1].split('|')[0].strip()} (measured flow passes)")
                continue
        problems.append("form: " + l.strip()[:160])
    import json
    adv = {b["bar"] for b in json.load(open(os.path.join(HERE, "..", "benchmark", "flow_template.json")))["bars"] if b.get("advisory")}
    for l in f:
        if " FAIL |" in l:
            if int(l.split(".")[0]) in adv:
                waived.append(f"bar {l.split('.')[0].strip()}: flow advisory (the original fails its own template here)")
                problems.append("__adv__")
                continue
            problems.append("flow: " + l.strip()[:160])
        elif l.strip().startswith("FAIL:") and problems and problems[-1].startswith("flow:") and not problems[-1].endswith("__"):
            problems[-1] += " -> " + l.strip()[5:150]
    problems = [p for p in problems if p != "__adv__"]
    rare = [l.strip()[:120] for l in r if "RARE" in l]
    return (not problems), problems, waived, rare


def check(slot, lines, quiet=False):
    ok, problems, waived, rare = problems_of(slot, lines)
    if not quiet:
        start = SLOTS[slot]
        print(f"== {slot} (bars {start}-{start + len(lines) - 1}): {'ALL PASS' if ok else f'{len(problems)} PROBLEMS'}")
        for p in problems:
            print("  x", p)
        for w in waived:
            print("  ~ waived", w)
        for x in rare:
            print("  ? G2 rare word check:", x)
    return ok


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--score":
        # the RANKING form of the verdict: how many form problems, not pass/fail (see the DoD in
        # CLAUDE.md and ml/generate.py). Exit code 0 always - this is a measurement, not a gate.
        lines = [l.strip() for l in sys.stdin.read().splitlines() if l.strip() and not l.startswith(("[", "#", "("))]
        ok, problems, waived, rare = problems_of(a[1], lines)
        print(f"{a[1]}: {len(problems)} form problems ({len(waived)} waived), "
              f"{len(rare)} rare-word lines -> {'exact form' if ok else 'NOT exact form'}")
        sys.exit(0)
    if a and a[0] == "--slot":
        lines = [l.strip() for l in sys.stdin.read().splitlines() if l.strip() and not l.startswith(("[", "#", "("))]
        sys.exit(0 if check(a[1], lines) else 1)
    if a and a[0] == "--song":
        # "==" is the slot header this file writes for the project format; without it the header lines
        # were read as BARS, so every slot window was shifted by one and each slot was scored against
        # the wrong lines (it reported "== Hook 5-8" as a bar of 1 syllable and made bar 1 of Hook 5-8
        # "So I boarded a plane out to Bordeaux", which belongs to Hook 1-4). Found 13 Oct 2026, the
        # same defect ratchet.py had.
        ours = [l.strip() for l in open(a[1], encoding="utf8") if l.strip() and not l.startswith(("[", "#", "(", "=="))]
        i, allok = 0, True
        for slot, size in SIZES.items():
            allok &= check(slot, ours[i:i + size])
            i += size
        print("SONG:", "ALL PASS (now Joe's ear)" if allok else "NOT YET")
        sys.exit(0 if allok else 1)
    print(__doc__)
