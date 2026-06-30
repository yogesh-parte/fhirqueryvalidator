# Architecture Decision Records (ADRs)

ADRs capture **why** significant technical decisions were made — context, alternatives considered, and trade-offs. Code shows what was built; ADRs explain the reasoning for future engineers and agents.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-fhir-search-validator.md) | FHIR Search Validator Architecture | Accepted | 2026-06-20 |
| [002](002-capability-statement-cache.md) | In-Memory CapabilityStatement Cache | Accepted | 2026-06-30 |

## Lifecycle

```text
PROPOSED → ACCEPTED → (SUPERSEDED or DEPRECATED)
```

Do not delete superseded ADRs. Write a new ADR that references and supersedes the old one.

## When to write an ADR

- Choosing a framework, library, or major dependency
- Significant API or behavioral contract changes
- Infrastructure patterns (caching, auth, persistence)
- Any decision that would be expensive to reverse

## Naming convention

```text
docs/adr/NNN-short-topic.md
```

Sequential numbering. Link related requirement IDs, spec sections, and code reviews where applicable.

## Related documentation

| Layer | Location |
|-------|----------|
| Product scope | [PRD](../prd.md) |
| Implementation spec | [Spec](../Spec/README.md) |
| Code reviews | [Reviews](../reviews/README.md) |
| Configuration | [configuration.md](../configuration.md) |
| API reference | [api.md](../api.md) |