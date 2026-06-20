import pytest

from fhir_validator_agent.config.public_servers import (
    PUBLIC_TEST_SERVERS,
    get_public_test_server,
    get_public_test_servers_without_auth,
    list_public_server_keys,
)


def test_all_registered_servers_are_no_auth():
    for server in PUBLIC_TEST_SERVERS.values():
        assert server["auth_required"] is False


def test_list_public_server_keys():
    keys = list_public_server_keys()
    assert "hapi" in keys
    assert "firely" in keys
    assert "spark" in keys
    assert "wildfhir" in keys


def test_get_public_test_server_hapi():
    server = get_public_test_server("hapi")
    assert server["base_url"] == "https://hapi.fhir.org/baseR4"
    assert server["metadata_url"].endswith("/metadata")


def test_get_public_test_server_unknown_key():
    with pytest.raises(KeyError, match="Unknown public server key"):
        get_public_test_server("not-a-server")


def test_get_public_test_servers_without_auth():
    servers = get_public_test_servers_without_auth()
    assert len(servers) == len(PUBLIC_TEST_SERVERS)
    assert all(not server["auth_required"] for server in servers)