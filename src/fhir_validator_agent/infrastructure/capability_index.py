import requests
from typing import Any

from .capability_cache import CapabilityStatementCache, get_capability_cache


def get_auth_headers(use_auth: bool, token_url: str, client_id: str, client_secret: str) -> dict[str, str]:
    if not use_auth:
        return {}

    if not all([token_url, client_id, client_secret]):
        raise RuntimeError("Missing OAuth configuration: TOKEN_URL, CLIENT_ID, CLIENT_SECRET")

    response = requests.post(
        token_url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=20,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("OAuth token response did not contain access_token")
    return {"Authorization": f"Bearer {token}"}


FHIR_JSON_HEADERS = {"Accept": "application/fhir+json"}


def load_capability_statement(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
    *,
    use_cache: bool | None = None,
    cache: CapabilityStatementCache | None = None,
) -> dict[str, Any]:
    cache_instance = cache or get_capability_cache()
    should_use_cache = cache_instance.enabled if use_cache is None else use_cache

    if should_use_cache:
        cached = cache_instance.get(url, headers)
        if cached is not None:
            return cached

    request_headers = {**FHIR_JSON_HEADERS, **(headers or {})}
    response = requests.get(url, headers=request_headers, timeout=timeout)
    response.raise_for_status()
    capability_statement = response.json()

    if should_use_cache:
        cache_instance.set(url, capability_statement, headers)

    return capability_statement