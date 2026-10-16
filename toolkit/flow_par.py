"""flow_par: a bar's flow must be no worse than the ORIGINAL'S OWN BAR in the same position (15 Oct 2026).

Why it exists. Joe: "how did this bar get through the gates without being fixed already". Four bars he heard as flowing
badly (toolkit/tests/flow_flagged.txt) passed every gate, because:
  - hard mouth-shape joins were allowed per BLOCK (2 bars in 8), so a bad bar hid inside the allowance;
  - stress clashes fired only as notes;
  - runs of short closed vowels and a clause restarting mid-bar were not measured at all.
This gate compares each bar with the same bar of the original, measure by measure, using instruments the repo already has:
  stress_run   longest run of stressed syllables (flow_fit.sylls, the template's own stress model)
  hard_joins   word joins scoring >= 2 (ww/write/earcheck.word_joins: 3+ consonant clusters, h after a cluster, hiss into hiss)
  closed_run   longest run of syllables on a short closed vowel (ɪ ʊ) (ww/write/rapfit._syl): the mouth never opens
  restart      a subject pronoun straight after a content word, with no conjunction (spaCy): the sentence restarts mid-bar

Honest status: the original passes by construction (each bar is its own par). The evidence that it measures what Joe
hears is the four flagged bars, all caught. There is no independent set of bars Joe has called good, so a tolerance is
loosened only when a measure fails a bar Joe calls good.

The original's per-bar values are stored as NUMBERS ONLY in benchmark/flow_par.json (rule 4: no original text).
  python toolkit/flow_par.py --build ORIG_LINES.txt     write benchmark/flow_par.json
  python toolkit/flow_par.py BAR "text"                 profile one bar against the original's bar
  python toolkit/flow_par.py --selftest                 the flagged bars fail; the stored par matches the measure
"""
import functools
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

import flow_fit as ff   # noqa: E402

PAR = os.path.join(ROOT, "benchmark", "flow_par.json")
FLAGGED = os.path.join(HERE, "tests", "flow_flagged.txt")
OK = os.path.join(HERE, "tests", "flow_ok.txt")
MEASURES = ("stress_run", "hard_joins", "closed_run", "restart")
# BAR-BOUND measures (15 Oct 2026, Joe on Hook 9-16 bars 13-14: "How is [Amsterdam or Koh Tao or Spain or Cairns or Wales / Prost and
# then you buy] the same flow as" the original's bars 13-14). The four measures above passed it; it differs in two ways they cannot see:
#   fast_jam   stressed syllables back to back on adjacent 16th steps of the original's own audio template for this bar ("Koh Tao" lands on
#              steps 7-8 where the original runs two weak syllables into a hit). The stress-run tolerance (+1) hid it, so TOL here is 0.
#   cell       where the original's bar repeats one cell (a content word said again in the bar, or an in-bar drum / echo: toolkit/ear.py),
#              ours must too, with internal rhyme (match.internal_density, single bar) no more than one below the original's bar. The
#              original does this in 5 bars (13, 24, 40, 48, 50); everywhere else the rule is silent.
#   barline    (15 Oct 2026, Joe: "In the original lyrics these look like long bars but if you look closely there are end rhymes in the
#              middle, so it's actually delivered over 8 bars ... See how we have end rhymes that don't rhyme?") 35 of the original's 74
#              timed lines run past one musical bar (audio steps >= 16). Where the original lands a rhyme on its OWN end at the bar line
#              (a content word whose stressed syllable sits on steps 11-20, with the same vowels from the stress to the end as the line's
#              end word: bars 41, 42, 50), ours must land one within a syllable of the same position. A line re-cut into two bars would
#              re-index every audio template, scheme letter and par table, so the bar-line rhyme is gated in place instead.
#              It must also be as CLOSE as the original's (Joe: "Turkey and certi is same closeness as stranger and Naples?"): vowels alone
#              let stranger / Naples (rapfit 0.69) stand in for Turkey / certi (0.81). Ours needs rapfit.score >= the original's - BAR_SLACK.
#   pause      (16 Oct 2026, Joe on bar 76: "Flows very differently" from the original's bar, and asked whether the gate hears "pauses"):
#              where the original breaks mid-bar (a punctuation mark after a word: 22 of its 76 bars, numbers only), ours must break after
#              the SAME syllable (flow_fit.sylls per word, the template's own count; the exact-count rule makes the indices comparable).
#              Ours may break with punctuation, or where a new clause starts (a joining word, or a subject pronoun straight after a
#              content word), since the comma cap (ww/write/phrase_audit) would otherwise force a comma at every one.
#   cell       also hears a SPELLED-OUT acronym (16 Oct 2026, the same bar): letters said as names repeat a cell inside one word ("W"
#              is "double-u"), which a word-level repeat count missed.
#   same_step  (16 Oct 2026, Joe on bar 46: the original's opener "is smoother than 'Fags? Cheap packs'") the audio puts two syllables on
#              one 16th in some bars and the original makes one of them weak; ours put two stresses there ("Cheap packs"). fast_jam only
#              counted ADJACENT 16ths, so the same-16th cram was invisible. TOL 0 against the original's same bar.
BAR_MEASURES = ("fast_jam", "cell", "barline", "pause", "same_step")
BAR_SLACK = 0.10
# Fitted 15 Oct 2026 on the only labels there are: the loosest tolerances that still catch all 4 flagged bars, which fail the
# fewest bars of hook r3 (Joe: "I like this", bar 12 excepted): 5 of 15 still fail, and they are listed to Joe to judge. At 0/0/0/0 the
# gate failed 11 of those 15. In-sample and tiny: every new verdict goes into flow_flagged.txt or flow_ok.txt and is re-checked here.
TOL = {"stress_run": 1, "hard_joins": 0, "closed_run": 1, "restart": 1}
CLOSED = {"ɪ", "ʊ"}
JOINERS = {"and", "but", "so", "when", "while", "if", "because", "cause", "cos", "that", "who", "which", "then", "or", "till",
           "until", "as", "where", "though", "once", "since", "before", "after", "nor", "like"}
