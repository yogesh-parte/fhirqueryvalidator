from __future__ import annotations

import logging
from urllib.parse import urlparse

logger = logging.getLogger("fhir_validator_agent.security")


def _redact_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port_suffix = ""
    if parsed.port and not (parsed.scheme == "https" and parsed.port == 443):
        port_suffix = f":{parsed.port}"
    path = parsed.path or "/"
    return f"{parsed.scheme}://{host}{port_suffix}{path}"


def log_outbound_blocked(url: str, reason: str) -> None:
    logger.warning(
        "outbound_request_blocked url=%s reason=%s",
        _redact_url(url),
        reason,
    )


def log_outbound_rate_limited(url: str) -> None:
    logger.warning("outbound_request_rate_limited url=%s", _redact_url(url))


def log_outbound_failure(url: str, request_kind: str, error: str) -> None:
    logger.warning(
        "outbound_request_failed url=%s kind=%s error=%s",
        _redact_url(url),
        request_kind,
        error,
    )


def log_outbound_success(url: str, request_kind: str) -> None:
    logger.info(
        "outbound_request_success url=%s kind=%s",
        _redact_url(url),
        request_kind,
    )