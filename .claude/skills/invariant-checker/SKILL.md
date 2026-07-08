---
name: invariant-checker
description: Runs and interprets .claude/scripts/check_architecture.py, and manually reasons through docs/INVARIANTS.md against a diff. Use whenever code changes under src/, before calling a task done.
---

# Invariant Checker

Two layers: a mechanical check, and a manual walk-through the mechanical
check cannot cover.

## Layer 1 — mechanical

Run:

```
python3 .claude/scripts/check_architecture.py
```

This currently catches two things:
- provider SDK imports (`anthropic`, `openai`, `google.generativeai`,
  `google.genai`, `cohere`, `mistralai`) anywhere under `src/cognet/core`
  (I-013)
- `CO_ACTIVATED_WITH` and `CAUSES` text co-occurring in a file under `src/`
  without a `CAUSAL_ADMISSION_REVIEWED` marker (I-004 heuristic)

A pass here is necessary, not sufficient — it is a static, textual/AST
heuristic, not a proof of invariant compliance. Treat a pass as "no known
mechanical violation," not "compliant."

## Layer 2 — manual walk-through

For each of I-001 through I-020 in `docs/INVARIANTS.md`, ask whether the
diff touches its subject matter, and if so, check its "Violation example"
specifically:

- I-001..I-003: does this add a model call where a deterministic mechanism
  would do, or run reasoning without a budget/step count?
- I-004..I-005, I-009: does this let associative evidence read as causal or
  inferential proof, or overwrite a contradiction? (Also check ADR-008's
  anti-accumulation rule specifically — it is not restated in I-004's short
  text.)
- I-006, I-010, I-014: does this cross a scope boundary without policy, or
  make identity resolution force a merge, or lose provenance?
- I-007, I-008, I-015, I-016: does this collapse memory into belief, collapse
  the four value dimensions, collapse typed uncertainty into one number, or
  use an untyped dict internally instead of at a boundary?
- I-011, I-012, I-013: does this let untrusted content self-promote, delete
  something for being rare, or import a provider SDK into core?
- I-017..I-020: does a benchmark claim lack a baseline, does an LLM rewrite
  the graph directly, does a failed-path anti-prior fail to decay/scope, or
  does this smuggle in later-phase work?

Report which invariants were checked and found compliant, not just which
were violated — an invariant review that only lists failures looks the same
as one that never checked the passing cases.

## Relationship to the adversarial-tester agent

This skill checks the diff as written. It does not try to break it under
adversarial input — that is `.claude/agents/adversarial-tester.md`'s job.
Run this skill first; hand confirmed-clean diffs to the adversarial tester
next, not instead.
