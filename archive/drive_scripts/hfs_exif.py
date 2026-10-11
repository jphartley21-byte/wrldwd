"""Read capture time and GPS from the headers of photos and videos on the HFS+ drive (READ ONLY).

Run elevated, after hfs_catalog.py (needs drive_catalog.csv next to this file).
Reads only: the first 256 KB of JPEGs, whole small HEICs, and the 'moov' header atom of videos.
Skips: Photos-Library thumbnail derivatives, PNG/GIF, documents, and everything not in the catalogue.
Also lists (names only) any 'Pics' folder in the Time Machine home folders and includes its media.
Outputs next to this file: exif_results.csv, exif_summary.json, exif_log.txt
"""
import os
import csv
import json
import time
import traceback
import collections

from hfs_io import HERE, attr, open_volume
import media_meta

CAT = os.path.join(HERE, "drive_catalog.csv")
OUT = os.path.join(HERE, "exif_results.csv")
SUM = os.path.join(HERE, "exif_summary.json")
LOG = os.path.join(HERE, "exif_log.txt")
open(LOG, "w").close()

JPEG = {".jpg", ".jpeg"}
HEIC = {".heic"}
VIDEO = {".mov", ".mp4", ".m4v", ".3gp"}
MEDIA = JPEG | HEIC | VIDEO | {".png", ".gif", ".tif", ".tiff", ".bmp", ".avi", ".mts", ".m2ts", ".mpg", ".mpeg",
                                ".mkv", ".wmv", ".dng", ".cr2", ".nef", ".arw"}
JPEG_HEAD = 256 * 1024
HEIC_MAX = 12 * 1024 * 1024
TIME_LIMIT = 90 * 60
T0 = time.time()


def log(msg):
    line = msg if msg.endswith("\n") else msg + "\n"
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line)
    print(line, end="", flush=True)


def is_dir(mode):
    return isinstance(mode, int) and (mode & 0o170000) == 0o040000


def children(e):
    try:
        return list(e.sub_file_entries)
    except Exception:
        return []


def find_child(e, name):
    for c in children(e):
        if str(attr(c, "name")) == name:
            return c
    return None


def reader_for(entry):
    def read(offset, size):
        try:
            return entry.read_buffer_at_offset(size, offset)
        except Exception:
            entry.seek_offset(offset, 0)
            return entry.read_buffer(size)
    return read


def docx_text(data):
    import io
    import re
    import html
    import zipfile
    z = zipfile.ZipFile(io.BytesIO(data))
    xml = z.read("word/document.xml").decode("utf-8", "ignore")
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        out.append(html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, flags=re.S))))
    return "\n".join(out)


def extract_itinerary(vol, root, target="Eurotrip Itinerary.docx"):
    """Read ONE named document from the Time Machine home folders and write only its plain text."""
    import re
    snap_re = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}$")
    bdb = find_child(root, "Backups.backupdb")
    if bdb is None:
        log("itinerary: no Backups.backupdb")
        return
    for m in [c for c in children(bdb) if not str(attr(c, "name")).startswith(".")]:
        snaps = sorted([c for c in children(m) if snap_re.match(str(attr(c, "name")))],
                       key=lambda c: str(attr(c, "name")))
        for snap in (snaps[:1] + snaps[-1:]):
            for v in [c for c in children(snap) if not str(attr(c, "name")).startswith(".")]:
                users = find_child(v, "Users")
                if users is None:
                    continue
                for u in children(users):
                    f = find_child(u, target)
                    if f is None:
                        continue
                    size = int(attr(f, "size") or 0)
                    log(f"itinerary: found {target} in snapshot {attr(snap, 'name')}: {size} bytes")
                    if size <= 0 or size > 8 * 1024 * 1024:
                        log("itinerary: unexpected size, skipped")
                        continue
                    text = docx_text(reader_for(f)(0, size))
                    with open(os.path.join(HERE, "eurotrip_itinerary.txt"), "w", encoding="utf-8") as fh:
                        fh.write(text)
                    log(f"itinerary: wrote eurotrip_itinerary.txt ({len(text)} characters)")
                    return
    log("itinerary: document not found")


def candidates_from_catalog():
    rows = list(csv.DictReader(open(CAT, encoding="utf-8-sig")))
    loose_names = {r["name"] for r in rows if not r["root"].startswith("TM ")}
    out = []
    for r in rows:
        path, ext = r["path"], r["ext"].lower()
        if "/resources/" in path:                       # Photos-Library derivatives (thumbnails, proxies)
            continue
        if ext not in JPEG | HEIC | VIDEO:
            continue
        if r["root"].startswith("TM ") and r["name"] in loose_names:      # duplicate of a loose copy
            continue
        out.append({"root": r["root"], "path": path, "name": r["name"], "ext": ext,
                    "size": int(r["size"] or 0), "modified": r["modified"]})
    return out


