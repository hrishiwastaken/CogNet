# ADR-007 — Governance Tooling Status

## Status
Accepted (as a factual record + follow-up proposal; the follow-up authorship
work itself is *not* pre-approved by this ADR — see Decision §3)

## Context
Two governance mechanisms exist in the repository to keep future
implementation work inside the frozen architecture:

1. `.claude/scripts/check_architecture.py` — a static checker for provider-SDK
   imports (I-013) and unreviewed causal-admission text (I-004).
2. `.claude/agents/{implementer,architecture-reviewer,adversarial-tester}.md`
   and `.claude/skills/{cognet-architecture,phase-planning,invariant-checker,
   test-and-verify,benchmark-runner}/` — intended agent/skill definitions per
   the execution pack's own `docs/README.md`, which lists "five project
   skills" and "implementer, reviewer, adversarial tester" as included
   contents.

Phase-0 reconnaissance found (1) broken and (2) empty, and the architect
directed verification of whether populated versions were lost during ZIP
extraction, repository restructuring, file movement, or renames, before
reinventing anything.

## Investigation

### Checker path defect
`check_architecture.py` lives at `.claude/scripts/check_architecture.py` and
computed `ROOT = Path(__file__).resolve().parents[1]`, which resolves to
`.claude/`, not the repository root. It therefore searched for
`.claude/src/cognet/core` — a path that can never exist — making its
provider-SDK guard a silent no-op. Fixed in this Phase-0 pass (see
"Consequences").

### Agent/skill files — full-history check

Checked, in order:

1. **File-level history** (`git log --all --follow` on each of the three
   agent files): both existing commits (`8727137` "Initial CogNet
   architecture" and `bf0331e` "Set up repository structure for CogNet
   v2.1") show the files as **0 bytes**. Git's rename-detection paired them
   with legacy files (`cognet/data/__init__.py`,
   `cognet/models/__init__.py`, `cognet/models/database_manager.py`) at 100%
   similarity — which is only possible because *both sides of the rename
   were empty*. This is not evidence of lost content; it is an artifact of
   rename detection matching two empty files.
2. **Execution-pack commit** (`921c40d`, the raw upload before any
   restructuring): `.claude/agents/*.md` were already present at that path
   and already empty; `.claude/skills/*/` already contained only `.gitkeep`,
   no `SKILL.md`. The pack's own `CogNet_Claude_Code_Execution_Pack/.../
   README.md` (also present in that commit) claims these were populated —
   the claim does not match the committed contents.
3. **Exhaustive blob search**: enumerated all 54 blob objects that have ever
   existed in this repository's history (`git rev-list --objects --all`) and
   grepped each for agent-prompt-shaped content (`adversarial`, `You are
   the`, `Architecture Reviewer`, `Implementer Agent`, etc.). Zero matches.

**Conclusion:** the populated agent/skill files described in the execution
pack's README were never actually committed to this repository, at any
point in its history, under any path. This is not data loss from
restructuring — the content does not exist to lose.

## Decision

1. **Checker fix (in scope for this Phase-0 pass):**
   `check_architecture.py`'s `ROOT` is corrected to
   `Path(__file__).resolve().parents[2]`, so it correctly resolves to the
   repository root and will actually scan `src/cognet/core` once that
   package exists.

2. **Governance files are confirmed genuinely absent, not recoverable.**
   Per the architect's own instruction ("do not silently invent a different
   governance architecture"), this ADR does **not** author replacement
   content for:
   - `.claude/agents/implementer.md`
   - `.claude/agents/architecture-reviewer.md`
   - `.claude/agents/adversarial-tester.md`
   - `.claude/skills/cognet-architecture/`
   - `.claude/skills/phase-planning/`
   - `.claude/skills/invariant-checker/`
   - `.claude/skills/test-and-verify/`
   - `.claude/skills/benchmark-runner/`

   These files remain empty/placeholder after this Phase-0 pass.

3. **Proposed restoration path (not self-authorized by this ADR):**
   Authoring these files encodes real governance authority — what an
   "architecture reviewer" is allowed to flag, what an "adversarial tester"
   is allowed to attack, what each skill is scoped to do. That is itself an
   architectural decision, not a mechanical restoration, since there is
   nothing to mechanically restore. Recommend a follow-up task, scoped and
   approved explicitly (its own ADR or explicit go-ahead), that:
   - defines each agent's responsibility boundary against the four planes
     in `docs/ARCHITECTURE.md` (e.g. `architecture-reviewer` checks
     invariant/plane-boundary compliance; `adversarial-tester` attempts to
     induce invariant violations named in `docs/INVARIANTS.md`;
     `implementer` follows the CLAUDE.md Inspect/Plan/Implement/Verify/Stop
     protocol)
   - defines each skill's scope against `docs/PHASE_PLAN.md` /
     `docs/PHASE_GATES.md` (e.g. `phase-planning`, `invariant-checker`,
     `test-and-verify`, `benchmark-runner`, `cognet-architecture`)
   - is reviewed by the architect before being treated as governing, the
     same way this ADR set was reviewed

## Affected invariants
- I-013 (Provider Independence) — the checker fix restores actual
  enforcement.
- I-004 (Causality Is Not Co-Activation) — the checker's
  `CAUSAL_ADMISSION_REVIEWED` heuristic also only runs now that the path is
  fixed.

## Migration / reversal cost
Low. The checker fix is a one-line path correction. Leaving governance files
unpopulated has no migration cost since nothing currently depends on them
executing; the cost is purely in delayed enforcement until they are
authored.

## Consequences
- `check_architecture.py` is fixed and functional as of this ADR.
- `docs/PHASE_GATES.md` Phase-0 status notes that agent/skill governance
  content remains an open, explicitly-tracked item — not a hidden
  ambiguity (this satisfies gate item "No unresolved expensive-to-reverse
  ambiguity remains hidden" by making the absence explicit rather than
  silent).
- No `.claude/agents/*` or `.claude/skills/*` content is written until a
  separate, explicit approval authorizes specific content.

## Approval
Accepted by architect, 2026-07-08. Restoration content itself remains
pending separate authorization per Decision §3.
