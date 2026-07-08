"""MemoryValue: MEMORY_IR.md "Value vector".

The four dimensions must not be collapsed into one scalar (I-008).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryValue:
    truth_confidence: float
    empirical_utility: float
    accessibility: float
    goal_relevance: float
