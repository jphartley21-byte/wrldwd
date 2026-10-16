"""rapfit: does this pair of bar endings rhyme the way it sounds WHEN RAPPED, not only on paper?   (a RANKING layer; status UNVALIDATED, ww/registry.py)

WHY IT EXISTS (Joe, 13 Oct 2026): the repo's grader (toolkit/phon.py + match.best_end, frozen, calibrate-protected) credits pairs that technically rhyme and
do not sound like a rhyme on the beat. Measured: "audit / biscuit / credit / orbit" and "limit / jacket / pocket / knit" graded 28/28 PERFECT in draft 8 because
the grader accepts a bare unstressed "-it" as a one-syllable rhyme, while the four stressed vowels (ɔː, ɪ, e, ɔː) all differ. In rap the rhyme lives on the syllables
that land on the beat; an unstressed tail echo is not heard as a rhyme. Reweighting the frozen grader failed twice (it broke the original's own checks), so this is a
separate layer that never edits it.

WHAT IT MEASURES (all from British phones through phon.syllables; no lyrics, no model):
  anchor      the rime starts at the LAST STRESSED syllable (that is where the beat falls). A bar that ends on a full vowel after it (Porto / though,
              Tobago / home) also offers the FINAL syllable as a second anchor, at a small discount: the ear hears the closing diphthong.
  stressed    vowel match (phon.vsim: height/backness/rounding, closing diphthongs by their glide) and coda match (consonant classes, from the right).
              Assonance counts: the original's carpets are vowel-led (goose/cruise/suit/do/shoot/through) and rate well by design.
  tail        the syllables after the anchor. Matching tails (favours/flavours, Lagos/Vegas) are a multisyllabic rhyme and earn a bonus; a tail on only one side
              (day / waiter) costs a little (masculine against feminine lands on a different beat).
  cap         if the stressed vowels do not match (< 0.55) the pair cannot exceed 0.30: a tail echo is not a rhyme.
Flags are reported beside the number: IDENTICAL word, TAIL-ONLY (the grader says rhyme, this says no), CHEAP (both sides on a rime >= CHEAP_FAMILY
dictionary words share).

THE PAIR SCORE ANSWERS "DO THESE RHYME?", NOT "IS THIS A GOOD RHYME" (15 Oct 2026). An identical, common rime scores 1.0, so a block of
me / we / free / tea / three / fee outscored the original, and Joe heard the original's end rhymes as better. Quality is BLOCK-level
(quality_of / quality_hard, HARD in check_block, numbers per slot in benchmark/rhyme_quality_targets.json, the original passes by
construction):
  carpet     end pairs whose ENDINGS match syllable by syllable from the end (chain_best depth >= 1) >= 85% of the original's: its
             Hook 5-8 rhymes all four bars on one ending (Lagos / favours / flavours / Vegas); people / solid / wallet / sequel and then
             posse / solid / wallet / copy passed while the scheme said ABBA and the pair score heard a shared vowel as a rhyme
  cheap      rhyming bars on a rime >= 150 dictionary words share, at most the original's count + 1
  identical  identical-rime pairs inside a family (toolkit/match.MANUAL_SCHEME), at most the original's count + 1
Joe's complaints are test cases: toolkit/tests/rhyme_complaints.txt (complaints_selftest).

HONEST LIMITS: the only ear-labelled pairs in the repo are the original's by-ear scheme (positives: same letter; negatives: different letter; Hook 5-8 is AAAA since 15 Oct 2026) and the 12 pairs in
toolkit/tests/rhyme_pairs.txt. None of them is a "technically rhymes but sounds flat" pair, so the cap cannot be fitted, only checked for not breaking those
labels. The pairs it demotes need Joe's ear: `python -m ww.cli rapfit --labels` writes the sheet.
"""
from __future__ import annotations

import collections
import itertools
import re
from functools import lru_cache

from .. import bridge

WEAK = {"ə", "ɪ", "i"}
# rapfit has its OWN scale (true rhymes in the original: median 0.74, quartiles 0.60-0.84; its non-rhymes: median 0.05). FLOOR is the single threshold that best
# separates Joe's by-ear pairs for the original: recall 91%, non-rhymes accepted 6% (Youden J 0.85, IN-SAMPLE on 274 pairs; the frozen grader at its 0.78 floor:
# recall 93%, accepted 28%). STRONG is where a pair is clearly a perfect-sounding rhyme. Neither is validated out of sample.
FLOOR = 0.50
STRONG = 0.80
GRADER_FLOOR = 0.78
FINAL_ANCHOR_DISCOUNT = 0.92
CLITIC_PRON = {"it", "him", "her", "them", "em", "'em", "us", "me", "you"}
WEAK_FORM = {"me": "i", "you": "ə", "her": "ə", "them": "ə", "em": "ə", "'em": "ə", "us": "ə", "him": "ɪ", "it": "ɪ"}
# a function word that carries the line's last stress when a pronoun closes the line ("for me", "to you", "at him")
STRONG_FORM = {"for": "ɔː", "to": "uː", "at": "æ", "from": "ɒ", "of": "ɒ", "on": "ɒ", "with": "ɪ", "and": "æ", "as": "æ", "than": "æ"}
# BLOCK-LEVEL RHYME QUALITY (15 Oct 2026; Joe: "originals end rhymes are better rn", then the Lagos/favours/flavours/Vegas carpet).
# The pair score says whether two endings rhyme; it scores an identical, common rime 1.0, so a block of me/we/free/tea/three/fee
# outscored the original. These three are measured per slot against the original (benchmark/rhyme_quality_targets.json):
CHEAP_FAMILY = 150      # a rime shared by >= 150 dictionary words is CHEAP: the 38 commonest of 45,529 rimes, 8% of the dictionary
CARPET_SHARE = 0.85     # end pairs heard (score >= FLOOR) must reach 85% of the original's count for the slot (the 12 Oct carpet rule)
QUALITY_SLACK = 1       # cheap bars and identical-rime pairs may exceed the original's count by one (the title's "guy" lands once)


