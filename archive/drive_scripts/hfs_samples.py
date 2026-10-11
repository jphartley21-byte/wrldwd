"""Save small preview images (max 900 px) of selected photos and video frames from the HFS+ drive.

Run elevated. READ-ONLY on the drive. Needs sample_plan.csv, frames.py and media_meta.py next to this file.
Writes previews to the 'samples' folder next to this file, plus samples_index.csv and samples_log.txt.
"""
import os
import re
import io
import csv
import time
import traceback

from PIL import Image, ImageOps

from hfs_io import HERE, attr, open_volume
import media_meta                              # registers the HEIC opener
from frames import EntryIO, grab_frames

PLAN = os.path.join(HERE, "sample_plan.csv")
OUTDIR = os.path.join(HERE, "samples")
INDEX = os.path.join(HERE, "samples_index.csv")
LOG = os.path.join(HERE, "samples_log.txt")
open(LOG, "w").close()
os.makedirs(OUTDIR, exist_ok=True)
IMAGE = {".jpg", ".jpeg", ".heic", ".png"}
MAX_IMG_BYTES = 30 * 1024 * 1024


def log(msg):
    line = msg if msg.endswith("\n") else msg + "\n"
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line)
    print(line, end="", flush=True)


def slug(s, n=40):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:n] or "x"


def save(img, name):
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((900, 900))
    img.save(os.path.join(OUTDIR, name), "JPEG", quality=72)


T0 = time.time()
done = failed = 0
try:
    plan = list(csv.DictReader(open(PLAN, encoding="utf-8-sig")))
    log(f"{len(plan)} files planned")
    pyfshfs, vol, raw = open_volume()
    with open(INDEX, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sample", "label", "date", "path"])
        for i, p in enumerate(plan):
            try:
                entry = vol.get_file_entry_by_path("/" + p["path"])
                if entry is None:
                    raise FileNotFoundError(p["path"])
                size = int(attr(entry, "size") or 0)
                base = f"{i:03d}_{slug(p['label'], 28)}_{slug(p['date'], 10)}_{slug(os.path.basename(p['path']), 24)}"
                if p["ext"] in IMAGE:
                    if size > MAX_IMG_BYTES:
                        raise ValueError("image too large")
                    data = entry.read_buffer_at_offset(size, 0)
                    name = base + ".jpg"
                    save(Image.open(io.BytesIO(data)), name)
                    w.writerow([name, p["label"], p["date"], p["path"]])
                else:
                    fobj = io.BufferedReader(EntryIO(entry, size), buffer_size=1 << 20)
                    fr = (0.5,) if p["frames"] == "1" else (0.25, 0.7)
                    imgs = grab_frames(fobj, fractions=fr)
                    for k, img in enumerate(imgs):
                        name = f"{base}_f{k + 1}.jpg"
                        save(img, name)
                        w.writerow([name, p["label"], p["date"], p["path"]])
                done += 1
            except Exception as e:
                failed += 1
                log(f"  skipped {p['path'][-60:]}: {type(e).__name__}: {str(e)[:80]}")
            if (i + 1) % 10 == 0:
                fh.flush()
                log(f"  ... {i + 1}/{len(plan)} done ({int(time.time() - T0)} s), {failed} skipped")
    vol.close()
except Exception:
    log("FATAL\n" + traceback.format_exc())
log(f"samples finished: {done} files done, {failed} skipped, {int(time.time() - T0)} s")
