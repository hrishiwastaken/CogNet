"""ADR-002: BudgetVector preserves all nine accounting dimensions."""
from __future__ import annotations

import dataclasses

import pytest

from cognet.core import BudgetVector


def test_budget_vector_has_nine_named_dimensions():
    """Test contract #16."""
    names = {f.name for f in dataclasses.fields(BudgetVector)}
    assert names == {
        "graph_expansions",
        "embedding_queries",
        "rule_evaluations",
        "contradiction_checks",
        "hypothesis_operations",
        "tool_calls",
        "model_input_tokens",
        "model_output_tokens",
        "wall_time_ms",
    }
    assert len(names) == 9


def test_budget_vector_rejects_negative_dimension():
    with pytest.raises(ValueError):
        BudgetVector(graph_expansions=-1)


def test_budget_vector_is_immutable():
    budget = BudgetVector(graph_expansions=5)
    with pytest.raises(dataclasses.FrozenInstanceError):
        budget.graph_expansions = 10


def test_budget_vector_dimensions_are_independently_settable():
    budget = BudgetVector(graph_expansions=3, tool_calls=1, wall_time_ms=500)
    assert budget.graph_expansions == 3
    assert budget.embedding_queries == 0
    assert budget.tool_calls == 1
    assert budget.wall_time_ms == 500
