"""rubric_score: score a 4-bar quad against the benchmark rubric's MEASURABLE criteria.

  python toolkit/rubric_score.py FILE|-        # blank line = new quad (4 bars each)

For each measurable rubric criterion it prints OURS vs PAR (the original's measured number) and a
verdict (BEATS / MATCH / BELOW). PAR comes from benchmark/original_profile.json (numbers only) and
the documented counts in benchmark/bars_1-8_breakdown.md; no original lyrics are stored or read.
Criteria that need a whole chain (length/coverage, hinge, bookend, escalation) or a human ear
(nonchalance, echo, lexical sets, lived detail, cringe, poster test) are listed as MANUAL and NOT scored.

Rubric ref: benchmark/benchmark_rubric.md (41 criteria; 3 = "matches the original"). A 3 here still
does NOT mean a bar is good — meaning and ear stay human (gates G1-G6).
"""
import contextlib
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rhyme_tools as rt          # noqa: E402
from flow_check import bar_profile  # noqa: E402

PROFILE = os.path.join(HERE, "..", "benchmark", "original_profile.json")
# The original's lyrics live OUTSIDE the project (CLAUDE.md rule 4): read-only input, never stored.
ORIG = os.path.join(os.path.expanduser("~"), "Documents", "Worldwide_private", "original_lines.txt")
REF_SLOTS = ["Hook 1-4", "Hook 5-8"]   # the benchmark task's 8 bars
# documented par values that are not in the profile (rubric / breakdown text)
PAR_DOC = {"enjamb": 1, "redup": 1, "carpet": 5 / 8, "numbers": 0}


def par(slots=None):
    P = json.load(open(PROFILE))
    slots = [P[s] for s in (slots or REF_SLOTS)]
    soft = max(sum(1 for b in s["bars"] if b["syl"] > b["grid"][-1]) for s in slots)
    spread = max(max(b["syl"] for b in s["bars"]) - min(b["syl"] for b in s["bars"]) for s in slots)
    flow = {k: max(sum(b[k] for b in s["bars"]) for s in slots) for k in ("clash", "pause", "cluster")}
    return {
        "soft": soft, "spread": spread,
        "internal": max(s["quad"]["internal_bars"] for s in slots),
        "multisyl": max(s["quad"]["multisyl"] for s in slots),
        "allit": max(s["quad"]["allit_bars"] for s in slots),
        "clash": flow["clash"], "pause": flow["pause"], "cluster": flow["cluster"], **PAR_DOC,
    }


def end_vowels(bar):
    """(anchor vowel, last-two-vowel tail) of the bar's final word — either pattern can be the carpet."""
    ws = re.findall(r"[A-Za-z']+", bar)
    if not ws:
        return None, None
    ph = rt.pron(ws[-1])
    if not ph:
        return None, None
    vi = [i for i, p in enumerate(ph) if rt.is_v(p)]
    if not vi:
        return None, None
    tail = "-".join(rt.strip(ph[i]) for i in vi[-2:])
    return rt.stressed_vowel(ph), tail


def carpet_share(bars):
    """best-of: share of end words on the commonest anchor vowel, or on the commonest 2-vowel tail."""
    pairs = [end_vowels(b) for b in bars]
    a = [x for x, _ in pairs if x]
    t = [y for _, y in pairs if y]
    sa = max((a.count(v) for v in set(a)), default=0) / len(a) if a else 0.0
    st = max((t.count(v) for v in set(t)), default=0) / len(t) if t else 0.0
    return max(sa, st)


def hygiene(bars):
    bad = []
    for b in bars:
        for w in re.findall(r"[A-Za-z']+", b):
            lw = re.sub(r"[^a-z]", "", w.lower())
            if lw in rt.BANNED:
                bad.append(f"BANNED:{lw}")
            elif rt.pron(w) is None:
                bad.append(f"OOV:{w}")
    return sorted(set(bad))


