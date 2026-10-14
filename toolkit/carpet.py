"""carpet.py: the Phase-A end-word tool. Pick the SOUND first, then write the words.

Why it exists (13 Oct 2026). Every regression in this song came from choosing an end word for its
vowel and then bending a sentence onto it. The fix is to choose a whole SET of end words that
satisfies the slot's measured target -- ending shape, syllables, and a carpet where every required
pair measures >= the threshold -- BEFORE any line is written. That is a search, not a judgement, so
it runs on CPU in seconds and never proposes a rhyme the grader rejects.

What it reads
  benchmark/original_profile.json   per-bar syllable target, end vowels, scheme, measured carpet
  benchmark/flow_template.json      per-bar end SHAPE (|Sw, |S, ~S) measured from the original's audio
  material/*.md                     TRUE places, with the file that documents them
  toolkit/theme_words.txt           the song's own vocabulary
  toolkit/local_words.txt           the code-switch supply
  toolkit/entities.txt              names (cities, towns, bands, films) as extra end-word material
  rhyme_tools.OVR                   places/slang with hand-added pronunciations
  bank.words_by_vowel               common words whose final tail starts on the frame's vowel

What it guarantees about a set it prints
  * every pair the by-ear scheme requires scores >= --threshold on match.best_end (aim: >= --aim)
  * if the slot's own measured carpet is complete (share 1.0), the whole slot is one clique
  * every end word carries the bar's ending shape, unless it is printed as a relaxed fallback
  * at least --places TRUE places (documented in material/) unless none can be found, which is said
  * the end word leaves at least one syllable of lead-in inside the bar's own length

usage
  python toolkit/carpet.py --slot "Hook 9-16"
  python toolkit/carpet.py --slot "V2 1-8" --threshold 0.78 --aim 0.95 --top 12
  python toolkit/carpet.py --selftest
Output is cached to benchmark/carpets_<slot>.json (slot name slugged).
"""

import argparse
import itertools
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import bank                      # noqa: E402
import flow_fit as ff            # noqa: E402
import match as mt               # noqa: E402
import phon                      # noqa: E402
import rhyme_tools as rt         # noqa: E402

PROFILE = os.path.join(ROOT, "benchmark", "original_profile.json")
TEMPLATE = os.path.join(ROOT, "benchmark", "flow_template.json")
MATERIAL = os.path.join(ROOT, "material")
MATERIAL_FILES = ["travel_history.md", "place_specifics.md", "place_sound_families.md"]
THEME = os.path.join(HERE, "theme_words.txt")
LOCAL = os.path.join(HERE, "local_words.txt")
ENTITIES = os.path.join(HERE, "entities.txt")

# Headers, column names, weekday/month names and register words that capitalise in the material files
# but are not places. Kept short and explicit so the flag is a claim about the SOURCE, not a guess.
STOP_PLACE = set("""year trip dates type source conf holiday holiday city backpacking festival rail motorbike
coastal family wedding hike weekend camping stopover staycation interrail seagate google photos gmail
calendar strava chrome time machine mac uk fr es de nz au it nl be us status privacy confidence timeline
coverage standouts music movies new zealand lads itinerary eurotrip the and jan feb mar apr may jun jul aug
sep oct nov dec monday tuesday wednesday thursday friday saturday sunday jane status gaps plan objective
shortlist bookings everything nothing but one read first day days trip trips trip notes note drive phone
exif gps photos photo from into then there here when where what who why how joe mate mates lads boys
holidays city city break break week weeks month months home back out on in at by to of the a an""".split())


def slug(slot):
    return re.sub(r"[^A-Za-z0-9]+", "_", slot).strip("_")


# ---------------------------------------------------------------- target

