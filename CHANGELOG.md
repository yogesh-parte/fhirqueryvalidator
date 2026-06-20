# Changelog

All notable changes to this project are documented in this file.

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