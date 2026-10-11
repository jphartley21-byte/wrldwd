"""compare: what changed between two drafts, against the original's shape. ADVISORY ONLY, never blocks (exit 0).
  python toolkit/compare.py OLD_DRAFT NEW_DRAFT
Reports: sections that now match / differ more from the original; keeper phrases and places that disappeared (so you can
choose whether that was deliberate); Joe-locked lines that changed. Joe's ear decides which direction is better.
"""
import io, json, os, sys, contextlib
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_all  # noqa: E402


def lines_of(path):
    return [l.strip() for l in open(path, encoding="utf8") if l.strip() and not l.startswith(("[", "#", "("))]


def section_status(lines):
    out, i = {}, 0
    for slot, size in check_all.SIZES.items():
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = check_all.check(slot, lines[i:i + size])
        out[slot] = (ok, sum(1 for l in buf.getvalue().splitlines() if l.strip().startswith("x ")))
        i += size
    return out


def keepers_report(text, K):
    t = text.lower()
    return [p for p in K["phrases"] + K["places"] if p.lower() not in t]


if __name__ == "__main__":
    old, new = sys.argv[1], sys.argv[2]
    K = json.load(open(os.path.join(HERE, "keepers.json"), encoding="utf8"))
    lo, ln = lines_of(old), lines_of(new)
    so, sn = section_status(lo), section_status(ln)
    bad = []
    for slot in so:
        (ok_o, n_o), (ok_n, n_n) = so[slot], sn[slot]
        if ok_o and not ok_n:
            bad.append(f"{slot}: matched the original before, differs now")
        elif n_n > n_o:
            bad.append(f"{slot}: differences from the original rose {n_o} -> {n_n}")
    lost = [k for k in keepers_report(open(new, encoding="utf8").read(), K) if k not in keepers_report(open(old, encoding="utf8").read(), K)]
    if lost:
        bad.append("keepers lost: " + ", ".join(lost))
    for l in K["locked_lines"]:
        if l not in ln:
            bad.append(f"locked line changed: {l}")
    gained = [s for s in so if not so[s][0] and sn[s][0]]
    print("now match the original:", gained or "nothing new")
    print("NOTES:", "nothing flagged" if not bad else " | ".join(bad))
    if bad:
        print("(Notes are for information. Keep the change if Joe prefers it.)")
    missing_now = keepers_report(open(new, encoding="utf8").read(), K)
    if missing_now:
        print("keepers not in the new draft (fine if deliberate):", ", ".join(missing_now))
    sys.exit(0)