LABEL = {"stress_run": "stressed syllables in a row", "hard_joins": "hard mouth-shape joins",
         "closed_run": "short closed vowels (ɪ ʊ) in a row", "restart": "sentence restarts mid-bar",
         "fast_jam": "stressed syllables jammed on back-to-back 16ths", "cell": "repeated cell + internal rhyme (needs a cell and internal rhyme >= the original's - 1)",
         "internal": "internal rhyme in a repeated-cell bar",
         "barline": "rhyme at the bar line (needs a word at the original's syllable, +-1, with the same vowels as the line's end word; ours has none)",
         "same_step": "stressed syllables crammed onto ONE 16th (where the original's bar puts a weak syllable in that slot)",
         "pause": "pause position (the original pauses after syllable(s) {p}; ours does not break there)",
         "barline_close": "bar-line rhyme too loose (rapfit pair score with the line's end; must be within 0.10 of the original's)"}


def _ww():
    from ww import bridge
    bridge._pron_ready()


def stress_run(line):
    best = run = 0
    for weak in ff.sylls(line):
        run = 0 if weak else run + 1
        best = max(best, run)
    return best


def hard_joins(line):
    _ww()
    from ww.write import earcheck
    return sum(1 for j in earcheck.word_joins(line) if j["score"] >= 2)


def closed_run(line):
    _ww()
    from ww.write import rapfit
    best = run = 0
    for v, *_ in rapfit._syl(line):
        run = run + 1 if v in CLOSED else 0
        best = max(best, run)
    return best


@functools.lru_cache(maxsize=1)
def _nlp():
    import spacy
    return spacy.load("en_core_web_sm")


def restart(line):
    """subject pronouns that start a new clause straight after a content word, with no joining word between."""
    doc = _nlp()(line)
    n = 0
    for t in doc:
        if t.dep_ in ("nsubj", "nsubjpass") and t.pos_ == "PRON" and t.i > 0:
            prev = doc[t.i - 1]
            if prev.text.lower() not in JOINERS and prev.pos_ in ("NOUN", "PROPN", "VERB", "ADJ", "ADV", "NUM") and not prev.is_punct:
                n += 1
    return n


