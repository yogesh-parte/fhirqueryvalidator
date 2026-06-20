# Week 2 — Implementation

**Theme:** Harden the CapabilityStatement-driven validator, expand test coverage, and prove end-to-end behavior across real FHIR servers.

**Dates:** Week of 2026-06-23  
**Status:** Mostly complete (~75%)

## Deliverables

| Deliverable | PRD ref | Status | Location |
|-------------|---------|--------|----------|
| Unit + regression test suites | FR-14 | ✅ Done | `tests/unit/`, `tests/regression/` |
| Integration test suite (4 servers) | FR-02 | ✅ Done | `tests/integration/` |
| Multi-server E2E script with summary | — | ✅ Done | `scripts/run_all_tests.py` |
| Test coverage ≥ 80% on core/services | NFR-03 | ✅ Done (98%) | `pytest --cov` |
| Public server registry (no auth) | FR-09 | ✅ Done | `config/public_servers.py` |
| FHIR JSON Accept header | — | ✅ Done | `infrastructure/capability_index.py` |
| Improved error messages | FR-08 | ✅ Partial | string errors with param/value context |
| Structured ValidationError types | FR-08 | ⬜ Pending | — |
| Malformed CapabilityStatement handling | — | ⬜ Pending | — |
| Env config validation at startup | FR-11 | ⬜ Partial | OAuth errors on fetch, not at init |
| Server health check helper | — | ⬜ Pending | — |

## Task breakdown

### Day 1–2: CapabilityStatement hardening

- [x] Pytest unit test suite (`tests/unit/`)
- [x] JSON-driven regression suite (`tests/regression/cases.json`)
- [x] Makefile test targets (`test-unit`, `test-regression`, `test-cov`)
- [x] URL parsing edge cases (trailing slash, encoding, multi-value, relative)
- [ ] Add structured error types (e.g. `ValidationError` with `code`, `param`, `message`)
- [ ] Handle malformed or empty CapabilityStatement responses gracefully
- [ ] Log metadata fetch URL and resource type on validation failure (debug mode)

### Day 3: Server configuration and auth

- [x] Public test server registry with 4 no-auth servers
- [x] Test OAuth path with mock token endpoint (unit test)
- [x] Integration test: HAPI public server (no auth)
- [x] Integration test: Firely public server (no auth)
- [x] Integration test: Spark and WildFHIR
- [ ] Validate env config at startup (clear errors for missing OAuth vars)
- [ ] Add server health check helper (metadata reachable?)
- [ ] Document HAPI vs Firely capability differences in test assertions

### Day 4: Expanded validation scenarios

- [x] Positive/negative cases for Patient and AllergyIntolerance (regression)
- [x] Modifier validation (`:exact`) against fixture
- [x] Comparator validation (`:gt`) against fixture
- [x] Expand `scripts/run_all_tests.py` to report pass/fail summary
- [x] Add pytest marker: `integration`
- [ ] Add pytest marker: `slow`

### Day 5: E2E verification and hardening

- [x] Coverage ≥ 80% on `core/` and `services/`
- [x] Integration bugs fixed (Spark URL, JSON Accept header)
- [x] Sample output captured in `docs/sample-output.md`
- [ ] Formal structured error review

## Acceptance criteria

- [x] `pytest -m "not integration"` passes (85 tests)
- [x] `pytest -m integration` passes (9 tests, 4 servers)
- [x] `python scripts/run_all_tests.py` prints pass/fail summary
- [x] Coverage ≥ 80% on `core/` and `services/`
- [x] Invalid queries return actionable error messages
- [ ] OAuth misconfiguration raises clear error at startup (partial — raises on auth header fetch)