import pytest

from fhir_validator_agent.config import settings


def test_get_capability_cache_ttl_seconds_defaults_to_24_hours(monkeypatch):
    monkeypatch.delenv("FHIR_CAPABILITY_CACHE_TTL_SECONDS", raising=False)
    assert settings.get_capability_cache_ttl_seconds() == 86_400


def test_get_capability_cache_enabled_defaults_to_true(monkeypatch):
    monkeypatch.delenv("FHIR_CAPABILITY_CACHE_ENABLED", raising=False)
    assert settings.get_capability_cache_enabled() is True


def test_get_capability_cache_ttl_seconds_reads_env(monkeypatch):
    monkeypatch.setenv("FHIR_CAPABILITY_CACHE_TTL_SECONDS", "120")
    assert settings.get_capability_cache_ttl_seconds() == 120


def test_get_capability_cache_enabled_reads_env(monkeypatch):
    monkeypatch.setenv("FHIR_CAPABILITY_CACHE_ENABLED", "false")
    assert settings.get_capability_cache_enabled() is False


def test_get_capability_cache_ttl_seconds_rejects_invalid_value(monkeypatch):
    monkeypatch.setenv("FHIR_CAPABILITY_CACHE_TTL_SECONDS", "not-a-number")
    with pytest.raises(ValueError, match="FHIR_CAPABILITY_CACHE_TTL_SECONDS"):
        settings.get_capability_cache_ttl_seconds()