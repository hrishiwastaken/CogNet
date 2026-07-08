"""Canonical identity per ADR-001.

Canonical identity is a runtime-generated UUIDv7 for every `MemoryObject`,
`Edge`, `ResolutionRecord`, `ProvenanceNode`, and `CausalAssessment`.
Content hashes are never canonical identity — see MEMORY_IR.md
"Identity semantics".
"""
from __future__ import annotations

import os
import time
import uuid

ObjectId = uuid.UUID


def new_id() -> ObjectId:
    """Generate a new canonical object identity (UUIDv7, RFC 9562).

    This runtime's stdlib `uuid` module has no `uuid.uuid7` (added upstream
    in a later Python release than this repository targets), so UUIDv7 is
    constructed directly from its RFC 9562 layout: a 48-bit big-endian
    millisecond Unix timestamp, a 4-bit version, 12 bits of randomness, a
    2-bit variant, and 62 more bits of randomness.
    """
    unix_ts_ms = time.time_ns() // 1_000_000
    ts_bytes = unix_ts_ms.to_bytes(6, byteorder="big")

    rand = bytearray(os.urandom(10))
    rand[0] = (rand[0] & 0x0F) | 0x70  # version nibble = 0b0111 (7)
    rand[2] = (rand[2] & 0x3F) | 0x80  # variant bits = 0b10

    return uuid.UUID(bytes=bytes(ts_bytes) + bytes(rand))


def is_uuidv7(value: uuid.UUID) -> bool:
    """True if `value` carries UUIDv7's version and RFC 4122 variant bits."""
    return value.version == 7 and value.variant == uuid.RFC_4122
