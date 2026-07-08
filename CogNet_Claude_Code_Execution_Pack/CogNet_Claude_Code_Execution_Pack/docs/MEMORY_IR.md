# CogNet Memory IR v0.1

This document freezes the initial domain model for Phase 0/1.

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

## Common MemoryObject

```text
MemoryObject
- id: UUID
- kernel_type: KernelType
- subtype: str
- scope_id: UUID
- payload: typed payload
- created_at: datetime
- valid_time: TimeInterval | None
- transaction_time: datetime
- source_id: UUID
- provenance_node_id: UUID
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

## Causal status

- ASSOCIATED
- CAUSAL_HYPOTHESIS
- CAUSAL_SUPPORTED
- CAUSAL_VERIFIED
- CAUSAL_CONTESTED
- CAUSAL_REJECTED

`CO_ACTIVATED_WITH -> CAUSES` is forbidden.

## Resolution state

- RESOLVED
- AMBIGUOUS
- NEW_IDENTITY
- DEFERRED

Ambiguous candidates are stored with scores. No forced merge.

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
