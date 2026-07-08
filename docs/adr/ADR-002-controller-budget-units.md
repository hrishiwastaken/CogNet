# ADR-002 — Controller Budget Units

## Status
Accepted

## Context
`docs/ARCHITECTURE.md`'s `ControlState` declares `remaining_budget` and a
scheduling formula `a* = argmax E[ΔUtility(a)] / (Cost(a) + ε)`, but never
defines the unit of budget or cost. Phase-0 gate item "Controller budget
units are defined" cannot pass on an undefined unit. Picking a single scalar
unit prematurely (e.g. "tokens only") would bias the controller toward one
resource type and make it impossible to bound non-LLM-cost operations such as
graph expansion.

## Decision drivers
- The controller must be able to bound cost for operations that have nothing
  to do with LLM tokens (graph traversal, rule evaluation) — I-003 requires
  every reasoning session to have a budget and step count, not just a token
  budget.
- Scheduling still needs a single comparable number to rank candidate
  operations (the `a*` formula divides by a scalar `Cost(a)`).
- Phase 1 must not implement adaptive/learned scheduling (I-020, Phase
  discipline) — only the accounting model.

## Options

### Option A — Single scalar budget (e.g. token count or wall-clock only)
Pros:
- Trivial to compare and enforce.

Cons:
- Cannot separately bound cheap-but-numerous operations (graph expansions)
  vs expensive-but-rare ones (model calls); a token-only budget lets
  unbounded graph expansion run as long as no LLM is called, violating the
  spirit of I-003.

### Option B — Multidimensional vector budget with a derived scalar projection
Pros:
- Each resource type is bounded independently and auditably.
- The scheduling formula still gets a single number via an explicit,
  documented normalization step — the vector is the source of truth, the
  scalar is a view over it.

Cons:
- More bookkeeping in `ControlState`.

## Recommendation
Option B.

## Decision

`ControlState.remaining_budget` (and its companion `consumed_budget`) is a
**vector**, not a scalar, with at minimum these dimensions:

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

The Cognitive Control Plane may compute a normalized scalar for scheduling:

```text
Cost(a) = weighted_normalization(consumed(a): BudgetVector) -> float
```

This scalar is a **scheduling projection only**. It feeds `a* = argmax
E[ΔUtility(a)] / (Cost(a) + ε)` and nothing else. It must never replace or be
persisted as a substitute for the underlying `BudgetVector` — termination
checks, audits, and per-dimension limits always read the vector directly.

Budget limits are configurable at multiple scopes:
- global (process-wide default)
- per session
- per operation class (e.g. cap `embedding_queries` independently of
  `tool_calls`)
- per agent capability

**Phase discipline:** Phase 0 specifies this model only. Phase 1 implements
straightforward vector accounting and threshold-based termination. Adaptive
or learned scheduling (weight tuning, RL-based cost normalization) is
out of scope until a phase that explicitly authorizes it (I-020).

## Affected invariants
- I-003 (Finite Reasoning) — the vector budget is the concrete mechanism
  that gives every reasoning session a real, multi-resource budget and step
  count.

## Migration / reversal cost
Medium. Changing the unit set after Phase 1 accounting code exists requires
touching every call site that decrements budget, but does not affect stored
domain data (budgets are transient control-plane state, not persisted
memory).

## Consequences
- `docs/ARCHITECTURE.md`'s `ControlState` block is updated to show the
  `BudgetVector` shape and the normalized-scalar note.
- Termination condition "budget exhausted" (already listed in
  `ARCHITECTURE.md`) means "any configured dimension limit reached," not
  "scalar reaches zero."

## Approval
Accepted by architect, 2026-07-08.
