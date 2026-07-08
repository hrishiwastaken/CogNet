"""Frozen enumerations from docs/MEMORY_IR.md and docs/adr/.

Every value here is copied verbatim from a frozen specification document.
Do not add values that are not explicitly frozen (CLAUDE.md: "Do not invent
an ontology beyond the specification").

# CAUSAL_ADMISSION_REVIEWED
`CO_ACTIVATED_WITH` and `CAUSES` both appear below only as EdgeType values
copied from MEMORY_IR.md's "Edge vocabulary". No promotion logic between
them exists in this module — the ADR-008 anti-accumulation rule is enforced
in causal.py, not here.
"""
from __future__ import annotations

from enum import Enum


class KernelType(str, Enum):
    """MEMORY_IR.md "Kernel ontology"."""

    ENTITY = "ENTITY"
    PROPOSITION = "PROPOSITION"
    EVENT = "EVENT"
    PROCEDURE = "PROCEDURE"
    GOAL = "GOAL"
    EVIDENCE = "EVIDENCE"
    SOURCE = "SOURCE"


class ScopeType(str, Enum):
    """MEMORY_IR.md "Scope types"."""

    GLOBAL_WORLD = "GLOBAL_WORLD"
    USER_PRIVATE = "USER_PRIVATE"
    PROJECT = "PROJECT"
    SESSION = "SESSION"
    HYPOTHETICAL = "HYPOTHETICAL"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    AGENT_LOCAL = "AGENT_LOCAL"
    SHARED_TEAM = "SHARED_TEAM"


class TrustDomain(str, Enum):
    """MEMORY_IR.md / ADR-005 "Trust, taint, and contextual reliability"."""

    LOCAL_SYSTEM = "LOCAL_SYSTEM"
    USER_ASSERTED = "USER_ASSERTED"
    TRUSTED_TOOL = "TRUSTED_TOOL"
    UNTRUSTED_TOOL = "UNTRUSTED_TOOL"
    IMPORTED_DOCUMENT = "IMPORTED_DOCUMENT"
    EXTERNAL_NETWORK = "EXTERNAL_NETWORK"
    MODEL_GENERATED = "MODEL_GENERATED"


class TaintState(str, Enum):
    """MEMORY_IR.md / ADR-005."""

    CLEAN = "CLEAN"
    UNVERIFIED = "UNVERIFIED"
    TAINTED = "TAINTED"
    QUARANTINED = "QUARANTINED"


class AccessState(str, Enum):
    """MEMORY_IR.md "Common MemoryObject" access_state."""

    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    ARCHIVED = "ARCHIVED"
    PRUNED = "PRUNED"


class ResolutionState(str, Enum):
    """MEMORY_IR.md / ADR-001 "Resolution state and ResolutionRecord"."""

    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    NEW_IDENTITY = "NEW_IDENTITY"
    DEFERRED = "DEFERRED"


class EdgeType(str, Enum):
    """MEMORY_IR.md "Edge vocabulary"."""

    # Associative
    SEMANTIC_ASSOCIATION = "SEMANTIC_ASSOCIATION"
    CO_ACTIVATED_WITH = "CO_ACTIVATED_WITH"
    SIMILAR_TO = "SIMILAR_TO"
    # Structural
    PART_OF = "PART_OF"
    INSTANCE_OF = "INSTANCE_OF"
    USED_FOR = "USED_FOR"
    OBSERVED_IN = "OBSERVED_IN"
    # Temporal
    PRECEDES = "PRECEDES"
    FOLLOWS = "FOLLOWS"
    # Epistemic/inference
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    DERIVED_FROM = "DERIVED_FROM"
    PREDICTS = "PREDICTS"
    ENABLES = "ENABLES"
    PREVENTS = "PREVENTS"
    CAUSES = "CAUSES"


class CausalStatus(str, Enum):
    """MEMORY_IR.md / ADR-008 "Causal admission and assessment"."""

    ASSOCIATED = "ASSOCIATED"
    CAUSAL_HYPOTHESIS = "CAUSAL_HYPOTHESIS"
    CAUSAL_SUPPORTED = "CAUSAL_SUPPORTED"
    CAUSAL_VERIFIED = "CAUSAL_VERIFIED"
    CAUSAL_CONTESTED = "CAUSAL_CONTESTED"
    CAUSAL_REJECTED = "CAUSAL_REJECTED"


class EvidenceClass(str, Enum):
    """ADR-008 evidence classes."""

    ASSOCIATIVE_SIGNAL = "ASSOCIATIVE_SIGNAL"
    SOURCED_CAUSAL_ASSERTION = "SOURCED_CAUSAL_ASSERTION"
    INTERVENTION_EVIDENCE = "INTERVENTION_EVIDENCE"
    DOMAIN_RULE_MECHANISM = "DOMAIN_RULE_MECHANISM"
    DERIVED_INFERENCE = "DERIVED_INFERENCE"
    CONTESTING_EVIDENCE = "CONTESTING_EVIDENCE"


class EvidenceRelation(str, Enum):
    """MEMORY_IR.md "Evidence" relation."""

    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
