"""ResolutionRecord: MEMORY_IR.md / ADR-001 "Resolution state and
ResolutionRecord".

Ambiguous or unresolved identity is never represented by a fake placeholder
entity — it is represented by this record. AMBIGUOUS/DEFERRED records may
exist indefinitely without a canonical entity (I-014).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .enums import ResolutionState
from .ids import ObjectId, is_uuidv7, new_id


@dataclass
class ResolutionRecord:
    mention_ref: str
    resolution_state: ResolutionState
    id: ObjectId = field(default_factory=new_id)
    candidate_entity_ids: tuple[ObjectId, ...] = ()
    candidate_scores: tuple[float, ...] = ()
    evidence_ids: tuple[ObjectId, ...] = ()
    provenance_node_id: ObjectId | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        if not is_uuidv7(self.id):
            raise ValueError("ResolutionRecord.id must be a UUIDv7 (ADR-001)")

        if len(self.candidate_scores) != len(self.candidate_entity_ids):
            raise ValueError(
                "candidate_scores must be parallel to candidate_entity_ids (ADR-001)"
            )

        # ADR-001: "RESOLVED — committed to exactly one canonical entity ID"
        # and "NEW_IDENTITY — resolved to a newly minted entity" both commit
        # to exactly one entity.
        if self.resolution_state in (ResolutionState.RESOLVED, ResolutionState.NEW_IDENTITY):
            if len(self.candidate_entity_ids) != 1:
                raise ValueError(
                    f"{self.resolution_state.value} requires committing to exactly "
                    "one entity id (ADR-001)"
                )

        # ADR-001: "AMBIGUOUS — multiple candidates remain, no commitment."
        if self.resolution_state == ResolutionState.AMBIGUOUS and len(self.candidate_entity_ids) < 2:
            raise ValueError("AMBIGUOUS requires multiple (>=2) candidate entity ids (ADR-001)")
