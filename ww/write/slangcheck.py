"""slangcheck: US-only slang (16 Oct 2026, Joe: "US specific slang should be flagged, but not UK").

The "torch" bar used torch for an arsonist, a US-only sense: a British listener hears a flashlight. A word list cannot catch that (torch is
everyday UK English); only the SENSE in the bar is wrong. So a model read, per section: list every word or phrase used in a slang sense
that is American and not used that way in British English. Slang British listeners know (much of it American in origin: guap, doobies,
the rap and drill vocabulary of UK radio) is fine.

A word is flagged only when BOTH reads name it (against read noise). Validated on the original (it must flag nothing) and on fixtures
(toolkit/tests/us_slang.txt: US-only bars that must be flagged, UK slang bars that must not). Cached for our drafts; the original is read
privately and never cached.
  python -m ww.write.slangcheck FILE | --validate
"""
from __future__ import annotations

import json
import re

from .. import config
from . import sensecheck as sc

SYSTEM = """You are a British listener checking a deadpan British rap section for American-only slang.
List every word or short phrase that the section uses in a SLANG sense that is American and NOT used that way in British English, so a British listener would miss or misread it (for example "torch" meaning an arsonist, "bum" meaning a homeless man, "packie" for an off-licence).
Do NOT list: slang British listeners know, even if it started in America (money, drug, gun and party slang heard in UK rap and drill, "dope", "guap", "doobies"); cockney rhyming slang, Multicultural London English, grime and drill vocabulary, which are British; standard words used in their normal sense; place names, brand names, foreign words, greetings.
Only list a word when you are SURE its sense is American-only. When unsure, leave it out.
Return JSON only: {"items": [{"n": bar number, "word": the word or phrase exactly as written, "sense": the American sense, "uk": what a British listener would hear instead}]} and an empty list if there are none."""

SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "n": {"type": "integer"}, "word": {"type": "string"}, "sense": {"type": "string"}, "uk": {"type": "string"}},
    "required": ["n", "word", "sense", "uk"]}}}, "required": ["items"]}
READS = 2
FIXTURES = config.ROOT / "toolkit" / "tests" / "us_slang.txt"


def _read(bars: list[str], llm, model: str) -> list[dict]:
    from ..llm import Request
    for _ in range(3):
        try:
            res = llm.complete(Request(model=model, system=SYSTEM, messages=[{"role": "user", "content": "SECTION:\n" + sc._context_block(bars)}],
                                       schema=SCHEMA, max_tokens=1200, effort="low", temperature=0.0, stage="slangcheck", scope="sense"), use_cache=False)
            if res.parsed is not None and "items" in res.parsed:
                return [x for x in res.parsed["items"] if isinstance(x, dict)]
        except Exception:  # noqa: BLE001
            continue
    raise RuntimeError("no read")


US_PLACES = set("america american usa us u.s.a states yank yanks new york nyc la vegas miami texas california chicago brooklyn "
                "hollywood florida detroit atlanta".split())


def _in_america(bars: list[str], n: int) -> bool:
    """a bar about America may use American slang, as the original's do (the same rule as a local word: it fits its place)."""
    near = " ".join(bars[max(0, n - 2):n + 1]).lower()
    return bool(set(re.findall(r"[a-z.]+", near)) & US_PLACES) or "u s.a" in near or "u.s.a" in near or re.search(r"\bin u\b", near) is not None


def agreed(reads: list[list[dict]], bars: list[str]) -> list[tuple[int, str, str]]:
    """[(bar n, word, sense)] named by every read, present in that bar, and not in a bar about America."""
    sets = []
    for rd in reads:
        s = {}
        for x in rd:
            try:
                n = int(x.get("n", 0))
            except (TypeError, ValueError):
                continue
            w = (x.get("word") or "").strip().lower()
            if 1 <= n <= len(bars) and w and w in bars[n - 1].lower():
                s[(n, w)] = x.get("sense", "")
        sets.append(s)
    common = set.intersection(*[set(s) for s in sets]) if sets else set()
    return sorted((n, w, sets[0][(n, w)]) for n, w in common if not _in_america(bars, n))


def check(bars: list[str], llm=None, model: str = None) -> dict:
    model = model or sc.model()
    cache = sc._load()
    key = sc._ckey(model, "USSLANG2\n" + "\n".join(bars))
    if key in cache:
        reads = cache[key]
    else:
        try:
            from ..llm import LLM, Ledger
            llm = llm or LLM(ledger=Ledger(run_id="slangcheck"))
            reads = [_read(bars, llm, model) for _ in range(READS)]
        except Exception as e:  # noqa: BLE001 - offline never fails a bar
            return {"flags": [], "unjudged": str(e)[:80]}
        cache[key] = reads
        sc._save()
    return {"flags": agreed(reads, bars)}


def fixtures() -> list[tuple[bool, str]]:
    out = []
    for ln in FIXTURES.read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            kind, bar = [x.strip() for x in ln.split("|", 1)]
            out.append((kind == "US", bar))
    return out


def selftest() -> tuple[bool, str]:
    r = agreed([[{"n": 1, "word": "Torch", "sense": "arsonist"}], [{"n": 1, "word": "torch", "sense": "arsonist"}, {"n": 2, "word": "bum", "sense": "x"}]],
               ["G'day there's a torch on call", "He's a bum"])
    ok = r == [(1, "torch", "arsonist")] and bool(fixtures())
    return ok, f"slangcheck: a word counts only when every read names it, in its bar {'ok' if ok else r}"


def validate(model: str = None) -> dict:
    from ..calib.original import SECTIONS, _lines, private_llm
    model = model or sc.model()
    L = _lines()
    priv = private_llm("slang-par")
    orig = {}
    for name, s, e in SECTIONS:
        bars = L[s:e]
        f = agreed([_read(bars, priv, model) for _ in range(READS)], bars)
        orig[name] = [(s + n, w) for n, w, _ in f]   # song bar numbers and single words only
    fx = fixtures()
    us = [b for k, b in fx if k]
    uk = [b for k, b in fx if not k]
    fu = check(us, model=model)["flags"]
    fk = check(uk, model=model)["flags"]
    return {"model": model, "original_flags": orig, "us_caught": sorted({n for n, _, _ in fu}), "us_n": len(us),
            "uk_flagged": sorted({n for n, _, _ in fk}), "uk_n": len(uk)}


def main(argv=None) -> int:
    import argparse
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args(argv)
    if a.validate:
        v = validate()
        n_o = sum(len(x) for x in v["original_flags"].values())
        print(f"US SLANG ({v['model']}, {READS} reads, both must agree): original flags {n_o} {[x for xs in v['original_flags'].values() for x in xs]}")
        print(f"  US-only fixtures caught {len(v['us_caught'])}/{v['us_n']}; UK-slang fixtures flagged {len(v['uk_flagged'])}/{v['uk_n']} {v['uk_flagged']}")
        (config.ROOT / "benchmark" / "us_slang_validation.json").write_text(json.dumps(v, indent=1), encoding="utf-8")
        return 0
    if a.file:
        cur, D = None, {}
        for ln in open(a.file, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if ln.startswith("== "):
                cur = ln[3:].strip()
                D[cur] = []
            elif ln.strip() and cur and not ln.startswith("#"):
                D[cur].append(ln.strip())
        n = 0
        for slot, bars in D.items():
            for b, w, sense in check(bars)["flags"]:
                n += 1
                print(f"  x {slot} bar {b}: '{w}' = {sense} (US-only) | {bars[b - 1]}")
        print(f"US SLANG: {'PASS' if not n else f'{n} flagged'}")
        return 1 if n else 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
