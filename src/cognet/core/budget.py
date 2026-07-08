"""BudgetVector: ADR-002 / docs/ARCHITECTURE.md "Budget accounting".

The vector is the canonical budget state. A normalized scalar cost
projection computed over it (for scheduling comparisons) is derived,
non-canonical, and not represented here — computing that projection and
acting on it is Cognitive Control Plane scheduling behavior, out of scope
for this milestone (docs/PHASE_PLAN.md Phase 3, ARCHITECTURE.md).
"""
from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass(frozen=True)
class BudgetVector:
    graph_expansions: int = 0
    embedding_queries: int = 0
    rule_evaluations: int = 0
    contradiction_checks: int = 0
    hypothesis_operations: int = 0
    tool_calls: int = 0
    model_input_tokens: int = 0
    model_output_tokens: int = 0
    wall_time_ms: int = 0

    def __post_init__(self) -> None:
        for f in fields(self):
            if getattr(self, f.name) < 0:
                raise ValueError(f"BudgetVector.{f.name} must not be negative")
