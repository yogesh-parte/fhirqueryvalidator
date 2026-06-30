import fhir_validator_agent as package


def test_fhir_validator_agent_alias():
    assert package.FhirValidatorAgent is package.FhirValidatorService


def test_public_exports():
    expected = {
        "DEFAULT_PUBLIC_SERVERS",
        "PUBLIC_TEST_SERVERS",
        "FhirQueryValidator",
        "FhirValidatorAgent",
        "FhirValidatorService",
        "STATIC_VALUESETS",
        "get_auth_config",
        "get_auth_headers",
        "get_default_server",
        "invalidate_capability_cache",
        "get_public_test_server",
        "get_public_test_servers_without_auth",
        "is_valid_patient_identifier",
        "list_public_server_keys",
        "load_capability_statement",
        "load_env_file",
        "parse_fhir_query",
        "resolve_fhir_urls",
    }
    assert set(package.__all__) == expected