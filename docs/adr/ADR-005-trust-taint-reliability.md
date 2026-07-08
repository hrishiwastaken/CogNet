# ADR-005 — Trust, Taint, and Contextual Reliability

## Status
Accepted

## Context
`docs/MEMORY_IR.md` references `trust_domain: TrustDomain` and
`taint_state: TaintState` on every `MemoryObject`, but neither enum was ever
defined — Phase-0 gate item "Trust/taint model is approved" cannot pass on
an undefined model. Separately, nothing in the existing docs distinguished
*where evidence came from* (trust domain) from *how much to believe it in a
given context* (reliability) from *whether it is safe to promote*
(taint) from *how justified a specific proposition currently is* (epistemic
confidence, part of `BeliefState`). Collapsing these into one score is a
common, quiet failure mode: a "trusted tool" being treated as infallible, or
"user-asserted" being treated as uniformly reliable regardless of subject
matter.

## Decision drivers
- I-008 (Multi-Dimensional Value) already forbids collapsing truth
  confidence, empirical utility, accessibility, and goal relevance into one
  scalar. The same discipline must extend to the trust/taint/reliability
  cluster, or I-008's spirit is violated one layer down.
- I-011 (Trust Boundaries Survive Ingestion) requires taint to persist until
  an explicit promotion rule clears it — it must not be silently cleared by
  a reliability or confidence update.
- I-010 (Provenance Is Auditable) requires that historical evidence remain
  inspectable in its original trust/taint state even after later
  corroboration changes what is believed.

## Options

### Option A — Single "reliability" score derived from trust domain
Pros:
- One field, trivial to implement.

Cons:
- A `TRUSTED_TOOL` source that is stale or misconfigured would inherit a high
  score it hasn't earned in that context.
- A `USER_ASSERTED` source would get one score across radically different
  subject matter (personal preference vs third-party scientific claim),
  which is empirically wrong.
- Conflates security boundary (where did this come from) with epistemic
  trust (should I believe it here), making both harder to reason about and
  impossible to audit independently.

### Option B — Four independent dimensions, no derivation between them
Pros:
- Matches how these actually vary in practice (a trusted tool can still be
  wrong; a low-trust-domain source can still be reliable for narrow claims).
- Each dimension can be audited, tested, and evolved independently.

Cons:
- More fields, more explicit plumbing before any of this "just works."

## Recommendation
Option B.

## Decision

### TrustDomain (security/origin boundary)

```text
TrustDomain
- LOCAL_SYSTEM
- USER_ASSERTED
- TRUSTED_TOOL
- UNTRUSTED_TOOL
- IMPORTED_DOCUMENT
- EXTERNAL_NETWORK
- MODEL_GENERATED
```

`TrustDomain` describes *where a `MemoryObject` entered the system from*. It
is assigned once, at ingestion, by the source-specific adapter (Integration
plane), and does not change afterward.

### TaintState (integrity/promotion restriction)

```text
TaintState
- CLEAN
- UNVERIFIED
- TAINTED
- QUARANTINED
```

`TaintState` gates whether content may be promoted into a more trusted scope
or role (e.g. from observation to verified belief, or from one scope to
another per ADR-004). Per I-011, taint is cleared only by an explicit
promotion rule — never implicitly by the passage of time, by corroborating
evidence alone, or by a reliability recomputation.

### SourceReliability (contextual, historical, separate from TrustDomain)

`SourceReliability` is **not** a field on `Source` or `MemoryObject`. It is a
computed, contextual assessment, because the same source can be reliable in
one context and not another:

```text
SourceReliabilityAssessment
- source_id
- context_domain: str        # e.g. "personal_preference", "third_party_fact"
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

Example (from architect guidance): a `USER_ASSERTED` source may score highly
for `context_domain="personal_preference"` and poorly for
`context_domain="external_scientific_claim"`, under the *same* `TrustDomain`.
A `TRUSTED_TOOL` does not automatically get a high `reliability_score` — it
can still be stale, misconfigured, or operating outside its validated
domain, and its assessments must reflect that from actual verification
history, not from its `TrustDomain` label.

**`SourceReliability` must never be derived directly from `TrustDomain`.**
No function maps one to the other; they are computed and stored
independently.

### Epistemic confidence (per-proposition, current justification)

Already modeled as `BeliefState.confidence` plus the typed uncertainty block
in `MEMORY_IR.md`. This ADR clarifies it as the fourth, distinct dimension:
it answers "how justified is this specific proposition right now," computed
from evidence, not copied from any source-level field.

### Non-collapse rule

`TrustDomain`, `SourceReliability`, `TaintState`, and epistemic confidence
(`BeliefState.confidence`) are four independent dimensions. No one-to-one
mapping between any pair is permitted anywhere in the kernel. A function
that takes a `TrustDomain` and returns a `TaintState`, a reliability score,
or a confidence value is an architecture violation.

### Historical immutability rule

Original evidence retains its original `TrustDomain` and `TaintState`
history permanently. Later corroboration, verification, or promotion does
**not** rewrite or "clean" historical evidence records. If previously
unverified or tainted evidence contributes to a later-promoted proposition,
the promotion produces a **new** derived proposition and/or `BeliefState`
with its own explicit provenance, verification evidence, promotion
operation, and `computation_version` — the original evidence object is
untouched.

## Affected invariants
- I-008 (Multi-Dimensional Value) — extended by analogy to this cluster.
- I-011 (Trust Boundaries Survive Ingestion) — `TaintState` lifecycle is the
  concrete mechanism.
- I-015 (Typed Uncertainty) — epistemic confidence remains distinct from,
  and not a proxy for, trust/taint/reliability.

## Migration / reversal cost
High if collapsed now and split later — every stored object would need
backfilled reliability assessments disentangled from a blended score.
Low now, before any writes exist.

## Consequences
- `docs/MEMORY_IR.md` gains explicit `TrustDomain`, `TaintState`, and
  `SourceReliabilityAssessment` definitions, plus the non-collapse and
  historical-immutability rules.
- Phase-1 write paths must set `TrustDomain` and `TaintState` at ingestion
  and must never implement a `TrustDomain -> SourceReliability` or
  `TrustDomain -> TaintState` derivation function.

## Approval
Accepted by architect, 2026-07-08.
