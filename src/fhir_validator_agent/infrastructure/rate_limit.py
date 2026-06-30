from __future__ import annotations

import threading
import time
from collections import deque
from urllib.parse import urlparse


class OutboundRateLimiter:
    def __init__(self, max_requests: int, window_seconds: float):
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def acquire(self, url: str) -> None:
        host = (urlparse(url).hostname or "").lower()
        if not host:
            raise ValueError("Outbound URL must include a hostname")

        now = time.monotonic()
        with self._lock:
            events = self._events.setdefault(host, deque())
            while events and now - events[0] >= self._window_seconds:
                events.popleft()
            if len(events) >= self._max_requests:
                raise ValueError(f"Outbound rate limit exceeded for host {host}")
            events.append(now)


_default_limiter: OutboundRateLimiter | None = None
_default_limiter_lock = threading.Lock()


def get_outbound_rate_limiter() -> OutboundRateLimiter:
    global _default_limiter
    with _default_limiter_lock:
        if _default_limiter is None:
            from ..config.settings import get_outbound_rate_limit_config

            max_requests, window_seconds = get_outbound_rate_limit_config()
            _default_limiter = OutboundRateLimiter(max_requests, window_seconds)
        return _default_limiter


def reset_outbound_rate_limiter() -> None:
    global _default_limiter
    with _default_limiter_lock:
        _default_limiter = None