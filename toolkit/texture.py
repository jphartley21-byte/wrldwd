"""texture: internal rhyme, sandwich rhymes and multisyllabic runs ACROSS WORDS, per section, against the ORIGINAL's same section (16 Oct 2026).

Why it exists. Joe: "Do we have gates for internal rhymes (amount and similarity between neighbours) and sandwich rhymes (same rhyme at
start and end of lines, or end of line and start of next line) and can multisyllabic rhymes be detected across words?" Measured: internal
rhyme was a soft target only (hard in 6 cell bars), the sandwich detector was in an unvalidated checker outside ww gate and did not tell
the two kinds apart, and multis were found only from the last content word of a line. Three measures, one unit (a section):

  internal   stressed syllables of CONTENT words before the end tail that share a vowel, inside a bar or between a bar and the next.
             amount   = how many such pairs (a word said again is a repeat, not a rhyme, and is skipped)
             strength = the same pairs graded by how close they are: 1.0 when the vowel AND the ending match (a rhyme), 0.5 when only
                        the vowel matches (assonance). This is the "similarity between neighbours".
  sandwich   frame: a bar's first content word rhymes with its own end (rapfit.score >= STRONG, different words)
             link:  a bar's end rhymes with the NEXT bar's first content word
  multi      a run of syllables, counted ACROSS word boundaries, in which at least two full / stressed syllables share their vowels in
             order with another run in the same bar or the next bar ("broke a leg" ~ "smoke a keg" is one run of three). Repeats of the
             same words are skipped. cross = runs that span two or more words on either side.

The gate: per section, ours must reach SLACK of the original's internal amount, internal strength and multis, and at least the
original's count of each sandwich kind (small counts, so no slack). The original passes by construction. Numbers only (rule 4):
benchmark/texture_par.json holds counts, never a word of the original.

  python toolkit/texture.py --build ORIG_LINES.txt     write benchmark/texture_par.json
  python toolkit/texture.py --selftest [ORIG]          fixtures fire; the original passes its own par
  python toolkit/texture.py FILE                        per-section report for a draft (no original text)
"""
import functools
import itertools
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PAR = os.path.join(ROOT, "benchmark", "texture_par.json")
SLACK = 0.8            # the same slack match.py's quad gates use for multis and internal bars; the original passes at any slack <= 1
STRONG = 0.80          # rapfit.STRONG: a pair score this high is a rhyme by ear (by-ear AUC 0.94 on the original's own scheme)
SANDWICH_HEAD = 3      # the first content word must be among a bar's first three words
LABEL = {"amount": "internal rhyme pairs", "strength": "internal rhyme strength (rhyme 1.0, assonance 0.5)",
         "frame": "frame sandwiches (a bar's first content word rhymes with its own end)",
         "link": "link sandwiches (a bar's end rhymes with the next bar's first content word)",
         "multi": "multisyllabic runs (2+ full syllables in order, across words)"}


def _ww():
    from ww import bridge
    bridge._pron_ready()


@functools.lru_cache(maxsize=None)
def toks(line):
    """[(word, syllables, is_content)] in order; hyphens split words and all-caps acronyms are said as letter names (flow_par.spell)."""
    _ww()
    import flow_par
    from ww.write import rapfit, rhymeview
    out = []
    for w in flow_par.spell(line).replace("-", " ").replace("—", " ").split():
        c = rhymeview.core(w)
        if c:
            out.append((c, rapfit._syl(c), c not in rhymeview.FUNC))
    return tuple(out)


def tail_at(line):
    from ww.write import rhymeview
    return rhymeview.tail_start([t[0] for t in toks(line)])


def end_text(line):
    ts = toks(line)
    return " ".join(t[0] for t in ts[tail_at(line):])


@functools.lru_cache(maxsize=None)
def _vs(a, b):
    from ww.write import rapfit
    return rapfit._phon().vsim(a, b)


def strength(x, y):
    """1.0 = same vowel and ending (a rhyme), 0.5 = same vowel only (assonance), 0 = different vowels."""
    from ww.write import rapfit
    if _vs(x[0], y[0]) < 0.99:
        return 0.0
    return 1.0 if rapfit._coda_sim_syl(x, y) >= 0.75 else 0.5


def _stressed(line):
    ts, t0 = toks(line), tail_at(line)
    return [(i, c, s) for i, (c, sy, content) in enumerate(ts[:t0]) if content for s in sy if s[1]]


def internal(bars):
    """{'within', 'neighbour', 'amount', 'strength', 'per_bar'}: stressed content syllables before the end tail sharing a vowel."""
    S = [_stressed(b) for b in bars]
    within = neigh = 0
    total = 0.0
    per_bar = []
    for i, s in enumerate(S):
        n_bar = 0
        for (wa, ca, a), (wb, cb, b) in itertools.combinations(s, 2):
            if wa != wb and _stem(ca) != _stem(cb):
                st = strength(a, b)
                if st:
                    within += 1
                    n_bar += 1
                    total += st
        if i + 1 < len(S):
            for (wa, ca, a) in s:
                for (wb, cb, b) in S[i + 1]:
                    if _stem(ca) != _stem(cb):
                        st = strength(a, b)
                        if st:
                            neigh += 1
                            n_bar += 1
                            total += st
        per_bar.append(n_bar)
    return {"within": within, "neighbour": neigh, "amount": within + neigh, "strength": round(total, 1), "per_bar": per_bar}


