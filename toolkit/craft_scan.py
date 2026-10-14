"""craft_scan: three detectors for things the earlier tools missed, found by Joe reading the map.

1. BAR TAIL (across words). The old tail came from the FINAL WORD only, so a two-word tail was
   invisible: "plain clothes" and "plane home" showed as a single "oh" when the rhyme unit is
   "ay-oh" spanning both words. That two-word tail is the original's headline device in the hook.
2. TAIL FAMILIES. The scheme must be built on the two-syllable tail, with the STRESSED vowel free to
   drift (documented technique: "the stressed vowel drifts from er to or to i so it never goes
   stale"). The old scheme keyed on the last stressed vowel alone and so called an AAAA passage
   `abcc`. Here a family = same final vowel (or vsim >= .78) + penultimate vowel within .5.
3. INTERNAL RHYMES INSIDE THE BAR. The old measure only compared a bar's other stressed syllables
   with the END vowel, so an internal pair like the two halves of "Wagwan" was invisible.
4. ALLITERATION STRANDS. The old measure took word-INITIAL onsets of CONTENT words only, so it
   missed a function word pairing with a content word ("to"/"Tobago") and consonants inside a word
   ("boys"/"To-bago").

No lyric text is ever written out by this module: it reports vowels, words and scores only.
"""
import os
import private_path
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rhyme_tools import pron, is_v, strip, vsim, FUNC   # noqa: E402
sys.path.insert(0, HERE)
import helpers                                      # noqa: E402

# ARPAbet -> British IPA, so a cmudict fallback can still be compared with britfone
ARPA2IPA = {"AA": "ɑː", "AE": "æ", "AH": "ʌ", "AO": "ɔː", "AW": "aʊ", "AY": "aɪ", "EH": "e",
            "ER": "ɜː", "EY": "eɪ", "IH": "ɪ", "IY": "iː", "OW": "əʊ", "OY": "ɔɪ", "UH": "ʊ",
            "UW": "uː"}

# Words britfone (a citation dictionary) does not carry, with their real British/loan pronunciations.
# Two of these decide rhyme verdicts on the original's own lines, so they cannot be left to the
# American fallback. "wagwan" is patois: its internal rhyme (the two halves of the word) is a feature
# of the delivered form ɑː-ɑː, and the anglicised citation form "wæg-wɒn" would hide it.
BRIT_OVR = {
    "favours": "f ˈeɪ v ə z", "flavours": "f l ˈeɪ v ə z",
    "lagos": "l ˈeɪ ɡ ɒ s", "wagwan": "w ɑː ɡ w ˈɑː n", "luego": "l w ˈe ɡ əʊ",
}


def brit_phones(word):
    """British IPA for a word: the repo's britfone dictionary, a small override table for words it lacks,
    else the CMU plus OVR fallback. Uses helpers.uk_phones, the same resolver phon.py scores with, so a
    word is never measured with one pronunciation here and another there."""
    b = BRIT_OVR.get(word.lower())
    if b:
        return b.split()
    try:
        return helpers.uk_phones(word)
    except Exception:
        return None


def vowels_of(phones):
    out = []
    for p in phones or []:
        if any(c in "iɪeɛæʌɒʊəuɑɔɜa" for c in p):
            out.append(p.replace("ˈ", "").replace("ˌ", ""))
    return out


def brit_vowel(word, idx, us_vowel, us_stress):
    """The British vowel for a stressed nucleus.

    `idx` is the NUCLEUS ORDINAL (how many-th vowel this is in the word), not the phone index:
    indexing the British vowel list with the American phone index shifted every reading by the number
    of consonants before the vowel, so "Lagos" came out ɒ-ɑː instead of eɪ-ɒ.

    britfone is a citation dictionary: for a word cmudict stresses but britfone reduces to schwa (the
    function word "for" is `f ə`), the reduced form is not the form that rhymes, so the American
    strong form is used and mapped to IPA. Everything else takes the British vowel.
    """
    bv = vowels_of(brit_phones(word))
    if bv and idx < len(bv):
        v = bv[idx]
        if v == "ə" and us_stress in ("1", "2"):
            return ARPA2IPA.get(us_vowel, us_vowel)
        return v
    return ARPA2IPA.get(us_vowel, us_vowel)