def slot_target(slot):
    """The slot's measured target: per-bar syllable length, end shape, end vowels; plus scheme + carpet."""
    prof = json.load(open(PROFILE, encoding="utf8"))[slot]
    tmpl = json.load(open(TEMPLATE, encoding="utf8"))["bars"]
    import check_all
    start, n = check_all.SLOTS[slot], len(prof["bars"])
    bars = tmpl[start - 1:start - 1 + n]
    targets = []
    for i, b in enumerate(prof["bars"]):
        t = bars[i] if i < len(bars) else {}
        keys = prof["keys"][i]
        shape = (t.get("end_shape") or "")
        targets.append({
            "bar": i + 1,
            "syl": t.get("syl") or b["syl"],
            "shape": shape or None,
            "shape_class": shape[1:] if shape else None,
            "marker": shape[:1] if shape else None,
            "vowels": list(keys[0]) if keys else [],
            "vowel": keys[0][0] if keys else None,       # the STRESSED syllable carries the rhyme
        })
    scheme = prof.get("scheme") or mt.MANUAL_SCHEME.get(slot, "")
    return {"slot": slot, "targets": targets, "scheme": scheme,
            "manual_scheme": mt.MANUAL_SCHEME.get(slot, ""),
            "carpet": prof.get("carpet", {}),
            "rhyme_map": prof.get("rhyme_map", []),   # the pairs the ORIGINAL itself rhymes
            "keys": prof.get("keys")}


# ---------------------------------------------------------------- supply

def material_places():
    """word -> the material file that documents it as a place.

    Targeted extraction, because a blanket "capitalised word" pass produced junk: travel_history's own
    table cells, the Places column of place_sound_families.md, and the bolded place bullets of
    place_specifics.md. A token still has to look like a name (initial capital, not a month/weekday and
    not a very common English word) to count.
    """
    out = {}
    common = set("""two use used room rooms route place places land land's other others one first last
    week weeks day days year years time times home town city coast area part parts north south east west
    new old big small top back front side end start same next last long short high low good bad best worst
    june july august may april march january february september october november december monday tuesday
    wednesday thursday friday saturday sunday black german french italian spanish portuguese greek norwegian
    slovak slovene irish scots welsh dutch thai indian polish swiss austrian basque frenchman irishman
    double triple single half quarter mile miles hour hours minute minutes morning evening night
    confirmed note notes source sources detail details private public family wedding stag festival
    rolling loud ahoy santa claus thing things bit bits lot lots dolly smith stage stages
    """.split())

    def add(tok, src):
        tok = tok.strip().strip("'’").strip()
        tok = re.sub(r"\s+\d.*$", "", tok).strip()
        if len(tok) < 3 or tok.lower() in STOP_PLACE or tok.lower() in common:
            return
        if not re.fullmatch(r"[A-Z][A-Za-z'’\-]*(?: [A-Z][A-Za-z'’\-]*){0,2}", tok):
            return
        if bank.rt_zipf(tok.lower()) >= 4.9 and tok not in out:
            return
        for part in tok.split():                     # "Black Forest" also yields the head word
            out.setdefault(part if len(part) > 3 else tok, src)
        out.setdefault(tok, src)

    def cell(text, src):
        text = re.sub(r"\([^)]*\)", " ", text)
        for chunk in re.split(r"[;/,]", text):
            add(chunk, src)

    for fn, col, pred in (("travel_history.md", 2, lambda l: l.startswith("|")),
                          ("place_sound_families.md", 2, lambda l: l.startswith("|") and "**" in l),
                          ("place_sound_families.md", None, lambda l: l.startswith("- "))):
        path = os.path.join(MATERIAL, fn)
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf8", errors="replace"):
            line = line.rstrip("\n")
            if not pred(line):
                continue
            if col is None:
                cell(line.lstrip("- ").split("(")[0], fn)
            else:
                cells = line.split("|")
                if len(cells) > col + 1:
                    cell(cells[col], fn)
    path = os.path.join(MATERIAL, "place_specifics.md")
    if os.path.exists(path):
        for line in open(path, encoding="utf8", errors="replace"):
            m = re.match(r"-\s+\*\*(.+?)\*\*", line.strip())
            if m:
                cell(m.group(1).split("(")[0], "place_specifics.md")
    # Places confirmed in the material's PROSE (not its tables), listed here by hand so the flag stays
    # a claim about a source rather than a guess.
    for name, src in (("Bristol", "travel_history.md"), ("Portsmouth", "travel_history.md"),
                      ("Naples", "travel_history.md"), ("Pen y Fan", "travel_history.md"),
                      ("Ullapool", "place_sound_families.md"),
                      ("Liverpool", "place_sound_families.md"), ("Polzeath", "place_specifics.md"),
                      ("Bodelva", "place_specifics.md")):
        cell(name, src)
    return out


def _read_words(path):
    if not os.path.exists(path):
        return []
    words = []
    for line in open(path, encoding="utf8", errors="replace"):
        line = line.split("#")[0]
        for part in re.split(r"[|,\s]+", line):
            w = part.strip()
            if w and not w.endswith("|") and len(w) > 1 and w.replace("-", "").isalpha():
                words.append(w)
    return words


