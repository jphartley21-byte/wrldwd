"""ukrap: the UK rap word supply, searchable by rhyme (16 Oct 2026, Joe: "Is the writers vocabulary limited that is making it harder
to find words that fit the rhyme scheme and flow that UK rappers would typically use or have access to?", then "build it").

Measured before this existed: of 117 UK rap / road / everyday British words, 30 had no pronunciation (invisible to every rhyme,
syllable and flow check) and 21 more were dropped by the US-weighted word-frequency filter the rhyme searches used, so the writer
drew on standard (mostly American-weighted) English. This tool searches a pool that ALWAYS includes toolkit/uk_rap_lexicon.txt
(exempt from the frequency filter, shown with its UK sense) and the repo's other UK supplies (rhyme_tools.OVR, bank.UK_EVERYDAY,
local_words.txt), plus common dictionary words, and scores every candidate with rapfit's own chain - the unit check_block, the depth
par and the multi-word gate use - so a word it lists rhymes the way the gates will hear it.

  python toolkit/ukrap.py lookup WORD                  pronunciation, syllables, shape, UK sense
  python toolkit/ukrap.py rhymes TAIL [TAIL ...]       words rhyming >= --depth deep with any of the given bar endings
         [--depth 2] [--shape Sw] [--register money] [--pronoun] [--uk-only] [--limit 40]
         --pronoun also tries every candidate + me / ya / it / 'em / him (two-word rhymes, as the multi-word gate counts them)
  python toolkit/ukrap.py list [--register drill]
  python toolkit/ukrap.py --selftest
"""
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import rhyme_tools as rt     # noqa: E402

MIN_ZIPF = 2.5               # common dictionary words only; every UK supply word is exempt
PRONOUNS = ["me", "ya", "it", "'em", "him"]
PRONOUN_HEADS = set("i me you ya he she it we they them him her us his hers its our their hes shes theyre youre weve ive im id ill lets thats whats".split())


def _zipf(w):
    try:
        from wordfreq import zipf_frequency
        return zipf_frequency(w, "en")
    except Exception:          # noqa: BLE001
        return 0.0


def _local_words():
    p = os.path.join(HERE, "local_words.txt")
    out = set()
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            if "|" in ln and not ln.startswith("#"):
                w = ln.split("|")[0].strip().lower()
                if w.isalpha():
                    out.add(w)
    return out


def sources(w):
    """where a word comes from: the UK lexicon (with register), OVR, UK_EVERYDAY, local words, or the dictionary."""
    tags = []
    if w in rt.UKLEX:
        tags.append("uk:" + rt.UKLEX[w]["register"])
    if w in rt.OVR and w not in rt.UKLEX:
        tags.append("ovr")
    try:
        import bank
        if w in bank.UK_EVERYDAY and w not in rt.UKLEX:
            tags.append("uk:everyday")
    except Exception:          # noqa: BLE001
        pass
    if w in _local_words():
        tags.append("local")
    return tags or ["dict"]


def uk_pool():
    pool = set(rt.UKLEX) | {w for w in rt.OVR if re.fullmatch(r"[a-z']+", w)} | _local_words()
    try:
        import bank
        pool |= set(bank.UK_EVERYDAY)
    except Exception:          # noqa: BLE001
        pass
    return {w for w in pool if rt.pron(w)}


def _stressed_vowel(phones):
    """the ARPAbet vowel of the last primary stress (else the last secondary)."""
    vs = [(i, p) for i, p in enumerate(phones) if p[-1] in "012"]
    for lvl in "12":
        hit = [p for i, p in vs if p[-1] == lvl]
        if hit:
            return hit[-1][:-1]
    return vs[-1][1][:-1] if vs else None


def shape(text):
    """the end shape the flow gates read: from the rhyme's stressed syllable to the end, S/w (flow_fit.sylls), prefixed '|'."""
    import flow_fit as ff
    ws = text.split()
    pat = "".join("w" if x else "S" for x in ff.sylls(text))
    phones = []
    for w in ws:
        phones += rt.pron(w) or []
    vs = [p for p in phones if p[-1] in "012"]
    if not vs or len(vs) != len(pat):
        return "|" + pat
    idx = max((i for i, p in enumerate(vs) if p[-1] == "1"), default=None)
    if idx is None:
        idx = max((i for i, p in enumerate(vs) if p[-1] == "2"), default=len(vs) - 1)
    return "|" + pat[idx:]


def _tail_syl(text):
    from ww.write import rapfit, rhymeview
    return rapfit._syl(rhymeview.tail_text(text.split()))