def score_quad(bars):
    q = rt.quad_stats(bars)
    prof = [bar_profile(b) for b in bars]
    syl = [p["syl"] for p in prof]
    soft = sum(1 for p in prof if p["syl"] > p["grid"][-1]) if all(p["grid"] for p in prof) else 0
    carpet = carpet_share(bars)
    flow = {k: sum(p[k] for p in prof) for k in ("clash", "pause", "cluster")}
    return dict(
        syl=syl, spread=(max(syl) - min(syl)) if syl else 0, soft=soft,
        internal=q["internal_bars"], multisyl=q["multisyl"], mosaic=q["mosaic"],
        homophones=q["homophones"], enjamb=q["enjamb"], redup=q["redup"], allit=q["allit_bars"],
        carpet=carpet, numbers=q["numbers"], flow=flow, hygiene=hygiene(bars),
    )


def verdict(ours, parv, lower_better=False):
    if lower_better:
        return "BEATS" if ours < parv else ("MATCH" if ours == parv else "BELOW")
    return "BEATS" if ours > parv else ("MATCH" if ours == parv else "BELOW")


# Counts that must be compared per bar, since a slot profile may cover more bars than the
# block we are measuring (e.g. a 4-bar quad against an 8-bar verse slot).
COUNT_KEYS = ("soft", "internal", "multisyl", "mosaic", "homophones", "enjamb", "redup",
              "allit", "numbers", "cutup", "band")
FLOW_KEYS = ("clash", "pause", "cluster")


def block_stats(bars):
    s = score_quad(bars)
    s["cutup"] = s["mosaic"] + s["homophones"]
    s["band"] = sum(1 for x in s["syl"] if 5 <= x <= 14)
    return s


def per_bar(stats, nbars):
    out = dict(stats)
    for k in COUNT_KEYS:
        v = out.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[k] = v / nbars
    if isinstance(out.get("flow"), dict):
        out["flow"] = {k: v / nbars for k, v in out["flow"].items()}
    return out


def rate_margin(bars, slot_par):
    """Criteria won minus lost when `bars` is compared with `slot_par`, per bar.

    Per-bar comparison keeps the test fair when the block is shorter than the slot
    profile, so a 4-bar quad is not asked to beat an 8-bar slot's raw counts.
    """
    n_par = len(slot_par.get("syl") or []) or len(bars)
    ours = per_bar(block_stats(bars), len(bars))
    theirs = per_bar(slot_par, n_par)
    w = l = 0
    for _, _, key, lower, _ in CRIT:
        if key in FLOW_KEYS:
            if key not in ours["flow"] or key not in theirs.get("flow", {}):
                continue
            ov, mv = theirs["flow"][key], ours["flow"][key]
        else:
            if key not in ours or key not in theirs:
                continue
            ov, mv = theirs[key], ours[key]
        if lower:
            w += mv < ov
            l += mv > ov
        else:
            w += mv > ov
            l += mv < ov
    return w - l


def rate_verdict(bars, slot_par):
    m = rate_margin(bars, slot_par)
    return "BEATS" if m > 0 else ("MATCH" if m == 0 else "loses")


# (rubric ref, label, key, higher/lower better, is_float)
CRIT = [
    ("2", "weak/feminine endings", "soft", False, False),
    ("5", "line-length spread", "spread", False, False),
    ("7", "bars with internal rhyme", "internal", False, False),
    ("8", "multisyllabic runs", "multisyl", False, False),
    ("8b", "cut-ups (mosaic+homophone)", "cutup", False, False),
    ("9", "enjambed rhymes", "enjamb", False, False),
    ("10", "reduplicated words", "redup", False, False),
    ("11", "end carpet density", "carpet", False, True),
    ("14", "number ladder", "numbers", False, False),
    ("23", "bars in 5-14 band", "band", False, False),
    ("32a", "stress clashes", "clash", True, False),
    ("32b", "mid-bar pauses", "pause", True, False),
    ("32c", "consonant pile-ups", "cluster", True, False),
]