_SUPPLY_CACHE = None


_STOP = None


def stopwords():
    """Function words and pronouns: a bar may not END on one (the clause has to finish on something)."""
    global _STOP
    if _STOP is None:
        _STOP = set(rt.FUNC) | set(mt.TAILWORDS) | set("""i me my mine you your yours he him his she her hers
        it its we us our ours they them their theirs who whom whose which what this that these those there
        here then than so such not no nor none any some all both each few more most other others
        a an the and or but if as at by for from in into of on onto to with within without up down out off
        over under again further once only very too also just even still yet ever never always is are was
        were be been being am do does did doing have has had having will would shall should can could may
        might must let us ya em them em""".split())
    return _STOP


def supply():
    """Every end-word candidate, with its measured shape, vowels and commonness.

    Built in ONE pass (the first version asked bank.words_by_vowel for 16 vowels, and each of those
    calls rebuilds the whole cmudict index and re-scores every candidate: minutes of CPU per slot).
    Commonness filters first, so phon.syllables only runs on words that can actually be used.
    """
    global _SUPPLY_CACHE
    if _SUPPLY_CACHE is not None:
        return _SUPPLY_CACHE
    words = set(_read_words(THEME)) | set(_read_words(LOCAL)) | set(rt.OVR)
    words |= set(material_places())          # the true places are candidate end words in their own right
    ent = bank.load_entities(ENTITIES)
    for kind in ("city", "uk-town", "country"):
        for row in [r for r in ent if r["type"] == kind and r["measurable"]][:150]:
            words.add(row["name"])
    for n in (1, 2, 3):
        for ws in rt.index(n, "perfect", "any").values():
            words.update(ws)
    stop = stopwords()
    # one spelling per word: prefer the capitalised form when the material documents it as a place
    doc_places = material_places()
    doc_lower = {p.lower() for p in doc_places}
    spelling = {}
    for w in words:
        k = w.lower()
        if k not in spelling or (w[:1].isupper() and k in doc_lower):
            spelling[k] = w
    out = {}
    for w in spelling.values():
        if not w or len(w) < 2 or not re.fullmatch(r"[A-Za-z'\-]+", w):
            continue
        if w.lower() in stop:
            continue
        z = bank.rt_zipf(w.lower())
        if z < 1.4 and w.lower() not in bank.UK_EVERYDAY and w not in rt.OVR:
            continue
        sy = phon.syllables(w)
        if not sy:
            continue
        shape = ff.end_shape(w)[0]
        out[w] = {"syls": len(sy), "shape": shape, "shape_class": shape[1:], "marker": shape[0],
                  "vowel": next((x[0] for x in reversed(sy) if x[1]), sy[-1][0]),
                  "last_vowel": sy[-1][0], "lead_weak": len(sy) > 1 or shape[1:] == "w",
                  "zipf": round(z, 2)}
    _SUPPLY_CACHE = out
    return out


def prep(w):
    return phon.syllables(w), mt.spans(w)[1]


def pair_score(p1, p2):
    """match.best_end, on pre-parsed syllables (called ~10^5 times per slot)."""
    A, eA = p1
    B, eB = p2
    best = 0.0
    for k in (1, 2, 3):
        if len(A) < k or len(B) < k:
            continue
        a, b = A[-k:], B[-k:]
        if k > 1 and not (a[0][1] or b[0][1]):
            continue
        sc, kind = phon.score(a, b)
        if kind != "none":
            best = max(best, sc)
    if eA and eB:
        sc, kind = phon.score(eA, eB)
        if kind != "none":
            best = max(best, sc)
    return best


# ---------------------------------------------------------------- search

