# CogNet Memory IR v0.2

Status: Approved (Phase 0) — 2026-07-08, incorporating ADR-001, ADR-004,
ADR-005. See `docs/adr/README.md`.

This document freezes the domain model for Phase 0/1.

## Kernel ontology

| Kernel Type | Purpose | Example Specializations |
|---|---|---|
| ENTITY | Identity-bearing object | Person, Device, Organization, ConceptEntity |
| PROPOSITION | Truth-evaluable content | Claim, Hypothesis, Preference |
| EVENT | Temporally situated occurrence | Episode, Action, StateTransition |
| PROCEDURE | Executable/reusable process | Plan, Skill, Workflow |
| GOAL | Desired state / target | TaskGoal, LongTermGoal, Constraint |
| EVIDENCE | Support/challenge material | Observation, Measurement, TestResult |
| SOURCE | Origin/trust boundary | User, Document, Tool, Sensor, WebSource |

Extensions inherit lifecycle, provenance, scope, and permission semantics.

## Identity semantics (ADR-001)

Canonical identity for every `MemoryObject`, `Edge`, `ResolutionRecord`, and
`ProvenanceNode` is a runtime-generated **UUIDv7**. UUIDv7 is chosen over
content-addressed IDs because canonical identity must survive payload
mutation, belief updates, and deduplication — content hashes change when
content changes, which would otherwise change "who" the object is.

Content hashes are **not** canonical identity. Where present (e.g.
`content_hash` on a `MemoryObject`), they exist only as:
- deduplication fingerprints
- integrity fingerprints
- exact-content comparison signals

Ambiguous or unresolved identity never produces a placeholder entity. See
`ResolutionRecord` below.

## Common MemoryObject

```text
MemoryObject
- id: UUIDv7                    # canonical identity, see Identity semantics
- content_hash: str | None      # non-canonical fingerprint, dedup/integrity only
- kernel_type: KernelType
- subtype: str
- scope_id: UUIDv7
- payload: typed payload
- created_at: datetime
- valid_time: TimeInterval | None
- transaction_time: datetime
- source_id: UUIDv7
- provenance_node_id: UUIDv7
- trust_domain: TrustDomain
- taint_state: TaintState
- access_state: HOT | WARM | COLD | ARCHIVED | PRUNED
- embedding_ref: str | None
- counters:
    exposure
    retrieval
    successful_use
    failed_use
    verification
```

## Scope types

- GLOBAL_WORLD
- USER_PRIVATE
- PROJECT
- SESSION
- HYPOTHETICAL
- COUNTERFACTUAL
- AGENT_LOCAL
- SHARED_TEAM

Every memory object belongs to exactly one primary scope in Phase 1.
Cross-scope references are allowed only through explicit policy.

## Scope promotion (ADR-004)

Cross-scope **access** (read) uses reference-by-ID plus explicit policy and
capability checks; it does not change an object's scope.

