"""ideas_cluster: offline pattern-finding over a mined idea list (no model tokens). ADVISORY.
  python toolkit/ideas_cluster.py ideas/hook.md [--out ideas/patterns_hook.md] [--beats work/hook/1_beats.md]
Input lines: `- [ ] idea text | device | place | end-sound | true/persona/invented` (tags optional; ticked = `[x]`).
Reports: end-sound families (perfect rhyme key and stressed vowel), devices, places, recurring words/bigrams (motifs),
place x device gaps, overused sounds, what Joe ticked vs the whole pool, and untouched beats. Uses rhyme_tools for sounds.
"""
import os, re, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    from rhyme_tools import pron, key, stressed_vowel
except Exception:  # cmudict missing: fall back to spelling
    pron = key = stressed_vowel = None

STOP = set("the a an and or but of to in on at for with my me i it is its im i'm so then that this he she we they you was be as up out all just got get like not no yes if when".split())
LINE = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s*(.+)$")


def parse(path):
    items = []
    for raw in open(path, encoding="utf8"):
        m = LINE.match(raw)
        if not m:
            continue
        parts = [p.strip() for p in m.group(2).split("|")]
        items.append(dict(ticked=m.group(1) in "xX", text=parts[0], device=(parts[1] if len(parts) > 1 else "").lower(),
                          place=(parts[2] if len(parts) > 2 else "").lower(), sound=(parts[3] if len(parts) > 3 else ""),
                          status=(parts[4].lower() if len(parts) > 4 else "")))
    return items


def last_word(t):
    ws = re.findall(r"[A-Za-z']+", t)
    return ws[-1].lower() if ws else ""


def sound_of(item):
    w = last_word(item["text"])
    if pron and w:
        ph = pron(w)
        if ph:
            try:
                k = key(ph, 0)
                sv = stressed_vowel(ph)
                return ("-".join(k) if isinstance(k, (list, tuple)) else str(k)), sv
            except Exception:
                pass
    return (w[-3:] if w else "?"), (w[-2:] if w else "?")


def words(t):
    return [w for w in re.findall(r"[a-z']+", t.lower()) if w not in STOP and len(w) > 2]


def table(counter, total, top=12, mark=0.2):
    out = []
    for k, n in counter.most_common(top):
        flag = "  <- heavy" if total and n / total >= mark and total >= 20 else ""
        out.append(f"- {k or '(untagged)'}: {n} ({n * 100 // max(total, 1)}%){flag}")
    return "\n".join(out) or "- none"


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    path = a[0]
    out = a[a.index("--out") + 1] if "--out" in a else None
    beats = a[a.index("--beats") + 1] if "--beats" in a else None
    items = parse(path)
    n = len(items)
    if not n:
        print("no tickable idea lines found (expected '- [ ] idea | device | place | end-sound | status')"); return
    for it in items:
        it["key"], it["vowel"] = sound_of(it)
    ticked = [i for i in items if i["ticked"]]
    r = []
    r.append(f"# Patterns for {os.path.basename(path)} (auto, advisory)\n\n{n} ideas, {len(ticked)} ticked by Joe.\n")
    r.append("## End-sound families (perfect rhyme tail)\n" + table(Counter(i["key"] for i in items), n))
    r.append("\n## Stressed vowel of the end word (vowel carpets)\n" + table(Counter(i["vowel"] for i in items), n))
    r.append("\n## Devices\n" + table(Counter(i["device"] for i in items), n))
    r.append("\n## Places\n" + table(Counter(i["place"] for i in items), n))
    r.append("\n## Truth status\n" + table(Counter(i["status"] for i in items), n))
    w = Counter(x for i in items for x in set(words(i["text"])))
    bg = Counter(b for i in items for b in set(zip(words(i["text"]), words(i["text"])[1:])))
    r.append("\n## Recurring words (motifs)\n" + ", ".join(f"{k} x{v}" for k, v in w.most_common(25) if v > 2))
    r.append("\n\n## Recurring word pairs\n" + (", ".join(f"{' '.join(k)} x{v}" for k, v in bg.most_common(15) if v > 1) or "none"))
    # place x device gaps
    devs = sorted({i["device"] for i in items if i["device"]})
    pls = [p for p, _ in Counter(i["place"] for i in items if i["place"]).most_common(10)]
    cell = Counter((i["place"], i["device"]) for i in items)
    gaps = [f"{p} x {d}" for p in pls for d in devs if cell[(p, d)] == 0]
    r.append("\n\n## Gaps (top places with no idea of a device; candidates to mine next)\n" + (", ".join(gaps[:30]) or "none"))
    if ticked:
        r.append("\n\n## What Joe ticked vs the pool (taste signal)")
        for label, f in (("sound", lambda i: i["key"]), ("device", lambda i: i["device"]), ("place", lambda i: i["place"])):
            pool, tk = Counter(f(i) for i in items), Counter(f(i) for i in ticked)
            rows = sorted(tk, key=lambda k: -tk[k] / pool[k])[:6]
            r.append(f"- {label}: " + ", ".join(f"{k or '(none)'} {tk[k]}/{pool[k]}" for k in rows))
    if beats and os.path.exists(beats):
        bt = open(beats, encoding="utf8").read().lower()
        used = [p for p in pls if p and p in bt]
        miss = [p for p in pls if p and p not in bt]
        r.append(f"\n\n## Versus beat sheet\n- places in ideas AND beats: {', '.join(used) or 'none'}\n- places in ideas but not in beats (unused material): {', '.join(miss) or 'none'}")
    text = "\n".join(r) + "\n"
    if out:
        open(out, "w", encoding="utf8").write(text); print("wrote", out)
    print(text)


if __name__ == "__main__":
    main()
