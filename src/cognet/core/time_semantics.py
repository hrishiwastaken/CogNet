"""Valid-time / transaction-time semantics per MEMORY_IR.md "Time semantics".

`valid_time` and `transaction_time` are kept separate and neither may be
substituted with `created_at` (MEMORY_IR.md).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimeInterval:
    """An interval of valid time. Either bound may be open (None)."""

    start: datetime | None = None
    end: datetime | None = None

    def __post_init__(self) -> None:
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("TimeInterval.start must not be after end")