def nuclei(bar):
    """Every vowel nucleus in the bar, in order:
    (word, index in the word, american vowel, stress, BRITISH vowel, coda after the vowel)."""
    out = []
    for w in re.findall(r"[A-Za-z']+", bar):
        ph = pron(w)
        if not ph:
            continue
        vcount = 0
        for i, p in enumerate(ph):
            if is_v(p):
                us = strip(p)
                stress = p[-1] if p[-1].isdigit() else "0"
                coda = "".join(strip(x) for x in ph[i + 1:] if not is_v(x)).lower()
                out.append((w, i, us, stress, brit_vowel(w, vcount, us, stress), coda))
                vcount += 1
    return out


def bar_tail(bar, n=2):
    """The bar's last n vowel nuclei, ACROSS word boundaries - the real rhyme unit."""
    v = nuclei(bar)
    tail = v[-n:] if len(v) >= n else v
    words = [x[0].lower() for x in tail]
    return {"vowels": [x[4] for x in tail], "arpa": [x[2] for x in tail], "words": words,
            "stress": [x[3] for x in tail], "coda": [x[5] for x in tail],
            "nuc": tail, "crosses_words": len(set(words)) > 1}


def tail_score(a, b):
    """Rhyme strength between two bar tails (lists of nuclei).

    The TAIL syllable carries the rhyme. An UNSTRESSED tail rhymes on its CODA once the vowel is
    reduced (Lagos/Vegas: -gos/-gas, both reduced), while a STRESSED tail rhymes on its vowel
    (clothes/home is therefore assonance, as the benchmark says). The stressed vowel in front may
    drift, as long as it stays in the same vowel class - the original's own technique.
    """
    if not a or not b:
        return 0.0
    fa, fb = a[-1], b[-1]
    va, vb, sa, sb = fa[4], fb[4], fa[3], fb[3]
    reduced = ("0",) if False else None
    both_unstressed = sa == "0" and sb == "0"
    if both_unstressed:
        s_final = 1.0 if fa[5] == fb[5] else (0.9 if va == vb else 0.5)
    else:
        s_final = 1.0 if va == vb else vsim(fa[2], fb[2])
    if len(a) < 2 or len(b) < 2:
        return s_final
    same_class = vclass(a[-2][4]) == vclass(b[-2][4])
    return s_final if same_class else s_final * 0.4


VCLASS = {}
for _v in "iː ɪ e eɪ æ".split():
    VCLASS[_v] = "front"
for _v in "ə ɜː ʌ".split():
    VCLASS[_v] = "central"
for _v in "ɑː ɒ ɔː əʊ ʊ uː".split():
    VCLASS[_v] = "back"
for _v in "aɪ ɔɪ aʊ".split():
    VCLASS[_v] = "diphthong"
for _v in "i e u æ".split():
    VCLASS.setdefault(_v, "front")
VCLASS["ə"] = "central"


def vclass(v):
    return VCLASS.get(v, "other")


def families(bars, threshold=0.78):
    """Group bars into rhyme families on the two-syllable tail. Returns (letters, reps, pairs)."""
    reps, letters, detail = [], [], []
    for bar in bars:
        t = bar_tail(bar)
        placed = False
        for i, r in enumerate(reps):
            s = tail_score(t["nuc"], r["nuc"])
            if s >= threshold:
                letters.append(chr(ord("A") + i))
                detail.append((bar, letters[-1], "-".join(r["vowels"]), "-".join(t["vowels"]), round(s, 2)))
                placed = True
                break
        if not placed:
            reps.append(t)
            letters.append(chr(ord("A") + len(reps) - 1))
            detail.append((bar, letters[-1], "-".join(t["vowels"]), "-".join(t["vowels"]), 1.0))
    return "".join(letters), reps, detail


