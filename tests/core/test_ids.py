"""ADR-001: canonical identity is UUIDv7."""
from __future__ import annotations

import uuid

from cognet.core import is_uuidv7, new_id


def test_new_id_is_uuidv7():
    generated = new_id()
    assert generated.version == 7
    assert is_uuidv7(generated)


def test_new_id_generates_unique_values():
    ids = {new_id() for _ in range(100)}
    assert len(ids) == 100


def test_is_uuidv7_rejects_other_versions():
    assert not is_uuidv7(uuid.uuid4())
