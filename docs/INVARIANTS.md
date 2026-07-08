# CogNet v2.1 Invariants

Non-negotiable constraints that define the system's correctness and reliability guarantees.

---

## 1. LLM never owns canonical memory mutation

**Principle:** The LLM is a *reader and suggester*, never the authoritative writer of stored memory state.

**Enforcement:**
- All memory writes require explicit user confirmation or deterministic application logic
- LLM outputs are proposals; they cannot directly modify persisted state
- User intent, application rules, or scheduled tasks own mutation gates
- Audit trail logs *who* (not just what) changed memory

**Rationale:** LLM inference is probabilistic and can hallucinate. Canonical state must remain under human/deterministic control.

---

## 2. No unbounded reasoning loop

**Principle:** Reasoning chains must have explicit depth/step limits and termination conditions.

**Enforcement:**
- All inference paths have maximum iteration counts (e.g., max 5 retrieval rounds)
- Loops terminate on fixed timeout, step limit, or explicit convergence signal—never on "I think I'm done"
- Each loop round has measurable cost; system fails fast if budget exhausted
- Reasoning traces are recorded for audit

**Rationale:** LLMs can get stuck in circular or divergent reasoning. Bounded loops prevent resource exhaustion and cascading failures.

---

## 3. No causal edge from co-activation

**Principle:** Two concepts co-activating in the same retrieval result does not imply they caused, affected, or are related to each other.

**Enforcement:**
- Associative recall (embeddings, search) is labeled as such—never treated as causal inference
- Downstream use of co-activated items must re-verify their relationship
- Causal claims require explicit graph edges or policy-governed inference rules
- Mixing associative and causal reasoning must be auditable and flagged

**Rationale:** Embeddings find similar items; similarity is not evidence of causation. Confusing the two leads to false inferences.

---

## 4. No silent contradiction overwrite

**Principle:** When new information contradicts stored facts, the system must surface the contradiction, not silently replace it.

**Enforcement:**
- Conflict detection runs on all memory updates
- Contradictions halt the write and require user/policy resolution
- Overwrite only happens after explicit approval or automatic conflict resolution policy is applied
- Conflict log is immutable and queryable

**Rationale:** Silent overwrites hide data loss and inconsistencies. Transparency ensures users understand what changed and why.

---

## 5. No cross-scope promotion without policy

**Principle:** Information, rules, or inferences valid in one scope (e.g., one conversation, one user context) cannot be promoted to a wider scope (e.g., shared memory, default behavior) without explicit policy approval.

**Enforcement:**
- Scope is explicit on all memory; privacy/access defaults to most restrictive
- Promotion requires change event + human review or predefined policy rule
- Cross-scope access is logged with requester identity
- Policy violations raise alerts before state change

**Rationale:** Prevents context leakage, privacy violations, and unintended generalization of local facts to global systems.

---

## 6. Associative path ≠ inference proof

**Principle:** A retrieval path (A → B via embeddings) is evidence for association, not proof of the inference A → B.

**Enforcement:**
- Retrieval results include confidence scores and rank; they are not assertions
- Claims built on retrieved items must cite the source and note the uncertainty
- Inference proofs require explicit rules, causal edges, or corroborating evidence
- Reports distinguish "retrieved" from "concluded"

**Rationale:** LLMs conflate search results with validated facts. Maintaining the distinction prevents false reasoning.

---

## 7. Accessibility ≠ truth ≠ utility ≠ goal relevance

**Principle:** An item being retrievable, factually correct, useful, and relevant to current goals are four independent properties.

**Enforcement:**
- Memory items carry metadata on all four dimensions (access level, validity, utility, goal relevance)
- Retrieval must specify which dimension(s) matter for the current query
- Conflating dimensions (e.g., "retrieve all useful things" vs. "retrieve all relevant goals") is an error
- Queries that mix dimensions are flagged as ambiguous

**Rationale:** These are orthogonal concerns. A true fact may not be useful; an accessible item may be false or off-goal. Clear separation prevents silent errors.

---

## 8. Core kernel never imports provider SDKs

**Principle:** The core reasoning kernel is provider-agnostic and does not depend on any LLM SDK (OpenAI, Anthropic, etc.).

**Enforcement:**
- Core kernel (memory IR, retrieval, policy engine, conflict resolution) is provider-independent
- Provider-specific code (API calls, token counting, model selection) lives in an adapter/plugin layer
- Kernel dependencies are vendored or minimal (only stdlib + lightweight abstractions)
- Adapter layer is swappable; kernel never calls it directly for state mutation

**Rationale:** Prevents vendor lock-in, simplifies testing, and ensures the reasoning engine survives provider changes.

---

## Audit & Verification

All invariants are:
- **Testable:** Each has measurable assertions
- **Traceable:** Violations generate logs with context
- **Recoverable:** Violations trigger alerts before harm propagates

Invariant violations are *always* errors—never silent, never user-invisible.
