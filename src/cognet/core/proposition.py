"""Proposition: MEMORY_IR.md "Proposition".

Implementation decision (not explicitly frozen): a Proposition is a
satellite record for a MemoryObject whose kernel_type is PROPOSITION — it
references its MemoryObject by id (`memory_object_id`, exactly as frozen)
rather than being nested inside `MemoryObject.payload`. See
memory_object.py's `KernelPayload` docstring for the reasoning.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .ids import ObjectId


@dataclass
class Proposition:
    memory_object_id: ObjectId
    subject_ref: ObjectId
    predicate: str
    object_ref_or_value: Any  # reference (ObjectId) or a literal value — union not further frozen
    polarity: str   # value set not frozen by MEMORY_IR.md — plain str, no invented enum
    modality: str   # value set not frozen by MEMORY_IR.md — plain str, no invented enum
    qualifiers: dict[str, Any] = field(default_factory=dict)
