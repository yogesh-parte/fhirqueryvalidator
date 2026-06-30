import pytest

from fhir_validator_agent.config import settings


def test_get_max_metadata_response_bytes_defaults_to_10mb(monkeypatch):
    monkeypatch.delenv("FHIR_MAX_METADATA_RESPONSE_BYTES", raising=False)
    assert settings.get_max_metadata_response_bytes() == 10 * 1024 * 1024


def test_get_max_metadata_response_bytes_reads_env(monkeypatch):
    monkeypatch.setenv("FHIR_MAX_METADATA_RESPONSE_BYTES", "5242880")
    assert settings.get_max_metadata_response_bytes() == 5_242_880


def test_get_max_metadata_response_bytes_rejects_invalid_value(monkeypatch):
    monkeypatch.setenv("FHIR_MAX_METADATA_RESPONSE_BYTES", "not-a-number")
    with pytest.raises(ValueError, match="FHIR_MAX_METADATA_RESPONSE_BYTES"):
        settings.get_max_metadata_response_bytes()


def test_get_outbound_rate_limit_config_defaults(monkeypatch):
    monkeypatch.delenv("FHIR_OUTBOUND_RATE_LIMIT_PER_HOST", raising=False)
    monkeypatch.delenv("FHIR_OUTBOUND_RATE_LIMIT_WINDOW_SECONDS", raising=False)
    assert settings.get_outbound_rate_limit_config() == (30, 60.0)


def test_get_outbound_rate_limit_config_reads_env(monkeypatch):
    monkeypatch.setenv("FHIR_OUTBOUND_RATE_LIMIT_PER_HOST", "10")
    monkeypatch.setenv("FHIR_OUTBOUND_RATE_LIMIT_WINDOW_SECONDS", "30")
    assert settings.get_outbound_rate_limit_config() == (10, 30.0)


def test_get_outbound_rate_limit_config_rejects_invalid_values(monkeypatch):
    monkeypatch.setenv("FHIR_OUTBOUND_RATE_LIMIT_PER_HOST", "bad")
    with pytest.raises(ValueError, match="FHIR_OUTBOUND_RATE_LIMIT_PER_HOST"):
        settings.get_outbound_rate_limit_config()