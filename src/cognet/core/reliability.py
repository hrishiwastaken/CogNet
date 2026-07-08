"""SourceReliabilityAssessment: MEMORY_IR.md / ADR-005.

Deliberately has no `TrustDomain` field and no constructor path that reads
one — reliability is computed independently of the trust boundary a source
entered through (ADR-005: SourceReliability "must never be derived directly
from TrustDomain").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .ids import ObjectId


@dataclass(frozen=True)
class ReliabilityBasis:
    observation_method: str
    verification_history_ids: tuple[ObjectId, ...] = ()
    historical_success_count: int = 0
    historical_failure_count: int = 0

    def __post_init__(self) -> None:
        if self.historical_success_count < 0 or self.historical_failure_count < 0:
            raise ValueError("historical success/failure counts must not be negative")


@dataclass(frozen=True)
class SourceReliabilityAssessment:
    source_id: ObjectId
    context_domain: str
    reliability_score: float
    basis: ReliabilityBasis
    computed_from_evidence_ids: tuple[ObjectId, ...]
    computation_version: str
    as_of_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
