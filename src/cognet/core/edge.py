"""Edge: MEMORY_IR.md "Edge".

`weight` is accessibility/traversal preference; `confidence` is
justification — the two must not be conflated (MEMORY_IR.md).

# CAUSAL_ADMISSION_REVIEWED
I-004's `CO_ACTIVATED_WITH -> CAUSES` prohibition is a *transition* rule,
not a property of a single Edge in isolation, and this module implements no
graph traversal or transition engine (forbidden for this milestone). The
ADR-008 anti-accumulation rule is enforced where a causal-status transition
actually happens — CausalAssessment's evidence-class gate (see causal.py) —
not here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .enums import EdgeType
from .ids import ObjectId, is_uuidv7, new_id


@dataclass
class Edge:
    source_id: ObjectId
    target_id: ObjectId
    edge_type: EdgeType
    scope_id: ObjectId
    id: ObjectId = field(default_factory=new_id)
    weight: float = 0.0
    confidence: float = 0.0
    support_count: int = 0
    contradiction_count: int = 0
    last_activated: datetime | None = None
    provenance_node_id: ObjectId | None = None

    def __post_init__(self) -> None:
        if not is_uuidv7(self.id):
            raise ValueError("Edge.id must be a UUIDv7 (ADR-001)")
