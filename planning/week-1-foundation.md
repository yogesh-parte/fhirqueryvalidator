# Week 1 — Foundation

**Theme:** Extract, structure, and make the validator reusable as a standard Python backend package.

**Dates:** April 24 – April 30, 2026  
**Delivery milestone:** May 15, 2026  
**Status:** Complete (~95%)

## Deliverables

| Deliverable | Status | Location |
|-------------|--------|----------|
| Layered package structure | ✅ Done | `src/fhir_validator_agent/` |
| `FhirValidatorService` orchestration | ✅ Done | `services/validator_service.py` |
| `fhir-validate` CLI | ✅ Done | `cli.py`, `pyproject.toml` |
| Environment config template | ✅ Done | `config/.env.example` |
| Unit tests (offline) | ✅ Done | `tests/unit/` (55 tests) |
| Demo notebook | ✅ Done | `examples/notebooks/` |
| README with Quick Start | ✅ Done | `README.md` |
| PRD | ✅ Done | `docs/prd.md` |
| ADR 001 | ✅ Done | `docs/adr/001-fhir-search-validator.md` |
| Makefile | ✅ Done | `Makefile` |
| GitHub Actions CI | ✅ Done | `.github/workflows/ci.yml` |

## Task breakdown

### Day 1–2: Package extraction and layering

- [x] Extract validator logic from notebook into Python modules
- [x] Organize into `config/`, `core/`, `infrastructure/`, `services/`
- [x] Extract settings from monolithic agent into `config/settings.py`
- [x] Preserve `FhirValidatorAgent` backward-compatible alias
- [x] Register `fhir-validate` console script in `pyproject.toml`

### Day 3: Configuration and entry points

- [x] Create `config/.env.example` with documented variables
- [x] Gitignore secret env files (`config/.env.local`)
- [x] Support HAPI and Firely server presets (extended to Spark, WildFHIR)
- [x] Support optional OAuth client-credentials config
- [x] Add `scripts/run_validator.py` wrapper

### Day 4: Testing foundation

- [x] Set up `tests/` with `conftest.py` and CapabilityStatement fixture
- [x] Unit tests for query parser, validator, codesets
- [x] Add `requirements-dev.txt` and `pyproject.toml` pytest config
- [x] Add CI workflow to run unit tests on push

### Day 5: Initial documentation

- [x] Write README with architecture mermaid diagram
- [x] Add Quick Start (install, configure, CLI, Python API, tests)
- [x] Write PRD (problem statement, approach, in/out of scope)
- [x] Update ADR 001 with layered architecture decisions
- [x] Move notebook to `examples/notebooks/`

## Acceptance criteria

- [x] `pytest -m "not integration"` passes (85 tests)
- [x] `fhir-validate "<url>"` returns valid/invalid result against HAPI
- [x] `from fhir_validator_agent import FhirValidatorService` works after install
- [x] PRD and ADR published under `docs/`
- [x] CI pipeline runs unit tests automatically