Cross-scope **promotion** never silently copies or moves an object.
Promotion always creates a **new** `MemoryObject` with:
- a new canonical ID (a new UUIDv7 — never the source object's ID)
- an explicit `DERIVED_FROM` edge to the source object
- a `ProvenanceNode` recording the promotion operation, including
  `source_scope_id`, `target_scope_id`, and the policy decision that
  authorized it

The original object is left unchanged in its original scope: same
`scope_id`, same trust/taint history, same content. This preserves
auditability, scope isolation, historical truth, and provenance.

## Trust, taint, and contextual reliability (ADR-005)

Four dimensions in this cluster are independent and must never be derived
one from another:

```text
TrustDomain            # security/origin boundary; set once at ingestion
- LOCAL_SYSTEM
- USER_ASSERTED
- TRUSTED_TOOL
- UNTRUSTED_TOOL
- IMPORTED_DOCUMENT
- EXTERNAL_NETWORK
- MODEL_GENERATED

TaintState             # integrity/promotion restriction
- CLEAN
- UNVERIFIED
- TAINTED
- QUARANTINED
```

`SourceReliability` is **not** a field on `Source` or `MemoryObject`. It is a
computed, contextual assessment — the same source can be reliable in one
context and not another (e.g. a `USER_ASSERTED` source is typically reliable
for personal preferences, weak for third-party scientific claims; a
`TRUSTED_TOOL` can still be stale or misconfigured):

```text
SourceReliabilityAssessment
- source_id: UUIDv7
- context_domain: str
- reliability_score: float
- basis:
    observation_method
    verification_history_ids: list[UUIDv7]
    historical_success_count
    historical_failure_count
- as_of_time: datetime
- computed_from_evidence_ids: list[UUIDv7]
- computation_version: str
```

The fourth dimension, **epistemic confidence**, is `BeliefState.confidence`
(see below) — how justified a specific proposition currently is. It is
computed from evidence, not copied from any source-level field.

No function may map `TrustDomain -> TaintState`,
`TrustDomain -> SourceReliability`, or any other pairwise derivation across
{`TrustDomain`, `TaintState`, `SourceReliability`, epistemic confidence}.
Each is set/computed independently.

**Historical immutability:** original evidence retains its original
`TrustDomain` and `TaintState` permanently. Later corroboration or
verification never rewrites or "cleans" historical evidence. If previously
unverified or tainted evidence contributes to a later-promoted proposition,
the promotion produces a new derived proposition and/or `BeliefState` with
its own provenance, verification evidence, promotion operation, and
`computation_version` — the original evidence object is untouched.

## Time semantics

Keep separate:
- `valid_time`: when the proposition/event is true in the represented world
- `transaction_time`: when CogNet learned/stored it

Do not substitute `created_at` for either semantic.

## Proposition

```text
Proposition
- memory_object_id
- subject_ref
- predicate
- object_ref_or_value
- polarity
- modality
- qualifiers
```

## Evidence

```text
Evidence
- memory_object_id
- target_proposition_id
- relation: SUPPORTS | CONTRADICTS
- strength
- observation_method
- reliability_inputs
```

## BeliefState

Belief is not a MemoryObject rewrite.

`BeliefState.source_reliability` is a summary drawn from the
`SourceReliabilityAssessment` records relevant to `computed_from_evidence_ids`
for this proposition's `context_domain` — it is not a redefinition of
`SourceReliability` and does not derive from `TrustDomain` (see "Trust,
taint, and contextual reliability" above).

```text
BeliefState
- proposition_id
- scope_id
- as_of_time
- confidence
- support
- source_reliability
- cross_context_consistency
- contradiction_pressure
- reasoning_success
- verification_level
- uncertainty:
    epistemic
    aleatoric
    ambiguity
    conflict
    staleness
    missing_evidence
- computed_from_evidence_ids
- computation_version
```

## Edge

```text
Edge
- id
- source_id
- target_id
- edge_type
- weight
- confidence
- scope_id
- support_count
- contradiction_count
- last_activated
- provenance_node_id
```

`weight` is accessibility/traversal preference.
`confidence` is justification.

## Edge vocabulary

Associative:
- SEMANTIC_ASSOCIATION
- CO_ACTIVATED_WITH
- SIMILAR_TO

Structural:
- PART_OF
- INSTANCE_OF
- USED_FOR
- OBSERVED_IN

Temporal:
- PRECEDES
- FOLLOWS

Epistemic/inference:
- SUPPORTS
- CONTRADICTS
- DERIVED_FROM
- PREDICTS
- ENABLES
- PREVENTS
- CAUSES

## Causal admission and assessment (ADR-008)

```text
CausalStatus
- ASSOCIATED
- CAUSAL_HYPOTHESIS
- CAUSAL_SUPPORTED
- CAUSAL_VERIFIED
- CAUSAL_CONTESTED
- CAUSAL_REJECTED
```

`CO_ACTIVATED_WITH -> CAUSES` is forbidden.

Causal justification is **not** a confidence number on the edge. It is a
separate, scoped, versioned object — the same pattern as `BeliefState`
being separate from `Proposition`:

```text
EvidenceClass
- ASSOCIATIVE_SIGNAL          # co-activation, embedding similarity
- SOURCED_CAUSAL_ASSERTION    # explicit causal claim from a source
- INTERVENTION_EVIDENCE       # controlled/observed intervention + effect
- DOMAIN_RULE_MECHANISM       # validated domain rule/mechanism
- DERIVED_INFERENCE           # auditable derivation from other causal-grade evidence
- CONTESTING_EVIDENCE         # counter-observation, failed replication, alternative explanation

CausalAssessment
- causal_assessment_id: UUIDv7
- causal_proposition_ref: reference to the specific causal claim
    (source ref, target ref, proposed mechanism ref)
- scope_id: UUIDv7
- context_domain: str | None
- causal_status: CausalStatus
- contested: bool
- supporting_evidence: list[(evidence_id, evidence_class)]
- contesting_evidence: list[(evidence_id, evidence_class)]
- transition_history: list[CausalTransitionRecord]
- as_of_time: datetime
- computed_from_evidence_ids: list[UUIDv7]
- computation_version: str
- provenance_node_id: UUIDv7

CausalTransitionRecord
- from_status: CausalStatus
- to_status: CausalStatus
- triggering_evidence_ids: list[UUIDv7]
- reviewer_ref: str
- transitioned_at: datetime
```

**Anti-accumulation rule:** `ASSOCIATIVE_SIGNAL` evidence, in any quantity,
never contributes — individually, summed, averaged, weighted, or
thresholded — to a status beyond `ASSOCIATED`. A `CausalAssessment` computed
entirely from `ASSOCIATIVE_SIGNAL` evidence is rejected by construction.

**Transitions** (every one requires a `CausalTransitionRecord`; none are
silent):

| From | To | Requires (never `ASSOCIATIVE_SIGNAL` alone) |
|---|---|---|
| `ASSOCIATED` | `CAUSAL_HYPOTHESIS` | `SOURCED_CAUSAL_ASSERTION`, `DOMAIN_RULE_MECHANISM`, or `DERIVED_INFERENCE` |
| `CAUSAL_HYPOTHESIS` | `CAUSAL_SUPPORTED` | `INTERVENTION_EVIDENCE`, independent corroborating `SOURCED_CAUSAL_ASSERTION`, or `DOMAIN_RULE_MECHANISM` |
| `CAUSAL_SUPPORTED` | `CAUSAL_VERIFIED` | multiple independent `INTERVENTION_EVIDENCE`, or high-verification `DOMAIN_RULE_MECHANISM`, without unresolved contest |
| any | `CAUSAL_CONTESTED` | any credible `CONTESTING_EVIDENCE`, not yet reviewed |
| `CAUSAL_CONTESTED` | `CAUSAL_REJECTED` | contesting evidence validated, prior support found insufficient (explicit review) |
| `CAUSAL_CONTESTED` | prior status | contesting evidence invalidated/retracted (explicit review) |

**Contested/rejected is contextual:** `CausalAssessment` is scoped and may
be further narrowed by `context_domain` (mirroring
`SourceReliabilityAssessment`). The same causal claim may be
`CAUSAL_SUPPORTED` in one scope and `CAUSAL_CONTESTED` in another; contest
propagates across scopes only via explicit promotion (see "Scope
promotion" above), never automatically. `CAUSAL_REJECTED` is a status, not
a deletion — the assessment and its `transition_history` remain queryable.

## Resolution state and ResolutionRecord (ADR-001)

```text
ResolutionState
- RESOLVED
- AMBIGUOUS
- NEW_IDENTITY
- DEFERRED
```

Ambiguous or unresolved identity is never represented by a fake placeholder
entity. Instead it is represented by a `ResolutionRecord`:

```text
ResolutionRecord
- resolution_record_id: UUIDv7
- mention_ref: reference to the input/mention that triggered resolution
- candidate_entity_ids: list[UUIDv7]
- candidate_scores: list[float]      # parallel to candidate_entity_ids
- resolution_state: ResolutionState
- evidence_ids: list[UUIDv7]
- provenance_node_id: UUIDv7
- created_at: datetime
- resolved_at: datetime | None
```

An `AMBIGUOUS` or `DEFERRED` `ResolutionRecord` may exist indefinitely
without committing to a canonical entity. Delayed commitment is a
first-class, non-error state (I-014) — resolution logic must never force a
merge just to eliminate an open `ResolutionRecord`.

## Provenance DAG node

```text
ProvenanceNode
- id
- operation
- algorithm_name
- algorithm_version
- parameters_digest
- input_object_ids
- source_ids
- created_at
```

The provenance graph must remain auditable from decision/derived claim back to raw source.

## Value vector

Do not collapse by default:

```text
MemoryValue
- truth_confidence
- empirical_utility
- accessibility
- goal_relevance
```
