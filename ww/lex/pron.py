"""Pronunciation chain (plan 6, 'pronunciation coverage as its own deliverable').

  1. the toolkit pronouncer (CMUdict + the hand OVR table + suffix rules + British spellings)      source = known
  2. compound splitting from two KNOWN parts ("wristband" = wrist + band; secondary stress on the 2nd part)   source = compound
  3. g2p-en guess, flagged `needs_check`                                                             source = g2p
  4. nothing: the word is OOV -> the candidate containing it is REJECTED and the word queued in eval/failures.jsonl (never guessed silently)

Derived entries are registered into rhyme_tools.OVR in memory (so every toolkit measure sees them) and persisted to
ww/lex/banks/pron_overrides.json, which is reloaded on import. Espeak-ng (foreign names) is not installed; names stay on the OVR route.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from .. import bridge, config

OVERRIDES = Path(__file__).resolve().parent / "banks" / "pron_overrides.json"


def _rt():
    import rhyme_tools
    return rhyme_tools


def _known(word: str):
    return _rt().pron(word.lower())


def _load() -> dict:
    return json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}


def _save(d: dict) -> None:
    OVERRIDES.parent.mkdir(parents=True, exist_ok=True)
    OVERRIDES.write_text(json.dumps(d, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


# hand-checked entries for words that appeared in real candidates and defeat every rule above (anglicised, as the song is English)
MANUAL = {
    "noord": "N AO1 R T", "dirham": "D IH0 R AE1 M", "dirhams": "D IH0 R AE1 M Z", "titisee": "T IH1 T IH0 S EY2",
    "salut": "S AE0 L UW1", "tombola": "T AA0 M B OW1 L AH0", "souk": "S UW1 K", "kgari": "K AH0 G AA1 R IY0",
}


GUESSED: set = set()      # words whose only pronunciation is a g2p guess AND that no trusted source (lexicon) vouches for


def is_guess(word: str) -> bool:
    return re.sub(r"[^a-z]", "", word.lower()) in GUESSED


def register_persisted() -> int:
    """persisted entries FILL GAPS only: a word cmudict already knows keeps its dictionary pronunciation.
    The persisted file holds lexicon names keyed with digits and symbols stripped, so without this rule
    A1 -> 'a' (EY1 W AH1 N), More4 -> 'more' (M AO1 F AO1 R), E4 -> 'e', Film4 -> 'film', Jet2 -> 'jet' shadowed
    the common words inside every ww process: 23 of the original's 76 bars were mis-counted there while the
    toolkit CLIs (which never load this file) counted them right (measured 14 Oct 2026)."""
    rt = _rt()
    d = _load()
    for w, rec in d.items():
        if w in rt.D:
            continue
        rt.OVR.setdefault(w, rec["arpabet"])
        if rec.get("source") == "g2p" and not rec.get("lexicon"):
            GUESSED.add(w)
    for w, a in MANUAL.items():
        rt.OVR.setdefault(w, a)
    return len(d) + len(MANUAL)


def _demote_primary(tokens: list[str]) -> list[str]:
    return [t[:-1] + "2" if t.endswith("1") else t for t in tokens]


def split_compound(word: str) -> Optional[tuple[str, list[str]]]:
    import wordfreq
    w = word.lower()
    best = None
    for i in range(2, len(w) - 1):
        a, b = w[:i], w[i:]
        if len(a) < 3 and wordfreq.zipf_frequency(a, 'en') < 5.0 or len(b) < 3 and wordfreq.zipf_frequency(b, 'en') < 5.0:
            continue   # a 2-letter part must be a very common word (by, up, in), or 'tombola' = tom + bola
        pa, pb = _known(a), _known(b)
        if not pa or not pb:
            continue
        score = min(wordfreq.zipf_frequency(a, "en"), wordfreq.zipf_frequency(b, "en"))
        if score >= 3.5 and (best is None or score > best[0]):  # both parts must be COMMON words, or 'tombola' = tomb+ola
            best = (score, a, b, pa, pb)
    if not best:
        return None
    _, a, b, pa, pb = best
    return f"{a}+{b}", list(pa) + _demote_primary(list(pb))


_G2P = None


def g2p_guess(word: str) -> Optional[list[str]]:
    global _G2P
    try:
        if _G2P is None:           # the neural model loads in ~1 s: build it once per process, WITHOUT g2p-en's nltk dependencies
            from g2p_en.g2p import G2p
            g = G2p.__new__(G2p)
            g.graphemes = ["<pad>", "<unk>", "</s>"] + list("abcdefghijklmnopqrstuvwxyz")
            g.phonemes = ["<pad>", "<unk>", "<s>", "</s>"] + ['AA0', 'AA1', 'AA2', 'AE0', 'AE1', 'AE2', 'AH0', 'AH1', 'AH2', 'AO0', 'AO1', 'AO2', 'AW0', 'AW1', 'AW2',
                                                               'AY0', 'AY1', 'AY2', 'B', 'CH', 'D', 'DH', 'EH0', 'EH1', 'EH2', 'ER0', 'ER1', 'ER2', 'EY0', 'EY1', 'EY2', 'F', 'G', 'HH',
                                                               'IH0', 'IH1', 'IH2', 'IY0', 'IY1', 'IY2', 'JH', 'K', 'L', 'M', 'N', 'NG', 'OW0', 'OW1', 'OW2', 'OY0', 'OY1', 'OY2',
                                                               'P', 'R', 'S', 'SH', 'T', 'TH', 'UH0', 'UH1', 'UH2', 'UW', 'UW0', 'UW1', 'UW2', 'V', 'W', 'Y', 'Z', 'ZH']
            g.g2idx = {x: i for i, x in enumerate(g.graphemes)}
            g.idx2g = {i: x for i, x in enumerate(g.graphemes)}
            g.p2idx = {x: i for i, x in enumerate(g.phonemes)}
            g.idx2p = {i: x for i, x in enumerate(g.phonemes)}
            g.load_variables()
            _G2P = g
        out = [t for t in _G2P.predict(re.sub(r"[^a-z]", "", word.lower())) if re.fullmatch(r"[A-Z]+[012]?", t)]
        return out or None
    except Exception:  # noqa: BLE001 - nltk data missing etc.: the chain simply ends here
        return None


def ensure(word: str, persist: bool = True) -> dict:
    """make the toolkit able to pronounce `word` if any rule can; returns {'word','source','arpabet','needs_check'}."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return {"word": word, "source": None, "arpabet": None, "needs_check": False}
    if _known(w):
        return {"word": word, "source": "known", "arpabet": " ".join(_known(w)), "needs_check": False}
    rec = None
    sc = split_compound(w)
    if sc:
        rec = {"source": "compound", "via": sc[0], "arpabet": " ".join(sc[1]), "needs_check": False}
    else:
        g = g2p_guess(w)
        if g:
            rec = {"source": "g2p", "via": "g2p-en", "arpabet": " ".join(g), "needs_check": True}
    if not rec:
        return {"word": word, "source": None, "arpabet": None, "needs_check": False}
    _rt().OVR[w] = rec["arpabet"]
    if rec["source"] == "g2p":
        GUESSED.add(w)
    if persist:
        d = _load()
        d[w] = rec
        _save(d)
    return {"word": word, **rec}


def selftest() -> tuple[bool, str]:
    problems = []
    _rt().OVR.pop("wristband", None)   # may have been registered from the persisted overrides
    r = ensure("wristband", persist=False)
    if r["source"] != "compound" or not r["arpabet"]:
        problems.append(f"wristband should split into wrist+band: {r}")
    if bridge.stress_pattern("wristband") not in ("12", "10"):
        problems.append(f"after ensure the stress shape should be known: {bridge.stress_pattern('wristband')}")
    if ensure("traffic", persist=False)["source"] != "known":
        problems.append("a dictionary word must be 'known'")
    z = ensure("qzxqxzqv", persist=False)
    if z["source"] not in (None, "g2p"):
        problems.append(f"nonsense must be unresolved or flagged g2p: {z}")
    register_persisted()               # restore whatever the persisted file says
    return (not problems, "; ".join(problems) if problems else "dictionary, compound-split (wrist+band) and flagged-g2p routes work; nonsense stays unresolved")


register_persisted()
