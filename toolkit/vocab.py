"""vocab: a persistent, G2-filtered vocabulary ledger.

Why this exists. toolkit/research.py can look words up (Datamuse, Wiktionary) but nothing recorded
what it found, so every session re-asked the same questions and learned nothing. This module makes
research COMPOUND: each word is stored once with everything a bar needs about it, and every later
lookup reads the ledger first.

The G2 verdict is the point. Gate G2 is recognisability - the gate Joe rejected bars on ("Burton
obscure", "good grouse lame", "Ahoj ... unknown to a British ear"). A wider vocabulary is NOT the
goal here; a wider vocabulary that a 30-something British mate already knows is. So every entry
carries a wordfreq Zipf score and a PASS / G2 RISK verdict, using the same threshold as
`helpers.py freq` (Zipf < 3.0 = rare).

What is stored per word (one JSON object per line, upserted by word):
  word, uk_pron (Britfone IPA), syllables, pattern (w/S from flow_fit), end tail (last two BRITISH
  vowels), family key (rhyme_tools key on the 2-syllable tail), in_original, zipf, g2, banned, oov,
  first_seen, seen, sources[].

  python toolkit/vocab.py info WORD [WORD ...]     one entry per word, computed fresh
  python toolkit/vocab.py g2 [WORD ...] | -        the G2 verdict for end words (reads stdin with -)
  python toolkit/vocab.py show [--rare] [--family KEY] [--limit N]
  python toolkit/vocab.py selftest                 must pass; asserted by toolkit/calibrate.py

Library use: toolkit/research.py records every word it looks up (and every candidate that already
passes G2) with `record_many`, and reads `cached_online` before paying for a network call again.

NETWORK BOUNDARY: this module never sends anything anywhere. Only toolkit/research.py does, and only
a headword of <= 3 words (see research.py `_outbound_ok`), never a lyric line or a material/ excerpt.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import helpers as h              # noqa: E402
import craft_scan as cs          # noqa: E402
import rhyme_tools as rt         # noqa: E402
import flow_fit as ff            # noqa: E402

LEDGER = os.path.join(HERE, "vocab_ledger.jsonl")
RARE_ZIPF = 3.0                  # same threshold as helpers.py freq (gate G2)


def zipf(word):
    """Commonness of a word OR phrase: the MINIMUM Zipf of its tokens, because a phrase is only as
    recognisable as its least common part. A single-letter token scores 0 (a letter is not
    vocabulary), which is what stops Datamuse's spelling junk ("j go", "dey go") being banked.

    Caveat that matters here: wordfreq's English list is US-weighted, so British slang reads as rare
    ("skint" scores 2.93 -> G2 RISK even though a mate would get it instantly). The ledger's verdict
    is a PROXY; on British slang it defers to Joe's ear (gate G2 is human).
    """
    toks = re.findall(r"[a-z']+", word.lower())
    if not toks or any(len(t) < 2 for t in toks):
        return 0.0
    try:
        from wordfreq import zipf_frequency
        return round(min(float(zipf_frequency(t, "en")) for t in toks), 2)
    except Exception:                                     # noqa: BLE001
        return None


def g2(word):
    """The recognisability verdict: a mate gets it, or it is a G2 risk."""
    z = zipf(word)
    if z is None:
        return "UNKNOWN", None
    return ("PASS" if z >= RARE_ZIPF else "G2 RISK"), z


_ORIG = None


def orig_words():
    """Words in the original's own lines (read-only, kept OUTSIDE the project - CLAUDE.md rule 4).
    Used only to answer 'is this word already used there'; no lyric text is stored or printed."""
    global _ORIG
    if _ORIG is None:
        _ORIG = set()
        p = os.path.join(os.path.expanduser("~"), "Documents", "Worldwide_private",
                         "original_lines.txt")
        if os.path.exists(p):
            for line in io.open(p, encoding="utf8"):
                _ORIG.update(w.lower().strip(",.?!") for w in line.split())
    return _ORIG


def end_tail(word):
    """Last two BRITISH vowels of the word - the end sound a bar would rhyme on."""
    ph = h.uk(word)
    if ph:
        vs = h.vowels_of(ph)
        if len(vs) >= 2:
            return "-".join(vs[-2:])
        if vs:
            return vs[-1]
    us = rt.pron(word)
    if us:
        vs = [rt.strip(p) for p in us if rt.is_v(p)]
        if vs:
            return "-".join(vs[-2:])
    return None


def family(word):
    ph = rt.pron(word)
    if not ph:
        return None
    try:
        return rt.key(ph, n=2, mode="perfect", stress=False)
    except Exception:                                     # noqa: BLE001
        return None


def info(word):
    """Everything the ledger knows about a word, computed fresh.

    `junk` marks a candidate with no commonness and no British dictionary entry (Datamuse returns
    nonce spellings like "boslego"); `g2` is the recognisability PROXY. Neither is a gate: cmudict
    contains surnames, wordfreq is US-weighted, so G2 is a prompt for Joe's ear, never a veto."""
    w = word.strip().lower()
    verdict, z = g2(w)
    in_brit = h.uk(w) is not None
    ph = rt.pron(w)
    return {
        "word": w,
        "uk_pron": " ".join(h.uk(w) or []) or None,
        "syllables": len(ff.sylls(w)) if (ph or in_brit) else None,
        "pattern": "".join("w" if x else "S" for x in ff.sylls(w)),
        "end_tail": end_tail(w),
        "family": family(w),
        "in_original": w in orig_words(),
        "zipf": z,
        "g2": verdict,
        "banned": w in rt.BANNED,
        "oov": ph is None,
        "junk": bool(z == 0.0 and not in_brit),
    }


