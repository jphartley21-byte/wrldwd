"""Flow check: stress clashes, lapses, mid-bar pauses and consonant pile-ups per bar.
Usage: python toolkit/flow_check.py -   (stdin: draft bars; optionally reference bars, then a line '---', then draft bars)
Stress is a text estimate (content words stressed, function words not): a screen, not an ear. Joe's ear decides.
"""
import re, sys
sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from rhyme_tools import pron, is_v

FUNC = set("""a an the and but or so to of in on at for with by from up as is it it's its i i'm my me we our you your he she they them their his her him us 'em em
that that's this then than be been was were are am do did has have had will would can could might may must shall should not no
there here what when where who how if just got get""".split())
VOICE = set("B D G V DH Z ZH JH M N NG L R W Y".split())


def bar_profile(line):
    words = re.findall(r"[A-Za-z'å]+|[,;:\-–—]", line)
    stress, pauses, clusters = [], 0, 0
    prev_coda = []
    for w in words:
        if w in ",;:–—":
            pauses += 1
            continue
        ph = pron(w.lower().replace("å", "a")) or []
        if not ph and w.isupper() and len(w) > 1:  # initialism, spoken letter by letter
            ph = ["AH1"] + ["AH0"] * (sum(3 if c == "W" else 1 for c in w) - 1)
        if not ph:  # out-of-dictionary: estimate syllables from vowel groups, stress the first
            n = max(1, len(re.findall(r"[aeiouy]+", w.lower().rstrip("e"))))
            ph = ["AH1"] + ["AH0"] * (n - 1)
        vs = [p for p in ph if is_v(p)]
        if not vs:
            continue
        func = w.lower() in FUNC
        for p in vs:
            s = 0 if func else (1 if p[-1] in "12" or len(vs) == 1 else 0)
            if not func and p[-1] == "2":
                s = 0
            stress.append(s)
        first_v = next(i for i, p in enumerate(ph) if is_v(p))
        last_v = max(i for i, p in enumerate(ph) if is_v(p))
        onset, coda = ph[:first_v], ph[last_v + 1:]
        if len(prev_coda) + len(onset) >= 3:
            clusters += 1
        prev_coda = coda
    clashes = sum(1 for a, b in zip(stress, stress[1:]) if a and b)
    lapse = max((len(m) for m in re.findall(r"0+", "".join(map(str, stress)))), default=0)
    pos = [i + 1 for i, s in enumerate(stress) if s]
    return dict(syl=len(stress), grid=pos, clash=clashes, lapse=lapse, pause=pauses, cluster=clusters)


def show(bars, tag):
    out = []
    for i, b in enumerate(bars, 1):
        p = bar_profile(b)
        out.append(p)
        print(f"{tag}{i}. syl={p['syl']:>2} stress={p['grid']} clash={p['clash']} lapse={p['lapse']} pause={p['pause']} cluster={p['cluster']}"
              + ("" if tag == "R" else f"   | {b}"))
    return out


def main():
    lines = [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]
    ref, draft = ([], lines)
    if "---" in lines:
        k = lines.index("---")
        ref, draft = lines[:k], lines[k + 1:]
    r = show(ref, "R") if ref else []
    d = show(draft, "D")
    tot = lambda P, k: sum(x[k] for x in P)
    for k in ("clash", "pause", "cluster"):
        print(f"total {k}: draft {tot(d, k)}" + (f" vs ref {tot(r, k)}" if r else ""))
    if r:
        for i, (a, b) in enumerate(zip(r, d), 1):
            flags = []
            if b["clash"] > a["clash"]: flags.append("more clashes")
            if b["pause"] > a["pause"]: flags.append("mid-bar pause")
            if b["cluster"] > a["cluster"]: flags.append("consonant pile-up")
            if b["lapse"] > a["lapse"] + 1: flags.append("long weak run")
            if a["grid"] and b["grid"] and a["syl"] - a["grid"][-1] != b["syl"] - b["grid"][-1]: flags.append("rhyme stress moved")
            print(f"bar {i}: " + (", ".join(flags) if flags else "ok"))


if __name__ == "__main__":
    main()
