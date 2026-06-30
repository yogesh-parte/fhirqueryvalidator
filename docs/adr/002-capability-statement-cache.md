# ADR 002: In-Memory CapabilityStatement Cache

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-06-30 |
| **Related** | [ADR 001](001-fhir-search-validator.md), [FR-15](../Spec/requirements.md), [PRD](../prd.md), [Code review](../reviews/2026-06-30-capability-statement-cache.md) |

## Context

`FhirValidatorService` fetches a server's CapabilityStatement from `/metadata` on construction. In typical usage — CLI batch validation, notebooks, or repeated `validate_query` calls — the same metadata URL is requested many times per process.

Fetching metadata on every service instantiation:

- Adds latency (network round-trip per instance)
- Increases load on public FHIR sandboxes during integration and manual testing
- Was acceptable for v0.1.0 but became a bottleneck as usage patterns grew

Requirements for a cache layer:

- Reduce redundant HTTP calls within a single process
- Respect per-server and per-auth-header differences (OAuth bearer tokens)
- Allow operators to tune freshness (TTL) without code changes
- Support explicit invalidation when server capabilities are known to have changed
- Stay within library scope (no new infrastructure dependencies)

## Decision

Add an **in-memory, per-process** CapabilityStatement cache in `infrastructure/capability_cache.py`, integrated into `load_capability_statement()`.

### Cache behavior

| Aspect | Choice |
|--------|--------|
| Storage | In-memory dict, thread-safe via `threading.Lock` |
| Scope | Per Python process (not shared across workers or hosts) |
| Cache key | `metadata_url` + sorted auth headers |
| Default TTL | 86_400 seconds (24 hours) |
| Configuration | `FHIR_CAPABILITY_CACHE_ENABLED`, `FHIR_CAPABILITY_CACHE_TTL_SECONDS` |
| Invalidation | `invalidate_capability_cache(url)` or `FhirValidatorService.refresh_capability()` |
| Bypass | `load_capability_statement(..., use_cache=False)` |
| Test isolation | `reset_capability_cache()` and injectable `cache=` parameter |

### API surface

- **Low-level:** `load_capability_statement()` checks cache before HTTP GET; stores on success only
- **Trigger:** `invalidate_capability_cache(url=None) -> int` returns entries removed
- **Service:** `FhirValidatorService.refresh_capability()` invalidates then reloads for `metadata_url`

Failed HTTP responses are **not** cached.

## Alternatives Considered

### No cache (status quo)

- **Pros:** Simplest; always fresh metadata
- **Cons:** Redundant network calls; slower batch validation
- **Rejected:** Unnecessary cost for stable metadata in typical dev/CI workflows

### Persistent cache (disk or Redis)

- **Pros:** Shared across processes and hosts; survives restarts
- **Cons:** New dependency or ops complexity; stale-data risk across tenants; overkill for embeddable library
- **Rejected:** Out of scope for v0.1.x; documented as OOS-06 in [requirements.md](../Spec/requirements.md)

### HTTP cache headers (`Cache-Control`, ETag)

- **Pros:** Standard protocol; server-driven freshness
- **Cons:** Not all FHIR servers emit reliable cache headers; harder to test offline; less explicit control for library consumers
- **Rejected:** Application-level TTL is simpler and predictable for this use case

### Cache inside `FhirValidatorService` only

- **Pros:** No global state
- **Cons:** Duplicate fetches when multiple service instances are created; `load_capability_statement()` callers would not benefit
- **Rejected:** Cache belongs at the HTTP fetch layer where all consumers converge

## Consequences

### Positive

- Repeated validation against the same server reuses metadata within TTL
- Multiple `FhirValidatorService` instances for one URL share a single cache entry
- Trigger-based invalidation supports operational refresh without process restart
- Configurable TTL and disable flag via environment variables
- 17 dedicated unit tests; FR-15 traceability in spec

### Negative / trade-offs

- **Stale metadata:** Validation may use outdated capabilities until TTL expires or explicit invalidation
- **Unbounded growth:** No LRU or max entry count; many unique URLs in one long-lived process could grow memory (acceptable for typical few-server usage)
- **Shared mutable objects:** Cache returns the same dict reference; caller mutation affects all consumers (pre-existing `cap_json` pattern, amplified by sharing)
- **Per-process only:** Multi-worker deployments (e.g. Gunicorn) each maintain separate caches
- **Auth in cache keys:** Bearer tokens stored in memory as part of key construction; not suitable for untrusted shared processes

### Follow-up work

- Return defensive copies from cache `get()` to prevent cross-instance mutation
- Extend coverage gate to `infrastructure/` in `pyproject.toml`
- Persistent or distributed cache if HTTP API or multi-tenant hosting is added (see PRD future considerations)

## References

- [ADR 001: FHIR Search Validator Architecture](001-fhir-search-validator.md)
- [Configuration guide — CapabilityStatement cache](../configuration.md#capabilitystatement-cache)
- [API reference — cache functions](../api.md)
- [Behavior spec §2.2](../Spec/behavior.md#22-capabilitystatement-indexing)
- [Code review 2026-06-30](../reviews/2026-06-30-capability-statement-cache.md)