"""Read-only probe of the HFS+ partition: partition table, volume header, volume name, and a look at
the folder structure (names and counts only, two levels deep).
Run elevated. Writes hfs_probe.json and hfs_log.txt next to this file. Never writes to the disk.
"""
import os
import json
import struct
import traceback

from hfs_io import RawPartition, HERE, log, attr, open_volume

OUT = os.path.join(HERE, "hfs_probe.json")
open(os.path.join(HERE, "hfs_log.txt"), "w").close()      # fresh log each run
result = {"steps": []}


def step(label, **kw):
    result["steps"].append({"step": label, **kw})
    log(f"[{label}] {kw}")


def safe(label, fn):
    try:
        v = fn()
        step(label, value=v)
        return v
    except Exception:
        step(label + "_failed", error=traceback.format_exc())
        return None


def is_dir(mode):
    return isinstance(mode, int) and (mode & 0o170000) == 0o040000


def n_children(e):
    try:
        return e.number_of_sub_file_entries
    except Exception:
        return None


def info(e):
    mode = attr(e, "file_mode")
    return {"name": str(attr(e, "name")), "dir": is_dir(mode), "children": n_children(e), "size": attr(e, "size")}


# 0. partition table straight from the disk (read-only)
try:
    from gpt_check import read_gpt
    gpt = read_gpt()
    result["gpt_on_disk"] = gpt
    step("gpt_on_disk", entries=gpt)
except Exception:
    step("gpt_on_disk_failed", error=traceback.format_exc())

# 1. volume header signature and flags
try:
    raw = RawPartition()
    raw.seek(1024)
    vh = raw.read(512)
    attrs = struct.unpack(">I", vh[4:8])[0]
    step("volume_header", signature=vh[:2].decode("latin1"), version=struct.unpack(">H", vh[2:4])[0],
         attributes=hex(attrs), journaled=bool(attrs & (1 << 13)), unmounted_cleanly=bool(attrs & (1 << 8)),
         software_locked=bool(attrs & (1 << 15)))
    raw.close()
except Exception:
    step("volume_header_failed", error=traceback.format_exc())

# 2. open the volume with libfshfs and look around
try:
    pyfshfs, vol, rawp = open_volume()
    step("opened", pyfshfs_version=getattr(pyfshfs, "get_version", lambda: "?")())
    safe("volume_name", lambda: str(attr(vol, "name")))
    root = vol.get_root_directory()
    step("root", members=[m for m in dir(root) if not m.startswith("_") and not m.startswith("get_")][:40])

    top = []
    subs = {}
    for e in root.sub_file_entries:
        i = info(e)
        top.append(i)
        if i["dir"]:
            kids = []
            try:
                for k, c in enumerate(e.sub_file_entries):
                    if k >= 40:
                        kids.append({"name": "...more", "dir": None, "children": None, "size": None})
                        break
                    kids.append(info(c))
            except Exception as ex:
                kids.append({"error": repr(ex)})
            subs[i["name"]] = kids
    result["top_level"] = top
    result["second_level"] = subs
    step("top_level", count=len(top))
    for t in top[:300]:
        log(f"   {t}")
    for name, kids in list(subs.items())[:60]:
        log(f"   [{name}] -> " + ", ".join(str(k.get("name")) + ("/" if k.get("dir") else "") for k in kids))

    names = {str(t["name"]) for t in top}
    result["hints"] = {
        "time_machine": "Backups.backupdb" in names,
        "photos_library": any(n.lower().endswith(".photoslibrary") for n in names),
        "has_users_folder": "Users" in names,
    }
    step("hints", **result["hints"])
    vol.close()
    result["ok"] = True
except Exception:
    result["ok"] = False
    result["error"] = traceback.format_exc()
    log(result["error"])

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, indent=2, default=str)
log("probe finished")
