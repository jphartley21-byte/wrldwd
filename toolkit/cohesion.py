"""Cohesion across sections: the JOINS (17 Oct 2026).

Joe: "I think because the sections are written seperately the song still lacks cohesion. Compare the cohesion of your draft to
the orignal", then "Dont just fix this draft but fix the pipeline so future naive writers don't make the same mistakes".

MEASURED FIRST (numbers only, rule 4; the probe compared the original with writing/song_toast_of_the_town_v1.md as it stood):
  NOT the difference, so NOT gated here:
    shared vocabulary   ours repeats MORE content words across sections (29 lemmas in 2+ sections vs the original's 16; 15 of
                        21 verse pairs share a word vs 12; 6 of 7 verse sections share a word with the hook vs 3 of 7). A gate on
                        shared words would push the wrong way.
    persona per section swagger and recount shares per section sit in the same range in both songs (each has one verse
                        section with no swagger bar at all).
  THE difference, gated here: what happens at each JOIN between two verse sections. All 6 of the original's joins are bridged:
  four open on a connective that carries the same monologue on (now / come on then / I just / and), and two reuse words from the
  bars just before the join, one of them a pun carried across the chorus into verse 2. Ours bridged 1 of 6 (an opening 'Now'),
  0 by a word: five sections opened cold, on a new scene, so each read as a separate story.

A JOIN = the last two bars of a verse section and the first two bars of the next verse section: V1 1-8 > V1 9-16 > V1 17-24 >
V1 25-32 > V1 33-44, then V1 33-44 > V2 1-8 (across the chorus), then V2 1-8 > V2 9-16. A join is
  WORD-bridged       when the two sides share a content word (a lemma) or a two-word phrase that is not two function words;
  CONNECTIVE-bridged when the next section's first bar opens on a connective (and, so, then, now, but, 'cause, till, still,
                     plus, come on then, go on then) or on 'just' / 'I just' (the original's own "just ... in" continuation).
Par (benchmark/cohesion_par.json, counts only): the original's number of bridged joins and of WORD bridges. Ours must reach both,
so a column of "And ..." openers cannot pass on its own. HARD in `ww gate` (song level); toolkit/tests/cohesion_flagged.txt holds
the joins Joe's complaint was about, and the selftest asserts they fail while the original passes.

  python toolkit/cohesion.py DRAFT.md            report + verdict
  python toolkit/cohesion.py --build ORIG.txt    write benchmark/cohesion_par.json (counts only)
  python toolkit/cohesion.py --selftest [ORIG]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAR = os.path.join(HERE, "..", "benchmark", "cohesion_par.json")
FLAGGED = os.path.join(HERE, "tests", "cohesion_flagged.txt")

VERSE_ORDER = ["V1 1-8", "V1 9-16", "V1 17-24", "V1 25-32", "V1 33-44", "V2 1-8", "V2 9-16"]
CONNECTIVES = {"and", "so", "then", "now", "but", "'cause", "cause", "cos", "till", "until", "still", "plus"}
PHRASE_OPENERS = ("come on then", "go on then", "just", "i just")
FUNCTION = {"a", "an", "the", "of", "to", "in", "on", "at", "for", "with", "and", "or", "but", "by", "from", "as", "i", "i'm",
            "me", "my", "you", "your", "it", "it's", "is", "was", "be", "that", "this", "he", "she", "we", "they", "his", "her",
            "our", "their", "them", "him", "are", "were", "so", "then", "now", "up"}
GENERIC = {"be", "have", "do", "get", "go", "make", "say", "come", "know", "see", "take", "want", "let", "put", "need", "look",
           "keep", "give", "tell", "feel", "yeah", "nah", "oh", "just", "really", "well", "too", "very"}


def _nlp():
    import recount
    return recount._nlp()


def _words(bar):
    return [w for w in re.findall(r"[a-z][a-z']*", bar.lower().replace("’", "'"))]


def _lemmas(bars):
    out = set()
    for b in bars:
        for t in _nlp()(b):
            if t.pos_ in ("NOUN", "PROPN", "VERB", "ADJ", "ADV", "NUM") and not t.is_stop and t.is_alpha \
                    and t.lemma_.lower() not in GENERIC:
                out.add(t.lemma_.lower())
    return out


def _pairs(bars):
    out = set()
    for b in bars:
        w = _words(b)
        out |= {(x, y) for x, y in zip(w, w[1:]) if not (x in FUNCTION and y in FUNCTION)}
    return out


def opener(bar):
    """the connective the bar opens on, or None."""
    w = _words(bar)
    head = " ".join(w[:3])
    for p in PHRASE_OPENERS:
        if head == p or head.startswith(p + " "):
            return p
    return w[0] if w and w[0] in CONNECTIVES else None


def join(before, after):
    """{'word': [shared words / phrases], 'connective': str | None, 'bridged': bool} for the last bars of one section and the first
    bars of the next."""
    shared = sorted(_lemmas(before) & _lemmas(after)) + [" ".join(p) for p in sorted(_pairs(before) & _pairs(after))]
    con = opener(after[0]) if after else None
    return {"word": shared, "connective": con, "bridged": bool(shared or con)}


def joins(sections):
    """[(from, to, join)] over the verse sections present, in song order."""
    have = [s for s in VERSE_ORDER if sections.get(s)]
    return [(a, b, join(sections[a][-2:], sections[b][:2])) for a, b in zip(have, have[1:])]


def measure(sections):
    J = joins(sections)
    return {"joins": len(J), "bridged": sum(j["bridged"] for _, _, j in J), "word": sum(bool(j["word"]) for _, _, j in J),
            "detail": J}


def par():
    if not os.path.exists(PAR):
        return None
    return json.load(open(PAR, encoding="utf-8"))


def hard(sections):
    """hard messages for a full song (the gate's song-level check). Empty when there is no par or fewer than all verse sections."""
    p = par()
    if not p or not all(sections.get(s) for s in VERSE_ORDER):
        return []
    m = measure(sections)
    out = []
    cold = [f"{a} > {b}" for a, b, j in m["detail"] if not j["bridged"]]
    if m["bridged"] < p["bridged"]:
        out.append(f"cohesion: {m['bridged']} of {m['joins']} section joins pick up from the section before (the original: "
                   f"{p['bridged']} of {p['joins']}). Cold opens: {', '.join(cold)}. Reuse a word from the last two bars before "
                   f"the join, or open the next section on a connective that carries the monologue on (Now / Come on then / I just; "
                   f"And / So / Then / But at most twice each in the song)")
    if m["word"] < p["word"]:
        out.append(f"cohesion: {m['word']} section joins share a word or phrase across the join (the original: {p['word']}). "
                   f"Reuse a word from the last two bars of a section in the first two bars of the next (the original carries "
                   f"a pun across the chorus into verse 2)")
    return out


def join_rule(slot, prev_bars=None):
    """the join as a writing instruction for the section `slot` (empty for the hook and for V1 1-8, which follows the chorus)."""
    if slot not in VERSE_ORDER or slot == VERSE_ORDER[0]:
        return ""
    prev = VERSE_ORDER[VERSE_ORDER.index(slot) - 1]
    head = (f"JOIN, HARD (checked on the whole song): this section continues straight on from {prev}; it is NOT a new story. "
            f"Bar 1 must pick up from {prev}'s last two bars: reuse a word or a phrase from them (a pun on one is best), or open on a "
            f"connective that carries the same monologue on (Now / Come on then / Go on then / I just / Still / Till; And / So / Then / "
            f"But open at most two bars each in the whole song, the meaning gate's cap).")
    if prev_bars:
        head += " Those bars: " + " / ".join(prev_bars[-2:])
    return head


def sections_of_original(path):
    sys.path.insert(0, HERE)
    import fitbar
    L = [l.strip() for l in open(path, encoding="utf-8") if l.strip()][:76]
    return {s: L[fitbar.STARTS[s] - 1:fitbar.STARTS[s] - 1 + n] for s, n in zip(fitbar.SLOTS, fitbar.SIZES)}   # STARTS are 1-based bars


def build(orig_path):
    m = measure(sections_of_original(orig_path))
    json.dump({"_note": "Section joins of the ORIGINAL (counts only, rule 4), built by toolkit/cohesion.py --build. A join is the last "
                        "two bars of a verse section and the first two of the next; bridged = a connective opener or a shared word.",
               "joins": m["joins"], "bridged": m["bridged"], "word": m["word"]}, open(PAR, "w", encoding="utf-8"), indent=1)
    return m


def flagged(path=FLAGGED):
    """{song: {slot: [bars]}} from 'song | slot | bar' lines (the drafts Joe called incohesive, the boundary bars only)."""
    out = {}
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="utf-8"):
        if l.strip() and not l.startswith("#"):
            song, slot, bar = [x.strip() for x in l.split("|", 2)]
            out.setdefault(song, {}).setdefault(slot, []).append(bar)
    return out


