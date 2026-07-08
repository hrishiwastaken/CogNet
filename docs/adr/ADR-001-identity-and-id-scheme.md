# ADR-001 — Identity and ID Scheme

## Status
Accepted

## Context
`docs/MEMORY_IR.md` v0.1 declared `MemoryObject.id: UUID` without specifying
a generation scheme, and did not define how ambiguous or unresolved identity
resolution is represented. Content-addressed IDs were a candidate alternative
to runtime-generated UUIDs. Getting this wrong is expensive to reverse: every
object, edge, and provenance node keys off this identity from the first write
in Phase 1.

## Decision drivers
- Canonical identity must survive payload mutation, belief updates,
  deduplication, and later re-resolution.
- Deduplication/integrity checks need a fingerprint, but that fingerprint
  must not double as the object's identity (a content edit would otherwise
  change "who" the object is).
- Identity resolution must be able to stay unresolved (I-014) without
  fabricating a placeholder entity that pollutes the graph.

## Options

### Option A — Content-addressed canonical ID
Pros:
- Deterministic, naturally deduplicating.

Cons:
- Identity changes when payload changes, breaking edges/provenance/belief
  history that reference the object.
- Conflates "same content" with "same identity" — two independent entities
  with identical payloads would collide.

### Option B — UUIDv7 canonical ID + separate content hash
Pros:
- Identity is stable across payload mutation.
- UUIDv7's time-ordered prefix gives useful creation-order locality for
  indexes without a separate `created_at` sort key.
- Content hash remains available as a dedup/integrity signal without being
  overloaded as identity.

Cons:
- Requires an explicit non-canonical fingerprint field in addition to `id`.

## Recommendation
Option B.

## Decision

1. **Canonical identity** for every `MemoryObject`, `Edge`, `ResolutionRecord`,
   and `ProvenanceNode` is a runtime-generated **UUIDv7**.
2. **Content hashes are not canonical identity.** They may exist as separate
   fields (`content_hash` or similar) used only for:
   - deduplication fingerprints
   - integrity fingerprints
   - exact-content comparison signals
3. **Ambiguous or unresolved identity does not get a placeholder entity.**
   Instead, create a `ResolutionRecord`:

   ```text
   ResolutionRecord
   - resolution_record_id: UUIDv7
   - mention_ref: reference to the input/mention that triggered resolution
   - candidate_entity_ids: list[UUIDv7]
   - candidate_scores: list[float]  # parallel to candidate_entity_ids
   - resolution_state: ResolutionState
   - evidence_ids: list[UUIDv7]
   - provenance_node_id: UUIDv7
   - created_at: datetime
   - resolved_at: datetime | None
   ```

4. **Resolution states:**
   - `RESOLVED` — committed to exactly one canonical entity ID.
   - `AMBIGUOUS` — multiple candidates remain, no commitment.
   - `NEW_IDENTITY` — resolved to a newly minted entity.
   - `DEFERRED` — resolution intentionally postponed.

   `AMBIGUOUS` and `DEFERRED` records may exist indefinitely without a
   canonical entity. Delayed commitment is a first-class, non-error state
   (I-014), not a pending failure.

## Affected invariants
- I-014 (Ambiguity Is Representable) — directly implemented by
  `ResolutionRecord` + non-forced resolution states.

## Migration / reversal cost
High if changed after Phase 1 data exists — every object, edge, and
provenance reference is keyed by canonical ID. Low now, before any code
exists.

## Consequences
- `MEMORY_IR.md` must define `ResolutionState` as an enum and specify that
  `MemoryObject.id` (and all other canonical IDs) are UUIDv7, with
  `content_hash` as a separate, explicitly non-canonical field.
- Identity resolution logic (Phase 2+) produces `ResolutionRecord` rows
  rather than tentative entities.

## Approval
Accepted by architect, 2026-07-08.
