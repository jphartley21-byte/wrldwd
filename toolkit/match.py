"""match: hard, measurable bar-by-bar comparison of OUR bars against the ORIGINAL slot bars.
Usage: python toolkit/match.py --slot "V1 1-8" -   (stdin: OUR bars only; compares with benchmark/original_profile.json, numbers only)
   or: printf "orig1\\norig2\\n...\\n---\\nours1\\nours2\\n..." | python toolkit/match.py -
The original is piped in, never saved. Output: per-bar PASS/FAIL with reasons, stanza checks, and an overall verdict.
A section is "form-matched" only when every line says PASS. Sense and voice (gates G1-G6) are still judged separately.
"""
import io, contextlib, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rhyme_tools import pron_phrase, uk, vidx, strip, quad_stats  # noqa: E402
from flow_check import bar_profile  # noqa: E402

WEAK = {"AH", "IH", "ER", "IY", "UH"}
TAILWORDS = {"ya", "this", "it", "him", "in", "em", "them", "her", "me", "us", "on", "up"}


CMU2IPA = {"AE": "æ", "AO": "ɔː", "AW": "aʊ", "AY": "aɪ", "EH": "e", "EY": "eɪ", "IH": "ɪ", "OW": "əʊ", "OY": "ɔɪ", "UH": "ʊ", "UW": "uː"}
UKWEAK = {"ə", "ɪ"}  # only schwa and short i are interchangeable; happy-i (lovely) is NOT weak


def uk_vowels(word):
    """British vowels of a word as [(vowel, primary_stress)], from Britfone; CMU fallback mapped to British."""
    from helpers import uk as bf
    w = word.lower().strip("'")
    p = bf(w)
    extra = []
    if not p:  # inflections: parcelled -> parcel + led, collared -> collar + ed
        for suf, add in (("led", "ə"), ("ed", None), ("d", None), ("ing", "ɪ"), ("es", None), ("s", None)):
            if w.endswith(suf) and bf(w[: -len(suf)]):
                p = bf(w[: -len(suf)]); extra = [(add, False)] if add and suf == "ing" else []
                break
            if suf == "led" and w.endswith("led") and bf(w[:-2]):
                p = bf(w[:-2]); break
    if p:
        out = []
        for t in p:
            v = t.replace("ˈ", "").replace("ˌ", "").replace("ɐ", "ʌ").replace("ɛ", "e")
            if any(c in "iɪeɛæʌɒʊəuɑɔɜaɐ" for c in v):
                out.append((v, t.startswith("ˈ")))
        if out:
            return out + extra
    from rhyme_tools import pron, is_v
    q = pron(w)
    if not q:
        return None
    out = []
    for x in q:
        if not is_v(x):
            continue
        base, st = strip(x), x[-1] == "1"
        if base == "AA":
            first = next((c for c in w if c in "aeiou"), "o")
            v = "ɑː" if first == "a" else "ɒ"
        elif base == "AH":
            v = "ʌ" if st else "ə"
        elif base == "ER":
            v = "ɜː" if st else "ə"
        elif base == "IY":
            v = "iː" if st else "i"
        else:
            v = CMU2IPA.get(base, base)
        out.append((v, st))
    return out


def end_key(line):
    """multisyllabic rhyme tail in BRITISH vowels: from the last primary-stressed syllable of the line's last
    content word to the end (tail words it/him/in count as weak). Returns (vowels, n_syllables)."""
    ws = [w.strip(".,?!") for w in line.replace("å", "a").replace("-", " ").split()]
    tail_weak = []
    while len(ws) > 1 and ws[-1].lower().strip("'") in TAILWORDS:
        tail_weak.append("ɪ"); ws = ws[:-1]
    vs, stress = [], []
    for w in reversed(ws):
        wv = uk_vowels(w)
        if not wv:
            if vs:
                break
            return None
        vs = [v for v, _ in wv] + vs
        stress = [st for _, st in wv] + stress
        if any(st for _, st in wv) or len(wv) > 1:
            break
    if not vs:
        return None
    k = max(i for i, st in enumerate(stress) if st) if any(stress) else len(vs) - 1
    tail = vs[k:] + tail_weak
    return (tail, len(tail))


