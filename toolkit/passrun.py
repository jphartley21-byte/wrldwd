"""passrun: mechanical helper for one pass of the full-draft run (ADVISORY).
  python toolkit/passrun.py N            # reads work/song/draft_current.md, writes work/song/passes/pN_*.txt and prints diagnostics
Draft format: '[Hook]' / '[Verse 1]' ... headers; '#' lines are comments; a line starting '=' is Joe's verbatim bar; blank line = chain break;
a comment '# C1 name' above a chain labels it. Chains = blocks of >= 4 bars in verse sections that are not all '=' lines.
Writes: pN_pool_A.txt / pN_pool_B.txt (shuffled stanzas: our chains + 4 original chains, with the shared glossary), pN_map.json (which stanza is whose),
and runs glossary.py (unknown words not in work/song/glossary_shared.md), quality.py per chain, bartest per chain.
"""
import json, os, random, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
W = os.path.join(ROOT, "work", "song"); P = os.path.join(W, "passes"); os.makedirs(P, exist_ok=True)
n = sys.argv[1] if len(sys.argv) > 1 else "0"


def chains():
    out, cur, name, sect = [], [], "", ""
    for raw in open(os.path.join(W, "draft_current.md"), encoding="utf8"):
        s = raw.rstrip("\n")
        if s.startswith("["):
            if cur: out.append((name, sect, cur)); cur = []
            sect = s.strip(); name = ""
            continue
        if s.startswith("#"):
            if cur: out.append((name, sect, cur)); cur = []
            m = re.match(r"#\s*(C\d+\S*)", s)
            if m: name = m.group(1)
            continue
        if not s.strip():
            if cur: out.append((name, sect, cur)); cur = []
            continue
        cur.append(s)
    if cur: out.append((name, sect, cur))
    return [(nm, sc, c) for nm, sc, c in out if sc.lower().startswith("[verse") and len(c) >= 4 and not all(x.startswith("=") for x in c)]


def orig_chunks():
    O = [l.strip() for l in open(os.path.join(ROOT, "reference", "original_lyrics.txt"), encoding="utf8") if l.strip() and not l.startswith("#")]
    return {"O-Dublin": O[32:40], "O-Turkey": O[40:48], "O-plod": O[48:60], "O-V2": O[60:68]}


def main():
    ch = chains()
    oc = orig_chunks()
    items = [(f"{nm or 'C?'}", [x.lstrip("=") for x in lines]) for nm, sc, lines in ch] + [(k, v) for k, v in oc.items()]
    for tag, ls in items:
        open(os.path.join(P, f"tmp_{tag}.txt"), "w", encoding="utf8").write("\n".join(ls) + "\n")
    gl = open(os.path.join(W, "glossary_shared.md"), encoding="utf8").read()
    known = gl.lower()
    # diagnostics
    for tag, ls in items:
        if tag.startswith("O-"):
            continue
        f = os.path.join(P, f"tmp_{tag}.txt")
        print(f"\n===== {tag} ({len(ls)} bars)")
        g = subprocess.run([sys.executable, os.path.join(HERE, "glossary.py"), f], capture_output=True, text=True, encoding="utf8").stdout
        miss = [l.split()[0] for l in g.splitlines() if "NEEDS GLOSS" in l and l.split()[0] not in known]
        print("  glossary: " + (("add to glossary_shared.md -> " + ", ".join(miss)) if miss else "clean vs shared glossary"))
        q = subprocess.run([sys.executable, os.path.join(HERE, "quality.py"), f], capture_output=True, text=True, encoding="utf8").stdout.strip().splitlines()
        print("  quality: " + " | ".join(l.strip() for l in q if "VERDICT" in l or "-" in l[:6] or "BELOW" in l)[:300])
        b = subprocess.run([sys.executable, os.path.join(HERE, "bartest.py"), f], capture_output=True, text=True, encoding="utf8").stdout.strip().splitlines()
        print("  bartest: " + (b[-1] if b else ""))
    # pools (two shuffles so the critics see different orders)
    for crit in ("A", "B"):
        random.seed(hash((n, crit)) % 10**6)
        order = items[:]; random.shuffle(order)
        txt = ["GLOSSARY (apply equally to all stanzas):", gl, ""]
        mp = {}
        for i, (tag, ls) in enumerate(order, 1):
            txt.append(f"STANZA {i}"); txt += ls; txt.append("")
            mp[i] = tag
        open(os.path.join(P, f"p{n}_pool_{crit}.txt"), "w", encoding="utf8").write("\n".join(txt))
        json.dump(mp, open(os.path.join(P, f"p{n}_map_{crit}.json"), "w"))
    for tag, _ in items:
        try: os.remove(os.path.join(P, f"tmp_{tag}.txt"))
        except OSError: pass
    print(f"\nwrote pools: work/song/passes/p{n}_pool_A.txt, p{n}_pool_B.txt (+ maps). Chains in pool: {[t for t,_ in items if not t.startswith('O-')]}")


if __name__ == "__main__":
    main()
