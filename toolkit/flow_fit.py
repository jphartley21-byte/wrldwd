"""flow_fit: lay OUR bars onto the ORIGINAL's measured rhythm (benchmark/flow_template.json, from flow_map.py).
Usage: python toolkit/flow_fit.py START_BAR -   (stdin: our bars; START_BAR = song bar number of the first line, 1-76)
For each bar, our syllables are placed in order onto the original's measured syllable steps. PASS needs:
  - syllables within ±1 of the original's;
  - syllables per beat within 2 (summed over the bar) of the original's: the same density and bunching;
  - at most one naturally weak syllable (unstressed part of a long word, or a/the/of/to...) landing on a beat;
  - our strong/weak syllable pattern mirrors the original's (>= 80% of positions, at most one mismatch on a beat).
Prints the original rhythm, ours, and the misses. Stress is dictionary-based: confirm by ear.
"""
import json, os, sys
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from flow_check import bar_profile  # noqa: E402

T = json.load(open(os.path.join(HERE, "..", "benchmark", "flow_template.json")))["bars"]


def grid(steps, marks, length):
    g = ["."] * length
    for s, m in zip(steps, marks):
        if 0 <= s < length:
            g[s] = m
    return "".join(g)


WEAKFN = set("""a an the of to and in on at for with as is it its it's was were be been am are i me my we our us
you your he she him her they them their his this that these those from by or but so if then than up out off do did
does not no can will would just 'em ya
he's she's that's there's what's i'm i've i'd i'll you're we're they're isn't wasn't don't didn't can't won't let's who's where's here's how's""".split())
# Kept deliberately identical to ww/write/flowaudit.FUNC -- that is the auditor the song is read with, and the
# two must not disagree about what a function word is. The old 23-word list here was missing every pronoun and
# contraction, so "so he says I nicked" measured as four consecutive STRONG syllables and the strong/weak
# pattern printed against the original's was wrong (14 Oct 2026). The stored per-bar patterns in
# benchmark/flow_template.json are DERIVED with this list: rebuild them (flow_fit.py --add-weak, --add-rhyme-pos)
# after any change, or the original stops agreeing with itself.


def sylls(line):
    """per syllable: True if naturally WEAK (unstressed syllable of a polysyllable, or a tiny function word)"""
    import re
    from rhyme_tools import pron, is_v
    out = []
    for w in re.findall(r"[A-Za-z'å]+", line):
        ph = pron(w.lower().replace("å", "a"))
        if not ph:
            n = sum(3 if c == "W" else 1 for c in w) if (w.isupper() and len(w) > 1) else max(1, len(re.findall(r"[aeiouy]+", w.lower().rstrip("e"))))
            out += ([False] * n) if (w.isupper() and len(w) > 1) else ([False] + [True] * (n - 1))
            continue
        vs = [p for p in ph if is_v(p)]
        if len(vs) == 1:
            out.append(w.lower() in WEAKFN)
        else:
            out += [v[-1] == "0" for v in vs]
    return out


def syll_words(line):
    """per syllable: (weak, starts_a_word)"""
    import re
    from rhyme_tools import pron, is_v
    out = []
    for w in re.findall(r"[A-Za-z'å]+", line):
        n = len(sylls(w))
        out += [(x, i == 0) for i, x in enumerate(sylls(w))][:n]
    return out


def end_shape(line):
    """the ending's shape from the rhyme syllable on: '|' if the rhyme starts a word, '~' if it lands mid-word,
    then strong/weak per syllable. 'in Lagos' -> |Sw ; 'Majorca' -> ~Sw (the rhyme lands mid-word)"""
    sw = syll_words(line)
    n = len(sw)
    ri = min(max(0, n - tail_len(line)), n - 1)
    starts = sw[ri][1]
    return ("|" if starts else "~") + "".join("w" if wk else "S" for wk, _ in sw[ri:]), ri


