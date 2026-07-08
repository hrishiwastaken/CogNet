# ADR-008 — Causal Admission and Assessment Policy

## Status
Accepted

## Context
`docs/PHASE_GATES.md` left "Causal admission policy is approved" as the one
open Phase-0 item after ADR-001..007. `docs/MEMORY_IR.md` already lists a
`Causal status` enum (`ASSOCIATED` … `CAUSAL_REJECTED`) and I-004 already
forbids `CO_ACTIVATED_WITH -> CAUSES` directly, but nothing specified: what
counts as evidence for a causal claim, how status transitions between the
enum values, or how a contested/rejected claim behaves. Without this, an
implementer could satisfy I-004's literal text ("never directly promote")
while still letting a causal claim accrete legitimacy by *indirect*
accumulation — e.g. summing enough `CO_ACTIVATED_WITH` weight across many
edges until some threshold function calls it "supported." That is the same
violation wearing a numeric disguise.

## Decision drivers
- I-004 (Causality Is Not Co-Activation) must hold under indirect pressure
  (thresholds, aggregation, weighted sums of associative signal), not just
  against a single direct promotion.
- I-005 (Contradictions Are Preserved) applies to causal claims exactly as
  it does to propositions: a contested or rejected causal claim's history
  must not be erased.
- I-008 / ADR-005's non-collapse discipline extends here: causal
  justification is its own dimension, not a repackaging of edge
  `confidence`.
- I-006 (Scope Isolation) and ADR-005's `context_domain` pattern both imply
  that a causal claim's status can legitimately differ by scope/context
  without one overwriting the other.

## Options

### Option A — Causal justification as a confidence number on the edge
Pros:
- Minimal: reuses `Edge.confidence`, already in the schema.

Cons:
- A single scalar cannot represent *what kind* of evidence produced it —
  the exact ambiguity I-004 exists to prevent becomes invisible: a
  confidence of 0.8 built from 200 co-activation observations looks
  identical to a confidence of 0.8 built from one validated intervention.
- No place to record contest, review, or the evidence that triggered a
  status change — violates I-010 (auditability) for causal claims
  specifically.

### Option B — Scoped CausalAssessment as a first-class object, separate from the edge
Pros:
- Matches the pattern already established for `BeliefState` (separate from
  `Proposition`) and `SourceReliabilityAssessment` (separate from
  `TrustDomain`): the edge shows discovery/current pointer, the assessment
  carries the evidence trail.
- Evidence is typed by *class*, not merely counted, so the admission policy
  can categorically exclude a class from ever justifying a transition,
  regardless of quantity.
- Naturally scoped and versioned, so contest/rejection in one context does
  not silently overwrite a supported assessment computed in another.

Cons:
- More structure than a scalar; requires an explicit transition table.

## Recommendation
Option B.

## Decision

### 1. Causal justification is a scoped assessment, not an edge confidence number

A `CAUSES` (or `CAUSAL_HYPOTHESIS`, etc.) edge points to the current
best-known status, but the justification itself lives in a separate,
versioned `CausalAssessment` object:

```text
CausalAssessment
- causal_assessment_id: UUIDv7
- causal_proposition_ref: reference to the specific causal claim
    (source entity/event ref, target entity/event ref, proposed mechanism ref)
- scope_id: UUIDv7
- context_domain: str | None        # mirrors ADR-005's contextual pattern
- causal_status: CausalStatus
- contested: bool
- supporting_evidence: list[EvidenceRef]   # (evidence_id, evidence_class)
- contesting_evidence: list[EvidenceRef]   # (evidence_id, evidence_class)
- transition_history: list[CausalTransitionRecord]
- as_of_time: datetime
- computed_from_evidence_ids: list[UUIDv7]
- computation_version: str
- provenance_node_id: UUIDv7
```

```text
CausalTransitionRecord
- from_status: CausalStatus
- to_status: CausalStatus
- triggering_evidence_ids: list[UUIDv7]
- reviewer_ref: str    # policy rule ID, or human/agent reviewer reference
- transitioned_at: datetime
```

Like `BeliefState`, a `CausalAssessment` recomputation never overwrites the
prior record in place — it is appended with a new `computation_version` and
`as_of_time`, preserving the full history (I-005, I-010).

### 2. Evidence classes, and the anti-accumulation rule

```text
EvidenceClass
- ASSOCIATIVE_SIGNAL          # co-activation, embedding similarity
- SOURCED_CAUSAL_ASSERTION    # explicit causal claim from a source
- INTERVENTION_EVIDENCE       # controlled/observed intervention + effect
- DOMAIN_RULE_MECHANISM       # validated domain rule/mechanism
- DERIVED_INFERENCE           # auditable derivation from other causal-grade evidence
- CONTESTING_EVIDENCE         # counter-observation, failed replication, alternative explanation
```