MANUAL = ("1 chain length/coverage, 3 breath lines, 4 hinge, 6 escalation/bookend, 12 nonchalance, "
          "13 echo with a twist, 15 lexical sets, 16 domestic anchors, 17 menace, 18 self-mockery, "
          "19 roll-call hook, 20 voice tics, 21-22 delivery/beat, 24b AI-shape, 25 no copying, "
          "26-31 truth/lived detail, 33 register, 34 cringe, 36 poster test, 37 nonchalance, 38-41 Joe's ear")


def slot_par(slot):
    """The raw measured profile of one original slot (as block_stats dict), for per-bar comparison."""
    return score_quad(orig_blocks(ORIG)[slot])

def report_vs_slot(bars, slot):
    """Per-bar comparison of one block against ONE slot. The fair test: a 4-bar quad is not
    asked to match an 8-bar slot's raw counts. Prints the verdict and the criteria it loses on."""
    p = par([slot])
    s = score_quad(bars)
    s["cutup"] = s["mosaic"] + s["homophones"]
    s["band"] = sum(1 for x in s["syl"] if 5 <= x <= 14)
    o = per_bar(s, len(bars))
    q = per_bar(slot_par(slot), len(par_of_slot_syls(slot)))
    print(f"== vs {slot}: {len(bars)} bars vs {len(par_of_slot_syls(slot))}  "
          f"syl={s['syl']}  carpet={s['carpet']:.2f} ==\n")
    print(f"  {'crit':4s} {'criterion':30s} {'ours/bar':>9s} {'par/bar':>8s}  verdict")
    lost = []
    for ref, label, key, lower, isf in CRIT:
        if key in ("clash", "pause", "cluster"):
            ov, pv = o["flow"].get(key), q["flow"].get(key)
        else:
            ov, pv = o.get(key), q.get(key)
        if ov is None or pv is None:
            continue
        v = verdict(ov, pv, lower)
        print(f"  {ref:4s} {label:30s} {ov:>9.2f} {pv:>8.2f}  {v}")
        if v == "BELOW":
            lost.append(f"{ref} {label}")
    if s["hygiene"]:
        print(f"  {'24':4s} {'hygiene (banned/OOV)':30s} {'BAD':>9s} {'ok':>8s}  BELOW {','.join(s['hygiene'])}")
        lost.append("24 hygiene")
    m = rate_margin(bars, slot_par(slot))
    print(f"\n  margin {m:+d} -> {'BEATS' if m > 0 else ('MATCH' if m == 0 else 'loses')}      "
          f"losing: {', '.join(lost) or 'nothing'}\n")
    return m, lost


def par_of_slot_syls(slot):
    return orig_blocks(ORIG)[slot]


def report(bars, tag="quad"):
    p = par()
    s = score_quad(bars)
    s["cutup"] = s["mosaic"] + s["homophones"]
    s["band"] = sum(1 for x in s["syl"] if 5 <= x <= 14)
    parv = dict(p, cutup=2, band=len(bars), clash=p["clash"], pause=p["pause"], cluster=p["cluster"])
    print(f"== {tag}: {len(bars)} bars  syl={s['syl']}  carpet={s['carpet']:.2f} ==\n")
    print(f"  {'crit':4s} {'criterion':30s} {'ours':>6s} {'par':>6s}  verdict")
    below = []
    for ref, label, key, lower, isf in CRIT:
        ours = s["flow"][key] if key in ("clash", "pause", "cluster") else s[key]
        parv_ = parv[key]
        v = verdict(ours, parv_, lower)
        o = f"{ours:.2f}" if isf else str(ours)
        q = f"{parv_:.2f}" if isf else str(parv_)
        print(f"  {ref:4s} {label:30s} {o:>6s} {q:>6s}  {v}")
        if v == "BELOW":
            below.append(f"{ref} {label} ({ours} vs {parv_})")
    hy = s["hygiene"]
    print(f"  {'24':4s} {'hygiene (banned/OOV)':30s} {'ok' if not hy else 'BAD':>6s} {'ok':>6s}  "
          f"{'MATCH' if not hy else 'BELOW ' + ','.join(hy)}")
    if hy:
        below.append("24 hygiene: " + ",".join(hy))
    if any(not (5 <= x <= 14) for x in s["syl"]):
        below.append("23 out-of-band line length")
    print(f"\n  below par: {len(below)}" + ("" if not below else " -> " + "; ".join(below)))
    print(f"  MANUAL (not scored): {MANUAL}\n")
    return s, below


