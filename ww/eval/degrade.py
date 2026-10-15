"""Degradations D1-D16 and null edits N1-N3 (plan 5.2). Each takes a list of bars and returns a changed list, or None when it does
not apply to that text. Deterministic given (seed, text). Offline kinds only; D7 (fluent-but-empty rewrite) has a template version
here and an LLM version to be added once a writer key exists - it MUST come from >= 2 families before it counts as evidence.

`EXPECT` states, for each kind, which measure classes it must move and which it must leave alone. That is the validation
contract: a SOUND measure must be invariant to D1/D4/D7 (sound preserved, sense destroyed) and must move on D2/D3 only through
rhyme/shape; a SENSE measure must fall on all of them; every measure must be invariant to the null edits.
"""
from __future__ import annotations

import hashlib
import random
import re
from typing import Callable, Optional

from .. import bridge
from ..write import frames

_ALPHA = re.compile(r"[A-Za-z']+")


def rng_for(seed: int, bars: list[str], kind: str) -> random.Random:
    h = hashlib.sha256((f"{seed}|{kind}|" + "\n".join(bars)).encode("utf-8")).hexdigest()
    return random.Random(int(h[:12], 16))


def _func() -> set:
    import rhyme_tools
    return {w.lower() for w in rhyme_tools.FUNC}


def _last_word(bar: str) -> Optional[re.Match]:
    ms = list(_ALPHA.finditer(bar))
    return ms[-1] if ms else None


def _differs(a: list[str], b: list[str]) -> bool:
    return [x.strip() for x in a] != [x.strip() for x in b]


# ---- sound-preserving, sense-destroying ---------------------------------------------------------------
def d1_wrong_end_word(bars, rng, pool=None):
    """swap one bar's end word for a perfect rhyme of the same length that is very likely the wrong sense."""
    import pronouncing
    import wordfreq
    func = _func()
    order = list(range(len(bars)))
    rng.shuffle(order)
    for i in order:
        m = _last_word(bars[i])
        if not m:
            continue
        w = m.group().lower().strip("'")
        phones = pronouncing.phones_for_word(w)
        if not phones:
            continue
        n_syl = pronouncing.syllable_count(phones[0])
        cands = sorted({r for r in pronouncing.rhymes(w)
                        if r.isalpha() and r != w and r not in func and wordfreq.zipf_frequency(r, "en") >= 3.3
                        and r[:3] != w[:3] and r[-3:] != w[-3:]
                        and (lambda p: bool(p) and pronouncing.syllable_count(p[0]) == n_syl)(pronouncing.phones_for_word(r))})
        if not cands:
            continue
        pick = rng.choice(cands)
        out = list(bars)
        out[i] = bars[i][:m.start()] + (pick.capitalize() if m.group()[0].isupper() else pick) + bars[i][m.end():]
        return out
    return None


def d4_filler_frame(bars, rng, pool=None):
    out = []
    for b in bars:
        t = _ALPHA.findall(b)
        if len(t) < 4:
            out.append(b)
            continue
        out.append(" ".join(t[:2]) + " and the whole " + t[-1])
    return out if _differs(bars, out) else None


def d7_cliche_template(bars, rng, pool=None):
    """template cliche rewrite of equal syllable count: fluent, on-topic-ish, says nothing. (LLM version comes later.)"""
    bank = [
        "Living my best life on the road", "Chasing the sunset in a far-off land", "Passport stamps and wanderlust",
        "Every journey makes you who you are", "Collecting memories not things", "The world is a book and I read it",
        "Following my dreams across the sea", "Just a soul out searching for the light", "Making moments that will last a lifetime",
        "Taking the road less travelled by", "Good vibes and great company all day", "Wherever I wander I find myself",
        "Sun on my skin and wind in my hair", "Adventure is calling and I answer", "Seeing the sights from coast to coast",
    ]
    out, left = [], list(bank)
    for b in bars:
        target = bridge.syllable_count(b)
        best = min(left or bank, key=lambda c: (abs(bridge.syllable_count(c) - target), rng.random()))
        if best in left:
            left.remove(best)
        out.append(best)
    return out


# ---- structure ----------------------------------------------------------------------------------------
def d2_shuffle_within(bars, rng, pool=None):
    if len(bars) < 3:
        return None
    for _ in range(10):
        out = list(bars)
        rng.shuffle(out)
        if _differs(bars, out):
            return out
    return None


