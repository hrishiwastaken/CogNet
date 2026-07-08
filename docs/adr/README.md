# Architecture Decision Records

Index of ADRs for CogNet v2.1. Each ADR follows `docs/ADR_TEMPLATE.md`.

An ADR is required whenever a decision is expensive to reverse once Phase 1
code or data depends on it (CLAUDE.md, "If the specification is ambiguous").

| ADR | Title | Status | Affected invariants |
|---|---|---|---|
| [ADR-001](ADR-001-identity-and-id-scheme.md) | Identity and ID Scheme | Accepted | I-014 |
| [ADR-002](ADR-002-controller-budget-units.md) | Controller Budget Units | Accepted | I-003 |
| [ADR-003](ADR-003-persistence-layout.md) | Persistence Layout | Accepted | I-006 |
| [ADR-004](ADR-004-scope-cardinality-and-promotion.md) | Scope Cardinality and Cross-Scope Promotion | Accepted | I-006, I-010 |
| [ADR-005](ADR-005-trust-taint-reliability.md) | Trust, Taint, and Contextual Reliability | Accepted | I-008, I-011, I-015 |
| [ADR-006](ADR-006-legacy-application-disposition.md) | Legacy Application Disposition | Accepted | I-020 |
| [ADR-007](ADR-007-governance-tooling-status.md) | Governance Tooling Status | Accepted | I-013, I-004 |
| [ADR-008](ADR-008-causal-admission-and-assessment-policy.md) | Causal Admission and Assessment Policy | Accepted | I-004, I-005, I-006, I-010 |

## Approval record

ADR-001 through ADR-007 were approved by the architect on 2026-07-08, in
response to the Phase-0 reconnaissance and gap analysis. ADR-008 was
approved by the architect the same day as the final Phase-0 task, closing
the one gate item ADR-001..007 left open (causal admission policy). See
each ADR's Approval section for the specific decision.
