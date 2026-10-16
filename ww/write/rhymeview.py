"""Rhyme highlighter (RhymeFlux-style): colour every bar's rhyme, side by side, so a rhyme scheme can be SEEN.

  python -m ww.cli rhymes --left original --right writing/ww_full_draft_v8.md --skeleton-left --out writing/rhymes_original_vs_v8.html
  python -m ww.cli rhymes --left original --right writing/ww_full_draft_v8.md --out ~/Documents/WORLDWIDE_PRIVATE/rhymes_original_vs_v8.html

WHAT IS COLOURED
  end tail   from the last stressed content word to the end of the bar ("double it", "shovel it" count as one tail). Bars whose tails rhyme share a
             colour and a scheme letter. Solid underline = perfect (grader >= 0.97), dotted = assonance or near (0.78-0.97), grey = unpaired.
  internal   any other stressed content word in the same section that rhymes (>= 0.80) with one of the section's end tails, in that group's lighter tint.
HOW THE GROUPS ARE FOUND
  drafts     the repo's grader (bridge.rhyme_score; a pair rhymes at >= 0.78), average-linkage inside each slot.
  original   Joe's BY-EAR scheme letters (slotcheck.spec(slot)["scheme"]), because the grader under-scores the original's assonant carpets
             (moi/dance, Jamaica/Mainz, the 3-syllable tails of V1 17-24).
LIMITS (read before trusting a colour): the grader's known holes apply (a weak "-it" tail can score perfect while the stressed vowels differ; assonance
sits at 0.80). Internal matches are a heuristic. The colour shows what the tools hear, not what is good.

RULE 4 (CLAUDE.md): the original's lyrics are never written into the project. The original is read from config.PRIVATE_ORIGINAL; a FULL-TEXT render
of it may only be written inside that folder (render() raises otherwise). Inside the project, skeleton=True shows ONLY the highlighted words (isolated
words) and one dot per syllable for everything else.
"""
from __future__ import annotations

import html
import itertools
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

from .. import bridge, config

SLOTS = [("Hook 1-4", 4), ("Hook 5-8", 4), ("Hook 9-16", 8), ("V1 1-8", 8), ("V1 9-16", 8), ("V1 17-24", 8), ("V1 25-32", 8),
         ("V1 33-44", 12), ("V2 1-8", 8), ("V2 9-16", 8)]
CLITIC = set("it him her them em us in on up a an the to of at as and".split())
FUNC = CLITIC | set("""i me my you your we he she they his their our who what that this is are was were be been am do does did have has had will would can
could may might just so if but or not no for with by from like then than there here when while out off over down yeah oh uh""".split())
THRESH, PERFECT, INTERNAL = 0.78, 0.97, 0.80
HUES = [210, 25, 130, 320, 50, 270, 175, 0, 95, 240, 340, 160]


# ------------------------------------------------------------------ loading

def load_original() -> dict[str, list[str]]:
    """the original's 76 bars in slot order, from the PRIVATE file (never copied into the project)."""
    lines = [l.strip() for l in config.PRIVATE_ORIGINAL.read_text(encoding="utf-8").splitlines() if l.strip()]
    out, i = {}, 0
    for slot, n in SLOTS:
        out[slot] = lines[i:i + n]
        i += n
    return out


def load_draft(path: str) -> dict[str, list[str]]:
    from . import flowaudit
    return flowaudit.parse_draft(path)


# ------------------------------------------------------------------ analysis

def core(w: str) -> str:
    return re.sub(r"[^a-z0-9'&]", "", w.lower().replace("’", "'")).strip("'")