def _load():
    if not os.path.exists(LEDGER):
        return {}
    out = {}
    with io.open(LEDGER, encoding="utf8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[rec["word"]] = rec
    return out


def record(word, source="research", extra=None, facts=None, drop_junk=False):
    """Upsert a single word. Equivalent to record_many. Defaults to KEEPING even a junk-flagged word,
    because an explicit lookup ("what is wazzock?") should always be remembered."""
    return record_many([word], source=source, extra=extra, facts=facts,
                       drop_junk=drop_junk) and lookup(word)


def record_many(words, source="research", extra=None, facts=None, min_zipf=None,
                drop_junk=True):
    """Upsert many words in ONE read/write. By default structural junk (no commonness and no British
    dictionary entry) is dropped; `min_zipf` is available for a stricter bank, but it is off by
    default because it would throw away real British words that wordfreq scores low (skint,
    winnebago). Returns the number written."""
    from datetime import date
    db = _load()
    n = 0
    for word in words:
        w = str(word).strip().lower()
        if not w or len(w.split()) > 3 or "\n" in w or len(w) > 30:
            continue
        r = (info(w) if facts is None else facts)
        if drop_junk and r.get("junk"):
            continue
        if min_zipf is not None and (r.get("zipf") is None or r["zipf"] < min_zipf):
            continue
        rec = db.get(w) or {"word": w, "first_seen": date.today().isoformat(), "seen": 0,
                            "sources": []}
        rec.update(r)
        rec["seen"] = int(rec.get("seen", 0)) + 1
        if source not in rec["sources"]:
            rec["sources"].append(source)
        if extra:
            for k, v in extra.items():
                if v not in (None, [], {}):
                    rec[k] = v
        db[w] = rec
        n += 1
    if n:
        _write(db)
    return n


def _write(db):
    tmp = LEDGER + ".tmp"
    with io.open(tmp, "w", encoding="utf8") as fh:
        for w in sorted(db):
            fh.write(json.dumps(db[w], ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, LEDGER)


def lookup(word):
    return _load().get(word.strip().lower())


def cached_online(word, mode):
    rec = lookup(word) or {}
    return (rec.get("online") or {}).get(mode)


def cache_online(word, mode, results):
    """Store an online result list so the same query is never paid for twice."""
    w = word.strip().lower()
    db = _load()
    rec = db.get(w) or {"word": w, "seen": 0, "sources": []}
    rec.setdefault("online", {})[mode] = list(results)[:25]
    db[w] = rec
    _write(db)


# --- CLI ------------------------------------------------------------------------------------
def cmd_info(words):
    for w in words:
        r = info(w)
        flag = "" if r["g2"] == "PASS" else "  <-- G2 RISK"
        print(f"{r['word']:<16} zipf {r['zipf']}  {r['g2']}{flag}")
        print(f"   uk {r['uk_pron'] or '?'} | {r['syllables']} syl {r['pattern']} | "
              f"tail {r['end_tail']} | family {r['family'] or '?'}")
        print(f"   banned {r['banned']} | oov {r['oov']} | in the original's lines "
              f"{r['in_original']}")


def cmd_g2(items):
    bad = 0
    for w in items:
        v, z = g2(w)
        if v != "PASS":
            bad += 1
        print(f"{w:<16} zipf {z}  {v}")
    print(f"\n{len(items) - bad}/{len(items)} pass G2")
    return bad == 0


def cmd_show(a):
    db = _load()
    rows = list(db.values())
    if "--rare" in a:
        rows = [r for r in rows if r.get("g2") == "G2 RISK" and not r.get("junk")]
    if "--family" in a:
        k = a[a.index("--family") + 1]
        rows = [r for r in rows if r.get("family") == k]
    if "--all" not in a:
        rows = [r for r in rows if not r.get("junk")]
    n = int(a[a.index("--limit") + 1]) if "--limit" in a else 40
    print(f"ledger {os.path.relpath(LEDGER, os.path.dirname(HERE))}: "
          f"{len(db)} words, showing {min(n, len(rows))}"
          f"{'' if '--all' in a else ' (junk hidden; --all to see it)'}")
    for r in sorted(rows, key=lambda r: (r.get("g2") != "G2 RISK", r["word"]))[:n]:
        print(f"  {r['word']:<18} {r.get('g2', '?'):<8} tail {str(r.get('end_tail')):<10} "
              f"syl {r.get('syllables')}  seen {r.get('seen')}")


def selftest():
    """Hermetic: points the ledger at a temp file so a calibrate run never pollutes the real one."""
    global LEDGER
    import tempfile
    real = LEDGER
    LEDGER = os.path.join(tempfile.gettempdir(), "wrldwd_vocab_selftest.jsonl")
    try:
        ok = True
        rare = "wazzock"          # a real British dialect word a mate may not know
        v_rare, z_rare = g2(rare)
        v_com, z_com = g2("border")
        good = v_com == "PASS" and (z_rare is None or v_rare == "G2 RISK")
        ok &= good
        print(("ok  " if good else "BAD ") +
              f"G2 separates common from obscure: border={z_com}/{v_com}, {rare}={z_rare}/{v_rare}")
        tail = end_tail("border")
        good = bool(tail) and tail.startswith("ɔ")
        ok &= good
        print(("ok  " if good else "BAD ") + f"end tail of 'border' is {tail} (british)")
        record(rare, source="selftest")
        record(rare, source="selftest")
        db = _load()
        good = db.get(rare, {}).get("seen", 0) >= 2 and len(db) == 1
        ok &= good
        print(("ok  " if good else "BAD ") +
              f"an explicit lookup is kept and upserts by word ({rare} seen "
              f"{db.get(rare, {}).get('seen')})")
        # structural junk must not be banked, but a real British word wordfreq under-scores must be
        record_many(["border", "boslego", "skint"], source="selftest")
        db = _load()
        good = ("border" in db and "skint" in db and "boslego" not in db)
        ok &= good
        print(("ok  " if good else "BAD ") +
              "junk is dropped but under-scored British words are kept (border+skint in, boslego out)")
        print("VOCAB SELFTEST", "PASSED" if ok else "FAILED")
        return ok
    finally:
        try:
            os.remove(LEDGER)
        except OSError:
            pass
        LEDGER = real


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    if a[0] == "info":
        cmd_info(a[1:])
    elif a[0] == "g2":
        items = [l.strip() for l in sys.stdin.read().splitlines() if l.strip()] if "-" in a else a[1:]
        sys.exit(0 if cmd_g2(items) else 1)
    elif a[0] == "show":
        cmd_show(a)
    elif a[0] in ("selftest", "--selftest"):
        sys.exit(0 if selftest() else 1)
    else:
        print(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