def allowed_words(info, target, places, relax_shape=False, cap=150):
    """Words that can END this bar: the frame's TAIL vowel, its landing pattern, its syllable budget.

    THE TAIL, NOT THE STRESSED VOWEL (13 Oct 2026). Filtering on the frame's STRESSED vowel is what
    broke V1 17-24 -- the block Joe judges the whole song by. Its bars 1-4 land on AH+IH and its bars
    5-8 on AE+IH: a different stressed vowel and the SAME tail, and the original rhymes 24 of its 28
    pairs. Keying on the stressed vowel threw one half of a rhyming family away. A word now qualifies
    if its last syllable carries one of the frame's tail vowels, which is what the rhyme is made of.

    A FRAME WITH NO STRESS IN ITS TAIL IS NOT A SHAPE. The flow template records bar 5 of that block as
    "|w" and bar 8 as "|SwS", and almost no word on earth has either shape, so those bars matched NO
    word and the writer was handed an empty shopping list. When the frame's shape carries no leading
    stress the shape is not a discriminator, so it is not applied.
    """
    out = {}
    want = target.get("shape_class") or ""
    tvowels = list(target.get("vowels") or [])
    shape_usable = want.startswith("S")
    for w, meta in info.items():
        if meta["syls"] > target["syl"] - 1:
            continue                      # the bar needs at least one syllable before the end word
        if tvowels and not (meta["vowel"] in tvowels or meta["last_vowel"] in tvowels):
            continue
        if want and not relax_shape and shape_usable and meta["shape_class"] != want:
            if not (meta["shape_class"].endswith("w") == want.endswith("w")
                    and meta["last_vowel"] == tvowels[-1]):
                continue
        out[w] = meta
    if len(out) > cap:
        keep = sorted(out, key=lambda w: (-out[w]["zipf"], w))[:cap]
        keep += [w for w in out if w in places]
        out = {w: out[w] for w in set(keep)}
    return out


def cliques(allowed, need, score, threshold, cap=60, budget=200000, key=None):
    """Choose `need` words, one per bar's own allowed set, so every pair clears the threshold.

    Bars in a group are searched smallest-allowed-set first (cheap, correct pruning), then the
    assignment is mapped back to bar order, which is exactly what the writer then has to write to.
    `key` orders each candidate set (commonest first, so the search finds USABLE cliques before the
    budget runs out rather than an alphabetical run of obscure ones). `budget` bounds the pair tests.
    """
    sets = [set(a) for a in allowed]
    order = sorted(range(need), key=lambda i: len(sets[i]))
    results, used = [], [0]
    skey = key or (lambda w: w)

    def ok(w, chosen):
        for x in chosen:
            used[0] += 1
            if score(w, x) < threshold:
                return False
        return True

    def dfs(k, chosen, cand):
        if len(results) >= cap or used[0] > budget:
            return
        if k == need:
            m = [None] * need
            for idx, w in zip(order, chosen):
                m[idx] = w
            results.append(m)
            return
        i = order[k]
        for w in sorted(cand & sets[i], key=skey):
            if not ok(w, chosen):
                continue
            chosen.append(w)
            dfs(k + 1, chosen, {x for x in cand if x != w and ok(x, chosen)})
            chosen.pop()
            if len(results) >= cap or used[0] > budget:
                return

    dfs(0, [], set(sets[order[0]]))
    return results


def groups_of(scheme, targets, carpet, rhyme_map=None):
    """Bar groups that must rhyme with each other.

    THE BY-EAR SCHEME IS THE GROUPING; THE FRAME'S VOWEL AND SHAPE ARE NOT (13 Oct 2026). The old rule
    grouped bars by (scheme letter, STRESSED vowel, shape) and it split V1 17-24 -- the block Joe judges
    the song by -- into [1,2,3] and [4,6], so the writer got end words for five bars out of eight and
    NOTHING for bars 5, 7 and 8. Two faults: it keyed on the stressed vowel of a block that rhymes on
    the TAIL, and it used the frame's shape class, which for that block is "w" for two bars -- a shape
    no word has. The by-ear scheme (AAAA BBBB there) is the original's own grouping and it is already
    the right answer: bars 1-4 rhyme with each other, 5-8 rhyme with each other, and the pairs ACROSS
    the two halves are not demanded of us even though the original's own carpet has 24 of 28.
    Trybars keeps the ACROSS-halves count as information, not as a requirement.
    A slot whose carpet is complete is still one group, because the original rhymes every pair there.
    """
    n = len(targets)
    if n < 2:
        return [], "none"
    if carpet.get("share", 0) >= 1.0:
        return [list(range(n))], "carpet"
    if scheme:
        groups = {}
        for i, ch in enumerate(scheme[:n]):
            groups.setdefault(ch, []).append(i)
        g = [x for x in groups.values() if len(x) > 1]
        if g:
            return g, "by-ear scheme"
    if rhyme_map:
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for row in rhyme_map:
            if len(row) < 4:
                continue
            _kind, i, j, sc = row[:4]
            if isinstance(i, int) and isinstance(j, int) and i < n and j < n and sc >= 0.78:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
        comp = {}
        for i in range(n):
            comp.setdefault(find(i), []).append(i)
        return [g for g in comp.values() if len(g) > 1], "measured carpet (the pairs the original rhymes)"
    return [], "none"