**Anti-accumulation rule (the core of this ADR):** `ASSOCIATIVE_SIGNAL`
evidence, in any quantity, can justify creating or strengthening
`SEMANTIC_ASSOCIATION` / `CO_ACTIVATED_WITH` / `SIMILAR_TO` edges only. It
can **never** contribute — individually or summed, averaged, weighted, or
thresholded — to a `CausalAssessment` transition beyond `ASSOCIATED`. A
`CausalAssessment` computation whose `computed_from_evidence_ids` resolve
entirely to `ASSOCIATIVE_SIGNAL`-class evidence must be rejected by
construction, not merely scored low. This closes the indirect-accumulation
gap I-004 left open (see Context).

### 3. Allowed transitions

| From | To | Requires (at least one, none of it `ASSOCIATIVE_SIGNAL`) |
|---|---|---|
| `ASSOCIATED` | `CAUSAL_HYPOTHESIS` | `SOURCED_CAUSAL_ASSERTION`, `DOMAIN_RULE_MECHANISM`, or `DERIVED_INFERENCE` citing a mechanism sketch |
| `CAUSAL_HYPOTHESIS` | `CAUSAL_SUPPORTED` | `INTERVENTION_EVIDENCE`, or independent corroborating `SOURCED_CAUSAL_ASSERTION` (independence checked via `SourceReliabilityAssessment` in the relevant `context_domain`, per ADR-005), or `DOMAIN_RULE_MECHANISM` validation |
| `CAUSAL_SUPPORTED` | `CAUSAL_VERIFIED` | multiple independent `INTERVENTION_EVIDENCE` observations, or a `DOMAIN_RULE_MECHANISM` at high verification level, reproduced without unresolved `CONTESTING_EVIDENCE` |
| any status | `CAUSAL_CONTESTED` | any credible `CONTESTING_EVIDENCE` not yet reviewed |
| `CAUSAL_CONTESTED` | `CAUSAL_REJECTED` | `CONTESTING_EVIDENCE` validated and prior supporting evidence found insufficient, via an explicit `CausalTransitionRecord` review — never automatic |
| `CAUSAL_CONTESTED` | prior status | contesting evidence itself invalidated/retracted, via an explicit `CausalTransitionRecord` review |

Every transition requires a `CausalTransitionRecord` with
`triggering_evidence_ids` and a `reviewer_ref`. No transition is silent.

### 4. Contested/rejected behavior is contextual, not global

`CausalAssessment` is scoped (`scope_id`) and optionally further narrowed by
`context_domain`, mirroring `SourceReliabilityAssessment` (ADR-005). A
causal claim may be `CAUSAL_SUPPORTED` in one scope's evidence base and
`CAUSAL_CONTESTED` in another, if the contesting evidence has not been
promoted or is not visible in the first scope's policy boundary (I-006).
Discovering contesting evidence in one scope does not retroactively rewrite
a `CausalAssessment` computed in a different scope — a new, separately
scoped assessment is what changes. Cross-scope propagation of a contest
follows the same explicit-policy promotion mechanics as ADR-004; it is
never automatic.

`CAUSAL_REJECTED` is not deletion. The rejected `CausalAssessment` and its
full `transition_history` remain queryable (I-005, I-010) — rejection is a
status, not an erasure.

## Affected invariants
- I-004 (Causality Is Not Co-Activation) — closes the indirect-accumulation
  gap; the categorical evidence-class gate, not a threshold, is the
  enforcement mechanism.
- I-005 (Contradictions Are Preserved) — contested/rejected assessments are
  appended, never overwritten.
- I-006 (Scope Isolation) — contest/rejection propagate across scopes only
  through explicit promotion, never automatically.
- I-010 (Provenance Is Auditable) — every transition carries
  `triggering_evidence_ids` and a `reviewer_ref`.

## Migration / reversal cost
Medium. This is additive to the existing `Causal status` enum and edge
schema — no existing field is removed, so it does not conflict with
ADR-001..007. Cost would be high only if a future implementation had
already conflated causal justification with `Edge.confidence`; no such
implementation exists yet.

## Consequences
- `docs/MEMORY_IR.md`'s "Causal status" section is extended with
  `EvidenceClass`, `CausalAssessment`, and `CausalTransitionRecord`.
- `docs/BENCHMARKS.md` gains concrete causal-admission task sketches,
  including an adversarial evidence-class-mislabeling scenario.
- `docs/PHASE_GATES.md`'s "Causal admission policy is approved" item is
  satisfied by this ADR.
- Phase-1 implementation must reject any causal-status transition function
  that accepts `ASSOCIATIVE_SIGNAL`-only input, at the type/construction
  level, not just via a low score.

## Approval
Accepted by architect, 2026-07-08.