def d3_swap_across(bars, rng, pool=None):
    """replace roughly half the bars with bars from another unit (pool = list of other units' bars)."""
    if not pool or len(bars) < 2:
        return None
    donor = rng.choice(pool)
    out = list(bars)
    for i in rng.sample(range(len(bars)), max(1, len(bars) // 2)):
        out[i] = rng.choice(donor)
    return out if _differs(bars, out) else None


def d6_payoff_deleted(bars, rng, pool=None):
    if len(bars) >= 4:
        return list(bars[:-1])
    ws = _ALPHA.findall(bars[-1]) if bars else []
    if len(ws) >= 5:
        return list(bars[:-1]) + [" ".join(ws[:-2])]
    return None


def d16_interleave(bars, rng, pool=None):
    if not pool or len(bars) < 4:
        return None
    donor = rng.choice(pool)
    out = [bars[i] if i % 2 == 0 else donor[(i // 2) % len(donor)] for i in range(len(bars))]
    return out if _differs(bars, out) else None


# ---- content / register ------------------------------------------------------------------------------
def d5_noun_stack(bars, rng, pool=None):
    func = _func()
    out = []
    for b in bars:
        ws = [w for w in _ALPHA.findall(b) if w.lower() not in func and not re.search(r"(ed|ing)$", w.lower()) and len(w) > 2]
        out.append(" ".join(ws[:6]) if len(ws) >= 2 else b)
    return out if _differs(bars, out) else None


def d8_persona_break(bars, rng, pool=None):
    sad = ["I felt so alone and I started to cry", "I was scared and I missed my mum", "I could not stop worrying about everything",
           "Honestly I was exhausted and miserable"]
    out = list(bars)
    out[rng.randrange(len(out))] = rng.choice(sad)
    return out


def d9_specificity_wash(bars, rng, pool=None):
    out = []
    for b in bars:
        s = re.sub(r"\b\d+(?:\.\d+)?\b", "a few", b)
        words = s.split(" ")
        for i, w in enumerate(words):
            core = re.sub(r"[^A-Za-z']", "", w)
            if i > 0 and core[:1].isupper() and core not in ("I", "I'm", "I'd", "I'll", "I've"):
                words[i] = w.replace(core, "somewhere")
        out.append(" ".join(words))
    return out if _differs(bars, out) else None


def d10_explain_joke(bars, rng, pool=None):
    return list(bars) + [rng.choice(["Because that is the joke, you see", "Get it, because it means two things", "That is a pun on the other meaning"])]


def d11_moral_ending(bars, rng, pool=None):
    return list(bars) + [rng.choice(["And that is what travel teaches us all", "Remember to be kind wherever you go",
                                     "In the end it is the people that matter"])]


def d12_telegraphic(bars, rng, pool=None):
    out = []
    for b in bars:
        s = re.sub(r"\b(the|a|an|I|I'm|he|she|we|they|was|were|is|are|am|had|have|has|did)\b\s*", "", b, flags=re.I)
        out.append(re.sub(r"\s+", " ", s).strip() or b)
    return out if _differs(bars, out) else None


def d13_dangling_pronoun(bars, rng, pool=None):
    out = list(bars)
    for i in rng.sample(range(len(bars)), len(bars)):
        m = re.search(r"\b(the|my|a)\s+([a-z]{3,})\b", bars[i])
        if m:
            out[i] = bars[i][:m.start()] + rng.choice(["him", "it", "them"]) + bars[i][m.end():]
            return out
    return None


US = {"lorry": "truck", "pub": "bar", "mate": "dude", "quid": "bucks", "lift": "elevator", "flat": "apartment",
      "football": "soccer", "holiday": "vacation", "petrol": "gas", "biscuit": "cookie", "chips": "fries", "crisps": "chips",
      "trainers": "sneakers", "mum": "mom", "queue": "line", "rubbish": "garbage", "pavement": "sidewalk", "boot": "trunk",
      "tube": "subway", "bloke": "guy", "lads": "guys", "skint": "broke"}


def d14_americanism(bars, rng, pool=None):
    out = []
    for b in bars:
        s = b
        for k, v in US.items():
            s = re.sub(r"\b" + k + r"\b", v, s, flags=re.I)
        out.append(s)
    return out if _differs(bars, out) else None


def d15_invented_word(bars, rng, pool=None):
    import wordfreq
    idx = list(range(len(bars)))
    rng.shuffle(idx)
    for i in idx:
        for m in _ALPHA.finditer(bars[i]):
            w = m.group()
            if len(w) >= 6 and w.isalpha() and wordfreq.zipf_frequency(w.lower(), "en") >= 3.0:
                k = rng.randrange(2, len(w) - 2)
                bad = w[:k] + w[k + 1] + w[k] + w[k + 2:]
                if wordfreq.zipf_frequency(bad.lower(), "en") == 0:
                    out = list(bars)
                    out[i] = bars[i][:m.start()] + bad + bars[i][m.end():]
                    return out
    return None


# ---- null edits: meaning-preserving; every measure must treat these as ties ------------------------------
SYN = {"big": "large", "buy": "purchase", "start": "begin", "get": "obtain", "quick": "fast", "bought": "purchased", "begin": "start"}


def n1_synonym_swap(bars, rng, pool=None):
    out = []
    for b in bars:
        s = b
        for k, v in SYN.items():
            if re.search(r"\b" + k + r"\b", s):
                s = re.sub(r"\b" + k + r"\b", v, s, count=1)
                break
        out.append(s)
    return out if _differs(bars, out) else None


def n2_whitespace_case(bars, rng, pool=None):
    out = [("  " + b.strip() + " ").replace(" ,", ",") for b in bars]
    out = [o.replace(",", " ,").replace(" ,", ",") for o in out]
    return out if [b.strip() for b in bars] == [o.strip() for o in out] and _differs(bars, out) else None


def n3_punctuation(bars, rng, pool=None):
    out = [b.rstrip(".,!?") + ("," if i % 2 == 0 else "") for i, b in enumerate(bars)]
    return out if _differs(bars, out) else None


KINDS: dict[str, Callable] = {
    "D1": d1_wrong_end_word, "D2": d2_shuffle_within, "D3": d3_swap_across, "D4": d4_filler_frame, "D5": d5_noun_stack,
    "D6": d6_payoff_deleted, "D7": d7_cliche_template, "D8": d8_persona_break, "D9": d9_specificity_wash,
    "D10": d10_explain_joke, "D11": d11_moral_ending, "D12": d12_telegraphic, "D13": d13_dangling_pronoun,
    "D14": d14_americanism, "D15": d15_invented_word, "D16": d16_interleave,
    "N1": n1_synonym_swap, "N2": n2_whitespace_case, "N3": n3_punctuation,
}
NULL = {"N1", "N2", "N3"}
# measure classes each kind should move: sound | sense | grammar | referent | stance | specificity | structure
EXPECT = {
    "D1": {"moves": {"sense"}, "keeps": {"sound"}}, "D2": {"moves": {"sense", "structure"}, "keeps": set()},
    "D3": {"moves": {"sense", "structure", "sound"}, "keeps": set()}, "D4": {"moves": {"sense"}, "keeps": {"sound"}},
    "D5": {"moves": {"sense", "grammar"}, "keeps": set()}, "D6": {"moves": {"sense", "structure"}, "keeps": set()},
    "D7": {"moves": {"sense", "specificity"}, "keeps": {"sound", "grammar"}}, "D8": {"moves": {"stance"}, "keeps": {"sound", "grammar"}},
    "D9": {"moves": {"specificity"}, "keeps": {"sound", "grammar"}}, "D10": {"moves": {"sense", "stance"}, "keeps": set()},
    "D11": {"moves": {"stance"}, "keeps": set()}, "D12": {"moves": {"grammar"}, "keeps": set()},
    "D13": {"moves": {"referent"}, "keeps": {"sound"}}, "D14": {"moves": {"stance"}, "keeps": {"grammar"}},
    "D15": {"moves": {"grammar"}, "keeps": {"sound"}}, "D16": {"moves": {"sense", "structure"}, "keeps": set()},
    "N1": {"moves": set(), "keeps": {"sound", "sense", "grammar"}}, "N2": {"moves": set(), "keeps": {"sound", "sense", "grammar"}},
    "N3": {"moves": set(), "keeps": {"sound", "sense", "grammar"}},
}


def degrade(kind: str, bars: list[str], seed: int = 0, pool: Optional[list[list[str]]] = None) -> Optional[list[str]]:
    out = KINDS[kind](list(bars), rng_for(seed, bars, kind), pool)
    return out


def variants(bars: list[str], seed: int = 0, pool: Optional[list[list[str]]] = None, kinds=None) -> dict[str, list[str]]:
    res = {}
    for k in (kinds or KINDS):
        v = degrade(k, bars, seed, pool)
        if v is not None:
            res[k] = v
    return res


def selftest() -> tuple[bool, str]:
    problems: list[str] = []
    bars = ["Said cheers at the beer garden in Porto", "Paid the bloke fifty quid in Bristol", "Lost my bag at the airport in Spain",
            "Then I caught a plane out to Bilbao"]
    pool = [["Cheers to the lads in Leeds tonight", "The bouncer changed his mind quite quickly", "My cousin in Cardiff brought that back for me",
             "Say I am out in Dundee"]]
    got = variants(bars, 1, pool)
    for k in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16"):
        if k not in got:
            problems.append(f"{k} did not apply to a text it should apply to")
    for k, v in got.items():
        if v == bars:
            problems.append(f"{k} returned the input unchanged")
    if "D1" in got:
        changed = [(a, b) for a, b in zip(bars, got["D1"]) if a != b]
        if len(changed) != 1 or bridge.rhyme_score(changed[0][0], changed[0][1]) < 0.9:
            problems.append(f"D1 must change exactly one bar and keep the rhyme: {changed}")
    if variants(bars, 1, pool) != got:
        problems.append("degradation is not deterministic")
    if "D14" in got and "Bristol" not in "".join(got["D14"]):
        problems.append("D14 destroyed a proper noun")
    if "N1" in variants(["Nothing to swap here at all"], 0):
        problems.append("N1 must not apply when no synonym is present")
    return (not problems, "; ".join(problems) if problems else f"{len(got)} degradation kinds apply, deterministic, D1 keeps the rhyme")
