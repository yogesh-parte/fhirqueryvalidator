# ADR 001: FHIR Search Validator Architecture

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-06-20 |
| **Related** | [PRD](../prd.md), [Specification](../Spec/spec.md) |

## Context

A notebook-based FHIR search validator demonstrated value in catching invalid queries before they hit live servers. However, the logic was embedded in notebook cells, making it difficult to reuse in CLIs, CI pipelines, or backend services.

FHIR search validation is non-trivial because:

- Each server publishes different capabilities via its **CapabilityStatement** (`/metadata`).
- Search parameters support modifiers (`:exact`) and comparators (`:gt`) that vary per param and per server.
- Some semantic constraints (coded values, identifier formats) are not expressed in the CapabilityStatement and require supplemental rules.

The product goal is defined in the [PRD](../prd.md): provide a pre-flight validator that intelligently uses each server's CapabilityStatement as the primary source of truth.

## Decision

### 1. Extract into a layered Python package

Create a reusable library under `src/fhir_validator_agent/` with clear separation of concerns:

| Layer | Responsibility |
|-------|----------------|
| `config/` | Environment loading, server presets, OAuth settings |
| `core/` | Query parsing, CapabilityStatement-driven validation, static value sets |
| `infrastructure/` | HTTP calls to fetch CapabilityStatement and OAuth tokens |
| `services/` | `FhirValidatorService` orchestration |
| `cli.py` | Console entry point (`fhir-validate`) |

This replaces the original flat module layout and the notebook-embedded logic.

### 2. Use the CapabilityStatement as the primary validation authority

On initialization, `FhirValidatorService` fetches the target server's CapabilityStatement and builds an in-memory index of:

- Supported resource types (`rest[].resource[].type`)
- Search parameters per resource (`rest[].resource[].searchParam[].name`)
- Allowed modifiers (`CapabilityStatementSearchParameterModifiers` extensions)
- Allowed comparators (`CapabilityStatementSearchParameterComparators` extensions)

Query validation checks parsed parameters against this index. This approach is **server-aware** and does not require maintaining a global FHIR search parameter registry in code.

### 3. Supplement with a narrow static value-set layer

Where the CapabilityStatement does not enumerate valid coded values, apply explicit static rules in `core/codeset_validator.py` for:

- `Patient.gender`
- `AllergyIntolerance.verification-status`
- `AllergyIntolerance.clinical-status`
- `Patient.identifier` format constraints

Structural validation is delegated to the CapabilityStatement; semantic validation is added only for defined business rules.

### 4. Standard backend repository layout

Adopt a conventional Python backend structure:

```text
config/                  # .env.example (no secrets committed)
docs/                    # PRD, ADRs
examples/notebooks/      # Demo notebook (moved from notebooks/)
scripts/                 # CLI wrappers and integration scripts
src/fhir_validator_agent/
tests/                   # Unit (offline) and integration (live server) tests
```

### 5. Library + CLI only (no HTTP API)

Expose validation via:

- Python API: `FhirValidatorService.from_env().validate_query(url)`
- CLI: `fhir-validate <url>` (registered in `pyproject.toml`)
- Script wrapper: `scripts/run_validator.py`

No REST API layer in v0.1.0. See [PRD — Out of Scope](../prd.md#4-out-of-scope).

### 6. Backward compatibility

Retain `FhirValidatorAgent` as an alias for `FhirValidatorService` in the public `__init__.py` exports to avoid breaking existing notebook and script imports.

### 7. Configuration via environment files

- Template: `config/.env.example` (committed)
- Secrets: `config/.env.local` (gitignored)
- Supports server presets (`hapi`, `firely`), URL overrides, and optional OAuth client-credentials

## Alternatives Considered

| Alternative | Why not chosen |
|-------------|----------------|
| **Static FHIR search parameter registry** | High maintenance; does not reflect per-server differences |
| **Validate only at request time (no pre-flight)** | Fails late; wastes network and pipeline cycles |
| **Terminology server lookups for all coded values** | Adds infrastructure dependency; out of scope for v0.1.0 |
| **FastAPI HTTP service** | Adds deployment complexity; library + CLI sufficient for initial release |
| **Keep logic in Jupyter notebook** | Poor testability and reuse |

## Consequences

### Positive

- Server-aware validation without hardcoding per-server rules
- Reusable across notebooks, CLIs, and Python backends
- Testable: unit tests use fixture CapabilityStatements; integration tests optional
- Clear documentation trail: PRD defines scope; ADR records architecture
- Enterprise-friendly config pattern (env template + gitignored secrets)

### Negative / trade-offs

- CapabilityStatement is fetched on each service initialization (no caching yet)
- Static value sets must be maintained manually for semantic checks
- Does not validate advanced search features (`_include`, chained searches, etc.)
- CapabilityStatement may not always reflect true server behavior (trust-but-verify)

### Follow-up work

- CapabilityStatement caching and refresh policy
- Expanded value-set validation
- Improved error messages with remediation hints
- See [3-Week Implementation Plan](../../planning/README.md)

## References

- [PRD: FHIR Search Validator](../prd.md)
- [FHIR R4 — CapabilityStatement](https://hl7.org/fhir/R4/capabilitystatement.html)
- [README](../../README.md)