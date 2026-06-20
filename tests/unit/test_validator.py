from fhir_validator_agent.core.validator import FhirQueryValidator


def test_extract_allowed_resource_types(validator: FhirQueryValidator):
    assert validator.allowed_resource_types == {"Patient", "AllergyIntolerance"}


def test_valid_gender_query(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("Patient", {"gender": ["male"]})
    assert errors == []


def test_invalid_gender_value(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("Patient", {"gender": ["fe"]})
    assert len(errors) == 1
    assert "Patient.gender" in errors[0]


def test_unknown_search_param(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("Patient", {"unknown_param": ["value"]})
    assert len(errors) == 1
    assert "unknown_param" in errors[0]


def test_allowed_modifier(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("Patient", {"gender:exact": ["male"]})
    assert errors == []


def test_disallowed_modifier(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("Patient", {"gender:missing": ["male"]})
    assert len(errors) == 1
    assert "missing" in errors[0]


def test_allowed_comparator(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("Patient", {"birthdate:gt": ["2000-01-01"]})
    assert errors == []


def test_invalid_patient_identifier(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("Patient", {"identifier": ["11111111"]})
    assert len(errors) == 1
    assert "Patient.identifier" in errors[0]


def test_allergy_clinical_status_valid(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("AllergyIntolerance", {"clinical-status": ["active"]})
    assert errors == []


def test_allergy_verification_status_invalid(validator: FhirQueryValidator):
    errors = validator.validate_fhir_query("AllergyIntolerance", {"verification-status": ["bogus"]})
    assert len(errors) == 1
    assert "AllergyIntolerance.verification-status" in errors[0]


def test_empty_capability_statement():
    validator = FhirQueryValidator({"resourceType": "CapabilityStatement", "rest": []})
    assert validator.allowed_resource_types == set()
    assert validator.validate_resource_type("Patient") is False