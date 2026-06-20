# Week 1 — Foundation

**Theme:** Extract, structure, and make the validator reusable as a standard Python backend package.

**Dates:** Week of 2026-06-16  
**Status:** ~80% complete

## Objectives

1. Move validation logic out of notebooks into a layered Python package
2. Provide CLI and Python API entry points
3. Establish configuration and testing foundations
4. Publish initial documentation (README, PRD, ADR)

## Deliverables

| Deliverable | Status | Location |
|-------------|--------|----------|
| Layered package structure | Done | `src/fhir_validator_agent/` |
| `FhirValidatorService` orchestration | Done | `services/validator_service.py` |
| `fhir-validate` CLI | Done | `cli.py`, `pyproject.toml` |
| Environment config template | Done | `config/.env.example` |
| Unit tests (offline) | Done | `tests/unit/` (15 tests) |
| Demo notebook | Done | `examples/notebooks/` |
| README with Quick Start | Done | `README.md` |
| PRD | Done | `docs/prd.md` |
| ADR 001 | Done | `docs/adr/001-fhir-search-validator.md` |

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
- [x] Support HAPI and Firely server presets
- [x] Support optional OAuth client-credentials config
- [x] Add `scripts/run_validator.py` wrapper

### Day 4: Testing foundation

- [x] Set up `tests/` with `conftest.py` and CapabilityStatement fixture
- [x] Unit tests for query parser
- [x] Unit tests for validator (params, modifiers, comparators, value sets)
- [x] Unit tests for patient identifier rules
- [x] Add `requirements-dev.txt` and `pyproject.toml` pytest config
- [ ] Add CI workflow to run unit tests on push (carryover → Week 1 end / Week 3)

### Day 5: Initial documentation

- [x] Write README with architecture mermaid diagram
- [x] Add Quick Start (install, configure, CLI, Python API, tests)
- [x] Write PRD (problem statement, approach, in/out of scope)
- [x] Update ADR 001 with layered architecture decisions
- [x] Move notebook to `examples/notebooks/`

## Remaining Week 1 carryover

These items were planned for Week 1 but slip to early Week 2 if not finished by Friday:

| Task | Owner | Target |
|------|-------|--------|
| GitHub Actions CI for unit tests | Eng | End of Week 1 |
| `Makefile` with `install`, `test`, `lint` targets | Eng | End of Week 1 |
| Validate `pip install -e ".[dev]"` on clean Python 3.11+ env | Eng | End of Week 1 |

## Acceptance criteria

- [x] `pytest -m "not integration"` passes (15 tests)
- [x] `fhir-validate "<url>"` returns valid/invalid result against HAPI
- [x] `from fhir_validator_agent import FhirValidatorService` works after install
- [x] PRD and ADR published under `docs/`
- [ ] CI pipeline runs unit tests automatically

## Dependencies

- None (foundational week)

## Risks

| Risk | Mitigation |
|------|------------|
| Python version mismatch on developer machines | Document Python 3.11+; use `python3` in README |
| Live server unavailable during manual testing | Unit tests use fixtures; integration deferred to Week 2 |

## References

- [PRD — In Scope (v0.1.0)](../docs/prd.md#3-in-scope)
- [ADR 001 — Layered package decision](../docs/adr/001-fhir-search-validator.md)