def fast_jam(bar_no, line):
    """stressed syllables on ADJACENT 16th steps of the original's audio template for this bar (None: no template or a different count)."""
    t = ff.T[bar_no - 1] if 1 <= bar_no <= len(ff.T) else {}
    steps = t.get("steps")
    w = ff.sylls(line)
    if not steps or len(steps) != len(w):
        return None
    return sum(1 for k in range(len(steps) - 1) if steps[k + 1] - steps[k] == 1 and not w[k] and not w[k + 1])


LETTER = {"W": "double you", "A": "ay", "B": "bee", "C": "see", "D": "dee", "E": "ee", "F": "eff", "G": "gee", "H": "aitch", "I": "eye",
          "J": "jay", "K": "kay", "L": "el", "M": "em", "N": "en", "O": "oh", "P": "pee", "Q": "queue", "R": "ar", "S": "ess", "T": "tee",
          "U": "you", "V": "vee", "X": "ex", "Y": "why", "Z": "zed"}


def spell(line):
    """all-caps acronyms (2+ letters) said as letter names: what the ear hears, not the spelling."""
    return re.sub(r"\b[A-Z]{2,}\b", lambda m: " ".join(LETTER[c] for c in m.group()), line)


def same_step(bar_no, line):
    """stressed syllable pairs that share ONE 16th step of the original's audio template (two syllables on one 16th: the original puts a
    weak syllable in that slot). None where there is no template or the syllable count differs."""
    t = ff.T[bar_no - 1] if 1 <= bar_no <= len(ff.T) else {}
    steps = t.get("steps")
    w = ff.sylls(line)
    if not steps or len(steps) != len(w):
        return None
    return sum(1 for k in range(len(steps) - 1) if steps[k + 1] == steps[k] and not w[k] and not w[k + 1])


def run_breaks(bar_no, line):
    """mid-bar stops (punctuation) where the next syllable falls on the same or the next 16th of the original's template: a stop with no
    room to stop. A NOTE, not a gate (16 Oct 2026): it fails 26 of v4's bars, so it waits for Joe's ear."""
    t = ff.T[bar_no - 1] if 1 <= bar_no <= len(ff.T) else {}
    steps = t.get("steps")
    if not steps or len(steps) != len(ff.sylls(line)):
        return None
    return sum(1 for k in breaks(line) if k < len(steps) and 0 <= steps[k] - steps[k - 1] <= 1)


def has_cell(line):
    """a repeated cell inside the bar: a content word said twice or more (acronyms spelled out), or an in-bar drum / echo (toolkit/ear.py)."""
    import collections
    import ear
    from ww.write import rhymeview
    ws = [rhymeview.core(w) for w in spell(line).split()]
    ws = [w for w in ws if w and w not in rhymeview.FUNC]
    rep = max(collections.Counter(ws).values()) if ws else 0
    return rep >= 2 or bool(ear.drums([line])) or bool(ear.echoes([line]))


def _vowels(sy):
    from ww.write import rapfit
    return tuple(x[0] for x in sy[rapfit._anchors(sy)[0][0]:])


def barline_hits(line, scored=False):
    """[(syllable index of the stress, 1-based)] for content words before the end tail whose vowels, from the stressed syllable to the end,
    are the line's end word's (an end rhyme landed inside the line). scored=True gives [(index, rapfit pair score with the end)]."""
    from ww.write import rapfit, rhymeview
    ws = line.split()
    ts = rhymeview.tail_start(ws)
    end = rhymeview.tail_text(ws)
    E = rapfit._syl(end)
    if not E:
        return []
    out, i = [], 0
    for w in ws[:ts]:
        c = rhymeview.core(w)
        n = len(ff.sylls(w)) if c else 0
        if c and c not in rhymeview.FUNC and n:
            sy = rapfit._syl(c)
            if sy:
                a = rapfit._anchors(sy)[0][0]
                if rapfit.prominent(sy[a]) and _vowels(sy) == _vowels(E):
                    out.append((i + a + 1, rapfit.score(c, end)["score"]) if scored else i + a + 1)
        i += n
    return out


