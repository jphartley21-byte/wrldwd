"""Single place for paths and switches. Nothing else in ww hard-codes a location.

Override with environment variables so a non-Joe checkout (or a test) never touches Joe's files:
  WW_ROOT              repo root (default: parent of this package)
  WW_PRIVATE_ORIGINAL  the original's lines; lives OUTSIDE the repo and is read by ww.calib only
  WW_EVAL_DIR          where gold sets, freeze manifests and failure logs live (default: <root>/eval)
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("WW_ROOT") or Path(__file__).resolve().parent.parent)
TOOLKIT = ROOT / "toolkit"
BENCHMARK = ROOT / "benchmark"
MATERIAL = ROOT / "material"
WRITING = ROOT / "writing"
EVAL_DIR = Path(os.environ.get("WW_EVAL_DIR") or ROOT / "eval")
FAILURES = EVAL_DIR / "failures.jsonl"
# Downloaded raw sources live OUTSIDE the repo (untrusted-download rule); only derived rows with provenance are stored in eval/.
DOWNLOADS = Path(os.environ.get("WW_DOWNLOADS") or Path.home() / "wrldwd_downloads")
PD_RAW = DOWNLOADS / "pd_verse" / "raw"
LEDGER_DIR = EVAL_DIR / "ledger"

# The original's lines. Rule 4: never copied into the repo, never logged, never in writer prompts.
# Same resolution as toolkit/private_path.py: the toolkit's folder is spelled Worldwide_private, ww's WORLDWIDE_PRIVATE;
# that is one folder on Windows and two on Linux/macOS, so take whichever exists (WORLDWIDE_PRIVATE first, as before).
PRIVATE_ORIGINAL = Path(
    os.environ.get("WW_PRIVATE_ORIGINAL")
    or next((p for p in (Path.home() / "Documents" / d / "original_lines.txt" for d in ("WORLDWIDE_PRIVATE", "Worldwide_private")) if p.exists()),
            Path.home() / "Documents" / "WORLDWIDE_PRIVATE" / "original_lines.txt")
)

# Packages whose versions are recorded in the freeze manifest (requirements.lock equivalent).
TRACKED_PACKAGES = (
    "cmudict", "g2p-en", "librosa", "nltk", "numpy", "scikit-learn", "wordfreq",
    "pronouncing", "requests", "anthropic", "spacy", "jiwer", "pytest",
)


def secret(name: str) -> str:
    """an API key from the process environment, else (Windows) the user-level environment, so a key set with `setx` works in an app
    session that started before it was set. Never printed, logged or written anywhere."""
    v = os.environ.get(name)
    if v:
        return v
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            val, _ = winreg.QueryValueEx(k, name)
            return str(val or "")
    except Exception:  # noqa: BLE001 - not Windows, or not set
        return ""
