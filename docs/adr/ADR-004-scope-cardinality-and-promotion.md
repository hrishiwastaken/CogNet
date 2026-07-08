# ADR-004 — Scope Cardinality and Cross-Scope Promotion

## Status
Accepted

## Context
`docs/MEMORY_IR.md` states "every memory object belongs to exactly one
primary scope in Phase 1" and "cross-scope references are allowed only
through explicit policy," but does not specify the mechanics: does crossing
a scope boundary copy, move, or reference the object? Without a decision,
an implementer could silently choose in-place mutation of `scope_id`, which
would destroy the historical record of what was known in the original scope
(violating I-005, I-007, I-010).

## Decision drivers
- I-006 (Scope Isolation) requires that promotion be an explicit, policed
  act, not a side effect of a query.
- I-010 (Provenance Is Auditable) requires that a promoted object trace back
  to its origin.
- I-007 (Memory != Belief) and I-005 (Contradictions Are Preserved) both
  imply that historical state must not be silently rewritten by a later
  operation — promotion is a later operation relative to the original
  observation.

## Options

### Option A — In-place scope reassignment
Pros:
- Simple: change `scope_id` on the existing row.

Cons:
- Destroys the historical fact "this object existed in scope S1 at time T."
- No way to represent "the same content is visible in two scopes with
  different trust histories" (e.g. promoted-and-original both matter).
- Silent cross-scope promotion is exactly the failure mode D-002 and I-006
  exist to prevent.

### Option B — Copy/move without new provenance
Pros:
- Preserves the original object.

Cons:
- Without a recorded promotion operation, the provenance DAG cannot show
  *why* or *under what policy* the copy was allowed to exist in the target
  scope — this is indistinguishable from an unaudited leak.

### Option C — Promotion creates a new object with explicit provenance
Pros:
- Original object is untouched: its scope, trust history, and taint state
  remain historically accurate.
- The new object's existence is itself an auditable, policy-gated event.
- Directly composes with the existing `DERIVED_FROM` edge type and
  `ProvenanceNode` schema already in `MEMORY_IR.md`.

Cons:
- Two objects now exist for "the same" content; consumers must understand
  that the target-scope object is a derived promotion, not a live sync.

## Recommendation
Option C.

## Decision

1. Each `MemoryObject` has **exactly one primary scope** in Phase 1
   (confirms existing `MEMORY_IR.md` language — this ADR formalizes it as
   approved rather than draft).
2. Cross-scope **access** (read, not promotion) uses reference-by-ID plus
   explicit policy evaluation and capability checks. It does not change
   which scope an object belongs to.
3. Cross-scope **promotion** never silently copies or moves an object.
   Promotion creates a **new object** with:
   - a new canonical ID (per ADR-001, a new UUIDv7 — never reuse the source
     object's ID)
   - an explicit `DERIVED_FROM` edge to the source object
   - a `ProvenanceNode` recording the promotion operation, including:
     - `source_scope_id`
     - `target_scope_id`
     - the policy decision that authorized the promotion (which policy,
       which capability, who/what invoked it)
4. The original object **remains unchanged** in its original scope: same
   `scope_id`, same trust/taint history, same content.

## Affected invariants
- I-006 (Scope Isolation) — promotion is the only sanctioned crossing
  mechanism, and it is always explicit and policed.
- I-010 (Provenance Is Auditable) — every promoted object has a traceable
  `DERIVED_FROM` + `ProvenanceNode` chain back to its source.
- I-005 / I-007 — the source object's historical state is never rewritten by
  a later promotion decision.

## Migration / reversal cost
High if changed after Phase-1 promotion logic and stored promoted objects
exist — consumers would need to distinguish "linked" vs "copied" semantics
retroactively. Low now.

## Consequences
- `docs/MEMORY_IR.md` gains an explicit "Scope promotion" section describing
  this mechanics, cross-referenced from the scope-types section.
- Phase-1 promotion implementation (when it arrives) always writes: new
  object + `DERIVED_FROM` edge + `ProvenanceNode`, atomically, in the single
  SQLite database established by ADR-003.

## Approval
Accepted by architect, 2026-07-08.
