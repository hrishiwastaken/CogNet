# CogNet Benchmark Strategy

Status: Approved (Phase 0) — 2026-07-08. Task sketches below satisfy the
Phase-0 gate item "Benchmark datasets/tasks are sketched." These are sketches
of task shape and synthetic-data structure, not built datasets — dataset
construction is Phase-6/7 work, gated by `docs/PHASE_GATES.md`.

## Primary controlled comparison

Same task suite and same weak LLM:

- A: no memory
- B: vector RAG
- C: conversation summary
- D: CogNet

## Headline comparison

- strong LLM + basic RAG
- weak LLM + CogNet

## Metrics

Retrieval:
- Precision@K
- Recall@K
- MRR

Resolution:
- entity merge accuracy
- entity split accuracy
- ambiguity calibration

Epistemics:
- contradiction precision/recall/F1
- Brier score where probabilistic targets exist
- expected calibration error where applicable
- stale-memory error rate

Reasoning:
- path relevance
- inference validity (separate from relevance)
- causal false-positive rate
- recovery after failed hypothesis
- repeated-dead-end rate

Systems:
- query latency
- compute budget consumption
- token usage
- memory growth
- graph density
- hot/warm/cold distribution

Long horizon:
- consistency
- personalization accuracy
- correction retention
- contradiction handling

Security/integrity:
- poisoning resistance
- unauthorized promotion rate
- scope leakage rate

## Phase-0 task sketches

Concrete task shapes for the metrics above, one per category. Each is
synthetic and small enough to hand-construct; real corpora are a later-phase
concern.

### Retrieval — "scoped fact lookup"
A fixed set of propositions distributed across `USER_PRIVATE`, `PROJECT`,
and `GLOBAL_WORLD` scopes, with some near-duplicate distractors that differ
only in scope or `valid_time`. Query asks for a fact "as of" a given time,
within a given scope. Scored on Precision@K/Recall@K/MRR against the one
correct in-scope, time-valid answer.

### Resolution — "same name, different entity" / "different name, same entity"
A mention stream containing: (a) two distinct entities sharing a surface
name, (b) one entity referred to by two different surface forms. Scored on
entity merge accuracy, entity split accuracy, and whether ambiguous cases
correctly produce a `ResolutionRecord` in `AMBIGUOUS`/`DEFERRED` state
instead of a forced merge (ambiguity calibration).

### Epistemics — "contradicting sources over time"
Two sources assert incompatible values for the same proposition at
overlapping `valid_time` windows, with one source later retracted or
corrected. Scored on contradiction precision/recall/F1, Brier score on the
resulting `BeliefState.confidence`, and whether the original (now-superseded)
evidence remains queryable unchanged (I-005, I-010).

### Reasoning — "co-activation is not causation" trap
A graph where two propositions are strongly `CO_ACTIVATED_WITH` but have no
sourced causal assertion, intervention evidence, or domain rule connecting
them. Scored on causal false-positive rate (a correct system reports
`ASSOCIATED`, never promotes to `CAUSES`) and on path relevance vs inference
validity scored separately (I-004, I-009).

### Causal admission — task sketches and adversarial tests (ADR-008)

**Accumulation trap.** Generate N (e.g. 500) synthetic `ASSOCIATIVE_SIGNAL`
observations co-activating the same pair of propositions, with steadily
increasing aggregate weight, and zero `SOURCED_CAUSAL_ASSERTION` /
`INTERVENTION_EVIDENCE` / `DOMAIN_RULE_MECHANISM` evidence. Expected: the
`CausalAssessment` for the pair stays at `ASSOCIATED` regardless of N. A
system that transitions to `CAUSAL_HYPOTHESIS` or beyond at any N fails —
this is the direct test of ADR-008's anti-accumulation rule.

**Legitimate intervention promotion.** One `INTERVENTION_EVIDENCE` record
(a synthetic "manipulate X, observe effect on Y" observation) is introduced
alongside a handful of `ASSOCIATIVE_SIGNAL` records. Expected: transition to
at least `CAUSAL_HYPOTHESIS`, with a `CausalTransitionRecord` whose
`triggering_evidence_ids` cite only the intervention evidence, never the
associative signals.

**Contested reversal.** A claim reaches `CAUSAL_SUPPORTED` via
`INTERVENTION_EVIDENCE`. A later `CONTESTING_EVIDENCE` record (failed
replication) arrives in the same scope. Expected: a new `CausalAssessment`
version at `CAUSAL_CONTESTED`, appended (not overwriting) the prior
`CAUSAL_SUPPORTED` version; both remain queryable by `as_of_time` (I-005).

**Cross-scope contest isolation.** The same contesting evidence as above is
recorded only in `PROJECT` scope A. Scope B's independently computed
`CausalAssessment` for the same claim is queried. Expected: scope B's
assessment is unaffected unless the contest was explicitly promoted per
ADR-004 — no automatic cross-scope contest propagation (I-006).

**Adversarial — evidence-class mislabeling attack.** An adversarial or
careless ingestion adapter labels `ASSOCIATIVE_SIGNAL` evidence as
`SOURCED_CAUSAL_ASSERTION` to force a transition it should not be able to
trigger. Expected defense: the admission policy does not trust
adapter-declared `evidence_class` alone for a transition-granting class —
`SOURCED_CAUSAL_ASSERTION` claims are cross-checked against the source's
`SourceReliabilityAssessment` for the relevant `context_domain` (ADR-005)
before being counted as transition-triggering. A system that promotes on
adapter-declared class alone, with no reliability cross-check, fails this
test. This is the adversarial-tester agent's canonical probe for I-004 +
I-011 (untrusted content must not self-promote).

**Adversarial — silent rejection attack.** An attempt to move a
`CausalAssessment` to `CAUSAL_REJECTED` (or to delete/overwrite a contested
assessment) without a `CausalTransitionRecord` carrying
`triggering_evidence_ids` and a `reviewer_ref`. Expected defense: the
operation is refused at the construction/type level, not merely logged as a
warning.

### Systems — "budget exhaustion under fan-out"
A query whose naive expansion would visit an unbounded number of graph
nodes. Scored on whether termination fires on the correct `BudgetVector`
dimension (`graph_expansions`), query latency, and whether the normalized
scheduling scalar was used only for ranking, not as the recorded budget
(ADR-002).

### Long horizon — "correction retention"
A multi-session sequence where the user corrects a previously stored
preference. Scored on whether later sessions reflect the correction
(correction retention) while the original, now-superseded proposition
remains in history (I-007), and on personalization accuracy after the
correction.

### Security/integrity — "untrusted document promotion attempt"
An `IMPORTED_DOCUMENT` source asserts a claim designed to look like a
verified fact. Scored on unauthorized promotion rate (the claim must not
reach `CAUSAL_VERIFIED` or `CLEAN` taint without passing an explicit
promotion rule) and scope leakage rate if the same content is scoped to
`USER_PRIVATE` vs `GLOBAL_WORLD` (I-006, I-011).

## Ablations

At minimum compare CogNet with:
- no lateral inhibition
- no failed-path memory
- no typed uncertainty
- no belief/memory separation
- no scope-aware retrieval
- no usefulness-gated reinforcement

## Research discipline

A result is not a win because a demo looks intelligent.
Predeclare tasks and metrics where practical.
Publish failure cases.
