"""phon: British syllables (vowel + consonants) and a graded rhyme score that understands slant rhymes.
  python toolkit/phon.py "come on then" "Dublin"     -> score and type (perfect / near / slant / none)
Vowels compared by mouth position (height, backness, rounding, length); consonants by class; final consonant weighted.
"""
import os, re, sys
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# (height 0=close..3=open, backness 0=front..2=back, rounded, long/diphthong-ish)
V = {"iː": (0, 0, 0, 1), "i": (0, 0, 0, 0), "ɪ": (0.5, 0.3, 0, 0), "e": (1.5, 0, 0, 0), "ɛ": (1.5, 0, 0, 0), "æ": (2.7, 0.2, 0, 0),
     "ʌ": (2.3, 1.3, 0, 0), "ɐ": (2.3, 1.3, 0, 0), "ə": (1.7, 1, 0, 0), "ɜː": (1.7, 1, 0, 1), "ɑː": (3, 2, 0, 1), "ɒ": (3, 2, 1, 0),
     "ɔː": (2, 2, 1, 1), "ʊ": (0.5, 1.7, 1, 0), "uː": (0, 2, 1, 1), "eɪ": (1.2, 0, 0, 1), "aɪ": (2.5, 0.8, 0, 1), "ɔɪ": (2, 1.6, 1, 1),
     "əʊ": (1.6, 1.4, 1, 1), "aʊ": (2.5, 1.4, 1, 1), "ɪə": (0.8, 0.5, 0, 1), "eə": (1.6, 0.3, 0, 1), "ɛə": (1.6, 0.3, 0, 1), "ʊə": (0.8, 1.6, 1, 1)}
CCLASS = [set("pb"), set("td"), set("kɡg"), set("fv"), set("θð"), set("szʃʒ"), {"tʃ", "dʒ"}, set("mnŋ"), set("l"), set("ɹr"), set("wj"), set("h")]
WEAKV = {"ə", "ɪ", "i"}
# REDUCED is the subset that can never carry a rime on its own. /ɪ/ and /i/ stay out of it on purpose:
# the original rhymes certi ~ forty and Dublin ~ him, and an over-broad guard demoted 17 of its own
# verse pairs before this was split out. Measured 13 Oct 2026.
REDUCED = {"ə"}
# Closing diphthongs as (start vowel, glide). Two diphthongs sharing a glide rhyme in the ear even
# when their starting points are far apart in the vowel space (aɪ ~ eɪ).
DIPH = {"eɪ": ("e", "ɪ"), "aɪ": ("æ", "ɪ"), "ɔɪ": ("ɔː", "ɪ"), "əʊ": ("ə", "ʊ"), "aʊ": ("æ", "ʊ"),
        "ɪə": ("ɪ", "ə"), "eə": ("e", "ə"), "ɛə": ("e", "ə"), "ʊə": ("ʊ", "ə")}


def vsim(a, b):
    if a == b:
        return 1.0
    if a not in V or b not in V:
        return 0.0
    (h1, b1, r1, l1), (h2, b2, r2, l2) = V[a], V[b]
    d = abs(h1 - h2) / 3 + abs(b1 - b2) / 2 + 0.25 * abs(r1 - r2) + 0.15 * abs(l1 - l2)
    out = max(0.0, 1 - d)
    # Closing diphthongs that share their glide rhyme in the ear, which the two-point model above rates
    # far apart: aɪ against eɪ scored 0.17, but the original does rhyme those (a German city with a
    # country), and the vowel-distance table made it impossible to represent. The glide is the rhyme.
    da, db = DIPH.get(a), DIPH.get(b)
    if da and db:
        glide = 1.0 if da[1] == db[1] else 0.0
        start = vsim(da[0], db[0]) if da[0] in V and db[0] in V else 0.0
        out = max(out, 0.45 + 0.4 * glide + 0.15 * start)
    return out


def csim(a, b):
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    ca = next((i for i, s in enumerate(CCLASS) if a in s), -1)
    cb = next((i for i, s in enumerate(CCLASS) if b in s), -2)
    return 0.6 if ca == cb else 0.0


def word_phones(w):
    """British phones for a word: list of tokens with stress marks on vowels ('ˈʌ')."""
    from helpers import uk_phones as bf, uk as bf_dict
    w = w.lower().strip("'.,?!")
    p = bf(w)
    if not p:
        for suf in ("led", "ed", "d", "ing", "s", "es", "'s"):
            base = w[: -len(suf)]
            if w.endswith(suf) and (bf(base) or bf_dict(base)):
                tail = {"led": ["l", "d"], "ed": ["d"], "d": ["d"], "ing": ["ɪ", "ŋ"], "s": ["z"], "es": ["ɪ", "z"], "'s": ["z"]}[suf]
                p = bf(base) + tail
                break
    if p:
        return [t.replace("ɐ", "ʌ").replace("ɛ", "e").replace("ɡ", "g") for t in p]
    from match import uk_vowels  # vowels only fallback
    vs = uk_vowels(w) or []
    return [("ˈ" if st else "") + v for v, st in vs]


def is_vowel(t):
    return any(c in "iɪeæʌɒʊəuɑɔɜa" for c in t.replace("ˈ", "").replace("ˌ", ""))


def syllables(text):
    """[(vowel, stressed, coda_consonants)] for a phrase; consonants before the next vowel go to the coda (rhyme view)."""
    from rhyme_tools import FUNC
    out = []
    for w in re.findall(r"[A-Za-z'å]+", text.replace("å", "a").replace("-", " ")):
        ph = word_phones(w)
        nv = sum(1 for t in ph if is_vowel(t))
        seen = False  # a word's onset consonants never join the previous word's coda
        for t in ph:
            if is_vowel(t):
                st = t.startswith("ˈ") or (nv == 1 and w.lower() not in FUNC)
                out.append([t.replace("ˈ", "").replace("ˌ", ""), st, []])
                seen = True
            elif out and seen:
                out[-1][2].append(t)
    return out


