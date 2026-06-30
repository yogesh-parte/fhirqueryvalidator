from unittest.mock import MagicMock, patch

import pytest

from fhir_validator_agent.infrastructure.capability_cache import reset_capability_cache
from fhir_validator_agent.services.validator_service import FhirValidatorService


@pytest.fixture(autouse=True)
def _reset_global_capability_cache():
    reset_capability_cache()
    yield
    reset_capability_cache()


@pytest.fixture
def mocked_service(sample_capability_statement):
    with (
        patch("fhir_validator_agent.services.validator_service.load_capability_statement") as mock_load,
        patch("fhir_validator_agent.services.validator_service.get_auth_headers") as mock_auth,
    ):
        mock_auth.return_value = {}
        mock_load.return_value = sample_capability_statement
        service = FhirValidatorService(
            metadata_url="https://example.com/metadata",
            server_base="https://example.com",
        )
        yield service


def test_validate_query_valid(mocked_service):
    result = mocked_service.validate_query("https://example.com/Patient?gender=male")
    assert result == {"valid": True, "errors": []}


def test_validate_query_invalid_gender(mocked_service):
    result = mocked_service.validate_query("https://example.com/Patient?gender=fe")
    assert result["valid"] is False
    assert any("Patient.gender" in error for error in result["errors"])


def test_validate_query_unsupported_resource(mocked_service):
    result = mocked_service.validate_query("https://example.com/Unknown?foo=bar")
    assert result["valid"] is False
    assert "Unknown" in result["errors"][0]


def test_validate_query_unparseable_resource_type(mocked_service):
    result = mocked_service.validate_query("https://example.com/")
    assert result["valid"] is False
    assert "Unable to parse resource type" in result["errors"][0]


@patch("fhir_validator_agent.services.validator_service.get_auth_config")
@patch("fhir_validator_agent.services.validator_service.resolve_fhir_urls")
@patch("fhir_validator_agent.services.validator_service.load_env_file")
@patch("fhir_validator_agent.services.validator_service.load_capability_statement")
@patch("fhir_validator_agent.services.validator_service.get_auth_headers")
def test_from_env(
    mock_auth,
    mock_load,
    mock_load_env,
    mock_resolve,
    mock_auth_config,
    sample_capability_statement,
):
    mock_auth.return_value = {}
    mock_load.return_value = sample_capability_statement
    mock_resolve.return_value = ("https://example.com/metadata", "https://example.com")
    mock_auth_config.return_value = (False, "", "", "")

    service = FhirValidatorService.from_env()

    assert service.metadata_url == "https://example.com/metadata"
    assert service.server_base == "https://example.com"
    mock_load_env.assert_called_once()


@patch("fhir_validator_agent.services.validator_service.load_capability_statement")
@patch("fhir_validator_agent.services.validator_service.invalidate_capability_cache")
def test_refresh_capability_invalidates_cache_and_reloads(
    mock_invalidate,
    mock_load,
    sample_capability_statement,
):
    updated_capability = {**sample_capability_statement, "id": "refreshed"}
    mock_load.side_effect = [sample_capability_statement, updated_capability]
    mock_invalidate.return_value = 1

    service = FhirValidatorService(
        metadata_url="https://example.com/metadata",
        server_base="https://example.com",
    )

    service.refresh_capability()

    mock_invalidate.assert_called_once_with("https://example.com/metadata")
    assert mock_load.call_count == 2
    assert service.cap_json["id"] == "refreshed"


@patch("fhir_validator_agent.services.validator_service.get_auth_headers")
@patch("fhir_validator_agent.infrastructure.capability_index.outbound_get")
def test_service_instances_share_capability_cache(
    mock_get,
    mock_auth,
    sample_capability_statement,
):
    reset_capability_cache()
    mock_auth.return_value = {}
    mock_response = MagicMock()
    mock_response.content = b'{"resourceType": "CapabilityStatement"}'
    mock_response.json.return_value = sample_capability_statement
    mock_get.return_value = mock_response

    FhirValidatorService(
        metadata_url="https://example.com/metadata",
        server_base="https://example.com",
    )
    FhirValidatorService(
        metadata_url="https://example.com/metadata",
        server_base="https://example.com",
    )

    mock_get.assert_called_once()