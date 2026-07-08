# CogNet Claude Code Execution Pack

This pack turns the CogNet v2.1 architecture into a phase-gated Claude Code workflow.

## Included

- `CLAUDE.md` — project constitution
- `docs/INVARIANTS.md` — non-negotiable architecture constraints
- `docs/ARCHITECTURE.md` — four-plane + control-plane architecture
- `docs/MEMORY_IR.md` — typed IR freeze candidate
- `docs/DECISIONS.md` — Phase-0 defaults
- `docs/PHASE_PLAN.md` — implementation sequence
- `docs/PHASE_GATES.md` — measurable exit gates
- `docs/BENCHMARKS.md` — falsifiable benchmark plan
- `docs/ADR_TEMPLATE.md` — architecture decision template
- `.claude/skills/` — five project skills
- `.claude/agents/` — implementer, reviewer, adversarial tester
- `scripts/check_architecture.py` — starter static architecture checker
- `tests/architecture/` — starter architecture-contract tests
- `FIRST_PROMPT_FOR_OPUS.md` — exact first prompt

## Install into your CogNet repository

Copy the contents of this pack into the repository root.

Do not blindly overwrite existing files. Review conflicts, especially:
- existing `CLAUDE.md`
- existing `.claude/`
- existing `docs/`
- existing tests

Then give Claude Code Opus the contents of `FIRST_PROMPT_FOR_OPUS.md`.

## Recommended workflow

1. Opus performs Phase-0 reconnaissance only.
2. You review its questions and ADR proposals.
3. Freeze Phase 0.
4. Begin Phase 1.
5. After each milestone:
   - implementer works
   - architecture reviewer audits
   - adversarial tester attacks
   - architecture checks run
6. Do not advance phases until the gate passes.

## Important

The pack is deliberately conservative. The goal is not maximum code generation speed.
The goal is preventing a long-running agent from quietly turning CogNet into:
- vector RAG with graph vocabulary
- LLM-owned memory mutation
- unbounded agent loops
- causal claims from correlation
- provider-coupled infrastructure
