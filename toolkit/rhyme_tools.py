#!/usr/bin/env python
"""rhyme_tools.py: rhyme, syllable and flow checks for the Worldwide track.
Built on the CMU pronouncing dictionary (US pronunciations) with a UK-ish layer: post-vocalic R is dropped
for rhyme matching (saw/sore, farm/calm), and custom pronunciations live in OVR (add place names and slang there).

  python rhyme_tools.py pron "double it"
  python rhyme_tools.py rhymes WORD [--n 1] [--mode perfect|assonance|near] [--max 60] [--stress]
  python rhyme_tools.py mosaic "double it" [--nsyl 2] [--max 40] [--loose]   # cut-up rhymes: word pairs that sound like a phrase
  python rhyme_tools.py families [--n 2] [--min 4]                           # rhyme families ranked by how many theme words they hold
  python rhyme_tools.py check FILE [--n 1]                                   # line and chain checks (one bar per line; blank line = new chain)
"""
import argparse
import collections
import os
import re
import sys

import cmudict

HERE = os.path.dirname(os.path.abspath(__file__))
D = cmudict.dict()

# Custom pronunciations (ARPAbet, stress digits). Extend freely. British-ish where it matters for rhyme.
OVR = {
    "ya": "Y AH0", "gon'": "G AH0 N", "pavos": "P AE1 V OW0 S", "dhal": "D AA1 L", "lah": "L AA1",
    "he's": "HH IY1 Z", "she's": "SH IY1 Z", "they'll": "DH EY1 L", "we've": "W IY1 V", "gaz": "G AE1 Z", "gaz'll": "G AE1 Z AH0 L", "'em": "AH0 M", "i've": "AY1 V", "you're": "Y AO1 R",
    "tao": "T AW1", "koh": "K OW1", "bilbao": "B IH0 L B AW1", "ljubljana": "L UW0 B L Y AA1 N AH0",
    "bratislava": "B R AE2 T IH0 S L AA1 V AH0", "lauterbrunnen": "L AW1 T ER0 B R UH2 N AH0 N",
    "zay": "Z EY1", "zell": "Z EH1 L", "hervey": "HH AA1 V IY0", "pompeii": "P AA0 M P EY1",
    "marrakesh": "M AE2 R AH0 K EH1 SH", "larrau": "L AH0 R AW1", "laruns": "L AH0 R AH1 N Z",
    "ainsa": "AY1 N S AH0", "domme": "D AA1 M", "arvo": "AA1 V OW0", "servus": "S EH1 R V UH0 S",
    "mai": "M AY1", "rai": "R AY1", "bracklesham": "B R AE1 K AH0 L SH AH0 M", "calais": "K AE1 L EY0",
    "peage": "P EY0 AA1 ZH", "kgari": "G ER1 IY0", "doobies": "D UW1 B IY0 Z", "doobie": "D UW1 B IY0",
    "dubai": "D UW0 B AY1", "scafell": "S K AO1 F EH2 L", "snowdon": "S N OW1 D AH0 N", "groats": "G R OW1 T S",
    "nevis": "N EH1 V IH0 S", "bergen": "B ER1 G AH0 N", "oslo": "AA1 Z L OW0", "padstow": "P AE1 D S T OW0",
    "porto": "P AO1 R T OW0", "hurtin": "HH ER1 T IH0 N", "fam": "F AE1 M", "grouse": "G R AW1 S", "bergen": "B ER1 G AH0 N", "skal": "S K AO1 L", "hurtigruten": "HH ER1 T IY0 G R UW2 T AH0 N", "majorca": "M AH0 Y AO1 R K AH0", "portsmouth": "P AO1 R T S M AH0 TH", "bordeaux": "B AO0 R D OW1", "vienna": "V IY0 EH1 N AH0", "zurich": "Z UH1 R IH0 K",
    "bern": "B ER1 N", "amsterdam": "AE1 M S T ER0 D AE2 M", "interrail": "IH1 N T ER0 R EY2 L",
    # Isle of Man and Donegal (the May 2023 motorbike trip in material/travel_history.md). Added 12 Oct
    # 2026: V1 17-24 owns these places and the tools could not pronounce a single one of them.
    "laxey": "L AE1 K S IY0", "castletown": "K AE1 S AH0 L T AW2 N", "douglas": "D AH1 G L AH0 S",
    "ramsey": "R AE1 M Z IY0", "onchan": "AA1 N CH AH0 N", "tynwald": "T IH1 N W AO0 L D",
    "snaefell": "S N EY1 F EH2 L", "peel": "P IY1 L", "donegal": "D AA2 N IH0 G AO1 L",
    "letterkenny": "L EH2 T ER0 K EH1 N IY0", "bundoran": "B AH2 N D AO1 R AH0 N",
    "malin": "M AE1 L IH0 N", "maughold": "M AO1 K AH0 L D",
    "panniers": "P AE1 N Y ER0 Z", "wetherspoons": "W EH1 DH ER0 S P UW2 N Z", "spoons": "S P UW1 N Z",
    "guten": "G UW1 T AH0 N", "morgen": "M AO1 R G AH0 N", "freiburg": "F R AY1 B UH0 R G",
    "horfield": "HH AO1 F IY0 L D", "rotterdam": "R AA1 T ER0 D AE2 M", "donegal": "D AA1 N AH0 G AO2 L",
    "cairns": "K AE1 N Z", "noosa": "N UW1 S AH0", "whitsundays": "W IH1 T S AH0 N D EY2 Z",
    "kettle": "K EH1 T AH0 L", "pyjamas": "P AH0 JH AA1 M AH0 Z", "tarn": "T AA1 N", "scree": "S K R IY1",
    "cairn": "K EH1 N", "fell": "F EH1 L", "gorse": "G AO1 S", "loch": "L AA1 K", "lough": "L AA1 K",
    "hasta": "AA1 S T AH0", "luego": "L W EH1 G OW0", "wagwan": "W AE1 G W AA2 N", "ese": "EH1 SH EH0",
    "lagos": "L EY1 G AA0 S", "tobago": "T AH0 B EY1 G OW0", "vegas": "V EY1 G AH0 S", "kaixo": "K AY1 SH OW0", "shukran": "SH UH1 K R AA0 N", "prost": "P R OW1 S T", "napoli": "N AA1 P AH0 L IY0", "lorry": "L AA1 R IY0", "quarry": "K W AA1 R IY0", "corrie": "K AA1 R IY0", "obrigado": "OW2 B R IH0 G AA1 D OW0", "bonjour": "B AO0 N ZH UH1 R", "bought": "B AO1 T", "sawn": "S AO1 N", "bonjourno": "B AA2 N JH AO1 N OW0", "should've": "SH UH1 D AH0 V", "shouldve": "SH UH1 D AH0 V", "sawnoff": "S AO1 N AO2 F", "caught": "K AO1 T", "brought": "B R AO1 T", "thought": "TH AO1 T", "taught": "T AO1 T", "fought": "F AO1 T", "sought": "S AO1 T", "maman": "M AH0 M AA1 N", "transatlantic": "T R AE2 N Z AH0 T L AE1 N T IH0 K",
    "fiver": "F AY1 V ER0", "gday": "G AH0 D EY1", "hei": "HH EY1", "handoff": "HH AE1 N D AO2 F", "rhine": "R AY1 N",
    "peaky": "P IY1 K IY0", "pyrenees": "P IH2 R AH0 N IY1 Z",
    # The transactional local words (toolkit/local_words.txt), by the country they belong to. Without these
    # the whole code-switching supply was unmeasurable: the toolkit could not count syllables, place stress
    # or rhyme any bar that used one, so a bar built on a local word read as a vowel blob. Anglicised on
    # purpose -- the song is in English and the word has to scan in an English line.
    "zdravo": "Z D R AA1 V OW0", "hvala": "HH V AA1 L AH0", "prosim": "P R OW1 S IH0 M",
    "pivo": "P IY1 V OW0", "kava": "K AA1 V AH0", "dakujem": "D Y AA1 K UW0 Y EH2 M",
    "danke": "D AA1 NG K AH0", "rechnung": "R EH1 K N UH0 NG",
    "grazie": "G R AA1 T S IY0", "birra": "B IH1 R AH0", "conto": "K AA1 N T OW0", "scusi": "S K UW1 Z IY0",
    "flics": "F L IH1 K S", "cuenta": "K W EH1 N T AH0", "tio": "T IY1 OW0",
    "cerveja": "S ER0 V EY1 ZH AH0", "conta": "K OW1 N T AH0", "vinho": "V IY1 N Y OW0",
    "yamas": "Y AA1 M AH0 S", "ouzo": "UW1 Z OW0", "parakalo": "P AA0 R AA1 K AH0 L OW0",
    "efharisto": "EH0 F AA0 R IY1 S T OW0",
    "takk": "T AA1 K", "ol": "OW1 L", "regningen": "R AY1 N IH0 NG AH0 N",
    "khop": "K AO1 P", "bhat": "B AE1 T", "farang": "F AA0 R AE1 NG", "xin": "S IH1 N",
    "bia": "B IY1 AH0", "certi": "S ER1 T IY0", "guap": "G W AE1 P",
    "nore": "N AO1 R AH0", "slideshow": "S L AY1 D SH OW0",
    # The -ow / -o family, where cmudict is inconsistent with itself: it marks the final syllable of
    # borrow, shadow, willow, potato, tobacco, tornado, solo, photo, tempo, kilo, memo as secondary-stressed
    # (OW2) and the identical syllable of sorrow, follow, hollow, yellow, window, burrow, polo, demo, weirdo,
    # logo, zero as unstressed (OW0). In speech they are all the same unstressed /əʊ/. The difference is not
    # cosmetic: the hook's end shape is |Sw (Joe's bars and the original's both), and an OW2 final makes a
    # perfect rhyme word read as two strong syllables, so a bar written to the shape FAILS as if it were
    # wrong. Measured 12 Oct 2026.
    "borrow": "B AA1 R OW0", "borrowed": "B AA1 R OW0 D", "tomorrow": "T AH0 M AA1 R OW0", "shadow": "SH AE1 D OW0",
    "willow": "W IH1 L OW0", "potato": "P AH0 T EY1 T OW0", "tomato": "T AH0 M EY1 T OW0",
    "tobacco": "T AH0 B AE1 K OW0", "tornado": "T AO0 R N EY1 D OW0", "solo": "S OW1 L OW0",
    "photo": "F OW1 T OW0", "tempo": "T EH1 M P OW0", "kilo": "K IH1 L OW0", "memo": "M EH1 M OW0",
    "calais": "K AE0 L EY1", "kaixo": "K AY1 SH OW0", "koh": "K OW1",
    "g'day": "G AH0 D EY1", "ahoj": "AH0 HH OY1", "zivjo": "ZH IY1 V Y OW0",
    # UK slang and everyday British words absent from cmudict. Without a pronunciation here the
    # toolkit cannot count syllables, place stress or rhyme the word, so these were unusable.
    "conker": "K AA1 NG K ER0", "skint": "S K IH1 N T", "knackered": "N AE1 K ER0 D", "chuffed": "CH AH1 F T", "dodgy": "D AO1 JH IY0", "minging": "M IH1 NG IH0 NG", "bevvy": "B EH1 V IY0",
    "bevvies": "B EH1 V IY0 Z", "bevvied": "B EH1 V IY0 D", "sarnie": "S AA1 N IY0", "butty": "B AH1 T IY0", "scran": "S K R AE1 N", "trollied": "T R AO1 L IY0 D",
    "wazzock": "W AE1 Z AH0 K", "skive": "S K AY1 V", "skiving": "S K AY1 V IH0 NG", "faff": "F AE1 F", "faffing": "F AE1 F IH0 NG", "kipping": "K IH1 P IH0 NG",
    "nicking": "N IH1 K IH0 NG", "scarper": "S K AA1 P ER0", "scarpered": "S K AA1 P ER0 D", "rozzer": "R AA1 Z ER0", "numpty": "N AH1 M P T IY0", "div": "D IH1 V",
    "gormless": "G AO1 M L AH0 S", "doolally": "D UW1 L AE2 L IY0", "barmy": "B AA1 M IY0", "narky": "N AA1 K IY0", "mardy": "M AA1 D IY0", "buzzin": "B AH1 Z IH0 N",
    "chav": "CH AE1 V", "plonker": "P L AA1 NG K ER0", "pillock": "P IH1 L AH0 K", "tosser": "T AA1 S ER0", "stonking": "S T AA1 NG K IH0 NG", "chocka": "CH AA1 K AH0",
    "chocker": "CH AA1 K ER0", "chippies": "CH IH1 P IY0 Z", "caff": "K AE1 F", "cushdy": "K UH1 SH D IY0", "blag": "B L AE1 G", "blagged": "B L AE1 G D",
    "innit": "IH1 N IH0 T", "cuppa": "K AH1 P AH0", "boozers": "B UW1 Z ER0 Z", "mullered": "M AH1 L ER0 D", "baccy": "B AE1 K IY0",
    # Place names that were MISSING, which mattered more than it sounds: phon.word_phones falls back
    # to a vowels-only guess when the dictionary has no entry, silently dropping every consonant. So
    # "Lagos" was parsed as two bare vowels with NO coda and could not rhyme with anything -- the
    # 12 Oct labelled-pair test caught it as a false negative on the original's own rhyme.
    "lagos": "L EY1 G AH0 S", "vegas": "V EY1 G AH0 S", "verona": "V ER0 OW1 N AH0", "bonn": "B AA1 N",
    "brisbane": "B R IH1 Z B AH0 N", "belgrade": "B EH0 L G R EY1 D", "mainz": "M AY1 N T S",
    "milano": "M IH0 L AA1 N OW0", "marbella": "M AA2 R B EH1 L AH0", "toulon": "T UW0 L AA1 N",
    "saigon": "S AY2 G AA1 N", "ibiza": "IH0 B IY1 TH AH0", "granada": "G R AH0 N AA1 D AH0",
    "bologna": "B AH0 L OW1 N Y AH0", "havana": "HH AH0 V AE1 N AH0", "prague": "P R AA1 G",
    # Australian slang (Joe, 14 Oct 2026: Aussie slang into the pool; the Sydney / Australia 2017 trips). Anglicised, as the song is English.
    "bottlo": "B AA1 T L OW0", "esky": "EH1 S K IY0", "brekkie": "B R EH1 K IY0", "ute": "Y UW1 T", "tinnie": "T IH1 N IY0", "smoko": "S M OW1 K OW0",
    "dunny": "D AH1 N IY0", "durry": "D ER1 IY0", "mozzie": "M AA1 Z IY0", "sickie": "S IH1 K IY0", "drongo": "D R AA1 NG G OW0", "larrikin": "L AE1 R IH0 K IH0 N",
    "galah": "G AH0 L AA1", "bludger": "B L AH1 JH ER0", "cobber": "K AA1 B ER0", "hooroo": "HH UW0 R UW1", "crikey": "K R AY1 K IY0", "strewth": "S T R UW1 TH",
    "bonzer": "B AA1 N Z ER0", "sook": "S UH1 K", "yakka": "Y AE1 K AH0", "bikkie": "B IH1 K IY0", "doona": "D UW1 N AH0", "billabong": "B IH1 L AH0 B AO2 NG",
    "swag": "S W AE1 G", "jackaroo": "JH AE2 K ER0 UW1", "tradie": "T R EY1 D IY0", "cossie": "K AA1 Z IY0", "maccas": "M AE1 K AH0 Z", "middy": "M IH1 D IY0",
    "chunder": "CH AH1 N D ER0", "dinkum": "D IH1 NG K AH0 M", "uey": "Y UW1 IY0", "coldie": "K OW1 L D IY0", "donger": "D AO1 NG ER0", "wallopers": "W AA1 L AH0 P ER0 Z",
    "straya": "S T R EY1 Y AH0", "kaixo": "K AY1 SH OW0",
    # The original's own out-of-dictionary words (14 Oct 2026): without these the toolkit dropped them, so bar 76 counted
    # 3 syllables instead of 12 in `check` and phon, and its rhyme tail had no consonants. Same syllable counts as the
    # template's vowel-group estimate, so the audio steps still line up.
    "chicas": "CH IY1 K AH0 Z", "federali": "F EH2 D ER0 AA1 L IY0", "fumez": "F Y UW1 M EH0 Z",
    "wwe": "D AH1 B AH0 L Y UW0 D AH1 B AH0 L Y UW0 IY1", "smackdown": "S M AE1 K D AW2 N",
    "shirty": "SH ER1 T IY0", "proost": "P R OW1 S T",   # UK: annoyed, in a mood (absent from cmudict like the 47 everyday British words above)
}
FUNC = set("""ya this a an the of to in on at for and or but so if as i my me we you he she it is was are am be been by
with from up that this his her our your they them their its im ill ive dont cant wont isnt wasnt then than do did
does not no too just all out off over into onto upon via per""".split())
BANNED = set("""journey fairytale vibes legend king throne neon shadows shadow echoes echo tapestry whisper whispers
grind destiny dreams dream""".split())
CLASSES = {"P": "S", "B": "S", "T": "S", "D": "S", "K": "S", "G": "S",   # stops
           "F": "F", "V": "F", "TH": "F", "DH": "F", "S": "F", "Z": "F", "SH": "F", "ZH": "F", "HH": "F",
           "M": "N", "N": "N", "NG": "N", "L": "L", "R": "L", "W": "G", "Y": "G", "CH": "A", "JH": "A"}
