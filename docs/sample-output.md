# Sample Output

Captured output from executing the FHIR Search Validator on **2026-06-20** against live public test servers (no authentication).

Environment:

- Python 3.14.5
- Package installed via `pip install -e ".[dev]"`
- Default server: HAPI FHIR R4 (`hapi`)

---

## CLI — valid query

```bash
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"
```

```text
Valid: True
```

Exit code: `0`

---

## CLI — invalid query

```bash
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=fe"
```

```text
Valid: False
Errors:
 - Value 'fe' for 'Patient.gender' is not allowed. Allowed values: {'male', 'unknown', 'other', 'female'}
```

Exit code: `1`

---

## Script wrapper

```bash
python3 scripts/run_validator.py "https://hapi.fhir.org/baseR4/Patient?gender=male"
```

```text
Valid: True
```

---

## Python API

```python
from fhir_validator_agent import FhirValidatorService

service = FhirValidatorService(
    metadata_url="https://hapi.fhir.org/baseR4/metadata",
    server_base="https://hapi.fhir.org/baseR4",
)
print(service.validate_query("https://hapi.fhir.org/baseR4/Patient?gender=male"))
print(service.validate_query("https://hapi.fhir.org/baseR4/Patient?gender=fe"))
```

```text
{'valid': True, 'errors': []}
{'valid': False, 'errors': ["Value 'fe' for 'Patient.gender' is not allowed. Allowed values: {'female', 'other', 'male', 'unknown'}"]}
```

---

## Public test server registry

```python
from fhir_validator_agent.config.public_servers import get_public_test_servers_without_auth

for server in get_public_test_servers_without_auth():
    print(f"{server['key']:10} {server['base_url']}")
```

```text
hapi       https://hapi.fhir.org/baseR4
firely     https://server.fire.ly
spark      https://spark.incendi.no/fhir
wildfhir   https://wildfhir.wildfhir.org/r4
```

---

## Firely preset via environment

```bash
export FHIR_DEFAULT_SERVER_KEY=firely
```

```python
from fhir_validator_agent.config.settings import resolve_fhir_urls
from fhir_validator_agent import FhirValidatorService

print("Resolved URLs:", resolve_fhir_urls())
service = FhirValidatorService(
    metadata_url=resolve_fhir_urls()[0],
    server_base=resolve_fhir_urls()[1],
)
print(service.validate_query("https://server.fire.ly/Patient?gender=male"))
```

```text
Resolved URLs: ('https://server.fire.ly/metadata', 'https://server.fire.ly')
{'valid': True, 'errors': []}
```

---

## Multi-server script (`scripts/run_all_tests.py`)

```bash
python3 scripts/run_all_tests.py
```

```text
Testing 2 queries across 4 public servers (no auth)...

--- HAPI FHIR Reference Server (hapi) ---
    Base: https://hapi.fhir.org/baseR4

  Query: Patient?gender=male (expected: positive)
  Result: valid

  Query: Patient?gender=fe (expected: negative)
  Result: invalid
   - Value 'fe' for 'Patient.gender' is not allowed. Allowed values: {'unknown', 'female', 'other', 'male'}

--- Firely Public Server (firely) ---
    Base: https://server.fire.ly

  Query: Patient?gender=male (expected: positive)
  Result: valid

  Query: Patient?gender=fe (expected: negative)
  Result: invalid
   - Value 'fe' for 'Patient.gender' is not allowed. Allowed values: {'unknown', 'female', 'other', 'male'}

--- Spark FHIR Reference Server (spark) ---
    Base: https://spark.incendi.no/fhir

  Query: Patient?gender=male (expected: positive)
  Result: valid

  Query: Patient?gender=fe (expected: negative)
  Result: invalid
   - Value 'fe' for 'Patient.gender' is not allowed. Allowed values: {'unknown', 'female', 'other', 'male'}

--- AEGIS WildFHIR Community Edition (wildfhir) ---
    Base: https://wildfhir.wildfhir.org/r4

  Query: Patient?gender=male (expected: positive)
  Result: valid

  Query: Patient?gender=fe (expected: negative)
  Result: invalid
   - Value 'fe' for 'Patient.gender' is not allowed. Allowed values: {'unknown', 'female', 'other', 'male'}
```

---

## Unit and regression tests

```bash
pytest -m "not integration" -q
```

```text
85 passed, 9 deselected in 0.04s
```

```bash
pytest tests/regression -m regression -q
```

```text
30 passed in 0.01s
```

```bash
make test-unit
```

```text
55 passed in 0.02s
```

---

## Coverage report

```bash
pytest -m "not integration" --cov=fhir_validator_agent --cov-report=term-missing -q
```

```text
........................................................................ [ 84%]
.............                                                            [100%]
================================ tests coverage ================================
_______________ coverage: platform darwin, python 3.14.5-final-0 _______________

Name                                                     Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------------
src/fhir_validator_agent/core/__init__.py                    4      0   100%
src/fhir_validator_agent/core/codeset_validator.py           9      0   100%
src/fhir_validator_agent/core/query_parser.py                9      0   100%
src/fhir_validator_agent/core/validator.py                  57      2    96%   19, 23
src/fhir_validator_agent/services/__init__.py                2      0   100%
src/fhir_validator_agent/services/validator_service.py      29      0   100%
--------------------------------------------------------------------------------------
TOTAL                                                      110      2    98%
Required test coverage of 80.0% reached. Total coverage: 98.18%
85 passed, 9 deselected in 0.06s
```

---

## Integration tests (live public servers)

```bash
pytest tests/integration -m integration -v
```

```text
tests/integration/test_live_servers.py::test_validate_query_against_hapi PASSED
tests/integration/test_public_servers.py::test_public_server_valid_patient_gender[hapi] PASSED
tests/integration/test_public_servers.py::test_public_server_valid_patient_gender[firely] PASSED
tests/integration/test_public_servers.py::test_public_server_valid_patient_gender[spark] PASSED
tests/integration/test_public_servers.py::test_public_server_valid_patient_gender[wildfhir] PASSED
tests/integration/test_public_servers.py::test_public_server_rejects_invalid_gender[hapi] PASSED
tests/integration/test_public_servers.py::test_public_server_rejects_invalid_gender[firely] PASSED
tests/integration/test_public_servers.py::test_public_server_rejects_invalid_gender[spark] PASSED
tests/integration/test_public_servers.py::test_public_server_rejects_invalid_gender[wildfhir] PASSED

9 passed in 5.48s
```

---

## Reproduce locally

```bash
pip install -e ".[dev]"
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"
pytest -m "not integration"
python3 scripts/run_all_tests.py
pytest tests/integration -m integration
```

> **Note:** Integration tests require network access to public FHIR servers. Set order of allowed values in error messages may vary (sets are unordered).