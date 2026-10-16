"""pointcheck: does each bar make a POINT a listener gets? (16 Oct 2026)

Joe, on seven v4 bars ("How did these pass the sense/quality gates?") and then "So how can we fix this so it doesn't flag false
positives in the original but catches true positives?".

WHY A NEW READ. ww/write/sensecheck.py asks "can a stranger restate this as a plain sentence?". That question fails 39 of the ORIGINAL's
76 bars (slang, loanwords, brands, violent euphemism, fragments, run-on halves) and passes ours whenever the words can be repeated back
("Yes, I have cash, and the judge gets lager"). So its hard rule had to be a per-section allowance, and bad bars hid inside it.

WHAT THIS READS. The whole section goes to the judge, run-on sentences joined (sensecheck.units). For each item it must explain the bar
to a mate in its OWN words: what the speaker claims or does and why it lands. Unknown words are never a fault (assume real slang);
fragments are never a fault. An item FAILS when (the rule chosen by `--validate`, see FAIL_ON):
  point     the judge cannot explain it without repeating its words or inventing facts ("NONE")
  hanging   it leaves something unresolved the listener needs (a comparison with nothing compared, an unexplained "my X")
  contra    it contradicts itself
  follows   it has no connection to the section (a non sequitur)
  lands     a mate would not get it on one hearing

VALIDATION (registry discipline: unvalidated until --validate meets the bar):
  must pass  the original's 76 bars (read privately: nothing of it is cached or written, only bar numbers)
  must fail  Joe's seven bars (toolkit/tests/sense_flagged.txt, read in their v4 sections; the prompt was written against them)
             and HELD_OUT: ten bars Joe or I rejected for saying nothing, read in the sections they came from (not used to write it)
  target     the original passes >= 90% and >= 85% of the bad bars are caught, held-out included.
  python -m ww.write.pointcheck --validate [--model haiku|sonnet] [--reads 2] [--prompt 1|2|3]
  python -m ww.write.pointcheck FILE      the report: bars scoring >= FLAG_AT, with what had to be worked out

RESULT (16 Oct 2026; benchmark/point_validation_<model>_p<prompt>.json). AUC of the 0-6 fault score, bad bars vs the original's:
  prompt 1 (charitable, "explain it to a mate")       0.59  it rescues every bar by inventing a meaning (a gnome as a stash)
  prompt 2 (worked out? natural? lands?), Haiku x2     0.89  >= 4 flags 18/76 of the original, catches 15/17
  prompt 2, Sonnet x1                                  0.86  >= 2 flags 21/76, catches 15/17
  prompt 3 (prompt 2 + looked-up glossary), Haiku x2   0.84  VOID: Wiktionary refused most requests (429) and a bug saved each
                                                             refusal as "no sense found" (47 of 99 words empty, "torch" got only the
                                                             flaming stick). The lookup idea is untested; the bug is fixed.
  No cut meets the adoption bar (original >= 90% pass AND >= 85% of bad bars caught), and the score is noisy: the same 12 bars read in
  two runs moved 1.2 points on average and the >= 4 flag flipped on 6 of them. So it is a REPORT that ranks; Joe's ear decides.
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor

from .. import config
from . import sensecheck as sc

SYSTEM = """You are a sharp British mate of the rapper, listening to one section of a deadpan British rap: boasts, threats, jokes, deflations, drug and violence euphemism, slang, loanwords, brand names and pop-culture references.
Rap is fragments: a bar does not need a verb or a full sentence. NEVER mark a bar down for a word you do not know: assume any slang, loanword, name, brand or reference is real and means what a fan would know or what the context suggests.
Some items are ONE sentence running over two or more bars, written "bar / bar": judge each such item as one.
For EACH item, explain it to a mate who missed it:
- point: in YOUR OWN words, what the speaker is claiming or doing AND why it lands (the flex, threat, joke, deflation, scene, greeting). Do not just repeat the bar's words. If the only way to explain it is to repeat its words, or you would have to invent facts that are not in the section, write "NONE".
- move: brag | threat | joke | deflate | scene | greeting | other
- hanging: what the item leaves unresolved that the listener needs (a comparison with nothing compared, "my X" or "the X" never explained that is not a known thing, a "for" or "so" that links to nothing). Unknown slang or names are NOT hanging. "" if nothing hangs.
- contradiction: true only if the item contradicts itself and that is not the joke.
- follows: false only if the item has no connection at all to the rest of the section (a non sequitur).
- lands: true if a mate gets the point on one hearing; false if not.
Be fair to rap and harsh on filler: a bar that exists only to land a rhyme word, with no point behind it, does not land. Return JSON only."""

# V2 (16 Oct 2026): v1 was too charitable. Haiku rescued our bars by reinterpreting words (a gnome as "a trade-slang stash", a torch as a
# gun, an elephant as a stash) and then called them landed; Joe's complaint is exactly that a listener has to work them out.
SYSTEM_V2 = """You are a British rap fan hearing one section of a deadpan British rap ONCE, at full speed, with no lyric sheet. The genre is boasts, threats, jokes, deflations, drug and violence euphemism, slang, loanwords, brand names and pop-culture references. Rap is fragments: a missing verb is fine.
Some items are ONE sentence running over two or more bars, written "bar / bar": judge each such item as one.
For EACH item:
- point: what the speaker is claiming or doing, in your own words.
- worked_out: true if YOU had to work the meaning out: you gave a word a sense it does not normally have and that is not established slang (an object standing for a stash, a gun, a person), or you supplied a link or a referent the words do not give ("one" of what? larger than what? cash for what?). Established slang, loanwords, names and brand references used the way fans use them are NOT worked out, even if a stranger would not know them. Give the reason in "how".
- how: what you had to supply or reinterpret, or "".
- natural: true if a British speaker would actually say it this way. false if the word order or word choice is bent to reach a rhyme or fill a beat (an idiom used wrongly, an odd word picked for its sound, a phrase no one says).
- lands: true if the fan gets it on that one hearing.
Judge every item on its own merits; do not grade on a curve. Return JSON only."""

SCHEMA_V2 = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {
        "type": "object",
        "properties": {"n": {"type": "integer"}, "point": {"type": "string"}, "worked_out": {"type": "boolean"}, "how": {"type": "string"},
                       "natural": {"type": "boolean"}, "lands": {"type": "boolean"}},
        "required": ["n", "point", "worked_out", "how", "natural", "lands"]}}},
    "required": ["items"],
}

SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {
        "type": "object",
        "properties": {"n": {"type": "integer"}, "point": {"type": "string"}, "move": {"type": "string"}, "hanging": {"type": "string"},
                       "contradiction": {"type": "boolean"}, "follows": {"type": "boolean"}, "lands": {"type": "boolean"}},
        "required": ["n", "point", "move", "hanging", "contradiction", "follows", "lands"]}}},
    "required": ["items"],
}

# V3 (16 Oct 2026, Joe: "Why not let it search the web to check slang and references"): v2's false flags on the original were mostly words
# the reader did not recognise. Pass 1 (v2) names the words it had to guess (quoted in "how"); the CODE looks each one up (Wiktionary,
# Urban Dictionary; only the word, at most three words, ever leaves the machine; the model never searches, so no line can be sent);
# pass 2 re-reads the section with that glossary. A word used in a looked-up sense is established; one used in a sense nobody lists is not.
SYSTEM_V3 = SYSTEM_V2.replace("Judge every item on its own merits", "A GLOSSARY of looked-up senses may follow the section: a word used in one of "
                              "its listed senses is established slang or a known reference, NOT worked out; a word used in a sense the glossary "
                              "does not list still is. Judge every item on its own merits")
PROMPTS = {1: (SYSTEM, SCHEMA), 2: (SYSTEM_V2, SCHEMA_V2), 3: (SYSTEM_V3, SCHEMA_V2)}
LOOKUP_CACHE = config.EVAL_DIR / "_lookup_cache.json"   # eval/_* is private (never pushed): it holds single words from the original
PROMPT = 2
CRITERIA = ("point", "hanging", "contra", "follows", "lands", "worked", "natural")
FAIL_ON = ("point", "hanging", "contra", "follows", "lands", "worked", "natural")   # narrowed by --validate if a criterion fails the original
FLAGGED = config.ROOT / "toolkit" / "tests" / "sense_flagged.txt"

# HELD-OUT bad bars, in the sections they came from (our drafts; each was rejected by Joe or failed for saying nothing). Not used to write
# the prompt. (file, section header or None for an inline block, the bad bar)
HELD_OUT = [
    (None, ["Cold beer on the house in Porto", "Two glasses, cold lager, back road corners", "Not the worst pint and last orders",
            "Might hit the road to Majorca"], "Two glasses, cold lager, back road corners"),
    (None, ["Cold beer on the house in Porto", "Port in the glass and a page of totals", "No names just numbers on folders",
            "Might take the long way to Oslo"], "No names just numbers on folders"),
    ("writing/_auto/ww_full_draft_v13_r1.md", "Hook 9-16", "Found pink top hat, wear it like bread."),
    ("writing/_auto/ww_full_draft_v13_r1.md", "V1 17-24", "Breakfast had me orange like little."),
    ("writing/_auto/ww_full_draft_v13_r1.md", "V2 9-16", "Tin of direct-to-rust, no recap, paint town red."),
    ("writing/ww_full_draft_v13.md", "V1 17-24", "Queue round the block for the film I'm buying in"),
    ("writing/full_draft_v26.md", "Hook 9-16", "Took a month of the lads and bikes and bins and kit"),
    ("writing/full_draft_v26.md", "V1 1-8", "Got a pass and a rail the road going"),
    ("writing/full_draft_v26.md", "V1 1-8", "Nine countries four walks cash going"),
    ("writing/full_draft_v26.md", "V1 1-8", "A packed bag a long rail a whole month a road going"),
]


def _section(path: str, slot: str) -> list[str]:
    out, cur = [], None
    for ln in (config.ROOT / path).read_text(encoding="utf-8").splitlines():
        if ln.startswith("== "):
            cur = ln[3:].strip()
        elif cur == slot and ln.strip() and not ln.startswith("#"):
            out.append(ln.strip())
    return out


def _terms(bar: str, rows: list[dict]) -> list[str]:
    """words the reader quoted as guessed ('Torch' is read as...), kept only if they occur in the bar and are at most three words."""
    out = []
    low = bar.lower()
    for r in rows:
        for q in re.findall(r"[\'\u2018\"\u201c]([A-Za-z][A-Za-z' \-]{1,30}?)[\'\u2019\"\u201d]", r.get("how", "") or ""):
            q = q.strip()
            if 0 < len(q.split()) <= 3 and q.lower() in low and q.lower() not in out:
                out.append(q.lower())
    return out


def _lookup_cache() -> dict:
    try:
        return json.loads(LOOKUP_CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _get(url: str):
    import time
    import urllib.request
    ua = {"User-Agent": "wrldwd-research/1.0 (personal songwriting project)"}
    for wait in (0, 3, 8, 20):
        time.sleep(wait)
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=20).read())
        except Exception as e:  # noqa: BLE001
            if "429" not in str(e) and "Too Many" not in str(e):
                if "404" in str(e):
                    return {}
                raise
    raise RuntimeError("rate-limited")


SENSE_LABELS = ("slang", "informal", "colloquial", "uk", "british", "multicultural", "mle", "cockney", "vulgar", "idiomatic", "derogatory", "euphemistic")


def lookup(term: str) -> str:
    """established senses of one headword (<= 3 words): Wiktionary's English definitions (labelled slang / informal senses first) and, for a
    name, brand or reference, Wikipedia's one-line description. Cached once a source has answered (a failed request is not cached).
    Urban Dictionary was tried and dropped (16 Oct 2026): its API no longer returns votes, and unranked it offers a crude sense for nearly
    every word, which would rescue every bad bar."""
    import urllib.parse
    assert len(term.split()) <= 3, "only a headword may leave the machine"
    cache = _lookup_cache()
    if term in cache:
        return cache[term]
    # ok = Wiktionary itself answered. A refused request (429) must never be saved as "no sense": the first glossary run did that for 47 of
    # 99 words (elephant and servo among them) and its result was void (16 Oct 2026).
    senses, ok = [], False
    try:
        d = _get("https://en.wiktionary.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "query", "prop": "extracts", "explaintext": 1, "titles": term, "format": "json", "redirects": 1}))
        ok = True
        ext = next(iter(d.get("query", {}).get("pages", {}).values()), {}).get("extract", "") or ""
        eng = ext.split("== English ==", 1)[1].split("\n== ", 1)[0] if "== English ==" in ext else ""
        defs = [ln.strip() for ln in eng.splitlines() if ln.strip() and not ln.strip().startswith("=") and len(ln.strip()) > 12
                and not ln.strip().lower().startswith(("from ", "clipping", "borrowed", "see ", "ipa", "rhymes", "hyphenation", "audio", "deverbal", "present participle"))
                and "ipa(key)" not in ln.lower() and "pronunciation" not in ln.lower()
                and term.split()[0] not in ln.strip().lower()[:len(term) + 2]]
        labelled = [d_ for d_ in defs if d_.startswith("(") and any(k in d_[:60].lower() for k in SENSE_LABELS)]
        for d_ in (labelled + [x for x in defs if x not in labelled])[:5]:
            senses.append("wiktionary: " + d_[:150])
    except Exception:  # noqa: BLE001 - no entry from this source
        pass
    if not senses:
        try:
            d = _get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(term.replace(" ", "_")))
            if d.get("type") != "disambiguation" and (d.get("description") or d.get("extract")):
                senses.append("wikipedia: " + ((d.get("description") or "") + ": " + (d.get("extract") or ""))[:180])
        except Exception:  # noqa: BLE001
            pass
    res = " | ".join(senses)
    if ok:
        cache[term] = res
        LOOKUP_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    return res


def glossary(bars: list[str], reads: list[list[dict]]) -> str:
    """the looked-up senses of every word pass 1 had to guess, as text for pass 2 ("" when nothing was guessed or found)."""
    lines = []
    for i, b in enumerate(bars):
        for term in _terms(b, [rd[i] for rd in reads]):
            s = lookup(term)
            if s and not any(ln.startswith(f"- {term}:") for ln in lines):
                lines.append(f"- {term}: {s}")
    return ("GLOSSARY (looked up; established senses only):\n" + "\n".join(lines)) if lines else ""


def _read(bars: list[str], llm, model: str, prompt: int = None, gloss: str = "") -> list[dict]:
    """one read of a section: per-bar rows (a run-on sentence's verdict is copied to each of its bars)."""
    from ..llm import Request
    U = sc.units(bars)
    texts = sc.unit_texts(bars, U)
    rows = []
    for _ in range(3):   # a CLI call that fails or drops items is retried (it happened under parallel load, 16 Oct 2026)
        try:
            system, schema = PROMPTS[prompt or PROMPT]
            res = llm.complete(Request(model=model, system=system, messages=[{"role": "user", "content": "SECTION (items in order):\n" + sc._context_block(texts)
                                                                                     + ("\n\n" + gloss if gloss else "")}],
                                       schema=schema, max_tokens=max(2000, 220 * len(texts)), effort="low", temperature=0.0, stage="pointcheck", scope="sense"),
                               use_cache=False)
            parsed = res.parsed or {}
        except Exception as e:  # noqa: BLE001
            parsed = {"_error": str(e)[:80]}
        by = {}
        for r in parsed.get("items", []):
            try:
                by[int(r.get("n", 0))] = r
            except (TypeError, ValueError):
                continue
        rows = [by.get(k + 1) or {"unjudged": parsed.get("_error", "missing")} for k in range(len(texts))]
        if not any("unjudged" in r for r in rows):
            break
    return sc._expand(rows, U)


def faults(r: dict) -> set[str]:
    if "unjudged" in r:
        return set()
    f = set()
    if r.get("point", "").strip().upper().startswith("NONE"):
        f.add("point")
    if r.get("hanging", "").strip():
        f.add("hanging")
    if r.get("contradiction"):
        f.add("contra")
    if r.get("follows") is False:
        f.add("follows")
    if r.get("lands") is False:
        f.add("lands")
    if r.get("worked_out") is True:
        f.add("worked")
    if r.get("natural") is False:
        f.add("natural")
    return f


def verdicts(reads: list[list[dict]], fail_on=FAIL_ON) -> list[dict]:
    """per bar: the faults of each read; a bar FAILS only when every read fails it (the sensecheck rule, against read noise)."""
    out = []
    for i in range(len(reads[0])):
        per = [faults(rd[i]) & set(fail_on) for rd in reads]
        out.append({"fails": all(per), "any": any(per), "faults": per, "rows": [rd[i] for rd in reads]})
    return out


def check(bars: list[str], llm=None, model: str = "haiku", reads: int = 2, prompt: int = None) -> dict:
    """cached read of OUR sections (never the original's). Prompt 3 = prompt 2's read, the lookups, then the re-read with the glossary."""
    prompt = prompt or PROMPT
    cache = sc._load()
    gloss = ""
    if prompt == 3:
        gloss = glossary(bars, check(bars, llm=llm, model=model, reads=reads, prompt=2)["reads"])
    key = sc._ckey(model, f"POINT{prompt}\n" + "\n".join(bars) + ("\n" + gloss if gloss else ""))
    if key in cache:
        rd = cache[key]
    else:
        from ..llm import LLM, Ledger
        llm = llm or LLM(ledger=Ledger(run_id="pointcheck"))
        rd = [_read(bars, llm, model, prompt=prompt, gloss=gloss) for _ in range(reads)]
        if not any("unjudged" in r for x in rd for r in x):
            cache[key] = rd
            sc._save()
    v = verdicts(rd)
    return {"verdicts": v, "reads": rd, "fails": [(i + 1, sorted(set().union(*x["faults"]))) for i, x in enumerate(v) if x["fails"]]}


# THE VERDICT ON VALIDATION (16 Oct 2026, benchmark/point_validation_*.json): prompt 2 separates bad bars from the original (AUC 0.89 Haiku
# x2, 0.86 Sonnet x1, 0.91 both) but no cut meets the target (original >= 90% pass AND >= 85% of bad bars caught). So it is a REPORT, not a
# gate: every bar at FLAG_AT or above is listed to Joe with what the reader had to work out (no section allowance to hide in).
SCORED = ("worked", "natural", "lands")
FLAG_AT = 4   # of 6 (2 Haiku reads x 3 faults): 15 of 17 known-bad bars, and 18 of the original's 76 bars (so about 1 flag in 4 is a good bar)


def bar_score(rows: list[dict]) -> int:
    return sum(len(faults(r) & set(SCORED)) for r in rows)


def flags(bars: list[str], model: str = "haiku", reads: int = 2, cached_only: bool = False) -> "list[tuple[int, int, str]] | None":
    """[(bar n, score, what had to be worked out)] for bars at FLAG_AT or above; None when cached_only and the section was never read."""
    key = sc._ckey(model, f"POINT{PROMPT}\n" + "\n".join(bars))
    if cached_only and key not in sc._load():
        return None
    r = check(bars, model=model, reads=reads)
    out = []
    for i in range(len(bars)):
        rows = [rd[i] for rd in r["reads"]]
        s = bar_score(rows)
        if s >= FLAG_AT:
            how = next((x.get("how", "") for x in rows if x.get("how")), "") or next((x.get("point", "") for x in rows), "")
            out.append((i + 1, s, how))
    return out


def selftest() -> tuple[bool, str]:
    t = _terms("G'day there's a torch on call", [{"how": "'Torch' is read as a gun; 'on call' means standby; 'Bristol' is not in the bar"}])
    s = bar_score([{"worked_out": True, "natural": False, "lands": False}, {"worked_out": False, "natural": True, "lands": True}])
    unread = flags(["a section nobody has read yet, kept out of the cache"], cached_only=True)
    ok = t == ["torch", "on call"] and s == 3 and unread is None
    return ok, ("pointcheck: guessed words come only from the bar (<= 3 words); the fault score adds up; an unread section reports as unread "
                f"{'ok' if ok else f'NO {t} {s} {unread}'}")


def _flagged() -> list[tuple[int, str]]:
    out = []
    for ln in FLAGGED.read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            b, line, _ = [x.strip() for x in ln.split("|", 2)]
            out.append((int(b), line))
    return out


def validate(model: str = "haiku", reads: int = 2, pass1: "dict | None" = None) -> dict:
    from ..calib.original import SECTIONS, _lines, private_llm
    import sys
    sys.path.insert(0, str(config.ROOT / "toolkit"))
    import fitbar
    olines = _lines()
    priv = private_llm("point-par")

    p1 = {name: rd for name, s, rd in (pass1 or {}).get("orig", [])}

    def orig(job):
        name, s, e = job
        bars = olines[s:e]
        gloss = glossary(bars, p1[name]) if PROMPT == 3 and name in p1 else ""
        return name, s, [_read(bars, priv, model, gloss=gloss) for _ in range(reads)]
    if PROMPT == 3:   # look the words up one at a time before the reads fan out (Wiktionary rate-limits parallel calls)
        for name, s, e in SECTIONS:
            if name in p1:
                glossary(olines[s:e], p1[name])
    with ThreadPoolExecutor(max_workers=3) as ex:
        ores = list(ex.map(orig, SECTIONS))
    # Joe's seven, in their v4 sections
    D = fitbar.read_draft(str(config.ROOT / "writing" / "song_know_a_guy_v4.md"))
    want = dict((line, b) for b, line in _flagged())
    dev_jobs = [(slot, bars) for slot, bars in D.items() if any(b in want for b in bars)]
    held_jobs = []
    for path, slot, bad in HELD_OUT:
        bars = slot if path is None else _section(path, slot)
        if bad in bars:
            held_jobs.append((path or "inline", bars, bad))

    # each distinct section is read once (three held-out bars share v26's V1 1-8), then the results are looked up per job
    uniq = list({tuple(b): None for b in [j[1] for j in dev_jobs] + [j[1] for j in held_jobs]})
    with ThreadPoolExecutor(max_workers=3) as ex:
        done = dict(zip(uniq, ex.map(lambda b: check(list(b), model=model, reads=reads), uniq)))
    dres = [(j, done[tuple(j[1])]) for j in dev_jobs]
    hres = [(j, done[tuple(j[1])]) for j in held_jobs]
    return {"model": model, "reads": reads, "orig": ores, "dev": dres, "held": hres, "want": want}


def summarise(v: dict, fail_on=FAIL_ON) -> dict:
    o_fail = [s + i + 1 for name, s, rd in v["orig"] for i, x in enumerate(verdicts(rd, fail_on)) if x["fails"]]
    dev_hit, dev_miss = [], []
    for (slot, bars), r in v["dev"]:
        for i, x in enumerate(verdicts(r["reads"], fail_on)):
            if bars[i] in v["want"]:
                (dev_hit if x["fails"] else dev_miss).append(bars[i])
    held_hit, held_miss = [], []
    for (path, bars, bad), r in v["held"]:
        x = verdicts(r["reads"], fail_on)[bars.index(bad)]
        (held_hit if x["fails"] else held_miss).append(bad)
    n_o = sum(len(rd[0]) for _, _, rd in v["orig"])
    return {"fail_on": list(fail_on), "orig_fail_bars": o_fail, "orig_pass_rate": round(1 - len(o_fail) / n_o, 3),
            "dev_caught": len(dev_hit), "dev_n": len(dev_hit) + len(dev_miss), "dev_missed": dev_miss,
            "held_caught": len(held_hit), "held_n": len(held_hit) + len(held_miss), "held_missed": held_miss}


def separation(v: dict) -> dict:
    """AUC of the 0-6 fault score (bad bars vs the original's), and what each cut would flag."""
    o = [bar_score([x[i] for x in rd]) for _, _, rd in v["orig"] for i in range(len(rd[0]))]
    neg = [bar_score([x[i] for x in r["reads"]]) for (slot, bars), r in v["dev"] for i, b in enumerate(bars) if b in v["want"]]
    neg += [bar_score([x[bars.index(bad)] for x in r["reads"]]) for (p, bars, bad), r in v["held"]]
    auc = sum((n > q) + 0.5 * (n == q) for n in neg for q in o) / max(1, len(neg) * len(o))
    return {"auc": round(auc, 3), "cuts": {th: {"original_flagged": sum(x >= th for x in o), "bad_caught": sum(x >= th for x in neg), "bad_n": len(neg)}
                                           for th in range(1, 7)}}


def per_criterion(v: dict) -> dict:
    """how often each criterion alone fires on the original, and on the bad bars (both reads)."""
    out = {}
    for c in CRITERIA:
        out[c] = summarise(v, (c,))
    return out


def main(argv=None) -> int:
    import argparse
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--reads", type=int, default=2)
    ap.add_argument("--prompt", type=int, default=PROMPT)
    ap.add_argument("--dump", help="write every raw read (incl. the original's paraphrases) to this path OUTSIDE the repo, for re-scoring")
    ap.add_argument("--rescore", help="re-score a --dump file without new model calls")
    ap.add_argument("--pass1", help="prompt 3: the --dump of a prompt-2 run, whose reads name the words to look up for the original")
    ap.add_argument("file", nargs="?")
    a = ap.parse_args(argv)
    globals()["PROMPT"] = a.prompt
    if a.validate or a.rescore:
        if a.rescore:
            v = json.loads(open(a.rescore, encoding="utf-8").read())
            v["dev"] = [((s, b), r) for (s, b), r in v["dev"]]
            v["held"] = [((p, b, bad), r) for (p, b, bad), r in v["held"]]
        else:
            v = validate(a.model, a.reads, json.loads(open(a.pass1, encoding="utf-8").read()) if a.pass1 else None)
            if a.dump:
                if str(config.ROOT) in str(__import__("pathlib").Path(a.dump).resolve()):
                    raise SystemExit("--dump must be outside the repo (it holds paraphrases of the original)")
                open(a.dump, "w", encoding="utf-8").write(json.dumps(v, ensure_ascii=False, default=sorted))
        full = summarise(v)
        crit = per_criterion(v)
        print(f"POINT READ ({a.model}, {a.reads} reads; a bar fails only when every read fails it)")
        for c, s in crit.items():
            print(f"  {c:8s} alone: original fails {len(s['orig_fail_bars']):2d}/76 | Joe's seven caught {s['dev_caught']}/{s['dev_n']} | held-out caught {s['held_caught']}/{s['held_n']}")
        print(f"  ALL     : original passes {full['orig_pass_rate']:.0%} (fails bars {full['orig_fail_bars']}) | Joe's seven caught {full['dev_caught']}/{full['dev_n']} "
              f"| held-out caught {full['held_caught']}/{full['held_n']}")
        print(f"  missed (Joe's): {full['dev_missed']}\n  missed (held-out): {full['held_missed']}")
        sep = separation(v)
        print(f"  fault score 0-6: AUC {sep['auc']} | " + " | ".join(f">={k}: original {c['original_flagged']}/76, bad {c['bad_caught']}/{c['bad_n']}" for k, c in sep["cuts"].items()))
        res = {"what": "point read validation: the original's failing bar numbers (no text) and the bad bars caught", "model": v.get("model", a.model),
               "reads": v.get("reads", a.reads), "prompt": a.prompt, "all": full, "per_criterion": crit, "separation": sep}
        (config.ROOT / "benchmark" / f"point_validation_{v.get('model', a.model)}_p{a.prompt}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        return 0
    if a.file:
        D = {}
        cur = None
        for ln in open(a.file, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if ln.startswith("== "):
                cur = ln[3:].strip()
                D[cur] = []
            elif ln.strip() and cur and not ln.startswith("#"):
                D[cur].append(ln.strip())
        tot = 0
        for slot, bars in D.items():
            fl = flags(bars, model=a.model, reads=a.reads)
            tot += len(fl)
            print(f"== {slot}: {len(fl)} bars a listener has to work out (score >= {FLAG_AT} of 6)")
            for n, s, how in fl:
                print(f"  ~ {n} [{s}/6] {bars[n - 1]}\n        {how[:150]}")
        print(f"POINT READ: {tot} bars flagged for Joe (a report: about 1 flag in 4 lands on a good bar; see benchmark/point_validation_haiku.json)")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