def internal_pairs(bar, threshold=0.5):
    """Pairs of vowels INSIDE the bar that match, including internal-to-internal pairs."""
    v = nuclei(bar)
    st = [x for x in v if x[3] in ("1", "2")]
    out = []
    for i in range(len(st)):
        for j in range(i + 1, len(st)):
            s = vsim(st[i][2], st[j][2])
            if s >= threshold:
                out.append((st[i][0].lower(), st[i][2], st[j][0].lower(), st[j][2], round(s, 2)))
    return out


def internal_pairs(bar, threshold=0.5):
    """Pairs of vowels INSIDE the bar that match, including internal-to-internal pairs."""
    v = nuclei(bar)
    st = [x for x in v if x[3] in ("1", "2")]
    out = []
    for i in range(len(st)):
        for j in range(i + 1, len(st)):
            s = vsim(st[i][2], st[j][2])
            if s >= threshold:
                out.append((st[i][0].lower(), st[i][2], st[j][0].lower(), st[j][2], round(s, 2)))
    return out


def loose_families(bars, thr=0.7):
    """The scheme read BY EAR: two tails are the same family when the final vowels are close
    (vsim >= thr), or when both are reduced and share a coda (Lagos/Vegas), or when the strict tail
    test passes anyway. A vowel-CLASS match is deliberately not used: it was tried and it merged
    families the ear separates.

    Calibrated against match.MANUAL_SCHEME, the annotation made by ear: it reproduces 5 of the 10
    slots exactly (including all three hook slots bar 5-8 and the opening verse) and agrees on 76% of
    the pairs overall, so the remaining verse differences are either the annotation being generous or
    the rhyme running on a longer tail than the two-vowel tail this reads. The strict `families()`
    above stays the one the gates use; this column exists so the difference is visible.
    """
    reps, letters = [], []
    for bar in bars:
        t = bar_tail(bar)
        if not t["nuc"]:
            letters.append("?")
            continue
        placed = False
        for i, r in enumerate(reps):
            if not r["nuc"]:
                continue
            fa, fb = t["nuc"][-1], r["nuc"][-1]
            same = vsim(fa[2], fb[2]) >= thr
            if not same and fa[3] == "0" and fb[3] == "0" and fa[5] == fb[5]:
                same = True
            if not same and tail_score(t["nuc"], r["nuc"]) >= 0.78:
                same = True
            if same:
                letters.append(chr(ord("A") + i))
                placed = True
                break
        if not placed:
            reps.append(t)
            letters.append(chr(ord("A") + len(reps) - 1))
    return "".join(letters)


def syllable_onsets(bar):
    """(consonant, word, index) for every SYLLABLE onset: the first phone of a word, plus any
    intervocalic consonant (V-C-V), which is the onset of the next syllable. Codas are excluded."""
    out = []
    for w in re.findall(r"[A-Za-z']+", bar):
        ph = pron(w)
        if not ph:
            continue
        for i, p in enumerate(ph):
            if is_v(p):
                continue
            if i == 0:
                out.append((strip(p), w.lower(), i))
            elif is_v(ph[i - 1]) and i + 1 < len(ph) and is_v(ph[i + 1]):
                out.append((strip(p), w.lower(), i))     # V-C-V: onset of the next syllable
    return out


def allit_strands(bar):
    """Consonant strands: same consonant opening 2+ different words, or 2+ syllables in this bar.
    Function words count, and consonants inside a word count (Tobago's B and G)."""
    ons = {}
    for c, w, i in syllable_onsets(bar):
        ons.setdefault(c, []).append((w, i))
    out = {}
    for c, items in ons.items():
        words = list(dict.fromkeys(w for w, _ in items))
        if len(words) >= 2 or len(items) >= 2:
            out[c] = words if len(words) >= 2 else [words[0]]
    return out


