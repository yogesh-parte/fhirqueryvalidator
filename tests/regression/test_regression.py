import json
from pathlib import Path
from unittest.mock import patch

import pytest

from fhir_validator_agent.core.query_parser import parse_fhir_query
from fhir_validator_agent.core.validator import FhirQueryValidator
from fhir_validator_agent.services.validator_service import FhirValidatorService

CASES_PATH = Path(__file__).parent / "cases.json"


def _load_regression_cases() -> list[dict]:
    with CASES_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _validate_with_fixture_cap(query: str, cap_json: dict) -> dict:
    validator = FhirQueryValidator(cap_json)
    resource_type, query_params = parse_fhir_query(query)
    if not resource_type:
        return {"valid": False, "errors": ["Unable to parse resource type from query URL."]}
    if not validator.validate_resource_type(resource_type):
        return {"valid": False, "errors": [f"Resource type '{resource_type}' is not supported."]}
    errors = validator.validate_fhir_query(resource_type, query_params)
    return {"valid": not bool(errors), "errors": errors}


REGRESSION_CASES = _load_regression_cases()


@pytest.mark.regression
@pytest.mark.parametrize("case", REGRESSION_CASES, ids=[case["id"] for case in REGRESSION_CASES])
def test_regression_core_validation(case, sample_capability_statement):
    result = _validate_with_fixture_cap(case["query"], sample_capability_statement)
    assert result["valid"] is case["expected_valid"], (
        f"{case['id']}: expected valid={case['expected_valid']}, got {result}"
    )
    if case.get("expected_errors") is not None:
        assert result["errors"] == case["expected_errors"]
    for substring in case.get("expected_error_substrings", []):
        joined = " ".join(result["errors"])
        assert substring in joined, (
            f"{case['id']}: expected error containing '{substring}', got {result['errors']}"
        )


@pytest.mark.regression
@pytest.mark.parametrize("case", REGRESSION_CASES, ids=[case["id"] for case in REGRESSION_CASES])
@patch("fhir_validator_agent.services.validator_service.load_capability_statement")
@patch("fhir_validator_agent.services.validator_service.get_auth_headers")
def test_regression_service_validation(mock_auth_headers, mock_load_cap, case, sample_capability_statement):
    mock_auth_headers.return_value = {}
    mock_load_cap.return_value = sample_capability_statement

    service = FhirValidatorService(
        metadata_url="https://example.com/metadata",
        server_base="https://example.com",
    )
    result = service.validate_query(case["query"])

    assert result["valid"] is case["expected_valid"], (
        f"{case['id']}: expected valid={case['expected_valid']}, got {result}"
    )
    for substring in case.get("expected_error_substrings", []):
        joined = " ".join(result["errors"])
        assert substring in joined, (
            f"{case['id']}: expected error containing '{substring}', got {result['errors']}"
        )