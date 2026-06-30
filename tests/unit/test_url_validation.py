import socket
from unittest.mock import patch

import pytest

from fhir_validator_agent.infrastructure.url_validation import (
    resolve_outbound_addresses,
    select_pinned_address,
    validate_outbound_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://hapi.fhir.org/baseR4/metadata",
        "https://server.fire.ly/metadata",
        "https://example.com:443/metadata",
    ],
)
def test_validate_outbound_url_allows_public_https_urls(url):
    validate_outbound_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://hapi.fhir.org/baseR4/metadata",
        "ftp://example.com/metadata",
        "file:///etc/passwd",
    ],
)
def test_validate_outbound_url_rejects_non_https_schemes(url):
    with pytest.raises(ValueError, match="HTTPS"):
        validate_outbound_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1/metadata",
        "https://localhost/metadata",
        "https://169.254.169.254/latest/meta-data/",
        "https://10.0.0.1/metadata",
        "https://192.168.1.1/metadata",
        "https://[::1]/metadata",
        "https://metadata.internal/service",
    ],
)
def test_validate_outbound_url_blocks_private_and_metadata_hosts(url):
    with pytest.raises(ValueError, match="not allowed|private or reserved"):
        validate_outbound_url(url)


def test_validate_outbound_url_requires_hostname():
    with pytest.raises(ValueError, match="hostname"):
        validate_outbound_url("https:///metadata")


@patch(
    "fhir_validator_agent.infrastructure.url_validation.socket.getaddrinfo",
    return_value=[(2, 1, 6, "", ("93.184.216.34", 443))],
)
def test_resolve_outbound_addresses_returns_public_ips(mock_getaddrinfo):
    assert resolve_outbound_addresses("example.com", 443) == ["93.184.216.34"]
    mock_getaddrinfo.assert_called_once_with("example.com", 443, type=socket.SOCK_STREAM)


@patch(
    "fhir_validator_agent.infrastructure.url_validation.socket.getaddrinfo",
    return_value=[(2, 1, 6, "", ("127.0.0.1", 443))],
)
def test_resolve_outbound_addresses_rejects_private_ips(mock_getaddrinfo):
    with pytest.raises(ValueError, match="private or reserved"):
        resolve_outbound_addresses("rebind.example", 443)


@patch(
    "fhir_validator_agent.infrastructure.url_validation.socket.getaddrinfo",
    return_value=[(2, 1, 6, "", ("93.184.216.34", 443))],
)
def test_select_pinned_address_resolves_hostname(mock_getaddrinfo):
    host, pinned_ip = select_pinned_address("https://example.com/metadata")
    assert host == "example.com"
    assert pinned_ip == "93.184.216.34"


def test_select_pinned_address_uses_literal_public_ip():
    host, pinned_ip = select_pinned_address("https://93.184.216.34/metadata")
    assert host == "93.184.216.34"
    assert pinned_ip == "93.184.216.34"