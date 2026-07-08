"""MemoryObject: the common envelope for every kernel type.

See MEMORY_IR.md "Common MemoryObject" and "Identity semantics" (ADR-001).

Implementation decision (not explicitly frozen): MEMORY_IR.md defines
field-level structure for PROPOSITION and EVIDENCE as separate satellite
records that reference their owning MemoryObject via `memory_object_id`
(see proposition.py, evidence.py) — they are not nested inside
`MemoryObject.payload`. ENTITY, EVENT, PROCEDURE, GOAL, and SOURCE have no
frozen payload schema at all. `payload` is therefore typed as an opaque
`KernelPayload` marker rather than a dict or an invented dataclass — see
`KernelPayload` docstring.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .enums import AccessState, KernelType, TaintState, TrustDomain
from .ids import ObjectId, is_uuidv7, new_id
from .time_semantics import TimeInterval


class KernelPayload:
    """Marker base for kernel_type-specific payload content.

    MEMORY_IR.md defines field-level structure only for kernel types that
    have their own frozen extension record (PROPOSITION -> Proposition,
    EVIDENCE -> Evidence). ENTITY, EVENT, PROCEDURE, GOAL, and SOURCE have no
    frozen payload schema yet. Subclassing this marker with concrete fields
    for those kernel types would invent an ontology the specification does
    not define — out of scope for this milestone (MEMORY_IR.md "Kernel
    ontology"; CLAUDE.md "No speculative abstraction before two concrete use
    cases").
    """


@dataclass
class MemoryCounters:
    """MEMORY_IR.md "Common MemoryObject" counters block.

    Mutable: these are expected to increment over a MemoryObject's lifetime,
    unlike the historical/versioned records elsewhere in this package.
    """

    exposure: int = 0
    retrieval: int = 0
    successful_use: int = 0
    failed_use: int = 0
    verification: int = 0

    def __post_init__(self) -> None:
        for name in ("exposure", "retrieval", "successful_use", "failed_use", "verification"):
            if getattr(self, name) < 0:
                raise ValueError(f"MemoryCounters.{name} must not be negative")


@dataclass
class MemoryObject:
    """MEMORY_IR.md "Common MemoryObject".

    `id` is canonical identity (ADR-001: UUIDv7) and is independent of
    `payload` / `content_hash`; mutating payload must never redefine
    identity. `content_hash` is an explicitly non-canonical fingerprint
    (dedup / integrity / exact-content comparison only) — never usable as
    `id`.
    """

    kernel_type: KernelType
    scope_id: ObjectId
    subtype: str
    source_id: ObjectId
    provenance_node_id: ObjectId
    trust_domain: TrustDomain
    taint_state: TaintState
    id: ObjectId = field(default_factory=new_id)
    content_hash: str | None = None
    payload: KernelPayload | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_time: TimeInterval | None = None
    transaction_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_state: AccessState = AccessState.HOT
    embedding_ref: str | None = None
    counters: MemoryCounters = field(default_factory=MemoryCounters)

    def __post_init__(self) -> None:
        if not is_uuidv7(self.id):
            raise ValueError("MemoryObject.id must be a UUIDv7 (ADR-001)")
        if self.scope_id is None:
            raise ValueError(
                "MemoryObject.scope_id is required — exactly one primary scope (MEMORY_IR.md)"
            )
