# CogNet Phase-0 Decisions

These are the default decisions for v2.1. Change through ADR, not silent implementation drift.

## D-001 Memory domain
CogNet accepts arbitrary observations:
- conversations
- documents
- codebases
- tool outputs
- web evidence
- sensor streams

All enter through source-specific adapters and are normalized into the typed IR.

## D-002 Sharing
Memory can be shared between agents only through explicit scopes and capability policy.
There is no single unrestricted communal brain.

## D-003 World vs personal
World knowledge and personal/user knowledge are separate scopes.

## D-004 Mutation rights
Agents submit observations, evidence, proposals, and feedback.
CogNet owns canonical mutation.

## D-005 Contradictory models
Supported through explicit scopes and possible worlds.

## D-006 Causality
Causal reasoning is distinct from association.
Causal edges use an admission policy.

## D-007 Privacy
Local-first core. Sync is optional and outside the initial kernel.

## D-008 First integration target
Generic MCP-compatible architecture.
Claude Code may be the first demo client.

## D-009 Internal representation
Rigid typed IR internally.
JSON at boundaries.

## D-010 Truth vs usefulness
Track separately.
A useful false heuristic remains a heuristic/procedure and is not promoted to factual belief.

## D-011 Initial persistence
SQLite is the Phase-1 default unless benchmark evidence forces change.

## D-012 Initial language
Python is the default implementation language for the kernel and SDK.

## D-013 MVC boundary
The first benchmarkable system is Minimum Viable Cognition, not the full research vision.
