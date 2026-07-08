"""Causal admission and assessment: ADR-008.

Causal justification is a scoped, versioned assessment over a causal
proposition — never a confidence number on an edge, and never derivable by
accumulating ASSOCIATIVE_SIGNAL evidence (I-004, ADR-008 anti-accumulation
rule). Causal proposition and CausalAssessment are distinct types.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .enums import CausalStatus, EvidenceClass
from .ids import ObjectId, is_uuidv7, new_id

# Evidence classes that can never, alone or combined, justify a transition
# beyond ASSOCIATED (ADR-008 anti-accumulation rule). CONTESTING_EVIDENCE is
# excluded here too: it drives CAUSAL_CONTESTED specifically (validated
# separately below), not a promotion.
NON_QUALIFYING_FOR_PROMOTION = frozenset(
    {EvidenceClass.ASSOCIATIVE_SIGNAL, EvidenceClass.CONTESTING_EVIDENCE}
)


@dataclass(frozen=True)
class CausalPropositionRef:
    """The causal claim being assessed.

    Distinct from CausalAssessment itself (ADR-008: "Causal proposition !=
    CausalAssessment").
    """

    source_ref: ObjectId
    target_ref: ObjectId
    mechanism_ref: str | None = None


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: ObjectId
    evidence_class: EvidenceClass


@dataclass(frozen=True)
class CausalTransitionRecord:
    """ADR-008: "Every transition requires a CausalTransitionRecord... no
    transition is silent."""

    from_status: CausalStatus
    to_status: CausalStatus
    triggering_evidence_ids: tuple[ObjectId, ...]
    reviewer_ref: str
    transitioned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.triggering_evidence_ids:
            raise ValueError(
                "CausalTransitionRecord requires triggering_evidence_ids — "
                "no transition is silent (ADR-008)"
            )
        if not self.reviewer_ref:
            raise ValueError(
                "CausalTransitionRecord requires a reviewer_ref — "
                "no transition is silent (ADR-008)"
            )


@dataclass(frozen=True)
class CausalAssessment:
    """ADR-008: scoped, versioned causal justification.

    Recomputation appends a new CausalAssessment (new computation_version /
    as_of_time); it never mutates a prior one (I-005, I-010), mirroring
    BeliefState.
    """

    causal_proposition_ref: CausalPropositionRef
    scope_id: ObjectId
    causal_status: CausalStatus
    supporting_evidence: tuple[EvidenceRef, ...]
    computed_from_evidence_ids: tuple[ObjectId, ...]
    computation_version: str
    id: ObjectId = field(default_factory=new_id)
    context_domain: str | None = None
    contested: bool = False
    contesting_evidence: tuple[EvidenceRef, ...] = ()
    transition_history: tuple[CausalTransitionRecord, ...] = ()
    as_of_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provenance_node_id: ObjectId | None = None

    def __post_init__(self) -> None:
        if not is_uuidv7(self.id):
            raise ValueError("CausalAssessment.id must be a UUIDv7 (ADR-001)")

        if self.causal_status == CausalStatus.CAUSAL_CONTESTED:
            # ADR-008: "any status -> CAUSAL_CONTESTED requires any credible
            # CONTESTING_EVIDENCE, not yet reviewed."
            if not self.contesting_evidence:
                raise ValueError(
                    "CAUSAL_CONTESTED requires at least one contesting evidence "
                    "item (ADR-008)"
                )
        elif self.causal_status == CausalStatus.CAUSAL_REJECTED:
            # ADR-008: rejection requires "contesting evidence validated and
            # prior support found insufficient (explicit review)" — i.e. a
            # recorded, reviewed transition, never silent.
            if not self.transition_history:
                raise ValueError(
                    "CAUSAL_REJECTED requires a recorded, reviewed transition — "
                    "no transition is silent (ADR-008)"
                )
        elif self.causal_status != CausalStatus.ASSOCIATED:
            # ADR-008 anti-accumulation rule: ASSOCIATIVE_SIGNAL evidence, in
            # any quantity, can never justify a status beyond ASSOCIATED.
            qualifying = [
                ref
                for ref in self.supporting_evidence
                if ref.evidence_class not in NON_QUALIFYING_FOR_PROMOTION
            ]
            if not qualifying:
                raise ValueError(
                    "CausalAssessment cannot reach a status beyond ASSOCIATED "
                    "without at least one non-associative, non-contesting "
                    "evidence class (ADR-008 anti-accumulation rule) — got "
                    f"status={self.causal_status.value} with evidence classes "
                    f"{[ref.evidence_class.value for ref in self.supporting_evidence]}"
                )
