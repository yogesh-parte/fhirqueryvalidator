# Code Review: CapabilityStatement Caching

| Field | Value |
|-------|-------|
| **Review date** | 2026-06-30 |
| **Review time (UTC)** | 2026-06-30T14:00:00Z |
| **Reviewer** | AI code review (`code-review-and-quality` skill) |
| **Commit** | `bd297b76465edf0c85eea7149ab6e6b7e1cd2d76` |
| **Commit message** | `added caching for the capability statement` |
| **Scope** | In-memory CapabilityStatement cache (TTL, invalidation), tests, documentation |
| **Verdict** | **Approve with minor follow-ups** |

---

## Context

This change adds in-memory CapabilityStatement caching with a 24-hour default TTL, trigger-based invalidation (`invalidate_capability_cache`, `refresh_capability`), environment configuration, tests, and spec/README updates.

**Files changed (27):** +640 / −41 lines across `src/`, `tests/`, `config/`, and documentation.

**Verification run at review time:**

| Check | Result |
|-------|--------|
| `pytest -m "not integration"` | 104 passed |
| `make test-cov` | 98.26% on gated `core/` + `services/` (gate: 80%) |

---

## 1. Correctness

| # | Finding | Severity | Timestamp |
|---|---------|----------|-----------|
| C-01 | Cache returns the **same dict object** by reference. Multiple `FhirValidatorService` instances for one URL now share one object. Caller mutation of `service.cap_json` corrupts the cache for all consumers. | **Consider** | 2026-06-30T14:00:00Z |
| C-02 | TTL expiry, header-scoped keys, invalidation, and `refresh_capability()` are implemented correctly and well tested. | Pass | 2026-06-30T14:00:00Z |
| C-03 | `FHIR_CAPABILITY_CACHE_TTL_SECONDS=0` behaves as documented (expires on next read). | Pass | 2026-06-30T14:00:00Z |
| C-04 | Failed HTTP responses are not cached (only successful `response.json()` paths write). | Pass | 2026-06-30T14:00:00Z |

**Test gaps (minor):**

- No test wiring `get_capability_cache()` singleton to env vars end-to-end.
- No test for `use_cache=True` when global cache is disabled (override path).

**Note:** The shared-mutable-object risk existed before caching, but caching amplifies it. A shallow `copy.copy(cached)` on `get()` / before `set()` would make the cache safer without much cost.

---

## 2. Readability & Simplicity

| # | Finding | Severity | Timestamp |
|---|---------|----------|-----------|
| R-01 | `capability_cache.py` is ~90 lines with clear naming and straightforward lock usage. | Pass | 2026-06-30T14:00:00Z |
| R-02 | `load_capability_statement()` integration is minimal — check cache, fetch, store. | Pass | 2026-06-30T14:00:00Z |
| R-03 | Commit message `added caching for the capability statement` is vague; prefer imperative form e.g. `Add in-memory CapabilityStatement cache with TTL and invalidation`. | **Nit** | 2026-06-30T14:00:00Z |

---

## 3. Architecture

| # | Finding | Severity | Timestamp |
|---|---------|----------|-----------|
| A-01 | Cache in `infrastructure/`, config in `settings.py`, orchestration in `validator_service.py` — matches layered design. | Pass | 2026-06-30T14:00:00Z |
| A-02 | Singleton + injectable `cache=` parameter is a good testability pattern. | Pass | 2026-06-30T14:00:00Z |
| A-03 | `reset_capability_cache()` is exported publicly (`infrastructure/__init__.py`) but is primarily a test hook. | **Optional** | 2026-06-30T14:00:00Z |
| A-04 | No circular dependencies introduced. | Pass | 2026-06-30T14:00:00Z |

**Structural note:** Design is appropriately scoped — no over-engineering (no Redis, no disk persistence). Aligns with updated OOS-06 boundary in the spec.

---

## 4. Security

| # | Finding | Severity | Timestamp |
|---|---------|----------|-----------|
| S-01 | Bearer tokens appear in cache keys (in-memory only, per process). Acceptable for this library; cache is not safe for multi-tenant shared processes. | **FYI** | 2026-06-30T14:00:00Z |
| S-02 | No secrets logged; no new dependencies. | Pass | 2026-06-30T14:00:00Z |
| S-03 | External metadata still validated via `raise_for_status()` before caching. | Pass | 2026-06-30T14:00:00Z |

---

## 5. Performance

| # | Finding | Severity | Timestamp |
|---|---------|----------|-----------|
| P-01 | Cache eliminates redundant `/metadata` HTTP calls — clear win for CLI/notebook batch validation. | Pass | 2026-06-30T14:00:00Z |
| P-02 | Cache is **unbounded** (no LRU/max entries). Fine for typical use (few servers); long-running processes hitting many unique URLs could grow memory without bound. | **Optional** | 2026-06-30T14:00:00Z |
| P-03 | Thread-safe reads/writes via `threading.Lock` — appropriate for sync `requests` usage. | Pass | 2026-06-30T14:00:00Z |

---

## 6. Documentation & Spec

| # | Finding | Severity | Timestamp |
|---|---------|----------|-----------|
| D-01 | README, Spec (FR-15, AC-20–22), API, configuration, ADR, PRD, traceability updated consistently. | Pass | 2026-06-30T14:00:00Z |
| D-02 | `pyproject.toml` coverage gate only covers `core/` and `services/` — `infrastructure/capability_cache.py` is untracked by coverage reporting despite 9 dedicated tests. | **Optional** | 2026-06-30T14:00:00Z |

---

## Review Checklist

| Item | Status |
|------|--------|
| Change intent and spec alignment understood (FR-15) | ✅ |
| Matches spec/task requirements | ✅ |
| Edge cases largely handled (TTL, invalidation, auth headers) | ✅ |
| Error paths: HTTP errors not cached; mutable shared objects | ⚠️ |
| Tests cover core behavior adequately | ✅ |
| Clear names, straightforward flow | ✅ |
| Follows existing patterns | ✅ |
| No new security vulnerabilities | ✅ |
| Net performance improvement | ✅ |
| 104 offline tests pass | ✅ |
| Coverage gate passes (on configured layers) | ✅ |

---

## Recommended Follow-ups

| Priority | Action | Severity | Timestamp |
|----------|--------|----------|-----------|
| 1 | Return `copy.copy(cached)` from cache `get()` to prevent cross-instance corruption via shared dict mutation. | **Consider** | 2026-06-30T14:00:00Z |
| 2 | Extend `[tool.coverage.report] include` in `pyproject.toml` to `infrastructure/*` so new infra code is gated. | **Optional** | 2026-06-30T14:00:00Z |
| 3 | Document unbounded cache growth and per-process/multi-tenant limitations in `docs/configuration.md`. | **Optional** | 2026-06-30T14:00:00Z |
| 4 | Use imperative, descriptive commit messages on future commits. | **Nit** | 2026-06-30T14:00:00Z |

---

## Final Verdict

**Approve with minor follow-ups.**

The change is solid, well-tested, and documented. It clearly improves code health and matches the updated spec. Nothing blocks merge.

Safe to merge as-is if the shared-mutable-dict trade-off is accepted (consistent with pre-existing `cap_json` handling).

---

## Related

- Commit: `bd297b7`
- Requirement: FR-15
- Acceptance criteria: AC-20, AC-21, AC-22
- ADR: [ADR 002 — In-Memory CapabilityStatement Cache](../adr/002-capability-statement-cache.md)
- Review skill: `code-review-and-quality` (five-axis review)