@lru_cache(maxsize=None)
def rs(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    try:
        return float(bridge.rhyme_score(a, b))
    except Exception:    # noqa: BLE001 - an unpronounceable token simply does not rhyme
        return 0.0


@lru_cache(maxsize=None)
def stressed(w: str) -> bool:
    try:
        sp = bridge.stress_pattern(w)
    except Exception:    # noqa: BLE001
        sp = None
    return bool(sp and ("1" in sp or "2" in sp))


@lru_cache(maxsize=None)
def nsyl(w: str) -> int:
    try:
        sp = bridge.stress_pattern(w)
    except Exception:    # noqa: BLE001
        sp = None
    return max(1, len(sp)) if sp else 1


AL_HUES = [20, 200, 330, 130, 270, 50, 170, 0]


@lru_cache(maxsize=None)
def onset(c: str):
    """the word's opening consonant sound(s) in British phones (so phone ~ fan, knight ~ nice, cat ~ kite), or None if it opens on a vowel / is unknown."""
    try:
        from . import rapfit
        p = rapfit._phon()
        out = []
        for t in p.word_phones(c):
            if p.is_vowel(t):
                break
            out.append(t)
        return tuple(out) or None
    except Exception:    # noqa: BLE001
        return None


def alliteration(ws: list[str]) -> dict[int, int]:
    """{word index: group} for words in ONE bar that open on the same sound: two or more DIFFERENT content words, at least one stressed.
    Same word repeated (German German German) is repetition, not alliteration. Cross-bar alliteration is not measured."""
    groups: dict = {}
    for j, w in enumerate(ws):
        c = core(w)
        if not c or c in FUNC or len(c) < 2:
            continue
        o = onset(c)
        if o:
            # one opening sound, whatever follows it (front ~ phone ~ fan); s+stop clusters (st, sp, sk) count as their own sound, as in stand/speak
            key = o[:2] if (o[0] == "s" and len(o) > 1 and o[1] in ("t", "p", "k")) else o[:1]
            groups.setdefault(key, []).append((j, c))
    out: dict[int, int] = {}
    k = 0
    for lst in groups.values():
        if len({c for _, c in lst}) >= 2 and any(stressed(c) for _, c in lst):
            for j, _ in lst:
                out[j] = k
            k += 1
    return out


def _al_wrap(w: str, g) -> str:
    """escape the word and, if it alliterates, wrap its opening letters (up to the first vowel letter) in a coloured bold span."""
    if g is None:
        return html.escape(w)
    m = re.search(r"[A-Za-z]", w)
    if not m:
        return html.escape(w)
    p = m.start()
    i = p
    while i < len(w) and w[i].lower() not in "aeiou":
        i += 1
    L = max(1, i - p)
    if w[p:p + 2].lower() == "qu":
        L = 2
    return html.escape(w[:p]) + f'<b class="al" style="--a:{AL_HUES[g % len(AL_HUES)]}">' + html.escape(w[p:p + L]) + "</b>" + html.escape(w[p + L:])


_VOW = set("aeiou")
_DIG = ("ck", "ch", "sh", "th", "ph", "wh", "gh", "ng", "qu", "kn", "wr")
_ONSETS = {"bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "sc", "sk", "sl", "sm", "sn", "sp", "st", "sw", "tr", "tw", "str", "spr", "scr", "spl"}


def _units(cs: str) -> list[str]:
    out, i = [], 0
    while i < len(cs):
        if cs[i:i + 2] in _DIG:
            out.append(cs[i:i + 2])
            i += 2
        else:
            out.append(cs[i])
            i += 1
    return out


def split_letters(w: str, syl: tuple) -> list[str]:
    """cut the written word into len(syl) chunks, one per phonetic syllable, for DISPLAY only. Heuristic: vowel-letter runs are the nuclei (silent final e dropped,
    consonant+le kept); a lone consonant after a stressed short vowel stays with it (cred-it, lim-it), otherwise it opens the next syllable (fa-vours).
    If the spelling cannot be made to agree with the phonetic count the word stays whole."""
    n = len(syl)
    if n <= 1 or len(w) < 2:
        return [w]
    lw = w.lower()
    runs: list[list[int]] = []
    i = 0
    while i < len(lw):
        if lw[i] in _VOW or (lw[i] == "y" and i > 0):
            j = i
            while j < len(lw) and (lw[j] in _VOW or (lw[j] == "y" and j > 0)):
                j += 1
            runs.append([i, j])
            i = j
        else:
            i += 1
    cons_le = len(lw) >= 3 and lw.endswith("le") and lw[-3] not in _VOW
    while len(runs) > n:
        last = runs[-1]
        tail = lw[last[0]:]
        if last[0] > 0 and tail in ("e", "es", "ed") and not cons_le:
            runs.pop()
            continue
        gaps = [(runs[k + 1][0] - runs[k][1], k) for k in range(len(runs) - 1)]
        k = min(gaps)[1]
        runs[k] = [runs[k][0], runs[k + 1][1]]
        del runs[k + 1]
    if len(runs) < n:
        k = max(range(len(runs)), key=lambda k: runs[k][1] - runs[k][0]) if runs else None
        if k is None or runs[k][1] - runs[k][0] < 2 or len(runs) + 1 != n:
            return [w]
        mid = runs[k][0] + 1
        runs[k:k + 1] = [[runs[k][0], mid], [mid, runs[k][1]]]
    cuts = []
    for k in range(n - 1):
        a, b = runs[k][1], runs[k + 1][0]
        units = _units(lw[a:b])
        stressed_short = bool(syl[k][1]) and syl[k][0] in ("ɪ", "e", "æ", "ʌ", "ɒ", "ʊ")
        if not units:
            cuts.append(a)
        elif len(units) == 1:
            cuts.append(a + len(units[0]) if stressed_short else a)
        else:
            whole = "".join(units)
            cuts.append(a if (whole in _ONSETS and not stressed_short) else a + len(units[0]))
    out, prev = [], 0
    for c in cuts + [len(w)]:
        out.append(w[prev:c])
        prev = c
    return out if all(out) and len(out) == n else [w]


REDUCED_FUNC = set("""the a an of to and or but in at for from with as is are was were be been am it its that this than then do does did has have had can could
will would i me my you your he she we they his her their our him them us on""".split())


def prominent_stream(ws: list[str], chunks: dict) -> list[dict]:
    """the syllables a rapper leans on, in reading order: stressed, or a full vowel; reduced words (the, of, in, with ...) and schwa/ɪ/i tails are skipped,
    so a bar reading 'chicas out' gives iː, aʊ."""
    from . import rapfit
    out = []
    for j, w in enumerate(ws):
        c = core(w)
        if not c or c in REDUCED_FUNC:
            continue
        sy = rapfit._syl(c)
        for k, x in enumerate(sy):
            if rapfit.prominent(x):
                out.append({"j": j, "ci": k if len(chunks.get(j, [])) == len(sy) else 0, "v": x[0], "c": c, "coda": tuple(x[2]), "syl": x})
    return out


def find_chains(streams: list[list[dict]], window: int = 1) -> list[dict]:
    """MULTI-SYLLABLE INTERNAL RHYMES: a sequence of 2+ consecutive prominent vowels that occurs again within `window` bars (a repeated iː-aʊ pair is the
    standard example). Longest first (3, then 2). One vowel repeated (out down) is a pile-up, not a mosaic rhyme, and is left out; the same words twice is
    repetition, not a rhyme."""
    chains, used = [], set()
    for n in (3, 2):
        occ: dict = {}
        for b, st in enumerate(streams):
            for p in range(len(st) - n + 1):
                key = tuple(x["v"] for x in st[p:p + n])
                if len(set(key)) == 1 or any((b, p + k) in used for k in range(n)):
                    continue
                occ.setdefault(key, []).append((b, p))
        for key, lst in occ.items():
            def near(o, o2):
                return o != o2 and abs(o2[0] - o[0]) <= window and not (o[0] == o2[0] and abs(o[1] - o2[1]) < n)
            keep = [o for o in lst if any(near(o, o2) for o2 in lst)]
            if len(keep) < 2:
                continue
            words_of = lambda o: tuple(streams[o[0]][o[1] + k]["c"] for k in range(n))
            # a real mosaic rhyme changes EVERY word (meat out ~ beach house); one word kept (when I'm ~ when wine, German x3) is a repeated phrase, not a rhyme
            keep = [o for o in keep if any(near(o, o2) and all(x != y for x, y in zip(words_of(o), words_of(o2))) for o2 in keep)]
            if len(keep) < 2:
                continue
            chains.append({"key": key, "n": n, "occ": keep})
            for b, p in keep:
                for k in range(n):
                    used.add((b, p + k))
    return chains


def chain_null(streams: list[list[dict]], trials: int = 40, seed: int = 7) -> float:
    """how many chain occurrences would SHUFFLED vowels give by chance (same number of prominent syllables per bar)? Only the excess is craft."""
    import random
    rnd = random.Random(seed)
    lens = [len(s) for s in streams]
    vowels = [x["v"] for st in streams for x in st]
    if len(vowels) < 4:
        return 0.0
    tot = 0
    for _ in range(trials):
        rnd.shuffle(vowels)
        k, fake = 0, []
        for b, L in enumerate(lens):
            fake.append([{"j": 0, "ci": 0, "v": vowels[k + i], "c": f"w{b}_{i}"} for i in range(L)])
            k += L
        tot += sum(len(c["occ"]) for c in find_chains(fake))
    return tot / trials


# 16 Oct 2026: an object pronoun closing the line is part of the end tail too ('caught me', 'for me'). Before, the tail was 'me' alone, so
# 'caught me' was heard to rhyme with 'Seedy' on the 'ee' and the original's own word + 'me' endings were measured one syllable deep.
TAIL_PRON = {"me", "you", "ya"}


def tail_start(ws: list[str]) -> int:
    """index of the first word of the end tail: back off over trailing clitics (it, him, in, me ...) to the last content word, at most 3 words."""
    n = len(ws)
    i = n - 1
    while i > 0 and (core(ws[i]) in CLITIC or core(ws[i]) in TAIL_PRON) and (n - i) < 3:
        i -= 1
    return i


def tail_text(ws: list[str]) -> str:
    return " ".join(core(w) for w in ws[tail_start(ws):] if core(w))


def _group_grader(tails: list[str]) -> list[Optional[int]]:
    """average-linkage clustering at THRESH: bar -> group index (None = unpaired)."""
    groups: list[list[int]] = []
    for i, t in enumerate(tails):
        best, bi = 0.0, None
        for gi, mem in enumerate(groups):
            avg = sum(rs(t, tails[m]) for m in mem) / len(mem)
            if avg > best:
                best, bi = avg, gi
        if bi is not None and best >= THRESH:
            groups[bi].append(i)
        else:
            groups.append([i])
    lab: list[Optional[int]] = [None] * len(tails)
    k = 0
    for mem in groups:
        if len(mem) >= 2:
            for m in mem:
                lab[m] = k
            k += 1
    return lab


def _group_ear(scheme: str, n: int) -> Optional[list[Optional[int]]]:
    if len(scheme) != n:
        return None
    letters = sorted({c for c in scheme if scheme.count(c) >= 2}, key=scheme.index)
    return [letters.index(c) if c in letters else None for c in scheme]


def analyze(sections: dict[str, list[str]], ear: bool = False) -> dict:
    out = {"slots": {}, "bars": 0, "paired": 0, "perfect": 0, "tech": 0, "internal": 0, "al_bars": 0, "al_words": 0}
    for slot, bars in sections.items():
        if not bars:
            continue
        words = [b.split() for b in bars]
        tails = [tail_text(w) for w in words]
        lab = None
        if ear:
            try:
                from . import slotcheck
                lab = _group_ear(slotcheck.spec(slot)["scheme"], len(bars))
            except Exception:    # noqa: BLE001
                lab = None
        if lab is None:
            lab = _group_grader(tails)
        members: dict[int, list[int]] = {}
        for i, g in enumerate(lab):
            if g is not None:
                members.setdefault(g, []).append(i)
        letters = {}
        for g in sorted(members, key=lambda g: members[g][0]):
            letters[g] = chr(ord("A") + len(letters))
        from . import rapfit
        ph = rapfit._phon()

        def stress_vowel(c):
            sy = rapfit._syl(c)
            idx = [k for k, x in enumerate(sy) if x[1]]
            return sy[idx[-1]][0] if idx else None

        def anchor_vowels(tail):
            sy = rapfit._syl(tail)
            return {sy[k][0] for k, _ in rapfit._anchors(sy)}

        gv = {g: set().union(*(anchor_vowels(tails[m]) for m in mem)) for g, mem in members.items()}
        marks_all: dict[int, dict] = {i: {} for i in range(len(words))}
        leftover: dict[str, list] = {}
        for i, ws in enumerate(words):
            for j in range(tail_start(ws)):
                c = core(ws[j])
                if not c or c in FUNC or not stressed(c):
                    continue
                v = stress_vowel(c)
                if not v:
                    continue
                bg, bs = None, 0.0
                for g, vs in gv.items():
                    sv = max((ph.vsim(v, av) for av in vs), default=0.0)
                    if sv > bs:
                        bs, bg = sv, g
                if bg is not None and bs >= 0.999:     # the SAME stressed vowel as one of the group's rhyme anchors (identical, not 0.9: aI~eI is 0.93 and made 'eye' an echo of an eI group)
                    marks_all[i][j] = ("int", bg, max(rapfit.score(c, tails[m])["score"] for m in members[bg]))
                else:
                    leftover.setdefault(v, []).append((i, j, c))
        nmin = 2 if len(bars) <= 4 else 3
        gid = (max(members) + 1) if members else 0
        for v, lst in leftover.items():                  # vowels that echo only each other (stage / plane) still form a group of their own
            if len(lst) >= nmin and len({c for _, _, c in lst}) >= 2:
                for i, j, c in lst:
                    marks_all[i][j] = ("int", gid, 0.6)
                gid += 1
        rows = []
        for i, ws in enumerate(words):
            ts = tail_start(ws)
            g = lab[i]
            anchor = tails[members[g][0]] if g is not None else None
            rap = (1.0 if i == members[g][0] else rapfit.score(tails[i], anchor)["score"]) if g is not None else None
            grd = (1.0 if i == members[g][0] else rs(tails[i], anchor)) if g is not None else None
            marks = dict(marks_all[i])
            for j in range(ts, len(ws)):
                marks[j] = ("end", g, rap)
            rows.append({"text": bars[i], "words": ws, "marks": marks, "g": g, "letter": letters.get(g, "·"), "score": rap, "grader": grd, "tail_from": ts, "al": alliteration(ws)})
        # SYLLABLE LEVEL: for every bar in an end group, compare its closing syllables with each partner's, counted from the END of the bar
        syls = [rapfit._syl(t) for t in tails]
        parent = {g: g for g in members}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for g1, g2 in itertools.combinations(sorted(members), 2):
            cross = [(i, j) for i in members[g1] for j in members[g2]]
            if cross and sum(1 for i, j in cross if rapfit.chain_best(syls[i], syls[j])["depth"] >= 1) / len(cross) >= 0.75:
                parent[find(g2)] = find(g1)
        fam = {g: find(g) for g in members}
        fam_members: dict = {}
        for g, root in fam.items():
            fam_members.setdefault(root, []).extend(members[g])
        for i, r in enumerate(rows):
            r["depth"], r["echo"], r["sy"] = None, 0, {}
            g = r["g"]
            if g is None:
                continue
            best_depth, best_echo, per_k = 0, 0, []
            for m in fam_members[fam[g]]:
                if m == i:
                    continue
                c = rapfit.chain(syls[i], syls[m])
                cb = rapfit.chain_best(syls[i], syls[m])          # depth counts the syllabic-consonant reading (Dublin ~ double it); chips show the dictionary syllables
                best_depth, best_echo = max(best_depth, cb["depth"]), max(best_echo, cb["echo"] if not cb["depth"] else 0)
                for k, st in enumerate(c["states"]):
                    while len(per_k) <= k:
                        per_k.append(0)
                    per_k[k] = max(per_k[k], st if c["depth"] else -st)       # negative = part of a tail echo only
            r["depth"], r["echo"] = best_depth, best_echo
            # map the tail's syllables (from the end) onto words and letter chunks
            ws = r["words"]
            order = []                                                         # (word index, chunk index) per syllable, in reading order
            for j in range(r["tail_from"], len(ws)):
                sy = rapfit._syl(core(ws[j]))
                alpha = re.sub(r"[^A-Za-z']", "", ws[j])
                ch = split_letters(alpha, sy) if sy else [alpha]
                for k in range(len(sy)):
                    order.append((j, k if len(ch) == len(sy) else 0))
            if len(order) == len(syls[i]):
                for k, st in enumerate(per_k):
                    j, ci = order[len(order) - 1 - k]
                    r["sy"].setdefault(j, {})[ci] = st
            else:                                                              # spelling/phonetics disagree: colour the whole word by its best syllable
                for k, st in enumerate(per_k):
                    if k < len(order):
                        j, _ = order[len(order) - 1 - k]
                        r["sy"].setdefault(j, {})["all"] = st
        out["depths"] = out.get("depths", [])
        out["depths"] += [(slot, r["depth"], r["echo"]) for r in rows if r["g"] is not None]
        for r in rows:                                                          # letter chunks for every word (display only)
            r["chunks"] = {}
            for j, w in enumerate(r["words"]):
                body = re.match(r"^([^A-Za-z']*)(.*?)([^A-Za-z']*)$", w).group(2)
                sy = rapfit._syl(core(w))
                if "-" in body and sy:
                    # hyphenated (on-stage): split each part by its own syllables and keep the hyphen with the part before it
                    ch = []
                    for k, part in enumerate(body.split("-")):
                        psy = rapfit._syl(core(part))
                        pc = split_letters(part, psy) if psy else [part]
                        pc = pc if (not psy or len(pc) == len(psy)) else [part]
                        if k < body.count("-"):
                            pc = pc[:-1] + [pc[-1] + "-"]
                        ch.extend(pc)
                else:
                    ch = split_letters(body, sy) if sy else [body]
                r["chunks"][j] = ch if ((not sy or len(ch) == len(sy)) and "".join(ch) == body) else [body]
        streams = [prominent_stream(r["words"], r["chunks"]) for r in rows]
        chains = find_chains(streams)
        for r in rows:
            r["chain"] = {}
        for cid, c in enumerate(chains):
            for b, p0 in c["occ"]:
                for k in range(c["n"]):
                    it = streams[b][p0 + k]
                    rows[b]["chain"][(it["j"], it["ci"])] = cid
        # how much of the REPEATED vowel material is a pattern (a chain) and how much is one sound piled up?
        rep = in_chain = 0
        for b, st in enumerate(streams):
            for p0, it in enumerate(st):
                near = [x for bb in range(max(0, b - 1), min(len(streams), b + 2)) for q, x in enumerate(streams[bb]) if not (bb == b and q == p0)]
                if any(x["v"] == it["v"] for x in near):
                    rep += 1
                    in_chain += 1 if (it["j"], it["ci"]) in rows[b]["chain"] else 0
        # EXACT-RIME CLASSES: prominent syllables in different words, within a bar of each other, that rhyme as syllables (same vowel, same ending OR the consonant is the
        # next syllable's onset: por-no ~ bor-deaux ~ bored ~ boar-ded). Linked transitively; kept when at least one member is not part of the bar's closing rhyme.
        items = [(bb, it) for bb, st in enumerate(streams) for it in st]
        par = list(range(len(items)))

        def f2(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        for ia in range(len(items)):
            for ib in range(ia + 1, len(items)):
                (ba, xa), (bb2, xb) = items[ia], items[ib]
                if abs(ba - bb2) <= 2 and xa["c"] != xb["c"] and rapfit.syl_match(xa["syl"], xb["syl"]) == 2:       # two bars: an exact rime is a strong signal (porno bar 2 ~ Bordeaux bar 4)
                    par[f2(ib)] = f2(ia)
        comps: dict = {}
        for k in range(len(items)):
            comps.setdefault(f2(k), []).append(items[k])
        rimes = []
        for r in rows:
            r["rime"] = {}
        for lst in comps.values():
            if len({it["c"] for _, it in lst}) < 2 or not any(it["j"] < rows[bb]["tail_from"] for bb, it in lst):
                continue
            cid = len(rimes)
            anchor_g = None
            for bb, it in lst:
                last = [x for x in streams[bb] if x["j"] >= rows[bb]["tail_from"]]
                if rows[bb]["g"] is not None and last and last[-1] is it:
                    anchor_g = rows[bb]["g"]
            rimes.append({"key": lst[0][1]["v"], "n": len(lst), "g": anchor_g})
            for bb, it in lst:
                rows[bb]["rime"][(it["j"], it["ci"])] = cid
        # VOWEL COLOURS: a prominent syllable takes the colour of its vowel when that vowel recurs in different words of the slot (or is a closing vowel of an end rhyme);
        # SOLID underline = another word within two bars has the same vowel AND ending (an exact rime), DOTTED = same vowel, different ending.
        vow_items: dict = {}
        for bb, st in enumerate(streams):
            for it in st:
                vow_items.setdefault(it["v"], []).append((bb, it))
        # weak "ɪ" syllables of content words (the -tic of transatlantic, -ing) cannot make a family but may JOIN one with a prominent member within a bar (tic ~ chips)
        joiners = []
        for bb, r in enumerate(rows):
            for j, w in enumerate(r["words"]):
                c = core(w)
                if not c or c in REDUCED_FUNC:
                    continue
                sy = rapfit._syl(c)
                for k, x in enumerate(sy):
                    if x[0] == "ɪ" and not rapfit.prominent(x):
                        joiners.append((bb, {"j": j, "ci": k if len(r["chunks"].get(j, [])) == len(sy) else 0, "v": "ɪ", "c": c, "syl": x}))
        anchor_v = set()
        for bb, r in enumerate(rows):
            if r["g"] is not None:
                for x in [x for x in streams[bb] if x["j"] >= r["tail_from"]][-2:]:
                    anchor_v.add(x["v"])
        vmin = 2 if len(bars) <= 4 else 3
        active: list = []
        for bb, st in enumerate(streams):
            for it in st:
                v = it["v"]
                if v not in active:
                    ws_ = {x["c"] for _, x in vow_items[v]}
                    near_j = {x["c"] for jb, x in joiners if x["v"] == v and any(abs(jb - pb) <= 1 for pb, _ in vow_items[v])}
                    pair_ = any(abs(b1 - b2) <= 2 and x1["c"] != x2["c"] and rapfit.syl_match(x1["syl"], x2["syl"]) == 2
                                for i1, (b1, x1) in enumerate(vow_items[v]) for (b2, x2) in vow_items[v][i1 + 1:])
                    if len(ws_) >= vmin or len(ws_ | near_j) >= vmin or (v in anchor_v and len(ws_) >= 2) or pair_:   # two words that are an exact rime (flew / brew) are enough
                        active.append(v)
        for r in rows:
            r["vow"], r["tl"] = {}, {}
        for v in active:
            for bb, it in vow_items[v]:
                exact = any(abs(bb - b2) <= 2 and it2["c"] != it["c"] and rapfit.syl_match(it["syl"], it2["syl"]) == 2 for b2, it2 in vow_items[v] if it2 is not it)
                rows[bb]["vow"][(it["j"], it["ci"])] = (active.index(v), exact, v)
            for jb, x in joiners:
                if x["v"] == v and any(abs(jb - pb) <= 1 and pit["c"] != x["c"] for pb, pit in vow_items[v]):
                    rows[jb]["vow"].setdefault((x["j"], x["ci"]), (active.index(v), False, v))
        for r in rows:                                          # a matched weak closing syllable carries on the colour of the stressed syllable before it
            carry = None
            for j in range(r["tail_from"], len(r["words"])):
                for ci in range(len(r["chunks"].get(j, [])) or 1):
                    if (j, ci) in r["vow"]:
                        carry = r["vow"][(j, ci)][0]
                    elif carry is not None and (r["sy"].get(j, {}).get(ci) or 0) >= 1:
                        r["tl"][(j, ci)] = carry
        out["chain_occ"] = out.get("chain_occ", 0) + sum(len(c["occ"]) for c in chains)
        out["chain_types"] = out.get("chain_types", 0) + len(chains)
        out["chain_null"] = out.get("chain_null", 0.0) + chain_null(streams)
        out["rep_syl"] = out.get("rep_syl", 0) + rep
        out["rep_in_chain"] = out.get("rep_in_chain", 0) + in_chain
        out["bars_chain"] = out.get("bars_chain", 0) + sum(1 for r in rows if r["chain"])
        scheme = "".join(r["letter"] if r["letter"] != "·" else "x" for r in rows)
        out["slots"][slot] = {"rows": rows, "scheme": scheme, "groups": {letters[g]: [tails[m] for m in members[g]] for g in members}, "chains": chains, "fam": fam, "rimes": rimes, "vowels": active}
        out["bars"] += len(rows)
        out["paired"] += sum(1 for r in rows if r["g"] is not None)
        out["perfect"] += sum(1 for r in rows if r["g"] is not None and (r["score"] or 0) >= rapfit.STRONG)
        out["tech"] += sum(1 for r in rows if r["g"] is not None and (r["score"] or 0) < rapfit.FLOOR)
        out["internal"] += sum(1 for r in rows for m in r["marks"].values() if m[0] == "int")
        out["al_bars"] += sum(1 for r in rows if r["al"])
        out["al_words"] += sum(len(r["al"]) for r in rows)
    return out


# ------------------------------------------------------------------ rendering

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--muted:#667085;--line:#e4e7ec;--card:#f8f9fb;--s:78%;--l-end:82%;--l-int:92%;--al-l:36%;--chain:#344054}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#101317;--fg:#e8eaed;--muted:#9aa4af;--line:#262c34;--card:#161a20;--s:45%;--l-end:30%;--l-int:21%;--al-l:72%;--chain:#d0d5dd}}
:root[data-theme="dark"]{--bg:#101317;--fg:#e8eaed;--muted:#9aa4af;--line:#262c34;--card:#161a20;--s:45%;--l-end:30%;--l-int:21%;--al-l:72%;--chain:#d0d5dd}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;padding:20px 16px 60px;max-width:1180px;margin:0 auto}
h1{font-size:22px;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 14px;max-width:80ch}
.key{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin:10px 0 18px;font-size:13px;color:var(--muted)}
.sum{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-bottom:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.card b{font-size:15px}.card div{font-size:13px;color:var(--muted)}
section{margin:0 0 26px}h2{font-size:16px;margin:0 0 8px;display:flex;gap:10px;flex-wrap:wrap;align-items:baseline}
h2 small{color:var(--muted);font-weight:400;font-size:12px;font-family:ui-monospace,Consolas,monospace}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:820px){.cols{grid-template-columns:1fr}}
.col{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.col h3{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:0 0 6px;font-weight:600}
.bar{display:grid;grid-template-columns:22px 18px 1fr;gap:6px;padding:2px 0;align-items:baseline}
.n{color:var(--muted);font-size:11px;text-align:right}.ltr{font:600 12px ui-monospace,Consolas,monospace;color:var(--muted)}
.txt{overflow-wrap:anywhere}
.r{border-radius:3px;padding:0 1px}
.r.vw{background:hsl(var(--h) var(--s) var(--l-end));text-underline-offset:3px}
.r.vw.x{text-decoration:underline solid}.r.vw.n{text-decoration:underline dotted}
.r.tl{background:hsl(var(--h) var(--s) var(--l-int))}
.r.e{text-decoration:underline wavy #d92d20;text-underline-offset:3px}
.r.ch{box-shadow:inset 0 -3px 0 var(--chain)}
.nm{text-decoration:underline dashed var(--muted);text-underline-offset:3px}
.gd{letter-spacing:1px}.r.dot{padding:0 2px;font-weight:700}
sup{font-size:9px;color:var(--muted);margin-left:1px}sup.eb{color:#d92d20}
.solo{text-decoration:underline;text-decoration-color:var(--muted);text-decoration-style:dotted;text-underline-offset:3px}
.al{font-weight:800;color:hsl(var(--a) 80% var(--al-l,36%))}.gap{color:var(--muted);letter-spacing:1px;opacity:.7}
.leg{font-size:12px;color:var(--muted);margin-top:6px}.leg b{font-family:ui-monospace,Consolas,monospace;color:var(--fg)}
"""


def _word_html(row: dict, j: int, w: str) -> str:
    """one word, syllable by syllable. FILL = the syllable's vowel (same vowel, same colour); UNDERLINE = how exact (solid: same ending too, dotted: different ending);
    a pale fill continues that colour over a matched weak closing syllable; wavy red = an unstressed tail echo; a dark bar under it = part of a multi-syllable internal rhyme;
    bold coloured opening letters = alliteration."""
    m = re.match(r"^([^A-Za-z']*)(.*?)([^A-Za-z']*)$", w)
    pre, body, suf = m.group(1), m.group(2), m.group(3)
    chunks = row["chunks"].get(j) or [body]
    if "".join(chunks) != body:
        chunks = [body]
    mark = row["marks"].get(j)
    states = row["sy"].get(j, {})
    al = row["al"].get(j)
    parts = []
    for ci, ch in enumerate(chunks):
        txt = _al_wrap(ch, al) if (ci == 0 and al is not None) else html.escape(ch)
        vw = row["vow"].get((j, ci))
        tl = row["tl"].get((j, ci))
        ch_ = (j, ci) in row["chain"]
        st = states.get(ci, states.get("all")) if (mark and mark[0] == "end" and mark[1] is not None) else None
        cls, style, tip = [], "", ""
        if vw is not None:
            cls, style = ["r", "vw", "x" if vw[1] else "n"], f"--h:{HUES[vw[0] % len(HUES)]}"
            tip = f"vowel {vw[2]}: " + ("same ending as another word nearby (exact rime)" if vw[1] else "same vowel, different ending")
        elif tl is not None:
            cls, style, tip = ["r", "tl"], f"--h:{HUES[tl % len(HUES)]}", "matching closing syllable"
        elif st is not None and st < 0:
            cls, tip = ["r", "e"], "unstressed tail echo: the stressed syllables do not rhyme"
        elif mark and mark[0] == "end" and mark[1] is None:
            cls = ["solo"]
        elif mark and mark[0] == "end" and st is None and mark[1] is not None and not ch_:
            cls, tip = ["nm"], "grouped with the other endings, but this syllable matches nothing"
        if ch_:
            cls = (cls or ["r"]) + (["ch"] if "r" in (cls or ["r"]) else [])
            tip = (tip + "; " if tip else "") + "part of a multi-syllable internal rhyme"
        if cls:
            parts.append(f'<span class="{" ".join(cls)}"' + (f' style="{style}"' if style else "") + (f' title="{tip}"' if tip else "") + f">{txt}</span>")
        else:
            parts.append(txt)
    return html.escape(pre) + "".join(parts) + html.escape(suf)


def _hidden_html(row: dict, j: int, w: str) -> str:
    """a word the project file must not print (rule 4): one dot per syllable, and a dot keeps the colour, underline and chain bar of the syllable it stands for, so the
    rhyme structure stays visible without the letters (a yellow dot in the same colour as stick / chick is the whip you cannot read)."""
    n = len(row["chunks"].get(j) or []) or nsyl(core(w))
    out = []
    for ci in range(n):
        vw, tl, chn = row["vow"].get((j, ci)), row["tl"].get((j, ci)), (j, ci) in row["chain"]
        if vw is not None:
            out.append(f'<span class="r vw {"x" if vw[1] else "n"} dot{" ch" if chn else ""}" style="--h:{HUES[vw[0] % len(HUES)]}" title="hidden syllable, vowel {html.escape(vw[2])}">•</span>')
        elif tl is not None:
            out.append(f'<span class="r tl dot{" ch" if chn else ""}" style="--h:{HUES[tl % len(HUES)]}" title="hidden syllable, matching closing syllable">•</span>')
        elif chn:
            out.append('<span class="r ch dot" title="hidden syllable in a multi-syllable internal rhyme">•</span>')
        else:
            out.append('<span class="gap">·</span>')
    return '<span class="gd">' + "".join(out) + "</span>"


def _bar_html(row: dict, skeleton: bool) -> str:
    ws = row["words"]
    shown = {k[0] for k in row["chain"]} | {k[0] for k in row["rime"]}
    visible = lambda j: row["marks"].get(j) is not None or j in row["al"] or j in shown or (row["g"] is None and j >= row["tail_from"])
    hide: set = set()
    if skeleton:                  # rule 4: never more than 3 consecutive words of the original on show, even when a short bar is all rhyme
        # a hyphenated token counts as its parts: 'duck-duck' is two words, and counting it as one let a 4-word run of the original through (14 Oct 2026)
        n_words = lambda j: max(1, len([p for p in re.split(r"[-–]+", ws[j]) if re.search(r"[A-Za-z]", p)]))
        run: list = []
        for j in range(len(ws) + 1):
            if j < len(ws) and visible(j):
                run.append(j)
            else:
                while run and sum(n_words(k) for k in run) > 3:
                    hide.add(run.pop(0))
                run = []
    out = []
    for j, w in enumerate(ws):
        if j in hide or (skeleton and not visible(j)):
            out.append(_hidden_html(row, j, w))
        else:
            out.append(_word_html(row, j, w))
    return " ".join(out)


def _col(title: str, data: dict, slot: str, skeleton: bool) -> str:
    s = data["slots"].get(slot)
    if not s:
        return f'<div class="col"><h3>{html.escape(title)}</h3><div class="leg">not in this text</div></div>'
    rows = []
    for i, r in enumerate(s["rows"], 1):
        badge = "" if r["g"] is None else (f'<sup title="rhyme depth in syllables">{r["depth"]}</sup>' if r["depth"] else '<sup class="eb" title="only an unstressed tail echo">e</sup>' if r["echo"] else '<sup class="eb" title="no syllable matches in the tool">0</sup>')
        rows.append(f'<div class="bar"><span class="n">{i}</span><span class="ltr">{r["letter"]}{badge}</span><span class="txt">{_bar_html(r, skeleton)}</span></div>')
    nch = sum(len(c["occ"]) for c in s.get("chains", []))
    vleg = " ".join(f'<span class="r vw n" style="--h:{HUES[k % len(HUES)]}">{html.escape(v)}</span>' for k, v in enumerate(s.get("vowels", [])))
    leg = f'<div class="leg">scheme <b>{s["scheme"]}</b> · {nch} multi-syllable internal rhyme{"s" if nch != 1 else ""} · vowels: {vleg or "none repeat"}</div>'
    return f'<div class="col"><h3>{html.escape(title)}</h3>{"".join(rows)}{leg}</div>'


def _depth_line(a: dict) -> str:
    d = list(a.get("depths", []))
    one = sum(1 for _, k, e in d if k == 1)
    two = sum(1 for _, k, e in d if k == 2)
    three = sum(1 for _, k, e in d if k >= 3)
    echo = sum(1 for _, k, e in d if k == 0 and e > 0)
    none = sum(1 for _, k, e in d if k == 0 and e == 0)
    n = max(1, len(d))
    return (f"1 syllable {one} ({100 * one // n}%) · 2 syllables {two} ({100 * two // n}%) · 3+ {three} ({100 * three // n}%) · "
            f"unstressed tail echo only {echo} ({100 * echo // n}%) · no syllable match {none}")


def _card(title: str, a: dict, note: str) -> str:
    pct = lambda x, y: f"{100 * x // max(1, y)}%"
    return (f'<div class="card"><b>{html.escape(title)}</b><div>{a["bars"]} bars · {a["paired"]} have an end-rhyme partner ({pct(a["paired"], a["bars"])})</div>'
            f'<div>end-rhyme depth in syllables: {_depth_line(a)}</div>'
            f'<div>{a["internal"]} internal echoes = {a["internal"] / max(1, a["bars"]):.2f} per bar</div>'
            f'<div>multi-syllable internal rhymes: {a.get("chain_occ", 0)} occurrences in {a.get("bars_chain", 0)} bars ({a.get("chain_occ", 0) / max(1, a["bars"]):.2f}/bar); {a.get("chain_null", 0):.1f} would arise by chance in shuffled text</div>'
            f'<div>repeated vowels that form a pattern (a chain) rather than piling one sound up: {100 * a.get("rep_in_chain", 0) // max(1, a.get("rep_syl", 1))}%</div>'
            f'<div>{a["al_bars"]} bars with alliteration ({100 * a["al_bars"] // max(1, a["bars"])}%) · {a["al_words"]} alliterating words</div><div>{html.escape(note)}</div></div>')


def render(left: dict, right: dict, left_label: str, right_label: str, out_path: str, left_is_original: bool = False,
           skeleton_left: bool = False, ear_left: bool = False, title: str = "Rhyme map") -> dict:
    out = Path(out_path).expanduser().resolve()
    if left_is_original and not skeleton_left:
        priv = config.PRIVATE_ORIGINAL.parent.resolve()
        if priv not in out.parents:
            raise PermissionError(f"RULE 4: a full-text render of the original may only be written inside {priv}; refusing {out}. "
                                  f"Use skeleton_left=True (rhyming words only) for a file inside the project.")
    A = analyze(left, ear=ear_left)
    B = analyze(right, ear=False)
    slots = [s for s, _ in SLOTS if s in A["slots"] or s in B["slots"]]
    body = []
    for slot in slots:
        sa = A["slots"].get(slot, {}).get("scheme", "-")
        sb = B["slots"].get(slot, {}).get("scheme", "-")
        body.append(f'<section><h2>{html.escape(slot)}<small>{html.escape(left_label)} {sa} · {html.escape(right_label)} {sb}</small></h2><div class="cols">'
                    f'{_col(left_label + (" (rhyming words only)" if skeleton_left else ""), A, slot, skeleton_left)}{_col(right_label, B, slot, False)}</div></section>')
    note_a = ("groups: Joe's by-ear scheme" if ear_left else "groups: the repo grader") + ("; non-rhyming words hidden" if skeleton_left else "")
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>'
            f'<style>{CSS}</style></head><body><h1>{html.escape(title)}</h1>'
            f'<p class="sub">Rhymes coloured the way a rhyme highlighter does it: the end of every bar, any other stressed word in the section that echoes it, and alliteration inside each bar. '
            f'Same colour = same rhyme group. The colour shows what the repo\'s tools hear, not what is good.</p>'
            f'<div class="key"><span><b>fill</b> = the vowel of the syllable: the same vowel is the same colour</span>'
            f'<span><b>underline</b> <span class="r vw x" style="--h:210">solid</span> same vowel AND ending as another word nearby (an exact rime) <span class="r vw n" style="--h:210">dotted</span> same vowel, different ending</span>'
            f'<span><span class="r tl" style="--h:210">pale</span> a matched weak closing syllable</span><span><span class="r e">wavy red</span> unstressed tail echo only (the stressed syllables do not rhyme)</span>'
            f'<span><span class="r ch">dark bar</span> multi-syllable internal rhyme</span><span><span class="r vw n dot" style="--h:210">•</span> in the project file a hidden word is one dot per syllable, and a coloured dot is a syllable in a rhyme family (the letters stay in the private full-text version)</span><span><b class="al" style="--a:20">Bold</b> opening letters = alliteration</span>'
            f'<span>letter = scheme · <sup>n</sup> = end-rhyme depth in syllables</span></div>'
            f'<div class="sum">{_card(left_label, A, note_a)}{_card(right_label, B, "groups: the repo grader (pair rhymes at >= 0.78)")}</div>'
            f'{"".join(body)}</body></html>')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return {"path": str(out), "left": {k: A.get(k) for k in ("bars", "paired", "perfect", "tech", "internal", "al_bars", "al_words", "chain_occ", "chain_types", "chain_null", "bars_chain", "rep_syl", "rep_in_chain")}, "right": {k: B.get(k) for k in ("bars", "paired", "perfect", "tech", "internal", "al_bars", "al_words", "chain_occ", "chain_types", "chain_null", "bars_chain", "rep_syl", "rep_in_chain")}}


def selftest() -> tuple[bool, str]:
    import tempfile
    problems = []
    secs = {"Hook 1-4": ["I walk past the fox in the box", "Then talk to the clock on the dock", "Nobody knows what is in it", "He drinks from the clock in a minute"]}
    a = analyze(secs)
    rows = a["slots"]["Hook 1-4"]["rows"]
    if not (rows[0]["g"] is not None and rows[0]["g"] == rows[1]["g"]):
        problems.append(f"fox/box and clock/dock should group: {[r['g'] for r in rows]}")
    # 16 Oct 2026: a closing object pronoun joins the tail with the word before it ('caught me' rhymes like 'naughty'; Joe on the original's 46-52)
    if tail_text("shovel it".split()) != "shovel it" or tail_text("He took it from me".split()) != "from me" or tail_text("they caught me".split()) != "caught me":
        problems.append("tail extraction: clitics and a closing object pronoun should be absorbed into the tail")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.html"
        try:
            render(secs, secs, "L", "R", str(p), left_is_original=True, skeleton_left=False)
            problems.append("a full-text render of the original outside the private folder must be refused")
        except PermissionError:
            pass
        r = render(secs, secs, "L", "R", str(p), left_is_original=True, skeleton_left=True)
        text = p.read_text(encoding="utf-8")
        if " what " in text.split("</h1>", 1)[1].split('class="col"', 2)[1]:
            problems.append("skeleton mode must hide non-rhyming words")
        if "dock" not in text:
            problems.append("skeleton mode must still show the rhyming words")
    if set(alliteration("Front row on my phone".split())) != {0, 4}:
        problems.append(f"front/phone alliterate on /f/: {alliteration('Front row on my phone'.split())}")
    if alliteration("Said damn at the porno".split()):
        problems.append("no shared opening sound in 'Said damn at the porno'")
    if alliteration("German German German".split()):
        problems.append("a repeated word is repetition, not alliteration")
    return (not problems, "; ".join(problems) if problems else "clusters fox/box + clock/dock, absorbs clitic tails, refuses a full-text original outside the private folder, skeleton hides non-rhyming words, alliteration front~phone")
