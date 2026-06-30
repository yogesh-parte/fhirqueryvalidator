# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- In-memory CapabilityStatement cache with configurable TTL (default 24 hours)
- `invalidate_capability_cache()` for trigger-based cache invalidation (per URL or global)
- `FhirValidatorService.refresh_capability()` to invalidate and reload metadata for the current server
- Environment variables `FHIR_CAPABILITY_CACHE_ENABLED` and `FHIR_CAPABILITY_CACHE_TTL_SECONDS`
- Unit tests for cache TTL, invalidation, and shared cache across service instances

## [0.1.0] - 2026-06-20

### Added

- Layered Python package (`config/`, `core/`, `infrastructure/`, `services/`)
- `FhirValidatorService` with CapabilityStatement-driven validation
- `fhir-validate` CLI entry point
- Public test server registry (HAPI, Firely, Spark, WildFHIR) — no authentication required
- Static value-set validation for Patient gender and AllergyIntolerance statuses
- Patient identifier format rules
- Unit test suite (55 tests), regression suite (30 cases), integration tests (9 cases)
- `Makefile` with install, test, and coverage targets
- Documentation: PRD, ADR, configuration guide, developer guide, API reference, sample output
- GitHub Actions CI for offline tests and coverage

### Changed

- Extracted validator from notebook into reusable library
- Renamed orchestrator to `FhirValidatorService` (`FhirValidatorAgent` alias retained)

### Fixed

- Spark FHIR metadata URL (`/fhir/metadata`)
- FHIR JSON `Accept` header for servers returning XML by default