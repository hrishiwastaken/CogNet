# ADR-003 — Persistence Layout

## Status
Accepted

## Context
`docs/DECISIONS.md` D-011 already names SQLite as the Phase-1 default "unless
benchmark evidence forces change." What was undecided is the *layout*:
one database for the whole Phase-1 kernel, or one database per scope (which
would make scope isolation, I-006, a physical/filesystem property instead of
a logical one).

## Decision drivers
- Scope isolation (I-006) must be enforced and testable in Phase 1.
- Cross-scope provenance (I-010) must remain traceable — provenance nodes,
  evidence, and promoted objects can legitimately reference material that
  originated in a different scope, once policy permits it.
- Phase 1 must not smuggle in deployment/security architecture that belongs
  to a later phase (I-020).

## Options

### Option A — Database-per-scope
Pros:
- Strong physical isolation; a filesystem-level boundary backs scope
  isolation.

Cons:
- Cross-scope provenance DAG traversal (I-010) becomes a cross-database join
  or requires duplicating data.
- Transactions spanning a promotion operation (write to target scope +
  provenance record referencing source scope) cannot be atomic within one
  DB engine.
- Possible-world / hypothetical scopes (`HYPOTHETICAL`, `COUNTERFACTUAL` in
  `MEMORY_IR.md`) would each need their own database, multiplying
  operational complexity for what are often short-lived scopes.
- Premature optimization for a security boundary that Phase 1 does not yet
  need to guarantee.

### Option B — Single database, logical scope isolation
Pros:
- Provenance DAG, promotion transactions, and cross-scope references stay
  within one transactional boundary.
- Scope isolation is enforced the same way every other invariant is enforced
  in Phase 1: explicit fields, policy checks, and architecture tests — not a
  side effect of deployment topology.
- Physical isolation remains available later for deployments that need it,
  without having been baked into the Phase-1 kernel's assumptions.

Cons:
- Scope isolation bugs are logic bugs, not filesystem-permission bugs — they
  must be caught by tests, not by the OS.

## Recommendation
Option B.

## Decision

1. **SQLite is frozen as the Phase-1 persistence substrate** (confirms
   D-011).
2. **One database** is used for the Phase-1 implementation. Database-per-scope
   is rejected for Phase 1.
3. Scope isolation is enforced entirely at the logical layer:
   - every row carries an explicit `scope_id`
   - repository/service methods perform policy checks before returning or
     mutating cross-scope data
   - capability checks gate any operation that reads outside the caller's
     declared scope
   - architecture tests assert that no query path can return another
     scope's rows without going through the policy check
4. Physical isolation (separate databases, separate processes, or separate
   deployments per scope/tenant) **may be added later** for deployments that
   require a stronger security boundary. This future possibility must not
   distort the Phase-1 kernel's schema or query layer — no premature
   sharding keys, no per-scope connection pooling scaffolding now.

## Affected invariants
- I-006 (Scope Isolation) — enforced logically, not physically, in Phase 1.
- I-010 (Provenance Is Auditable) — a single transactional store keeps
  cross-scope provenance traversal simple and consistent.

## Migration / reversal cost
Medium. Moving to physical per-scope isolation later is an infrastructure
change behind the repository/service boundary; it does not require changing
the domain model as long as `scope_id` was always explicit (which it is,
per `MEMORY_IR.md`).

## Consequences
- Phase 1 persistence work targets one SQLite file/connection.
- Scope-isolation architecture tests are a Phase-1 gate requirement (already
  listed in `docs/PHASE_GATES.md` Phase 1 gate).

## Approval
Accepted by architect, 2026-07-08.
