"""The ONLY door from ww into toolkit/.

Pure functions: no printing, no file writes, no benchmark/ access, safe under captured stdout and under
multiprocessing (spawn). Everything the new pipeline needs from the old sound instruments is exposed here with
a stable signature, so toolkit/ internals can change without touching ww.

What is deliberately NOT exposed: the learned judge, forge/pipeline, funny/attest, flow-pattern % and the beat
grid (registry status failed_validation). Syllable count and end shape are the only flow facts that are hard.
"""
from __future__ import annotations

import re
import sys
from typing import Iterable

from . import config


def _toolkit_on_path() -> None:
    p = str(config.TOOLKIT)
    if p not in sys.path:
        sys.path.insert(0, p)


_toolkit_on_path()

_WORD = re.compile(r"[A-Za-z']+")


def norm(text: str) -> str:
    """curly quotes and dashes to ASCII, so "wouldn’t" is one word (it used to split into 'wouldn' + 't' and read as OOV)."""
    try:
        from rhyme_tools import register_caps
        register_caps(text)
    except Exception:   # noqa: BLE001 - the toolkit is not on the path yet
        pass
    return text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("—", " - ")


def words(text: str) -> list[str]:
    return _WORD.findall(norm(text))


_PRON_READY = False


def _pron_ready() -> None:
    """register the persisted pronunciation overrides (lexicon, reviewed brands, g2p guesses) with the toolkit, once per process."""
    global _PRON_READY
    if not _PRON_READY:
        _PRON_READY = True
        from .lex import pron   # noqa: F401  (importing registers the overrides)


def syllable_count(line: str) -> int:
    """syllables as the project counts them (CMU + OVR, upper-case acronyms spelt out)."""
    _pron_ready()
    import flow_fit
    return len(flow_fit.sylls(line))


def end_shape(line: str) -> str:
    """'|Sw' = rhyme starts a word, then Strong+weak; '~' = rhyme lands mid-word (e.g. Majorca '~Sw')."""
    import flow_fit
    return flow_fit.end_shape(line)[0]


def rhyme_score(a: str, b: str) -> float:
    """graded rhyme of two bar endings, 0-1 (>= 0.78 counts as a rhyme; 0.80 may be bare assonance - see phon.score)."""
    _pron_ready()
    import match
    return round(float(match.best_end(a, b)), 3)


def carpet(lines: Iterable[str]) -> dict:
    """{'pairs','total','min','share'}: how many of all end-pairs rhyme (>= 0.78)."""
    import match
    return match.carpet_of(list(lines))


def phones(word: str):
    """British phones for scoring, or None when neither Britfone, CMU nor the OVR table knows the word."""
    _pron_ready()
    import helpers
    w = re.sub(r"[^a-z']", "", word.lower())
    return helpers.uk_phones(w) if w else None


def rare_joins(line: str):
    """Word boundaries where the mouth must reorganise in one of the RARE ways: a fricative into /h/ (a glottal
    reset), or a voiced fricative into a liquid (same-place stop-stop was removed 15 Oct 2026: it is the easiest join, Joe's ear). Returns (word_a, word_b, reason).
    The original's par, counted on its 92 lines (14 Oct 2026): 0 in 78% of its bars and 2 or more in only 6.
    Joe's ear found this by hand in "whites, he's" / "he's wrecked" before any tool measured it -- see
    toolkit/flow_check.joins for the tables and the calibration."""
    _toolkit_on_path()
    import flow_check
    return flow_check.rare_joins(line)


def stress_pattern(word: str):
    """e.g. '10' for a stress-first two-syllable word, from the project's pronouncer (CMU + OVR + suffix rules + British spellings),
    or None if unknown. Used for end-word SHAPE decisions."""
    import re as _re
    import rhyme_tools
    ph = rhyme_tools.pron(word)
    if not ph:
        from .lex import pron as _pron   # lazy: ww.lex.pron imports this module
        _pron.ensure(word)
        ph = rhyme_tools.pron(word)
    if not ph:
        return None
    out = ""
    for t in ph:
        m = _re.search(r"([A-Z]+)([012]?)$", t)
        if m and rhyme_tools.is_v(t):
            out += m.group(2) or "0"
    return out or None


def oov_words(text: str) -> list[str]:
    """Words the sound tools cannot pronounce. A candidate containing any of these must be REJECTED and the word
    queued (ww.failures), never guessed: the old vowel-only fallback is how 'Zurich' lost its /k/.

    The queue was documented but never written (14 Oct 2026: ww/failures.py had no caller and eval/failures.jsonl did not
    exist, so rule R10's "every rejection becomes data" collected nothing and the same word was re-discovered every run).
    It is written here, once per distinct word per process, and de-duplicated against the log on disk."""
    import rhyme_tools
    out = []
    for w in words(text):
        lw = w.lower().strip("'")
        if len(lw) < 2 and lw not in ("a", "i"):
            continue
        if phones(lw) is None and not rhyme_tools.pron(lw):
            from .lex import pron as _pron   # lazy: ww.lex.pron imports this module
            _pron.ensure(lw)                  # compound split / flagged g2p, registered for every toolkit measure
            if not rhyme_tools.pron(lw):
                out.append(w)
                _queue_oov(lw)
    return out


_OOV_SEEN = None