def rhymes(a, b):
    """same stressed vowel; unstressed syllables weak-or-equal; lengths within 1"""
    if a is None or b is None:
        return False
    (ta, na), (tb, nb) = a, b
    if ta[0] != tb[0] or abs(na - nb) > 1:
        return False
    return all(x == y or (x in UKWEAK and y in UKWEAK) for x, y in zip(ta[1:], tb[1:]))


def _k(k):
    return (list(k[0]), k[1]) if k else None


def depth(a, b):
    if not rhymes(a, b):
        return 0
    return min(a[1], b[1])


def head_key(line):
    """the opening rhyme in British vowels: from the first primary-stressed content syllable in the first words, two syllables"""
    from rhyme_tools import FUNC
    vs, st = [], []
    for w in [w.strip(".,?!") for w in line.replace("å", "a").replace("-", " ").split()][:4]:
        wv = uk_vowels(w)
        if not wv:
            n = max(1, len(re.findall(r"[aeiouy]+", w.lower().rstrip("e"))))
            vs += ["?"] * n; st += [False] * n; continue
        vs += [v for v, _ in wv]
        st += [x and w.lower() not in FUNC for _, x in wv]
    if True not in st:
        return None
    k = st.index(True)
    t = vs[k:k + 2]
    return (t, len(t)) if len(t) == 2 and "?" not in t else None


def bookends(lines):
    """bars whose opening rhyme matches an end tail somewhere in the stanza (2+ syllables)"""
    ends = [end_key(l) for l in lines]
    out = []
    for i, l in enumerate(lines):
        h = head_key(l)
        out.append(bool(h) and any(e and len(e[0]) >= 2 and e[0][0] == h[0][0] and (h[0][1] == e[0][1] or (h[0][1] in UKWEAK and e[0][1] in UKWEAK)) for e in ends))
    return out


def spans(line):
    """(head, end) syllable spans for graded rhyme: head = 3 syllables from the first stressed content syllable;
    end = from the last stressed syllable to the end of the bar"""
    import phon
    sy = phon.syllables(line)
    if not sy:
        return None, None
    st = [i for i, x in enumerate(sy) if x[1]]
    end = sy[st[-1]:] if st else sy[-2:]
    head = sy[st[0]:st[0] + 3] if st else None
    return head, end


def rhyme_map(lines, floor=0.8):
    """all rhyme links in a stanza with their graded strength: [(kind, i, j, score)]"""
    import phon
    sp = [spans(l) for l in lines]
    links = []
    for i in range(len(lines)):
        for j in range(len(lines)):
            for ka, kb, kind in ((1, 1, "end-end"), (0, 1, "open-end")):
                if kind == "end-end" and j <= i:
                    continue
                a, b = sp[i][ka], sp[j][kb]
                if a and b:
                    sc, _ = phon.score(a, b)
                    if sc >= floor:
                        links.append((kind, i, j, sc))
    return links


# Rhyme schemes of the ORIGINAL, annotated by ear in the main thread (letters only, no lyrics).
# Same letter = those bars rhyme (perfect, near or slant). Tool readings missed slant chains (lonesome/long one).
MANUAL_SCHEME = {"Hook 1-4": "AAAA", "Hook 5-8": "ABBA", "Hook 9-16": "AABACBDB", "V1 1-8": "AAAAAABA",
                 "V1 9-16": "AABAAAAA", "V1 17-24": "AAAABBBB", "V1 25-32": "AAABACCC", "V1 33-44": "AABBCCCCCCDC",
                 "V2 1-8": "AAAAAAAA", "V2 9-16": "AAAABBCB"}


def stressed_sylls(line):
    import phon
    return [i for i, x in enumerate(phon.syllables(line)) if x[1]], phon.syllables(line)


def best_end(a_line, b_line):
    """best graded rhyme between two bar endings over the last 1-3 syllables (a span must start on a stressed syllable
    unless it is the final syllable): handles 'plain clothes' ~ 'Tobago' and 'lonesome' ~ 'long one'"""
    import phon
    A, B = phon.syllables(a_line), phon.syllables(b_line)
    best = 0.0
    for k in (1, 2, 3):
        if len(A) < k or len(B) < k:
            continue
        a, b = A[-k:], B[-k:]
        if k > 1 and not (a[0][1] or b[0][1]):
            continue
        best = max(best, phon.score(a, b)[0])
    ea, eb = spans(a_line)[1], spans(b_line)[1]  # stressed-syllable-aligned tails: waiter ~ way, people ~ beat
    if ea and eb:
        best = max(best, phon.score(ea, eb)[0])
    return best


