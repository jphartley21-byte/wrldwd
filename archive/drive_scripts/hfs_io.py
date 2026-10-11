"""Read-only access to the HFS+ partition on the Seagate drive (needs an elevated process).

Opens \\\\.\\PhysicalDrive1 for READ ONLY, serves aligned reads for one partition, and exposes the
file-object interface that libfshfs (pyfshfs) expects. Nothing in this module writes to the disk.
"""
import os
import sys
import json
import traceback
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
DEVICE = r"\\.\PhysicalDrive1"
PART_OFFSET = 209735680          # Get-Partition -DiskNumber 1 -PartitionNumber 2
PART_SIZE = 999860912128
ALIGN = 4096                     # physical sector size of the drive
BLOCK = 1024 * 1024              # read-ahead block


class RawPartition:
    def __init__(self, device=DEVICE, offset=PART_OFFSET, size=PART_SIZE):
        self.f = open(device, "rb", buffering=0)   # read-only
        self.offset = offset
        self.size = size
        self.pos = 0
        self.cache = OrderedDict()
        self.reads = 0

    # file-object interface used by libyal bindings
    def get_size(self):
        return self.size

    def tell(self):
        return self.pos

    def seek(self, pos, whence=0):
        if whence == 0:
            self.pos = pos
        elif whence == 1:
            self.pos += pos
        elif whence == 2:
            self.pos = self.size + pos
        return self.pos

    def _block(self, index):
        blk = self.cache.get(index)
        if blk is not None:
            self.cache.move_to_end(index)
            return blk
        start = self.offset + index * BLOCK
        a_start = start - (start % ALIGN)
        skip = start - a_start
        length = ((BLOCK + skip + ALIGN - 1) // ALIGN) * ALIGN
        self.f.seek(a_start)
        data = self.f.read(length)[skip:skip + BLOCK]
        self.reads += 1
        self.cache[index] = data
        if len(self.cache) > 48:
            self.cache.popitem(last=False)
        return data

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        out = bytearray()
        pos = self.pos
        end = pos + n
        while pos < end:
            index = pos // BLOCK
            blk = self._block(index)
            inner = pos - index * BLOCK
            take = min(end - pos, BLOCK - inner)
            if inner >= len(blk):
                break
            out += blk[inner:inner + take]
            pos += take
            if len(blk) < BLOCK:
                break
        self.pos += len(out)
        return bytes(out)

    def close(self):
        self.f.close()


def log(msg, path=None):
    path = path or os.path.join(HERE, "hfs_log.txt")
    line = msg if msg.endswith("\n") else msg + "\n"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line)
    try:
        sys.stdout.write(line)
        sys.stdout.flush()
    except Exception:
        pass


def attr(obj, name, default=None):
    """Read a property or call a getter, whichever this pyfshfs version offers."""
    try:
        v = getattr(obj, name)
    except Exception:
        v = None
    if v is None:
        try:
            g = getattr(obj, "get_" + name)
            v = g() if callable(g) else g
        except Exception:
            v = default
    return v


def open_volume():
    import pyfshfs
    raw = RawPartition()
    vol = pyfshfs.volume()
    vol.open_file_object(raw)
    return pyfshfs, vol, raw
