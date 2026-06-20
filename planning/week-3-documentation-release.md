# Week 3 — Documentation & Release

**Theme:** Complete all user, developer, and operational documentation; finalize CI; ship v0.1.0.

**Dates:** Week of 2026-06-30  
**Status:** In progress (~85%)

## Deliverables

| Deliverable | Audience | Status | Location |
|-------------|----------|--------|----------|
| Configuration guide | Operators | ✅ Done | `docs/configuration.md` |
| Developer guide | Contributors | ✅ Done | `docs/development.md` |
| API reference | Developers | ✅ Done | `docs/api.md` |
| Public test servers guide | All | ✅ Done | `docs/public-test-servers.md` |
| Sample output | All | ✅ Done | `docs/sample-output.md` |
| E2E sign-off checklist | QA | ✅ Done | `docs/e2e-checklist.md` |
| CONTRIBUTING.md | Contributors | ✅ Done | `CONTRIBUTING.md` |
| LICENSE (MIT) | All | ✅ Done | `LICENSE` |
| CHANGELOG | All | ✅ Done | `CHANGELOG.md` |
| CI workflow | Engineering | ✅ Done | `.github/workflows/ci.yml` |
| Release notes / git tag | All | ⬜ Pending | `v0.1.0` tag |

## Task breakdown

### Day 1–2: User and developer documentation

- [x] Configuration guide (`docs/configuration.md`)
- [x] Developer guide (`docs/development.md`)
- [x] API reference (`docs/api.md`)

### Day 3: Contributor and legal docs

- [x] CONTRIBUTING.md
- [x] LICENSE — MIT
- [x] CHANGELOG.md — v0.1.0 initial release notes
- [x] Update README links to all new docs

### Day 4: CI, release pipeline, and operational docs

- [x] GitHub Actions CI (`.github/workflows/ci.yml`)
- [x] Makefile (`install`, `test`, `test-integration`, `lint`)
- [x] E2E sign-off checklist (`docs/e2e-checklist.md`)
- [x] ADR 001 still accurate post-implementation

### Day 5: Release and sign-off

- [x] Offline and integration tests verified (see `docs/sample-output.md`)
- [ ] Run E2E checklist notebook step on clean machine
- [ ] First CI run passes on GitHub
- [ ] Create git tag `v0.1.0`
- [ ] Publish GitHub release with CHANGELOG summary
- [x] Close Week 1–3 planning items (this update)

## Documentation index (current)

```text
docs/
├── prd.md
├── configuration.md
├── development.md
├── api.md
├── public-test-servers.md
├── sample-output.md
├── e2e-checklist.md
└── adr/
    └── 001-fhir-search-validator.md

CONTRIBUTING.md
CHANGELOG.md
LICENSE
README.md
```

## Acceptance criteria

- [x] All documentation files in the index exist
- [x] CONTRIBUTING.md and LICENSE published
- [x] CI workflow committed
- [x] E2E checklist completed (except notebook + CI first run)
- [ ] v0.1.0 tagged with CHANGELOG entry
- [x] README Documentation section links to full doc set