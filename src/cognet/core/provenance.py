"""ProvenanceNode: MEMORY_IR.md "Provenance DAG node".

This milestone defines the typed record only — no DAG traversal engine and
no persistence (see docs/PHASE_GATES.md P1-M1 scope, MEMORY_IR.md's own
note that "the provenance graph must remain auditable," which is a property
of the data, not of an engine implemented here).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .ids import ObjectId, is_uuidv7, new_id


@dataclass(frozen=True)
class ProvenanceNode:
    operation: str
    algorithm_name: str
    algorithm_version: str
    parameters_digest: str
    input_object_ids: tuple[ObjectId, ...]
    source_ids: tuple[ObjectId, ...]
    id: ObjectId = field(default_factory=new_id)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not is_uuidv7(self.id):
            raise ValueError("ProvenanceNode.id must be a UUIDv7 (ADR-001)")
