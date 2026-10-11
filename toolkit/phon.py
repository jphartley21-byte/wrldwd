"""phon: British syllables (vowel + consonants) and a graded rhyme score that understands slant rhymes.
  python toolkit/phon.py "come on then" "Dublin"     -> score and type (perfect / near / slant / none)
Vowels compared by mouth position (height, backness, rounding, length); consonants by class; final consonant weighted.
"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# (height 0=close..3=open, backness 0=front..2=back, rounded, long/diphthong-ish)
V = {"iː": (0, 0, 0, 1), "i": (0, 0, 0, 0), "ɪ": (0.5, 0.3, 0, 0), "e": (1.5, 0, 0, 0), "ɛ": (1.5, 0, 0, 0), "æ": (2.7, 0.2, 0, 0),
     "ʌ": (2.3, 1.3, 0, 0), "ɐ": (2.3, 1.3, 0, 0), "ə": (1.7, 1, 0, 0), "ɜː": (1.7, 1, 0, 1), "ɑː": (3, 2, 0, 1), "ɒ": (3, 2, 1, 0),
     "ɔː": (2, 2, 1, 1), "ʊ": (0.5, 1.7, 1, 0), "uː": (0, 2, 1, 1), "eɪ": (1.2, 0, 0, 1), "aɪ": (2.5, 0.8, 0, 1), "ɔɪ": (2, 1.6, 1, 1),
     "əʊ": (1.6, 1.4, 1, 1), "aʊ": (2.5, 1.4, 1, 1), "ɪə": (0.8, 0.5, 0, 1), "eə": (1.6, 0.3, 0, 1), "ɛə": (1.6, 0.3, 0, 1), "ʊə": (0.8, 1.6, 1, 1)}
CCLASS = [set("pb"), set("td"), set("kɡg"), set("fv"), set("θð"), set("szʃʒ"), {"tʃ", "dʒ"}, set("mnŋ"), set("l"), set("ɹr"), set("wj"), set("h")]
WEAKV = {"ə", "ɪ", "i"}


def vsim(a, b):
    if a == b:
        return 1.0
    if a not in V or b not in V:
        return 0.0
    (h1, b1, r1, l1), (h2, b2, r2, l2) = V[a], V[b]
    d = abs(h1 - h2) / 3 + abs(b1 - b2) / 2 + 0.25 * abs(r1 - r2) + 0.15 * abs(l1 - l2)
    return max(0.0, 1 - d)


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
    from helpers import uk as bf
    w = w.lower().strip("'.,?!")
    p = bf(w)
    if not p:
        for suf in ("led", "ed", "d", "ing", "s", "es", "'s"):
            base = w[: -len(suf)]
            if w.endswith(suf) and bf(base):
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
    total = 0.5 * stressed + 0.3 * rest + 0.2 * final
    if stressed < 0.75:
        return round(total, 2), "none"
    kind = "perfect" if total >= 0.97 else "near" if total >= 0.85 else "slant" if total >= 0.7 else "none"
    return round(total, 2), kind


if __name__ == "__main__":
    s, k = score(sys.argv[1], sys.argv[2])
    print(f"{sys.argv[1]!r} ~ {sys.argv[2]!r}: {s} {k}  | {syllables(sys.argv[1])} vs {syllables(sys.argv[2])}")
