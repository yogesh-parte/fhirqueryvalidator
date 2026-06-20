from fhir_validator_agent.core.query_parser import parse_fhir_query


def test_parse_full_patient_query_url():
    resource_type, params = parse_fhir_query("https://hapi.fhir.org/baseR4/Patient?gender=male&active=true")
    assert resource_type == "Patient"
    assert params["gender"] == ["male"]
    assert params["active"] == ["true"]


def test_parse_relative_query_path():
    resource_type, params = parse_fhir_query("/Patient?gender=female")
    assert resource_type == "Patient"
    assert params["gender"] == ["female"]


def test_parse_query_with_modifier_in_param_name():
    resource_type, params = parse_fhir_query("https://example.com/Patient?gender:exact=male")
    assert resource_type == "Patient"
    assert "gender:exact" in params


def test_parse_trailing_slash_path():
    resource_type, params = parse_fhir_query("https://example.com/baseR4/Patient/?gender=male")
    assert resource_type == "Patient"
    assert params["gender"] == ["male"]


def test_parse_url_encoded_values():
    resource_type, params = parse_fhir_query("https://example.com/Patient?name=John%20Doe")
    assert resource_type == "Patient"
    assert params["name"] == ["John Doe"]


def test_parse_multiple_values_for_same_param():
    resource_type, params = parse_fhir_query("https://example.com/Patient?gender=male&gender=female")
    assert resource_type == "Patient"
    assert params["gender"] == ["male", "female"]


def test_parse_empty_query_string():
    resource_type, params = parse_fhir_query("https://example.com/Patient")
    assert resource_type == "Patient"
    assert params == {}