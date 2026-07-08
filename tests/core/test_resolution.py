"""ADR-001: ResolutionRecord — unresolved ambiguity without fake entities."""
from __future__ import annotations

import pytest

from cognet.core import ResolutionRecord, ResolutionState, new_id


def test_ambiguous_record_exists_without_canonical_commitment():
    """Test contract #5: ResolutionRecord supports unresolved ambiguity
    without creating a fake entity."""
    candidates = (new_id(), new_id())
    record = ResolutionRecord(
        mention_ref="mention:123",
        resolution_state=ResolutionState.AMBIGUOUS,
        candidate_entity_ids=candidates,
        candidate_scores=(0.6, 0.4),
    )
    assert record.resolution_state == ResolutionState.AMBIGUOUS
    assert record.resolved_at is None
    # No canonical entity id field exists on ResolutionRecord at all —
    # ambiguity is representable without ever minting a placeholder entity.
    assert not hasattr(record, "canonical_entity_id")


def test_deferred_record_may_have_no_candidates_yet():
    record = ResolutionRecord(
        mention_ref="mention:456",
        resolution_state=ResolutionState.DEFERRED,
    )
    assert record.candidate_entity_ids == ()
    assert record.resolved_at is None


def test_candidate_scores_must_be_parallel_to_candidate_ids():
    """Test contract #6: candidate score validation per ADR-001."""
    with pytest.raises(ValueError):
        ResolutionRecord(
            mention_ref="mention:789",
            resolution_state=ResolutionState.AMBIGUOUS,
            candidate_entity_ids=(new_id(), new_id()),
            candidate_scores=(0.9,),  # mismatched length
        )


def test_resolved_requires_exactly_one_candidate():
    with pytest.raises(ValueError):
        ResolutionRecord(
            mention_ref="mention:abc",
            resolution_state=ResolutionState.RESOLVED,
            candidate_entity_ids=(new_id(), new_id()),
            candidate_scores=(0.9, 0.8),
        )

    # Exactly one candidate is valid.
    single = new_id()
    record = ResolutionRecord(
        mention_ref="mention:abc",
        resolution_state=ResolutionState.RESOLVED,
        candidate_entity_ids=(single,),
        candidate_scores=(0.95,),
    )
    assert record.candidate_entity_ids == (single,)


def test_new_identity_requires_exactly_one_candidate():
    with pytest.raises(ValueError):
        ResolutionRecord(
            mention_ref="mention:def",
            resolution_state=ResolutionState.NEW_IDENTITY,
            candidate_entity_ids=(),
        )


def test_ambiguous_requires_at_least_two_candidates():
    with pytest.raises(ValueError):
        ResolutionRecord(
            mention_ref="mention:ghi",
            resolution_state=ResolutionState.AMBIGUOUS,
            candidate_entity_ids=(new_id(),),
            candidate_scores=(0.5,),
        )


def test_resolution_record_id_is_uuidv7():
    record = ResolutionRecord(mention_ref="m", resolution_state=ResolutionState.DEFERRED)
    assert record.id.version == 7