def barline_par(bar_no, line):
    """the ORIGINAL's bar-line rhyme: the stressed syllable (1-based) of a hit that lands on steps 11-20 of its audio template, else 0."""
    t = ff.T[bar_no - 1] if 1 <= bar_no <= len(ff.T) else {}
    st = t.get("steps")
    if not st:
        return (0, 0.0)
    hits = [(k, sc) for k, sc in barline_hits(line, scored=True) if k <= len(st) and 11 <= st[k - 1] <= 20 and k < len(st) - 1]
    return hits[0] if hits else (0, 0.0)


PUNCT = re.compile(r"[,.;:?!\u2026\u2014\u2013]['\"\u2019\u201d)]*$")
OPENERS = {"and", "but", "so", "cause", "cos", "then", "or", "when", "if", "while", "till", "until", "because", "though", "once", "since"}


def breaks(line, clauses=False):
    """syllable indices (1-based: the syllable a pause FOLLOWS) where the line breaks mid-bar: a punctuation mark after a word.
    clauses=True also counts a new clause starting with no mark (a joining word, or a subject pronoun straight after a content word)."""
    toks = line.split()
    out, i, ends = [], 0, []
    for j, t in enumerate(toks):
        i += len(ff.sylls(t))
        ends.append(i)
        if j < len(toks) - 1 and PUNCT.search(t):
            out.append(i)
    if clauses:
        for j in range(1, len(toks)):
            w = re.sub(r"[^a-z']", "", toks[j].lower().replace("\u2019", "'"))
            if w in OPENERS:
                out.append(ends[j - 1])
        doc = _nlp()(line)
        for t in doc:
            # a MAIN clause only: "the guy I know" (a relative clause with no "that") is said through, not paused
            if t.dep_ in ("nsubj", "nsubjpass") and t.pos_ == "PRON" and t.i > 0 and t.head.dep_ in ("ROOT", "conj", "parataxis"):
                prev = doc[t.i - 1]
                if prev.pos_ in ("NOUN", "PROPN", "VERB", "ADJ", "ADV", "NUM") and prev.text.lower() not in JOINERS:
                    out.append(len(ff.sylls(doc[:t.i].text)))
    return sorted(set(k for k in out if k))


def internal(line):
    import match
    return match.internal_density([line])[0]


def profile(line):
    return {"stress_run": stress_run(line), "hard_joins": hard_joins(line), "closed_run": closed_run(line), "restart": restart(line)}


@functools.lru_cache(maxsize=1)
def par_table():
    try:
        return json.load(open(PAR, encoding="utf-8"))["bars"]
    except OSError:
        return None


def check(bar_no, line):
    """[(measure, ours, original's bar)] for every measure where the bar is worse than the original's bar beyond TOL.
    An empty list means the bar passes; None means there is no par for that bar (no table, or out of range)."""
    tab = par_table()
    if not tab or not (1 <= bar_no <= len(tab)):
        return None
    par = tab[bar_no - 1]
    ours = profile(line)
    out = [(m, ours[m], par[m]) for m in MEASURES if ours[m] > par[m] + TOL[m]]
    if "fast_jam" in par:
        fj = fast_jam(bar_no, line)
        if fj is not None and fj > par["fast_jam"]:
            out.append(("fast_jam", fj, par["fast_jam"]))
    if "same_step" in par:
        ss = same_step(bar_no, line)
        if ss is not None and ss > par["same_step"]:
            out.append(("same_step", ss, par["same_step"]))
    if par.get("barline"):
        k, need = par["barline"], par.get("barline_score", 0.0) - BAR_SLACK
        near = [sc for h, sc in barline_hits(line, scored=True) if abs(h - k) <= 1]
        if not near:
            out.append(("barline", 0, k))
        elif max(near) < need:
            out.append(("barline_close", max(near), round(par.get("barline_score", 0.0), 2)))
    if par.get("pause"):
        have = breaks(line, clauses=True)
        miss = [k for k in par["pause"] if k not in have]
        if miss:
            out.append(("pause", have, par["pause"]))
    if par.get("cell"):
        if not has_cell(line):
            out.append(("cell", 0, 1))
        elif internal(line) < par.get("internal", 0) - 1:
            out.append(("internal", internal(line), par.get("internal", 0)))
    return out