MANUAL_PER_QUAD = [
    ("12", "nonchalance: something big/illicit reported flat, no wink"),
    ("13", "echo with a twist: a word repeated with a changed sense, or an idiom made literal"),
    ("15", "lexical-set metaphor: one domain's words describing another"),
    ("16", "domestic anchors: tea/bins/rent/pint/mum/the lads ARE the voice"),
    ("17", "understated menace: euphemism or a flat swear, tone never changes"),
    ("18", "self-mockery (only if true, Joe confirms)"),
    ("20", "voice tics (mate/then/nah) at fixed rhythm positions"),
    ("23", "breath-control bursts: a 12-15 syllable bar packed in one breath"),
    ("24b", "no AI tell-shapes: no rule-of-three lists, no abstract nouns, no explained joke"),
    ("26", "true or flagged: every fact from material/ or tagged (invented)/(persona)"),
    ("28", "layers that reward a rewind: at least one line with two readings"),
    ("30", "accuracy: every local/foreign word correct and confirmed"),
    ("31", "lived detail: something only Joe's trips could produce"),
    ("33", "register: full spoken clauses, first person, a bloke talking"),
    ("34", "cringe filter: would a mate wince? (any yes = cut)"),
    ("36", "poster test: would this look good in a music video / on a film poster?"),
    ("37", "nonchalance first: never shouts the boast, mentions it"),
    ("38", "clever wordplay carried by rhyme and flow, payoff word in the rhyme slot"),
    ("39", "no gag structure (no setup-then-punchline)"),
    ("40", "character carried by words alone (audio only)"),
    ("41", "the rhyme scheme and flow are enjoyable to speak at tempo"),
]
SONG_LEVEL = [("1", "chain length/coverage"), ("3", "breath lines"), ("4", "hinge line"),
              ("6", "escalation arc + bookend"), ("19", "roll-call hook with a local word per place"),
              ("21", "two voices"), ("22", "hook riff and beat"), ("25", "no copying"),
              ("27", "signature set-piece (double-time run)"), ("29", "handoff device")]


def literary(bars):
    """literary/human signals + a scoring sheet. PROXIES are signals, NOT scores: only Joe can score these."""
    cats = rt.theme_words()
    words = set(w for b in bars for w in re.findall(r"[A-Za-z']+", b.lower()))
    hit = {c: sorted(words & {x.lower() for x in ws}) for c, ws in cats.items()}
    hit = {c: v for c, v in hit.items() if v}
    clause = sum(1 for b in bars if re.search(r"\b(i|we|he|she|they|you|my|me)\b", b.lower()))
    echoes = sorted({w for b in bars for w in re.findall(r"[A-Za-z']+", b.lower())
                     if len(w) > 3 and w not in rt.FUNC
                     and sum(1 for b2 in bars if re.search(rf"\b{w}\b", b2.lower())) > 1})
    print("  LITERARY PROXIES (signals, not scores):")
    print(f"    full-clause bars (has a subject): {clause}/{len(bars)}")
    print(f"    theme sets touched: {len(hit)} -> " + "; ".join(f"{c}:{','.join(v[:4])}" for c, v in hit.items()))
    print(f"    repeated words (echo?): {', '.join(echoes[:8]) or '-'}")
    print("  HUMAN SCORECARD (0-3 each; Joe/critic decides - the tool cannot):")
    for ref, q in MANUAL_PER_QUAD:
        print(f"    [{ref}] {q}")
    print("  SONG-LEVEL (not judged per quad): " + ", ".join(r for r, _ in SONG_LEVEL))