def build_sets(slot, threshold=0.78, aim=0.95, top=12, min_places=2, relax_shape=False):
    tgt = slot_target(slot)
    n = len(tgt["targets"])
    info = supply()
    places = material_places()
    allowed = [allowed_words(info, t, places, relax_shape) for t in tgt["targets"]]

    memo = {}

    def score(a, b):
        key = (a, b) if a <= b else (b, a)
        if key not in memo:
            memo[key] = pair_score(prep(a), prep(b))
        return memo[key]

    scheme = tgt["manual_scheme"] or tgt["scheme"]
    groups, how = groups_of(scheme, tgt["targets"], tgt["carpet"], tgt.get("rhyme_map"))

    # the per-bar bank: EVERY word that fits this bar's own vowel, shape and budget, commonest first.
    # This is the writer's shopping list for a free bar, and the honest answer when a bar cannot join
    # its group (see groups_of).
    per_bar = []
    for i, t in enumerate(tgt["targets"]):
        ws = sorted(allowed[i], key=lambda w: (-info[w]["zipf"], w))
        per_bar.append([{"word": w, "place": places.get(w), "syl": info[w]["syls"],
                         "shape": info[w]["shape"], "zipf": round(info[w]["zipf"], 2),
                         "lead": t["syl"] - info[w]["syls"]} for w in ws[:40]])

    per_group, unmet = [], []
    skey = lambda w: (-info[w]["zipf"], w)          # noqa: E731
    for g in groups:
        found = cliques([allowed[b] for b in g], len(g), score, threshold, cap=top * 8, key=skey)
        if not found:
            unmet.append(g)
            continue
        ranked = []
        for c in found:
            ps = [score(c[i], c[j]) for i in range(len(g)) for j in range(i + 1, len(g))]
            ranked.append({"bars": g, "words": c, "min": round(min(ps), 3) if ps else 1.0,
                           "places": sum(1 for w in c if w in places),
                           "zipf": sum(info[w]["zipf"] for w in c) / len(c)})
        ranked.sort(key=lambda r: (-r["min"], -r["places"], -r["zipf"]))
        per_group.append(ranked[:top])

    met = {b for p in per_group for b in p[0]["bars"]} if per_group else set()
    free = [i for i in range(n) if i not in met]
    choices = [p[:top] for p in per_group]
    choices += [[{"bars": [i], "words": [row["word"]], "min": 1.0,
                  "places": 1 if row["place"] else 0, "zipf": row["zipf"]}
                 for row in per_bar[i][:6]] for i in free]
    sets, ncombo = [], 0
    met_groups = [p[0]["bars"] for p in per_group]
    for combo in itertools.product(*choices):
        ncombo += 1
        if ncombo > 6000:
            break
        pick = {}
        for part in combo:
            for bar, w in zip(part["bars"], part["words"]):
                pick[bar] = w
        if len(pick) != n:
            continue
        words = [pick[i] for i in range(n)]
        req = [(i, j) for i in range(n) for j in range(i + 1, n)
               if any(i in g and j in g for g in met_groups)]
        allp = [(i, j) for i in range(n) for j in range(i + 1, n)]
        sets.append({
            "words": words,
            "min": round(min((score(words[i], words[j]) for i, j in req), default=1.0), 3),
            "carpet_min": round(min((score(words[i], words[j]) for i, j in allp), default=1.0), 3),
            "places": sum(1 for w in words if w in places),
            "lead": [tgt["targets"][i]["syl"] - info[words[i]]["syls"] for i in range(n)],
            "zipf": round(sum(info[w]["zipf"] for w in words) / n, 2)})
    strong = [s for s in sets if s["places"] >= min_places]
    sets = strong or sets
    sets.sort(key=lambda s: (-s["min"], -s["places"], -s["zipf"]))
    seen, uniq = set(), []
    for s in sets:
        k = tuple(s["words"])
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    return {"slot": slot, "target": tgt, "grouping": how, "threshold": threshold, "aim": aim,
            "groups": groups, "unmet_groups": unmet, "cliques": per_group, "free_bars": free,
            "per_bar": per_bar, "sets": uniq[:top], "places_known": len(places),
            "supply": len(info)}