def describe(fails):
    return "; ".join(LABEL[m].format(p=", ".join(map(str, p))) + f" (ours breaks after {', '.join(map(str, o)) or 'none'})" if m == "pause"
                     else f"{LABEL[m]} {o} (the original's bar has {p})" for m, o, p in fails)


def flagged(path=FLAGGED):
    out = []
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="utf-8"):
        if l.strip() and not l.startswith("#"):
            b, line, why = [x.strip() for x in l.split("|", 2)]
            out.append((int(b), line, why))
    return out


def par_syl(bar_no):
    """the original's syllable count for this bar, counted by the same counter slotcheck uses (bridge.syllable_count). The audio
    template's count differs in one bar (64, "would've"), so the exact-count rule compares like with like."""
    tab = par_table()
    if not tab or not (1 <= bar_no <= len(tab)):
        return None
    return tab[bar_no - 1].get("syl")


def build(orig_path):
    L = [l.strip() for l in open(orig_path, encoding="utf8") if l.strip()][:76]
    _ww()
    from ww import bridge
    bars = [dict(profile(l), syl=bridge.syllable_count(l), fast_jam=fast_jam(i + 1, l) or 0, cell=int(has_cell(l)), internal=internal(l),
                 barline=barline_par(i + 1, l)[0], barline_score=barline_par(i + 1, l)[1], pause=breaks(l),
                 same_step=same_step(i + 1, l) or 0, run_breaks=run_breaks(i + 1, l) or 0) for i, l in enumerate(L)]
    json.dump({"_note": "Per-bar flow profile of the ORIGINAL (numbers only, rule 4), built by toolkit/flow_par.py --build. "
                        "A draft bar may be no worse than the original's bar in the same position.", "measures": list(MEASURES) + list(BAR_MEASURES), "bars": bars},
              open(PAR, "w", encoding="utf-8"), indent=1)
    par_table.cache_clear()
    return bars


def selftest(orig_path=None):
    ok = True
    if par_table() is None:
        print("flow_par selftest: FAILED (no benchmark/flow_par.json; run --build ORIG)")
        return False
    if orig_path:
        L = [l.strip() for l in open(orig_path, encoding="utf8") if l.strip()][:76]
        bad = [i + 1 for i, l in enumerate(L) if check(i + 1, l)]
        good = not bad
        ok &= good
        print(("ok  " if good else "BAD ") + f"the original passes its own par in all {len(L)} bars (by construction){'' if good else ': ' + str(bad)}")
    caught = [(b, line, check(b, line)) for b, line, _ in flagged()]
    miss = [(b, line) for b, line, f in caught if not f]
    good = not miss
    ok &= good
    print(("ok  " if good else "BAD ") + f"Joe's flagged bars are caught: {len(caught) - len(miss)} of {len(caught)}" + (f"; missed {miss}" if miss else ""))
    for b, line, f in caught:
        print(f"     bar {b}: {describe(f) if f else 'NOT CAUGHT'}")
    oks = [(b, line, check(b, line)) for b, line, _ in flagged(OK)]
    wrong = [(b, line) for b, line, f in oks if f]
    good = not wrong
    ok &= good
    print(("ok  " if good else "BAD ") + f"bars Joe said flow fine pass: {len(oks) - len(wrong)} of {len(oks)}" + (f"; failing {wrong}" if wrong else ""))
    print("flow_par selftest:", "PASSED" if ok else "FAILED")
    return ok


def main():
    a = sys.argv[1:]
    if a and a[0] == "--build":
        bars = build(a[1])
        print(f"wrote {os.path.relpath(PAR, ROOT)} ({len(bars)} bars, numbers only)")
        return 0
    if not a or a[0] == "--selftest":
        return 0 if selftest(a[1] if len(a) > 1 else os.environ.get("WW_PRIVATE_ORIGINAL")) else 1
    b, line = int(a[0]), " ".join(a[1:])
    ours, par = profile(line), (par_table() or [{}] * 76)[b - 1]
    for m in MEASURES:
        print(f"  {LABEL[m]:38s} ours {ours[m]}  original bar {b}: {par.get(m, '?')}")
    f = check(b, line)
    print("PASS" if not f else "FAIL: " + describe(f))
    return 0 if not f else 1


if __name__ == "__main__":
    sys.exit(main())
