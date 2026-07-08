# CogNet — Claude Code Project Constitution

## Mission

Build CogNet v2.1 as a model-agnostic, uncertainty-aware cognitive substrate for agentic systems.

CogNet must perform memory selection, scoped association, evidence tracking, belief maintenance,
contradiction management, bounded graph reasoning, and compact context compilation outside the LLM.

The governing rule is:

> Algorithm first. Model only on unresolved entropy.

The LLM is an optional language interface and last-resort disambiguator. It is not the canonical
owner of memory, belief, graph mutation, causal structure, or reasoning validity.

## Required reading order before architectural work

1. `CLAUDE.md`
2. `docs/INVARIANTS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/MEMORY_IR.md`
5. `docs/DECISIONS.md`
6. `docs/PHASE_PLAN.md`
7. The current phase gate in `docs/PHASE_GATES.md`
8. `docs/COGNET_V2.1_SPEC.pdf` when deeper context is required

Do not begin implementation until the current phase and gate are explicit.

## Operating protocol

For every non-trivial implementation task:

1. **Inspect**
   - Read affected modules.
   - Search for existing interfaces before inventing new ones.
   - Identify the current phase.
   - Identify affected invariants.

2. **Plan**
   - State the smallest coherent change.
   - List files expected to change.
   - Define acceptance tests before implementation.
   - Surface ambiguities instead of silently choosing architecture.

3. **Implement**
   - Implement only the current milestone.
   - Prefer deterministic mechanisms.
   - Keep provider dependencies outside the core kernel.
   - Preserve provenance and scope semantics.

4. **Verify**
   - Run targeted tests.
   - Run architecture tests.
   - Run broader regression tests when relevant.
   - Check invariants explicitly.
   - Report commands actually run and their results.

5. **Stop**
   - Do not start the next phase automatically.
   - Do not perform unrelated refactors.
   - Do not replace missing architecture with a convenient LLM call.

## Non-negotiable constraints

- The LLM never owns canonical memory mutation.
- No unbounded reasoning loop.
- No `CAUSES` edge from co-activation alone.
- No silent overwrite of contradictory claims.
- No cross-scope promotion without explicit policy.
- No inference conclusion without evidence trace or explicit speculation state.
- Accessibility, truth confidence, empirical utility, and goal relevance are separate dimensions.
- An associative path is not an inference proof.
- Rare memory is not deleted merely because it is rare.
- The core kernel never imports a provider SDK.
- Untrusted content cannot silently promote itself into verified belief or executable procedure.
- Every benchmark claim requires a baseline and, where meaningful, ablation.
- JSON is a boundary format, not permission to use untyped dictionaries everywhere internally.
- Stored memory and current belief are separate objects.
- Every reasoning loop consumes a finite budget and has termination conditions.

## Architecture boundaries

### Cognitive Control Plane
Owns:
- budgets
- scheduling
- stopping
- escalation
- session state
- no-progress detection

Must not:
- silently invent beliefs
- mutate canonical memory without kernel APIs

### Memory Plane
Owns:
- typed IR
- associative graph
- episodes
- activation
- scopes
- provenance references
- consolidation state

Must not:
- treat activation paths as proofs
- infer causality from co-occurrence

### Reasoning Plane
Owns:
- query modes
- search
- hypotheses
- rules
- planning
- candidate path scoring

Must not:
- bypass evidence validation
- run without controller budget

### Epistemic Plane
Owns:
- evidence
- belief state
- contradiction
- typed uncertainty
- source reliability
- temporal validity

Must not:
- rewrite source history when belief changes

### Integration / I-O Plane
Owns:
- MCP
- SDK
- HTTP
- tools
- adapters
- documents
- sensors
- model providers

Must not:
- leak provider SDK types into the core kernel

## Coding principles

- Python first unless a phase decision explicitly changes this.
- Use explicit types and dataclasses/Pydantic-like boundary validation where appropriate.
- Core domain objects should not be generic nested dicts.
- Prefer pure functions for scoring and state transitions.
- Make time semantics explicit: valid time vs transaction time.
- Make scope explicit in every query that can cross memory boundaries.
- Make source and provenance explicit for every promoted proposition.
- Make ambiguity representable. Do not force resolution.
- Favor small modules with one architectural responsibility.
- Comments should explain non-obvious reasoning, not narrate syntax.
- Avoid corporate filler comments and pointless docstrings.
- No speculative abstraction before two concrete use cases.

## Dependency policy

Before adding a dependency:
- prove the standard library or an existing dependency is insufficient
- state why it is needed
- keep it behind an adapter if it is infrastructure-specific
- never add a provider SDK to core packages

## Definition of done

A task is done only when:
- implementation exists
- tests exist or a justified reason is recorded
- relevant tests pass
- architecture checks pass
- affected invariants are reviewed
- deviations are documented
- no next-phase work was smuggled in

## If the specification is ambiguous

Do not guess silently.

Create or update an ADR proposal under `docs/adr/` with:
- context
- options
- tradeoffs
- recommendation
- affected invariants
- migration cost

Then ask for approval if the choice is expensive to reverse.