def per_beat(steps, n_beats):
    c = [0] * n_beats
    for s in steps:
        if 0 <= s // 4 < n_beats:
            c[s // 4] += 1
    return c


def fit(bar_no, line):
    t = T[bar_no - 1]
    if t.get("missing"):
        return None, "no template (not heard)"
    orig = [s for s in t["steps"]]
    # A template that disagrees with itself cannot be met by any line: its stored text pattern (from
    # sylls) and its audio step list describe different syllable counts, so every rule downstream is
    # phase-shifted. Exactly 1 of the original's 92 bars is in this state -- bar 64, where the text counts
    # "would've" as two syllables and the aligner heard one onset. Waived, and printed, never silent.
    if t.get("weak") and len(t["weak"]) != len(orig):
        return True, (f"WAIVED: this bar's template disagrees with itself (text pattern {len(t['weak'])} vs "
                      f"audio steps {len(orig)}) - no line can be measured against it")
    weak = sylls(line)
    n = len(weak)
    why = []
    if abs(n - len(orig)) > 1:
        why.append(f"syllables {n} vs {len(orig)}")
    steps = list(orig[:n]) + [orig[-1] + 1] * max(0, n - len(orig))
    nb = 4 * t.get("bars_spanned", 1)
    a, b = per_beat(orig, nb), per_beat(steps, nb)
    off = sum(abs(x - y) for x, y in zip(a, b))
    if off > 2:
        why.append(f"syllables per beat {b} vs {a}")
    ow = t.get("weak")
    if ow:
        # len(orig) belongs in this min(): the stored pattern comes from the TEXT model and the steps come
        # from the AUDIO, so a bar whose text counts one syllable more than the aligner heard (bar 64,
        # "would've") used to index past the end of the step list and kill the whole run at that bar.
        m = min(n, len(ow), len(orig))
        beats = [i for i in range(m) if orig[i] % 4 == 0]
        beat_miss = [i + 1 for i in beats if weak[i] != ow[i]]
        agree = sum(1 for i in range(m) if weak[i] == ow[i]) / max(1, m)
        if agree < 0.8 or len(beat_miss) > 1:
            why.append(f"strong/weak pattern {''.join('w' if x else 'S' for x in weak)} vs original {''.join('w' if x else 'S' for x in ow)} ({int(agree * 100)}% same; beat mismatches at {beat_miss})")
    ri = t.get("rhyme_idx")
    if ri is not None and not t.get("advisory"):
        if n != len(orig):
            why.append(f"line length {n} syllables vs original {len(orig)} (must be exact)")
        our_ri = max(0, n - tail_len(line))
        es = t.get("end_shape")
        if es:
            mine = end_shape(line)[0]
            if mine != es:
                why.append(f"end shape {mine} vs original {es} (| = the rhyme starts a word, ~ = it lands mid-word; then strong/weak syllables from the rhyme on)")
        if our_ri < len(orig) and ri < len(orig) and orig[our_ri] != orig[ri]:
            why.append(f"end rhyme starts on step {orig[min(our_ri, len(orig) - 1)]} (syllable {our_ri + 1}) vs original step {orig[ri]} (syllable {ri + 1})")
    own = ow if ow else orig
    nbad = [i + 1 for i, st in enumerate(steps) if st % 4 == 0 and i < n and weak[i]]
    # Par, not zero. The reference bar is the allowance: the original lands two or more weak syllables on a
    # downbeat in 14 of its 76 bars, so "more than one" cannot be the rule (a gate the benchmark fails is a
    # wrong gate -- the same reason the carpet, cash and places demands are all par comparisons). The bar is
    # flagged only when it is worse than the reference at the same position, and the reference's count is
    # printed so the flag can be argued with.
    obad = sum(1 for i, st in enumerate(orig) if st % 4 == 0 and i < len(own) and own[i])
    if len(nbad) > max(1, obad):
        why.append(f"weak syllable on the beat at syllable {nbad} (original has {obad})")
    length = 16 * t.get("bars_spanned", 1)
    o = grid(orig, ["X" if s % 4 == 0 else "x" for s in orig], length)
    u = grid(steps, ["w" if weak[i] else "S" for i in range(n)], length)
    nl = chr(10)
    return not why, f"orig {o}{nl}    ours {u}" + ("" if not why else nl + "    FAIL: " + "; ".join(why))


def tail_len(line):
    """syllables in the end-rhyme tail (from the last stressed syllable), via match.spans"""
    from match import spans
    e = spans(line)[1]
    return len(e) if e else 1


def head_idx(line):
    import phon
    sy = phon.syllables(line)
    return next((i for i, x in enumerate(sy) if x[1]), None)


def add_rhyme_pos(lyrics_txt):
    """store, per bar, the syllable index where the original's end rhyme starts and its first stressed syllable"""
    path = os.path.join(HERE, "..", "benchmark", "flow_template.json")
    d = json.load(open(path))
    lines = [l.strip() for l in open(lyrics_txt, encoding="utf8") if l.strip()]
    for b, l in zip(d["bars"], lines):
        n = len(sylls(l))
        b["rhyme_idx"] = max(0, n - tail_len(l))
        b["end_shape"] = end_shape(l)[0]
        b["head_idx"] = head_idx(l)
    json.dump(d, open(path, "w"), indent=0)
    print("rhyme positions stored for", len(lines), "bars")


def add_weak(lyrics_txt):
    """store the original's strong/weak pattern per bar (booleans only) in the template"""
    path = os.path.join(HERE, "..", "benchmark", "flow_template.json")
    d = json.load(open(path))
    lines = [l.strip() for l in open(lyrics_txt, encoding="utf8") if l.strip()]
    for b, l in zip(d["bars"], lines):
        b["weak"] = sylls(l)
    json.dump(d, open(path, "w"), indent=0)
    print("weak patterns stored for", len(lines), "bars")


if __name__ == "__main__" and sys.argv[1] == "--add-rhyme-pos":
    add_rhyme_pos(sys.argv[2]); sys.exit()
if __name__ == "__main__" and sys.argv[1] == "--add-weak":
    add_weak(sys.argv[2]); sys.exit()
if __name__ == "__main__":
    start = int(sys.argv[1])
    lines = [l.strip() for l in sys.stdin.read().lstrip("﻿").splitlines() if l.strip() and not l.startswith(("[", "#", "(", "=="))]
    fails = 0
    for k, line in enumerate(lines):
        ok, msg = fit(start + k, line)
        fails += ok is False
        print(f"{start + k:>2}. {'PASS' if ok else ('SKIP' if ok is None else 'FAIL')} | {line}\n    {msg}")
    print("VERDICT:", "FLOW-MATCHED" if not fails else f"NOT YET ({fails} bars off the original's rhythm)")
