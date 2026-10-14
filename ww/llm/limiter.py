"""Adaptive concurrency limiter. DeepSeek ties the account's concurrent-request limit to the remaining balance (observed: 32 threads fine
at a few dollars, limit 6 at $0.27), and answers 429 'concurrency limit of N'. The limiter starts conservative and shrinks to N when told."""
from __future__ import annotations

import threading


class AdaptiveLimiter:
    def __init__(self, n: int = 8):
        self.n = max(1, n)
        self._active = 0
        self._cv = threading.Condition()

    def __enter__(self):
        with self._cv:
            while self._active >= self.n:
                self._cv.wait()
            self._active += 1
        return self

    def __exit__(self, *exc):
        with self._cv:
            self._active -= 1
            self._cv.notify_all()

    def shrink_to(self, n: int) -> None:
        with self._cv:
            self.n = max(1, min(self.n, n))

    def grow_to(self, n: int) -> None:
        with self._cv:
            self.n = max(self.n, n)
            self._cv.notify_all()
