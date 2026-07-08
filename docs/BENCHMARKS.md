# CogNet Benchmark Strategy

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