def show(res, top=8):
    tgt = res["target"]
    print(f"== {res['slot']}  by-ear scheme {tgt['manual_scheme']} (measured {tgt['scheme']})  "
          f"carpet {tgt['carpet'].get('pairs')}/{tgt['carpet'].get('total')} "
          f"min {tgt['carpet'].get('min')}  grouping: {res['grouping']}")
    print("   bars: " + "  ".join(
        f"{t['bar']}:{t['syl']}syl/{t['vowel']}/{t['shape']}" for t in tgt["targets"]))
    for g in res["groups"]:
        print(f"   must-rhyme group: bars {[b + 1 for b in g]}  "
              f"(vowel {tgt['targets'][g[0]]['vowel']}, shape {tgt['targets'][g[0]]['shape_class']})")
    for g in res.get("unmet_groups", []):
        print(f"   UNMET group (no word set clears {res['threshold']:.2f}): bars {[b + 1 for b in g]} "
              f"-- vowel {tgt['targets'][g[0]]['vowel']}, shape {tgt['targets'][g[0]]['shape_class']}; "
              f"treat as free and link by assonance")
    if res["free_bars"]:
        print(f"   free bars (no rhyme demanded by the frame): {[b + 1 for b in res['free_bars']]}")
    pl = material_places()
    for cl in res.get("cliques", []):
        g = cl[0]["bars"]
        print(f"   clique options for bars {[b + 1 for b in g]} (every pair >= {res['threshold']:.2f}):")
        for opt in cl[:4]:
            words = ", ".join(f"{w}{'*' if w in pl else ''}" for w in opt["words"])
            print(f"     min {opt['min']:.2f}  places {opt['places']}  {words}")
    print("   per-bar bank (fits that bar's vowel, shape and length; commonest first):")
    for i, rows in enumerate(res["per_bar"]):
        if not rows:
            print(f"     bar {tgt['targets'][i]['bar']:>2}: NONE fit -- frame vowel "
                  f"{tgt['targets'][i]['vowel']} / shape {tgt['targets'][i]['shape']}")
            continue
        shown = []
        for r in rows[:14]:
            tag = "*" if r["place"] else ""
            shown.append(f"{r['word']}{tag}")
        print(f"     bar {tgt['targets'][i]['bar']:>2}: " + ", ".join(shown))
    if not res["sets"]:
        print("   NO full slot set -- write from the per-bar bank above (a slot whose 8 bars end on 8 "
              "different vowels cannot carpet; that is the frame's own shape, not a failure).")
        return
    print("   candidate slot sets (all bars):")
    places = material_places()
    for k, s in enumerate(res["sets"][:top], 1):
        flag = "OK " if s["min"] >= 0.95 else ("ok " if s["min"] >= 0.85 else "   ")
        print(f" {flag}set {k}: required-min {s['min']:.2f}  carpet-min {s['carpet_min']:.2f}  "
              f"places {s['places']}  lead {s['lead']}  zipf {s['zipf']}")
        for i, w in enumerate(s["words"]):
            src = places.get(w)
            print(f"       bar {tgt['targets'][i]['bar']:>2} {w:<12} "
                  f"{'PLACE(' + src + ')' if src else ''}")