# words as they are SUNG on the original, where the dictionary says otherwise (Joe's ear: luego rhymes with Tobago, Mainz with Spain)
SUNG = {"luego": "L W EY1 G OW0", "mainz": "M EY1 N Z",
        "chicas": "CH IY1 K AH0 Z",                                    # the dictionary guess gave the second syllable a full vowel
        "transatlantic": "T R AE2 N Z AE2 T L AE1 N T IH0 K"}        # trans-AT-LAN-tic: all three syllables are the same full vowel as delivered


def _phon():
    bridge._toolkit_on_path()
    bridge._pron_ready()          # teaches the toolkit the words only ww knows (loanwords, names): without it 'chicas' has no syllables at all
    import rhyme_tools
    for w, a in SUNG.items():
        rhyme_tools.OVR[w] = a
    import phon
    return phon


@lru_cache(maxsize=None)
def _syl(text: str) -> tuple:
    try:
        p = _phon()
        out = []
        # per WORD, so each syllable can say whether another syllable of its word follows (4th field). The toolkit's syllables attach every consonant before the next
        # vowel to the PREVIOUS syllable ('por' = ɔː+n, 'Bor' = ɔː+d), but the ear hears por-no / bor-DOH as the same open /ɔː/ + a new onset.
        # A clitic pronoun after another word is unstressed (15 Oct 2026): the dictionary stresses every monosyllable, so a tail such as
        # <stressed ae syllable> + "him" anchored on "him" and the original's own three-syllable V1 17-24 rhymes scored 0.06 a pair.
        # Destressed: by-ear AUC 0.932 -> 0.943, recall 90.5% -> 93.4%, non-rhymes accepted unchanged at 5.1%.
        # 16 Oct 2026 (Joe, the original's bars 46-50 against ours): a destressed pronoun also takes its WEAK VOWEL ('me' = /i/, as in the
        # last syllable of 'naughty'), and a small function word straight before one takes its STRONG form and the stress ('for me' = /fɔː mi/).
        # Before this, 'caught me' kept the stressed /iː/ of 'me', so the tools heard it rhyme with 'Seedy' on the 'ee' alone and did not hear
        # the original's word + 'me' endings rhyme with its own 'forty' / 'naughty' bars.
        ws = re.findall(r"[A-Za-z'å]+", text.replace("å", "a").replace("-", " "))
        for wi, w in enumerate(ws):
            sy = p.syllables(w)
            lw = w.lower()
            weak = wi > 0 and lw in CLITIC_PRON and len(sy) == 1
            strong = (lw in STRONG_FORM and len(sy) == 1 and wi + 1 < len(ws) and ws[wi + 1].lower() in CLITIC_PRON
                      and wi + 1 == len(ws) - 1)
            for k, (v, st, c) in enumerate(sy):
                if weak:
                    v = WEAK_FORM.get(lw, v)
                elif strong:
                    v, st = STRONG_FORM[lw], True
                out.append((v, bool(st) and not weak, tuple(c), k < len(sy) - 1))
        return tuple(out)
    except Exception:    # noqa: BLE001 - unpronounceable text has no syllables
        return ()


def _codasim(ca: tuple, cb: tuple) -> float:
    if ca == cb:
        return 1.0
    p = _phon()
    sims = []
    for x, y in itertools.zip_longest(reversed(ca), reversed(cb)):
        sims.append(0.35 if (x is None or y is None) else p.csim(x, y))
    return sum(sims) / len(sims)


def _coda_sim_syl(x: tuple, y: tuple) -> float:
    """ending similarity of two syllables, AMBISYLLABIC: where another syllable of the word follows, its last consonant may really be that syllable's onset
    (por-no, bor-deaux, fa-vours, la-gos), so the better of 'consonant in the ending' and 'consonant belongs to the next syllable' counts."""
    best = _codasim(x[2], y[2])
    xi = len(x) > 3 and x[3]
    yi = len(y) > 3 and y[3]
    if xi or yi:
        best = max(best, _codasim(x[2][:-1] if xi else x[2], y[2][:-1] if yi else y[2]))
    return best


def _anchors(sy: tuple) -> list[tuple[int, bool]]:
    """[(index, is_secondary)] where the rime may start."""
    idx = [i for i, s in enumerate(sy) if s[1]]
    out: list[tuple[int, bool]] = []
    if idx:
        out.append((idx[-1], False))
    last = len(sy) - 1
    if last >= 0 and sy[last][0] not in WEAK and (not out or out[-1][0] != last):
        out.append((last, True))
    if not out and last >= 0:
        out.append((last, False))
    return out


def _core(a: tuple, b: tuple) -> tuple[float, bool]:
    """(score, tail_matched) for rimes a, b (syllable tuples that start on the anchor)."""
    p = _phon()
    sv = p.vsim(a[0][0], b[0][0])
    if sv < 0.55:
        return 0.30 * sv, False                                   # the stressed vowels do not rhyme: a tail echo is not a rhyme
    sc = _codasim(a[0][2], b[0][2])          # the PAIR SCORE keeps the strict ending: it ranks Joe's by-ear pairs better (AUC 0.931 vs 0.917 ambisyllabic)
    ta, tb = a[1:], b[1:]
    if ta and tb:
        k = min(len(ta), len(tb))
        sims = []
        for x, y in zip(ta[:k], tb[:k]):
            v = 0.85 if (x[0] in WEAK and y[0] in WEAK) else p.vsim(x[0], y[0])
            sims.append(0.5 * v + 0.5 * _codasim(x[2], y[2]))
        st = sum(sims) / k
        matched = sum(1 for s in sims if s >= 0.85)
        # a multisyllabic rime is carried by the vowel and the TAIL together, so a differing consonant inside it (global/mogul) costs less
        total = 0.45 * sv + 0.20 * sc + 0.35 * st + 0.04 * min(2, matched) - 0.08 * abs(len(ta) - len(tb))
        return max(0.0, min(1.0, total)), matched > 0
    total = 0.60 * sv + 0.40 * sc - 0.08 * (len(ta) + len(tb))   # masculine against feminine lands on a different beat
    return max(0.0, min(1.0, total)), False