def score(a, b):
    """graded rhyme between two spans of syllables. Aligns first (stressed) and last syllables; middle by position.
    Returns (score 0-1, kind)."""
    A, B = syllables(a) if isinstance(a, str) else a, syllables(b) if isinstance(b, str) else b
    if not A or not B:
        return 0.0, "none"
    if abs(len(A) - len(B)) > 1:
        return 0.0, "none"
    n = min(len(A), len(B))
    # Alignment is from the LEFT, stressed-syllable-anchored, which is what the rhyme map is built on
    # and what the original's own profile requires. A RIGHT-aligned variant was tried on 12 Oct to stop
    # "dot" ~ "Ljubljana" (1-vs-2 syllables, nothing in common but ɒ); it fixed that and broke four
    # "original vs own profile" checks, because the original's own B-group links (a place name against a
    # country) have exactly the same shape -- matching stressed vowel, one side ending in a weak open
    # tail. The two cases are indistinguishable in this representation, so the alignment cannot decide
    # between them and the schema check stays advisory. See toolkit/tests/rhyme_pairs.txt for the set.
    pairs = [(A[0], B[0])] + [(A[i], B[i]) for i in range(1, n - 1)] + ([(A[-1], B[-1])] if n > 1 else [])
    vs = []
    for i, (x, y) in enumerate(pairs):
        s = vsim(x[0], y[0])
        if i > 0 and x[0] in WEAKV and y[0] in WEAKV:
            s = max(s, 0.85)
        vs.append(s)
    stressed = vs[0]
    rest = sum(vs[1:]) / max(1, len(vs) - 1) if len(vs) > 1 else 1.0
    fa, fb = (A[-1][2][-1] if A[-1][2] else ""), (B[-1][2][-1] if B[-1][2] else "")
    final = 1.0 if fa == fb else csim(fa, fb)
    # Rhyme, measured against pairs whose verdict is known (12 Oct 2026). The original version of
    # this function graded 4 of 10 wrong, in both directions:
    #   FALSE POSITIVE: "dot" / "orders" / "borders" ~ "Ljubljana" all scored exactly 0.80 -- a
    #     stressed-vowel-only match with no coda agreement -- and the 0.78 scheme floor admits that,
    #     because the grader's "slant" band starts at 0.70. That is how a non-rhyming place name got
    #     into a block whose scheme demanded a rhyme.
    #   FALSE NEGATIVE: the original's own place-name rhyme (ɒ against ə in a matching -gas frame)
    #     graded 0.45-0.50, below the same floor.
    # The coda (the actual rime) carries 0.2 of the score, and "stressed vowel must match" gates the
    # rest. Reweighting was tried and reverted: it broke 8 of 10 "original vs own profile" rhyme-map
    # checks, because the original rhymes on the vowel far more than on the coda. So the two
    # corrections below are scoped to the two shapes that were demonstrably wrong, and nothing else.
    if final >= 0.9 and len(A) == len(B) == 1 and (A[-1][0] in WEAKV or B[-1][0] in WEAKV):
        # A weak vowel inside a MATCHING coda still rhymes (--gas against --gəs). Without this the
        # pair is gated out entirely and the original's own link scores 0.00.
        stressed = max(stressed, 0.8)
    total = 0.5 * stressed + 0.3 * rest + 0.2 * final
    if len(A) == 1 and len(B) == 1 and A[-1][0] in REDUCED and B[-1][0] in REDUCED:
        # Two reduced syllables are not a rhyme, whatever their codas do. Only /ə/ counts as reduced:
        # /i/ and /ɪ/ are full vowels that DO carry a rime (the original rhymes certi ~ forty,
        # thirsty ~ shortly, curly ~ thirty on a final /i/ and Dublin ~ him, in ~ him on /ɪ/ + nasal),
        # and an earlier version of this guard used all of WEAKV and demoted 17 of the original's own
        # verse pairs -- a gate the benchmark fails is a wrong gate.
        # What it must stop is the schwa: this used to require final < 0.5 (codas disagree), which let
        # the WORSE shape through, because with agreeing codas (z/z, s/z) the reduced vowels score
        # vsim(ə,ə)=1.0, `rest` defaults to 1.0 (a one-syllable span has no middle) and the pair graded
        # 1.00/perfect on the schwa alone. "Naples" ~ "sellers" and "Naples" ~ "Florence" scored 1.00
        # and 0.92 that way while their STRESSED syllables (EY against EH, EY against ɒ) do not rhyme
        # at all -- the two-syllable alignment of both pairs is 0.42/none. Joe heard the non-rhyme
        # through a "6/6 carpet, min 0.92" reading, 13 Oct 2026. The original's weakest hook pair,
        # Lagos ~ Vegas, is unaffected: it scores 0.80 on the two-syllable span.
        return min(total, 0.65), "none"
    if stressed < 0.75:
        return round(total, 2), "none"
    kind = "perfect" if total >= 0.97 else "near" if total >= 0.85 else "slant" if total >= 0.7 else "none"
    return round(total, 2), kind


if __name__ == "__main__":
    s, k = score(sys.argv[1], sys.argv[2])
    print(f"{sys.argv[1]!r} ~ {sys.argv[2]!r}: {s} {k}  | {syllables(sys.argv[1])} vs {syllables(sys.argv[2])}")
