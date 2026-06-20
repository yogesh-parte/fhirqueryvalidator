import pytest

from fhir_validator_agent.core.validator import FhirQueryValidator


@pytest.fixture
def sample_capability_statement() -> dict:
    return {
        "resourceType": "CapabilityStatement",
        "rest": [
            {
                "resource": [
                    {
                        "type": "Patient",
                        "searchParam": [
                            {
                                "name": "gender",
                                "extension": [
                                    {
                                        "url": "http://hl7.org/fhir/StructureDefinition/CapabilityStatementSearchParameterModifiers",
                                        "valueCoding": {"code": "exact"},
                                    }
                                ],
                            },
                            {
                                "name": "birthdate",
                                "extension": [
                                    {
                                        "url": "http://hl7.org/fhir/StructureDefinition/CapabilityStatementSearchParameterComparators",
                                        "valueCoding": {"code": "gt"},
                                    }
                                ],
                            },
                            {"name": "identifier"},
                        ],
                    },
                    {
                        "type": "AllergyIntolerance",
                        "searchParam": [
                            {"name": "clinical-status"},
                            {"name": "verification-status"},
                        ],
                    },
                ]
            }
        ],
    }


@pytest.fixture
def validator(sample_capability_statement) -> FhirQueryValidator:
    return FhirQueryValidator(sample_capability_statement)