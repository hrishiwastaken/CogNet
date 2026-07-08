"""Shared fixtures for P1-M1 executable typed IR tests.

Test-only helpers — production code never gets this kind of convenience
factory (CLAUDE.md: no speculative abstraction in the domain model itself).
"""
from __future__ import annotations

import pytest

from cognet.core import TaintState, TrustDomain, new_id


@pytest.fixture
def scope_id():
    return new_id()


@pytest.fixture
def source_id():
    return new_id()


@pytest.fixture
def provenance_node_id():
    return new_id()


@pytest.fixture
def default_trust_domain():
    return TrustDomain.USER_ASSERTED


@pytest.fixture
def default_taint_state():
    return TaintState.CLEAN
