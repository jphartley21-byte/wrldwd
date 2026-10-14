"""Helpers added 9 Oct 2026: British pronunciations (Britfone), word commonness (wordfreq), rhyme lists (Datamuse).
python toolkit/helpers.py freq -            # per bar: words with Zipf < 3.0 (rare: would mates know it? gate G2)
python toolkit/helpers.py uk "word or line" # British IPA from Britfone (MIT), '?' if missing
python toolkit/helpers.py tails -           # per bar: last two vowel sounds of the end word(s), British
python toolkit/helpers.py rp -              # RhymePad (Kenneth Reitz, pip rhymepad): scheme incl multi-word rhymes, rhyme groups, meter per line (US CMU + g2p)
python toolkit/helpers.py dm WORD [rhy|nry|sl] [min_freq]  # Datamuse rhymes / near rhymes / sounds-like, commonest first
"""
import json, os, re, sys, urllib.request
from wordfreq import zipf_frequency
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
VOWELS = "iɪeɛæʌɒʊəuɑɔɜa"
# CMU phones that are not vowels (match.CMU2IPA covers those), as Britfone-style IPA.
CMU_CONS = {"B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f", "G": "g", "HH": "h", "JH": "dʒ", "K": "k",
            "L": "l", "M": "m", "N": "n", "NG": "ŋ", "P": "p", "R": "ɹ", "S": "s", "SH": "ʃ", "T": "t",
            "TH": "θ", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"}
# CMU vowels -> British IPA. ONE copy: match.uk_vowels and _ovr_phones both go through cmu_vowels, because
# two copies of this mapping is exactly how "Zurich" came to be scored without its consonants.
CMU_VOW = {"AE": "æ", "AO": "ɔː", "AW": "aʊ", "AY": "aɪ", "EH": "e", "EY": "eɪ", "IH": "ɪ", "OW": "əʊ",
           "OY": "ɔɪ", "UH": "ʊ", "UW": "uː"}
_BF = None


def cmu_vowels(ph, word):
    """British (vowel, primary_stress) pairs for a CMU phone list. Shared by match.uk_vowels and the
    Britfone fallback. AA is the two-way one: British /ɑː/ in "bath/grass" words, /ɒ/ otherwise."""
    out = []
    for x in ph:
        base, st = x.rstrip("012"), x[-1] == "1"
        if base not in CMU_VOW and base not in ("AA", "AH", "ER", "IY"):
            continue
        if base == "AA":
            first = next((c for c in word if c in "aeiou"), "o")
            v = "ɑː" if first == "a" else "ɒ"
        elif base == "AH":
            v = "ʌ" if st else "ə"
        elif base == "ER":
            v = "ɜː" if st else "ə"
        elif base == "IY":
            v = "iː" if st else "i"
        else:
            v = CMU_VOW[base]
        out.append((v, st))
    return out


def britfone():
    global _BF
    if _BF is None:
        _BF = {}
        with open(os.path.join(HERE, "britfone.csv"), encoding="utf8") as f:
            for line in f:
                if "," not in line:
                    continue
                w, p = line.rstrip("\n").split(",", 1)
                w = re.sub(r"\(\d+\)$", "", w.strip()).lower()
                _BF.setdefault(w, p.strip().split())
    return _BF


def words(text):
    return re.findall(r"[a-zA-Zå']+", text)


def _ovr_phones(w):
    """British phones for a word Britfone does NOT have, from the CMU dictionary plus the project's OVR
    table (rhyme_tools), converted to the same IPA tokens Britfone returns.

    Why this exists (13 Oct 2026): without it, word_phones fell through to a VOWELS-ONLY fallback, so every
    place name missing from Britfone silently lost its consonants. "Zurich" was scored as the vowels (ʊ, ɪ)
    with no final /k/, which capped Zurich ~ traffic / Munich / panic at 0.80 ("slant") even though all four
    share the -ɪk rime -- and the same applied to Porto, Bordeaux, Ljubljana, Majorca and the original's own
    "Spoons". The vowel part comes from match.uk_vowels so the two cannot drift apart; the consonants are the
    standard CMU phoneset.
    """
    from rhyme_tools import pron, uk as drop_r, is_v
    ph = pron(w)
    if not ph:
        return None
    vowels = cmu_vowels(ph, w)
    out, vi = [], 0
    for p in drop_r(ph):
        if is_v(p):
            if vi < len(vowels):
                v, stressed = vowels[vi]
                vi += 1
                out.append(("ˈ" if stressed else "") + v)
            continue
        cons = CMU_CONS.get(p.rstrip("012"))
        if cons:
            out.append(cons)
    return out or None


def uk(word):
    """British phones from the Britfone DICTIONARY, or None. Dictionary membership is the point: vocab.py
    decides whether a candidate is junk ("no commonness and no British dictionary entry") with it, so it must
    not resolve words Britfone does not have. Use uk_phones when you want phones for scoring."""
    return britfone().get(word.lower().strip("'"))


def uk_phones(word):
    """British phones for SCORING: the Britfone dictionary, else the CMU dictionary plus the project's OVR
    table (see _ovr_phones for why the fallback is needed)."""
    w = word.lower().strip("'")
    return britfone().get(w) or _ovr_phones(w)


def vowels_of(phones):
    return [p.replace("ˈ", "").replace("ˌ", "") for p in phones if any(c in VOWELS for c in p)]


def lines_in():
    return [l.strip() for l in sys.stdin.read().splitlines() if l.strip() and not l.startswith(("[", "#", "("))]


def cmd_freq():
    for i, l in enumerate(lines_in(), 1):
        rare = [(w, round(zipf_frequency(w.lower(), "en"), 1)) for w in words(l)]
        rare = [f"{w}({z})" for w, z in rare if z < 3.0]
        print(f"{i:>2}. {'RARE: ' + ', '.join(rare) if rare else 'ok'}   | {l}")


def cmd_tails():
    for i, l in enumerate(lines_in(), 1):
        ws = words(l)
        vs, miss = [], []
        for w in reversed(ws):
            p = uk(w)
            if p is None:
                miss.append(w)
                break
            vs = vowels_of(p) + vs
            if len(vs) >= 2:
                break
        print(f"{i:>2}. {'-'.join(vs[-2:]) if not miss else '? ' + miss[0]:<12} | {l}")


def cmd_dm(word, rel="rhy", minf="1"):
    key = {"rhy": "rel_rhy", "nry": "rel_nry", "sl": "sl"}[rel]
    url = f"https://api.datamuse.com/words?{key}={urllib.request.quote(word)}&md=fs&max=200"
    data = json.load(urllib.request.urlopen(url, timeout=15))
    out = []
    for d in data:
        f = float(next((t[2:] for t in d.get("tags", []) if t.startswith("f:")), 0))
        if f >= float(minf) and d["word"] != word:
            out.append((f, d["word"], d.get("numSyllables")))
    for f, w, n in sorted(out, reverse=True)[:60]:
        print(f"{w} ({n}syl, {f:.1f}/M)", end="; ")
    print()


def cmd_rp():
    import io, contextlib
    with contextlib.redirect_stderr(io.StringIO()):
        import rhymes
    text = chr(10).join(lines_in())
    d = rhymes.analyze_text(text)
    L = d["lines"]
    for st in d["stanzas"]:
        print("scheme", st["scheme"], "lines", st["lines"][0] + 1, "-", st["lines"][-1] + 1)
    groups = {}
    for t in d["tokens"]:
        groups.setdefault(t["g"], []).append(f"{L[t['l']][t['s']:t['e']]}({t['l'] + 1}{'E' if t['end'] else ''})")
    for g in d["groups"]:
        print(f"group {g['id']} [{g['sound']}] {'slant' if g['slant'] else 'perfect'} {g['strength']}: " + ", ".join(groups.get(g["id"], [])))
    for m in d["meter"]:
        print(f"{m['l'] + 1:>2}. {m['syl']}syl {m['stress']} {m['label']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit()
    if a[0] == "freq": cmd_freq()
    elif a[0] == "tails": cmd_tails()
    elif a[0] == "uk": print(" | ".join(f"{w}: {' '.join(uk(w) or ['?'])}" for w in words(" ".join(a[1:]))))
    elif a[0] == "dm": cmd_dm(*a[1:])
    elif a[0] == "rp": cmd_rp()
