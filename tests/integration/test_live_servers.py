import pytest

from fhir_validator_agent import FhirValidatorService


@pytest.mark.integration
def test_validate_query_against_hapi():
    service = FhirValidatorService(
        metadata_url="https://hapi.fhir.org/baseR4/metadata",
        server_base="https://hapi.fhir.org/baseR4",
    )
    result = service.validate_query("https://hapi.fhir.org/baseR4/Patient?gender=male")
    assert result["valid"] is True
    assert result["errors"] == []