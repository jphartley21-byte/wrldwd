"""Grab a few still frames from a video through a file-like wrapper (works on HFS+ entries or normal files)."""
import io

import av


class EntryIO(io.RawIOBase):
    """Seekable read-only file object over an object exposing read_buffer_at_offset(size, offset)."""

    def __init__(self, entry, size):
        self.entry = entry
        self.size = size
        self.pos = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        if whence == 0:
            self.pos = off
        elif whence == 1:
            self.pos += off
        elif whence == 2:
            self.pos = self.size + off
        self.pos = max(0, min(self.pos, self.size))
        return self.pos

    def readinto(self, b):
        n = min(len(b), self.size - self.pos)
        if n <= 0:
            return 0
        data = self.entry.read_buffer_at_offset(n, self.pos)
        b[:len(data)] = data
        self.pos += len(data)
        return len(data)


def grab_frames(fileobj, fractions=(0.2, 0.5, 0.8), max_side=900):
    """Return a list of PIL images, one per requested fraction of the video's duration."""
    out = []
    with av.open(fileobj) as container:
        dur = container.duration            # microseconds (AV_TIME_BASE), may be None
        for f in fractions:
            if dur:
                container.seek(int(dur * f), backward=True, any_frame=False)
            for frame in container.decode(video=0):
                img = frame.to_image()
                img.thumbnail((max_side, max_side))
                out.append(img)
                break
    return out