def internal_pairs(bar, cap=2):
    """Pairs of stressed vowels inside the bar, using BRITISH vowels.

    "internal rhyme" means the SAME vowel (the rubric's own definition: a stressed syllable sharing
    the end's last stressed vowel). A different vowel is not reported as a rhyme at all - that is
    where the false positives came from ("more" ɔː against "home" əʊ). The one exception is a single
    word repeating its own consonant frame (Wag-wan), which is heard as an internal rhyme.
    """
    v = nuclei(bar)
    st = [x for x in v if x[3] in ("1", "2")]
    out = []
    for i in range(len(st)):
        for j in range(i + 1, len(st)):
            wa, va, wb, vb = st[i][0].lower(), st[i][4], st[j][0].lower(), st[j][4]
            if wa == wb and st[i][1] == st[j][1]:
                continue
            if wa in FUNC and wb in FUNC:
                continue                      # two function words sharing a vowel is not a rhyme
            s = vsim(st[i][2], st[j][2])
            if va == vb:
                out.append(("internal rhyme", wa, va, wb, vb, round(s, 2)))
            elif wa == wb and _onset_of(wa, st[i][1]) == _onset_of(wb, st[j][1]):
                out.append(("consonant frame (self-rhyming word)", wa, va, wb, vb, round(s, 2)))
    out.sort(key=lambda x: -x[5])
    return out[:cap]


IDIOM_REGISTER = {
    "plain clothes": "authority (undercover police)", "wrist": "punishment", "chips down": "gambling",
    "hold it down": "business", "one eye open": "caution", "back shortly": "time",
    "open": "none", "miss the boat": "travel", "on the house": "money", "in the dark": "ignorance",
    "the long way": "travel", "out of the blue": "surprise", "over the moon": "feeling",
    "at the end of the day": "time", "take the biscuit": "feeling", "off the rails": "trouble",
    "on the nose": "precision", "under the radar": "stealth", "blue in the face": "effort",
    "spill the beans": "disclosure", "hit the sack": "rest", "in the bag": "certainty",
    "on the ball": "alertness", "the small print": "admin", "last straw": "patience",
    "cold turkey": "withdrawal", "cut corners": "shortcut", "no-go": "refusal",
    "no show": "absence", "dead end": "failure", "short notice": "time", "free rein": "freedom",
    "safe bet": "gambling", "big deal": "importance", "on the cards": "likelihood",
    "in the same boat": "sharing", "on the ropes": "trouble", "long way round": "travel",
    "ball park": "estimate", "on a plate": "ease", "in the pipeline": "process",
    "off the hook": "escape", "on the level": "honesty", "the wrong end": "mistake",
    "under his belt": "achievement", "under the belt": "achievement", "small talk": "conversation",
    "keep in touch": "contact", "a name to a face": "memory", "put a name to a face": "memory",
    "hit the road": "travel", "the last leg": "travel", "check out": "admin",
}


def idioms_in(bar):
    """Stock phrases present, NAMED, with the register they signal. The quality of a cashed idiom is
    not just that it is there: it is (a) the world it implies, (b) whether its literal sense is
    switched on, and (c) whether a second bar answers it with a homophone.

    Matching tolerates up to two words inside the phrase ("cut a few corners" IS "cut corners"),
    because a literal-adjacency test silently missed the very lines this map is meant to judge.
    """
    import coherence_gate as cg          # imported here to keep this module free of cycles
    low = bar.lower()
    found = []
    for k in cg.IDIOMS:
        pat = r"\b" + r"\W+(?:\w+\W+){0,2}?".join(re.escape(w) + r"\w{0,4}" for w in k.split()) + r"\b"
        if re.search(pat, low):
            found.append((k, IDIOM_REGISTER.get(k, "idiom")))
    return found


def payoff_in_rhyme_slot(bar):
    """True when the bar's LAST stressed nucleus is also its final word - the rhyme slot. Rubric 38:
    the payoff word sits in the rhyme slot in the original's wordplay lines."""
    v = nuclei(bar)
    st = [x for x in v if x[3] in ("1", "2")]
    return bool(v and st and st[-1] == v[-1])


