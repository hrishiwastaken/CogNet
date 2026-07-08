# CogNet Phase Gates

## Current Gate: Phase 0

Phase 0 passes only when:

- [ ] Kernel ontology is approved.
- [ ] MemoryObject schema is versioned.
- [ ] Proposition, Evidence, BeliefState schemas are versioned.
- [ ] Scope model is approved.
- [ ] Valid-time vs transaction-time semantics are explicit.
- [ ] Provenance DAG schema is approved.
- [ ] Trust/taint model is approved.
- [ ] Causal admission policy is approved.
- [ ] Controller budget units are defined.
- [ ] Stopping conditions are defined.
- [ ] Benchmark datasets/tasks are sketched.
- [ ] ADR template exists.
- [ ] No unresolved expensive-to-reverse ambiguity remains hidden.

### Phase 0 forbidden work
- semantic resolver implementation
- activation engine
- LLM integration
- curiosity engine
- RL
- automatic abstraction

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