def tm_pics_candidates(vol, root):
    """Names-only walk of 'Pics' in the oldest and newest Time Machine snapshot home folders."""
    import re
    snap_re = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}$")
    found = []
    bdb = find_child(root, "Backups.backupdb")
    if bdb is None:
        return found
    for m in [c for c in children(bdb) if not str(attr(c, "name")).startswith(".")]:
        mname = str(attr(m, "name"))
        snaps = sorted([c for c in children(m) if snap_re.match(str(attr(c, "name")))],
                       key=lambda c: str(attr(c, "name")))
        picks = ([snaps[0]] + ([snaps[-1]] if len(snaps) > 1 else [])) if snaps else []
        for snap in picks:
            sname = str(attr(snap, "name"))
            for v in [c for c in children(snap) if not str(attr(c, "name")).startswith(".")]:
                vname = str(attr(v, "name"))
                users = find_child(v, "Users")
                if users is None:
                    continue
                for u in children(users):
                    uname = str(attr(u, "name"))
                    if uname.startswith(".") or uname in ("Shared", "Guest"):
                        continue
                    pics = find_child(u, "Pics")
                    if pics is None:
                        continue
                    base = f"Backups.backupdb/{mname}/{sname}/{vname}/Users/{uname}/Pics"
                    stack, seen = [(base, pics)], set()
                    while stack:
                        prefix, d = stack.pop()
                        ident = attr(d, "identifier")
                        if ident in seen:
                            continue
                        seen.add(ident)
                        for c in children(d):
                            nm = str(attr(c, "name"))
                            p = f"{prefix}/{nm}"
                            if is_dir(attr(c, "file_mode")):
                                stack.append((p, c))
                            else:
                                ext = os.path.splitext(nm)[1].lower()
                                if ext in JPEG | HEIC | VIDEO:
                                    found.append({"root": f"TM Pics {sname[:10]}", "path": p, "name": nm, "ext": ext,
                                                  "size": int(attr(c, "size") or 0), "modified": str(attr(c, "modification_time") or "")})
                    log(f"TM Pics in {sname} / {uname}: {len(found)} media files so far")
    return found


counts = collections.Counter()
gps_counts = collections.Counter()
try:
    pyfshfs, vol, raw = open_volume()
    root = vol.get_root_directory()
    cands = candidates_from_catalog()
    log(f"candidates from catalogue: {len(cands)}")
    try:
        extra = tm_pics_candidates(vol, root)
    except Exception:
        extra = []
        log("TM Pics discovery failed:\n" + traceback.format_exc())
    log(f"candidates from TM Pics: {len(extra)}")
    cands += extra
    seen_keys = set()
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["root", "path", "name", "ext", "size", "exif_time", "lat", "lon", "note", "catalog_modified"])
        for i, c in enumerate(cands):
            if time.time() - T0 > TIME_LIMIT:
                log("time limit reached")
                break
            key = (c["name"], c["size"], c["modified"][:10])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            meta = {"time": "", "lat": "", "lon": "", "note": ""}
            try:
                entry = vol.get_file_entry_by_path("/" + c["path"])
                if entry is None:
                    meta["note"] = "path not found"
                else:
                    rd = reader_for(entry)
                    size = int(attr(entry, "size") or 0)
                    if c["ext"] in JPEG:
                        meta = media_meta.parse_image(rd(0, min(JPEG_HEAD, size)))
                    elif c["ext"] in HEIC:
                        if size <= HEIC_MAX:
                            meta = media_meta.parse_image(rd(0, size))
                        else:
                            meta["note"] = "heic too large"
                    else:
                        meta = media_meta.parse_quicktime(rd, size)
            except Exception as e:
                meta["note"] = "read failed: %s" % type(e).__name__
            w.writerow([c["root"], c["path"], c["name"], c["ext"], c["size"], meta["time"], meta["lat"], meta["lon"],
                        meta["note"], c["modified"]])
            counts[c["root"]] += 1
            if meta["lat"] != "":
                gps_counts[c["root"]] += 1
            if (i + 1) % 250 == 0:
                fh.flush()
                log(f"  ... {i + 1}/{len(cands)} files read, GPS found in {sum(gps_counts.values())} ({int(time.time() - T0)} s)")
    try:
        extract_itinerary(vol, root)
    except Exception:
        log("itinerary extraction failed:\n" + traceback.format_exc())
    vol.close()
except Exception:
    log("FATAL\n" + traceback.format_exc())

summary = {"files_read": dict(counts), "with_gps": dict(gps_counts), "elapsed_s": int(time.time() - T0)}
with open(SUM, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2)
log(f"exif pass finished: {sum(counts.values())} files, {sum(gps_counts.values())} with GPS, {summary['elapsed_s']} s")
