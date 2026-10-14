"""sense_checks.py - the two gate holes Joe found: bars that are lists rather than thoughts, and
blocks whose bars open new scenes instead of developing one.

Both are calibrated the same way as everything else: the ORIGINAL's own block sets the par, so the
original only just passes and a block that hops more, or lists more, than the original does at that
position fails.

  list_fragments(bars)  bars chaining 2+ "and/or" between noun phrases with no finite verb
  hops(bars)            consecutive bars with no link at all: no shared content word, no pronoun
                        antecedent, no place chain, no connective
  report(bars, block_start)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

import coherence_gate as cg      # noqa: E402
import meaning_gate as mg        # noqa: E402

CONNECTIVES = {"and", "so", "then", "but", "cos", "because", "till", "until", "then", "when",
               "while", "still", "yet", "though", "if", "as", "now"}
FINITE_HINTS = ("is", "are", "was", "were", "am", "be", "been", "has", "have", "had", "do", "does",
                "did", "will", "would", "can", "could", "might", "may", "must", "shall", "should",
                "says", "said", "gets", "got", "goes", "went", "holds", "held", "kept", "keeps",
                "pays", "paid", "takes", "took", "chucks", "chucked", "wants", "needs", "needed")

FIELDS = {
    "vehicle": "brake bike chain tyre engine tank saddle panniers helmet mudguard pillion ride rode",
    "weather": "rain snow fog wind sun frost cloud storm sleet hail drizzle heat cold dry wet",
    "food": "beer lager pint chips guava lava chilli coffee tea sandwich bread bacon roll",
    "money": "cash paid pay owes owed price fare quid pound twenty fifty money slate invoice",
    "authority": "border customs copper gendarme officer passport stamp barrier gate officer desk",
    "transport": "ferry boat train bus tram plane flight rail tunnel bridge coach port harbour",
    "admin": "orders invoice receipt ledger form book bookkeeping notice papers parcel postage",
    "place": "lagos vegas porto oslo douro gaia bilbao bordeaux larrau burgos fermoselle",
    "lodging": "hostel dorm bed bunk room campsite tent pitch hostelry digs",
}


def fields(bars):
    """Coarse lexical fields present in the block, with the words that triggered them."""
    hits = {}
    for f, words in FIELDS.items():
        w = [b for b in bars for b in [b]]
        found = sorted({x.lower() for bar in bars for x in cg.words(bar)
                        if x.lower().strip(",.") in words.split()})
        if found:
            hits[f] = found
    return hits


def field_spread(bars):
    return len(fields(bars))


def list_fragments(bars):
    """Bars that are a chain of items rather than a statement: a list.

    Two shapes count, because the first version only caught the second one and let a comma list
    through:
      * 2+ "and/or" joins with no finite verb
      * 2+ comma breaks with no finite verb (a comma-separated list of things)
    The par is the original's own count for the same block, so the original only just passes.
    """
    out = []
    for i, b in enumerate(bars, 1):
        low = " " + b.lower() + " "
        conj = len(re.findall(r"\b(and|or)\b", low))
        commas = b.count(",") + b.count(";")
        finite = any(re.search(rf"\b{h}\b", low) for h in FINITE_HINTS)
        if not finite and (conj >= 2 or commas >= 2):
            out.append(i)
    return out


def links(prev, cur):
    """Is there any link from prev to cur? shared content word, pronoun with an antecedent, a
    connective, or a shared place."""
    pw, cw = {w.lower() for w in cg.words(prev)}, {w.lower() for w in cg.words(cur)}
    shared = {w for w in pw & cw if w not in cg.FUNC and len(w) > 2}
    if shared:
        return ("word", sorted(shared)[0])
    # near-identical word (favours/flavours - the original's register flip)
    for a in pw:
        for b in cw:
            if len(a) > 4 and len(b) > 4 and (a in b or b in a) and abs(len(a) - len(b)) <= 2:
                return ("echo", f"{a}/{b}")
    low = " " + cur.lower() + " "
    if any(re.search(rf"\b{c}\b", low) for c in CONNECTIVES):
        return ("connective", "connective")
    if re.search(r"\b(he|she|they|them|his|her|their|it|that|this)\b", low):
        return ("pronoun", "pronoun")
    pl = {w.lower() for w in cg.words(prev)} & mg.PLACES
    cl = {w.lower() for w in cg.words(cur)} & mg.PLACES
    if pl and cl:
        return ("place", f"{sorted(pl)[0]}/{sorted(cl)[0]}")
    return (None, None)


def hops(bars):
    """Consecutive bars with no link at all - each one opens a new scene."""
    out = []
    for i in range(1, len(bars)):
        kind, _ = links(bars[i - 1], bars[i])
        if kind is None:
            out.append((i, i + 1))
    return out


def content_novelty(bars):
    """How much NEW material the block carries: content words (non-function words) that appear for the
    first time, and the ones it repeats.

    Par = the original's own block, which repeats none of its content words: its list bar and its
    register flip both add new material. A block that restates its own words is saying less than the
    original says in the same four bars - the failure that got through every other gate.
    """
    seen, repeats, new = {}, [], 0
    for i, b in enumerate(bars, 1):
        for w in [w.lower() for w in cg.words(b) if w.lower() not in cg.FUNC]:
            if w in seen:
                repeats.append((i, w))
            else:
                new += 1
            seen[w] = seen.get(w, 0) + 1
    return new, repeats


def proper_nouns(bars):
    """Mid-line capitalised words: the block's named places or people. A sentence-initial capital is
    just grammar, so it is not evidence. Par = the original's block, which names two - one inside the
    greeting frame and one in the closer, outside it."""
    out = []
    for i, b in enumerate(bars, 1):
        for j, tok in enumerate(b.split()):
            t = tok.strip(",.;:")
            t = re.sub(r"'s$", "", t)                      # "Bristol's" is still a place
            if j and len(t) > 2 and t[:1].isupper() and t.replace("-", "").isalpha():
                out.append((i, t))
    return out


def report(bars, block_start=None):
    print(f"  list-fragment bars: {list_fragments(bars)}")
    print(f"  hops (no link): {hops(bars)}")
    for i in range(1, len(bars)):
        kind, what = links(bars[i - 1], bars[i])
        print(f"    {i}->{i+1}: {kind or 'NO LINK'} {what or ''}")


if __name__ == "__main__":
    import io
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    bars = ([l.strip() for l in io.open(src, encoding="utf8") if l.strip()]
            if src != "-" else [l.strip() for l in sys.stdin if l.strip()])
    report(bars)
