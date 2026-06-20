# Week 3 — Documentation & Release

**Theme:** Complete all user, developer, and operational documentation; finalize CI; ship v0.1.0.

**Dates:** Week of 2026-06-30  
**Status:** Not started

## Objectives

1. Publish complete documentation for users, developers, and operators
2. Establish CI/CD and release process
3. Run full end-to-end sign-off on a clean environment
4. Tag and release v0.1.0

## Deliverables

| Deliverable | Audience | Location |
|-------------|----------|----------|
| Configuration guide | Operators | `docs/configuration.md` |
| Developer guide | Contributors | `docs/development.md` |
| API reference | Developers | `docs/api.md` |
| CONTRIBUTING.md | Contributors | `CONTRIBUTING.md` |
| LICENSE (MIT) | All | `LICENSE` |
| CHANGELOG | All | `CHANGELOG.md` |
| CI workflow | Engineering | `.github/workflows/ci.yml` |
| Release notes | All | GitHub release / `CHANGELOG.md` |
| E2E sign-off checklist | QA | `docs/e2e-checklist.md` |

## Task breakdown

### Day 1–2: User and developer documentation

- [ ] **Configuration guide** (`docs/configuration.md`)
  - All env variables with examples
  - HAPI vs Firely setup walkthrough
  - OAuth client-credentials setup
  - Troubleshooting (metadata unreachable, auth failures)
- [ ] **Developer guide** (`docs/development.md`)
  - Local setup and dev dependencies
  - Project layout and layer responsibilities
  - How to add static value sets
  - How to add new resource type test fixtures
  - Running unit vs integration tests
- [ ] **API reference** (`docs/api.md`)
  - `FhirValidatorService` methods and return contract
  - `FhirQueryValidator` for advanced/direct use
  - CLI usage (`fhir-validate`)
  - Code examples for library integration

### Day 3: Contributor and legal docs

- [ ] **CONTRIBUTING.md**
  - Branch naming, PR process, commit conventions
  - Test requirements before merge
  - Code style (match existing patterns)
- [ ] **LICENSE** — MIT
- [ ] **CHANGELOG.md** — v0.1.0 initial release notes
- [ ] Update README links to all new docs
- [ ] Update PRD "Last updated" and cross-references

### Day 4: CI, release pipeline, and operational docs

- [ ] **GitHub Actions CI** (`.github/workflows/ci.yml`)
  - Python 3.11, 3.12 matrix
  - `pip install -e ".[dev]"`
  - `pytest -m "not integration" --cov`
  - Fail on coverage below threshold (80% core/services)
- [ ] **Makefile** (if not done in Week 1)
  - `make install`, `make test`, `make test-integration`, `make lint`
- [ ] **E2E sign-off checklist** (`docs/e2e-checklist.md`)
  - Clean install walkthrough
  - CLI positive/negative cases
  - Python API example
  - Notebook execution
  - Multi-server integration script
- [ ] **ADR review** — confirm ADR 001 still accurate post-implementation

### Day 5: Release and sign-off

- [ ] Run E2E checklist on clean machine (Python 3.11+)
- [ ] Final `pytest` run (unit + integration)
- [ ] Review all docs for broken links and outdated paths
- [ ] Bump version to `0.1.0` in `pyproject.toml` (if not already)
- [ ] Create git tag `v0.1.0`
- [ ] Publish release notes summarizing:
  - CapabilityStatement-driven validation
  - CLI and Python API
  - Supported servers and configuration
  - Test coverage and documentation index
- [ ] Close Week 1–3 planning items; archive completed tasks

## Documentation index (target state)

```text
docs/
├── prd.md                      # Product requirements (done)
├── adr/
│   └── 001-fhir-search-validator.md  # Architecture (done)
├── configuration.md            # Operator guide
├── development.md              # Contributor dev guide
├── api.md                      # API reference
└── e2e-checklist.md            # Release sign-off checklist

CONTRIBUTING.md
CHANGELOG.md
LICENSE
README.md                       # Entry point with links to all docs
```

## E2E sign-off checklist (summary)

| Step | Command / action | Pass? |
|------|------------------|-------|
| Clean install | `pip install -e ".[dev,notebook]"` | |
| Unit tests | `pytest -m "not integration"` | |
| CLI valid query | `fhir-validate "…/Patient?gender=male"` | |
| CLI invalid query | `fhir-validate "…/Patient?gender=fe"` | |
| Python API | `FhirValidatorService.from_env().validate_query(...)` | |
| Multi-server script | `python scripts/run_all_tests.py` | |
| Integration tests | `pytest -m integration` | |
| Notebook | Run `examples/notebooks/FHIR_search_validator_demo.ipynb` | |
| Docs review | All links in README resolve | |

## Acceptance criteria

- [ ] All documentation files in the index exist and are accurate
- [ ] CONTRIBUTING.md and LICENSE published
- [ ] CI passes on main branch
- [ ] E2E checklist completed with all items passing
- [ ] v0.1.0 tagged with CHANGELOG entry
- [ ] README "Documentation" section links to full doc set
- [ ] PRD success criteria (Section 1) verified against delivered product

## Dependencies

- Week 2 implementation complete and stable
- Integration tests passing or documented skip reasons

## Risks

| Risk | Mitigation |
|------|------------|
| Documentation drift from code | Generate API examples from tested code paths |
| Release blocked by flaky integration tests | CI runs unit only; integration manual pre-release |
| Missing legal/contribution docs delay adoption | Prioritize LICENSE and CONTRIBUTING on Day 3 |

## Post-release (beyond Week 3)

Items explicitly deferred to future releases:

- CapabilityStatement caching
- HTTP API wrapper
- Google ADK agent integration
- Expanded terminology validation
- Chained search and `_include` support

Track these in a future `planning/backlog.md` if needed.

## References

- [PRD — Success criteria](../docs/prd.md#1-problem-statement)
- [PRD — Deliverables](../docs/prd.md#33-deliverables-current-release)
- [3-Week Plan overview](README.md)