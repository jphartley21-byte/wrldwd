"""Copy photos and videos from the Seagate HFS+ volume to C:\\Seagate (READ-ONLY on the drive).

Run from an elevated PowerShell:   python C:\\Users\\Joe\\Desktop\\seagate_probe\\hfs_copy.py
Needs hfs_io.py and drive_catalog.csv next to this file. The drive is only ever read.
Folder layout is mirrored under DEST. Files are written as .part and renamed when the size matches the catalogue,
so a stopped run can be started again and will skip finished files.

Default: skips the Movies folder (70 GB) and the Time Machine pictures; stops if C: free space would drop below --min-free-gb.
  --movies      include the Movies folder
  --tm          include the Time Machine pictures (names with odd characters may fail)
  --dry-run     list what would be copied, touch nothing (no admin needed)
"""
import argparse
import calendar
import csv
import os
import re
import shutil
import sys
import time
import traceback
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "drive_catalog.csv")
CHUNK = 4 * 1024 * 1024

ap = argparse.ArgumentParser()
ap.add_argument("--dest", default=r"C:\Seagate")
ap.add_argument("--movies", action="store_true")
ap.add_argument("--tm", action="store_true")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--min-free-gb", type=float, default=30.0)
args = ap.parse_args()

DEST = args.dest
LOG = os.path.join(DEST, "copy_log.txt")


def log(msg):
    line = msg if msg.endswith("\n") else msg + "\n"
    if not args.dry_run:
        os.makedirs(DEST, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line)
    print(line, end="", flush=True)


def clean(part):
    part = re.sub(r'[<>:"|?*\x00-\x1f]', "_", part).rstrip(" .")
    return part or "_"


def long(path):
    path = os.path.abspath(path)
    return path if path.startswith("\\\\?\\") else "\\\\?\\" + path


def parse_time(s):
    try:
        return calendar.timegm(datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S").timetuple())
    except Exception:
        return None


rows = list(csv.DictReader(open(CATALOG, encoding="utf-8-sig")))
plan = []
for r in rows:
    root = r["root"]
    if root == "Movies" and not args.movies:
        continue
    if root.startswith("TM ") and not args.tm:
        continue
    plan.append(r)
total = sum(int(r["size"]) for r in plan)
print(f"{len(plan)} files, {total / 1e9:.1f} GB planned (of {len(rows)} catalogued). Destination {DEST}")
free = shutil.disk_usage("C:\\").free
print(f"C: free {free / 1e9:.1f} GB; will stop if free space falls below {args.min_free_gb} GB")
if total > free - args.min_free_gb * 1e9:
    print("NOTE: the plan is bigger than the space allowed; the run will stop early at the free-space limit.")
if args.dry_run:
    sys.exit(0)

T0 = time.time()
done = skipped = failed = 0
copied = 0
try:
    from hfs_io import attr, open_volume
    log(f"=== copy run {time.strftime('%Y-%m-%d %H:%M:%S')}: {len(plan)} files, {total / 1e9:.1f} GB planned")
    pyfshfs, vol, raw = open_volume()
    stopped = False
    for i, r in enumerate(plan):
        size = int(r["size"])
        rel = [clean(p) for p in r["path"].split("/")]
        dest = os.path.join(DEST, *rel)
        try:
            if os.path.exists(long(dest)) and os.path.getsize(long(dest)) == size:
                skipped += 1
                continue
            if shutil.disk_usage("C:\\").free - size < args.min_free_gb * 1e9:
                log(f"STOP: free space would drop below {args.min_free_gb} GB at file {i + 1}/{len(plan)}")
                stopped = True
                break
            entry = vol.get_file_entry_by_path("/" + r["path"])
            if entry is None:
                raise FileNotFoundError(r["path"])
            real = int(attr(entry, "size") or 0)
            if real != size:
                raise ValueError(f"size differs: catalogue {size}, volume {real}")
            os.makedirs(long(os.path.dirname(dest)), exist_ok=True)
            tmp = long(dest + ".part")
            off = 0
            with open(tmp, "wb") as out:
                while off < size:
                    data = entry.read_buffer_at_offset(min(CHUNK, size - off), off)
                    if not data:
                        raise IOError(f"short read at {off}")
                    out.write(data)
                    off += len(data)
            if os.path.getsize(tmp) != size:
                raise IOError("written size mismatch")
            os.replace(tmp, long(dest))
            t = parse_time(r["modified"])
            if t:
                os.utime(long(dest), (t, t))
            done += 1
            copied += size
        except Exception as e:
            failed += 1
            log(f"  FAILED {r['path'][-70:]}: {type(e).__name__}: {str(e)[:90]}")
        if (i + 1) % 100 == 0:
            log(f"  ... {i + 1}/{len(plan)}: {done} copied, {skipped} already there, {failed} failed, {copied / 1e9:.1f} GB, {int(time.time() - T0)} s")
    vol.close()
except Exception:
    log("FATAL\n" + traceback.format_exc())
log(f"=== finished: {done} copied ({copied / 1e9:.1f} GB), {skipped} already there, {failed} failed, {int(time.time() - T0)} s. Log: {LOG}")
