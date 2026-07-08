# ADR-006 — Legacy Application Disposition

## Status
Accepted

## Context
Prior to the CogNet v2.1 restructure, this repository contained a PySide6
desktop note-taking application (`cognet/main.py`, `cognet/ui/*`,
`cognet/models/note_model.py`, `cognet/data/database_manager.py`), preserved
in git history at commit `c60ee93` and earlier. It used JSON `list[dict]`
persistence, a `sentence-transformers` embedding pipeline loaded at startup,
and a matplotlib-based 3D embedding viewer. Phase-0 reconnaissance flagged
several direct conflicts with v2.1 architecture (I-001, I-016, I-020) and
asked whether it should serve as a migration base or an import-adapter
requirement for Phase 1.

## Decision drivers
- I-001 (Algorithm First) — the legacy app makes ML embeddings a startup
  dependency, ahead of any deterministic retrieval, inverting the required
  order.
- I-016 (JSON Is a Boundary) — the legacy app's canonical store *is* a JSON
  list of untyped dicts; that is exactly the pattern I-016 exists to bound to
  the API/persistence edge, not the internal domain model.
- I-020 (Phase Discipline) — the legacy app's embedding/3D-visualization
  logic belongs to Phase-2/UI concerns, not something to fold into Phase 1
  under the guise of "reuse."
- CogNet v2.1 is a headless cognitive substrate (SDK/MCP/HTTP per
  `docs/ARCHITECTURE.md`'s Integration/I-O Plane), not a desktop UI
  application — the legacy app's entire shape (Qt windows, splash screen)
  does not correspond to any planned v2.1 component.

## Options

### Option A — Use legacy app as Phase-1 migration base
Pros:
- Reuses existing, working code.

Cons:
- Every reason listed above; effectively means importing I-001/I-016/I-020
  violations into the frozen kernel on day one.

### Option B — Treat as abandoned reference architecture; no port, no adapter
Pros:
- Phase 1 starts from the typed IR in `docs/MEMORY_IR.md`, not from a
  retrofit of incompatible data shapes.
- No speculative migration-adapter work before a concrete requirement
  exists (matches CLAUDE.md: "No speculative abstraction before two concrete
  use cases").

Cons:
- Any real user data in an existing `cognet_db.json` would need a bespoke
  import path later if it ever matters.

## Recommendation
Option B.

## Decision

1. The legacy PySide6/JSON application is **abandoned reference
   architecture**. It documents what CogNet was before the v2.1 cognitive
   substrate redesign; it is not a foundation for Phase 1.
2. Phase 1 (and Phase 0) does **not** port:
   - JSON `list[dict]` persistence
   - the `sentence-transformers` startup dependency
   - the 3D embedding-visualization architecture
   - the UI-centric data model (`{id, title, category, content, timestamp,
     sentences}`)
3. Legacy history is preserved via git history (already the case at commit
   `c60ee93` and earlier on `main`) — no further branch/tag action is
   required unless the architect requests one.
4. **No `cognet_db.json` migration/import adapter is built in Phase 0 or
   Phase 1.** Such an adapter may be considered later, only if a concrete
   requirement emerges from real retained user data — not speculatively.
5. CogNet v2.1 is architecturally a new cognitive substrate, not an
   evolution of the note-taking app's codebase.

## Affected invariants
- I-020 (Phase Discipline) — prevents Phase-2/UI-shaped legacy code from
  entering Phase 1.
- I-001 (Algorithm First) — prevents the legacy embedding-first startup
  pattern from setting precedent.

## Migration / reversal cost
Low. This decision has no code dependency; it only forecloses reuse of code
that already conflicts with the frozen architecture. Legacy code remains
recoverable from git history if a future concrete requirement justifies
revisiting this decision.

## Consequences
- Phase-1 planning proceeds purely from `docs/MEMORY_IR.md` and this ADR
  set, with no legacy-compatibility constraint.
- If a user-data-import requirement appears later, it is scoped as its own
  ADR at that time, not assumed now.

## Approval
Accepted by architect, 2026-07-08.
