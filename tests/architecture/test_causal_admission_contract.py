"""Architecture-contract tests for ADR-008 (Causal Admission and Assessment Policy).

These tests become active as the implementation appears. They intentionally
skip when the corresponding module does not yet exist, mirroring
test_invariant_contract.py.
"""
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def test_causal_admission_spec_exists():
    adr = ROOT / "docs" / "adr" / "ADR-008-causal-admission-and-assessment-policy.md"
    assert adr.exists(), "ADR-008 is required before any causal admission code is written"

    memory_ir = (ROOT / "docs" / "MEMORY_IR.md").read_text(encoding="utf-8")
    required_terms = [
        "CausalAssessment",
        "EvidenceClass",
        "ASSOCIATIVE_SIGNAL",
        "CausalTransitionRecord",
    ]
    missing = [t for t in required_terms if t not in memory_ir]
    assert not missing, f"MEMORY_IR.md is missing causal-admission terms: {missing}"


def test_associative_evidence_alone_cannot_reach_causal_hypothesis():
    core = SRC / "cognet" / "core"
    if not core.exists():
        pytest.skip("causal admission module not implemented yet")

    from cognet.core import CausalAssessment, CausalPropositionRef, CausalStatus, EvidenceClass, EvidenceRef, new_id

    evidence = tuple(
        EvidenceRef(evidence_id=new_id(), evidence_class=EvidenceClass.ASSOCIATIVE_SIGNAL)
        for _ in range(50)
    )
    with pytest.raises(ValueError):
        CausalAssessment(
            causal_proposition_ref=CausalPropositionRef(source_ref=new_id(), target_ref=new_id()),
            scope_id=new_id(),
            causal_status=CausalStatus.CAUSAL_HYPOTHESIS,
            supporting_evidence=evidence,
            computed_from_evidence_ids=tuple(e.evidence_id for e in evidence),
            computation_version="v1",
        )


def test_causal_transition_requires_review_record():
    core = SRC / "cognet" / "core"
    if not core.exists():
        pytest.skip("causal admission module not implemented yet")

    from cognet.core import CausalStatus, CausalTransitionRecord, new_id

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
