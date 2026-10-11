"""Read ONE document ('Eurotrip Itinerary.docx') from the Time Machine home folders (READ ONLY) and
write only its plain text next to this file as eurotrip_itinerary.txt. Run elevated.
"""
import os
import re
import io
import html
import zipfile
import traceback

from hfs_io import HERE, attr, open_volume

LOG = os.path.join(HERE, "itinerary_log.txt")
OUT = os.path.join(HERE, "eurotrip_itinerary.txt")
TARGET = "Eurotrip Itinerary.docx"
SNAP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}$")
open(LOG, "w").close()


def log(msg):
    line = msg if msg.endswith("\n") else msg + "\n"
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line)
    print(line, end="", flush=True)


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


def read_all(entry, size):
    try:
        return entry.read_buffer_at_offset(size, 0)
    except Exception:
        entry.seek_offset(0, 0)
        return entry.read_buffer(size)


def docx_text(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    xml = z.read("word/document.xml").decode("utf-8", "ignore")
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        out.append(html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, flags=re.S))))
    return "\n".join(out)


done = False
try:
    pyfshfs, vol, raw = open_volume()
    root = vol.get_root_directory()
    bdb = find_child(root, "Backups.backupdb")
    log("backupdb found: %s" % (bdb is not None))
    for m in [c for c in children(bdb) if not str(attr(c, "name")).startswith(".")] if bdb else []:
        snaps = sorted([c for c in children(m) if SNAP_RE.match(str(attr(c, "name")))],
                       key=lambda c: str(attr(c, "name")))
        log("snapshots: %d" % len(snaps))
        for snap in (snaps[:1] + snaps[-1:]):
            for v in [c for c in children(snap) if not str(attr(c, "name")).startswith(".")]:
                users = find_child(v, "Users")
                if users is None:
                    continue
                for u in children(users):
                    f = find_child(u, TARGET)
                    if f is None:
                        continue
                    size = int(attr(f, "size") or 0)
                    log("found %s in snapshot %s: %d bytes" % (TARGET, attr(snap, "name"), size))
                    if 0 < size <= 8 * 1024 * 1024:
                        text = docx_text(read_all(f, size))
                        with open(OUT, "w", encoding="utf-8") as fh:
                            fh.write(text)
                        log("wrote eurotrip_itinerary.txt (%d characters)" % len(text))
                        done = True
                        break
                if done:
                    break
            if done:
                break
        if done:
            break
    if not done:
        log("document not found or unreadable")
    vol.close()
except Exception:
    log("FATAL\n" + traceback.format_exc())
log("itinerary step finished")
