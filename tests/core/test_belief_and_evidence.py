"""I-007 (Memory != Belief) and ADR-005 historical immutability."""
from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest

from cognet.core import (
    BeliefState,
    Evidence,
    EvidenceRelation,
    MemoryObject,
    TypedUncertainty,
    new_id,
)


def _uncertainty():
    return TypedUncertainty()


def test_memory_object_and_belief_state_are_distinct_types():
    """Test contract #10: MemoryObject and BeliefState are distinct domain
    objects — a remembered proposition is not automatically a believed one."""
    assert MemoryObject is not BeliefState
    assert not issubclass(BeliefState, MemoryObject)
    assert not issubclass(MemoryObject, BeliefState)

    # BeliefState never needs a MemoryObject instance to construct — only
    # an id reference — reinforcing that belief computation and memory
    # storage are separate concerns.
    belief = BeliefState(
        proposition_id=new_id(),
        scope_id=new_id(),
        as_of_time=datetime.now(timezone.utc),
        confidence=0.7,
        support=0.5,
        source_reliability=0.6,
        cross_context_consistency=0.8,
        contradiction_pressure=0.1,
        reasoning_success=0.9,
        verification_level=0.5,
        uncertainty=_uncertainty(),
        computed_from_evidence_ids=(),
        computation_version="v1",
    )
    assert belief.proposition_id is not None


def test_belief_state_is_immutable():
    belief = BeliefState(
        proposition_id=new_id(),
        scope_id=new_id(),
        as_of_time=datetime.now(timezone.utc),
        confidence=0.7,
        support=0.5,
        source_reliability=0.6,
        cross_context_consistency=0.8,
        contradiction_pressure=0.1,
        reasoning_success=0.9,
        verification_level=0.5,
        uncertainty=_uncertainty(),
        computed_from_evidence_ids=(),
        computation_version="v1",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        belief.confidence = 0.99


def test_evidence_is_immutable():
    evidence = Evidence(
        memory_object_id=new_id(),
        target_proposition_id=new_id(),
        relation=EvidenceRelation.SUPPORTS,
        strength=0.8,
        observation_method="manual_review",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        evidence.strength = 0.1


def test_evidence_has_no_belief_fields():
    """Test contract #11: historical evidence remains representable
    independently of belief updates — Evidence carries no confidence/status
    field that a later belief recomputation could be confused with."""
    names = {f.name for f in dataclasses.fields(Evidence)}
    assert "confidence" not in names
    assert "belief" not in names


def test_multiple_belief_versions_do_not_require_mutating_evidence():
    evidence = Evidence(
        memory_object_id=new_id(),
        target_proposition_id=new_id(),
        relation=EvidenceRelation.SUPPORTS,
        strength=0.8,
        observation_method="manual_review",
    )
    proposition_id = new_id()
    scope_id = new_id()

    belief_v1 = BeliefState(
        proposition_id=proposition_id,
        scope_id=scope_id,
        as_of_time=datetime.now(timezone.utc),
        confidence=0.4,
        support=0.3,
        source_reliability=0.5,
        cross_context_consistency=0.5,
        contradiction_pressure=0.2,
        reasoning_success=0.5,
        verification_level=0.2,
        uncertainty=_uncertainty(),
        computed_from_evidence_ids=(evidence.memory_object_id,),
        computation_version="v1",
    )
    belief_v2 = BeliefState(
        proposition_id=proposition_id,
        scope_id=scope_id,
        as_of_time=datetime.now(timezone.utc),
        confidence=0.9,
        support=0.8,
        source_reliability=0.5,
        cross_context_consistency=0.5,
        contradiction_pressure=0.0,
        reasoning_success=0.9,
        verification_level=0.8,
        uncertainty=_uncertainty(),
        computed_from_evidence_ids=(evidence.memory_object_id,),
        computation_version="v2",
    )
    # Both belief versions coexist; the underlying evidence was never touched.
    assert belief_v1.confidence != belief_v2.confidence
    assert evidence.strength == 0.8
