# E2E Sign-off Checklist

Release readiness checklist for v0.1.0. Last verified: **2026-06-20**.

| Step | Command / action | Pass? |
|------|------------------|-------|
| Clean install | `pip install -e ".[dev,notebook]"` | ✅ |
| Unit + regression tests | `pytest -m "not integration"` | ✅ (85 passed) |
| Coverage ≥ 80% | `make test-cov` | ✅ (98%) |
| CLI valid query | `fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"` | ✅ |
| CLI invalid query | `fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=fe"` | ✅ |
| Python API | `FhirValidatorService.from_env().validate_query(...)` | ✅ |
| Multi-server script | `python3 scripts/run_all_tests.py` | ✅ (4 servers) |
| Integration tests | `pytest tests/integration -m integration` | ✅ (9 passed) |
| Notebook | `examples/notebooks/FHIR_search_validator_demo.ipynb` | ⬜ manual |
| Docs links in README | All documentation links resolve | ✅ |
| No secrets in repo | `.env.local` gitignored | ✅ |
| CI workflow | `.github/workflows/ci.yml` passes on push | ⬜ pending first CI run |
| Git tag | `v0.1.0` created | ⬜ pending |

## Reproduce

```bash
pip install -e ".[dev,notebook]"
pytest -m "not integration" -v
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=male"
fhir-validate "https://hapi.fhir.org/baseR4/Patient?gender=fe"
python3 scripts/run_all_tests.py
pytest tests/integration -m integration -v
```

Captured output: [sample-output.md](sample-output.md)