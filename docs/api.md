# API Reference

## FhirValidatorService

Primary entry point for validating FHIR search queries.

### `FhirValidatorService(metadata_url, server_base, use_auth=False, token_url="", client_id="", client_secret="")`

Loads the CapabilityStatement from `metadata_url` and prepares the validator.

```python
from fhir_validator_agent import FhirValidatorService

service = FhirValidatorService(
    metadata_url="https://hapi.fhir.org/baseR4/metadata",
    server_base="https://hapi.fhir.org/baseR4",
)
```

### `FhirValidatorService.from_env() -> FhirValidatorService`

Loads `config/.env.local`, resolves server preset and OAuth settings.

```python
service = FhirValidatorService.from_env()
```

### `refresh_capability() -> None`

Invalidates the cached CapabilityStatement for this service's `metadata_url` and reloads it from the server. Rebuilds the internal `FhirQueryValidator` with the fresh metadata.

```python
service.refresh_capability()
```

### `validate_query(query_url: str) -> dict`

| Field | Type | Description |
|-------|------|-------------|
| `valid` | `bool` | `True` if query passes all checks |
| `errors` | `list[str]` | Human-readable error messages (empty when valid) |

```python
result = service.validate_query("https://hapi.fhir.org/baseR4/Patient?gender=male")
# {"valid": True, "errors": []}

result = service.validate_query("https://hapi.fhir.org/baseR4/Patient?gender=fe")
# {"valid": False, "errors": ["Value 'fe' for 'Patient.gender' is not allowed. ..."]}
```

### Backward-compatible alias

```python
from fhir_validator_agent import FhirValidatorAgent  # same as FhirValidatorService
```

---

## FhirQueryValidator

Low-level validator for direct use with a CapabilityStatement JSON dict.

### `FhirQueryValidator(cap_json: dict)`

```python
from fhir_validator_agent import FhirQueryValidator

validator = FhirQueryValidator(capability_statement_dict)
```

### Key methods

| Method | Returns | Description |
|--------|---------|-------------|
| `parse_fhir_query(url)` | `(resource_type, params)` | Delegates to query parser |
| `validate_resource_type(type)` | `bool` | Whether type is in CapabilityStatement |
| `validate_fhir_query(type, params)` | `list[str]` | Validation errors (empty if valid) |
| `get_allowed_params(type)` | `dict` | Allowed params with modifiers/comparators |

---

## Query parser

### `parse_fhir_query(query_url: str) -> tuple[str | None, dict[str, list[str]]]`

```python
from fhir_validator_agent import parse_fhir_query

resource_type, params = parse_fhir_query(
    "https://hapi.fhir.org/baseR4/Patient?gender=male"
)
# ("Patient", {"gender": ["male"]})
```

---

## Public server registry

### `get_public_test_servers_without_auth() -> list[PublicTestServer]`

Returns all built-in no-auth sandboxes.

```python
from fhir_validator_agent import get_public_test_servers_without_auth

for server in get_public_test_servers_without_auth():
    print(server["key"], server["base_url"])
```

### `get_public_test_server(key: str) -> PublicTestServer`

```python
from fhir_validator_agent import get_public_test_server

server = get_public_test_server("hapi")
```

Keys: `hapi`, `firely`, `spark`, `wildfhir`

---

## Infrastructure

### `load_capability_statement(url, headers=None, timeout=20, *, use_cache=None, cache=None) -> dict`

Fetches CapabilityStatement JSON. Sends `Accept: application/fhir+json`. Results are cached in-memory by default (keyed by URL and auth headers) with a configurable TTL.

```python
from fhir_validator_agent import load_capability_statement

# Uses global cache (enabled by default, 24h TTL)
cap = load_capability_statement("https://hapi.fhir.org/baseR4/metadata")

# Bypass cache for a single fetch
cap = load_capability_statement("https://hapi.fhir.org/baseR4/metadata", use_cache=False)
```

### `invalidate_capability_cache(url=None) -> int`

Trigger-based cache invalidation. Returns the number of entries removed. See [ADR 002](adr/002-capability-statement-cache.md) for design rationale.

```python
from fhir_validator_agent import invalidate_capability_cache

# Invalidate one metadata URL (all auth header variants)
invalidate_capability_cache("https://hapi.fhir.org/baseR4/metadata")

# Invalidate entire cache
invalidate_capability_cache()
```

### `get_auth_headers(use_auth, token_url, client_id, client_secret) -> dict`

Returns `{}` when auth disabled, or `{"Authorization": "Bearer ..."}` for client-credentials.

---

## CLI

### `fhir-validate <FHIR_QUERY_URL>`

Installed via `pip install -e .`. Exit code `0` when valid, `1` when invalid or usage error.

```bash
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"
```

Programmatic equivalent:

```python
from fhir_validator_agent.cli import main
exit_code = main(["https://hapi.fhir.org/baseR4/Patient?gender=male"])
```

---

## Static value sets

### `STATIC_VALUESETS`

Dict mapping `"ResourceType.param"` to allowed string values.

### `is_valid_patient_identifier(identifier: str) -> tuple[bool, str | None]`

Returns `(True, None)` or `(False, error_message)`.