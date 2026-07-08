"""ADR-005: TrustDomain, TaintState, SourceReliability, and epistemic
confidence are independent dimensions with no derivation between them.
"""
from __future__ import annotations

import dataclasses

import pytest

from cognet.core import (
    BeliefState,
    ReliabilityBasis,
    SourceReliabilityAssessment,
    TaintState,
    TrustDomain,
    TypedUncertainty,
    new_id,
)


def _field_names(dc_type) -> set[str]:
    return {f.name for f in dataclasses.fields(dc_type)}


def test_source_reliability_assessment_has_no_trust_domain_field():
    """Test contract #7: TrustDomain independent from SourceReliabilityAssessment.

    There is no field, and therefore no derivation path, from TrustDomain to
    SourceReliabilityAssessment.
    """
    assert "trust_domain" not in _field_names(SourceReliabilityAssessment)


def test_source_reliability_assessment_has_no_taint_state_field():
    """Test contract #8: TaintState independent from SourceReliabilityAssessment."""
    assert "taint_state" not in _field_names(SourceReliabilityAssessment)


def test_belief_state_confidence_has_no_trust_domain_field():
    """Test contract #9: epistemic confidence (BeliefState.confidence) is
    independent from TrustDomain — BeliefState has no trust_domain field or
    parameter to derive confidence from."""
    assert "confidence" in _field_names(BeliefState)
    assert "trust_domain" not in _field_names(BeliefState)


def test_low_reliability_source_can_have_any_trust_domain():
    """A TRUSTED_TOOL is not automatically reliable, and an UNTRUSTED_TOOL is
    not automatically unreliable — reliability is computed, not derived."""
    trusted_but_unreliable = SourceReliabilityAssessment(
        source_id=new_id(),
        context_domain="external_scientific_claim",
        reliability_score=0.1,
        basis=ReliabilityBasis(observation_method="manual_review"),
        computed_from_evidence_ids=(),
        computation_version="v1",
    )
    untrusted_but_reliable_in_context = SourceReliabilityAssessment(
        source_id=new_id(),
        context_domain="personal_preference",
        reliability_score=0.9,
        basis=ReliabilityBasis(observation_method="manual_review"),
        computed_from_evidence_ids=(),
        computation_version="v1",
    )
    # Both constructions succeed with no TrustDomain involved at all —
    # nothing in the type couples the two dimensions.
    assert trusted_but_unreliable.reliability_score == 0.1
    assert untrusted_but_reliable_in_context.reliability_score == 0.9


def test_reliability_basis_rejects_negative_counts():
    with pytest.raises(ValueError):
        ReliabilityBasis(observation_method="x", historical_success_count=-1)


def test_typed_uncertainty_has_six_frozen_dimensions():
    names = _field_names(TypedUncertainty)
    assert names == {
        "epistemic",
        "aleatoric",
        "ambiguity",
        "conflict",
        "staleness",
        "missing_evidence",
    }


def test_trust_domain_and_taint_state_enums_are_frozen_value_sets():
    assert {m.value for m in TrustDomain} == {
        "LOCAL_SYSTEM",
        "USER_ASSERTED",
        "TRUSTED_TOOL",
        "UNTRUSTED_TOOL",
        "IMPORTED_DOCUMENT",
        "EXTERNAL_NETWORK",
        "MODEL_GENERATED",
    }
    assert {m.value for m in TaintState} == {"CLEAN", "UNVERIFIED", "TAINTED", "QUARANTINED"}
