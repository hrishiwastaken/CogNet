---
name: phase-planning
description: Determines the current CogNet phase and whether a proposed task belongs to it, using docs/PHASE_PLAN.md and docs/PHASE_GATES.md. Use before starting any implementation task, to block work that belongs to a phase whose gate hasn't opened yet.
---

# Phase Planning

CogNet is built in gated phases (`docs/PHASE_PLAN.md`, Phase 0 through
Phase 10). This skill's only job is to answer, before any implementation
starts: **what phase is this task in, and has that phase's gate passed?**

## Procedure

1. Read `docs/PHASE_GATES.md` and find the current gate (the highest
   numbered phase whose checklist is fully `[x]`, plus one).
2. Read `docs/PHASE_PLAN.md` and find which phase's "Deliver" list the
   requested task actually belongs to. A task can look like it belongs to
   the current phase while actually smuggling in a later one — check
   specifically against each phase's forbidden-work list where one exists
   (e.g. Phase 0's "semantic resolver implementation, activation engine,
   LLM integration, curiosity engine, RL, automatic abstraction").
3. If the task's phase gate has not passed: stop, name which gate item(s)
   are unmet, and do not proceed. This is not a suggestion to work around —
   CLAUDE.md's "Stop" step is explicit that the next phase does not start
   automatically.
4. If the task's phase gate has passed: proceed, but only implement what
   that phase's "Deliver" list actually names (I-020, Phase Discipline).

## Current phase snapshot (update this when gates change)

As of the last Phase-0 freeze: Phase 0 gate is 13/13 (see
`docs/PHASE_GATES.md` status log). Phase 1 ("Deterministic Kernel") is open
to begin, pending explicit architect go-ahead — a passed gate authorizes the
phase, it does not by itself constitute a request to start it.

## Common failure this skill exists to catch

An implementer reuses a "just this one embedding call" or "just this one
LLM disambiguation" inside Phase-1 work because it's convenient, even though
embeddings are Phase 2 and LLM disambiguation is explicitly last-resort
(CLAUDE.md Mission statement, "Algorithm first. Model only on unresolved
entropy."). Catch this before it's written, not in review.
