# Week 2 — Implementation

**Theme:** Harden the CapabilityStatement-driven validator, expand test coverage, and prove end-to-end behavior across real FHIR servers.

**Dates:** Week of 2026-06-23  
**Status:** In progress

## Objectives

1. Strengthen core validation logic and error reporting
2. Expand test coverage across resource types and edge cases
3. Prove E2E validation against HAPI and Firely public servers
4. Improve server selection, auth, and operational robustness

## Deliverables

| Deliverable | PRD ref | Location |
|-------------|---------|----------|
| Improved error messages with remediation hints | FR-08 | `core/validator.py` |
| Server selection and URL override hardening | FR-09, FR-10 | `config/settings.py` |
| OAuth error handling for protected endpoints | FR-11 | `infrastructure/capability_index.py` |
| Expanded static value sets (if needed) | FR-06 | `core/codeset_validator.py` |
| Integration test suite (HAPI + Firely) | FR-02 | `tests/integration/` |
| Multi-server E2E script | — | `scripts/run_all_tests.py` |
| Test coverage report ≥ 80% on core/services | NFR-03 | `pytest --cov` |

## Task breakdown

### Day 1–2: CapabilityStatement hardening

- [x] Pytest unit test suite (`tests/unit/`)
- [x] JSON-driven regression suite (`tests/regression/cases.json`)
- [x] Makefile test targets (`test-unit`, `test-regression`, `test-cov`)
- [ ] Add structured error types (e.g. `ValidationError` with `code`, `param`, `message`)
- [ ] Validate edge cases in URL parsing:
  - Trailing slashes
  - Multiple values per parameter
  - URL-encoded values
  - Relative vs absolute URLs
- [ ] Handle malformed or empty CapabilityStatement responses gracefully
- [ ] Log metadata fetch URL and resource type on validation failure (debug mode)
- [ ] Unit tests for each edge case

### Day 3: Server configuration and auth

- [ ] Validate env config at startup (clear errors for missing OAuth vars)
- [ ] Add server health check helper (metadata reachable?)
- [ ] Document Firely vs HAPI capability differences in test assertions
- [ ] Test OAuth path with mock token endpoint (unit test)
- [ ] Integration test: HAPI public server (no auth)
- [ ] Integration test: Firely public server (no auth)

### Day 4: Expanded validation scenarios

- [ ] Add positive/negative test matrix per resource type (at minimum: Patient, AllergyIntolerance)
- [ ] Test modifier validation (`:exact`, `:missing`) against fixture CapabilityStatement
- [ ] Test comparator validation (`:gt`, `:lt`, `:ge`, `:le`) against fixture
- [ ] Expand `scripts/run_all_tests.py` to report pass/fail summary
- [ ] Add pytest markers: `integration`, `slow`

### Day 5: E2E verification and hardening

- [ ] Run full E2E: install → configure → CLI → Python API → notebook
- [ ] Achieve ≥ 80% coverage on `core/` and `services/`
- [ ] Fix any bugs found during integration testing
- [ ] Review error message clarity with sample invalid queries
- [ ] Update unit tests for any API changes

## Test matrix (target)

| Query | Server | Expected | Type |
|-------|--------|----------|------|
| `Patient?gender=male` | HAPI, Firely | Valid | Positive |
| `Patient?gender=fe` | HAPI, Firely | Invalid (value set) | Negative |
| `Patient?unknown=foo` | HAPI, Firely | Invalid (param) | Negative |
| `Patient?gender:missing=true` | HAPI | Depends on capability | Modifier |
| `Patient?birthdate=gt2000-01-01` | HAPI | Depends on capability | Comparator |
| `Patient?identifier=11111111` | HAPI, Firely | Invalid (format) | Negative |
| `Foo?bar=baz` | HAPI, Firely | Invalid (resource type) | Negative |

## Acceptance criteria

- [ ] `pytest -m "not integration"` passes with expanded unit tests
- [ ] `pytest -m integration` passes against HAPI and Firely (or skips gracefully with reason)
- [ ] `python scripts/run_all_tests.py` prints clear pass/fail summary
- [ ] Coverage ≥ 80% on `src/fhir_validator_agent/core/` and `services/`
- [ ] Invalid queries return actionable error messages (param name, allowed values)
- [ ] OAuth misconfiguration raises clear error at startup, not mid-validation

## Dependencies

- Week 1 foundation complete (package, CLI, unit test scaffold)

## Risks

| Risk | Mitigation |
|------|------------|
| Public FHIR servers down or rate-limited | Mark integration tests skippable; use fixtures for CI |
| CapabilityStatement differs between servers | Server-specific assertions; document differences |
| OAuth testing requires real credentials | Mock token endpoint in unit tests; document manual OAuth test |

## References

- [PRD — Approach: CapabilityStatement](../docs/prd.md#2-approach-intelligent-use-of-the-capabilitystatement)
- [PRD — Functional requirements FR-01–FR-14](../docs/prd.md#31-functional-requirements)