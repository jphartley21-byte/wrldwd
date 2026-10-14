"""Multi-word rhyme finder (14 Oct 2026, Joe: "Honda wins" rhymes with "gone to bins").

THE GAP. The graders already accept that pair (match.best_end 1.00, rapfit.chain_best depth 3), but nothing could
FIND one: rhyme_tools.py mosaic needs every later segment to match the target's phones exactly (so "bins" can never
stand for "wins"), and the verse menu offers single dictionary words. A rhyme needs the vowels and the endings to
agree; the consonant a later syllable STARTS on is free, and the short vowels in the middle (da / to) are weak, so
a function word can fill them.

HOW. Index ~20k common words by the vowel class of each syllable (unstressed schwa / short i collapse to one weak
class). Split the target's last k syllables into 1-3 chunks, one word per chunk:
  - the first word carries the target's stressed vowel and the consonant that closes it (n in Hon-da);
  - the middle chunks are FUNCTION words only (to, the, of, for, and, a ...);
  - the last word matches the target's final ending (voicing ignored: s~z, t~d);
  - starting consonants are free.
Every candidate is then re-scored by the repo's own graders and kept only at match.best_end >= 0.95 and
rapfit.chain_best depth >= k. The index and the search take a few seconds.

WHAT IT DOES NOT DO: read for sense. The prototype's first ranking was mostly nonsense ("ron to twins", "food are
news"), so candidates are filtered (given names and surnames, fragments, function words in the wrong slot) and
ranked toward shapes people say (content + function + content, content + function) and toward the song's own world
(places, local words, theme words). They are still PHONETIC matches that nobody has read. Every candidate is
labelled UNREAD; `--sense "the bar's claim"` asks a model (needs a key) which can end a sentence about it.

  python toolkit/multirhyme.py "Honda wins" [--tail 3] [--top 40] [--min-zipf 3.8] [--shape cfc,cf,cc]
  python toolkit/multirhyme.py "Honda wins" --echo          mid-bar words that echo the stressed syllable
  python toolkit/multirhyme.py --selftest
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

WEAK_V = {"ə", "ɪ", "i"}
MIN_ZIPF = 3.3          # low enough to keep "bins" (3.4), Joe's own example; common words rank first anyway
NAME_ZIPF = 5.0          # a given name or surname this common is also an ordinary word (will, bill, mark)
POOL_CAP = 60            # words kept per chunk slot, commonest first
SCORE_CAP = 40000        # phrases scored by the repo's graders
MIN_BEST_END = 0.95

# weak words: the only words allowed in the middle of a phrase
FUNC = frozenset("""to the a of on in at and for from by with my her his our as an up off it he she we they you i us
them be is was are am or but so no not that this these those your their its if too""".split())
# function words that may END a phrase (the original's own V1 17-24 ends on in / him / it)
END_FUNC = frozenset("in on out up off it him her them me you us".split())
# contractions and spelling-speak that wordfreq counts as words but nobody writes into a bar
FRAGMENTS = frozenset("""mins ins wanna gonna gotta kinda outta lemme gimme ya em ur thru tho cuz ok okay nah yeah yep
non wan con cons pos negs ish ing ed er est don didn doesn isn aren wasn weren couldn wouldn shouldn hasn haven hadn
mustn ain ll ve re bon""".split())
# first names and surnames that entities.txt does not carry (its given-name list is a partial Wiktionary pull) and
# that wordfreq scores as ordinary words; words that are also names (will, bill, mark, rob, jack) are left alone
NAMEISH = frozenset("""ron jon john ronald ken ben tom jim tim dan sam ian roy len les lou mike nick phil paul ross russ ryan
sean steve stu ted tony troy vic wes zac zach kev dave gaz baz hughes cruz jones smith clarke evans lewis""".split())
# bridge words in the order they sound natural between two content words; the rest (are, was, that, them ...) come last
BRIDGE_ORDER = ("to", "of", "for", "and", "the", "a", "in", "on", "at", "with", "from", "by", "my", "your", "his", "her", "our")
MAX_PER_PAIR, MAX_PER_END, MAX_PER_FIRST = 2, 4, 3
# HYGIENE for pairings nobody reads before they reach the writer (14 Oct 2026): group-identity nouns and slurs are kept out
# of random word-pairs ("cute to jews" surfaced in a scooter-queues run). This is not the repo's pool policy: swearing and
# vulgar slang are untouched. The slurs are stored rot13 so the source file does not spell them out.
GROUP_WORDS = frozenset("jews jewish muslim muslims christian christians hindu hindus sikh sikhs arabs asians africans blacks whites gays".split())
_SLURS_ROT13 = "avtten avttn snttbg cnxv puvax fcvp xvxr qlxr genaal eroneq erneqf zbatby ergneq".split()
HYGIENE = GROUP_WORDS | frozenset(__import__("codecs").decode(w, "rot13") for w in _SLURS_ROT13)
_VOICE = {"s": "z", "t": "d", "k": "g", "f": "v", "p": "b", "ʃ": "ʒ", "θ": "ð", "tʃ": "dʒ"}

_INDEX: dict | None = None
_NAMES: set | None = None


def _norm(cs) -> list:
    return [_VOICE.get(c, c) for c in cs]


def _names() -> set:
    """given names and surnames from entities.txt (single words, lower case)."""
    global _NAMES
    if _NAMES is None:
        _NAMES = set()
        path = os.path.join(HERE, "entities.txt")
        if os.path.exists(path):
            for line in open(path, encoding="utf-8-sig", errors="replace"):
                p = [x.strip() for x in line.split("|")]
                if len(p) >= 2 and not line.startswith("#") and p[1] in ("given-name", "surname") and " " not in p[0]:
                    _NAMES.add(p[0].lower())
    return _NAMES


def cls(v: str, stressed: bool) -> str:
    return "W" if (v in WEAK_V and not stressed) else v


def index(min_zipf: float = MIN_ZIPF, top: int = 25000) -> dict:
    """{word: {z, sy, v, st}} for common, speakable words. Cached per process."""
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    import phon
    import wordfreq
    names = _names()
    out = {}
    for w in wordfreq.top_n_list("en", top):
        if not w.isalpha() or not 1 <= len(w) <= 9 or w in FRAGMENTS or w in HYGIENE or (len(w) < 3 and w not in FUNC):
            continue
        z = wordfreq.zipf_frequency(w, "en")
        if w in NAMEISH or (w in names and z < NAME_ZIPF):
            continue                                   # ron, jon, hughes, cruz: names, not words in a bar
        if w not in FUNC and z < min_zipf:
            continue
        try:
            sy = phon.syllables(w)
        except Exception:  # noqa: BLE001
            continue
        if not sy:
            continue
        out[w] = {"z": z, "sy": sy, "v": tuple(s[0] for s in sy), "st": tuple(bool(s[1]) for s in sy)}
    _INDEX = out
    return out


def _world() -> dict:
    """places / local words / theme words of the song (reservoir's loaded sets); empty if the tools are missing."""
    try:
        import bank
        import carpet
        import reservoir
        return reservoir._loaded_sets(carpet, bank)
    except Exception:  # noqa: BLE001
        return {}


def shape_of(words: list[str]) -> str:
    """cfc = content + function + content; cf = content + function ('double it'); cc = two content; ccc / other."""
    f = [w in FUNC for w in words]
    if len(words) == 3 and not f[0] and f[1] and not f[2]:
        return "cfc"
    if len(words) == 2 and not f[0] and f[1]:
        return "cf"
    if len(words) == 2 and not f[0] and not f[1]:
        return "cc"
    if len(words) == 1:
        return "one"
    return "other"


SHAPE_RANK = {"cfc": 0, "cf": 1, "cc": 2, "one": 3, "other": 4}


def find(target: str, k: int | None = None, min_zipf: float = MIN_ZIPF, shapes=None, top: int = 40) -> list[dict]:
    """phrases whose last k syllables rhyme with the target's. top=0 returns all that passed the graders."""
    import match
    import phon
    from ww.write import rapfit
    idx = index(min_zipf)
    tsy = phon.syllables(target)
    k = k or min(len(tsy), 4)
    tsy = tsy[-k:]
    if len(tsy) < k:
        return []
    T = [cls(s[0], s[1]) for s in tsy]
    first_c = _norm(tsy[0][2][:1])
    last_c = _norm(tsy[-1][2])
    tgt_words = {w.lower() for w in target.replace("'", " ").split()}

    def chunk_ok(w: str, a: int, b: int) -> bool:
        m = idx[w]
        if len(m["v"]) != b - a or [cls(v, s) for v, s in zip(m["v"], m["st"])] != T[a:b]:
            return False
        if b == k and _norm(m["sy"][-1][2]) != last_c:
            return False
        if a == 0 and _norm(m["sy"][0][2][:1]) != first_c:
            return False
        return True

    cand: dict[tuple, list] = defaultdict(list)
    for w in idx:
        for a in range(k):
            for b in range(a + 1, k + 1):
                if not chunk_ok(w, a, b):
                    continue
                middle = 0 < a and b < k
                if middle and w not in FUNC:
                    continue
                if not middle and w in FUNC and not (b == k and w in END_FUNC):
                    continue                              # first words are content; last may be in / it / him ...
                cand[(a, b)].append(w)

    phrases = set()
    for cuts in itertools.chain.from_iterable(itertools.combinations(range(1, k), r) for r in range(0, k)):
        pts = [0, *cuts, k]
        sp = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        pools = [sorted(cand.get(c, []), key=lambda w: -idx[w]["z"])[:POOL_CAP] for c in sp]
        if any(not p for p in pools):
            continue
        for combo in itertools.product(*pools):
            if tgt_words & set(combo) or len(set(combo)) < len(combo):
                continue
            phrases.add(" ".join(combo))
            if len(phrases) >= SCORE_CAP:
                break

    world = _world()
    loaded = set().union(*[world.get(x, set()) for x in ("place", "local", "theme")]) if world else set()
    want = set(shapes) if shapes else None
    out = []
    for p in phrases:
        ws = p.split()
        sh = shape_of(ws)
        if want and sh not in want:
            continue
        try:
            be = match.best_end(target, p)
            if be < MIN_BEST_END:
                continue
            depth = rapfit.chain_best(rapfit._syl(target), rapfit._syl(p))["depth"]
            rs = rapfit.score(target, p)["score"]
        except Exception:  # noqa: BLE001
            continue
        if depth < k:
            continue
        zs = [idx[w]["z"] for w in ws if w not in FUNC]
        out.append({"phrase": p, "best_end": round(be, 2), "rapfit": round(rs, 2), "depth": depth, "shape": sh,
                    "min_zipf": round(min(zs), 1) if zs else 9.0, "world": any(w in loaded for w in ws)})
    def bridge(r):
        ws = r["phrase"].split()
        return BRIDGE_ORDER.index(ws[1]) if r["shape"] == "cfc" and ws[1] in BRIDGE_ORDER else len(BRIDGE_ORDER)

    # shape first, then the natural bridge word, then how common the rarest content word is (in half-point buckets so the
    # song's own world can break ties inside a bucket without promoting a rare foreign word over an everyday one)
    out.sort(key=lambda r: (SHAPE_RANK[r["shape"]], bridge(r), -round(r["min_zipf"] * 2) / 2, not r["world"], -r["best_end"], r["phrase"]))
    return _diversify(out, top) if top else out


def _diversify(rows: list[dict], top: int) -> list[dict]:
    """one pair of content words should not fill the page with every function word: at most MAX_PER_PAIR bridges per
    (first, last), MAX_PER_END phrases per final word and MAX_PER_FIRST per first word."""
    pair: dict = defaultdict(int)
    end: dict = defaultdict(int)
    first: dict = defaultdict(int)
    keep = []
    for r in rows:
        ws = r["phrase"].split()
        pk, ek, fk = (ws[0], ws[-1]), ws[-1], ws[0]
        if pair[pk] >= MAX_PER_PAIR or end[ek] >= MAX_PER_END or first[fk] >= MAX_PER_FIRST:
            continue
        pair[pk] += 1
        end[ek] += 1
        first[fk] += 1
        keep.append(r)
        if len(keep) >= top:
            break
    return keep


def stock(target: str, k: int | None = None, top: int = 12) -> list[dict]:
    """REAL stock phrases (toolkit/phrases.txt + phrases_raw.txt, ~7k) whose tail rhymes the target's last k syllables.
    Natural English by construction, so this list is read-ready where find() is not; it is thin, so use both."""
    import bank
    import match
    import phon
    from ww.write import rapfit
    k = k or min(len(phon.syllables(target)), 4)
    tgt_words = {w.lower() for w in target.replace("'", " ").split()}
    out, seen = [], set()
    for r in bank.load_phrases():
        ph = r["phrase"].lower()
        ws = ph.split()
        if ph in seen or tgt_words & set(ws) or len(ws) < 2 or HYGIENE & set(ws):
            continue
        seen.add(ph)
        try:
            if len(phon.syllables(ph)) < k:
                continue
            be = match.best_end(target, ph)
            if be < MIN_BEST_END:
                continue
            depth = rapfit.chain_best(rapfit._syl(target), rapfit._syl(ph))["depth"]
        except Exception:  # noqa: BLE001
            continue
        if depth >= k:
            out.append({"phrase": ph, "best_end": round(be, 2), "depth": depth, "sense": r.get("sense", "")})
    out.sort(key=lambda x: (-x["depth"], -x["best_end"], len(x["phrase"])))
    return out[:top] if top else out


def echo_words(word: str, n: int = 12, min_zipf: float = MIN_ZIPF) -> list[str]:
    """MID-BAR echoes (internal rhyme): content words sharing the stressed vowel and the consonant that closes it."""
    import phon
    idx = index(min_zipf)
    sy = phon.syllables(word)
    st = next((s for s in sy if s[1]), sy[0] if sy else None)
    if not st:
        return []
    c0 = _norm(st[2][:1])
    world = _world()
    loaded = set().union(*[world.get(x, set()) for x in ("place", "local", "theme")]) if world else set()
    rows = []
    for w, m in idx.items():
        if w == word.lower() or w in FUNC or len(m["v"]) > 3:
            continue
        for s in m["sy"]:
            if s[1] and s[0] == st[0] and _norm(s[2][:1]) == c0:
                rows.append((w not in loaded, abs(m["z"] - 4.4), w))
                break
    rows.sort()
    return [w for _a, _b, w in rows[:n]]


def sense_filter(cands: list[dict], claim: str, llm, model: str | None = None, keep_max: int = 20) -> list[dict]:
    """ask a model which phrases can end a sentence about `claim` without being nonsense. `llm` is a ww.llm.LLM
    (or anything with .complete(Request) -> object with .parsed). Cached by the client at temperature 0."""
    from ww.llm import Request
    if model is None:
        from ww.write import evolve
        model = evolve.WRITER
    listing = "\n".join(f"{i + 1}. {c['phrase']}" for i, c in enumerate(cands))
    req = Request(model=model, system="You check rhyme candidates for a deadpan British rap. Return JSON only.",
                  messages=[{"role": "user", "content": (
                      f"A bar must end on one of these phrases and be about: {claim}\nKeep ONLY the phrases that read as ordinary "
                      f"English and could finish a sentence about that, without being nonsense or a list of names. "
                      f"Return {{\"keep\": [numbers]}}.\n\n{listing}")}],
                  max_tokens=400, effort=None, temperature=0, stage="multirhyme_sense", scope="write",
                  schema={"type": "object", "required": ["keep"], "properties": {"keep": {"type": "array", "items": {"type": "integer"}}}})
    res = llm.complete(req, use_cache=True)
    keep = [i for i in ((res.parsed or {}).get("keep") or []) if isinstance(i, int) and 1 <= i <= len(cands)]
    return [cands[i - 1] for i in keep][:keep_max]


def selftest() -> tuple[bool, str]:
    problems = []
    if shape_of(["gone", "to", "bins"]) != "cfc" or shape_of(["double", "it"]) != "cf" or shape_of(["food", "news"]) != "cc":
        problems.append("shape_of misclassifies")
    if _norm(["s", "t"]) != ["z", "d"]:
        problems.append("voicing must be ignored on endings")
    res = find("Honda wins", 3, top=0)
    phrases = {r["phrase"] for r in res}
    if "gone to bins" not in phrases:
        problems.append("Joe's pair (Honda wins ~ gone to bins) must be among the candidates")
    if any(r["best_end"] < MIN_BEST_END or r["depth"] < 3 for r in res):
        problems.append("every candidate must clear the repo's own graders (best_end >= 0.95, depth >= k)")
    if {"ron to twins", "jon you skins", "wanna pins"} & phrases:
        problems.append("given names and fragments must be filtered out")
    idx = index()
    for r in res:
        ws = r["phrase"].split()
        if len(ws) == 3 and ws[1] not in FUNC:
            problems.append(f"a content word in the middle slot: {r['phrase']}")
            break
    if not res or res[0]["shape"] != "cfc":
        problems.append("content + function + content must rank first")
    if "jews" in idx or any(w in idx for w in HYGIENE):
        problems.append("group-identity words and slurs must stay out of auto-generated pairings")
    if "blues and twos" not in {x["phrase"] for x in stock("scooter queues", 3, top=0)}:
        problems.append("the stock-phrase source must find 'blues and twos' for 'scooter queues' (a real phrase, depth 3)")

    class _Res:
        parsed = {"keep": [2, 99]}

    class _FakeLLM:
        def complete(self, req, use_cache=True):
            return _Res()

    try:
        got = sense_filter([{"phrase": "ron to twins"}, {"phrase": "gone to bins"}], "binning a Honda", _FakeLLM(), model="x")
        if [g["phrase"] for g in got] != ["gone to bins"]:
            problems.append(f"sense_filter must keep only valid indices: {got}")
    except ImportError:
        pass
    return (not problems, "; ".join(problems) if problems else
            f"Joe's pair is found among {len(res)} candidates for 'Honda wins' (index {len(idx)} words); names, fragments and "
            f"content-word middles are filtered")


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--tail", type=int, default=None, help="syllables to rhyme (default: the target's length, max 4)")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--min-zipf", type=float, default=MIN_ZIPF)
    ap.add_argument("--shape", default="", help="comma list of cfc,cf,cc,one,other")
    ap.add_argument("--echo", action="store_true", help="mid-bar echo words for internal rhyme")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        ok, msg = selftest()
        print(("MULTIRHYME SELFTEST PASSED: " if ok else "MULTIRHYME SELFTEST FAILED: ") + msg)
        return 0 if ok else 1
    if not a.target:
        ap.error("target required")
    if a.echo:
        print(f"mid-bar echoes of the stressed syllable in '{a.target}': " + ", ".join(echo_words(a.target, a.top)))
        return 0
    st = stock(a.target, a.tail, 10)
    print(f"'{a.target}': STOCK PHRASES that rhyme the same tail ({len(st)} shown; real idioms, read-ready): "
          + ("; ".join(f"{x['phrase']} [{x['sense']}]" if x['sense'] else x['phrase'] for x in st) or "none"))
    res = find(a.target, a.tail, a.min_zipf, [s for s in a.shape.split(",") if s] or None, a.top)
    print(f"'{a.target}': {len(res)} shown. PHONETIC MATCHES ONLY, UNREAD for sense (best_end >= {MIN_BEST_END}, depth >= tail). "
          f"[W] = uses the song's own places / local / theme words")
    for r in res:
        print(f"  {r['phrase']:<26} {r['shape']:<5} best_end {r['best_end']:.2f}  rapfit {r['rapfit']:.2f}  depth {r['depth']}  "
              f"min-zipf {r['min_zipf']}{'  [W]' if r['world'] else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
