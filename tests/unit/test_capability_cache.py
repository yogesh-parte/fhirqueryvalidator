import time
from unittest.mock import patch

import pytest

from fhir_validator_agent.infrastructure.capability_cache import (
    CapabilityStatementCache,
    DEFAULT_CACHE_TTL_SECONDS,
    invalidate_capability_cache,
    reset_capability_cache,
)


@pytest.fixture(autouse=True)
def _reset_global_cache():
    reset_capability_cache()
    yield
    reset_capability_cache()


def test_default_ttl_is_24_hours():
    assert DEFAULT_CACHE_TTL_SECONDS == 86_400


def test_cache_returns_stored_value_within_ttl():
    cache = CapabilityStatementCache(ttl_seconds=3600)
    cap = {"resourceType": "CapabilityStatement", "id": "cached"}

    cache.set("https://example.com/metadata", cap)
    result = cache.get("https://example.com/metadata")

    assert result == cap


def test_cache_miss_returns_none():
    cache = CapabilityStatementCache()
    assert cache.get("https://example.com/metadata") is None


def test_cache_expires_after_ttl():
    cache = CapabilityStatementCache(ttl_seconds=10)
    cap = {"resourceType": "CapabilityStatement"}

    with patch("fhir_validator_agent.infrastructure.capability_cache.time.monotonic") as mock_mono:
        mock_mono.return_value = 100.0
        cache.set("https://example.com/metadata", cap)

        mock_mono.return_value = 109.0
        assert cache.get("https://example.com/metadata") == cap

        mock_mono.return_value = 110.0
        assert cache.get("https://example.com/metadata") is None


def test_cache_disabled_skips_storage_and_lookup():
    cache = CapabilityStatementCache(enabled=False)
    cap = {"resourceType": "CapabilityStatement"}

    cache.set("https://example.com/metadata", cap)

    assert cache.get("https://example.com/metadata") is None


def test_cache_key_does_not_store_raw_bearer_token():
    cache = CapabilityStatementCache()
    cache.set(
        "https://example.com/metadata",
        {"id": "cached"},
        headers={"Authorization": "Bearer super-secret-token"},
    )

    stored_keys = list(cache._entries.keys())
    assert len(stored_keys) == 1
    assert "super-secret-token" not in stored_keys[0]


def test_cache_key_includes_auth_headers():
    cache = CapabilityStatementCache()
    cap_a = {"resourceType": "CapabilityStatement", "auth": "a"}
    cap_b = {"resourceType": "CapabilityStatement", "auth": "b"}

    cache.set("https://example.com/metadata", cap_a, headers={"Authorization": "Bearer a"})
    cache.set("https://example.com/metadata", cap_b, headers={"Authorization": "Bearer b"})

    assert cache.get("https://example.com/metadata", headers={"Authorization": "Bearer a"}) == cap_a
    assert cache.get("https://example.com/metadata", headers={"Authorization": "Bearer b"}) == cap_b


def test_invalidate_specific_url_removes_all_header_variants():
    cache = CapabilityStatementCache()
    cache.set("https://a.example/metadata", {"id": "a"})
    cache.set("https://b.example/metadata", {"id": "b"})
    cache.set(
        "https://a.example/metadata",
        {"id": "a-auth"},
        headers={"Authorization": "Bearer token"},
    )

    removed = cache.invalidate("https://a.example/metadata")

    assert removed == 2
    assert cache.get("https://a.example/metadata") is None
    assert cache.get("https://b.example/metadata") == {"id": "b"}


def test_invalidate_all_clears_every_entry():
    cache = CapabilityStatementCache()
    cache.set("https://a.example/metadata", {"id": "a"})
    cache.set("https://b.example/metadata", {"id": "b"})

    removed = cache.invalidate()

    assert removed == 2
    assert cache.get("https://a.example/metadata") is None
    assert cache.get("https://b.example/metadata") is None


def test_invalidate_capability_cache_uses_global_cache():
    cache = CapabilityStatementCache()
    with patch(
        "fhir_validator_agent.infrastructure.capability_cache.get_capability_cache",
        return_value=cache,
    ):
        cache.set("https://example.com/metadata", {"id": "cached"})
        removed = invalidate_capability_cache("https://example.com/metadata")

    assert removed == 1
    assert cache.get("https://example.com/metadata") is None