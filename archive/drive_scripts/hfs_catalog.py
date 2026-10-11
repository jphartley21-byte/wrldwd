"""Read-only catalogue of PHOTO and VIDEO files on the HFS+ drive (names, sizes, dates only).

Run elevated. Never writes to the disk, never opens non-media files, never reads file contents:
only the catalogue entries (name, size, creation and modification time) are recorded.

Scans: a fixed list of loose top-level folders, loose media files at the top level, and, inside the Time
Machine backup, the Pictures and Movies folders of the oldest and newest snapshots.
Outputs (next to this file): drive_catalog.csv, drive_catalog_summary.json, catalog_log.txt
"""
import os
import re
import csv
import json
import time
import traceback
import collections

from hfs_io import HERE, attr, open_volume

LOG = os.path.join(HERE, "catalog_log.txt")
CSV_OUT = os.path.join(HERE, "drive_catalog.csv")
SUM_OUT = os.path.join(HERE, "drive_catalog_summary.json")
open(LOG, "w").close()

MEDIA = {".jpg", ".jpeg", ".png", ".heic", ".gif", ".tif", ".tiff", ".bmp", ".dng", ".cr2", ".nef", ".arw",
         ".raf", ".orf", ".rw2", ".mov", ".mp4", ".m4v", ".avi", ".mts", ".m2ts", ".3gp", ".mpg", ".mpeg",
         ".mkv", ".wmv", ".aae"}
# Loose top-level folders to catalogue (everything else, e.g. documents and downloads, is ignored)
LOOSE_ROOTS = ["Australia 2017", "New Zealand 2015", "Movies", "Pictures", "iMovie Library.imovielibrary",
               "iMovie Theater.theater"]
SKIP_PREFIXES = (".Spotlight", ".fseventsd", ".Trashes", ".TemporaryItems", ".DocumentRevisions",
                 ".HFS+ Private", "␀␀␀␀HFS+ Private")
MAX_FILES = 600_000
TIME_LIMIT = 60 * 60          # seconds
T0 = time.time()
SNAP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}$")


def log(msg):
    line = msg if msg.endswith("\n") else msg + "\n"
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line)
    print(line, end="", flush=True)


def is_dir(mode):
    return isinstance(mode, int) and (mode & 0o170000) == 0o040000


def when(e, name):
    v = attr(e, name)
    return str(v) if v is not None else ""


def children(entry):
    try:
        return list(entry.sub_file_entries)
    except Exception:
        return []


def find_child(entry, name):
    for c in children(entry):
        if str(attr(c, "name")) == name:
            return c
    return None


writer = None
rows_written = 0
counts = collections.Counter()
by_root = collections.Counter()
by_ext = collections.Counter()
by_ym = collections.defaultdict(collections.Counter)
errors = 0
visited_dirs = set()
tm_notes = {}


def emit(root_label, rel_path, e):
    global rows_written
    name = str(attr(e, "name"))
    ext = os.path.splitext(name)[1].lower()
    size = attr(e, "size")
    created = when(e, "creation_time")
    modified = when(e, "modification_time")
    writer.writerow([root_label, rel_path, name, ext, size, created, modified, attr(e, "identifier"),
                     attr(e, "link_identifier")])
    rows_written += 1
    by_root[root_label] += 1
    by_ext[ext] += 1
    ym = modified[:7] if modified else "unknown"
    by_ym[root_label][ym] += 1
    if rows_written % 5000 == 0:
        log(f"  ... {rows_written} media files catalogued ({int(time.time() - T0)} s)")


def walk(root_label, rel, entry):
    """Iterative walk of one directory tree, emitting media files only."""
    global errors
    stack = [(rel, entry)]
    while stack:
        if rows_written >= MAX_FILES or time.time() - T0 > TIME_LIMIT:
            log("limit reached, stopping this walk")
            return
        prefix, d = stack.pop()
        ident = attr(d, "identifier")
        if ident in visited_dirs:
            continue
        visited_dirs.add(ident)
        try:
            kids = list(d.sub_file_entries)
        except Exception:
            errors += 1
            continue
        for c in kids:
            try:
                name = str(attr(c, "name"))
                if name.startswith(SKIP_PREFIXES):
                    continue
                mode = attr(c, "file_mode")
                path = f"{prefix}/{name}" if prefix else name
                if is_dir(mode):
                    stack.append((path, c))
                else:
                    if os.path.splitext(name)[1].lower() in MEDIA and not name.startswith("._"):
                        emit(root_label, path, c)
            except Exception:
                errors += 1