def _queue_oov(word: str) -> None:
    """record an unpronounceable word in eval/failures.jsonl (kind=oov), once per word per process."""
    global _OOV_SEEN
    if _OOV_SEEN is None:
        from . import failures
        _OOV_SEEN = {r.get("text") for r in failures.read("oov")}
    if word in _OOV_SEEN:
        return
    _OOV_SEEN.add(word)
    try:
        from . import failures
        failures.log("oov", word, detail="no pronunciation in britfone, cmudict, OVR or the g2p chain", source="bridge.oov_words")
    except Exception:  # noqa: BLE001 - logging must never break a scoring path
        pass


def meaning_flags(bars: Iterable[str], kinds: tuple = ("inventory", "filler")) -> list[tuple[int, str, list[str]]]:
    """toolkit/meaning_gate hard findings per bar. By default only the SENSE rules (inventory of things with no claim; filler
    frame). The function-word-end rule is a rap-bar convention, not grammar - real enjambed verse trips it - so it is excluded
    unless asked for with kinds=('inventory','filler','end word'). Calibrated quiet on the original's 92 lines; a PREFILTER."""
    import meaning_gate
    r = meaning_gate.audit([norm(b) for b in bars])
    out = []
    for i, b, hard, _ in r["bars"]:
        keep = [h for h in hard if any(h.startswith(k) for k in kinds)]
        if keep:
            out.append((i, b, keep))
    return out


def invented_words(text: str) -> list[str]:
    """tokens that look made-up: unknown to CMU/Britfone/OVR AND to wordfreq, not capitalised mid-line, 4+ letters.
    Real rare words (grandmamma, photographically) have a wordfreq entry; 'boraded' does not."""
    import wordfreq
    out = []
    t = norm(text)
    for m in _WORD.finditer(t):
        w = m.group()
        lw = w.lower().strip("'")
        if len(lw) < 4 or not lw.isalpha():
            continue
        if m.start() > 0 and w[0].isupper():
            continue
        if wordfreq.zipf_frequency(lw, "en") == 0:
            from .lex import pron as _pron       # lazy: ww.lex.pron imports this module
            if phones(lw) is None or _pron.is_guess(lw):     # a g2p guess for a word no dictionary or lexicon knows is still invented
                out.append(w)
    return out


def selftest() -> tuple[bool, str]:
    """Contract tests: the bridge agrees with what calibrate.py already proves about the toolkit."""
    import io
    import contextlib
    problems: list[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            problems.append(msg)

    # Joe's accepted hook 1-4 (own text, kept in toolkit/tests as the gates' positive control)
    import fixtures
    bars = fixtures.joe_bars()
    check(len(bars) == 4, f"expected 4 positive-control bars, got {len(bars)}")
    c = carpet(bars)
    check(c["pairs"] == 6 and c["min"] >= 0.99, f"positive-control carpet should be 6/6 at 1.00, got {c}")
    check(syllable_count("Yo, bonjourno") >= 3, "syllable_count too low for 'Yo, bonjourno'")
    check(end_shape(bars[1]).startswith("|"), f"end_shape of a rhyme-from-word-start bar: {end_shape(bars[1])}")
    check(rhyme_score("Bordeaux", "porno") >= 0.78, "Bordeaux ~ porno should rhyme")
    check(rhyme_score("Bordeaux", "plain") < 0.78, "Bordeaux ~ plain should not rhyme")
    check(oov_words("Zurich Porto Bordeaux Ljubljana") == [], f"place names must be pronounceable: {oov_words('Zurich Porto Bordeaux Ljubljana')}")
    # since 13 Oct the pron chain's g2p (no nltk) pronounces anything, so nonsense is caught as an INVENTED word (unknown to every dictionary AND to wordfreq)
    check(invented_words("a qzxqxzq boraded") == ["qzxqxzq", "boraded"], f"nonsense must be reported invented: {invented_words('a qzxqxzq boraded')}")
    mf = meaning_flags(["Pass maps plans and the road the rail going", "So I boarded a plane out to Bordeaux"])
    check(len(mf) == 1 and mf[0][0] == 1, f"meaning_flags should flag only the inventory bar: {mf}")
    # captured stdout: the import-time reconfigure bug (13 Oct) must stay dead
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        syllable_count("one two three")
    check(buf.getvalue() == "", "bridge calls must not print")
    # the OOV queue must actually write (rule R10): it was documented for weeks with no caller and no eval/failures.jsonl
    # at all, so an unpronounceable word was re-discovered on every run and never collected.
    import tempfile
    from pathlib import Path
    from . import config, failures
    real = config.FAILURES
    try:
        config.FAILURES = Path(tempfile.mkdtemp()) / "f.jsonl"
        global _OOV_SEEN
        _OOV_SEEN = None                      # forget the in-process de-dupe cache for the test
        _queue_oov("qzxqxzq")
        _queue_oov("qzxqxzq")                 # second call must not write a duplicate row
        rows = failures.read("oov")
        check(len(rows) == 1 and rows[0]["text"] == "qzxqxzq", f"the OOV queue must write exactly one row: {rows}")
    finally:
        config.FAILURES = real
        _OOV_SEEN = None
    return (not problems, "; ".join(problems) if problems else "bridge contract holds")


def _child(args):  # top-level so it pickles under spawn
    from ww import bridge
    return bridge.rhyme_score(*args), bridge.syllable_count("Yo, bonjourno")


def selftest_multiprocessing() -> tuple[bool, str]:
    """same pure functions inside spawned worker processes (Windows default start method)."""
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(2) as pool:
        out = pool.map(_child, [("Bordeaux", "porno"), ("Bordeaux", "plain")])
    ok = out[0][0] >= 0.78 and out[1][0] < 0.78 and out[0][1] == out[1][1]
    return ok, f"workers returned {out}"
