from unittest.mock import MagicMock, patch

import pytest
import requests

from fhir_validator_agent.infrastructure.outbound_http import outbound_get, outbound_post
from fhir_validator_agent.infrastructure.rate_limit import reset_outbound_rate_limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    reset_outbound_rate_limiter()
    yield
    reset_outbound_rate_limiter()


@patch("fhir_validator_agent.infrastructure.outbound_http.requests.get")
@patch(
    "fhir_validator_agent.infrastructure.outbound_http.select_pinned_address",
    return_value=("example.com", "93.184.216.34"),
)
def test_outbound_get_uses_pinned_connection(mock_select_pinned, mock_get):
    mock_response = MagicMock()
    mock_get.return_value = mock_response

    result = outbound_get("https://example.com/metadata", headers={"Accept": "application/json"})

    assert result is mock_response
    mock_select_pinned.assert_called_once_with("https://example.com/metadata")
    mock_get.assert_called_once_with(
        "https://example.com/metadata",
        headers={"Accept": "application/json"},
        timeout=20,
        allow_redirects=False,
    )


@patch("fhir_validator_agent.infrastructure.outbound_http.requests.post")
@patch(
    "fhir_validator_agent.infrastructure.outbound_http.select_pinned_address",
    return_value=("auth.example", "93.184.216.34"),
)
def test_outbound_post_uses_pinned_connection(mock_select_pinned, mock_post):
    mock_response = MagicMock()
    mock_post.return_value = mock_response

    result = outbound_post(
        "https://auth.example/token",
        data={"grant_type": "client_credentials"},
        auth=("client", "secret"),
    )

    assert result is mock_response
    mock_select_pinned.assert_called_once_with("https://auth.example/token")
    mock_post.assert_called_once_with(
        "https://auth.example/token",
        data={"grant_type": "client_credentials"},
        auth=("client", "secret"),
        timeout=20,
        allow_redirects=False,
    )


@patch(
    "fhir_validator_agent.infrastructure.outbound_http.select_pinned_address",
    side_effect=ValueError("blocked host"),
)
def test_outbound_get_logs_blocked_request(mock_select_pinned, caplog):
    import logging

    caplog.set_level(logging.WARNING, logger="fhir_validator_agent.security")

    with pytest.raises(ValueError, match="blocked host"):
        outbound_get("https://example.com/metadata")

    assert any("outbound_request_blocked" in record.message for record in caplog.records)


@patch("fhir_validator_agent.infrastructure.outbound_http.get_outbound_rate_limiter")
@patch("fhir_validator_agent.infrastructure.outbound_http.requests.get")
@patch(
    "fhir_validator_agent.infrastructure.outbound_http.select_pinned_address",
    return_value=("example.com", "93.184.216.34"),
)
def test_outbound_get_logs_rate_limited_request(mock_select_pinned, mock_get, mock_get_limiter, caplog):
    import logging

    caplog.set_level(logging.WARNING, logger="fhir_validator_agent.security")
    limiter = MagicMock()
    limiter.acquire.side_effect = ValueError("Outbound rate limit exceeded for host example.com")
    mock_get_limiter.return_value = limiter

    with pytest.raises(ValueError, match="rate limit exceeded"):
        outbound_get("https://example.com/metadata")

    assert any("outbound_request_rate_limited" in record.message for record in caplog.records)
    mock_get.assert_not_called()


@patch("fhir_validator_agent.infrastructure.outbound_http.requests.get")
@patch(
    "fhir_validator_agent.infrastructure.outbound_http.select_pinned_address",
    return_value=("example.com", "93.184.216.34"),
)
def test_outbound_get_logs_request_failures(mock_select_pinned, mock_get, caplog):
    import logging

    caplog.set_level(logging.WARNING, logger="fhir_validator_agent.security")
    mock_get.side_effect = requests.Timeout("timed out")

    with pytest.raises(requests.Timeout):
        outbound_get("https://example.com/metadata")

    assert any("outbound_request_failed" in record.message for record in caplog.records)