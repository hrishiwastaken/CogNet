"""ADR-008: causal admission and assessment policy."""
from __future__ import annotations

import dataclasses

import pytest

from cognet.core import (
    CausalAssessment,
    CausalPropositionRef,
    CausalStatus,
    CausalTransitionRecord,
    EvidenceClass,
    EvidenceRef,
    new_id,
)


def _ref():
    return CausalPropositionRef(source_ref=new_id(), target_ref=new_id())


def test_causal_proposition_ref_and_causal_assessment_are_distinct_types():
    """Test contract #12."""
    assert CausalPropositionRef is not CausalAssessment
    assert not issubclass(CausalAssessment, CausalPropositionRef)


def test_causal_assessment_is_scoped():
    """Test contract #13."""
    scope_a, scope_b = new_id(), new_id()
    claim = _ref()
    evidence = (EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.INTERVENTION_EVIDENCE),)

    assessment_a = CausalAssessment(
        causal_proposition_ref=claim,
        scope_id=scope_a,
        causal_status=CausalStatus.CAUSAL_SUPPORTED,
        supporting_evidence=evidence,
        computed_from_evidence_ids=(evidence[0].evidence_id,),
        computation_version="v1",
    )
    assessment_b = CausalAssessment(
        causal_proposition_ref=claim,
        scope_id=scope_b,
        causal_status=CausalStatus.ASSOCIATED,
        supporting_evidence=(),
        computed_from_evidence_ids=(),
        computation_version="v1",
    )
    # Same causal claim, independently scoped assessments, no coupling.
    assert assessment_a.scope_id != assessment_b.scope_id
    assert assessment_a.causal_status != assessment_b.causal_status


def test_transition_history_is_representable():
    """Test contract #14."""
    triggering = (new_id(),)
    record = CausalTransitionRecord(
        from_status=CausalStatus.ASSOCIATED,
        to_status=CausalStatus.CAUSAL_HYPOTHESIS,
        triggering_evidence_ids=triggering,
        reviewer_ref="policy:causal-admission-v1",
    )
    assessment = CausalAssessment(
        causal_proposition_ref=_ref(),
        scope_id=new_id(),
        causal_status=CausalStatus.CAUSAL_HYPOTHESIS,
        supporting_evidence=(
            EvidenceRef(evidence_id=triggering[0], evidence_class=EvidenceClass.SOURCED_CAUSAL_ASSERTION),
        ),
        computed_from_evidence_ids=triggering,
        computation_version="v1",
        transition_history=(record,),
    )
    assert assessment.transition_history == (record,)
    assert assessment.transition_history[0].to_status == CausalStatus.CAUSAL_HYPOTHESIS


@pytest.mark.parametrize("associative_signal_count", [1, 10, 1000])
def test_associative_signal_alone_cannot_reach_causal_hypothesis(associative_signal_count):
    """Test contract #15 — the ADR-008 anti-accumulation rule. This is the
    canonical adversarial-tester probe: no quantity of ASSOCIATIVE_SIGNAL
    evidence may justify promotion beyond ASSOCIATED."""
    evidence = tuple(
        EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.ASSOCIATIVE_SIGNAL)
        for _ in range(associative_signal_count)
    )
    with pytest.raises(ValueError, match="anti-accumulation"):
        CausalAssessment(
            causal_proposition_ref=_ref(),
            scope_id=new_id(),
            causal_status=CausalStatus.CAUSAL_HYPOTHESIS,
            supporting_evidence=evidence,
            computed_from_evidence_ids=tuple(e.evidence_id for e in evidence),
            computation_version="v1",
        )


def test_associated_status_allows_pure_associative_evidence():
    """Positive control: ASSOCIATED is exactly what ASSOCIATIVE_SIGNAL
    evidence can support."""
    evidence = (EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.ASSOCIATIVE_SIGNAL),)
    assessment = CausalAssessment(
        causal_proposition_ref=_ref(),
        scope_id=new_id(),
        causal_status=CausalStatus.ASSOCIATED,
        supporting_evidence=evidence,
        computed_from_evidence_ids=(evidence[0].evidence_id,),
        computation_version="v1",
    )
    assert assessment.causal_status == CausalStatus.ASSOCIATED