_FAMILY_INDEX: dict = {}


def _rime_ph(ph: list) -> tuple:
    """the dictionary rime from the last primary stress (else secondary, else the last vowel), British R-drop, an unstressed
    ER read as schwa (British -er = -a), stress digits stripped."""
    import rhyme_tools as rt
    ph = rt.uk(ph)
    idx = [i for i, x in enumerate(ph) if x.endswith("1")] or [i for i, x in enumerate(ph) if x.endswith("2")] or \
        [i for i, x in enumerate(ph) if x[-1] in "012"]
    if not idx:
        return ()
    t = ph[idx[-1]:]
    return tuple("AH" if (x.startswith("ER") and x.endswith("0")) else rt.strip(x) for x in t)


def _family_index() -> dict:
    if not _FAMILY_INDEX:
        _phon()
        import rhyme_tools as rt
        cnt: collections.Counter = collections.Counter()
        for w, prons in rt.D.items():
            if w.isalpha():
                k = _rime_ph(list(prons[0]))
                if k:
                    cnt[k] += 1
        _FAMILY_INDEX.update(cnt)
    return _FAMILY_INDEX


@lru_cache(maxsize=None)
def rime_family(text: str):
    """how many dictionary words share this ending's rime (from its last stressed syllable; a clitic pronoun after a word is
    unstressed, so 'having him' keeps its rime on the stressed syllable and has a family of 0: a mosaic). None = unpronounceable."""
    _phon()
    import rhyme_tools as rt
    ph = []
    for k, w in enumerate(re.findall(r"[A-Za-z']+", text.replace("-", " "))):
        p = rt.pron(w)
        if not p:
            return None
        if k > 0 and w.lower() in CLITIC_PRON:
            p = [x[:-1] + "0" if x[-1] in "12" else x for x in p]
        ph += p
    k = _rime_ph(ph)
    return _family_index().get(k, 0) if k else None


def rime_key(text: str):
    """the heard rime (British syllables from the last stressed one: vowel + ending each); equal keys = an IDENTICAL rime."""
    sy = _syl(text)
    if not sy:
        return None
    i = _anchors(sy)[0][0]
    return tuple((x[0], tuple(x[2])) for x in sy[i:])


def cheap(text: str) -> bool:
    f = rime_family(text)
    return f is not None and f >= CHEAP_FAMILY


def score(a: str, b: str) -> dict:
    """{'score', 'multi', 'flags'} for two bar-ending texts."""
    A, B = _syl(a), _syl(b)
    if not A or not B:
        return {"score": 0.0, "multi": False, "flags": ["UNPRONOUNCEABLE"]}
    best, multi = 0.0, False
    for ia, sa in _anchors(A):
        for ib, sb in _anchors(B):
            s, m = _core(A[ia:], B[ib:])
            if sa or sb:
                s *= FINAL_ANCHOR_DISCOUNT
            if s > best:
                best, multi = s, m
    flags = []
    if a.strip().lower() == b.strip().lower():
        flags.append("IDENTICAL")
    try:
        base = bridge.rhyme_score(a, b)
    except Exception:    # noqa: BLE001
        base = 0.0
    if base >= GRADER_FLOOR and best < FLOOR:
        flags.append("TAIL-ONLY")
    if best >= FLOOR and cheap(a) and cheap(b):
        flags.append("CHEAP")
    return {"score": round(best, 2), "multi": multi, "flags": flags, "grader": round(base, 2)}


def selftest() -> tuple[bool, str]:
    problems = []

    def s(a, b):
        return score(a, b)["score"]
    if s("audit", "biscuit") >= FLOOR or s("credit", "orbit") >= FLOOR:
        problems.append(f"a bare unstressed -it must not rhyme: audit~biscuit {s('audit', 'biscuit')}, credit~orbit {s('credit', 'orbit')}")
    if "TAIL-ONLY" not in score("audit", "biscuit")["flags"]:
        problems.append("audit~biscuit should be flagged TAIL-ONLY (the grader says perfect)")
    for a, b in (("favours", "flavours"), ("Lagos", "Vegas"), ("fox", "box"), ("debt", "vet"), ("global", "mogul"), ("goose", "cruise"), ("Porto", "though")):
        if s(a, b) < FLOOR:
            problems.append(f"{a}~{b} should rhyme: {s(a, b)}")
    if s("ferry", "Mary") < FLOOR or s("gammon", "hammer") < FLOOR:
        problems.append("near-vowel and consonant-variant pairs the original also uses should still rhyme")
    if s("fox", "fox") < 0.95 or "IDENTICAL" not in score("fox", "fox")["flags"]:
        problems.append("identical words are flagged, not hidden")
    if s("day", "waiter") >= s("day", "way"):
        problems.append("masculine~feminine should cost something against a plain masculine pair")
    problems += depth_selftest()
    c = chain_best(_syl("Dublin"), _syl("double it"))
    if c["depth"] < 2:
        problems.append(f"Dublin / double it share a syllabic-l rime and should reach depth 2: {c}")
    # 15 Oct 2026: this used the four Hook 1-4 bars once called "Joe's accepted hook" (Joe: never approved, never a bar or a gate
    # again). A Hook 1-4 that passes the slot checker stands in.
    cb = check_block("Hook 1-4", ["Kaixo I'm famous", "Front page in Bilbao: an invasion", "Bern Perth Crete Cairns and it's the same game",
                                  "My file's two foot thick a real cold case"])
    anchor_hard = [h for h in cb["hard"] if not h.startswith(("carpet:", "cheap:", "identical:"))]
    if anchor_hard:
        problems.append(f"a Hook 1-4 that passes the slot checker must pass the stress-anchor gate: {anchor_hard}")
    if not any(h.startswith("carpet:") for h in cb["hard"]):
        problems.append("famous / invasion / game / case share the stressed vowel but not the ending: the carpet must fail it")
    bad = check_block("V1 17-24", ["Audit", "Biscuit", "Credit", "Orbit", "Limit", "Jacket", "Pocket", "Knit"])
    if not bad["hard"]:
        problems.append("a block of bare -it endings must fail the stress-anchor gate")
    k = rime_key("packaged him")
    if not k or k[0][0] != "æ" or (rime_family("packaged him") or 0) > 5:
        problems.append(f"a clitic pronoun after a word is unstressed: 'packaged him' must rhyme from its stressed æ and be a rare (mosaic) rime: {k}")
    if not cheap("free") or cheap("favours"):
        problems.append("free (a rime hundreds of words share) is CHEAP and favours is not")
    problems += complaints_selftest()
    return (not problems, "; ".join(problems) if problems else "bare -it tails demoted and flagged; favours~flavours, Lagos~Vegas, fox~box, goose~cruise, Porto~though all rhyme; masculine~feminine costs a little")


