---
name: cognet-architecture
description: Answers "which plane owns X", "does this violate an invariant", or "what does the frozen IR say about Y" by looking up docs/ARCHITECTURE.md, docs/INVARIANTS.md, docs/MEMORY_IR.md, and docs/adr/. Use before any architectural decision, or when unsure which plane a piece of code belongs to.
---

# CogNet Architecture Reference

This skill is a lookup discipline, not a source of new architecture. It
never answers from memory or invents an answer the docs don't already give —
it reads the frozen Phase-0 specification and reports what it says,
including when the spec doesn't cover the question (in which case: raise an
ADR per CLAUDE.md, don't guess).

## Lookup order

1. **Plane ownership** — `docs/ARCHITECTURE.md`. Five planes: Cognitive
   Control, Memory, Reasoning, Epistemic, Integration/I-O. Each has an
   "Owns" and "Must not" list. A change belongs to exactly the plane(s)
   whose "Owns" list covers it; if it's unclear, that ambiguity itself is
   worth flagging rather than picking one.
2. **Invariants** — `docs/INVARIANTS.md` (I-001..I-020). Check the
   invariant's "Violation example" where present — the title alone is often
   too abstract to apply directly.
3. **Domain model** — `docs/MEMORY_IR.md`. The typed IR: `MemoryObject`,
   `Proposition`, `Evidence`, `BeliefState`, `Edge`, `ResolutionRecord`,
   `CausalAssessment`, `SourceReliabilityAssessment`, scope types, and the
   enums (`TrustDomain`, `TaintState`, `EvidenceClass`, `CausalStatus`,
   `ResolutionState`). Before proposing a new field or type, check whether
   this file already defines it.
4. **Decisions** — `docs/DECISIONS.md` (D-001..D-013) and `docs/adr/`
   (ADR-001..008). ADRs are the authoritative record for anything expensive
   to reverse: identity scheme, budget units, persistence layout, scope
   promotion, trust/taint/reliability separation, legacy disposition,
   governance tooling, causal admission.

## Common questions this skill answers directly

- "Can the Memory Plane infer causality from co-occurrence?" — No
  (`ARCHITECTURE.md` Memory Plane "Must not"; I-004; ADR-008).
- "Where does `SourceReliability` live?" — Not on `Source` or
  `MemoryObject`; it's a separate `SourceReliabilityAssessment`, contextual
  by `context_domain` (ADR-005, `MEMORY_IR.md`).
- "What happens when an object is promoted to another scope?" — A new
  object is created with a new UUIDv7, a `DERIVED_FROM` edge, and a
  `ProvenanceNode` recording the promotion; the original is untouched
  (ADR-004).
- "Can enough `CO_ACTIVATED_WITH` evidence ever justify a `CAUSES` edge?" —
  No, categorically, regardless of quantity (I-004, ADR-008
  anti-accumulation rule).

## When the docs don't answer the question

Say so explicitly. Point at CLAUDE.md's "If the specification is
ambiguous" section: propose an ADR under `docs/adr/`, do not silently pick
an architecture.
