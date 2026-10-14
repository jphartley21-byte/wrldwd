"""meaning_judge: can a LOCAL model read a bar for SENSE? A measured experiment, not a claim.

Why (13 Oct 2026). Joe: "surely AI CAN do this now to some extent?" The repo has tried three times and
failed -- funny.py (89% base rate), attest.py (flags good lines as hard as gibberish), ml/judge (learned
from ONE positive block; its word-level effects are <= 0.014). All three were LEXICAL/STATISTICAL proxies.
None of them could PARAPHRASE, which is the one operation that actually tests "does this bar claim
anything": restate the bar as a plain sentence, and if the restatement collapses to a list of objects,
the bar said nothing.

That is exactly the test craft_principles.md section 4 calls the paraphrase test and marks human-only.
A local instruct model can do it offline. This tool asks for it and then MEASURES the answer against the
labelled set we already own, because a screen that cannot separate known-good from known-empty is another
judge that has to be thrown away -- which is the whole history of this problem.

Everything is localhost. No lyric of the original's is ever sent, stored or read here (rule 4).

  python ml/meaning_judge.py                     # the labelled set: accuracy, then the failures
  python ml/meaning_judge.py --bars FILE         # report only, on any draft in project format
  python ml/meaning_judge.py --selftest          # offline: the parser and the verdict rule
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OLLAMA = "http://localhost:11434/api/generate"

PROMPT = """You are a strict lyric editor. One bar of a rap is below.

A bar "says something" when something is at stake in it: a person doing something, an
attitude, a complaint, a plan, a place being reached. A bar "says nothing" when it is a
SUMMARY -- a list of kit, places, trips or counts, however concrete -- with nothing
happening in it.

Examples of that distinction (not from this song):
- says something: Bribed the doorman with the last of the change
- says nothing:  Rucksack, railcard, two nights in a hostel

Answer with JSON only, no prose:
{{"plain": "...", "kind": "action|stance|scene|summary|phatic"}}

"plain": the bar restated as a plain sentence of at most 12 words. ALWAYS fill this in, even
when the bar says nothing.

"kind" is one of:
- "action"  -- someone does something
- "stance"  -- the speaker judges, wants, feels or intends something
- "scene"   -- a specific moment is placed: who is where, and what is happening
- "summary" -- a list of kit, places, trips or counts; nothing happens in it
- "phatic"  -- a greeting or an address with no content at all

BAR: {bar}"""


KINDS = ("action", "stance", "scene", "summary", "phatic")
# "summary" is the one that says nothing. "phatic" is the bar that only greets -- a burden it cannot
# carry alone, but Joe's own locked opener is phatic, so a bar is not condemned for being one.
EMPTY_KINDS = {"summary"}


def ollama(model, bar, temperature=0.1, timeout=180):
    payload = {"model": model, "prompt": PROMPT.format(bar=bar), "stream": False,
               "options": {"temperature": temperature, "num_predict": 120, "num_ctx": 2048}}
    req = urllib.request.Request(OLLAMA, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read()).get("response", "")
    except urllib.error.URLError as e:
        sys.exit(f"cannot reach Ollama ({e}). Start it with `ollama serve`.")


def parse(text):
    """The model's JSON, tolerantly. Returns (kind, plain); kind is None if it did not answer."""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None, None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None, None
    kind = str(d.get("kind", "")).strip().lower()
    for k in KINDS:
        if kind.startswith(k):
            kind = k
            break
    else:
        kind = None
    return kind, str(d.get("plain", "")).strip()


def verdict(kind, plain):
    """Said nothing = the model read it as a list, OR could not answer, OR paraphrased to nothing."""
    if kind is None:
        return None
    if kind in EMPTY_KINDS:
        return False
    if kind == "phatic":
        return True          # nothing to restate; the bar's job is the greeting itself
    words = re.findall(r"[A-Za-z']+", plain.lower())
    if len(words) < 3:
        return False
    return True