# ------------------------------------------------------------------ evaluation against Joe's ear

def ear_pairs() -> list[dict]:
    """labelled pairs from the original's BY-EAR scheme (slotcheck.spec): same letter = rhymes (1), different letter or a lone letter = does not (0).
    Read from the private file; only isolated end words are ever printed, nothing is written."""
    from . import rhymeview, slotcheck
    orig = rhymeview.load_original()
    out = []
    for slot, bars in orig.items():
        # until 15 Oct 2026 Hook 5-8 was ABBA (closest partner), so Lagos~favours was a "does not rhyme" label although Joe hears the
        # whole block as one rhyme; it is AAAA now (toolkit/match.MANUAL_SCHEME)
        scheme = slotcheck.spec(slot)["scheme"]
        if len(scheme) != len(bars):
            continue
        tails = [rhymeview.tail_text(b.split()) for b in bars]
        for i, j in itertools.combinations(range(len(bars)), 2):
            same = scheme[i] == scheme[j] and scheme.count(scheme[i]) >= 2
            out.append({"slot": slot, "i": i, "j": j, "a": tails[i], "b": tails[j], "y": 1 if same else 0})
    return out


def _auc(pos: list[float], neg: list[float]) -> float:
    if not pos or not neg:
        return float("nan")
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def evaluate(verbose: bool = True) -> dict:
    pairs = ear_pairs()
    floors = {"base": GRADER_FLOOR, "rap": FLOOR}
    for p in pairs:
        p["base"] = float(bridge.rhyme_score(p["a"], p["b"]))
        p["rap"] = score(p["a"], p["b"])["score"]
    res = {"n": len(pairs), "pos": sum(p["y"] for p in pairs)}
    for name in ("base", "rap"):
        pos = [p[name] for p in pairs if p["y"]]
        neg = [p[name] for p in pairs if not p["y"]]
        res[name] = {"auc": round(_auc(pos, neg), 3), "recall": round(sum(v >= floors[name] for v in pos) / len(pos), 3),
                     "false_accept": round(sum(v >= floors[name] for v in neg) / len(neg), 3)}
    # leave-one-slot-out is moot for a model with no fitted weights; per-slot AUC shows where each scorer is blind
    res["by_slot"] = {}
    for slot in dict.fromkeys(p["slot"] for p in pairs):
        ps = [p for p in pairs if p["slot"] == slot]
        res["by_slot"][slot] = {n: round(_auc([p[n] for p in ps if p["y"]], [p[n] for p in ps if not p["y"]]), 2) for n in ("base", "rap")}
    res["rap_misses"] = [(p["slot"], p["a"].split()[-1], p["b"].split()[-1], p["rap"], p["base"]) for p in pairs if p["y"] and p["rap"] < FLOOR]
    res["rap_false"] = [(p["slot"], p["a"].split()[-1], p["b"].split()[-1], p["rap"], p["base"]) for p in pairs if not p["y"] and p["rap"] >= FLOOR]
    res["base_false"] = [(p["slot"], p["a"].split()[-1], p["b"].split()[-1], p["rap"], p["base"]) for p in pairs if not p["y"] and p["base"] >= GRADER_FLOOR]
    if verbose:
        print(f"BY-EAR LABELS from the original: {res['n']} pairs, {res['pos']} rhyme / {res['n'] - res['pos']} do not (Joe's by-ear scheme: toolkit/match.MANUAL_SCHEME)")
        for name, label in (("base", "grader (match.best_end, frozen)"), ("rap", "rapfit (new layer)")):
            r = res[name]
            print(f"  {label:34} AUC {r['auc']:.3f} | recall of true rhymes {r['recall']:.0%} | non-rhymes wrongly accepted {r['false_accept']:.0%}")
        print("  per-slot AUC (grader / rapfit): " + "; ".join(f"{s} {v['base']}/{v['rap']}" for s, v in res["by_slot"].items()))
    return res


# ------------------------------------------------------------------ the sheet only Joe's ear can fill in