def internal_density(lines):
    """for each bar i: number of stressed-syllable vowel matches (>= 0.85) within bar i and between bar i and bar i+1,
    excluding the final syllables (end rhymes are scored separately)"""
    import phon
    out = []
    data = [stressed_sylls(l) for l in lines]
    for i in range(len(lines)):
        st, sy = data[i]
        mids = [sy[k][0] for k in st[:-1]]
        n = sum(1 for a in range(len(mids)) for b in range(a + 1, len(mids)) if phon.vsim(mids[a], mids[b]) >= 0.85)
        if i + 1 < len(lines):
            st2, sy2 = data[i + 1]
            nxt = [sy2[k][0] for k in st2[:-1]]
            n += sum(1 for a in mids for b in nxt if phon.vsim(a, b) >= 0.85)
        out.append(n)
    return out


def scheme(lines):
    keys = [end_key(l) for l in lines]
    letters, reps = [], []
    for k in keys:
        for i, r in enumerate(reps):
            if rhymes(k, r):
                letters.append("abcdefghij"[i]); break
        else:
            reps.append(k); letters.append("abcdefghij"[len(reps) - 1] if len(reps) <= 10 else "?")
    return "".join(letters), keys


def quiet_quad(lines):
    with contextlib.redirect_stdout(io.StringIO()):
        return quad_stats(lines)


PROFILE = os.path.join(HERE, "..", "benchmark", "original_profile.json")


def profile_of(lines):
    so, ko = scheme(lines)
    return {"bars": [bar_profile(l) for l in lines], "keys": ko, "scheme": so, "bookends": bookends(lines), "rhyme_map": rhyme_map(lines), "internal": internal_density(lines), "quad": {k: v for k, v in quiet_quad(lines).items() if k in ("multisyl", "internal_bars", "allit_bars")}}


