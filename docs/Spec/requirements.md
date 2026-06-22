# Requirements — FHIR Search Validator v0.1.0

Formal requirement IDs with verification hooks. Product context lives in the [PRD](../prd.md); this document is the implementation contract.

## Functional requirements

| ID | Requirement | Priority | Spec section | Implementation | Test evidence |
|----|-------------|----------|--------------|----------------|---------------|
| FR-01 | Parse a FHIR search URL into resource type and query parameters | P0 | [behavior §2.1](behavior.md#21-url-parsing) | `core/query_parser.py` | `tests/unit/test_query_parser.py` (7 tests) |
| FR-02 | Fetch and parse a server's CapabilityStatement from `/metadata` | P0 | [behavior §2.2](behavior.md#22-capabilitystatement-indexing) | `infrastructure/capability_index.py` | `tests/unit/test_capability_index.py` (7 tests) |
| FR-03 | Validate resource type against server-declared supported types | P0 | [behavior §2.3](behavior.md#23-structural-validation) | `core/validator.py`, `services/validator_service.py` | `tests/unit/test_validator.py`, `tests/unit/test_service.py` |
| FR-04 | Validate search parameters against server-declared params per resource | P0 | [behavior §2.3](behavior.md#23-structural-validation) | `core/validator.py` | `tests/unit/test_validator.py`, regression cases |
| FR-05 | Validate modifiers and comparators from CapabilityStatement extensions | P0 | [behavior §2.3](behavior.md#23-structural-validation) | `core/validator.py` | `tests/unit/test_validator.py`, regression cases |
| FR-06 | Validate static coded value sets for defined resource.param pairs | P0 | [behavior §2.4](behavior.md#24-semantic-validation) | `core/codeset_validator.py` | `tests/unit/test_validator.py`, `tests/unit/test_codeset_validator.py` |
| FR-07 | Validate `Patient.identifier` against project-specific format rules | P1 | [behavior §2.4](behavior.md#24-semantic-validation) | `core/codeset_validator.py` | `tests/unit/test_codeset_validator.py`, regression cases |
| FR-08 | Return `{valid: bool, errors: list[str]}` result contract | P0 | [interfaces](interfaces.md#result-contract) | `services/validator_service.py` | `tests/unit/test_service.py`, `tests/regression/` |
| FR-09 | Support HAPI R4 and Firely public servers via configuration | P0 | [interfaces §Public servers](interfaces.md#public-server-registry) | `config/public_servers.py`, `config/settings.py` | `tests/unit/test_public_servers_registry.py`, `tests/integration/test_public_servers.py` |
| FR-10 | Support custom servers via `FHIR_METADATA_URL` / `FHIR_SERVER_BASE` | P0 | [interfaces §Environment](interfaces.md#environment-variables) | `config/settings.py` | `tests/unit/test_settings.py` |
| FR-11 | Optional OAuth client-credentials for protected metadata endpoints | P1 | [behavior §2.2](behavior.md#22-capabilitystatement-indexing) | `infrastructure/capability_index.py` | `tests/unit/test_capability_index.py` |
| FR-12 | CLI entry point (`fhir-validate`) and Python API (`FhirValidatorService`) | P0 | [interfaces](interfaces.md) | `cli.py`, `services/validator_service.py` | `tests/unit/test_cli.py`, `tests/unit/test_service.py` |
| FR-13 | Demo notebook with positive and negative test scenarios | P1 | [spec §7](spec.md#7-entry-points) | `examples/notebooks/FHIR_search_validator_demo.ipynb` | Manual E2E (see [e2e-checklist](../e2e-checklist.md)) |
| FR-14 | Unit tests with offline CapabilityStatement fixtures | P0 | [traceability](traceability.md) | `tests/conftest.py`, `tests/unit/` | `pytest -m "not integration"` (85 offline tests) |

## Non-functional requirements

| ID | Requirement | Spec section | Verification |
|----|-------------|--------------|--------------|
| NFR-01 | Python 3.11+ | [interfaces](interfaces.md) | `pyproject.toml` `requires-python` |
| NFR-02 | No secrets committed; environment config via `config/.env.local` | [interfaces §Environment](interfaces.md#environment-variables) | `.gitignore`, `config/.env.example` |
| NFR-03 | Unit tests run without network access | [agent-workflow §5](agent-workflow.md#5-verification-commands) | `pytest -m "not integration"` |
| NFR-04 | Backward-compatible `FhirValidatorAgent` alias | [interfaces §Public exports](interfaces.md#public-exports) | `tests/unit/test_public_api.py` |

## Out of scope (will not)

Explicit non-requirements. These must not be implemented without a new requirement ID and spec update.

| ID | Item | Rationale |
|----|------|-----------|
| OOS-01 | Execute search queries against FHIR servers | Pre-flight validation only |
| OOS-02 | HTTP/REST API service (FastAPI, etc.) | Library + CLI only for v0.1.0 |
| OOS-03 | Google ADK / GenAI agent orchestration | Deferred |
| OOS-04 | Live ValueSet / CodeSystem lookups via Terminology Server | Static value sets used instead |
| OOS-05 | Complete FHIR R4 search specification enforcement | CapabilityStatement is the authority |
| OOS-06 | CapabilityStatement caching or TTL policies | Metadata fetched on service init |
| OOS-07 | Chained search, `_include`, `_revinclude` validation | Not in v0.1.0 |
| OOS-08 | `_sort`, `_count`, `_summary`, `_elements` validation | Special query modifiers not in scope |
| OOS-09 | Multi-tenant deployment / hosted SaaS | Consumer library only |
| OOS-10 | UI or dashboard | CLI, library, and notebook only |

## Coverage gate

| Layer | Minimum coverage | Current (v0.1.0) |
|-------|------------------|------------------|
| `core/` | ≥ 80% | ~98% |
| `services/` | ≥ 80% | ~98% |

Verified via `make test-cov`.