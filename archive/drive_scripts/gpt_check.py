"""Read the GPT partition table from a disk, READ ONLY, and report each partition's on-disk type GUID."""
import struct
import uuid

DEVICE = r"\\.\PhysicalDrive1"


def read_gpt(device=DEVICE, max_entries=16):
    with open(device, "rb", buffering=0) as dev:
        dev.seek(0)
        head = dev.read(4096 * 6)          # sector-aligned read: covers LBA 0 to 47
    hdr = head[512:512 + 92]
    if hdr[:8] != b"EFI PART":
        raise ValueError("no GPT signature at LBA 1: %r" % hdr[:8])
    entries_lba = struct.unpack("<Q", hdr[72:80])[0]
    n_entries = struct.unpack("<I", hdr[80:84])[0]
    entry_size = struct.unpack("<I", hdr[84:88])[0]
    out = []
    for i in range(min(n_entries, max_entries)):
        off = entries_lba * 512 + i * entry_size
        e = head[off:off + entry_size]
        if len(e) < 128 or e[:16] == b"\x00" * 16:
            continue
        out.append({
            "index": i + 1,
            "type_guid": str(uuid.UUID(bytes_le=e[:16])),
            "first_lba": struct.unpack("<Q", e[32:40])[0],
            "last_lba": struct.unpack("<Q", e[40:48])[0],
            "name": e[56:128].decode("utf-16le", "ignore").rstrip("\x00"),
        })
    return out
