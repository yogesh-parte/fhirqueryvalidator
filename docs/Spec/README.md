# Specification — Spec-Driven Development (SDD)

This folder contains the **implementation specification** for the FHIR Search Validator. It is the authoritative contract for developers and AI agents.

## Showcase intent

> **Ideal SDD flow:** Specification → Implementation → Tests → Verify against Spec.

This repository demonstrates that specifications can also be **extracted retroactively** from a working system. Version 0.1.0 was built organically (notebook → package → tests → docs). The Spec folder formalizes what was built so that **v0.2+ work follows true spec-driven discipline**.

## Document hierarchy

| Layer | Location | Audience | Purpose |
|-------|----------|----------|---------|
| Product | [../prd.md](../prd.md) | Stakeholders | Why we built it; business scope |
| Architecture | [../adr/README.md](../adr/README.md) | Engineers | Design decisions and trade-offs (ADRs) |
| **Specification** | **this folder** | **Agents + implementers** | **What the system must do** |
| Operations | [../configuration.md](../configuration.md) | Operators | How to configure and run |
| API reference | [../api.md](../api.md) | Developers | Quick API lookup |
| Code reviews | [../reviews/README.md](../reviews/README.md) | Engineers | Timestamped review records |

**Rule:** For implementation truth, Spec overrides PRD. PRD provides product context only.

## Spec index

| Document | Description |
|----------|-------------|
| [spec.md](spec.md) | **Start here** — master system specification |
| [requirements.md](requirements.md) | FR/NFR/OOS requirement IDs with verification |
| [interfaces.md](interfaces.md) | API, CLI, environment, and result contracts |
| [behavior.md](behavior.md) | Validation rules, error catalog, scenarios |
| [acceptance-criteria.md](acceptance-criteria.md) | Given/When/Then acceptance tests |
| [traceability.md](traceability.md) | Requirement → code → test mapping |
| [agent-workflow.md](agent-workflow.md) | How agents must use specs before coding |

## Agent rules (summary)

1. Read [spec.md](spec.md) before any feature or fix work.
2. Every change must trace to a requirement ID in [requirements.md](requirements.md).
3. Update [behavior.md](behavior.md) and [acceptance-criteria.md](acceptance-criteria.md) before changing validation logic.
4. Add regression cases to `tests/regression/cases.json` for new behavioral rules.
5. Update [traceability.md](traceability.md) when adding requirements or tests.
6. Verify with `pytest -m "not integration"` and `make test-cov`.

Full instructions: [agent-workflow.md](agent-workflow.md).