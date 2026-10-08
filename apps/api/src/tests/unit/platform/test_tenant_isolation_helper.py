"""Tenant isolation helper — repositories must filter by tenant_id."""

from __future__ import annotations

import ast
from pathlib import Path

MODULES_ROOT = Path(__file__).resolve().parents[3] / "modules"


def test_tenant_scoped_repositories_exist_for_core_modules() -> None:
    """Smoke: core modules keep a repository base with tenant awareness."""
    required = ("foundation", "finance", "inventory", "procurement", "sales")
    for name in required:
        base = MODULES_ROOT / name / "repository" / "base.py"
        assert base.exists(), f"Missing {name}/repository/base.py"
        text = base.read_text(encoding="utf-8")
        assert "tenant" in text.lower() or "OrgScoped" in text or "TenantScoped" in text


def test_platform_outbox_model_is_tenant_mixin() -> None:
    from modules.platform.models.outbox import FndOutboxMessage

    assert hasattr(FndOutboxMessage, "tenant_id")
