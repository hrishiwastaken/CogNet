"""CogNet core domain model (P1-M1: executable typed Memory IR).

This package contains only typed domain objects and their frozen validation
rules. It does not implement persistence, retrieval, activation, reasoning,
or any provider/LLM integration — see docs/PHASE_GATES.md P1-M1 scope.
"""
from .belief import BeliefState, TypedUncertainty
from .budget import BudgetVector
from .causal import (
    CausalAssessment,
    CausalPropositionRef,
    CausalTransitionRecord,
    EvidenceRef,
)
from .edge import Edge
from .enums import (
    AccessState,
    CausalStatus,
    EdgeType,
    EvidenceClass,
    EvidenceRelation,
    KernelType,
    ResolutionState,
    ScopeType,
    TaintState,
    TrustDomain,
)
from .evidence import Evidence
from .ids import ObjectId, is_uuidv7, new_id
from .memory_object import KernelPayload, MemoryCounters, MemoryObject
from .proposition import Proposition
from .provenance import ProvenanceNode
from .reliability import ReliabilityBasis, SourceReliabilityAssessment
from .resolution import ResolutionRecord
from .time_semantics import TimeInterval
from .value import MemoryValue

__all__ = [
    "AccessState",
    "BeliefState",
    "BudgetVector",
    "CausalAssessment",
    "CausalPropositionRef",
    "CausalStatus",
    "CausalTransitionRecord",
    "Edge",
    "EdgeType",
    "Evidence",
    "EvidenceClass",
    "EvidenceRef",
    "EvidenceRelation",
    "KernelPayload",
    "KernelType",
    "MemoryCounters",
    "MemoryObject",
    "MemoryValue",
    "ObjectId",
    "Proposition",
    "ProvenanceNode",
    "ReliabilityBasis",
    "ResolutionRecord",
    "ResolutionState",
    "ScopeType",
    "SourceReliabilityAssessment",
    "TaintState",
    "TimeInterval",
    "TrustDomain",
    "TypedUncertainty",
    "is_uuidv7",
    "new_id",
]