def label_sheet(draft_path: str, out_path: str, max_tech: int = 24) -> dict:
    """Pairs from OUR draft, written as a markdown table for Joe to mark (rhymes when rapped? y / n / meh). Three kinds, shuffled by id so the kind is not
    obvious: TECH (the grader accepts, rapfit does not hear it), BORDER (rapfit 0.50-0.70) and STRONG controls (rapfit >= 0.90 and the grader agrees).
    Only our own words are written."""
    import random
    from . import rhymeview
    secs = rhymeview.load_draft(draft_path)
    seen, tech, border, strong = set(), [], [], []
    for slot, bars in secs.items():
        tails = [rhymeview.tail_text(b.split()) for b in bars]
        lab = rhymeview._group_grader(tails)
        for g in {x for x in lab if x is not None}:
            mem = [i for i, x in enumerate(lab) if x == g]
            for i, j in itertools.combinations(mem, 2):
                a, b = tails[i], tails[j]
                if a == b or (a, b) in seen or (b, a) in seen:
                    continue
                seen.add((a, b))
                r = score(a, b)
                row = {"slot": slot, "a": a, "b": b, "rap": r["score"], "grader": r["grader"]}
                if "TAIL-ONLY" in r["flags"]:
                    tech.append(row)
                elif FLOOR <= r["score"] < 0.70:
                    border.append(row)
                elif r["score"] >= 0.90 and r["grader"] >= GRADER_FLOOR:
                    strong.append(row)
    rnd = random.Random(13)
    pick = lambda xs, n: rnd.sample(xs, min(n, len(xs)))
    rows = [dict(r, kind="TECH") for r in pick(tech, max_tech)] + [dict(r, kind="BORDER") for r in pick(border, 8)] + [dict(r, kind="STRONG") for r in pick(strong, 8)]
    rnd.shuffle(rows)
    L = ["# Does this rhyme when it is RAPPED? (ear sheet for rapfit)", "",
         "Say each pair on the beat. Mark **y** = it sounds like a rhyme, **n** = it only rhymes on paper, **m** = meh / borderline. Nothing here is a verdict until you mark it.",
         "The kind of pair is hidden on purpose. Your marks become the labels that set rapfit's floor and test whether it favours what sounds good.", "",
         "| id | slot | pair | your ear (y / n / m) |", "|---|---|---|---|"]
    for k, r in enumerate(rows, 1):
        L.append(f"| {k} | {r['slot']} | {r['a']} ~ {r['b']} | |")
    L += ["", "<!-- answer key, do not read before marking: " + "; ".join(f"{k}={r['kind']}(rap {r['rap']}, grader {r['grader']})" for k, r in enumerate(rows, 1)) + " -->"]
    from pathlib import Path
    Path(out_path).write_text("\n".join(L) + "\n", encoding="utf-8")
    return {"tech": len(tech), "border": len(border), "strong": len(strong), "written": len(rows), "path": out_path}


# ------------------------------------------------------------------ syllable-level matching (the unit a rapper hears)

SHORT = {"ɪ", "e", "æ", "ʌ", "ɒ", "ʊ"}


def syl_match(x: tuple, y: tuple) -> int:
    """2 = same vowel AND coda (the syllables rhyme), 1 = same vowel only (assonance), 0 = different.  x, y = (vowel, stressed, coda)."""
    p = _phon()
    sv = p.vsim(x[0], y[0])
    if 0.9 <= sv < 0.99:
        return 1                     # a near vowel that shares a glide (aɪ ~ eɪ: eye ~ ba) is assonance, never an exact rime
    if sv < 0.9:
        # a NEAR stressed vowel with a matching ending still rhymes by ear (ferry / Mary: e ~ eə; Holtman: vowels that differ only slightly in height or length)
        return 1 if (sv >= 0.62 and (x[1] or y[1]) and _coda_sim_syl(x, y) >= 0.75) else 0
    return 2 if _coda_sim_syl(x, y) >= 0.75 else 1


def long_vowel(v: str) -> bool:
    """long monophthong or diphthong (iː uː ɑː ɔː ɜː eɪ aɪ ɔɪ əʊ aʊ ɪə eə ʊə): the ear still leans on it when it is unstressed (bonjourNO, tobaGO)."""
    return bool(_phon().V.get(v, (0, 0, 0, 0))[3])


def prominent(s: tuple) -> bool:
    """a syllable a rapper puts weight on: stressed, or ANY full vowel (trans-at-LAN-tic is delivered four-square, so the unstressed full 'æ' of 'trans' counts). Only the
    reduced vowels (ə, ɪ, i) do not: the 'it' of biscuit / credit is a tail, not a rhyme."""
    return bool(s[1]) or s[0] not in WEAK


def chain(A: tuple, B: tuple) -> dict:
    """syllable-by-syllable match from the END of two tails. {'states': [2|1 ...] from the last syllable backwards, 'depth', 'echo'}.
    depth = length of the matching run IF it reaches a prominent syllable (a real rhyme); echo = the run's length when it does NOT
    (an unstressed tail echo: biscuit / credit share only the 'it')."""
    states = []
    for k in range(1, min(len(A), len(B)) + 1):
        m = syl_match(A[-k], B[-k])
        if m == 0:
            break
        states.append(m)
    prom = any(prominent(A[-1 - k]) or prominent(B[-1 - k]) for k in range(len(states)))
    return {"states": states, "depth": len(states) if prom else 0, "echo": 0 if prom else len(states)}


def depth_selftest() -> list[str]:
    problems = []

    def c(a, b):
        return chain(_syl(a), _syl(b))
    r = c("audit", "biscuit")
    if r["depth"] != 0 or r["echo"] != 1:
        problems.append(f"audit/biscuit should be a 1-syllable tail echo only: {r}")
    r = c("favours", "flavours")
    if r["depth"] != 2 or r["states"] != [2, 2]:
        problems.append(f"favours/flavours should be a 2-syllable full rhyme: {r}")
    if c("luego", "Tobago")["depth"] < 1:
        problems.append("luego/Tobago share a full closing vowel and should count as a rhyme")
    if c("fox", "box")["depth"] != 1:
        problems.append("fox/box is a 1-syllable stressed rhyme")
    r = c("porno", "Bordeaux")
    if r["depth"] != 2 or r["states"] != [2, 2]:
        problems.append(f"por-no / bor-deaux are the same open vowel then the same closing vowel (the n/d belong to the next syllable): {r}")
    r = c("Lagos", "favours")
    if r["depth"] != 2:
        problems.append(f"Lagos / favours are a two-syllable rhyme: {r}")
    if syl_match(_syl("eye")[0], _syl("plain")[0]) == 2:
        problems.append("eye (aɪ) and plain (eɪ) share a glide but are not an exact rime")
    if syl_match(_syl("plain")[0], _syl("plane")[0]) != 2:
        problems.append("plain / plane are homophones: an exact rime")
    sy = _syl("transatlantic")
    if [prominent(x) for x in sy] != [True, True, True, False]:
        problems.append(f"transatlantic: trans, at and lan carry full æ and tic is the weak tail: {[prominent(x) for x in sy]}")
    r = c("luego", "Tobago")
    if r["depth"] != 2:
        problems.append(f"luego (sung 'lway-go') and Tobago share eɪ then əʊ: {r}")
    return problems


