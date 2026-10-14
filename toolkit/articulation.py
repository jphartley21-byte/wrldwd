"""Articulation data (15 Oct 2026): PanPhon feature distance between sounds, and the Klatt/MITalk duration table.

 * join_cost(a, b): how far the mouth must travel between two ARPAbet phones (PanPhon weighted feature edit distance,
   Mortensen et al. 2016, pip install panphon). 0 = no movement (p|p), 0.25 = voicing only (t|d), 1.12 = lips to tongue
   tip (p|t), 2.12 = tongue tip to tongue back (t|k), 3.0 = z|r, 3.9 = s|h. Joe's ear, 15 Oct: p|p is instant, t|k is slow.
 * klatt(phone): (inherent_ms, minimum_ms) from toolkit/klatt_durs.scm, the Festival/CSTR copy of the Klatt (1987) MITalk
   table for the MRPA (British) phone set, copyright notice kept in that file. Read-speech values, not rap.
   (PanPhon needs a `unicodecsv`; on Python 3.13 it fails to build, so the cloud container carries a tiny shim.)
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))

ARPA2IPA = {"B": "b", "CH": "t͡ʃ", "D": "d", "DH": "ð", "F": "f", "G": "ɡ", "HH": "h", "JH": "d͡ʒ", "K": "k", "L": "l",
            "M": "m", "N": "n", "NG": "ŋ", "P": "p", "R": "ɹ", "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "V": "v",
            "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"}
ARPA2MRPA = {"B": "b", "CH": "ch", "D": "d", "DH": "dh", "F": "f", "G": "g", "HH": "h", "JH": "jh", "K": "k", "L": "l",
             "M": "m", "N": "n", "NG": "ng", "P": "p", "R": "r", "S": "s", "SH": "sh", "T": "t", "TH": "th", "V": "v",
             "W": "w", "Y": "y", "Z": "z", "ZH": "zh",
             "AE": "a", "AO": "oo", "AW": "au", "AY": "ai", "EH": "e", "ER": "@@", "EY": "ei", "IH": "i", "IY": "ii",
             "OW": "ou", "OY": "oi", "UH": "u", "UW": "uu"}
_D = None
_CACHE = {}


PLACE_FEATURES = ("ant", "cor", "distr", "lab", "hi", "lo", "back", "round")  # where the lips/tongue go; not voicing or manner
_FT = None


def _place_vec(ipa):
    global _FT
    if _FT is None:
        import panphon
        _FT = panphon.FeatureTable()
    v = _FT.word_to_vector_list(ipa, numeric=True)
    if not v:
        return None
    return {n: x for n, x in zip(_FT.names, v[0])}


def _primary(v):
    """the articulator that makes the constriction: lips, tongue, or glottis (w counts as lips, with the tongue only secondary)"""
    if v["lab"] == 1:
        return "lips"
    if v["cor"] == 1 or v["hi"] == 1 or v["back"] == 1 or v["lo"] == 1:
        return "tongue"
    return "glottis"


def join_cost(a, b):
    """mouth travel between consonant phones a and b (ARPAbet, no stress digits), from PanPhon place features.
    Articulatory Phonology (Browman & Goldstein): gestures on DIFFERENT articulators overlap in time, gestures on the SAME
    articulator at a different place cannot. So: same place = 0 (p|p, t|d, t|s: no movement); different articulators = 1
    (lips then tongue, tongue then glottis: they overlap); same articulator, different place = 1 + 0.5 per differing place feature
    (tongue tip to tongue back, t|k: the tongue has to travel). Voicing and manner are ignored on purpose.
    PanPhon's full weighted distance (join_cost_full) ranks glides far from every stop, which is phonological similarity,
    not travel ('and|we' scored as hard as anything). None if a phone is unknown."""
    k = (a, b)
    if k in _CACHE:
        return _CACHE[k]
    ia, ib = ARPA2IPA.get(a), ARPA2IPA.get(b)
    if not ia or not ib:
        return None
    if a == "HH" or b == "HH":  # /h/ is a glottal gesture, whatever PanPhon says about its supralaryngeal features
        _CACHE[k] = 0.0 if a == b else 1.0
        return _CACHE[k]
    va, vb = _place_vec(ia), _place_vec(ib)
    if not va or not vb:
        return None
    diffs = sum(1 for f in PLACE_FEATURES if va[f] != vb[f])
    if diffs == 0:
        t = 0.0
    elif _primary(va) != _primary(vb):
        t = 1.0
    elif _primary(va) == "lips":
        t = 0.5  # p|w, b|m, f|w: the lips just change shape; the w's tongue-back lift is secondary and does not travel
    else:
        t = 1.0 + 0.5 * diffs
    _CACHE[k] = t
    return t


def join_cost_full(a, b):
    """PanPhon weighted feature edit distance (all features); kept for comparison"""
    global _D
    ia, ib = ARPA2IPA.get(a), ARPA2IPA.get(b)
    if not ia or not ib:
        return None
    if _D is None:
        import panphon.distance
        _D = panphon.distance.Distance()
    return round(_D.weighted_feature_edit_distance(ia, ib), 2)


_K = None


def klatt(mrpa):
    """(inherent_ms, minimum_ms) for an MRPA phone"""
    global _K
    if _K is None:
        _K = {}
        for m in re.finditer(r"^\((\S+)\s+([\d.]+)\s+([\d.]+)\)", open(os.path.join(HERE, "klatt_durs.scm"), encoding="utf8").read(), re.M):
            _K[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return _K.get(mrpa)


def selftest():
    p = []
    c = {k: join_cost(*k) for k in (("P", "P"), ("T", "D"), ("P", "T"), ("T", "K"), ("Z", "R"))}
    if c[("P", "P")] != 0:
        p.append("p|p not 0: %s" % c)
    if not (c[("P", "P")] == c[("T", "D")] == 0 and 0 < c[("P", "T")] < c[("T", "K")]):
        p.append("join order wrong: %s" % c)
    if not klatt("ii") or klatt("ii")[0] <= klatt("i")[0]:
        p.append("long vowel not longer than short in the Klatt table")
    if len(_K) < 40:
        p.append("Klatt table has %d entries" % len(_K))
    return (not p, "; ".join(p) if p else "articulator model order p|p = t|d < p|t < t|k holds; Klatt table loaded (%d phones)" % len(_K))


if __name__ == "__main__":
    ok, msg = selftest()
    print(("PASSED: " if ok else "FAILED: ") + msg)
    sys.exit(0 if ok else 1)
