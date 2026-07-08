"""Evidence: MEMORY_IR.md "Evidence".

Historical evidence must remain representable independently of later belief
updates (ADR-005 "Historical immutability rule") — Evidence is therefore an
immutable record. A later reassessment produces a new BeliefState /
CausalAssessment; it never mutates this object.
"""
from __future__ import annotations

from dataclasses import dataclass

from .enums import EvidenceRelation
from .ids import ObjectId


@dataclass(frozen=True)
class Evidence:
    memory_object_id: ObjectId
    target_proposition_id: ObjectId
    relation: EvidenceRelation
    strength: float
    observation_method: str
    # Implementation decision (not explicitly frozen): reliability_inputs
    # shape is not detailed in MEMORY_IR.md; represented as a tuple of
    # referenced ids (e.g. prior assessments) rather than an invented
    # structure. Tuple, not list, to keep this frozen record's fields
    # immutable end-to-end.
    reliability_inputs: tuple[ObjectId, ...] = ()
