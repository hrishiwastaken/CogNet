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