def selftest(orig_path=None):
    ok = True
    p = par()
    if not p:
        print("cohesion selftest: FAILED (no benchmark/cohesion_par.json; run --build ORIG)")
        return False
    if orig_path:
        m = measure(sections_of_original(orig_path))
        good = m["bridged"] >= p["bridged"] and m["word"] >= p["word"] and not hard(sections_of_original(orig_path))
        print(f"{'ok ' if good else 'XX '} the original passes its own par ({m['bridged']} of {m['joins']} joins bridged, {m['word']} by a word)")
        ok &= good
    F = flagged()
    for song, S in F.items():
        h = hard(S)
        print(f"{'ok ' if h else 'XX '} {song}: Joe's 'lacks cohesion' draft fails the join gate" + (f" ({len(h)} message(s))" if h else " (NOT CAUGHT)"))
        ok &= bool(h)
    ok &= bool(F)
    # fixtures: a cold open is not a bridge; a connective, a shared word and a shared phrase are
    t = [join(["I ride the bike to Rome", "And I park it by the sea"], ["Camden Lock, a pint of mild"])["bridged"] is False,
         join(["I ride the bike to Rome"], ["And then the bike broke down"])["bridged"] is True,
         join(["Tap him on the head, duck duck goose"], ["I sip that goose till I lose"])["word"] == ["goose"],
         join(["I'm out in Spain"], ["Out here you want some"])["word"] == ["out here"] or "out here" in join(["like I'm out here"], ["I'm out here, you want some"])["word"],
         opener("Come on then, touch down in Leeds") == "come on then", opener("In the bar") is None]
    print(f"{'ok ' if all(t) else 'XX '} join fixtures: {sum(t)} of {len(t)}")
    ok &= all(t)
    print("cohesion selftest: " + ("PASSED" if ok else "FAILED"))
    return ok


def main():
    a = sys.argv[1:]
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a and a[0] == "--build":
        m = build(a[1])
        print(f"cohesion par written: {m['bridged']} of {m['joins']} joins bridged, {m['word']} by a word")
        return 0
    if a and a[0] == "--selftest":
        return 0 if selftest(a[1] if len(a) > 1 else None) else 1
    sys.path.insert(0, HERE)
    import fitbar
    D, _ = fitbar.read_draft(a[0], with_cash=True)
    m = measure(D)
    for x, y, j in m["detail"]:
        print(f"  {x} > {y}: " + ("bridged" if j["bridged"] else "COLD") + (f" (opens on '{j['connective']}')" if j["connective"] else "")
              + (f" (shares {', '.join(j['word'])})" if j["word"] else ""))
    h = hard(D)
    for x in h:
        print("x " + x)
    print("COHESION: " + ("PASS" if not h else "FAIL"))
    return 0 if not h else 1


if __name__ == "__main__":
    sys.exit(main())
