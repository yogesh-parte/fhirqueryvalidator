# Interfaces — FHIR Search Validator v0.1.0

Machine-precise contracts for public APIs, CLI, environment configuration, and HTTP behavior.

## Result contract

All validation entry points return the same shape:

```python
{"valid": bool, "errors": list[str]}
```

| Field | Type | Semantics |
|-------|------|-----------|
| `valid` | `bool` | `True` when `errors` is empty |
| `errors` | `list[str]` | Human-readable messages; empty list when valid |

Errors are collected from all failed checks. Multiple errors may be returned for a single query.

## FhirValidatorService

Primary orchestration API in `services/validator_service.py`.

### Constructor

```python
FhirValidatorService(
    metadata_url: str,
    server_base: str,
    use_auth: bool = False,
    token_url: str = "",
    client_id: str = "",
    client_secret: str = "",
)
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `metadata_url` | Yes | CapabilityStatement URL (typically `{base}/metadata`) |
| `server_base` | Yes | FHIR server base URL (used for context; not fetched during validation) |
| `use_auth` | No | When `True`, obtain OAuth bearer token before metadata fetch |
| `token_url` | When auth | OAuth token endpoint |
| `client_id` | When auth | OAuth client ID |
| `client_secret` | When auth | OAuth client secret |

**Side effects on construction:**

1. If `use_auth`, call `get_auth_headers()` (may raise `RuntimeError` on missing config or token failure).
2. Fetch CapabilityStatement from `metadata_url` via `load_capability_statement()`.
3. Build `FhirQueryValidator` from the returned JSON.

### `from_env() -> FhirValidatorService`

1. Load `config/.env.local` if present (`load_env_file()`).
2. Resolve `metadata_url` and `server_base` via `resolve_fhir_urls()`.
3. Read OAuth settings via `get_auth_config()`.
4. Return a new `FhirValidatorService` instance.

### `validate_query(query_url: str) -> dict`

| Input condition | `valid` | `errors` |
|-----------------|---------|----------|
| Cannot parse resource type | `False` | `["Unable to parse resource type from query URL."]` |
| Resource type not in CapabilityStatement | `False` | `["Resource type '{type}' is not supported."]` |
| Structural or semantic failures | `False` | One or more error strings from validator |
| All checks pass | `True` | `[]` |

## FhirQueryValidator

Low-level validator constructed from a CapabilityStatement JSON dict. Does not perform HTTP.

| Method | Returns | Description |
|--------|---------|-------------|
| `parse_fhir_query(url)` | `(resource_type, params)` | Delegates to `parse_fhir_query` |
| `validate_resource_type(type)` | `bool` | Whether type appears in CapabilityStatement |
| `validate_fhir_query(type, params)` | `list[str]` | All validation errors |
| `get_allowed_params(type)` | `dict` | Param names → `{modifiers, comparators}` sets |

## Query parser

```python
parse_fhir_query(query_url: str) -> tuple[str | None, dict[str, list[str]]]
```

- `resource_type`: last path segment after stripping leading/trailing slashes; `None` if path is empty.
- `params`: `urllib.parse.parse_qs` result — each value is a `list[str]` (supports repeated params).

## CLI

### Command

```bash
fhir-validate <FHIR_QUERY_URL>
```

Installed via `pip install -e .` entry point `fhir-validate`.

### Behavior

1. Requires exactly one positional argument (the query URL).
2. Constructs `FhirValidatorService.from_env()`.
3. Calls `validate_query(url)`.
4. Prints `Valid: True` or `Valid: False`.
5. Prints `Errors:` followed by bullet lines when errors exist.

### Exit codes

| Code | Condition |
|------|-----------|
| `0` | Query is valid |
| `1` | Query is invalid, or usage error (wrong argument count) |

### Script wrapper

`python3 scripts/run_validator.py "<url>"` — equivalent behavior using the same service.

## Environment variables

Loaded from `config/.env.local` (copy from `config/.env.example`). Never commit `.env.local`.

| Variable | Default | Description |
|----------|---------|-------------|
| `FHIR_DEFAULT_SERVER_KEY` | `hapi` | Preset key: `hapi`, `firely`, `spark`, `wildfhir` |
| `FHIR_METADATA_URL` | (from preset) | Override CapabilityStatement URL |
| `FHIR_SERVER_BASE` | (from preset) | Override FHIR server base URL |
| `FHIR_USE_AUTH` | `false` | Enable OAuth client-credentials (`true`/`1`/`yes`) |
| `TOKEN_URL` | — | OAuth token endpoint |
| `CLIENT_ID` | — | OAuth client ID |
| `CLIENT_SECRET` | — | OAuth client secret |

**Resolution order:** `FHIR_METADATA_URL` / `FHIR_SERVER_BASE` env vars override preset URLs from `FHIR_DEFAULT_SERVER_KEY`. Unknown preset keys fall back to `hapi`.

## Public server registry

Defined in `config/public_servers.py`.

| Key | Name | Metadata URL | Base URL |
|-----|------|--------------|----------|
| `hapi` | HAPI FHIR Reference Server | `https://hapi.fhir.org/baseR4/metadata` | `https://hapi.fhir.org/baseR4` |
| `firely` | Firely Public Server | `https://server.fire.ly/metadata` | `https://server.fire.ly` |
| `spark` | Spark FHIR Reference Server | `https://spark.incendi.no/fhir/metadata` | `https://spark.incendi.no/fhir` |
| `wildfhir` | AEGIS WildFHIR Community Edition | `https://wildfhir.wildfhir.org/r4/metadata` | `https://wildfhir.wildfhir.org/r4` |

