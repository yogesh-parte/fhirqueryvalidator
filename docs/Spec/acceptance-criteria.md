# Acceptance Criteria — FHIR Search Validator v0.1.0

Given/When/Then scenarios for verification. Maps to requirement IDs in [requirements.md](requirements.md) and regression cases in [behavior.md §4](behavior.md#4-regression-scenarios).

## Core validation

### AC-01: Valid Patient gender query

- **Requirement:** FR-01, FR-03, FR-06, FR-08
- **Regression:** `patient_gender_male_valid`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query("https://hapi.fhir.org/baseR4/Patient?gender=male")` is called
- **Then** `valid` is `true` and `errors` is `[]`

### AC-02: Invalid gender coded value

- **Requirement:** FR-06, FR-08
- **Regression:** `patient_gender_invalid_value`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query(".../Patient?gender=fe")` is called
- **Then** `valid` is `false` and `errors` contains a message mentioning `Patient.gender` and `fe`

### AC-03: Unknown search parameter

- **Requirement:** FR-04, FR-08
- **Regression:** `patient_unknown_param`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query(".../Patient?unknown_param=value")` is called
- **Then** `valid` is `false` and `errors` contains `unknown_param` and `not allowed`

### AC-04: Allowed modifier on search param

- **Requirement:** FR-05, FR-08
- **Regression:** `patient_gender_exact_modifier_valid`
- **Given** the CapabilityStatement allows `:exact` on `gender`
- **When** `validate_query(".../Patient?gender:exact=male")` is called
- **Then** `valid` is `true` and `errors` is `[]`

### AC-05: Disallowed modifier on search param

- **Requirement:** FR-05, FR-08
- **Regression:** `patient_gender_missing_modifier_invalid`
- **Given** the CapabilityStatement does not allow `:missing` on `gender`
- **When** `validate_query(".../Patient?gender:missing=true")` is called
- **Then** `valid` is `false` and `errors` mention `missing` and `gender`

### AC-06: Allowed comparator on date param

- **Requirement:** FR-05, FR-08
- **Regression:** `patient_birthdate_gt_comparator_valid`
- **Given** the CapabilityStatement allows `:gt` on `birthdate`
- **When** `validate_query(".../Patient?birthdate:gt=2000-01-01")` is called
- **Then** `valid` is `true` and `errors` is `[]`

### AC-07: Valid Patient identifier

- **Requirement:** FR-07, FR-08
- **Regression:** `patient_identifier_valid`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query(".../Patient?identifier=12345678")` is called
- **Then** `valid` is `true` and `errors` is `[]`

### AC-08: Invalid Patient identifier (all identical digits)

- **Requirement:** FR-07, FR-08
- **Regression:** `patient_identifier_all_identical_digits`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query(".../Patient?identifier=11111111")` is called
- **Then** `valid` is `false` and `errors` mention `Patient.identifier` and `identical`

### AC-09: Unsupported resource type

- **Requirement:** FR-03, FR-08
- **Regression:** `unsupported_resource_type`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query(".../UnknownResource?foo=bar")` is called
- **Then** `valid` is `false` and `errors` mention `UnknownResource` and `not supported`

### AC-10: Relative URL parsing

- **Requirement:** FR-01, FR-08
- **Regression:** `relative_url_patient_gender`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query("/Patient?gender=other")` is called
- **Then** `valid` is `true` and `errors` is `[]`

### AC-11: Multiple params with one invalid value

- **Requirement:** FR-06, FR-08
- **Regression:** `multiple_params_one_invalid`
- **Given** a HAPI CapabilityStatement fixture is loaded
- **When** `validate_query(".../Patient?gender=invalid&identifier=12345678")` is called
- **Then** `valid` is `false` and `errors` mention `Patient.gender` and `invalid`

## CLI

### AC-12: CLI exits 0 for valid query

- **Requirement:** FR-12
- **Given** environment is configured for HAPI (or mocked service)
- **When** `fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"` runs
- **Then** exit code is `0` and stdout contains `Valid: True`

### AC-13: CLI exits 1 for invalid query

- **Requirement:** FR-12
- **Given** environment is configured for HAPI (or mocked service)
- **When** `fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=fe"` runs
- **Then** exit code is `1` and stdout contains `Valid: False` and `Errors:`

### AC-14: CLI usage error

- **Requirement:** FR-12
- **Given** no arguments provided
- **When** `fhir-validate` runs with zero arguments
- **Then** exit code is `1` and stdout contains `Usage:`

## Public server integration

### AC-15: HAPI live server validates Patient gender

- **Requirement:** FR-02, FR-09
- **Given** network access to `https://hapi.fhir.org/baseR4/metadata`
- **When** `FhirValidatorService(metadata_url=..., server_base=...)` validates `Patient?gender=male`
- **Then** `valid` is `true`

### AC-16: Each public server rejects invalid gender

- **Requirement:** FR-09
- **Given** network access to a public server (`hapi`, `firely`, `spark`, or `wildfhir`)
- **When** `validate_query(".../Patient?gender=invalid")` is called
- **Then** `valid` is `false`

## CapabilityStatement cache

### AC-20: Cache reuse within TTL

- **Requirement:** FR-15
- **Given** a CapabilityStatement for `https://example.com/metadata` is cached with TTL not yet expired
- **When** `load_capability_statement("https://example.com/metadata")` is called again
- **Then** the cached JSON is returned without a second HTTP GET

### AC-21: Trigger-based invalidation

- **Requirement:** FR-15
- **Given** a cached CapabilityStatement for a metadata URL
- **When** `invalidate_capability_cache(url)` or `service.refresh_capability()` is called
- **Then** the next fetch performs a new HTTP GET and returns fresh metadata

### AC-22: TTL expiry refetches metadata

- **Requirement:** FR-15
- **Given** a cached entry older than `FHIR_CAPABILITY_CACHE_TTL_SECONDS`
- **When** `load_capability_statement(url)` is called
- **Then** the expired entry is removed and metadata is fetched again

## Service construction

### AC-17: from_env loads configuration

- **Requirement:** FR-10, FR-12
- **Given** `config/.env.local` sets `FHIR_DEFAULT_SERVER_KEY=firely`
- **When** `FhirValidatorService.from_env()` is called (with mocked metadata fetch)
- **Then** service uses Firely metadata and base URLs

### AC-18: OAuth headers when auth enabled

- **Requirement:** FR-11
- **Given** `FHIR_USE_AUTH=true` and valid OAuth credentials
- **When** `get_auth_headers(...)` is called
- **Then** returned headers include `Authorization: Bearer {token}`

## Backward compatibility

### AC-19: FhirValidatorAgent alias

- **Requirement:** NFR-04
- **Given** the public package API
- **When** `from fhir_validator_agent import FhirValidatorAgent` is executed
- **Then** `FhirValidatorAgent` is identical to `FhirValidatorService`