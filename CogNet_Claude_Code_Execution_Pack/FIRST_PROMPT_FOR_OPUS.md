# First Prompt for Claude Code Opus

Use this as the first implementation prompt.

---

You are beginning work on CogNet v2.1.

Do **not** implement the full system. Do **not** begin Phase 1 yet.

Your task is to execute **Phase 0 specification freeze and repository reconnaissance only**.

Read in this exact order:

1. `CLAUDE.md`
2. `docs/INVARIANTS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/MEMORY_IR.md`
5. `docs/DECISIONS.md`
6. `docs/PHASE_PLAN.md`
7. `docs/PHASE_GATES.md`
8. `docs/BENCHMARKS.md`
9. `docs/COGNET_V2.1_SPEC.pdf` if your environment can inspect it; otherwise rely on the extracted architecture documents above

Then inspect the entire existing repository before proposing changes.

## Required output before any code edits

Produce:

### A. Repository map
- current modules
- current persistence layer
- current UI layer
- current embedding logic
- current data models
- tests
- obvious legacy architecture conflicts

### B. Phase-0 gap analysis
For every Phase-0 checkbox in `docs/PHASE_GATES.md`, report:
- PASS
- FAIL
- PARTIAL
- UNKNOWN

with evidence.

### C. Invariant risk audit
For each relevant invariant:
- current risk
- evidence
- likely migration issue

### D. Proposed Phase-0 work plan
Include:
- exact files to add/change
- non-goals
- acceptance criteria
- expensive-to-reverse ambiguities
- ADRs required

### E. Questions for the architect
Ask only questions that materially affect expensive-to-reverse design.

## Hard constraints

- No Phase-1 implementation.
- No semantic resolver.
- No activation engine.
- No LLM integration.
- No provider SDK in core.
- No broad refactor.
- No UI redesign.
- Do not silently choose unresolved architecture.
- Do not modify the frozen v2.1 PDF.
- Treat the current codebase as evidence, not as automatically correct architecture.

Stop after the Phase-0 analysis and plan. Wait for architect approval.
