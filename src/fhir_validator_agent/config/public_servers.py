"""
Curated public FHIR R4 test servers that do not require authentication.

Sourced from the HL7 FHIR Public Test Servers list and common community sandboxes
used for open read/search testing (see docs/public-test-servers.md).
"""

from typing import TypedDict


class PublicTestServer(TypedDict):
    key: str
    name: str
    fhir_version: str
    metadata_url: str
    base_url: str
    auth_required: bool
    description: str
    reference: str


PUBLIC_TEST_SERVERS: dict[str, PublicTestServer] = {
    "hapi": {
        "key": "hapi",
        "name": "HAPI FHIR Reference Server",
        "fhir_version": "R4",
        "metadata_url": "https://hapi.fhir.org/baseR4/metadata",
        "base_url": "https://hapi.fhir.org/baseR4",
        "auth_required": False,
        "description": "Open-source Apache 2.0 reference server with broad R4 search support.",
        "reference": "https://hapifhir.io/",
    },
    "firely": {
        "key": "firely",
        "name": "Firely Public Server",
        "fhir_version": "R4",
        "metadata_url": "https://server.fire.ly/metadata",
        "base_url": "https://server.fire.ly",
        "auth_required": False,
        "description": "Firely demo server for open read/search testing (stable public endpoint).",
        "reference": "https://server.fire.ly/",
    },
    "spark": {
        "key": "spark",
        "name": "Spark FHIR Reference Server",
        "fhir_version": "R4",
        "metadata_url": "https://spark.incendi.no/fhir/metadata",
        "base_url": "https://spark.incendi.no/fhir",
        "auth_required": False,
        "description": "Open-source Spark FHIR server maintained by Incendi (BSD-3).",
        "reference": "https://github.com/FirelyTeam/spark",
    },
    "wildfhir": {
        "key": "wildfhir",
        "name": "AEGIS WildFHIR Community Edition",
        "fhir_version": "R4",
        "metadata_url": "https://wildfhir.wildfhir.org/r4/metadata",
        "base_url": "https://wildfhir.wildfhir.org/r4",
        "auth_required": False,
        "description": "Community FHIR R4 reference server with open metadata and search.",
        "reference": "https://wildfhir.wildfhir.org/r4",
    },
}


def list_public_server_keys() -> list[str]:
    return list(PUBLIC_TEST_SERVERS.keys())


def get_public_test_server(key: str) -> PublicTestServer:
    normalized = key.lower()
    if normalized not in PUBLIC_TEST_SERVERS:
        known = ", ".join(list_public_server_keys())
        raise KeyError(f"Unknown public server key '{key}'. Known keys: {known}")
    return PUBLIC_TEST_SERVERS[normalized]


def get_public_test_servers_without_auth() -> list[PublicTestServer]:
    return [server for server in PUBLIC_TEST_SERVERS.values() if not server["auth_required"]]


def get_server_urls(key: str) -> dict[str, str]:
    server = get_public_test_server(key)
    return {
        "metadata_url": server["metadata_url"],
        "base_url": server["base_url"],
    }