# The labelled set: bars whose verdict we already know, from Joe's own decisions. Positives are the
# eight locked/passing hook bars of the section that passes every gate; negatives are the inventory
# lines this session produced and the widened meaning gate now catches. Every label carries its
# provenance, so the ground truth can be argued with rather than trusted. Nothing here is the
# original's. n=14: one bar is worth 7% of the accuracy figure.
LABELLED = [
    ("pass", "Yo, bonjourno", "locked Hook 1-4 (phatic opener Joe wrote)"),
    ("pass", "Said damn at the on-stage porno", "locked Hook 1-4"),
    ("pass", "Front row on my phone, so bored, though", "locked Hook 1-4"),
    ("pass", "So I boarded a plane out to Bordeaux", "locked Hook 1-4"),
    ("pass", "Cash back on the bier in Zurich", "Hook 5-8 v15, ALL PASS"),
    ("pass", "Stuck in the black van in all the traffic", "Hook 5-8 v15, ALL PASS"),
    ("pass", "Sitting back with a real panic", "Hook 5-8 v15, ALL PASS"),
    ("pass", "Might pack the backpack in Munich", "Hook 5-8 v15, ALL PASS"),
    ("fail", "Two glasses, cold lager, back road corners", "v25 inventory; Joe's reject shape"),
    ("fail", "Pass maps plans and the road the rail going", "v25/v26 inventory"),
    ("fail", "A packed bag a long rail a whole month a road going", "v25/v26 inventory"),
    ("fail", "Cash cards and paid the same day", "v25/v26 inventory"),
    ("fail", "Nine countries four walks cash going", "v25/v26 inventory"),
    ("fail", "Gave them the cash the cards and the pass", "v25/v26 inventory"),
]


def score(rows):
    tp = fp = tn = fn = 0
    for want, got in rows:
        if want == "pass" and got is True:
            tp += 1
        elif want == "fail" and got is False:
            tn += 1
        elif want == "fail" and got is not False:
            fn += 1
        else:
            fp += 1
    n = tp + fp + tn + fn
    return tp, fp, tn, fn, (tp + tn) / max(1, n), n


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print("  FAIL", name)

    chk("parses clean json", parse('{"kind": "action", "plain": "he paid the man"}') == ("action", "he paid the man"))
    chk("parses fenced json", parse('Here you go:\n```json\n{"kind": "summary", "plain": "kit list"}\n```'
                                    ) == ("summary", "kit list"))
    chk("parses a padded kind", parse('{"kind": "Summary (a list)", "plain": "things"}'
                                      ) == ("summary", "things"))
    chk("garbage -> unknown", parse("I cannot help") == (None, None))
    chk("a listed bar fails", verdict("summary", "cash cards keys") is False)
    chk("a claim with an empty paraphrase fails too", verdict("action", "it") is False)
    chk("a claim with a real paraphrase passes", verdict("action", "he paid the driver in cash") is True)
    chk("a greeting is not condemned", verdict("phatic", "hello") is True)
    chk("no answer is not a verdict", verdict(None, "") is None)
    tp, fp, tn, fn, acc, n = score([("pass", True), ("pass", True), ("fail", False), ("fail", True)])
    chk("scoring counts a miss", (tp, fp, fn) == (2, 0, 1) and abs(acc - 0.75) < 1e-9)
    print("meaning_judge selftest:", "PASSED" if ok else "FAILED")
    return ok


def judge_bars(bars, model, quiet=False):
    out = []
    for b in bars:
        kind, plain = parse(ollama(model, b))
        v = verdict(kind, plain)
        out.append((b, v, kind, plain))
        if not quiet:
            tag = "CLAIMS" if v else ("EMPTY " if v is False else "????? ")
            print(f"  {tag} [{kind or '?':<9}] {b}")
            if plain:
                print(f"          -> {plain[:90]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="nollama/mythomax-l2-13b:Q4_K_M")
    ap.add_argument("--bars", help="a draft in project format: report only")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.bars:
        sys.path.insert(0, os.path.join(ROOT, "toolkit"))
        import songcheck as sc
        secs = [(s, b) for s, b in sc.bars_of(open(a.bars, encoding="utf8").read()) if s]
        bars = [l for _s, b in secs for l in b]
        res = judge_bars(bars, a.model)
        bad = [b for b, v, _k, _p in res if v is False]
        print(f"\nmeaning_judge: {len(bad)} of {len(bars)} bars read as claiming nothing")
        return
    print(f"labelled set: {len(LABELLED)} bars, model {a.model}\n")
    rows = []
    for want, bar, _why in LABELLED:
        kind, plain = parse(ollama(a.model, bar))
        got = verdict(kind, plain)
        rows.append((want, got))
        mark = "ok " if (want == "pass") == (got is True) else "XX "
        print(f"  {mark} want {want:<4} read {kind or '?????':<9} {bar}")
        if plain:
            print(f"          -> {plain[:90]}")
    tp, fp, tn, fn, acc, n = score(rows)
    print(f"\naccuracy {acc:.0%} on {n} bars (n={n}: each bar is {100 // n}% of this figure) | "
          f"caught {tn} of {tn + fn} empties, passed {tp} of {tp + fp} real bars")


if __name__ == "__main__":
    main()
