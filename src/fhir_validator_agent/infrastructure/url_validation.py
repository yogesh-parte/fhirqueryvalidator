from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_OUTBOUND_SCHEMES = frozenset({"https"})
BLOCKED_HOSTNAMES = frozenset({
    "localhost",
    "127.0.0.1",
    "0.0.0.0",  # nosec B104 — blocked SSRF target, not a bind address
    "169.254.169.254",
    "::1",
})


def _validate_ip_address(host: str) -> None:
    ip = ipaddress.ip_address(host)
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
        raise ValueError(f"Outbound URL must not target private or reserved address: {host}")


def validate_outbound_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_OUTBOUND_SCHEMES:
        raise ValueError(f"Outbound URL must use HTTPS, got scheme {parsed.scheme!r}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Outbound URL must include a hostname")

    host = hostname.lower().strip("[]")
    if host in BLOCKED_HOSTNAMES or host.endswith(".internal"):
        raise ValueError(f"Outbound URL host is not allowed: {host}")

    try:
        ipaddress.ip_address(host)
    except ValueError:
        return

    _validate_ip_address(host)


def resolve_outbound_addresses(hostname: str, port: int) -> list[str]:
    host = hostname.lower().strip("[]")
    try:
        results = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve outbound URL host {host!r}") from exc

    addresses: list[str] = []
    seen: set[str] = set()
    for _, _, _, _, sockaddr in results:
        ip_str = sockaddr[0]
        if ip_str in seen:
            continue
        seen.add(ip_str)
        _validate_ip_address(ip_str)
        addresses.append(ip_str)

    if not addresses:
        raise ValueError(f"No public addresses resolved for host {host!r}")
    return addresses


def select_pinned_address(url: str) -> tuple[str, str]:
    validate_outbound_url(url)
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Outbound URL must include a hostname")

    host = hostname.lower().strip("[]")
    port = parsed.port or 443

    try:
        ipaddress.ip_address(host)
        pinned_ip = host
    except ValueError:
        pinned_ip = resolve_outbound_addresses(host, port)[0]

    return host, pinned_ip