VOICE = {"B": "P", "D": "T", "G": "K", "V": "F", "Z": "S", "ZH": "SH", "JH": "CH", "DH": "TH"}


def strip(p):
    return p.rstrip("012")


def is_v(p):
    return p[-1] in "012"


def pron(word):
    # The apostrophe must survive the lookup. It used to be stripped first, which made every contraction
    # in cmudict and in OVR an OOV word: "he's" (HH IY1 Z, present in BOTH tables) resolved to None, so
    # it fell through to the vowel-group estimate and lost its /h/ and /z/ entirely. Consequence (14 Oct
    # 2026): a join such as "whites, he's" could not be measured for consonants at all, and the word
    # could not be stress-classified. Measured before the fix: 27 apostrophe tokens in the original's 92
    # bars, 5 of them unresolvable; and after it, the original's own syllable counts and stress patterns
    # are unchanged bar for bar, so the fix is a repair, not a recalibration.
    raw = word.lower().strip().strip(".,?!;:")
    if raw in OVR:
        return OVR[raw].split()
    if raw in D:
        return list(D[raw][0])
    w = re.sub(r"[^a-z]", "", raw)
    if not w:
        return None
    if w in OVR:
        return OVR[w].split()
    if w in D:
        return list(D[w][0])
    for a_, b_ in (("our", "or"), ("ise", "ize"), ("yse", "yze"), ("tre", "ter"), ("ll", "l")):
        if a_ in w and w.replace(a_, b_) in D:
            return list(D[w.replace(a_, b_)][0])
    for suf, add in (("ies", "IY0 Z"), ("es", "AH0 Z"), ("s", "Z"), ("ing", "IH0 NG"), ("ed", "D"), ("ly", "L IY0")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            base = w[: -len(suf)]
            for b in (base, base + "e", base + "y"):
                if b in OVR:
                    return OVR[b].split() + add.split()
                if b in D:
                    return list(D[b][0]) + add.split()
    return None


def pron_phrase(text):
    out = []
    for t in re.findall(r"[A-Za-z']+", text):
        p = pron(t)
        if p is None:
            return None, t
        out += p
    return out, None


def uk(ph):
    """drop post-vocalic R (not before a vowel)"""
    out = []
    for i, p in enumerate(ph):
        if strip(p) == "R" and i > 0 and is_v(ph[i - 1]) and (i + 1 == len(ph) or not is_v(ph[i + 1])):
            continue
        out.append(p)
    return out


def vidx(ph):
    return [i for i, p in enumerate(ph) if is_v(p)]


def tail(ph, n):
    vi = vidx(ph)
    return ph[vi[-n]:] if len(vi) >= n else None


def anchor(ph):
    ph = uk(ph)
    idx = [i for i, p in enumerate(ph) if p.endswith("1")] or [i for i, p in enumerate(ph) if p.endswith("2")]
    if idx:
        return ph, idx[-1]
    vi = vidx(ph)
    return ph, (vi[-1] if vi else None)


def stressed_vowel(ph):
    ph2, i = anchor(ph)
    return strip(ph2[i]) if i is not None else None


def key(ph, n=1, mode="perfect", stress=False):
    if n == 0:
        ph2, i = anchor(ph)
        if i is None:
            return None
        t = ph2[i:]
        if mode == "perfect":
            return tuple(strip(p) for p in t)
        if mode == "assonance":
            return tuple(strip(p) for p in t if is_v(p))
        return tuple(strip(p) if is_v(p) else CLASSES.get(strip(p), strip(p)) for p in t)
    t = tail(uk(ph), n)
    if t is None:
        return None
    if mode == "perfect":
        return tuple((p if stress else strip(p)) for p in t)
    if mode == "assonance":
        return tuple(strip(p) for p in t if is_v(p))
    if mode == "near":
        return tuple(strip(p) if is_v(p) else CLASSES.get(strip(p), strip(p)) for p in t)
    raise ValueError(mode)


_IDX = {}


def index(n, mode, stress=False):
    k = (n, mode, stress)
    if k not in _IDX:
        idx = collections.defaultdict(list)
        for w, prons in D.items():
            if not w.isalpha() or len(w) > 12:
                continue
            kk = key(prons[0], n, mode, stress)
            if kk:
                idx[kk].append(w)
        for w, p in OVR.items():
            kk = key(p.split(), n, mode, stress)
            if kk:
                idx[kk].append(w)
        _IDX[k] = idx
    return _IDX[k]


def nsyl(ph):
    return len(vidx(ph))


def rank_words(ws):
    return sorted(set(ws), key=lambda w: (len(w), w))


def cmd_pron(a):
    ph, bad = pron_phrase(a.text)
    if ph is None:
        print(f"OOV word: {bad} (add it to OVR)")
        return
    print(" ".join(ph))
    print("UK-ish:", " ".join(uk(ph)), "| syllables:", nsyl(ph))


def cmd_rhymes(a):
    ph, bad = pron_phrase(a.word)
    if ph is None:
        print(f"OOV word: {bad} (add it to OVR)")
        return
    kk = key(ph, a.n, a.mode, a.stress)
    ws = [w for w in index(a.n, a.mode, a.stress).get(kk, []) if w != a.word.lower()]
    ws = rank_words(ws)
    print(f"{a.word}: key={'-'.join(kk) if kk else None} mode={a.mode} n={a.n} matches={len(ws)}")
    print(", ".join(ws[: a.max]))


def phones_noaccent(ph):
    return [strip(p) for p in uk(ph)]


def loose(p):
    return VOICE.get(p, p)


def cmd_mosaic(a):
    ph, bad = pron_phrase(a.text)
    if ph is None:
        print(f"OOV word: {bad}")
        return
    T = phones_noaccent(ph)
    vi = [i for i, p in enumerate(T) if p in {strip(x) for x in ("AA0 AE0 AH0 AO0 AW0 AY0 EH0 ER0 EY0 IH0 IY0 OW0 OY0 UH0 UW0".split())}]
    if len(vi) < a.nsyl:
        print("phrase too short for --nsyl")
        return
    T = T[vi[-a.nsyl]:]
    if a.loose:
        T = [loose(p) for p in T]
    VSET = {strip(x) for x in ("AA0 AE0 AH0 AO0 AW0 AY0 EH0 ER0 EY0 IH0 IY0 OW0 OY0 UH0 UW0".split())}
    full = collections.defaultdict(list)     # exact phone tuple -> words
    onset = collections.defaultdict(list)    # phones from first vowel on -> words (onset free)
    for w, prons in D.items():
        if not w.isalpha() or len(w) > 10:
            continue
        P = phones_noaccent(prons[0])
        if a.loose:
            P = [loose(p) for p in P]
        full[tuple(P)].append(w)
        fv = next((i for i, p in enumerate(P) if p in VSET), None)
        if fv is not None:
            onset[tuple(P[fv:])].append(w)
    results = []

    def rec(Tr, depth, suffix_words):
        # choose the word that ends the remaining target
        for i in range(len(Tr)):
            seg = tuple(Tr[i:])
            if i == 0:
                cands = onset.get(seg, [])
            else:
                cands = full.get(seg, [])
            if i == 0:
                for w in cands[:8]:
                    results.append([w] + suffix_words)
            elif depth > 1:
                for w in cands[:5]:
                    rec(Tr[:i], depth - 1, [w] + suffix_words)
    rec(T, 3 if a.words > 2 else 2, [])
    seen, out = set(), []
    for r in results:
        t = " ".join(r)
        if len(r) >= 2 and t not in seen and t != a.text.lower():
            seen.add(t)
            out.append(t)
    out.sort(key=lambda s: (len(s.split()), len(s)))
    print(f"target tail: {' '.join(T)}  ({len(out)} cut-ups)")
    print("; ".join(out[: a.max]))


def theme_words():
    path = os.path.join(HERE, "theme_words.txt")
    cats, cur = collections.defaultdict(list), "misc"
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            cur = line[1:].strip()
            continue
        for w in line.split():
            cats[cur].append(w.replace("_", " "))
    return cats


def cmd_families(a):
    cats = theme_words()
    fam = collections.defaultdict(set)
    for cat, ws in cats.items():
        for w in ws:
            ph, bad = pron_phrase(w)
            if ph is None:
                continue
            kk = key(ph, a.n, "perfect", False)
            if kk:
                fam[kk].add(w)
    idx = index(a.n, "perfect", False)
    rows = sorted(fam.items(), key=lambda kv: (-len(kv[1]), -len(idx.get(kv[0], []))))
    shown = 0
    for kk, ws in rows:
        if len(ws) < a.min:
            continue
        print(f"-{'-'.join(kk)}  theme={len(ws)} bank={len(idx.get(kk, []))}: {', '.join(sorted(ws))}")
        shown += 1
        if shown >= a.top:
            break


def analyse_line(line, n=1):
    toks = re.findall(r"[A-Za-z']+", line)
    syl = 0
    stress = 0
    pattern = []
    oov, ban = [], []
    ends = None
    words = []
    for t in toks:
        ph = pron(t)
        lw = re.sub(r"[^a-z]", "", t.lower())
        if lw in BANNED:
            ban.append(lw)
        if ph is None:
            oov.append(t)
            continue
        s = [p[-1] for p in ph if is_v(p)]
        syl += len(s)
        for d in s:
            on = (d == "1") or (d == "2" and len(s) > 1) or (len(s) == 1 and lw not in FUNC)
            stress += 1 if on else 0
            pattern.append("X" if on else "x")
        words.append((lw, ph))
    end = words[-1] if words else None
    internal = []
    if end:
        ev = stressed_vowel(end[1])
        content = [(w, ph) for w, ph in words if w not in FUNC and nsyl(ph)]
        for w, ph in content[:-1]:
            if stressed_vowel(ph) == ev:
                internal.append(w)
        ends = key(end[1], n, "perfect")
    pairs = []
    cw = [(w, stressed_vowel(ph)) for w, ph in words if w not in FUNC and nsyl(ph)]
    for i in range(len(cw)):
        for j in range(i + 1, len(cw)):
            if cw[i][1] == cw[j][1] and cw[i][0] != cw[j][0]:
                pairs.append(f"{cw[i][0]}/{cw[j][0]}")
    return dict(carpet=stressed_vowel(end[1]) if end else None, pairs=pairs, text=line.strip(), syl=syl, stress=stress, pattern="".join(pattern), end=end[0] if end else "",
               endkey=ends, internal=internal, oov=oov, banned=ban, mate=len(re.findall(r"\bmate\b", line.lower())),
               words=[w for w, _ in words])


def depth(p1, p2):
    a, b = phones_noaccent(p1), phones_noaccent(p2)
    k = 0
    while k < min(len(a), len(b)) and a[-1 - k] == b[-1 - k]:
        k += 1
    return k


def cmd_check(a):
    chains, cur = [], []
    src = sys.stdin.read().splitlines() if a.file == "-" else open(a.file, encoding="utf-8").read().splitlines()
    for line in src:
        s = line.rstrip("\n")
        if s.strip().startswith("#"):
            continue
        if not s.strip():
            if cur:
                chains.append(cur)
                cur = []
            continue
        s = re.sub(r"^\s*\d+[.)]\s*", "", s)
        cur.append(s)
    if cur:
        chains.append(cur)
    for ci, chain in enumerate(chains, 1):
        print(f"=== chain {ci}: {len(chain)} bars")
        infos = [analyse_line(l, a.n) for l in chain]
        endph = []
        for i, inf in enumerate(infos, 1):
            flags = []
            if inf["syl"] < 5 or inf["syl"] > 14:
                flags.append("LEN")
            if inf["stress"] < 3 or inf["stress"] > 8:
                flags.append("STRESS")
            if inf["oov"]:
                flags.append("OOV:" + ",".join(inf["oov"]))
            if inf["banned"]:
                flags.append("BANNED:" + ",".join(inf["banned"]))
            print(f"{i:>2}. syl={inf['syl']:>2} acc<={inf['stress']} end={inf['end']:<10} key={'-'.join(inf['endkey']) if inf['endkey'] else '?':<12} carpet={inf['carpet']:<3} echo-of-end-vowel={','.join(inf['internal']) or '-':<12} same-vowel pairs={','.join(inf['pairs']) or '-'} {' '.join(flags)}")
            print(f"    {inf['pattern']}   | {inf['text']}")
            p = pron(inf["end"]) if inf["end"] else None
            endph.append(p)
        keys = [i["endkey"] for i in infos if i["endkey"]]
        top = collections.Counter(keys).most_common(1)
        fam = top[0] if top else (None, 0)
        print(f"-- end-key families: {len(set(keys))} distinct; most common {'-'.join(fam[0]) if fam[0] else '?'} x{fam[1]} of {len(infos)}")
        car = collections.Counter(i['carpet'] for i in infos)
        print("-- vowel carpet (stressed vowel of each end word):", ", ".join(f"{v}x{c}" for v, c in car.most_common()))
        ds = [depth(endph[i], endph[i + 1]) for i in range(len(endph) - 1) if endph[i] and endph[i + 1]]
        print(f"-- adjacent end-sound match depth (phones): {ds}")
        print(f"-- internal-rhyme bars: {sum(1 for i in infos if i['internal'])}/{len(infos)}; avg syl {sum(i['syl'] for i in infos) / len(infos):.1f}; 'mate' x{sum(i['mate'] for i in infos)}")
        reps = [w for w, c in collections.Counter(i['end'] for i in infos).items() if c > 1]
        if reps:
            print("-- repeated end words:", ", ".join(reps))


NEAR_V = [{"EH", "EY"}, {"IH", "IY"}, {"UH", "UW"}, {"AA", "AO", "AH"}, {"OW", "AO"}]
REDUCED = {"AH0", "IH0", "ER0"}


def vsim(a, b):
    """2 = same vowel, 1 = near vowel, 0 = different (stress ignored)"""
    a, b = strip(a), strip(b)
    if a == b:
        return 2
    return 1 if any(a in g and b in g for g in NEAR_V) else 0


def sylls(ph):
    """split phones into syllables: (onset, vowel, coda); single intervocalic consonant goes to the onset"""
    vi = vidx(ph)
    out, start = [], 0
    for k, i in enumerate(vi):
        nxt = vi[k + 1] if k + 1 < len(vi) else len(ph)
        mid = ph[i + 1:nxt]
        if k + 1 < len(vi):
            cut = 0 if len(mid) <= 1 else 1
            coda, rest = mid[:cut], mid[cut:]
        else:
            coda, rest = mid, []
        out.append((ph[start:i], ph[i], coda))
        start = i + 1 + len(coda)
    return out


def coda_rel(c1, c2):
    a, b = [strip(x) for x in c1], [strip(x) for x in c2]
    if a == b:
        return "perfect"
    if [VOICE.get(x, x) for x in a] == [VOICE.get(x, x) for x in b]:
        return "slant"
    if a and b and CLASSES.get(a[0]) == CLASSES.get(b[0]):
        return "slant"
    return "assonance"


def build_S(bars, quiet=False):
    S = []  # (bar, word, onset, vowel, coda, stressed)
    for b, line in enumerate(bars, 1):
        for w in re.findall(r"[A-Za-z']+", line):
            ph = pron(w)
            if ph is None:
                if not quiet:
                    print(f"OOV: {w} (add to OVR)")
                continue
            ph = uk(ph); lw = w.lower()
            ss = sylls(ph)
            for (on, v, co) in ss:
                st = v[-1] in "12" and not (lw in FUNC and len(ss) == 1)
                S.append((b, w, on, v, co, st))
    return S


def read_bars(f):
    src = sys.stdin.read().splitlines() if f == "-" else open(f, encoding="utf-8").read().splitlines()
    return [re.sub(r"^\s*\d+[.)]\s*", "", l) for l in src if l.strip() and not l.strip().startswith("#")]


NUMS = set("one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty sixty seventy eighty ninety hundred thousand grand ton".split())


def _letter(i):
    """A..Z, then AA, AB, ... so blocks longer than 8 bars still get a scheme."""
    n, s = i, ""
    while True:
        s = chr(ord("A") + n % 26) + s
        n = n // 26 - 1
        if n < 0:
            return s


def quad_stats(bars):
    S = build_S(bars, quiet=True)
    nb = len(bars)
    rows = [[x for x in S if x[0] == b] for b in range(1, nb + 1)]
    out = {}
    out["syl"] = [len(r) for r in rows]
    # end scheme on 2-syllable tails (near allowed), fallback 1-syllable vowel
    tails = [r[-2:] for r in rows]
    letters, groups = [], []
    for t in tails:
        for gi, g in enumerate(groups):
            sc = [vsim(x[3], y[3]) for x, y in zip(g, t)]
            if len(sc) == 2 and min(sc) > 0:
                letters.append(_letter(gi)); break
        else:
            groups.append(t); letters.append(_letter(len(groups) - 1))
    out["scheme2"] = "".join(letters)
    lv = [strip(r[-1][3]) if r else "-" for r in rows]
    m = {}
    out["scheme1"] = "".join(m.setdefault(v, _letter(len(m))) for v in lv)
    out["end_cover2"] = max(out["scheme2"].count(c) for c in set(out["scheme2"]))
    out["fem_end"] = sum(1 for r in rows if r and not r[-1][5])
    out["enjamb"] = sum(1 for b in bars if re.findall(r"[A-Za-z']+", b)[-1].lower() in FUNC)
    # internal rhyme: a stressed non-final syllable in the bar sharing the end's last stressed vowel
    ib = 0
    for r in rows:
        st = [x for x in r if x[5]]
        if len(st) >= 2:
            endv = strip(st[-1][3])
            if any(strip(x[3]) == endv and x[1] != st[-1][1] for x in st[:-1]):
                ib += 1
    out["internal_bars"] = ib
    # multisyllabic runs (2+ syl, exact/near, >=1 stressed, no schwas), and mosaic (one side spans a word break)
    multi, mosaic, seen = 0, 0, set()
    for n in (3, 2):
        for i in range(len(S) - n + 1):
            A = S[i:i + n]
            if len({x[0] for x in A}) > 1 or any(x[3] in REDUCED for x in A) or not any(x[5] for x in A):
                continue
            for j in range(i + n, len(S) - n + 1):
                B = S[j:j + n]
                if len({x[0] for x in B}) > 1 or any(x[3] in REDUCED for x in B) or not any(x[5] for x in B):
                    continue
                if min(vsim(x[3], y[3]) for x, y in zip(A, B)) == 0:
                    continue
                if " ".join(x[1] for x in A).lower() == " ".join(x[1] for x in B).lower():
                    continue
                if any((i + d, j + e) in seen for d in range(n) for e in range(n)):
                    continue
                for d in range(n):
                    seen.add((i + d, j + d))
                multi += 1
                if (len({x[1] for x in A}) > 1) != (len({x[1] for x in B}) > 1) or len({x[1] for x in A}) > 1:
                    mosaic += 1
    out["multisyl"] = multi
    out["mosaic"] = mosaic
    # perfect and homophone pairs among stressed syllables (different words)
    st = [x for x in S if x[5]]
    perf = homo = 0
    for p_ in range(len(st)):
        for q in range(p_ + 1, len(st)):
            x, y = st[p_], st[q]
            if x[1].lower() == y[1].lower() or strip(x[3]) != strip(y[3]):
                continue
            if coda_rel(x[4], y[4]) == "perfect":
                perf += 1
                if [strip(c) for c in x[2]] == [strip(c) for c in y[2]]:
                    homo += 1
    out["perfect_pairs"] = perf
    out["homophones"] = homo
    # alliteration: bars with a repeated stressed onset
    out["allit_bars"] = sum(1 for b in bars if allit(b))
    # vowel carpet: share of stressed syllables on the commonest vowel
    vs = [strip(x[3]) for x in st]
    top = max(set(vs), key=vs.count) if vs else "-"
    out["carpet"] = f"{top} {vs.count(top)}/{len(vs)}"
    words = [w.lower() for b in bars for w in re.findall(r"[A-Za-z']+", b)]
    cw = [w for w in words if w not in FUNC and len(w) > 3]
    out["echo_words"] = sorted({w for w in cw if cw.count(w) > 1})
    out["numbers"] = sum(1 for w in words if w in NUMS)
    rep = 0
    for b in bars:
        lb = b.lower()
        rep += len(re.findall(r"\b(\w+)-\1\b", lb))       # bye-bye, pop-pop
        rep += len(re.findall(r"\b(\w+)\s\1\b", lb))      # dot dot
        for m_ in re.finditer(r"\b(\w+)[- ](\w+)\b", lb):  # click-clack (first letter dropped)
            if m_.group(1) != m_.group(2) and len(m_.group(1)) > 2 and m_.group(1)[1:] == m_.group(2)[1:]:
                rep += 1
    out["redup"] = rep
    out["mate"] = words.count("mate")
    return out


def allit(bar):
    ons = {}
    for w in re.findall(r"[A-Za-z']+", bar):
        if w.lower() in FUNC:
            continue
        ph = pron(w)
        if not ph:
            continue
        c = strip(ph[0])
        if not is_v(ph[0]):
            ons.setdefault(c, []).append(w)
    return {k: list(dict.fromkeys(v)) for k, v in ons.items() if len({x.lower() for x in v}) > 1}


def cmd_quad(a):
    bars = read_bars(a.file)
    for k in range(0, len(bars), 4):
        q = bars[k:k + 4]
        o = quad_stats(q)
        print(f"== bars {k+1}-{k+len(q)} ==")
        for key_, v in o.items():
            print(f"  {key_:14s} {v}")


def cmd_syllmap(a):
    bars = read_bars(a.file)
    S = build_S(bars)
    print("== SYLLABLE MAP (CAPS = stressed; vowel+coda) ==")
    for b in range(1, len(bars) + 1):
        row = [x for x in S if x[0] == b]
        cells = [(strip(v) + "".join(strip(c) for c in co)).upper() if st else (strip(v) + "".join(strip(c) for c in co)).lower() for _, _, _, v, co, st in row]
        print(f"{b}. [{len(row)}] " + " ".join(cells) + f"   | {bars[b-1]}")
    print("== END TAILS (last 2 / 3 syllable vowels) ==")
    tails = []
    for b in range(1, len(bars) + 1):
        row = [x for x in S if x[0] == b]
        t2 = [strip(x[3]) for x in row[-2:]]; t3 = [strip(x[3]) for x in row[-3:]]
        tails.append(row[-2:])
        print(f"{b}. {'-'.join(t2):10s} {'-'.join(t3):14s} ({' '.join(dict.fromkeys(x[1] for x in row[-2:]))})")
    for i in range(len(tails) - 1):
        for j in range(i + 1, len(tails)):
            sc = [vsim(x[3], y[3]) for x, y in zip(tails[i], tails[j])]
            if len(sc) == 2 and min(sc) > 0:
                print(f"   2-syl end match bars {i+1}~{j+1}: {'exact' if min(sc) == 2 else 'near'}")
    print("== STRESSED SINGLE-SYLLABLE RHYMES (different words) ==")
    st = [(k, x) for k, x in enumerate(S) if x[5]]
    found = {"perfect": [], "slant": [], "assonance": []}
    for p_ in range(len(st)):
        for q in range(p_ + 1, len(st)):
            (k1, x), (k2, y) = st[p_], st[q]
            if x[1].lower() == y[1].lower() or vsim(x[3], y[3]) != 2:
                continue
            if x[0] == y[0] and abs(k1 - k2) == 1 and x[1] == y[1]:
                continue
            found[coda_rel(x[4], y[4])].append(f"{x[1]}({x[0]})~{y[1]}({y[0]})")
    for kind, lst in found.items():
        print(f"{kind} [{len(lst)}]: " + ", ".join(lst))
    print("== MULTISYLLABIC (2-4 consecutive syllables, same/near vowels, >=1 stressed, no schwas) ==")
    seen = set()
    for n in (4, 3, 2):
        for i in range(len(S) - n + 1):
            A = S[i:i + n]
            if len({x[0] for x in A}) > 1 or any(x[3] in REDUCED for x in A) or not any(x[5] for x in A):
                continue
            for j in range(i + n, len(S) - n + 1):
                B = S[j:j + n]
                if len({x[0] for x in B}) > 1 or any(x[3] in REDUCED for x in B) or not any(x[5] for x in B):
                    continue
                sc = [vsim(x[3], y[3]) for x, y in zip(A, B)]
                if min(sc) == 0:
                    continue
                if " ".join(x[1] for x in A).lower() == " ".join(x[1] for x in B).lower():
                    continue
                if any((i + d, j + e) in seen for d in range(n) for e in range(n)):
                    continue
                for d in range(n):
                    seen.add((i + d, j + d))
                tag = "exact" if min(sc) == 2 else "near"
                print(f"{n}-syl {tag}: '{' '.join(dict.fromkeys(x[1] for x in A))}'({A[0][0]}) ~ '{' '.join(dict.fromkeys(x[1] for x in B))}'({B[0][0]})  {'-'.join(strip(x[3]) for x in A)}")
    print("== ALLITERATION (word-initial consonant of content words, per bar) ==")
    for b, line in enumerate(bars, 1):
        r = allit(line)
        print(f"{b}. " + ("; ".join(f"{k}: {'/'.join(v)}" for k, v in r.items()) or "none"))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # the map prints IPA; under a pipe on
    #                                                           # Windows the default is cp1252 and the CLI
    #                                                           # dies instead of printing
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("pron"); p.add_argument("text"); p.set_defaults(f=cmd_pron)
    p = sp.add_parser("rhymes"); p.add_argument("word"); p.add_argument("--n", type=int, default=0)
    p.add_argument("--mode", default="perfect"); p.add_argument("--max", type=int, default=60)
    p.add_argument("--stress", action="store_true"); p.set_defaults(f=cmd_rhymes)
    p = sp.add_parser("mosaic"); p.add_argument("text"); p.add_argument("--nsyl", type=int, default=2)
    p.add_argument("--max", type=int, default=40); p.add_argument("--loose", action="store_true")
    p.add_argument("--words", type=int, default=2); p.set_defaults(f=cmd_mosaic)
    p = sp.add_parser("families"); p.add_argument("--n", type=int, default=0); p.add_argument("--min", type=int, default=4)
    p.add_argument("--top", type=int, default=25); p.set_defaults(f=cmd_families)
    p = sp.add_parser("check"); p.add_argument("file"); p.add_argument("--n", type=int, default=0); p.set_defaults(f=cmd_check)
    p = sp.add_parser("syllmap"); p.add_argument("file"); p.set_defaults(f=cmd_syllmap)
    p = sp.add_parser("quad"); p.add_argument("file"); p.set_defaults(f=cmd_quad)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
