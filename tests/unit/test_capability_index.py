from unittest.mock import MagicMock, patch

import pytest
import requests

from fhir_validator_agent.infrastructure.capability_index import get_auth_headers, load_capability_statement


def test_get_auth_headers_returns_empty_when_auth_disabled():
    assert get_auth_headers(False, "", "", "") == {}


def test_get_auth_headers_raises_when_oauth_config_incomplete():
    with pytest.raises(RuntimeError, match="Missing OAuth configuration"):
        get_auth_headers(True, "", "client", "secret")


@patch("fhir_validator_agent.infrastructure.capability_index.requests.post")
def test_get_auth_headers_returns_bearer_token(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "token-123"}
    mock_post.return_value = mock_response

    headers = get_auth_headers(
        True,
        "https://auth.example/token",
        "client-id",
        "client-secret",
    )

    assert headers == {"Authorization": "Bearer token-123"}
    mock_post.assert_called_once()


@patch("fhir_validator_agent.infrastructure.capability_index.requests.post")
def test_get_auth_headers_raises_when_token_missing(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    with pytest.raises(RuntimeError, match="access_token"):
        get_auth_headers(True, "https://auth.example/token", "id", "secret")


@patch("fhir_validator_agent.infrastructure.capability_index.requests.get")
def test_load_capability_statement_returns_json(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"resourceType": "CapabilityStatement"}
    mock_get.return_value = mock_response

    result = load_capability_statement("https://example.com/metadata")

    assert result["resourceType"] == "CapabilityStatement"
    mock_get.assert_called_once_with(
        "https://example.com/metadata",
        headers={"Accept": "application/fhir+json"},
        timeout=20,
    )


@patch("fhir_validator_agent.infrastructure.capability_index.requests.get")
def test_load_capability_statement_passes_headers(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"resourceType": "CapabilityStatement"}
    mock_get.return_value = mock_response

    load_capability_statement("https://example.com/metadata", headers={"Authorization": "Bearer x"})

    mock_get.assert_called_once_with(
        "https://example.com/metadata",
        headers={"Accept": "application/fhir+json", "Authorization": "Bearer x"},
        timeout=20,
    )


@patch("fhir_validator_agent.infrastructure.capability_index.requests.get")
def test_load_capability_statement_raises_on_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        load_capability_statement("https://example.com/metadata")