def main():
    import json
    rows = [l.strip() for l in sys.stdin.read().splitlines() if l.strip() and not l.startswith(("[", "#", "("))]
    if "--build" in sys.argv:  # stdin: '== SLOT' headers + original lines; writes numbers only
        prof, cur = {}, None
        for r in rows:
            if r.startswith("== "):
                cur = r[3:]; prof[cur] = []
            else:
                prof[cur].append(r)
        json.dump({k: profile_of(v) for k, v in prof.items()}, open(PROFILE, "w"), indent=0)
        print("profile written:", ", ".join(prof)); return
    if "--slot" in sys.argv:
        P = json.load(open(PROFILE))[sys.argv[sys.argv.index("--slot") + 1]]
        D = rows
        po_bars, ko, so, qo = P["bars"], [tuple(k) if k else None for k in P["keys"]], P["scheme"], P["quad"]
    else:
        k = rows.index("---")
        O, D = rows[:k], rows[k + 1:]
        P = profile_of(O)
        po_bars, ko, so, qo = P["bars"], P["keys"], P["scheme"], P["quad"]
    O = po_bars
    if len(O) != len(D):
        print(f"FAIL: {len(D)} bars vs original {len(O)}"); return
    sd, kd = scheme(D)
    fails = 0
    for i, (po, d) in enumerate(zip(O, D)):
        pd = bar_profile(d)
        why = []
        if abs(po["syl"] - pd["syl"]) > 1:
            why.append(f"syllables {pd['syl']} vs {po['syl']}")
        if po["grid"] and pd["grid"]:
            eo, ed = po["syl"] - po["grid"][-1], pd["syl"] - pd["grid"][-1]
            if eo != ed:
                why.append(f"ending {'hard' if ed == 0 else 'soft+' + str(ed)} vs {'hard' if eo == 0 else 'soft+' + str(eo)}")
            hit = sum(1 for p in po["grid"] if any(abs(p - q) <= 1 for q in pd["grid"]))
            if hit / len(po["grid"]) < 0.75 or abs(len(po["grid"]) - len(pd["grid"])) > 1:
                why.append(f"stress grid {pd['grid']} vs {po['grid']}")
        if pd["pause"] > po["pause"]:
            why.append("extra mid-bar pause")
        for j in range(len(O)):
            if j != i and rhymes(_k(ko[i]), _k(ko[j])):
                if not rhymes(kd[i], kd[j]):
                    why.append(f"must rhyme with bar {j + 1} (original does; ours {'-'.join(kd[i][0]) if kd[i] else '?'} vs {'-'.join(kd[j][0]) if kd[j] else '?'})"); break
                if depth(kd[i], kd[j]) < min(depth(_k(ko[i]), _k(ko[j])), 3):
                    why.append(f"rhyme with bar {j + 1} only {depth(kd[i], kd[j])} syllables deep; original {depth(_k(ko[i]), _k(ko[j]))}"); break
        fails += bool(why)
        print(f"{i + 1:>2}. {'PASS' if not why else 'FAIL: ' + '; '.join(why)}   | {d}")
    qd = quiet_quad(D)
    slot = sys.argv[sys.argv.index("--slot") + 1] if "--slot" in sys.argv else None
    ms = MANUAL_SCHEME.get(slot)
    if ms and len(ms) == len(D):
        import phon
        sp = [spans(l) for l in D]
        miss = []
        for i in range(len(D)):
            for j in range(i + 1, len(D)):
                if ms[i] == ms[j]:
                    sc = best_end(D[i], D[j])
                    if sc < 0.78:
                        miss.append(f"{i + 1}-{j + 1} ({sc:.2f})")
        ok = not miss
        fails += not ok
        print(f"original rhyme scheme {ms} (by ear): {'PASS' if ok else 'FAIL, these bars must rhyme and do not: ' + ', '.join(miss)}")
    oi = P.get("internal")
    if oi:
        di = internal_density(D)
        short = [f"bar {i + 1}: {b} vs {a}" for i, (a, b) in enumerate(zip(oi, di)) if a >= 3 and b < 0.6 * a]
        tot_ok = sum(di) >= 0.8 * sum(oi)
        ok = tot_ok and not short
        fails += not ok
        print(f"internal rhyme density (stressed vowels within a bar and into the next): ours {sum(di)} vs original {sum(oi)} -> {'PASS' if ok else 'FAIL ' + '; '.join(short)}")
    rm = P.get("rhyme_map")
    if rm:
        import phon
        sp = [spans(l) for l in D]
        weak = []
        for kind, i, j, sc in rm:
            ka, kb = (1, 1) if kind == "end-end" else (0, 1)
            a, b = sp[i][ka] if i < len(sp) else None, sp[j][kb] if j < len(sp) else None
            ours = phon.score(a, b)[0] if a and b else 0.0
            if ours < min(sc, 0.9) - 0.08:
                weak.append(f"{kind} bar {i + 1}->{j + 1}: ours {ours:.2f} vs original {sc:.2f}")
        strong = [x for x in weak if "open-end" in x or float(x.split("original ")[1]) >= 0.85]
        ok = not strong and len(weak) <= len(rm) // 5
        fails += not ok
        print(f"rhyme strength map ({len(rm)} links in the original, incl. slant and opening-to-end): {'PASS' if ok else 'FAIL'}" + ("" if not weak else "; weaker: " + "; ".join(weak[:8])))
    bo, bd = P.get("bookends"), bookends(D)
    if bo:
        miss = [i + 1 for i, (a, b) in enumerate(zip(bo, bd)) if a and not b]
        need = sum(bo)
        ok = len(miss) <= need // 4
        fails += not ok
        print(f"bookend multis (bar opens on the stanza's end rhyme): original bars {[i + 1 for i, a in enumerate(bo) if a]}, ours {[i + 1 for i, b in enumerate(bd) if b]} -> {'PASS' if ok else 'FAIL, missing in bars ' + str(miss)}")
    print(f"scheme: ours {sd} vs original {so}")
    for key, slack in (("multisyl", 0.8), ("internal_bars", 0.8), ("allit_bars", 1.0)):
        a, b = qo.get(key, 0), qd.get(key, 0)
        ok = b >= a * slack if key != "allit_bars" else b >= a - 1
        fails += not ok
        print(f"{key}: ours {b} vs original {a} -> {'PASS' if ok else 'FAIL'}")
    print("VERDICT:", "FORM MATCHES THE ORIGINAL (advisory; judge sense and voice)" if not fails else f"{fails} bars differ from the original (advisory, not an error)")


if __name__ == "__main__":
    main()
