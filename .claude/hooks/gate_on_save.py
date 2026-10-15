"""PostToolUse hook: after any Write/Edit of a draft under writing/ (*.md), run `ww gate` on it and hand the verdict back to
Claude (15 Oct 2026). A writer who never asks for the check still gets it after every save. It never blocks the save:
work in progress is allowed to fail; "done" is not (CLAUDE.md, Definition of done).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    path = (data.get("tool_input") or {}).get("file_path") or (data.get("tool_response") or {}).get("filePath") or ""
    path = os.path.abspath(path)
    writing = os.path.join(ROOT, "writing") + os.sep
    if not (path.startswith(writing) and path.endswith(".md") and os.path.exists(path)):
        return 0
    with open(path, encoding="utf-8", errors="replace") as f:
        if not any(l.startswith("== ") for l in f):
            return 0          # not a '== Slot' draft: nothing for the gate to check
    # NOT --quiet (15 Oct 2026): quiet counted the slotcheck notes and hid them, so "end-rhyme carpet 2/6, the original holds 6/6"
    # reached nobody and people / solid / wallet / sequel shipped. Notes are fixed or listed to Joe (rule 10); the writer must see them.
    r = subprocess.run([sys.executable, "-m", "ww.cli", "gate", path], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=110)
    verdict = (r.stdout + r.stderr).strip()[-12000:]
    rel = os.path.relpath(path, ROOT)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                      "additionalContext": f"ww gate {rel} (auto, on save):\n{verdict}"}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # a broken hook must never block saving
        print(json.dumps({"systemMessage": f"gate_on_save hook error: {e}"}))
        sys.exit(0)
