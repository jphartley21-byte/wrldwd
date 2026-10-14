"""build_dataset: mine this repo into a labelled dataset of stanzas.

There is no public corpus of "bars Joe liked", but three years of this project already record his
verdicts. This turns them into rows. Only files INSIDE the project are read: the original's lyrics
live outside (CLAUDE.md rule 4) and are NEVER touched here, so no model trained from this data can
memorise the original.

Label sources, strongest first:

  accept   toolkit/keepers.json -> locked_lines      (bars 1-4 Joe locked; the only ground truth)
  park     writing/contenders.md                     ("not bad, it's a contender" - held OUT of
                                                      training, scored as a mid-case sanity check)
  reject   toolkit/tests/rejected_*.txt              (stanzas Joe rejected; first line '# SLOT BAR')
  weak_neg writing/agents/*.md  "Weakest bar: N"     (an agent's own weakest bar per round - weak)
  unlabel  writing/full_draft_v*.md, bars_*.md       (never judged: kept for later labelling)

Usage:
  python ml/build_dataset.py                 # write ml/data/dataset.jsonl + print a summary
  python ml/build_dataset.py --json          # print the summary as JSON
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import features as F  # noqa: E402

OUT = os.path.join(HERE, "data", "dataset.jsonl")


def _read(path):
    with open(path, encoding="utf8") as fh:
        return [l.rstrip("\n") for l in fh]


def _clean_bars(lines):
    """Thin alias so this module and ml/judge.py share one definition of 'a bar'."""
    return F.clean_bars(lines)


def from_keepers():
    """accept: the four locked bars; like: shorter fragments Joe explicitly kept."""
    path = os.path.join(ROOT, "toolkit", "keepers.json")
    k = json.load(open(path, encoding="utf8"))
    locked = [b for b in k.get("locked_lines", []) if b.strip()]
    rows = []
    if len(locked) >= 2:
        rows.append({"source": "keepers.json:locked_lines", "label": "accept",
                     "provenance": "Joe locked these bars in writing/bars_1-4_v9.md (9 Oct 2026)",
                     "bars": locked})
    phrases = [p for p in k.get("phrases", []) if p.strip()]
    if phrases:
        rows.append({"source": "keepers.json:phrases", "label": "like",
                     "provenance": "phrases Joe kept in toolkit/keepers.json (lines he liked)",
                     "bars": phrases})
    return rows


def from_contenders():
    """park: stanzas Joe called a contender but did not accept."""
    path = os.path.join(ROOT, "writing", "contenders.md")
    if not os.path.exists(path):
        return []
    rows, cur_head, buf = [], None, []
    for l in _read(path):
        if l.startswith("## "):
            if cur_head and len(buf) >= 2:
                keep = _clean_bars(buf)
                keep = [b for b in keep if not b.startswith(("ABBA", "Internal", "Wordplay"))]
                if len(keep) >= 2:
                    rows.append({"source": "contenders.md", "label": "park",
                                 "provenance": f'Joe: {cur_head.strip("# ")[:80]}',
                                 "bars": keep[:4]})
            cur_head, buf = l, []
        elif cur_head:
            buf.append(l)
    if cur_head and len(buf) >= 2:
        keep = _clean_bars(buf)
        keep = [b for b in keep if not b.startswith(("ABBA", "Internal", "Wordplay"))]
        if len(keep) >= 2:
            rows.append({"source": "contenders.md", "label": "park",
                         "provenance": f'Joe: {cur_head.strip("# ")[:80]}', "bars": keep[:4]})
    return rows


def from_rejected():
    """reject: the calibration fixtures Joe rejected (the strongest negative evidence)."""
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "toolkit", "tests", "rejected_*.txt"))):
        lines = _read(path)
        if not lines:
            continue
        head = lines[0]                       # '# SLOT STARTBAR'
        bars = _clean_bars(lines[1:])
        if len(bars) < 2:
            continue
        rows.append({"source": os.path.basename(path), "label": "reject",
                     "provenance": f"Joe rejected this stanza ({head.strip('# ').strip()})",
                     "bars": bars})
    return rows


ROUND_RE = re.compile(r"^#\s*Round\b")
# A bar line in a round listing: a 1-2 digit bar number, then the text. Two-digit numbers are
# followed by ONE space in the transcripts ("10 The in-laws say..."), so 2+ spaces is too strict.
BAR_RE = re.compile(r"^\s*(\d{1,2})\s+(?=\S)(.+?)\s*$")


def from_agent_weakest():
    """weak_neg: in each writer round, the agent named its own weakest bar (the bar, with text)."""
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "writing", "agents", "*.md"))):
        section, bars, hits = None, {}, []
        sections = []            # (section_heading, {bar_no: text}, [weak bar numbers])

        def close(sec, bmap, hit_list):
            picked = [bmap[n] for n in hit_list if n in bmap]
            if sec and picked:
                sections.append((sec, picked))

        for l in _read(path):
            if ROUND_RE.match(l):
                close(section, bars, hits)
                section, bars, hits = l, {}, []
                continue
            m = BAR_RE.match(l)
            if m and not re.search(r"\|\s*\d", l) and "PASS" not in l and "FAIL" not in l:
                txt = re.split(r"\s{2,}(?:CHANGED|NOTE)\b", m.group(2))[0].strip()
                if 1 < len(txt.split()) <= 20 and int(m.group(1)) <= 20:
                    bars[int(m.group(1))] = txt
                continue
            w = re.search(r"Weakest (?:bar|runner-up)[^:]*:\s*(\d+)", l)
            if w:
                hits.append(int(w.group(1)))
        close(section, bars, hits)
        for sec, picked in sections:
            rows.append({"source": os.path.basename(path), "label": "weak_neg",
                         "provenance": f"agent self-report in {sec.strip('# ')[:60]}",
                         "bars": picked[:3]})
    seen, uniq = set(), []
    for r in rows:
        key = tuple(r["bars"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    return uniq


DRAFT_GLOBS = ["writing/full_draft_v*.md", "writing/bars_1-4_v*.md", "writing/bars_5-8_v*.md",
               "writing/bars_1-8_v*.txt", "writing/hook_1-16_v*.md"]


def from_drafts():
    """unlabel: bars never carried a verdict - the pool Joe can label later."""
    rows = []
    for pat in DRAFT_GLOBS:
        for path in sorted(glob.glob(os.path.join(ROOT, pat))):
            bars = _clean_bars(_read(path))
            if len(bars) >= 4:
                rows.append({"source": os.path.relpath(path, ROOT).replace("\\", "/"),
                             "label": "unlabel", "provenance": "never judged", "bars": bars[:16]})
    return rows


def build():
    raw = from_keepers() + from_contenders() + from_rejected() + from_agent_weakest() + from_drafts()
    blocks = []
    for r in raw:
        rows = F.block_row(r["bars"], r["source"], r["label"], r["provenance"])
        blocks.append(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf8") as fh:
        for b in blocks:
            fh.write(json.dumps(b, ensure_ascii=False) + "\n")
    return blocks


def summary(blocks):
    by = {}
    for b in blocks:
        s = by.setdefault(b["label"], {"blocks": 0, "bars": 0, "priors": []})
        s["blocks"] += 1
        s["bars"] += len(b["bars"])
        s["priors"] += [r["features"]["rule_prior"] for r in b["bars"]]
    out = {}
    for label, s in sorted(by.items()):
        priors = s["priors"]
        out[label] = {"blocks": s["blocks"], "bars": s["bars"],
                      "mean_prior": round(sum(priors) / len(priors), 2),
                      "min": round(min(priors), 2), "max": round(max(priors), 2)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    blocks = build()
    summ = summary(blocks)
    if a.json:
        print(json.dumps(summ, indent=1))
        return
    print(f"wrote {os.path.relpath(OUT, ROOT)}  ({len(blocks)} blocks, "
          f"{sum(len(b['bars']) for b in blocks)} bars)\n")
    print(f"{'label':10} {'blocks':>6} {'bars':>5}  rule prior (mean / min / max)")
    for label, s in summ.items():
        print(f"{label:10} {s['blocks']:>6} {s['bars']:>5}  "
              f"{s['mean_prior']:>5} / {s['min']:>5} / {s['max']:>5}")
    print("\nstrong training rows = accept + reject; park is held out; weak_neg weights 0.4.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