All registered servers have `auth_required: false`.

### Registry functions

| Function | Returns |
|----------|---------|
| `get_public_test_server(key)` | `PublicTestServer` dict; raises `KeyError` for unknown key |
| `get_public_test_servers_without_auth()` | List of all no-auth servers |
| `list_public_server_keys()` | `["hapi", "firely", "spark", "wildfhir"]` |
| `get_server_urls(key)` | `{"metadata_url", "base_url"}` |

## HTTP behavior

### CapabilityStatement fetch

`load_capability_statement(url, headers=None, timeout=20)`:

- Sends `Accept: application/fhir+json` on every request.
- Merges optional auth headers (e.g. `Authorization: Bearer ...`).
- Raises `requests.HTTPError` on non-2xx responses.
- Returns parsed JSON dict.

### OAuth

`get_auth_headers(use_auth, token_url, client_id, client_secret)`:

- Returns `{}` when `use_auth` is `False`.
- Raises `RuntimeError` when auth enabled but `TOKEN_URL`, `CLIENT_ID`, or `CLIENT_SECRET` missing.
- POSTs `grant_type=client_credentials` with HTTP basic auth.
- Raises `RuntimeError` when response lacks `access_token`.

## Public exports

From `fhir_validator_agent.__init__`:

| Export | Type |
|--------|------|
| `FhirValidatorService` | Class |
| `FhirValidatorAgent` | Alias for `FhirValidatorService` (deprecated name) |
| `FhirQueryValidator` | Class |
| `parse_fhir_query` | Function |
| `STATIC_VALUESETS` | Dict |
| `is_valid_patient_identifier` | Function |
| `load_capability_statement` | Function |
| `get_auth_headers` | Function |
| `load_env_file` | Function |
| `resolve_fhir_urls` | Function |
| `get_auth_config` | Function |
| `get_default_server` | Function |
| `DEFAULT_PUBLIC_SERVERS` | Dict |
| `PUBLIC_TEST_SERVERS` | Dict |
| `get_public_test_server` | Function |
| `get_public_test_servers_without_auth` | Function |
| `list_public_server_keys` | Function |

## Static value sets

`STATIC_VALUESETS` maps `"ResourceType.param"` → `set[str]` of allowed coded values. See [behavior §2.4](behavior.md#24-semantic-validation).

`is_valid_patient_identifier(identifier) -> tuple[bool, str | None]` — returns `(True, None)` or `(False, reason)`.