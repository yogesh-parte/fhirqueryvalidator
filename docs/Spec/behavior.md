# Behavior — FHIR Search Validator v0.1.0

Normative validation rules, error catalog, and regression scenarios. This is the authoritative behavioral contract.

## 1. Validation order

When `validate_query(url)` is called:

1. Parse URL → resource type + params ([§2.1](#21-url-parsing))
2. Reject if resource type cannot be determined
3. Reject if resource type not in CapabilityStatement index ([§2.3](#23-structural-validation))
4. For each query parameter, run structural then semantic checks ([§2.3](#23-structural-validation), [§2.4](#24-semantic-validation))
5. Return aggregated errors

CapabilityStatement is loaded at service construction via the metadata cache ([§2.2](#22-capabilitystatement-indexing)). Subsequent service instances for the same URL reuse the cached entry until TTL expiry or explicit invalidation.

## 2. Normative rules

### 2.1 URL parsing

**Component:** `core/query_parser.py` — `parse_fhir_query(query_url)`

| Rule | Behavior |
|------|----------|
| Resource type extraction | Last non-empty path segment after `strip("/")` and `split("/")` |
| Relative URLs | `/Patient?gender=male` → resource type `Patient` |
| Trailing slash | `.../Patient/?gender=male` → resource type `Patient` |
| URL encoding | Percent-encoded values decoded by `urllib.parse` |
| Multi-value params | `?gender=male&gender=female` → `{"gender": ["male", "female"]}` |
| Modifiers in param name | `gender:exact` preserved as single param key (not split further) |
| Empty path | `?foo=bar` → resource type `None` |
| Empty query | `Patient` → `({},)` params dict empty |

### 2.2 CapabilityStatement indexing

**Components:** `infrastructure/capability_index.py`, `infrastructure/capability_cache.py`, `core/validator.py`

#### Metadata fetch

- HTTP GET to `metadata_url` when cache miss or cache disabled
- Request header: `Accept: application/fhir+json`
- Optional `Authorization: Bearer {token}` when OAuth enabled
- Timeout: 20 seconds (default)
- Non-2xx responses propagate as exceptions (not validation errors)

#### Metadata cache

**Component:** `infrastructure/capability_cache.py`

| Rule | Behavior |
|------|----------|
| Cache scope | In-memory, per process |
| Cache key | `metadata_url` + sorted auth headers (e.g. `Authorization`) |
| Default TTL | 86_400 seconds (24 hours) via `FHIR_CAPABILITY_CACHE_TTL_SECONDS` |
| Enable/disable | `FHIR_CAPABILITY_CACHE_ENABLED` (default `true`) |
| TTL expiry | Checked on read; expired entries are removed and metadata is re-fetched |
| Shared cache | Multiple `FhirValidatorService` instances for the same URL share one entry |
| Bypass | `load_capability_statement(..., use_cache=False)` skips read and write |
| Invalidate one URL | `invalidate_capability_cache(url)` removes all auth variants for that URL |
| Invalidate all | `invalidate_capability_cache()` clears entire cache |
| Service refresh | `FhirValidatorService.refresh_capability()` invalidates then reloads for `metadata_url` |

#### Index construction

From `CapabilityStatement.rest[].resource[]`:

| Indexed data | Source path |
|--------------|-------------|
| Allowed resource types | `resource.type` |
| Search param names | `resource.searchParam[].name` |
| Allowed modifiers | Extension URL ending `CapabilityStatementSearchParameterModifiers` → `valueCoding.code` |
| Allowed comparators | Extension URL ending `CapabilityStatementSearchParameterComparators` → `valueCoding.code` |

Empty or missing `rest` → no resource types, no search params (all queries fail structural validation).

### 2.3 Structural validation

**Component:** `core/validator.py` — `validate_param`, `validate_fhir_query`

For each query parameter key (e.g. `birthdate:gt`, `gender:exact`):

1. Split on first `:` → `param_name` and optional `operator`
2. If `param_name` not in allowed params for resource → error
3. If `operator` present and not in param's `modifiers` or `comparators` → error
4. If `operator` absent → param name match alone is sufficient

**Modifier vs comparator:** Both are treated identically — the operator after `:` must appear in either the modifiers set or comparators set for that param.

### 2.4 Semantic validation

**Component:** `core/codeset_validator.py`

Applied after structural validation passes for each param. Uses base param name (before `:`).

#### Static value sets

| Key | Allowed values |
|-----|----------------|
| `Patient.gender` | `male`, `female`, `other`, `unknown` |
| `AllergyIntolerance.verification-status` | `unconfirmed`, `confirmed`, `refuted`, `entered-in-error` |
| `AllergyIntolerance.clinical-status` | `active`, `inactive`, `resolved` |

When a key exists in `STATIC_VALUESETS`, every value in the query param must be a member of the allowed set.

#### Patient identifier rules

When `resource_type == "Patient"` and `param_name == "identifier"`:

| Rule | Error reason |
|------|--------------|
| Digits only | `Identifier must be numeric only.` |
| Length 8–10 | `Identifier must be between 8 and 10 digits.` |
| Not all identical digits | `Identifier cannot be all identical digits.` |

Each identifier value is validated independently.

## 3. Error catalog

Canonical error message patterns. Agents may match these with substring or regex checks.

| ID | Pattern | Example |
|----|---------|---------|
| ERR-01 | `Unable to parse resource type from query URL.` | Empty path URL |
| ERR-02 | `Resource type '{type}' is not supported.` | `UnknownResource` not in CapabilityStatement |
| ERR-03 | `Search param '{param}' not allowed for resource` | `unknown_param` on Patient |
| ERR-04 | `Modifier/comparator '{op}' not allowed for param '{param}'` | `gender:missing` when `:missing` not allowed |
| ERR-05 | `Value '{value}' for '{key}' is not allowed. Allowed values: {set}` | `gender=fe` → key `Patient.gender` |
| ERR-06 | `Patient.identifier '{id}' invalid: {reason}` | Non-numeric, wrong length, identical digits |

Errors from multiple params are concatenated. A query with one invalid param and one valid param still returns `valid: false`.

## 4. Regression scenarios

All cases in `tests/regression/cases.json` are normative. They use the HAPI fixture CapabilityStatement from `tests/conftest.py` unless noted.

| Case ID | Description | Expected |
|---------|-------------|----------|
| `patient_gender_male_valid` | Valid Patient gender | `valid: true` |
| `patient_gender_female_valid` | Valid gender female | `valid: true` |
| `patient_gender_invalid_value` | Invalid coded value `fe` | `valid: false`, errors mention `Patient.gender` |
| `patient_unknown_param` | Unsupported param | `valid: false`, errors mention `not allowed` |
| `patient_gender_exact_modifier_valid` | Allowed `:exact` modifier | `valid: true` |
| `patient_gender_missing_modifier_invalid` | Disallowed `:missing` modifier | `valid: false`, errors mention `missing` |
| `patient_birthdate_gt_comparator_valid` | Allowed `:gt` comparator | `valid: true` |
| `patient_identifier_valid` | 8-digit numeric identifier | `valid: true` |
| `patient_identifier_all_identical_digits` | `11111111` | `valid: false`, errors mention `identical` |
| `patient_identifier_too_short` | 7 digits | `valid: false`, errors mention `8 and 10` |
| `unsupported_resource_type` | `UnknownResource` | `valid: false`, errors mention `not supported` |
| `allergy_clinical_status_active_valid` | Valid clinical-status | `valid: true` |
| `allergy_clinical_status_invalid` | `deleted` value | `valid: false`, errors mention `clinical-status` |
| `relative_url_patient_gender` | Relative URL `/Patient?gender=other` | `valid: true` |
| `multiple_params_one_invalid` | Mixed valid/invalid params | `valid: false`, errors mention invalid gender |

Regression tests assert `expected_valid` and check `expected_error_substrings` when present.

## 5. Integration behavior (live servers)

Integration tests (`pytest -m integration`) validate against live public servers:

- Each of `hapi`, `firely`, `spark`, `wildfhir` can load metadata and validate `Patient?gender=male` as valid.
- Each rejects `Patient?gender=invalid` with semantic errors.

Network failures are test infrastructure concerns, not validation contract changes.