# ------------------------------------------------------------------ the enforcement layer (13 Oct 2026, Joe: "placement and vowel type enforced during the writing process")

TARGETS_PATH = None


def _elide(sy: tuple) -> tuple:
    """syllabic l / n / m: a schwa that only carries l, n or m after a consonant is the end of the PREVIOUS syllable (double = dʌbl, not dʌ-bə-l), so
    'double it' (three dictionary syllables) can rhyme with 'Dublin' (two): move the consonant into the previous coda and drop the schwa syllable."""
    out: list = []
    for k, x in enumerate(sy):
        if k > 0 and x[0] == "ə" and not x[1] and x[2] and x[2][0] in ("l", "n", "m") and out and out[-1][2]:
            prev = out[-1]
            out[-1] = (prev[0], prev[1], tuple(prev[2]) + tuple(x[2])) + ((x[3],) if len(x) > 3 else ())
            continue
        out.append(x)
    return tuple(out)


def chain_best(A: tuple, B: tuple) -> dict:
    """chain() tried on the dictionary syllables and on the syllabic-consonant reading of each side; the deepest real rhyme wins."""
    best = None
    for a in {A, _elide(A)}:
        for b in {B, _elide(B)}:
            c = chain(a, b)
            key = (c["depth"], c["echo"])
            if best is None or key > best[0]:
                best = (key, c)
    return best[1]


def _targets() -> dict:
    global TARGETS_PATH
    from .. import config
    import json as _j
    p = config.BENCHMARK / "rhyme_depth_targets.json"
    return _j.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def write_depth_targets() -> dict:
    """numbers only (rule 4): for each slot of the ORIGINAL, the median rhyme depth (in syllables) of its end-rhyming bars, from Joe's by-ear groups."""
    import json as _j
    import statistics
    from .. import config
    from . import rhymeview
    orig = rhymeview.load_original()
    out = {}
    for slot, bars in orig.items():
        a = rhymeview.analyze({slot: bars}, ear=True)
        ds = [d for _, d, e in a["depths"] if d > 0]
        if ds:
            out[slot] = {"median_depth": int(statistics.median(ds)), "max_depth": max(ds), "bars": len(ds)}
    p = config.BENCHMARK / "rhyme_depth_targets.json"
    p.write_text(_j.dumps({"_note": "median rhyme depth in syllables of the original's end-rhyming bars per slot (rapfit.chain_best, Joe's by-ear groups); numbers only", **out}, indent=1), encoding="utf-8")
    return out


BAR_TARGETS = "rhyme_bar_targets.json"


def _tail_depth(a: str, b: str) -> int:
    from . import rhymeview
    return chain_best(_syl(rhymeview.tail_text(a.split())), _syl(rhymeview.tail_text(b.split())))["depth"]


@lru_cache(maxsize=1)
def _bar_targets() -> dict:
    from .. import config
    import json as _j
    p = config.BENCHMARK / BAR_TARGETS
    return _j.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def write_bar_targets() -> dict:
    """numbers only (rule 4), 16 Oct 2026: for each slot of the ORIGINAL, every bar's rhyme depth with its by-ear group (check_block's own unit),
    and the rhymes the original makes ACROSS a section break (the last two bars of a section against the first two of the next). Joe on the
    original's bars 46-52: one two-syllable ending held for five bars, straight through the break between V1 25-32 and V1 33-44."""
    import json as _j
    from .. import config
    from . import rhymeview, slotcheck
    orig = rhymeview.load_original()
    bars = {s: check_block(s, b)["depths"] for s, b in orig.items()}
    order = [n for n, _, _ in slotcheck.SECS]
    bnd = []
    for k in range(len(order) - 1):
        a, b = order[k], order[k + 1]
        A, B = orig.get(a), orig.get(b)
        if not A or not B:
            continue
        for i in (len(A) - 2, len(A) - 1):
            for j in (0, 1):
                d = _tail_depth(A[i], B[j])
                if d:
                    bnd.append({"a": a, "i": i, "b": b, "j": j, "depth": d})
    out = {"_note": "the ORIGINAL's per-bar end-rhyme depth with its by-ear group, and its rhymes across section breaks (rapfit, numbers only)",
           "bars": bars, "boundary": bnd}
    (config.BENCHMARK / BAR_TARGETS).write_text(_j.dumps(out, indent=1), encoding="utf-8")
    _bar_targets.cache_clear()
    return out


def boundary_hard(sections: dict) -> list[str]:
    """HARD (16 Oct 2026): where the original rhymes across a section break, ours must rhyme the same two bars at least as deep."""
    out = []
    from . import rhymeview
    for r in _bar_targets().get("boundary", []):
        A, B = sections.get(r["a"]), sections.get(r["b"])
        if not A or not B or len(A) <= r["i"] or len(B) <= r["j"]:
            continue
        d = _tail_depth(A[r["i"]], B[r["j"]])
        if d < r["depth"]:
            ea, eb = (rhymeview.tail_text(x.split()) or "?" for x in (A[r["i"]], B[r["j"]]))
            out.append(f"boundary: {r['a']} bar {r['i'] + 1} ('{ea}') ~ {r['b']} bar {r['j'] + 1} ('{eb}'): rhyme depth {d}; the original rhymes "
                       f"these two bars across the section break {r['depth']} syllable(s) deep (one ending carried over the break)")
    return out


QUALITY_PATH = "rhyme_quality_targets.json"