def head(line):
    """(word index, word) of the bar's first content word among its first SANDWICH_HEAD words, if it sits before the end tail."""
    ts, t0 = toks(line), tail_at(line)
    for i, (c, sy, content) in enumerate(ts[:SANDWICH_HEAD]):
        if content and sy:
            return (i, c) if i < t0 else None
    return None


@functools.lru_cache(maxsize=None)
def _rhymes(a, b):
    """a chain matched from the end that holds a full rhyme (vowel AND ending), and either 2+ syllables deep or a strong pair score. Fitted on
    the original's candidates (numbers only): the rhyming ones stand apart (1.0; 0.93 and 0.73 with a three-syllable chain) from the rest
    (0.76 and below with no chain, or a vowel-only chain)."""
    from ww.write import rapfit
    if not a or not b or a == b or a.split()[-1] == b.split()[-1]:
        return False
    c = rapfit.chain_best(rapfit._syl(a), rapfit._syl(b))
    if 2 not in c["states"] or not c["depth"]:
        return False                                     # no syllable matching in vowel AND ending: guy ~ pay (0.96 on the pair score) is a near vowel
    return c["depth"] >= 2 or rapfit.score(a, b)["score"] >= STRONG


def sandwiches(bars):
    """{'frame': [bar indices], 'link': [bar index i where bar i's end rhymes with bar i+1's head]} (0-based)."""
    H = [head(b) for b in bars]
    E = [end_text(b) for b in bars]
    frame = [i for i in range(len(bars)) if H[i] and _rhymes(H[i][1], E[i])]
    link = [i for i in range(len(bars) - 1) if H[i + 1] and _rhymes(E[i], H[i + 1][1])]
    return {"frame": frame, "link": link}


def _flat(line):
    """[(syllable, word index, word, content)] across the whole bar."""
    return [(s, i, c, content) for i, (c, sy, content) in enumerate(toks(line)) for s in sy]


def _match(x, y):
    from ww.write import rapfit
    wx, wy = x[0] in rapfit.WEAK and not x[1], y[0] in rapfit.WEAK and not y[1]
    if wx or wy:
        return wx and wy
    return _vs(x[0], y[0]) >= 0.99


def _stem(w):
    return re.sub(r"('s|s')$", "", w)


def _runs(A, B, same):
    """maximal runs A[a:a+L] ~ B[b:b+L] (B after A when same) with 2+ full syllables matched, a content stress on each side, other words."""
    from ww.write import rapfit
    out = []
    for a in range(len(A)):
        for b in range(len(B)):
            if same and b <= a:
                continue
            if a and b and (not same or b - 1 > a - 1) and _match(A[a - 1][0], B[b - 1][0]):
                continue                                 # not left-maximal: counted from an earlier start
            L = 0
            while a + L < len(A) and b + L < len(B) and (not same or a + L < b) and _match(A[a + L][0], B[b + L][0]):
                L += 1
            ra, rb = A[a:a + L], B[b:b + L]
            k = 0
            while k < L and not (rapfit.prominent(ra[k][0]) and rapfit.prominent(rb[k][0])):
                k += 1                                   # a run starts on a full syllable
            ra, rb = ra[k:], rb[k:]
            full = sum(1 for x, y in zip(ra, rb) if rapfit.prominent(x[0]) and rapfit.prominent(y[0]))
            if full < 2:
                continue
            if not (any(x[3] and x[0][1] for x in ra) and any(y[3] and y[0][1] for y in rb)):
                continue
            wa, wb = [x[2] for x in ra], [y[2] for y in rb]
            if wa == wb or (same and {x[1] for x in ra} & {y[1] for y in rb}):
                continue                                 # the same words again: a repeat, not a rhyme
            if {_stem(x[2]) for x in ra if x[3]} & {_stem(y[2]) for y in rb if y[3]}:
                continue                                 # a content word shared by both runs: a repeat
            out.append({"len": len(ra), "full": full, "cross": len({x[1] for x in ra}) > 1 or len({y[1] for y in rb}) > 1,
                        "a": " ".join(dict.fromkeys(wa)), "b": " ".join(dict.fromkeys(wb))})
    return out


def multis(bars):
    """{'n', 'cross', 'runs': [(bar, bar, run)]}: multisyllabic runs inside a bar and between neighbouring bars, across words."""
    F = [_flat(b) for b in bars]
    found = []
    for i in range(len(bars)):
        found += [(i, i, r) for r in _runs(F[i], F[i], True)]
        if i + 1 < len(bars):
            found += [(i, i + 1, r) for r in _runs(F[i], F[i + 1], False)]
    return {"n": len(found), "cross": sum(1 for f in found if f[2]["cross"]), "runs": found}


