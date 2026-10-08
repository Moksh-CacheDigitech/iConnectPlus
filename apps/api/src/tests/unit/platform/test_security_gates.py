"""CI gates: tenant scoping, RBAC catalog alignment (API + web), OpenAPI contract."""

from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path

import pytest

MODULES_ROOT = Path(__file__).resolve().parents[3] / "modules"
WEB_SRC = Path(__file__).resolve().parents[5] / "web" / "src"
_WEB_PERMISSION = re.compile(r"""["']((?:[a-z_]+\.)+[a-z_]+:[a-z_]+)["']""")

_SCOPE_MARKERS = ("tenant_id", "apply_", "_scoped", "_base(", "company_id", "ctx.tenant")

# Reviewed exceptions: pre-auth/global lookups and correlated EXISTS helpers whose
# outer query is tenant-scoped. Adding to this list requires a security review.
_UNSCOPED_ALLOWED = frozenset(
    {
        "asset/repository/asset_repository.py::_exists_active_assignment",
        "asset/repository/asset_repository.py::_exists_active_assignment_for_department",
        "asset/repository/asset_repository.py::_exists_current_location",
        "asset/repository/asset_repository.py::_exists_current_site_location",
        "asset/repository/asset_repository.py::_exists_active_assignment_employee_search",
        # SCM callback authenticates with a service API key, not a tenant user.
        "asset/repository/dc_challan_repository.py::get_by_id_unscoped",
        "finance/repository/gl_repository.py::exists_for_journal",
        "foundation/repository/role_repository.py::list_all",
        "foundation/repository/role_repository.py::get_by_code",
        "foundation/repository/role_repository.py::list_modules",
        "foundation/repository/session_repository.py::get_refresh_token",
        "foundation/repository/session_repository.py::get_refresh_token_any",
        "foundation/repository/session_repository.py::revoke_all_refresh_for_session",
        "foundation/repository/tenant_repository.py::get_by_code",
        "foundation/repository/tenant_repository.py::list_all",
        "foundation/repository/user_repository.py::get_active_by_email",
        "foundation/repository/workflow_repository.py::get_steps",
    }
)


def _unscoped_repository_queries() -> list[str]:
    found: list[str] = []
    for path in sorted(MODULES_ROOT.glob("*/repository/*.py")):
        src = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.FunctionDef):
                continue
            body = ast.get_source_segment(src, node) or ""
            if "select(" not in body and ".query(" not in body:
                continue
            if any(marker in body for marker in _SCOPE_MARKERS):
                continue
            key = f"{path.relative_to(MODULES_ROOT).as_posix()}::{node.name}"
            if key not in _UNSCOPED_ALLOWED:
                found.append(key)
    return found


def test_repository_queries_are_tenant_or_company_scoped() -> None:
    leaks = _unscoped_repository_queries()
    assert not leaks, "Repository queries without tenant/company scope:\n" + "\n".join(leaks)


def _permission_codes_used_in_routes() -> dict[str, str]:
    used: dict[str, str] = {}
    for path in MODULES_ROOT.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name not in ("require_permission", "require_any_permission"):
                continue
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    used.setdefault(arg.value, path.relative_to(MODULES_ROOT).as_posix())
    return used


def test_every_route_permission_exists_in_catalog() -> None:
    from modules.platform.permission_catalog import all_permission_codes

    catalog = all_permission_codes()
    missing = {code: where for code, where in _permission_codes_used_in_routes().items() if code not in catalog}
    assert not missing, "Route permissions missing from catalog:\n" + "\n".join(
        f"{code}  ({where})" for code, where in sorted(missing.items())
    )


def test_web_permission_codes_exist_in_catalog() -> None:
    if not WEB_SRC.is_dir():
        pytest.skip("web app not present in this checkout")
    from modules.platform.permission_catalog import all_permission_codes

    catalog = all_permission_codes()
    missing: dict[str, str] = {}
    for path in [*WEB_SRC.rglob("*.ts"), *WEB_SRC.rglob("*.tsx")]:
        for code in _WEB_PERMISSION.findall(path.read_text(encoding="utf-8", errors="ignore")):
            if code not in catalog:
                missing.setdefault(code, path.relative_to(WEB_SRC).as_posix())
    assert not missing, "Web permission codes missing from API catalog:\n" + "\n".join(
        f"{code}  ({where})" for code, where in sorted(missing.items())
    )


def test_openapi_contract_generates_with_unique_operations() -> None:
    from main import create_app

    schema = create_app().openapi()
    operations = [
        (path, method, op)
        for path, methods in schema["paths"].items()
        for method, op in methods.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    assert operations, "OpenAPI schema has no operations"
    duplicates = [oid for oid, n in Counter(op.get("operationId") for _, _, op in operations).items() if n > 1]
    assert not duplicates, f"Duplicate operationIds: {duplicates[:20]}"
    undocumented = [f"{m.upper()} {p}" for p, m, op in operations if not op.get("responses")]
    assert not undocumented, f"Operations without responses: {undocumented[:20]}"
