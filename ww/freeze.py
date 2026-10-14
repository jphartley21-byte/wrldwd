"""Baseline freeze (plan P0b): a manifest of what the measuring instruments were when we started building on them.

No git commit is required (committing is Joe's call). The manifest holds SHA-256 hashes only - of the toolkit code, the
benchmark JSON/CSV, the test fixtures, and the private original (hash only: its text is never read here) - plus package
versions and the normalised output hash of toolkit/calibrate.py. `check` reports drift so a silent tool change cannot
masquerade as a quality change (rule R6).
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata

from . import config

FROZEN_GLOBS = (
    "toolkit/*.py", "toolkit/tests/*", "benchmark/original_profile.json", "benchmark/flow_template.json",
    "benchmark/original_map.csv", "ml/meaning_judge.py", "brief/suno_rap_rules.md",
)
MANIFEST = config.EVAL_DIR / "freeze.json"


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def package_versions() -> dict:
    out = {}
    for name in config.TRACKED_PACKAGES:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = None
    return out


def file_hashes() -> dict:
    out = {}
    for pattern in FROZEN_GLOBS:
        for p in sorted(config.ROOT.glob(pattern)):
            if p.is_file() and "__pycache__" not in p.parts:
                out[p.relative_to(config.ROOT).as_posix()] = sha256_file(p)
    return out


def run_calibrate() -> tuple[bool, str]:
    """run toolkit/calibrate.py against the private original; returns (passed, normalised stdout)."""
    if not config.PRIVATE_ORIGINAL.exists():
        return False, f"private original not found at {config.PRIVATE_ORIGINAL}"
    r = subprocess.run(
        [sys.executable, str(config.TOOLKIT / "calibrate.py"), str(config.PRIVATE_ORIGINAL)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(config.ROOT),
    )
    text = "\n".join(l.rstrip() for l in r.stdout.splitlines() if l.strip())
    return "CALIBRATION PASSED" in r.stdout, text


def build(with_calibrate: bool = True) -> dict:
    m = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": package_versions(),
        "files": file_hashes(),
        "private_original_sha256": sha256_file(config.PRIVATE_ORIGINAL) if config.PRIVATE_ORIGINAL.exists() else None,
    }
    if with_calibrate:
        passed, text = run_calibrate()
        m["calibrate"] = {"passed": passed, "output_sha256": sha256_text(text), "lines": text.count("\n") + 1}
    return m


def write(with_calibrate: bool = True) -> dict:
    config.EVAL_DIR.mkdir(parents=True, exist_ok=True)
    m = build(with_calibrate)
    MANIFEST.write_text(json.dumps(m, indent=2, sort_keys=True), encoding="utf-8")
    return m


def check(with_calibrate: bool = True) -> list[str]:
    """list of drift messages; empty means the instruments are exactly the frozen ones."""
    if not MANIFEST.exists():
        return [f"no freeze manifest at {MANIFEST}"]
    old = json.loads(MANIFEST.read_text(encoding="utf-8"))
    new = build(with_calibrate)
    drift = []
    for k in sorted(set(old["files"]) | set(new["files"])):
        if old["files"].get(k) != new["files"].get(k):
            kind = "added" if k not in old["files"] else "removed" if k not in new["files"] else "changed"
            drift.append(f"{kind}: {k}")
    if old.get("private_original_sha256") != new.get("private_original_sha256"):
        drift.append("private original changed or missing")
    for k in sorted(set(old["packages"]) | set(new["packages"])):
        if old["packages"].get(k) != new["packages"].get(k):
            drift.append(f"package {k}: {old['packages'].get(k)} -> {new['packages'].get(k)}")
    if with_calibrate and old.get("calibrate") != new.get("calibrate"):
        drift.append(f"calibrate: {old.get('calibrate')} -> {new.get('calibrate')}")
    return drift


def selftest() -> tuple[bool, str]:
    h = sha256_text("abc")
    ok = h.startswith("ba7816bf") and package_versions().get("numpy") is not None
    return ok, "sha256 and package versions work" if ok else "freeze primitives broken"
