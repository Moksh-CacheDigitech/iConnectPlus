"""Stub removed modules so historical Alembic revisions can import."""
from __future__ import annotations

import sys
import types


class _StubModule(types.ModuleType):
    def __getattr__(self, name: str):  # noqa: ANN001
        val = type(name, (), {})
        setattr(self, name, val)
        return val


def _ensure(name: str) -> None:
    parts = name.split(".")
    for i in range(1, len(parts) + 1):
        pkg = ".".join(parts[:i])
        if pkg not in sys.modules:
            sys.modules[pkg] = _StubModule(pkg)


for _mod in (
    "modules.sales",
    "modules.sales.models",
    "modules.sales.models.pricing",
    "modules.sales.models.credit",
    "modules.sales.models.quotation",
    "modules.sales.models.order",
    "modules.sales.models.delivery",
    "modules.sales.models.invoice",
    "modules.sales.models.return_doc",
    "modules.sales.permissions",
    "modules.grc",
    "modules.grc.models",
    "modules.grc.models.policy",
    "modules.grc.models.policy_version",
    "modules.grc.models.policy_acknowledgement",
    "modules.grc.models.control",
    "modules.grc.models.control_test",
    "modules.grc.models.risk_category",
    "modules.grc.models.risk_register",
    "modules.grc.models.risk_assessment",
    "modules.grc.models.risk_treatment",
    "modules.grc.models.compliance_framework",
    "modules.grc.models.compliance_requirement",
    "modules.grc.models.compliance_assessment",
    "modules.grc.models.audit_plan",
    "modules.grc.models.audit",
    "modules.grc.models.audit_finding",
    "modules.grc.models.corrective_action",
    "modules.grc.models.exception",
    "modules.grc.models.incident",
    "modules.grc.models.notification",
    "modules.grc.models.report",
    "modules.grc.permissions",
    "modules.integration",
    "modules.integration.models",
    "modules.integration.models.external_system",
    "modules.integration.models.connector",
    "modules.integration.models.api_credential",
    "modules.integration.models.oauth_client",
    "modules.integration.permissions",
    "modules.portal",
    "modules.portal.models",
    "modules.portal.permissions",
):
    _ensure(_mod)
