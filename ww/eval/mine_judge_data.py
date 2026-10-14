"""Mine the Claude-agent judge transcripts into a labelled dataset: (candidate bars, judge scores) per judge call.

Why: every judge call scored 3-8 candidate blocks on character / wordplay / sense / rhyme / flow / overall, after reading the original. Across the
rounds that is several hundred scored candidate-instances. Comparing a candidate with the others IN THE SAME CALL removes the judge's own scale,
so within-call rank correlation of any text feature with the 'flow' score is the cleanest validation available without a human.

  python -m ww.eval.mine_judge_data            -> eval/flow_dataset.jsonl
Each row: {wf, agent, slot, label, bars, scores{...}, n_in_call}. The original's text never appears (judges' replies are abstract; prompts hold OUR bars only).
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

BASE = os.path.expanduser(r"~\.claude\projects\C--Users-Joe-wrldwd\9051a56f-6441-4ed2-af43-297c1ef84980\subagents\workflows")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "eval", "flow_dataset.jsonl")


def _text(msg) -> str:
    c = msg.get("content")
    if isinstance(c, str):
        return c
    out = []
    for b in c or []:
        if isinstance(b, dict) and b.get("type") == "text":
            out.append(b.get("text", ""))
    return "\n".join(out)


def parse_prompt(p: str):
    m = re.search(r"reference block for ([^)]+)\)", p)
    if not m:
        return None
    slot = m.group(1).strip()
    i = p.find("CANDIDATES:")
    if i < 0:
        return None
    body = p[i + len("CANDIDATES:"):]
    blocks = re.split(r"\n\s*\n(?=\s*\[)", body.strip("\n"))
    cands = {}
    for b in blocks:
        lines = [l.strip() for l in b.strip().splitlines() if l.strip()]
        if not lines or not re.match(r"^\[[^\]]+\]$", lines[0]):
            continue
        label = lines[0][1:-1]
        bars = []
        for l in lines[1:]:
            if l.startswith("(the writer says") or l.startswith("(writer"):
                continue
            bars.append(re.sub(r"^\d+\.\s*", "", l))
        if bars:
            cands[label] = bars
    return slot, cands


def result_of(rows):
    for r in reversed(rows):
        if r.get("type") != "assistant":
            continue
        for b in (r.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "StructuredOutput":
                return b.get("input")
    return None


def mine() -> list[dict]:
    out = []
    for d in sorted(glob.glob(os.path.join(BASE, "wf_*"))):
        for f in glob.glob(os.path.join(d, "agent-*.jsonl")):
            try:
                rows = [json.loads(l) for l in open(f, encoding="utf-8", errors="replace")]
            except Exception:    # noqa: BLE001
                continue
            user = next((r for r in rows if r.get("type") == "user"), None)
            if not user:
                continue
            parsed = parse_prompt(_text(user.get("message") or {}))
            if not parsed:
                continue
            res = result_of(rows)
            if not res or "candidates" not in res:
                continue
            slot, cands = parsed
            n = len(res["candidates"])
            for c in res["candidates"]:
                lab = c.get("id")
                if lab in cands and c.get("scores"):
                    out.append({"wf": os.path.basename(d), "agent": os.path.basename(f)[6:-6], "slot": slot, "label": lab, "bars": cands[lab], "scores": c["scores"], "n_in_call": n})
    return out


def main() -> int:
    rows = mine()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(rows), "scored candidate-instances from", len({(r['wf'], r['agent']) for r in rows}), "judge calls ->", os.path.normpath(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
