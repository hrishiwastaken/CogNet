# CogNet Phase Gates

## Current Gate: Phase 0

Phase 0 passes only when:

- [x] Kernel ontology is approved. — `MEMORY_IR.md` v0.2, approved 2026-07-08.
- [x] MemoryObject schema is versioned. — `MEMORY_IR.md` v0.2; identity
      semantics per ADR-001.
- [x] Proposition, Evidence, BeliefState schemas are versioned. — same v0.2
      freeze; `BeliefState.source_reliability` clarified per ADR-005.
- [x] Scope model is approved. — `MEMORY_IR.md` scope types + promotion
      semantics per ADR-004.
- [x] Valid-time vs transaction-time semantics are explicit. — `MEMORY_IR.md`
      "Time semantics".
- [x] Provenance DAG schema is approved. — `MEMORY_IR.md` `ProvenanceNode`;
      promotion-provenance mechanics per ADR-004.
- [x] Trust/taint model is approved. — `TrustDomain`/`TaintState` enums +
      `SourceReliabilityAssessment` per ADR-005.
- [ ] Causal admission policy is approved. — **PARTIAL**, carried over.
      `I-004`/D-006/causal-status states exist, but the transition policy
      between causal-status states (e.g. what evidence moves
      `CAUSAL_HYPOTHESIS` → `CAUSAL_SUPPORTED`) has not been specified or
      submitted to the architect. Tracked, not hidden.
- [x] Controller budget units are defined. — `BudgetVector` (9 dimensions) +
      normalized-scalar-is-projection-only rule per ADR-002, in
      `ARCHITECTURE.md`.
- [x] Stopping conditions are defined. — `ARCHITECTURE.md` "Required
      termination".
- [x] Benchmark datasets/tasks are sketched. — `BENCHMARKS.md` "Phase-0 task
      sketches", one concrete synthetic task per metric category.
- [x] ADR template exists. — `docs/ADR_TEMPLATE.md`; `docs/adr/` now
      populated with ADR-001..007.
- [x] No unresolved expensive-to-reverse ambiguity remains hidden. — the one
      open item above (causal admission transitions) and governance-file
      authorship (ADR-007 §3) are explicitly tracked, not silently decided
      or concealed.

**Status: 12/13 satisfied.** One item (causal admission transition policy)
remains open and is explicitly tracked rather than blocking silently.
Architect sign-off required before this is marked fully closed.

### Phase 0 forbidden work
- semantic resolver implementation
- activation engine
- LLM integration
- curiosity engine
- RL
- automatic abstraction

### Phase-0 status log
- 2026-07-08 — Initial reconnaissance and gap analysis (12 PARTIAL/FAIL of
  13 items).
- 2026-07-08 — Architect reviewed and issued ADR-001 through ADR-007
  decisions. Gates updated above; 12/13 now satisfied. Governance
  (`.claude/agents/*`, `.claude/skills/*`) confirmed empty in all repository
  history, not silently reinvented — see ADR-007.

## Phase 1 Gate

Pass only when:

- [ ] Typed domain objects exist.
- [ ] SQLite persistence round-trips all Phase-1 objects.
- [ ] Scope isolation tests pass.
- [ ] Provenance DAG traversal tests pass.
- [ ] Associative/inference graph separation tests pass.
- [ ] `CO_ACTIVATED_WITH -> CAUSES` is structurally blocked.
- [ ] Contradictory propositions can coexist.
- [ ] Belief state is not stored by overwriting propositions.
- [ ] Core imports no provider SDK.
- [ ] Architecture test suite passes.

## Phase 2 Gate

- [ ] Resolver benchmark exists.
- [ ] Ambiguity is preserved.
- [ ] Merge/split errors are measured.
- [ ] Resolver uses multiple signals.
- [ ] No LLM required for baseline operation.

## Phase 3 Gate

- [ ] Every reasoning/activation run has finite budget.
- [ ] Loop prevention is tested.
- [ ] Lateral inhibition is tested.
- [ ] Top-K workspace is enforced.
- [ ] No-progress termination is tested.

## Phase 4 Gate

- [ ] Evidence and belief are separate.
- [ ] Typed uncertainty is populated.
- [ ] Temporal contradiction cases are tested.
- [ ] Source disagreement is represented.
- [ ] Belief updates preserve source history.

## Phase 5 Gate

- [ ] One causal reasoning mode works end-to-end.
- [ ] Causal admission policy is enforced.
- [ ] Failed paths are contextual and decaying.
- [ ] Associative paths are never presented as proof without validation.
- [ ] Reasoning returns uncertainty.

## Phase 6 Gate

- [ ] MCP adapter works.
- [ ] Python SDK works.
- [ ] Provider SDKs remain outside core.
- [ ] Context packs are compact and typed.

## Phase 7 Gate

- [ ] A/B/C/D baselines run on same tasks.
- [ ] Metrics are predeclared.
- [ ] Failures are reported.
- [ ] Ablations exist for major CogNet components.