def profile(bars):
    it, sw, mu = internal(bars), sandwiches(bars), multis(bars)
    return {"amount": it["amount"], "strength": it["strength"], "within": it["within"], "neighbour": it["neighbour"],
            "frame": len(sw["frame"]), "link": len(sw["link"]), "multi": mu["n"], "multi_cross": mu["cross"]}


@functools.lru_cache(maxsize=1)
def par_table():
    try:
        return json.load(open(PAR, encoding="utf-8"))["sections"]
    except OSError:
        return None


def check(slot, bars, par=None):
    """[(measure, ours, need)] where the section falls short of the original's same section; [] passes; None = no par."""
    par = par or (par_table() or {}).get(slot)
    if not par:
        return None
    p = profile(bars)
    out = []
    for m in ("amount", "strength", "multi"):
        need = round(SLACK * par[m], 1)
        if p[m] < need:
            out.append((m, p[m], need))
    for m in ("frame", "link"):
        if p[m] < par[m]:
            out.append((m, p[m], par[m]))
    return out


def describe(fails):
    return "; ".join(f"{LABEL[m]} {o}, need >= {n} (the original's section x {SLACK if m in ('amount', 'strength', 'multi') else 1})" for m, o, n in fails)


def build(orig_path):
    from ww.write import slotcheck
    L = [l.strip() for l in open(orig_path, encoding="utf8") if l.strip()][:76]
    secs = {name: profile(L[s:e]) for name, s, e in slotcheck.SECS}
    json.dump({"_note": "Per-section rhyme texture of the ORIGINAL (counts only, rule 4), built by toolkit/texture.py --build.",
               "slack": SLACK, "sections": secs}, open(PAR, "w", encoding="utf-8"), indent=1)
    par_table.cache_clear()
    return secs


FIXTURES = {
    # assistant-written lines, not lyrics: each measure must fire where the device is and stay quiet where it is not
    "multi_cross": (["I broke a leg then I smoke a keg", "Plain words and nothing else at all"], 1),
    "frame": (["Cable on the roof and the TV's stable", "Nothing here to say at all"], 1),
    "link": (["Down at the docks I paid the fee", "Free as a bird I drove away"], 1),
    "flat": (["Down at the docks I paid the man", "Out on the road we drove away"], 0),
}


def selftest(orig_path=None):
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(("ok  " if cond else "BAD ") + name + (f": {detail}" if detail and not cond else ""))

    m = multis(FIXTURES["multi_cross"][0])
    chk("a multisyllabic run across words is found (broke a leg ~ smoke a keg)", m["cross"] >= 1, str(m["runs"]))
    chk("a frame sandwich is found (cable ... stable)", sandwiches(FIXTURES["frame"][0])["frame"] == [0], str(sandwiches(FIXTURES["frame"][0])))
    chk("a link sandwich is found (fee / free)", sandwiches(FIXTURES["link"][0])["link"] == [0], str(sandwiches(FIXTURES["link"][0])))
    f = profile(FIXTURES["flat"][0])
    chk("flat bars carry no sandwich and no multi", f["frame"] == f["link"] == f["multi"] == 0, str(f))
    chk("a repeated word is a repeat, not an internal rhyme", internal(["Cash for cash and cash for cash today"])["amount"] == 0)
    if par_table() is None:
        chk("benchmark/texture_par.json exists (run --build ORIG)", False)
    elif orig_path:
        from ww.write import slotcheck
        L = [l.strip() for l in open(orig_path, encoding="utf8") if l.strip()][:76]
        bad = [name for name, s, e in slotcheck.SECS if check(name, L[s:e])]
        chk("the original passes its own texture par in every section", not bad, str(bad))
    print("texture selftest:", "PASSED" if ok else "FAILED")
    return ok


def report(path):
    from ww.write import rhymeview, slotcheck
    d = rhymeview.load_draft(path)
    tab = par_table() or {}
    bad = 0
    for name, s, e in slotcheck.SECS:
        bars = d.get(name)
        if not bars:
            continue
        p, par = profile(bars), tab.get(name, {})
        f = check(name, bars) or []
        bad += bool(f)
        print(f"{name:10s} " + "  ".join(f"{k} {p[k]}/{par.get(k, '?')}" for k in ("amount", "strength", "frame", "link", "multi")) +
              f"  cross {p['multi_cross']}  " + ("PASS" if not f else "FAIL: " + describe(f)))
    return bad


def main():
    a = sys.argv[1:]
    if a and a[0] == "--build":
        secs = build(a[1])
        print(f"wrote {os.path.relpath(PAR, ROOT)} ({len(secs)} sections, counts only)")
        return 0
    if not a or a[0] == "--selftest":
        return 0 if selftest(a[1] if len(a) > 1 else os.environ.get("WW_PRIVATE_ORIGINAL")) else 1
    return 1 if report(a[0]) else 0


if __name__ == "__main__":
    sys.exit(main())
