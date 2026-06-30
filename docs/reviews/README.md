# Code Reviews

Timestamped review records for significant changes:

- **Code quality reviews** — five-axis framework (correctness, readability, architecture, security, performance)
- **OWASP security reviews** — `python-owasp-reviewer` SAST + taint analysis (OWASP Top 10)

## Index

| Date (UTC) | Type | Review | Commit / Scope | Verdict |
|------------|------|--------|----------------|---------|
| 2026-06-30 | Code quality | [CapabilityStatement caching](2026-06-30-capability-statement-cache.md) | `bd297b7` | Approve with minor follow-ups |
| 2026-06-30 | OWASP security | [Security review (A01–A10)](2026-06-30-owasp-security-review.md) | `bd297b7` / full `src/` | **Approved** — all findings mitigated; residual DNS rebinding TOCTOU accepted |

## Naming convention

Review files use the pattern:

```text
docs/reviews/YYYY-MM-DD-<short-topic>.md
```

Each file includes:

- Review date and UTC timestamp
- Commit hash and scope
- Findings with per-observation timestamps and severity
- Verification results (tests, coverage)
- Verdict and recommended follow-ups

## Adding a review

1. Create a new file under `docs/reviews/` using the naming convention above.
2. Add a row to the index table in this file.
3. Link related requirement IDs, acceptance criteria, or [ADRs](../adr/README.md) where applicable.