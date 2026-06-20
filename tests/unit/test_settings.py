import os
from unittest.mock import patch

import pytest

from fhir_validator_agent.config.settings import (
    DEFAULT_PUBLIC_SERVERS,
    get_auth_config,
    get_default_server,
    resolve_fhir_urls,
)


def test_default_server_is_hapi():
    with patch.dict(os.environ, {}, clear=True):
        server = get_default_server()
    assert server == DEFAULT_PUBLIC_SERVERS["hapi"]


def test_default_server_firely_key():
    with patch.dict(os.environ, {"FHIR_DEFAULT_SERVER_KEY": "firely"}, clear=True):
        server = get_default_server()
    assert server == DEFAULT_PUBLIC_SERVERS["firely"]


def test_default_server_unknown_key_falls_back_to_hapi():
    with patch.dict(os.environ, {"FHIR_DEFAULT_SERVER_KEY": "unknown"}, clear=True):
        server = get_default_server()
    assert server == DEFAULT_PUBLIC_SERVERS["hapi"]


def test_resolve_fhir_urls_uses_env_overrides():
    env = {
        "FHIR_METADATA_URL": "https://custom.example/metadata",
        "FHIR_SERVER_BASE": "https://custom.example",
    }
    with patch.dict(os.environ, env, clear=True):
        metadata_url, server_base = resolve_fhir_urls()
    assert metadata_url == "https://custom.example/metadata"
    assert server_base == "https://custom.example"


def test_get_auth_config_disabled_by_default():
    with patch.dict(os.environ, {}, clear=True):
        use_auth, token_url, client_id, client_secret = get_auth_config()
    assert use_auth is False
    assert token_url == ""
    assert client_id == ""
    assert client_secret == ""


@pytest.mark.parametrize("truthy", ["true", "True", "1", "yes"])
def test_get_auth_config_enabled(truthy):
    env = {
        "FHIR_USE_AUTH": truthy,
        "TOKEN_URL": "https://auth.example/token",
        "CLIENT_ID": "client",
        "CLIENT_SECRET": "secret",
    }
    with patch.dict(os.environ, env, clear=True):
        use_auth, token_url, client_id, client_secret = get_auth_config()
    assert use_auth is True
    assert token_url == "https://auth.example/token"
    assert client_id == "client"
    assert client_secret == "secret"