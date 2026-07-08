---
name: benchmark-runner
description: Runs or interprets the task sketches in docs/BENCHMARKS.md once a kernel exists to run them against. In Phase 0/1, reports which sketches are runnable and which require later-phase components, rather than fabricating results.
---

# Benchmark Runner

`docs/BENCHMARKS.md` defines the A/B/C/D controlled comparison, metrics, and
concrete task sketches (retrieval, resolution, epistemics, reasoning,
systems, long-horizon, security/integrity, and the causal-admission
sketches from ADR-008). This skill runs them when a kernel exists to run
them against, and is explicit about phase-gating otherwise.

## Phase gate check first

Before attempting to run anything, use the `phase-planning` skill's
procedure to check whether the components a given sketch needs actually
exist yet:

- Retrieval, resolution, systems (budget) sketches need at least Phase-1
  persistence and Phase-2/3 resolution/activation, depending on the sketch.
- The causal-admission sketches (ADR-008) need a `CausalAssessment`
  implementation, which is Phase-5 work ("one causal reasoning mode").
- The A/B/C/D controlled comparison itself is explicitly gated at Phase 7 —
  `docs/PHASE_GATES.md` Phase 7 gate, and `docs/DECISIONS.md`/
  `docs/PHASE_PLAN.md` both say not to claim superiority before that gate.

## If the required component doesn't exist

Report exactly that: which sketch was requested, which component it needs,
and that it is not runnable yet. Do not simulate a result, do not estimate
a plausible score, and do not run a substitute benchmark and present it as
equivalent. I-017 (Benchmark Claims Need Baselines) applies to internal
reporting too, not just external claims.

## If the required component exists

1. Construct the synthetic scenario exactly as sketched (e.g. "N
   `ASSOCIATIVE_SIGNAL` observations, zero causal-grade evidence" for the
   accumulation-trap sketch).
2. Run it against the real implementation, not a mock.
3. Report the metric(s) named in `docs/BENCHMARKS.md` for that category,
   plus pass/fail against the sketch's stated expected behavior.
4. For any comparative claim, include the baseline being compared against
   (I-017) and, where the sketch has an ablation counterpart in
   `docs/BENCHMARKS.md`'s "Ablations" list, run that too.

## Adversarial sketches specifically

The ADR-008 adversarial sketches (evidence-class mislabeling, silent
rejection attack) overlap with `.claude/agents/adversarial-tester.md`'s
scope. When both apply, this skill runs the sketch as a benchmark
(quantified pass/fail), while the adversarial-tester agent explores variants
beyond the sketch's literal scenario. Don't treat one as a substitute for
the other.
