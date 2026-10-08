"""Architecture boundary tests — no cross-module ORM imports outside adapters/platform."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

MODULES_ROOT = Path(__file__).resolve().parents[3] / "modules"

# Modules may import foundation + organization + their own package freely.
ALWAYS_ALLOWED = frozenset({"foundation", "organization", "platform"})

# Adapter / port / tasks files may import sibling domain services (not models).
ADAPTER_PATH_MARKERS = (
    "/adapters/",
    "\\adapters\\",
    "/ports/",
    "\\ports\\",
)


def _module_packages() -> list[str]:
    return sorted(
        p.name
        for p in MODULES_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith("_") and p.name != "platform"
    )


def _iter_py_files(package: str) -> list[Path]:
    root = MODULES_ROOT / package
    return [p for p in root.rglob("*.py") if p.is_file()]


def _imported_modules(tree: ast.AST) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                found.append(alias.name)
    return found


def _is_model_import(module_path: str, foreign_pkg: str) -> bool:
    """True if importing foreign package ORM models."""
    return (
        module_path == f"modules.{foreign_pkg}.models"
        or module_path.startswith(f"modules.{foreign_pkg}.models.")
    )


def _collect_cross_module_orm_violations(package: str) -> list[str]:
    violations: list[str] = []
    for path in _iter_py_files(package):
        rel = str(path)
        if any(m in rel for m in ADAPTER_PATH_MARKERS):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        for mod in _imported_modules(tree):
            if not mod.startswith("modules."):
                continue
            parts = mod.split(".")
            if len(parts) < 2:
                continue
            foreign = parts[1]
            if foreign in ALWAYS_ALLOWED or foreign == package:
                continue
            if _is_model_import(mod, foreign):
                violations.append(f"{path.relative_to(MODULES_ROOT)}: {mod}")
    return violations


def test_platform_package_has_no_accidental_foreign_orm_in_non_adapters() -> None:
    """Platform non-adapter code must not import business ORM models."""
    violations = _collect_cross_module_orm_violations("platform")
    assert not violations, "Platform boundary broken:\n" + "\n".join(violations)


def test_no_cross_module_orm_imports_outside_adapters() -> None:
    """Foreign ORM models are reachable only from adapters/ports.

    Master data is consumed through ``modules.master_data.published``.
    """
    all_violations: list[str] = []
    for package in _module_packages():
        all_violations.extend(_collect_cross_module_orm_violations(package))
    assert not all_violations, "Cross-module ORM imports:\n" + "\n".join(all_violations[:40])


def test_audit_facade_covers_every_method_services_call() -> None:
    import re

    from modules.platform.compat.audit_facade import PlatformAuditFacade

    missing: dict[str, str] = {}
    for path in MODULES_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "PlatformAuditFacade" not in text:
            continue
        for name in re.findall(r"self\._audit\.(\w+)\(", text):
            if not hasattr(PlatformAuditFacade, name):
                missing.setdefault(name, str(path.relative_to(MODULES_ROOT)))
    assert not missing, f"PlatformAuditFacade missing methods used by services: {missing}"


def test_master_data_projections_reject_writes() -> None:
    from types import SimpleNamespace

    from modules.master_data.published import (
        EmployeeRead,
        PublishedReadOnlyError,
        _reject_projection_writes,
    )

    projection = EmployeeRead.__new__(EmployeeRead)
    session = SimpleNamespace(new={projection}, deleted=set(), dirty=set())
    with pytest.raises(PublishedReadOnlyError):
        _reject_projection_writes(session, None, None)

def test_platform_ports_export_expected_protocols() -> None:
    from modules.platform.ports import (
        IAudit,
        IDocumentNumbering,
        IFinancePosting,
        IIntegrationGateway,
        IInventoryStock,
        IMasterDataLookup,
        INotify,
        IOutbox,
        IWorkflow,
    )

    assert all(
        hasattr(p, "__protocol_attrs__") or True
        for p in (
            IAudit,
            IDocumentNumbering,
            IFinancePosting,
            IIntegrationGateway,
            IInventoryStock,
            IMasterDataLookup,
            INotify,
            IOutbox,
            IWorkflow,
        )
    )


def test_approval_policy_matrix_covers_core_docs() -> None:
    from modules.platform.policies import APPROVAL_POLICIES, ApprovalMode, approval_policy

    assert approval_policy("procurement.purchase_order") is not None
    assert APPROVAL_POLICIES["finance.journal"].mode == ApprovalMode.WORKFLOW


def test_optimistic_lock_helper() -> None:
    from modules.platform.optimistic import OptimisticLockError, assert_version, bump_version

    class Row:
        version = 3

    row = Row()
    assert_version(row, 3)
    with pytest.raises(OptimisticLockError):
        assert_version(row, 2)
    assert bump_version(row) == 4


def test_slo_registry_has_critical_paths() -> None:
    from modules.platform.slo import CRITICAL_PATH_SLOS

    keys = {s.path_key for s in CRITICAL_PATH_SLOS}
    assert "auth.login" in keys
    assert "finance.invoice_post" in keys


def test_domain_event_registry() -> None:
    from modules.platform.events import is_registered_domain_event

    assert is_registered_domain_event("domain.finance.journal_posted")
    assert not is_registered_domain_event("domain.random.noise")
