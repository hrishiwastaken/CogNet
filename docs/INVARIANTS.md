# CogNet Architectural Invariants

Status: Approved (Phase 0) — 2026-07-08. See `docs/adr/README.md` for
decisions (ADR-001..007) that operationalize several of these invariants.

These are executable design constraints, not inspirational statements.

## I-001 — Algorithm First
Every subsystem must prefer deterministic rules, parsers, graph algorithms, local embeddings,
or small classifiers before LLM escalation.

**Violation example:** calling an LLM to decide whether two exact IDs are identical.

## I-002 — Canonical Mutation Ownership
Agents submit observations, evidence, proposals, and feedback. CogNet owns canonical mutation.

**Violation example:** an agent directly setting a belief to VERIFIED.

## I-003 — Finite Reasoning
Every reasoning session has a budget, step count, stopping rules, and no-progress detection.

## I-004 — Causality Is Not Co-Activation
`CO_ACTIVATED_WITH` can never directly promote to `CAUSES`.

A causal edge requires an admitted ground:
- sourced causal assertion
- intervention evidence
- validated domain rule/mechanism
- auditable derived inference
- or provisional `CAUSAL_HYPOTHESIS`

## I-005 — Contradictions Are Preserved
Conflicting claims are not silently overwritten. Scope and valid-time overlap are checked first.

## I-006 — Scope Isolation
No cross-scope promotion without explicit policy/capability.

## I-007 — Memory != Belief
Stored propositions preserve history. Belief states are computed and may change independently.

## I-008 — Multi-Dimensional Value
Do not collapse:
- truth confidence
- empirical utility
- accessibility
- goal relevance

into one permanent scalar.

## I-009 — Association != Inference
Associative traversal discovers candidates. Inference structures justify conclusions.

## I-010 — Provenance Is Auditable
Derived claims and decisions must trace through a provenance DAG to sources.

## I-011 — Trust Boundaries Survive Ingestion
Untrusted content remains tainted until an explicit promotion rule succeeds.

## I-012 — Rare != Disposable
Low frequency alone is insufficient for destructive deletion.

## I-013 — Provider Independence
Core kernel modules must not import Anthropic, OpenAI, Google, or other model-provider SDKs.

## I-014 — Ambiguity Is Representable
Identity resolution may remain unresolved. Delayed commitment is a valid state.

## I-015 — Typed Uncertainty
Uncertainty should distinguish at least:
- epistemic
- aleatoric
- ambiguity
- conflict
- staleness
- missing evidence

## I-016 — JSON Is a Boundary
JSON is allowed at APIs and persistence boundaries. Internal domain logic uses typed structures.

## I-017 — Benchmark Claims Need Baselines
Performance claims require controlled comparison against relevant baselines.

## I-018 — No Unrestricted LLM Graph Rewriting
LLM output is a proposal/evidence source, not an automatic canonical graph mutation.

## I-019 — Failed Paths Are Contextual
Dead-end anti-priors are scoped, decaying, and bypassable by materially new evidence.

## I-020 — Phase Discipline
Do not implement later-phase research features inside earlier phases without an approved ADR.