def homophone_pairs(bars, max_gap=3):
    """Word pairs in different nearby bars with IDENTICAL phone sequences (plain/plane). This is the
    mechanisable part of the two-bar pun pair: the menace phrase in one bar answered by its
    homophone in a mundane setting in the next."""
    out = []
    for i in range(len(bars)):
        for j in range(i + 1, min(len(bars), i + 1 + max_gap)):
            wa = {w.lower() for w in re.findall(r"[A-Za-z']+", bars[i])}
            wb = {w.lower() for w in re.findall(r"[A-Za-z']+", bars[j])}
            for a in sorted(wa):
                for b in sorted(wb):
                    if a == b or len(a) < 3 or len(b) < 3:
                        continue
                    pa, pb = pron(a), pron(b)
                    if pa and pb and [strip(x) for x in pa] == [strip(x) for x in pb]:
                        out.append((a, i + 1, b, j + 1))
    return out


def tail_pair_class(a, b, threshold=0.78):
    """How cleanly two bar tails rhyme, and in which position.

    Returns ("clean", score) when the rhyme lands the way the original's own pairs do - an identical
    STRESSED vowel and, where the tail is reduced, an identical coda (Lagos/Vegas: eɪ + s) - and
    ("drift", score) when the two tails only agree because their stressed vowels happen to sit in the
    same vowel CLASS (Porto ɔː vs Oslo ɒ). The original's own hook pairs are all clean, so drift is
    not allowed to count as a rhyme for us; it is allowed only where the original itself does it.
    """
    if not a or not b:
        return "none", 0.0
    sc = tail_score(a, b)
    if len(a) < 2 or len(b) < 2:
        return ("clean" if sc >= threshold else "weak"), sc
    va, vb = a[-2][4], b[-2][4]
    sa, sb = a[-2][3], b[-2][3]
    stressed = sa in ("1", "2") or sb in ("1", "2")
    if va == vb:
        return ("clean" if sc >= threshold else "weak"), sc
    if stressed:
        return "drift", sc * 0.5
    return ("clean" if sc >= threshold else "weak"), sc


def drift_pairs(bars):
    """End-pairs that share a rhyme family but only by stressed-vowel drift (see tail_pair_class)."""
    letters = families(bars)[0]
    out = []
    for i in range(len(bars)):
        for j in range(i + 1, len(bars)):
            if letters[i] != letters[j]:
                continue
            a, b = bar_tail(bars[i])["nuc"], bar_tail(bars[j])["nuc"]
            kind, _sc = tail_pair_class(a, b)
            if kind == "drift":
                out.append((i + 1, j + 1))
    return out


def _onset_of(word, idx):
    ph = pron(word)
    if not ph:
        return None
    for k in range(idx, -1, -1):
        if k == 0:
            return strip(ph[0]) if not is_v(ph[0]) else None
        if is_v(ph[k - 1]):
            for q in range(k - 1, -1, -1):
                if not is_v(ph[q]):
                    return strip(ph[q])
            return None
    return None


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    orig = private_path.original_path()
    bars = [l.strip() for l in open(orig, encoding="utf8") if l.strip()][:8]
    print("== bar tails across words ==")
    for i, b in enumerate(bars[:4], 1):
        t = bar_tail(b)
        print(f"  L{i}: tail {t['vowels']} from {t['words']}  crosses words: {t['crosses_words']}")
    letters, reps, det = families(bars[:4])
    print(f"\n== families on the two-syllable tail: {letters} ==")
    for bar, l, a, c, s in det:
        print(f"  {l}: family tail {c} vs {a}  score {s}")
    print("\n== internal pairs (line 2) ==")
    for p in internal_pairs(bars[1]):
        print("  ", p)
    print("\n== alliteration strands (line 2) ==", allit_strands(bars[1]))
    print("== alliteration strands (lines 1-4) ==")
    for i, b in enumerate(bars[:4], 1):
        print(f"  L{i}: {allit_strands(b)}")
