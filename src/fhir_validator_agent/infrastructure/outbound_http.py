from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Any

import requests

from .rate_limit import get_outbound_rate_limiter
from .security_audit import (
    log_outbound_blocked,
    log_outbound_failure,
    log_outbound_rate_limited,
    log_outbound_success,
)
from .url_validation import select_pinned_address

_connection_patch_lock = threading.Lock()


@contextmanager
def _pinned_connection(hostname: str, pinned_ip: str):
    import urllib3.util.connection as urllib3_connection

    original_create_connection = urllib3_connection.create_connection

    def patched_create_connection(address, *args, **kwargs):
        host, port = address
        if host == hostname:
            return original_create_connection((pinned_ip, port), *args, **kwargs)
        return original_create_connection(address, *args, **kwargs)

    with _connection_patch_lock:
        urllib3_connection.create_connection = patched_create_connection
        try:
            yield
        finally:
            urllib3_connection.create_connection = original_create_connection


def outbound_get(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
    request_kind: str = "metadata",
) -> requests.Response:
    try:
        hostname, pinned_ip = select_pinned_address(url)
    except ValueError as exc:
        log_outbound_blocked(url, str(exc))
        raise

    limiter = get_outbound_rate_limiter()
    try:
        limiter.acquire(url)
    except ValueError:
        log_outbound_rate_limited(url)
        raise

    try:
        with _pinned_connection(hostname, pinned_ip):
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=False,
            )
        log_outbound_success(url, request_kind)
        return response
    except requests.RequestException as exc:
        log_outbound_failure(url, request_kind, str(exc))
        raise


def outbound_post(
    url: str,
    *,
    data: dict[str, Any] | None = None,
    auth: tuple[str, str] | None = None,
    timeout: int = 20,
    request_kind: str = "oauth_token",
) -> requests.Response:
    try:
        hostname, pinned_ip = select_pinned_address(url)
    except ValueError as exc:
        log_outbound_blocked(url, str(exc))
        raise

    limiter = get_outbound_rate_limiter()
    try:
        limiter.acquire(url)
    except ValueError:
        log_outbound_rate_limited(url)
        raise

    try:
        with _pinned_connection(hostname, pinned_ip):
            response = requests.post(
                url,
                data=data,
                auth=auth,
                timeout=timeout,
                allow_redirects=False,
            )
        log_outbound_success(url, request_kind)
        return response
    except requests.RequestException as exc:
        log_outbound_failure(url, request_kind, str(exc))
        raise