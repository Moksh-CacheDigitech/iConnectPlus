"""Unit tests for RBAC engine."""

from unittest.mock import MagicMock
from uuid import uuid4

from security.rbac import RBACEngine


def test_has_permission_from_query_result() -> None:
    db = MagicMock()
    user_id = uuid4()
    tenant_id = uuid4()
    chain = db.query.return_value.join.return_value.join.return_value
    chain.filter.return_value.distinct.return_value.all.return_value = [
        ("foundation.user:read",),
    ]
    engine = RBACEngine(db)
    assert engine.has_permission(user_id, tenant_id, "foundation.user:read")
    assert not engine.has_permission(user_id, tenant_id, "foundation.user:delete")