def selftest():
    """Hermetic checks on the parts that can be wrong silently: grouping, shape filtering, clique search."""
    ok = True

    def chk(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print("  FAIL", name)

    carpet = {"share": 1.0, "pairs": 6, "total": 6}
    tg = [{"vowel": "æ"}] * 4
    g, how = groups_of("abcc", tg, carpet)
    chk("complete carpet -> one group", how == "carpet" and g == [[0, 1, 2, 3]])
    # The MEASURED carpet decides the groups. V1 17-24 is the case that matters: the original links its
    # bars 1-4 to bars 5-8 -- a different STRESSED vowel, the same tail -- and the old rule split them,
    # handing the writer end words for five bars and nothing for the other three.
    tg6 = [{"vowel": "ʌ", "shape_class": "Sw"}, {"vowel": "ʌ", "shape_class": "Sww"},
           {"vowel": "æ", "shape_class": "w"}, {"vowel": "æ", "shape_class": "Sww"}]
    g, how = groups_of("aaaa", tg6, {"share": 0.86}, [])
    chk("the by-ear scheme groups, not the frame's vowel or shape",
        how == "by-ear scheme" and g == [[0, 1, 2, 3]])
    g, how = groups_of("abbc", tg, {"share": 0.5}, [])
    chk("the by-ear scheme skips singletons", how == "by-ear scheme" and g == [[1, 2]])
    chk("a complete carpet beats the scheme", groups_of("abcc", tg, carpet)[1] == "carpet")
    g, how = groups_of("", tg, {"share": 0.5}, [["end-end", 1, 2, 0.9]])
    chk("no scheme -> the measured pairs group", how.startswith("measured carpet") and g == [[1, 2]])
    chk("singletons are never demanded", groups_of("abcd", tg, {"share": 0.5}, [])[0] == [])
    chk("pair_score is symmetric", abs(pair_score(prep("Zurich"), prep("traffic"))
                                      - pair_score(prep("traffic"), prep("Zurich"))) < 1e-9)
    chk("pair_score matches match.best_end", abs(pair_score(prep("Zurich"), prep("Munich"))
                                                 - mt.best_end("Zurich", "Munich")) < 1e-9)
    chk("shape filter keeps |Sw", ff.end_shape("Munich")[0] == "|Sw")
    info = {"cash": {"syls": 1, "shape": "|S", "shape_class": "S", "vowel": "æ", "last_vowel": "æ", "zipf": 5.0},
            "back": {"syls": 1, "shape": "|S", "shape_class": "S", "vowel": "æ", "last_vowel": "æ", "zipf": 5.0},
            "backpack": {"syls": 2, "shape": "|S", "shape_class": "S", "vowel": "æ", "last_vowel": "æ", "zipf": 5.0}}
    al = allowed_words(info, {"vowel": "æ", "vowels": ["æ"], "shape_class": "S", "syl": 3}, {})
    chk("allowed_words keeps the word that leaves lead-in", set(al) == {"cash", "back", "backpack"})
    al = allowed_words(info, {"vowel": "æ", "vowels": ["æ"], "shape_class": "S", "syl": 2}, {})
    chk("allowed_words drops the word with no lead-in", set(al) == {"cash", "back"})
    # A TAIL-RHYMED frame: one of the frame's tail vowels is enough, whatever the stressed vowel is.
    info2 = {"governor": {"syls": 3, "shape": "|Sww", "shape_class": "Sww", "vowel": "ʌ", "last_vowel": "ə", "zipf": 4.5},
             "customer": {"syls": 3, "shape": "|Sww", "shape_class": "Sww", "vowel": "ʌ", "last_vowel": "ə", "zipf": 4.0}}
    al = allowed_words(info2, {"vowel": "æ", "vowels": ["æ", "ə"], "shape_class": "Sww", "syl": 5}, {})
    chk("a tail vowel qualifies a word whose stressed vowel differs",
        set(al) == {"governor", "customer"})
    al = allowed_words(info2, {"vowel": "æ", "vowels": ["æ", "ə"], "shape_class": "w", "syl": 5}, {})
    chk("a frame with no stress in its tail applies no shape filter",
        set(al) == {"governor", "customer"})
    cl = cliques([al, al], 2, lambda a, b: 1.0, 0.78, cap=8)
    chk("cliques finds pairs", len(cl) >= 1 and all(len(c) == 2 for c in cl))
    cl = cliques([al, al], 2, lambda a, b: 0.0, 0.78, cap=8)
    chk("cliques respects the threshold", cl == [])
    print("carpet selftest:", "PASSED" if ok else "FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot")
    ap.add_argument("--threshold", type=float, default=0.78)
    ap.add_argument("--aim", type=float, default=0.95)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--min-places", type=int, default=2)
    ap.add_argument("--relax-shape", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if not a.slot:
        ap.error("--slot is required (or --selftest)")
    if a.slot not in json.load(open(PROFILE, encoding="utf8")):
        ap.error(f"unknown slot {a.slot!r}")
    res = build_sets(a.slot, a.threshold, a.aim, a.top, a.min_places, a.relax_shape)
    show(res)
    out = os.path.join(ROOT, "benchmark", f"carpets_{slug(a.slot)}.json")
    json.dump(res, open(out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"   cached -> {os.path.relpath(out, ROOT)}  ({len(res['sets'])} sets, "
          f"supply {res['supply']} words, {res['places_known']} known places)")


if __name__ == "__main__":
    main()