def orig_blocks(path):
    import check_all
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()][:76]
    out, i = {}, 0
    for slot, size in check_all.SIZES.items():
        out[slot] = lines[i:i + size]
        i += size
    return out


def compare_to_blocks(bars, blocks):
    """print, per original block, which of the 13 criteria our quad beats/matches/loses."""
    p = par()
    s = score_quad(bars)
    s["cutup"] = s["mosaic"] + s["homophones"]
    s["band"] = sum(1 for x in s["syl"] if 5 <= x <= 14)
    ours = {k: (s["flow"][k] if k in ("clash", "pause", "cluster") else s[k]) for _, _, k, _, _ in CRIT}
    print(f"  ours: syl={s['syl']}")
    wins = []
    for slot, blk in blocks.items():
        o = score_quad(blk)
        o["cutup"] = o["mosaic"] + o["homophones"]
        o["band"] = sum(1 for x in o["syl"] if 5 <= x <= 14)
        w = l = 0
        for ref, label, k, lower, _ in CRIT:
            ov = o["flow"][k] if k in ("clash", "pause", "cluster") else o[k]
            mv = ours[k]
            if lower:
                w += mv < ov; l += mv > ov
            else:
                w += mv > ov; l += mv < ov
        verdict = "BEATS" if (w > l and not s["hygiene"]) else ("MATCH" if w == l else "loses")
        wins.append((slot, w, l, verdict))
    for slot, w, l, v in wins:
        print(f"    vs {slot:10s}: beats on {w:2d} / loses on {l:2d}  -> {v}")
    return wins


def main():
    args = sys.argv[1:]
    if args and args[0] == "--slot":
        slot = args[1]
        path = args[2]
        src = sys.stdin.read().splitlines() if path == "-" else open(path, encoding="utf-8").read().splitlines()
        bars = [l.strip() for l in src if l.strip() and not l.strip().startswith(("#", "[", "("))]
        report_vs_slot(bars[:len(par_of_slot_syls(slot))], slot)
        return
    if args and args[0] == "--blocks":
        blocks = orig_blocks(args[1])
        p = par()
        print(f"== original blocks ({len(blocks)}) ==")
        for slot, blk in blocks.items():
            o = score_quad(blk)
            print(f"  {slot:10s} syl={o['syl']} soft={o['soft']} internal={o['internal']} multi={o['multisyl']} "
                  f"cutup={o['mosaic'] + o['homophones']} enj={o['enjamb']} redup={o['redup']} "
                  f"carpet={o['carpet']:.2f} flow={o['flow']}")
        return
    if args and args[0] == "--vs":
        orig = orig_blocks(args[1])
        src = sys.stdin.read().splitlines() if args[2] == "-" else open(args[2], encoding="utf-8").read().splitlines()
        cur, quads = [], []
        for line in src:
            s = line.strip()
            if not s or s.startswith(("#", "-", "[", "(")):
                if cur:
                    quads.append(cur)
                    cur = []
                continue
            cur.append(s)
        if cur:
            quads.append(cur)
        for i, q in enumerate(quads, 1):
            print(f"== quad {i}: {q[0][:44]} ==")
            compare_to_blocks(q[:4], orig)
            literary(q[:4])
        return
    # default: read quads, report mechanical + literary
    files = [a for a in args if not a.startswith("--")]
    path = files[0] if files else "-"
    src = sys.stdin.read().splitlines() if path == "-" else open(path, encoding="utf-8").read().splitlines()
    quads, cur = [], []
    for line in src:
        s = line.strip()
        if not s or s.startswith(("#", "-", "[", "(")):
            if cur:
                quads.append(cur)
                cur = []
            continue
        cur.append(s)
    if cur:
        quads.append(cur)
    for i, q in enumerate(quads, 1):
        report(q[:4], tag=f"quad {i}")
        if "--literary" in args:
            literary(q[:4])


if __name__ == "__main__":
    main()