def quality_of(slot: str, bars: list[str]) -> dict:
    """the block's end-rhyme CARPET (end pairs whose endings chain from the end, chain_best depth >= 1, all pairs), its CHEAP bars (rhyming bars whose rime >=
    CHEAP_FAMILY dictionary words share) and its IDENTICAL-rime pairs (inside one rhyme family). Numbers and bar indices only."""
    from . import rhymeview, slotcheck
    fam = slotcheck.spec(slot)["scheme"]
    n = min(len(bars), len(fam))
    tails = [rhymeview.tail_text(b.split()) for b in bars[:n]]
    # a pair joins the carpet only when its ENDINGS match syllable by syllable from the end through a stressed or full syllable (the
    # unit check_block uses). The pair score alone heard a shared stressed vowel as a rhyme: posse ~ solid 0.66 although -ossy and
    # -olid end differently, so an ABBA block passed as AAAA (15 Oct 2026, Joe: "Why is hook 5-8 still ABBA when the original is AAAA?")
    syls = [_syl(t) for t in tails]
    heard = [(i, j) for i, j in itertools.combinations(range(n), 2) if chain_best(syls[i], syls[j])["depth"] >= 1]
    grouped = [i for i in range(n) if fam.count(fam[i]) >= 2]
    cheap_bars = [i for i in grouped if cheap(tails[i])]
    keys = [rime_key(t) for t in tails]
    ident = [(i, j) for i, j in itertools.combinations(grouped, 2) if fam[i] == fam[j] and keys[i] and keys[i] == keys[j]]
    return {"n": n, "pairs": n * (n - 1) // 2, "carpet": len(heard), "cheap": cheap_bars, "identical": ident, "tails": tails}


def _quality_targets() -> dict:
    import json as _j
    from .. import config
    p = config.BENCHMARK / QUALITY_PATH
    return _j.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def write_quality_targets() -> dict:
    """numbers only (rule 4): the ORIGINAL's carpet, cheap-bar count and identical-pair count per slot."""
    import json as _j
    from .. import config
    from . import rhymeview
    out = {}
    for slot, bars in rhymeview.load_original().items():
        q = quality_of(slot, bars)
        out[slot] = {"n": q["n"], "pairs": q["pairs"], "carpet": q["carpet"], "cheap": len(q["cheap"]), "identical": len(q["identical"])}
    p = config.BENCHMARK / QUALITY_PATH
    p.write_text(_j.dumps({"_note": "the original's end rhymes per slot (rapfit.quality_of): carpet = end pairs whose endings chain from the end, cheap = rhyming "
                           f"bars on a rime >= {CHEAP_FAMILY} dictionary words share, identical = identical-rime pairs inside a "
                           "family; numbers only", **out}, indent=1), encoding="utf-8")
    return out


def quality_hard(slot: str, bars: list[str]) -> list[str]:
    """HARD (15 Oct 2026): a full block may not fall below the original's carpet nor exceed its cheap and identical counts."""
    t = _quality_targets().get(slot)
    if not t:
        return []
    q = quality_of(slot, bars)
    if q["n"] != t["n"]:
        return []
    out = []
    ends = [x.split()[-1] if x else "?" for x in q["tails"]]
    need = int(CARPET_SHARE * t["carpet"])
    if q["carpet"] < need:
        out.append(f"carpet: {q['carpet']} of {q['pairs']} end pairs share their ending (matched syllable by syllable from the end), the "
                   f"original's {slot} holds {t['carpet']} (need >= {need}): a bar shares the stressed vowel but not the ending; give every bar "
                   "of the family the same ending, as Lagos / favours / flavours / Vegas do")
    cap = t["cheap"] + QUALITY_SLACK
    if len(q["cheap"]) > cap:
        out.append(f"cheap: {len(q['cheap'])} end rhymes on a rime hundreds of words share ({', '.join(ends[i] for i in q['cheap'])}); "
                   f"the original has {t['cheap']} here (max {cap}): use a rarer or multi-syllable rime")
    cap = t["identical"] + QUALITY_SLACK
    if len(q["identical"]) > cap:
        pairs = ", ".join(f"{ends[i]}/{ends[j]}" for i, j in q["identical"][:6])
        out.append(f"identical: {len(q['identical'])} pairs end on the identical rime ({pairs}{' ...' if len(q['identical']) > 6 else ''}); "
                   f"the original has {t['identical']} here (max {cap}): keep the vowel, vary what follows it")
    return out


def complaints_selftest() -> list[str]:
    """Joe's rhyme complaints (toolkit/tests/rhyme_complaints.txt) must each fire their named rule, and the original must pass
    every slot. Only counts are printed for the original."""
    from .. import config
    from . import rhymeview
    problems = []
    path = config.ROOT / "toolkit" / "tests" / "rhyme_complaints.txt"
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        slot, rules, text = line.split("\t")[:3]
        bars_ = [b.strip() for b in text.split(" / ")]
        hard = quality_hard(slot, bars_)
        # rules that live in check_block (16 Oct 2026): 'tail' = a bar rhymes with its group only on an unstressed tail; 'depth' = a bar
        # rhymes less deep than the original's same bar
        hard += check_block(slot, bars_)["hard"]
        for r in rules.split(","):
            if not any(h.startswith(r.strip() + ":") for h in hard):
                problems.append(f"{slot}: Joe's complaint should fail the '{r.strip()}' rule and does not ({'; '.join(h[:40] for h in hard) or 'no rhyme issue'})")
    orig = rhymeview.load_original()
    for slot, bars in orig.items():
        if quality_hard(slot, bars):
            problems.append(f"the original fails its own {slot} rhyme-quality targets")
        if check_block(slot, bars)["hard"]:
            problems.append(f"the original fails its own {slot} rhyme block rules (tail / depth)")
    if boundary_hard(orig):
        problems.append("the original fails its own rhymes across section breaks")
    # Joe (4), 16 Oct 2026: our V1 25-32 -> V1 33-44 blocks must also fail the rhyme across the section break
    rows = {l.split("\t")[0]: [b.strip() for b in l.split("\t")[2].split(" / ")] for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#") and "\ttail\t" in l}
    if {"V1 25-32", "V1 33-44"} <= set(rows) and not boundary_hard(rows):
        problems.append("Joe's V1 25-32 -> V1 33-44 complaint should fail the rhyme across the section break")
    return problems


def check_block(slot: str, bars: list[str]) -> dict:
    """STRESS-ANCHOR GATE for the writing process.
    HARD: inside every by-ear scheme group of 2+ bars, each bar must have at least one partner it rhymes with THROUGH A PROMINENT SYLLABLE (rime depth >= 1).
          A bar whose partners share only an unstressed tail ('-it' of biscuit / credit) or nothing fails: that is not a rhyme (rule R1, benchmark/rhyme_theory.md).
    SOFT: the bar's best depth is below the original's median for this slot."""
    from . import rhymeview, slotcheck
    hard, soft, depths = [], [], []
    try:
        scheme = slotcheck.spec(slot)["scheme"]
    except Exception:    # noqa: BLE001 - unknown slot: nothing to enforce
        return {"hard": [], "soft": [], "depths": [], "target": None}
    n = min(len(bars), len(scheme))
    tails = [rhymeview.tail_text(b.split()) for b in bars[:n]]
    syls = [_syl(t) for t in tails]
    tg = _targets().get(slot, {}).get("median_depth")
    for i in range(n):
        mates = [j for j in range(n) if j != i and scheme[j] == scheme[i]]
        if not mates:
            depths.append(None)
            continue
        cs = [chain_best(syls[i], syls[j]) for j in mates]
        d = max(c["depth"] for c in cs)
        e = max(c["echo"] for c in cs)
        depths.append(d)
        end = tails[i] if tails[i] else "?"
        if d == 0:
            if e:
                hard.append(f"tail: bar {i + 1} ('{end}'): rhymes with its group only on an unstressed tail ({e} syllable), the stressed syllables do not rhyme; a rhyme must start on a stressed syllable")
            else:
                # the tool hears NOTHING here. On the original that is mostly its own blind spots (loanwords, loose sections), so it is a check-by-ear note, not a veto.
                soft.append(f"bar {i + 1} ('{end}'): the tool hears no syllable match with its rhyme group ({scheme[i]}); check it by ear")
        elif tg and d < tg:
            soft.append(f"bar {i + 1} ('{end}'): rhyme depth {d} syllable(s); the original's median for {slot} is {tg}")
        # HARD (16 Oct 2026, Joe: "Can you see the difference in quality?"): no shallower than the ORIGINAL'S SAME BAR, measured the same way.
        # A tail-only bar already failed above; a bar the tool hears nothing in fails here when the original's bar rhymes.
        par_d = (_bar_targets().get("bars", {}).get(slot) or [])
        if len(par_d) == len(scheme) and i < len(par_d) and par_d[i] and d < par_d[i] and not (d == 0 and e):
            hard.append(f"depth: bar {i + 1} ('{end}'): rhyme depth {d} syllable(s) with its group; the original's bar here rhymes {par_d[i]} deep "
                        "(share the stressed vowel and everything after it, as the original's bar does)")
    # TEMPLATE / BLOCK RULES (Joe, 13 Oct 2026; measured on the original's V1 17-24: the stressed rhyme syllable sits at the same distance from the end in 4 of 4 bars of BOTH blocks)
    if tg and tg >= 2:
        for k in range(0, n - 3, 4):
            vals = [d for d in depths[k:k + 4] if d is not None]
            if len(vals) < 3:
                continue
            modal, cnt = collections.Counter(vals).most_common(1)[0]
            if cnt < 3:
                soft.append(f"bars {k + 1}-{k + 4}: the rhyme sits at different depths ({sorted(vals)}); a block should repeat ONE template, the same stressed syllable the same distance from the end in at least 3 of 4 bars")
            if tg >= 3 and sum(1 for d in vals if d >= 3) < 3:
                hard.append(f"bars {k + 1}-{k + 4}: {slot} is a 3-syllable slot (the original's bars 1-4 and 5-8 each end on one three-syllable rhyme in at least 3 of 4 bars); only {sum(1 for d in vals if d >= 3)} of these bars do")
    hard += quality_hard(slot, bars[:n])
    return {"hard": hard, "soft": soft, "depths": depths, "target": tg}


def internal_echo(bars: list[str]) -> dict:
    """REWARD (a ranking number in 0..1, not a gate): does the end rhyme's stressed vowel come back INSIDE the bar, and does it sit at about the same point in the next bar?
    Per 4-bar block: the end vowels are the full vowels of each bar's closing syllables; an internal echo is an earlier prominent syllable with one of them. Score = half the share of bars
    that have an echo + half the mean closeness of the echoes in ADJACENT bars, closeness = 1 - 4 x (distance between their positions as a share of the bar's syllables), floored at 0
    (one syllable apart in a ten-syllable bar = 0.6, two = 0.2)."""
    from . import rhymeview
    scores, detail = [], []
    for k in range(0, len(bars) - 3, 4):
        blk = bars[k:k + 4]
        sy = [_syl(rhymeview.tail_text(b.split())) for b in blk]
        endv = {x[0] for s_ in sy for x in s_[-3:] if prominent(x)}
        pos = []
        for b in blk:
            st = []
            for w in b.split():
                c = rhymeview.core(w)
                if c:
                    st += [(c, x) for x in _syl(c)]
            n = len(st)
            tail_n = len(_syl(rhymeview.tail_text(b.split())))
            pos.append([(i + 0.5) / n for i, (c, x) in enumerate(st[:max(0, n - tail_n)]) if prominent(x) and x[0] in endv])
        has = sum(1 for p in pos if p) / 4
        close = []
        for a, b2 in zip(pos, pos[1:]):
            close.append(max(0.0, 1 - 4 * min(abs(x - y) for x in a for y in b2)) if a and b2 else 0.0)
        sc = 0.5 * has + 0.5 * (sum(close) / len(close))
        scores.append(sc)
        detail.append({"bars": f"{k + 1}-{k + 4}", "echo_share": round(has, 2), "closeness": [round(c, 2) for c in close], "score": round(sc, 2)})
    return {"score": round(sum(scores) / len(scores), 3) if scores else 0.0, "blocks": detail}
