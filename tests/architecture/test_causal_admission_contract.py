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

    # Once implemented, this test must construct a CausalAssessment whose
    # computed_from_evidence_ids resolve entirely to ASSOCIATIVE_SIGNAL-class
    # evidence and assert the transition to CAUSAL_HYPOTHESIS (or beyond) is
    # rejected by construction, regardless of evidence count (ADR-008 anti-
    # accumulation rule). Left unimplemented until the module exists so this
    # test has a real target to import.
    pytest.fail(
        "core/causal admission module exists but this test was not updated "
        "to exercise it — see ADR-008 anti-accumulation rule"
    )


def test_causal_transition_requires_review_record():
    core = SRC / "cognet" / "core"
    if not core.exists():
        pytest.skip("causal admission module not implemented yet")

    # Once implemented, this test must assert that no CausalStatus transition
    # (including to CAUSAL_REJECTED) can be recorded without a
    # CausalTransitionRecord carrying triggering_evidence_ids and a
    # reviewer_ref (ADR-008 "no transition is silent").
    pytest.fail(
        "core/causal admission module exists but this test was not updated "
        "to exercise it — see ADR-008 transition table"
    )