def rhymes(tails, depth=2, want_shape=None, register=None, pronoun=False, uk_only=False, limit=40):
    """[{'text','depth','shape','tags','zipf','cheap'}] rhyming >= depth with ANY of `tails`, UK words first."""
    from ww.write import rapfit
    targets = [(t, _tail_syl(t)) for t in tails]
    want_v = set()
    for t, _ in targets:
        ph = []
        for w in t.split():
            ph += rt.pron(w) or []
        v = _stressed_vowel(ph)
        if v:
            want_v.add(v)
    uk = uk_pool()
    try:
        import bank
        ukwords = set(rt.UKLEX) | set(bank.UK_EVERYDAY)
    except Exception:          # noqa: BLE001
        ukwords = set(rt.UKLEX)
    pool = set(uk)
    if not uk_only:
        pool |= {w for w in rt.D if w.isalpha() and len(w) > 1 and _zipf(w) >= MIN_ZIPF}
    if register:
        pool = {w for w in pool if w in rt.UKLEX and rt.UKLEX[w]["register"] == register}
    cands = []
    for w in pool:
        ph = rt.pron(w)
        if not ph:
            continue
        if want_v and _stressed_vowel(ph) not in want_v:
            continue
        cands.append(w)
        # a two-word rhyme needs a real head word: no function words, pronouns, contractions or fragments
        # heads come from the UK lexicon / everyday list or common dictionary words, never OVR-only entries (place and brand names)
        if pronoun and w.isalpha() and len(w) >= 3 and w not in rt.FUNC and w not in PRONOUN_HEADS and (
                w in ukwords or (w in rt.D and _zipf(w) >= 3.0)):
            cands += [f"{w} {p}" for p in PRONOUNS]
    out, own = [], {t.lower() for t, _ in targets}
    for c in cands:
        if c.lower() in own:
            continue
        try:
            sy = _tail_syl(c)
        except Exception:      # noqa: BLE001
            continue
        if not sy:
            continue
        d = max(rapfit.chain_best(sy, s)["depth"] for _, s in targets if s)
        if d < depth:
            continue
        if " " in c and d <= len(_tail_syl(c.split()[-1]) or []):
            continue                                   # a two-word candidate must rhyme past its last word
        sh = shape(c)
        if want_shape and sh != "|" + want_shape.lstrip("|"):
            continue
        head = c.split()[0]
        out.append({"text": c, "depth": d, "shape": sh, "tags": sources(head), "zipf": round(_zipf(head), 1),
                    "cheap": rapfit.cheap(c), "sense": rt.UKLEX.get(head, {}).get("sense", "")})
    rank = lambda r: 0 if any(t.startswith("uk:") for t in r["tags"]) else 1 if r["tags"] == ["dict"] else 2   # noqa: E731
    out.sort(key=lambda r: (-r["depth"], rank(r), -r["zipf"], r["text"]))
    return out[:limit]


def lookup(word):
    w = word.lower()
    ph = rt.pron(w)
    return {"word": w, "pron": " ".join(ph) if ph else None, "syllables": rt.nsyl(ph) if ph else None,
            "shape": shape(w) if ph else None, "tags": sources(w), "zipf": round(_zipf(w), 1),
            "sense": rt.UKLEX.get(w, {}).get("sense", ""), "register": rt.UKLEX.get(w, {}).get("register", "")}


def selftest(orig_path=None):
    ok = True
    miss = [w for w in rt.UKLEX if not rt.pron(w)]
    good = not miss
    ok &= good
    print(("ok  " if good else "BAD ") + f"every lexicon word is pronounceable ({len(rt.UKLEX)} entries){'' if good else ': ' + str(miss)}")
    if orig_path is None:
        cand = glob.glob(os.path.expanduser("~/Documents/*/original_lines.txt"))
        orig_path = cand[0] if cand else None
    if orig_path:
        toks = {re.sub(r"[^a-z']", "", t.lower()) for ln in open(orig_path, encoding="utf8") for t in ln.split()}
        hit = toks & rt.UKLEX_FILLED
        good = not hit
        ok &= good
        print(("ok  " if good else "BAD ") + f"the lexicon fills no word of the original, so the original is measured as before "
              f"({len(hit)} filled)")
    r = [x["text"] for x in rhymes(["arms"], depth=1, uk_only=True, limit=200)]
    good = "garms" in r and _zipf("garms") < MIN_ZIPF
    ok &= good
    print(("ok  " if good else "BAD ") + "a UK word the frequency filter would drop (garms) is found as a rhyme for 'arms'")
    r = rhymes(["dead cheeky"], depth=2, pronoun=True, uk_only=True, limit=400)
    two = [x["text"] for x in r if " " in x["text"]]
    good = bool(two)
    ok &= good
    print(("ok  " if good else "BAD ") + f"two-word rhymes are offered for 'cheeky' ({len(two)}, e.g. {two[:3]})")
    lk = lookup("mandem")
    good = lk["pron"] and lk["syllables"] == 2 and lk["register"] == "road"
    ok &= good
    print(("ok  " if good else "BAD ") + f"lookup reads a road word: mandem = {lk['pron']}, {lk['syllables']} syllables, '{lk['sense']}'")
    print("ukrap selftest:", "PASSED" if ok else "FAILED")
    return ok


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:          # noqa: BLE001
        pass
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return 0 if selftest(sys.argv[2] if len(sys.argv) > 2 else None) else 1
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("lookup")
    a.add_argument("word")
    b = sub.add_parser("rhymes")
    b.add_argument("tails", nargs="+")
    b.add_argument("--depth", type=int, default=2)
    b.add_argument("--shape")
    b.add_argument("--register")
    b.add_argument("--pronoun", action="store_true")
    b.add_argument("--uk-only", action="store_true")
    b.add_argument("--limit", type=int, default=40)
    c = sub.add_parser("list")
    c.add_argument("--register")
    args = ap.parse_args()
    if args.cmd == "lookup":
        print(lookup(args.word))
    elif args.cmd == "rhymes":
        for r in rhymes(args.tails, args.depth, args.shape, args.register, args.pronoun, args.uk_only, args.limit):
            print(f"  {r['depth']}  {r['text']:<22} {r['shape']:<6} {','.join(r['tags']):<16} zipf {r['zipf']:<4}"
                  f"{' CHEAP' if r['cheap'] else ''}  {r['sense']}")
    elif args.cmd == "list":
        for w, e in sorted(rt.UKLEX.items()):
            if not args.register or e["register"] == args.register:
                print(f"  {w:<14} {e['register']:<9} {e['sense']}")
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
