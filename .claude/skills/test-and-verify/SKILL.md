---
name: test-and-verify
description: Runs pytest tests/architecture (and any future test suites) and checks the result against CLAUDE.md's Definition of Done. Use as the last step before reporting a task complete.
---

# Test and Verify

This skill runs tests and reports what actually happened — it does not
summarize a task as done because the implementation "should" work.

## Procedure

1. Run the architecture test suite:

   ```
   python3 -m pytest tests/architecture/ -v
   ```

2. Run any test suite specific to the module that changed, if one exists.
3. Run the mechanical architecture check (see `invariant-checker` skill):

   ```
   python3 .claude/scripts/check_architecture.py
   ```

4. Compare the result against CLAUDE.md's Definition of Done:
   - implementation exists
   - tests exist, or a justified reason for their absence is recorded
   - relevant tests pass
   - architecture checks pass
   - affected invariants are reviewed (see `invariant-checker` skill)
   - deviations are documented
   - no next-phase work was smuggled in (see `phase-planning` skill)

## Reporting rule

Report the exact commands run and their exact output (pass/fail counts,
skip reasons), not a paraphrase. A skipped test (e.g. `test_core_has_no_
provider_sdk_imports` skipping because `src/cognet/core` doesn't exist yet)
is not a pass — say explicitly that it skipped and why, so it's clear the
check hasn't actually run yet.

## What "verified" does not mean

Passing `tests/architecture` today mostly means the *specification* is
internally consistent (e.g. `test_spec_files_exist`,
`test_causal_admission_spec_exists`) — it does not mean kernel code is
correct, because in Phase 0/1 that code mostly doesn't exist yet. Don't
report a green test run as evidence of correctness beyond what the tests
actually exercise.