try:
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["root", "path", "name", "ext", "size", "created", "modified", "identifier", "link_id"])
        pyfshfs, vol, raw = open_volume()
        log("opened volume: " + str(attr(vol, "name")))
        root = vol.get_root_directory()
        top = children(root)

        # 1. loose top-level media files and the fixed loose folders
        for e in top:
            name = str(attr(e, "name"))
            mode = attr(e, "file_mode")
            if not is_dir(mode) and os.path.splitext(name)[1].lower() in MEDIA:
                emit("(top-level files)", name, e)
        for rn in LOOSE_ROOTS:
            e = find_child(root, rn)
            if e is None:
                log(f"missing loose root: {rn}")
                continue
            log(f"cataloguing {rn} ...")
            walk(rn, rn, e)
            log(f"  {rn}: {by_root[rn]} media files")

        # 2. Time Machine: structure first (names only), then Pictures and Movies of oldest and newest snapshot
        bdb = find_child(root, "Backups.backupdb")
        if bdb is not None:
            machines = [c for c in children(bdb) if not str(attr(c, "name")).startswith(".")]
            tm_notes["machines"] = [str(attr(m, "name")) for m in machines]
            log("Time Machine machines: " + repr(tm_notes["machines"]))
            for m in machines:
                mname = str(attr(m, "name"))
                snaps = sorted([c for c in children(m) if SNAP_RE.match(str(attr(c, "name")))],
                               key=lambda c: str(attr(c, "name")))
                tm_notes[mname] = {"snapshot_count": len(snaps),
                                   "first": str(attr(snaps[0], "name")) if snaps else None,
                                   "last": str(attr(snaps[-1], "name")) if snaps else None}
                log(f"{mname}: {len(snaps)} snapshots; first {tm_notes[mname]['first']} last {tm_notes[mname]['last']}")
                picks = []
                if snaps:
                    picks.append(snaps[0])
                    if len(snaps) > 1:
                        picks.append(snaps[-1])
                for snap in picks:
                    sname = str(attr(snap, "name"))
                    vols = [c for c in children(snap) if not str(attr(c, "name")).startswith(".")]
                    for v in vols:
                        vname = str(attr(v, "name"))
                        users = find_child(v, "Users")
                        log(f"  snapshot {sname} / {vname}: Users found = {users is not None}; "
                            f"entry is_dir={is_dir(attr(v, 'file_mode'))}")
                        if users is None:
                            log("    top-level names: " + ", ".join(str(attr(c, 'name')) for c in children(v)[:40]))
                            continue
                        for u in children(users):
                            uname = str(attr(u, "name"))
                            if uname.startswith(".") or uname in ("Shared", "Guest"):
                                continue
                            mode = attr(u, "file_mode")
                            log(f"    user {uname}: is_dir={is_dir(mode)} mode={oct(mode) if isinstance(mode, int) else mode} "
                                f"link_id={attr(u, 'link_identifier')} children={len(children(u))}")
                            log("      home top-level names: " + ", ".join(str(attr(c, 'name')) for c in children(u)[:40]))
                            for sub in ("Pictures", "Movies"):
                                s = find_child(u, sub)
                                if s is None:
                                    log(f"      {sub}: not found")
                                    continue
                                label = f"TM {sname[:10]} {uname}/{sub}"
                                walk(label, f"Backups.backupdb/{mname}/{sname}/{vname}/Users/{uname}/{sub}", s)
                                log(f"      {label}: {by_root[label]} media files")
        vol.close()
        log("done walking")
except Exception:
    log("FATAL\n" + traceback.format_exc())

summary = {
    "rows": rows_written,
    "errors": errors,
    "elapsed_s": int(time.time() - T0),
    "by_root": dict(by_root),
    "by_ext": dict(by_ext),
    "by_year_month": {k: dict(sorted(v.items())) for k, v in by_ym.items()},
    "time_machine": tm_notes,
}
with open(SUM_OUT, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2)
log(f"catalogue finished: {rows_written} media files, {errors} errors, {summary['elapsed_s']} s")
