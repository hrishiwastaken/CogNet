# CogNet v2.1 Architecture

Status: Approved (Phase 0) — 2026-07-08, incorporating ADR-002, ADR-003.
See `docs/adr/README.md`.

## System shape

CogNet is organized as four interacting planes coordinated by a Cognitive Control Plane.

```text
+------------------------------------------------------+
|              COGNITIVE CONTROL PLANE                 |
| budgets | scheduling | stopping | goals | escalation|
+--------------------------+---------------------------+
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
+----------------+ +----------------+ +----------------+
| MEMORY PLANE   | | REASONING      | | EPISTEMIC     |
| typed IR       | | PLANE          | | PLANE          |
| episodes       | | search         | | evidence       |
| associations   | | rules          | | belief         |
| activation     | | planning       | | conflict       |
| consolidation  | | hypotheses     | | uncertainty    |
+--------+-------+ +--------+-------+ +--------+-------+
         |                  |                  |
         +------------------+------------------+
                            v
+------------------------------------------------------+
|                INTEGRATION / I-O PLANE               |
| agents | MCP | SDK | tools | docs | code | sensors  |
+------------------------------------------------------+
```

## Control Plane

Owns finite compute and execution control.

Core state:

```text
ControlState
- session_id
- active_goal_ids
- remaining_budget: BudgetVector
- consumed_budget: BudgetVector
- step_count
- visited_reasoning_states
- pending_operations
- escalation_level
- termination_reason
- last_progress_score
```

### Budget accounting (ADR-002)

Budget is a **vector**, not a scalar, with at minimum these dimensions:

```text
BudgetVector
- graph_expansions: int
- embedding_queries: int
- rule_evaluations: int
- contradiction_checks: int
- hypothesis_operations: int
- tool_calls: int
- model_input_tokens: int
- model_output_tokens: int
- wall_time_ms: int
```

A single resource type (e.g. token count) cannot bound unrelated operations
(e.g. unbounded graph expansion). Each dimension is tracked and limited
independently. Limits are configurable globally, per session, per operation
class, and per agent capability.

Candidate next operation:

```text
a* = argmax E[Delta Utility(a)] / (Cost(a) + epsilon)
```

`Cost(a)` is a **normalized scalar projection** computed from the consumed
`BudgetVector` for scheduling comparison only. It never replaces the
underlying vector — termination checks, audits, and per-dimension limits
always read `BudgetVector` directly, never the scalar. Phase 1 implements
straightforward vector accounting and threshold termination; adaptive or
learned cost normalization is out of scope until an explicitly authorized
later phase (I-020).

Required termination:
- budget exhausted (any single `BudgetVector` dimension limit reached, not
  only the normalized scalar)
- confidence threshold reached
- expected information gain too low
- no progress for N steps
- repeated state beyond tolerance
- external observation required
- permission/safety boundary

## Memory Plane

Owns:
- typed Memory IR
- scope membership
- associative graph
- activation state
- memory access tiers
- provenance references
- consolidation proposals

Does not own:
- canonical belief truth
- inference validity

## Reasoning Plane

Owns:
- query intent
- decomposition
- candidate search
- hypotheses
- causal search
- planning
- path scoring
- failed-path traces

Associative candidates are inputs to reasoning, not proofs.

## Epistemic Plane

Owns:
- evidence
- belief states
- source reliability
- contradiction analysis
- typed uncertainty
- temporal validity
- verification state

Belief updates never rewrite source history.

## Integration / I-O Plane

Owns:
- MCP adapter
- Python SDK
- HTTP API
- provider adapters
- tool observations
- document/code/sensor ingestion adapters

Provider-specific types stop at this boundary.

## Runtime reasoning protocol

1. PARSE
2. ACTIVATE
3. DECOMPOSE
4. RETRIEVE
5. GENERATE
6. CHALLENGE
7. SCORE
8. IDENTIFY GAPS
9. SEEK INFORMATION
10. SYNTHESIZE
11. CALIBRATE
12. ACT
13. OBSERVE
14. LEARN
15. CONSOLIDATE

This is not a mandatory linear pass. The controller may skip irrelevant operations,
repeat bounded cycles, or terminate early.

## Discovery vs justification

### Associative Graph
Purpose: candidate discovery.

Typical relations:
- SEMANTIC_ASSOCIATION
- CO_ACTIVATED_WITH
- SIMILAR_TO

### Inference Graph
Purpose: justification.

Typical relations:
- SUPPORTS
- CONTRADICTS
- DERIVED_FROM
- PRECEDES
- ENABLES
- PREVENTS
- CAUSES (admission-controlled)

Invariant:

> Activation discovers. Inference validates.
