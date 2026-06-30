from __future__ import annotations

from typing import Any

import requests

DEFAULT_MAX_RESPONSE_BYTES = 10 * 1024 * 1024


def read_json_response(response: requests.Response, max_bytes: int = DEFAULT_MAX_RESPONSE_BYTES) -> dict[str, Any]:
    body_size = len(response.content)
    if body_size > max_bytes:
        raise ValueError(
            f"Response body exceeds maximum size of {max_bytes} bytes (received {body_size} bytes)"
        )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Expected JSON object response")
    return payload