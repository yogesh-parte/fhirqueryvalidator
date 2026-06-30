from __future__ import annotations

import threading
import time
from typing import Any

from ..config.settings import get_capability_cache_enabled, get_capability_cache_ttl_seconds

DEFAULT_CACHE_TTL_SECONDS = 86_400


def _cache_key(url: str, headers: dict[str, str] | None) -> str:
    if not headers:
        return url
    header_parts = [f"{key}={value}" for key, value in sorted(headers.items())]
    return f"{url}|{'|'.join(header_parts)}"


class CapabilityStatementCache:
    def __init__(self, ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS, enabled: bool = True):
        self._ttl_seconds = ttl_seconds
        self._enabled = enabled
        self._entries: dict[str, tuple[float, dict[str, Any]]] = {}
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any] | None:
        if not self._enabled:
            return None

        key = _cache_key(url, headers)
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None

            fetched_at, data = entry
            if time.monotonic() - fetched_at >= self._ttl_seconds:
                del self._entries[key]
                return None

            return data

    def set(self, url: str, data: dict[str, Any], headers: dict[str, str] | None = None) -> None:
        if not self._enabled:
            return

        key = _cache_key(url, headers)
        with self._lock:
            self._entries[key] = (time.monotonic(), data)

    def invalidate(self, url: str | None = None) -> int:
        with self._lock:
            if url is None:
                removed = len(self._entries)
                self._entries.clear()
                return removed

            prefix = f"{url}|"
            keys_to_remove = [key for key in self._entries if key == url or key.startswith(prefix)]
            for key in keys_to_remove:
                del self._entries[key]
            return len(keys_to_remove)


_default_cache: CapabilityStatementCache | None = None
_default_cache_lock = threading.Lock()


def get_capability_cache() -> CapabilityStatementCache:
    global _default_cache
    with _default_cache_lock:
        if _default_cache is None:
            _default_cache = CapabilityStatementCache(
                ttl_seconds=get_capability_cache_ttl_seconds(),
                enabled=get_capability_cache_enabled(),
            )
        return _default_cache


def invalidate_capability_cache(url: str | None = None) -> int:
    return get_capability_cache().invalidate(url)


def reset_capability_cache() -> None:
    global _default_cache
    with _default_cache_lock:
        _default_cache = None