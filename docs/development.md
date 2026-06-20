# Developer Guide

Guide for contributors working on the FHIR Search Validator codebase.

## Local setup

### Prerequisites

- Python 3.11+
- `pip` and a virtual environment

### Install

```bash
git clone https://github.com/yogesh-parte/fhirqueryvalidator.git
cd fhirqueryvalidator

python3 -m venv .venv
source .venv/bin/activate

make install-dev
# equivalent: pip install -e ".[dev,notebook]"
```

### Verify

```bash
make test-cov
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"
```

## Project layout

```text
src/fhir_validator_agent/
├── config/           # Environment settings and public server registry
├── core/             # Query parsing, validation rules, static value sets
├── infrastructure/   # HTTP: CapabilityStatement fetch, OAuth
├── services/         # FhirValidatorService orchestration
└── cli.py            # fhir-validate entry point
```

| Layer | Responsibility |
|-------|----------------|
| `config/` | `settings.py`, `public_servers.py` |
| `core/` | Pure logic — no HTTP |
| `infrastructure/` | External I/O |
| `services/` | Wires layers together |

## Running tests

```bash
make test-unit          # Fast module tests
make test-regression    # JSON-driven regression cases
make test-cov           # Offline tests + 80% coverage gate
make test-integration   # Live public FHIR servers (network)
```

See [sample-output.md](sample-output.md) for expected results.

### Pytest markers

| Marker | Usage |
|--------|-------|
| `integration` | `pytest -m integration` — live servers |
| `regression` | `pytest -m regression` — fixed cases in `tests/regression/cases.json` |

Exclude integration in CI:

```bash
pytest -m "not integration"
```

## Adding a static value set

Edit `src/fhir_validator_agent/core/codeset_validator.py`:

```python
STATIC_VALUESETS = {
    "Patient.gender": {"male", "female", "other", "unknown"},
    "ResourceType.param_name": {"value1", "value2"},
}
```

Add unit tests in `tests/unit/test_codeset_validator.py` and regression cases in `tests/regression/cases.json`.

## Adding a CapabilityStatement fixture

Extend `sample_capability_statement` in `tests/conftest.py` with new resource types and search parameters. Use extensions for modifiers/comparators:

```python
{
    "url": "http://hl7.org/fhir/StructureDefinition/CapabilityStatementSearchParameterModifiers",
    "valueCoding": {"code": "exact"},
}
```

## Adding a public test server

Edit `src/fhir_validator_agent/config/public_servers.py`:

1. Verify `/metadata` returns JSON with `Accept: application/fhir+json`
2. Set `auth_required: False` only for open endpoints
3. Add unit test in `tests/unit/test_public_servers_registry.py`
4. Integration tests auto-include via `get_public_test_servers_without_auth()`
5. Document in `docs/public-test-servers.md`

## Adding a regression case

Append to `tests/regression/cases.json`:

```json
{
  "id": "unique_case_id",
  "description": "What behavior this guards",
  "query": "https://hapi.fhir.org/baseR4/Patient?gender=male",
  "expected_valid": true,
  "expected_errors": []
}
```

For invalid cases, use `expected_error_substrings` instead of exact error lists.

## Code style

- Match existing patterns in the layer you are editing
- Keep `core/` free of HTTP dependencies
- Prefer focused unit tests with fixtures over live-server tests
- Run `make lint` and `make test-cov` before opening a PR

## References

- [API reference](api.md)
- [Configuration guide](configuration.md)
- [ADR 001](adr/001-fhir-search-validator.md)
- [PRD](prd.md)