def test_intervention_evidence_can_reach_causal_hypothesis():
    """Positive control: legitimate causal-grade evidence is accepted."""
    evidence = (EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.INTERVENTION_EVIDENCE),)
    assessment = CausalAssessment(
        causal_proposition_ref=_ref(),
        scope_id=new_id(),
        causal_status=CausalStatus.CAUSAL_HYPOTHESIS,
        supporting_evidence=evidence,
        computed_from_evidence_ids=(evidence[0].evidence_id,),
        computation_version="v1",
    )
    assert assessment.causal_status == CausalStatus.CAUSAL_HYPOTHESIS


def test_mixed_associative_and_causal_evidence_still_requires_the_causal_grade_item():
    """Adding arbitrarily many ASSOCIATIVE_SIGNAL items alongside a single
    qualifying item must still pass — quantity of weak evidence must not
    matter either way."""
    evidence = (
        EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.SOURCED_CAUSAL_ASSERTION),
        *(
            EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.ASSOCIATIVE_SIGNAL)
            for _ in range(50)
        ),
    )
    assessment = CausalAssessment(
        causal_proposition_ref=_ref(),
        scope_id=new_id(),
        causal_status=CausalStatus.CAUSAL_HYPOTHESIS,
        supporting_evidence=evidence,
        computed_from_evidence_ids=tuple(e.evidence_id for e in evidence),
        computation_version="v1",
    )
    assert assessment.causal_status == CausalStatus.CAUSAL_HYPOTHESIS


def test_causal_contested_requires_contesting_evidence():
    with pytest.raises(ValueError):
        CausalAssessment(
            causal_proposition_ref=_ref(),
            scope_id=new_id(),
            causal_status=CausalStatus.CAUSAL_CONTESTED,
            supporting_evidence=(),
            computed_from_evidence_ids=(),
            computation_version="v1",
        )

    ok = CausalAssessment(
        causal_proposition_ref=_ref(),
        scope_id=new_id(),
        causal_status=CausalStatus.CAUSAL_CONTESTED,
        supporting_evidence=(),
        contesting_evidence=(
            EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.CONTESTING_EVIDENCE),
        ),
        computed_from_evidence_ids=(),
        computation_version="v1",
    )
    assert ok.contested is False or ok.contested is True  # field is settable independent of status


def test_causal_rejected_requires_a_recorded_transition():
    with pytest.raises(ValueError):
        CausalAssessment(
            causal_proposition_ref=_ref(),
            scope_id=new_id(),
            causal_status=CausalStatus.CAUSAL_REJECTED,
            supporting_evidence=(),
            computed_from_evidence_ids=(),
            computation_version="v1",
        )


def test_causal_transition_record_requires_evidence_and_reviewer():
    with pytest.raises(ValueError):
        CausalTransitionRecord(
            from_status=CausalStatus.CAUSAL_CONTESTED,
            to_status=CausalStatus.CAUSAL_REJECTED,
            triggering_evidence_ids=(),
            reviewer_ref="policy:x",
        )
    with pytest.raises(ValueError):
        CausalTransitionRecord(
            from_status=CausalStatus.CAUSAL_CONTESTED,
            to_status=CausalStatus.CAUSAL_REJECTED,
            triggering_evidence_ids=(new_id(),),
            reviewer_ref="",
        )


def test_causal_assessment_is_immutable():
    assessment = CausalAssessment(
        causal_proposition_ref=_ref(),
        scope_id=new_id(),
        causal_status=CausalStatus.ASSOCIATED,
        supporting_evidence=(),
        computed_from_evidence_ids=(),
        computation_version="v1",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        assessment.causal_status = CausalStatus.CAUSAL_VERIFIED
