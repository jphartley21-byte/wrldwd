"""Pure functions that read capture time and GPS from photo and video headers.

Nothing here touches the disk by itself: callers pass bytes or a reader(offset, size) function.
Photos: EXIF (JPEG, HEIC). Videos: QuickTime/MP4 'moov' atom (creation time, ISO 6709 location).
"""
import io
import re
import struct
import datetime

try:
    from PIL import Image
except Exception:                     # pragma: no cover
    Image = None
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:                     # pragma: no cover
    pillow_heif = None

EPOCH_1904 = datetime.datetime(1904, 1, 1)


def _deg(v, ref):
    try:
        d, m, s = [float(x) for x in v]
        out = d + m / 60.0 + s / 3600.0
        if ref in ("S", "W", b"S", b"W"):
            out = -out
        return round(out, 6)
    except Exception:
        return None


def parse_image(data):
    """Return dict(time, lat, lon, note) from JPEG/HEIC bytes (head of the file is enough for JPEG)."""
    out = {"time": "", "lat": "", "lon": "", "note": ""}
    if Image is None:
        out["note"] = "no PIL"
        return out
    try:
        img = Image.open(io.BytesIO(data))
        ex = img.getexif()
        exif_ifd = {}
        gps_ifd = {}
        try:
            exif_ifd = ex.get_ifd(0x8769)
        except Exception:
            pass
        try:
            gps_ifd = ex.get_ifd(0x8825)
        except Exception:
            pass
        t = exif_ifd.get(36867) or exif_ifd.get(36868) or ex.get(306) or ""
        out["time"] = str(t)
        if gps_ifd and gps_ifd.get(2) and gps_ifd.get(4):
            lat = _deg(gps_ifd.get(2), gps_ifd.get(1))
            lon = _deg(gps_ifd.get(4), gps_ifd.get(3))
            if lat is not None and lon is not None and not (lat == 0 and lon == 0):
                out["lat"], out["lon"] = lat, lon
    except Exception as e:                # truncated or unsupported files end up here
        out["note"] = "image parse failed: %s" % type(e).__name__
    return out


def find_moov(reader, size):
    """Walk top-level QuickTime/MP4 atoms with small header reads; return (offset, length) of moov payload."""
    pos, hops = 0, 0
    while pos + 8 <= size and hops < 200:
        hdr = reader(pos, 16)
        if len(hdr) < 8:
            return None
        asize = struct.unpack(">I", hdr[:4])[0]
        typ = hdr[4:8]
        hlen = 8
        if asize == 1 and len(hdr) >= 16:
            asize = struct.unpack(">Q", hdr[8:16])[0]
            hlen = 16
        elif asize == 0:
            asize = size - pos
        if typ == b"moov":
            return pos + hlen, asize - hlen
        if asize < 8:
            return None
        pos += asize
        hops += 1
    return None


ISO6709 = re.compile(rb"([+-]\d{1,2}\.\d{2,})([+-]\d{1,3}\.\d{2,})")
CREATIONDATE = re.compile(rb"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4})")


def parse_quicktime(reader, size, max_moov=24 * 1024 * 1024):
    out = {"time": "", "lat": "", "lon": "", "note": ""}
    try:
        loc = find_moov(reader, size)
        if not loc:
            out["note"] = "no moov"
            return out
        off, length = loc
        if length <= 0 or length > max_moov:
            out["note"] = "moov too large (%d)" % length
            return out
        moov = reader(off, length)
        i = moov.find(b"mvhd")
        if i >= 0:
            ver = moov[i + 4]
            if ver == 0:
                ct = struct.unpack(">I", moov[i + 8:i + 12])[0]
            else:
                ct = struct.unpack(">Q", moov[i + 8:i + 16])[0]
            if ct:
                out["time"] = (EPOCH_1904 + datetime.timedelta(seconds=ct)).strftime("%Y:%m:%d %H:%M:%S") + "Z"
        m = CREATIONDATE.search(moov)
        if m:
            out["time"] = m.group(1).decode("ascii")          # local time with offset, preferred
        g = ISO6709.search(moov)
        if g:
            lat, lon = float(g.group(1)), float(g.group(2))
            if not (lat == 0 and lon == 0):
                out["lat"], out["lon"] = round(lat, 6), round(lon, 6)
    except Exception as e:
        out["note"] = "quicktime parse failed: %s" % type(e).__name__
    return out
