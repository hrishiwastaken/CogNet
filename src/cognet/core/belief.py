"""BeliefState: MEMORY_IR.md "BeliefState".

Belief is not a MemoryObject rewrite (I-007) — BeliefState is a distinct,
immutable, versioned computation over evidence. Recomputation produces a new
BeliefState (new computation_version / as_of_time); it never mutates a
prior one (I-005).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .ids import ObjectId


@dataclass(frozen=True)
class TypedUncertainty:
    """I-015 "Typed Uncertainty" — the six frozen categories."""

    epistemic: float = 0.0
    aleatoric: float = 0.0
    ambiguity: float = 0.0
    conflict: float = 0.0
    staleness: float = 0.0
    missing_evidence: float = 0.0


@dataclass(frozen=True)
class BeliefState:
    proposition_id: ObjectId
    scope_id: ObjectId
    as_of_time: datetime
    confidence: float  # epistemic confidence — independent of TrustDomain/TaintState (ADR-005)
    support: float
    # Summary drawn from SourceReliabilityAssessment records relevant to
    # computed_from_evidence_ids — not a redefinition of SourceReliability
    # and never derived from TrustDomain (ADR-005; MEMORY_IR.md "BeliefState").
    source_reliability: float
    cross_context_consistency: float
    contradiction_pressure: float
    reasoning_success: float
    verification_level: float
    uncertainty: TypedUncertainty
    computed_from_evidence_ids: tuple[ObjectId, ...]
    computation_version: str
