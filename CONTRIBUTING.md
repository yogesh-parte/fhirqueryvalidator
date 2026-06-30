# Contributing

Thank you for contributing to the FHIR Search Validator.

## Getting started

1. Fork the repository
2. Clone your fork and create a branch
3. Read the [Specification](docs/Spec/README.md) — especially [agent-workflow.md](docs/Spec/agent-workflow.md) — before changing validation logic or public APIs
4. Install dev dependencies: `make install-dev`
5. Make changes and add tests
6. Run `make test-cov` before opening a PR

## Branch naming

- `feature/short-description` — new features
- `fix/short-description` — bug fixes
- `docs/short-description` — documentation only

## Pull request process

1. Update or add tests for behavior changes
2. Add regression cases to `tests/regression/cases.json` for validation rule changes
3. Update relevant docs (`docs/`, `README.md`); add an [ADR](docs/adr/README.md) for significant architectural decisions
4. Ensure `pytest -m "not integration"` passes
5. Open a PR against `main` with a clear description

## Test requirements

| Change type | Required tests |
|-------------|----------------|
| Core validation logic | Unit tests + regression case |
| New public server | Registry unit test; verify metadata is JSON |
| Config / settings | Unit tests in `tests/unit/test_settings.py` |
| CLI changes | Tests in `tests/unit/test_cli.py` |

Integration tests (`pytest -m integration`) are optional in PRs but encouraged for server-related changes.

## Code style

- Match existing naming and layer boundaries
- Keep HTTP calls in `infrastructure/` only
- No secrets in code or committed env files
- Run `make lint` before submitting

## Questions

Open an issue at https://github.com/yogesh-parte/fhirqueryvalidator/issues