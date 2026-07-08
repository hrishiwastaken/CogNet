"""ADR-001 / MEMORY_IR.md "Common MemoryObject": identity, content_hash,
scope cardinality.
"""
from __future__ import annotations

import uuid

import pytest

from cognet.core import (
    KernelPayload,
    KernelType,
    MemoryCounters,
    MemoryObject,
    TaintState,
    TrustDomain,
    new_id,
)


def _make_object(**overrides):
    defaults = dict(
        kernel_type=KernelType.ENTITY,
        scope_id=new_id(),
        subtype="Person",
        source_id=new_id(),
        provenance_node_id=new_id(),
        trust_domain=TrustDomain.USER_ASSERTED,
        taint_state=TaintState.CLEAN,
    )
    defaults.update(overrides)
    return MemoryObject(**defaults)


def test_memory_object_id_is_uuidv7():
    obj = _make_object()
    assert obj.id.version == 7


def test_memory_object_rejects_non_uuidv7_id():
    with pytest.raises(ValueError):
        _make_object(id=uuid.uuid4())


def test_mutable_payload_does_not_redefine_identity():
    """Test contract #2: mutable payload does not define canonical identity."""
    obj = _make_object()
    original_id = obj.id

    class FakeEntityPayload(KernelPayload):
        def __init__(self, name):
            self.name = name

    obj.payload = FakeEntityPayload("Ada")
    obj.payload.name = "Grace"

    assert obj.id == original_id


def test_content_hash_is_non_canonical():
    """Test contract #3: content_hash is non-canonical — two objects can
    share the same content_hash while remaining distinct identities."""
    obj_a = _make_object(content_hash="sha256:deadbeef")
    obj_b = _make_object(content_hash="sha256:deadbeef")

    assert obj_a.id != obj_b.id
    assert obj_a.content_hash == obj_b.content_hash


def test_memory_object_has_exactly_one_primary_scope():
    """Test contract #4: scope_id is a single field, not a collection, and
    is required."""
    scope = new_id()
    obj = _make_object(scope_id=scope)
    assert obj.scope_id == scope
    assert not isinstance(obj.scope_id, (list, tuple, set))


def test_memory_object_requires_a_scope():
    with pytest.raises(ValueError):
        _make_object(scope_id=None)


def test_memory_counters_reject_negative_values():
    with pytest.raises(ValueError):
        MemoryCounters(exposure=-1)
