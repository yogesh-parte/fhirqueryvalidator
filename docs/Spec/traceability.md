# Traceability — FHIR Search Validator v0.1.0

Requirement → implementation → test mapping. Update this file when adding requirements, code, or tests.

## Functional requirements

| Req | Implementation | Unit tests | Regression / integration |
|-----|----------------|------------|--------------------------|
| FR-01 | `core/query_parser.py` | `test_query_parser.py` (7) | `relative_url_patient_gender` |
| FR-02 | `infrastructure/capability_index.py` | `test_capability_index.py` (10) | `test_public_servers.py`, `test_live_servers.py` |
| FR-03 | `core/validator.py`, `services/validator_service.py` | `test_validator.py`, `test_service.py` | `unsupported_resource_type` |
| FR-04 | `core/validator.py` | `test_validator.py` | `patient_unknown_param` |
| FR-05 | `core/validator.py` | `test_validator.py` | `patient_gender_exact_modifier_valid`, `patient_gender_missing_modifier_invalid`, `patient_birthdate_gt_comparator_valid` |
| FR-06 | `core/codeset_validator.py`, `core/validator.py` | `test_validator.py`, `test_codeset_validator.py` | `patient_gender_invalid_value`, `allergy_clinical_status_*` |
| FR-07 | `core/codeset_validator.py` | `test_codeset_validator.py` (6) | `patient_identifier_*` cases |
| FR-08 | `services/validator_service.py` | `test_service.py` (7) | All 15 regression cases |
| FR-09 | `config/public_servers.py` | `test_public_servers_registry.py` (5) | `test_public_servers.py` (8 parametrized) |
| FR-10 | `config/settings.py` | `test_settings.py` (6) | — |
| FR-11 | `infrastructure/capability_index.py` | `test_capability_index.py` | — |
| FR-12 | `cli.py`, `services/validator_service.py` | `test_cli.py` (3), `test_service.py` | AC-12–AC-14 |
| FR-13 | `examples/notebooks/FHIR_search_validator_demo.ipynb` | — | Manual E2E checklist |
| FR-14 | `tests/conftest.py` (fixture) | All `tests/unit/` (74 tests) | `test_regression.py` (30 runs: 15 cases × 2 paths) |
| FR-15 | `infrastructure/capability_cache.py`, `config/settings.py` | `test_capability_cache.py` (9), `test_settings_cache.py` (5), `test_capability_index.py`, `test_service.py` | — ([ADR 002](../adr/002-capability-statement-cache.md)) |

## Non-functional requirements

| Req | Implementation | Verification |
|-----|----------------|--------------|
| NFR-01 | `pyproject.toml` | `requires-python = ">=3.11"` |
| NFR-02 | `config/.env.example`, `.gitignore` | No `.env.local` in repo |
| NFR-03 | Test markers in `pyproject.toml` | `pytest -m "not integration"` |
| NFR-04 | `__init__.py` alias | `test_public_api.py::test_fhir_validator_agent_alias` |

## Regression case → acceptance criteria

| Regression ID | AC ID |
|---------------|-------|
| `patient_gender_male_valid` | AC-01 |
| `patient_gender_invalid_value` | AC-02 |
| `patient_unknown_param` | AC-03 |
| `patient_gender_exact_modifier_valid` | AC-04 |
| `patient_gender_missing_modifier_invalid` | AC-05 |
| `patient_birthdate_gt_comparator_valid` | AC-06 |
| `patient_identifier_valid` | AC-07 |
| `patient_identifier_all_identical_digits` | AC-08 |
| `unsupported_resource_type` | AC-09 |
| `relative_url_patient_gender` | AC-10 |
| `multiple_params_one_invalid` | AC-11 |
| `patient_gender_female_valid` | AC-01 (variant) |
| `patient_identifier_too_short` | AC-08 (variant) |
| `allergy_clinical_status_active_valid` | FR-06 coverage |
| `allergy_clinical_status_invalid` | FR-06 coverage |

## Component → file map

| Layer | Files |
|-------|-------|
| Config | `config/settings.py`, `config/public_servers.py`, `config/__init__.py` |
| Core | `core/query_parser.py`, `core/validator.py`, `core/codeset_validator.py` |
| Infrastructure | `infrastructure/capability_index.py`, `infrastructure/capability_cache.py` |
| Services | `services/validator_service.py` |
| CLI | `cli.py` |
| Package | `__init__.py` |

## Test suite summary

| Suite | Location | Count | Network |
|-------|----------|-------|---------|
| Unit | `tests/unit/` | 74 | No |
| Regression | `tests/regression/` | 30 (15 cases × 2) | No |
| Integration | `tests/integration/` | 9+ | Yes |
| **Offline total** | unit + regression | **104** | No |

## Error catalog → tests

| Error ID | Verified by |
|----------|-------------|
| ERR-01 | `test_service.py::test_validate_query_unparseable_resource_type` |
| ERR-02 | `test_service.py::test_validate_query_unsupported_resource`, `unsupported_resource_type` |
| ERR-03 | `test_validator.py::test_unknown_search_param`, `patient_unknown_param` |
| ERR-04 | `test_validator.py::test_disallowed_modifier`, `patient_gender_missing_modifier_invalid` |
| ERR-05 | `test_validator.py::test_invalid_gender_value`, regression gender/allergy cases |
| ERR-06 | `test_codeset_validator.py`, `patient_identifier_*` cases |