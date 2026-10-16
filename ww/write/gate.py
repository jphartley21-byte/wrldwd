"""gate: ONE verdict for a draft, used everywhere (15 Oct 2026).

Joe: "Are these gates locked in so a naive writer would produce the same flow?" They were not: the checks only ran when the
writer chose to run them, the automated writer passed failing blocks on as best-effort results, "done" never required the slot
checker, and a gate switched off by an environment flag left only a quiet note. This module is the single verdict the
definition of done, the save hook (.claude/settings.json) and calibrate.py's naive-writer test all use.

Per section (a '== Slot' draft):
  ww/write/slotcheck.check, with the section's `#cash` lines: syllables (exact where the original was timed), end shape,
  the by-ear rhyme rules, stress before the rhyme, the per-bar flow par (toolkit/flow_par.py), weak runs, recount, the
  retired-bar guard, names, suffix ends, narrator, cashed idioms, and the sense read (DeepSeek, else Claude via the CLI).
On the whole file: toolkit/meaning_gate, phrase_audit and swagger, the character cap, and songcheck on a full song.
Exit 0 only when every hard check passes. Notes are printed per section (fix them or list them to Joe). A gate that is
switched off prints as "GATE OFF" at the top, never as a pass.

  python -m ww.cli gate FILE [--quiet]
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

from .. import config

TOOLKIT = config.ROOT / "toolkit"


def gates_off() -> list[str]:
    off = []
    if os.environ.get("WW_SENSE", "1") == "0":
        off.append("sense read (WW_SENSE=0)")
    elif _sense_unrunnable():
        off.append(f"sense read ({_sense_unrunnable()})")
    if os.environ.get("WW_RAPFIT_GATE", "1") == "0":
        off.append("stress-anchored rhyme rule (WW_RAPFIT_GATE=0)")
    if os.environ.get("WW_TEXTURE", "1") == "0":
        off.append("rhyme texture: internal, sandwich, multis (WW_TEXTURE=0)")
    if os.environ.get("WW_USSLANG", "1") == "0":
        off.append("US-only slang read (WW_USSLANG=0)")
    if os.environ.get("WW_RECOUNT", "1") == "0":
        off.append("recount (WW_RECOUNT=0)")
    if os.environ.get("WW_LEGACY_FLOW", "0") == "1":
        off.append("current flow rules replaced by the legacy ones (WW_LEGACY_FLOW=1)")
    return off


def _sense_unrunnable():
    """why the SELECTED sense reader cannot run, or None. 16 Oct 2026: with WW_SENSE_MODEL=haiku, no `claude` CLI on PATH and a
    DeepSeek key set, every bar came back unjudged and the verdict said PASS with no GATE OFF line (the old test asked whether ANY
    reader could run, not the one chosen)."""
    try:
        from . import sensecheck
        from ..llm import pricing
        m = sensecheck.model()
        prov = pricing.provider(m)
    except Exception as e:  # noqa: BLE001
        return f"the sense model could not be resolved: {str(e)[:60]}"
    if prov == "anthropic" and not shutil.which("claude") and not config.secret("ANTHROPIC_API_KEY"):
        return f"{m}: no `claude` CLI on PATH and no ANTHROPIC_API_KEY, the model read cannot run"
    if prov == "deepseek" and not config.secret("DEEPSEEK_API_KEY"):
        return f"{m}: no DEEPSEEK_API_KEY, the model read cannot run"
    return None


def _tool(name: str, path: str) -> str:
    r = subprocess.run([sys.executable, str(TOOLKIT / f"{name}.py"), path], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout + r.stderr


def run(path: str) -> dict:
    """{"ok", "off", "sections": {slot: {"hard", "notes"}}, "file": [hard issues across the file], "notes": int}"""
    sys.path.insert(0, str(TOOLKIT))
    import fitbar
    fitbar.use_ww()
    from . import slotcheck
    import characters
    D, C = fitbar.read_draft(path, with_cash=True)
    secs = {}
    for s in fitbar.SLOTS:
        if not D.get(s):
            continue
        r = slotcheck.check(s, D[s], cash=C.get(s) or [])
        notes = [x for x in slotcheck.report(r).splitlines() if x.startswith(("FLOW bar", "EAR bar"))] + \
                [x for x in r["notes"] if not x.startswith(("recount codes", "cadence"))]
        secs[s] = {"hard": r["hard"], "notes": notes}
    file_hard = []
    # END RHYMES ACROSS SECTION BREAKS (16 Oct 2026, Joe on the original's bars 46-52): where the original carries one ending over a section
    # break, ours must too (rapfit.boundary_hard; numbers in benchmark/rhyme_bar_targets.json)
    if os.environ.get("WW_RAPFIT_GATE", "1") != "0":
        from . import rapfit
        file_hard += rapfit.boundary_hard({s: D[s] for s in fitbar.SLOTS if D.get(s)})
        # MULTI-WORD RHYMES (16 Oct 2026, Joe): a song-level minimum, no maximum, cheap / shallow / repeated ones not counted
        if all(D.get(s) for s in fitbar.SLOTS):
            file_hard += rapfit.multiword_hard({s: D[s] for s in fitbar.SLOTS})
            import texture as _tx
            file_hard += _tx.unit_echo_hard({s: D.get(s) for s in fitbar.SLOTS})
    out = _tool("meaning_gate", path)
    if "MEANING GATE: PASS" not in out:
        file_hard.append("meaning gate: " + next((l.strip() for l in out.splitlines() if "MEANING GATE" in l), "no verdict"))
    out = _tool("phrase_audit", path)
    if "PHRASE AUDIT: PASS" not in out:
        file_hard.append("phrase audit: " + next((l.strip() for l in out.splitlines() if "PHRASE AUDIT" in l), "no verdict"))
    out = _tool("swagger", path)
    if "SWAGGER: PASS" not in out:
        file_hard.append("swagger: " + "; ".join(l.strip() for l in out.splitlines() if l.strip().startswith("x "))[:300])
    bars = [b for s in fitbar.SLOTS for b in D.get(s, [])]
    over = characters.over_cap(bars)
    if over:
        file_hard.append("characters over the cap of 2: " + "; ".join(over))
    if len(secs) >= 5:
        out = _tool("songcheck", path)
        if "SONGCHECK: PASS" not in out:
            file_hard.append("songcheck: " + "; ".join(l.strip()[3:] for l in out.splitlines() if l.strip().startswith("XX"))[:400])
    # QUALITY (15 Oct 2026, report-only): Claude's per-bar marks (first listen, rewind, clever, forced, in character) and the song's
    # character read, from the cache; `python -m ww.write.qualityread FILE` fills it. No axis is hard: none separated Joe's rejected bars
    # from the original's (benchmark/quality_par_<model>.json); an axis gates only once it agrees with Joe's marks (writing/quality_labels.md).
    quality = {}
    if os.environ.get("WW_QUALITY", "1") != "0":
        try:
            from . import qualityread
            quality = qualityread.notes(qualityread.read_file(path, cached_only=True))
            for s, lines in quality.items():
                if s in secs:
                    secs[s]["notes"] += lines
        except Exception as e:  # noqa: BLE001 - report-only: never fails the gate
            quality = {"_error": [str(e)[:80]]}
    # POINT READ (16 Oct 2026, report-only): bars a listener has to work out (ww/write/pointcheck.py), from the cache;
    # `python -m ww.write.pointcheck FILE` fills it. It missed the adoption bar (benchmark/point_validation_*.json: AUC 0.89, but no cut
    # passes 90% of the original and catches 85% of the bad bars, and a flag flips between runs on half the borderline bars), so it never
    # fails the gate: every flag is listed to Joe instead.
    point_unread = []
    if os.environ.get("WW_POINT", "1") != "0":
        try:
            from . import pointcheck
            for s in secs:
                fl = pointcheck.flags(D[s], cached_only=True)
                if fl is None:
                    point_unread.append(s)
                    continue
                secs[s]["notes"] += [f"POINT bar {n} [{sc_}/6]: {how[:140]}" for n, sc_, how in fl]
        except Exception as e:  # noqa: BLE001 - report-only
            point_unread = [f"error: {str(e)[:60]}"]
    n_hard = sum(len(v["hard"]) for v in secs.values()) + len(file_hard)
    off = gates_off()
    # a model read that was chosen but did not run (CLI not logged in, network) is a gate OFF, not a pass (16 Oct 2026)
    for kind, label in (("sense read unavailable", "sense read"), ("US slang read unavailable", "US-only slang read")):
        miss = [s for s, v in secs.items() if any(n.startswith(kind) for n in v["notes"])]
        if miss and not any(x.startswith(label) for x in off):
            why = next(n for n in secs[miss[0]]["notes"] if n.startswith(kind)).split(":", 1)[-1].strip()
            off.append(f"{label} did not run in {len(miss)} section(s) ({why[:60]})")
    return {"ok": n_hard == 0 and bool(secs), "off": off, "sections": secs, "file": file_hard, "hard": n_hard,
            "notes": sum(len(v["notes"]) for v in secs.values()), "quality": quality, "point_unread": point_unread}


def report(r: dict, quiet: bool = False) -> str:
    L = [f"GATE OFF: {x}" for x in r["off"]]
    for s, v in r["sections"].items():
        n = len(v["hard"])
        L.append(f"{s}: " + ("PASS" if not n else f"FAIL ({n} hard)"))
        L += [f"   x {h[:220]}" for h in v["hard"]]
        if not quiet:
            L += [f"   ~ {n[:200]}" for n in v["notes"]]
    L += [f"FILE x {h}" for h in r["file"]]
    q = r.get("quality", {})
    if not quiet:
        L += [f"SONG ~ {x}" for x in q.get("_song", [])]
    if q.get("_unread"):
        L.append(f"QUALITY not read for {q['_unread']}: run python -m ww.write.qualityread {'FILE'} (report-only)")
    if r.get("point_unread"):
        L.append(f"POINT READ not run for {r['point_unread']}: run python -m ww.write.pointcheck FILE (report-only; flags go to Joe)")
    if not r["sections"]:
        L.append("no '== Slot' sections found: nothing was checked")
    L.append(f"GATE: {'PASS' if r['ok'] else 'FAIL'} ({r['hard']} hard issues, {r['notes']} notes to fix or list to Joe)"
             + (f"; {len(r['off'])} gate(s) OFF" if r["off"] else ""))
    return "\n".join(L)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="ww gate")
    ap.add_argument("file")
    ap.add_argument("--quiet", action="store_true", help="hard issues only, no notes")
    a = ap.parse_args(argv)
    r = run(a.file)
    print(report(r, a.quiet))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
