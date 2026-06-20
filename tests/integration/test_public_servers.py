import pytest

from fhir_validator_agent import FhirValidatorService
from fhir_validator_agent.config.public_servers import get_public_test_servers_without_auth


@pytest.mark.integration
@pytest.mark.parametrize(
    "server",
    get_public_test_servers_without_auth(),
    ids=[server["key"] for server in get_public_test_servers_without_auth()],
)
def test_public_server_valid_patient_gender(server):
    service = FhirValidatorService(
        metadata_url=server["metadata_url"],
        server_base=server["base_url"],
    )
    result = service.validate_query(f"{server['base_url']}/Patient?gender=male")
    assert result["valid"] is True, f"{server['key']}: {result['errors']}"


@pytest.mark.integration
@pytest.mark.parametrize(
    "server",
    get_public_test_servers_without_auth(),
    ids=[server["key"] for server in get_public_test_servers_without_auth()],
)
def test_public_server_rejects_invalid_gender(server):
    service = FhirValidatorService(
        metadata_url=server["metadata_url"],
        server_base=server["base_url"],
    )
    result = service.validate_query(f"{server['base_url']}/Patient?gender=fe")
    assert result["valid"] is False
    assert any("Patient.gender" in error for error in result["errors"])