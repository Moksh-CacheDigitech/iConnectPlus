"""Platform ops / SLO / evolution endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.connectors import list_connector_types
from modules.platform.evolution import (
    EXTRACT_STATUS,
    K8S_READY,
    OPENSEARCH_READY,
    WAREHOUSE_READY,
)
from modules.platform.policies import APPROVAL_POLICIES, workflow_backed_keys
from modules.platform.slo import (
    CRITICAL_PATH_SLOS,
    prometheus_text,
    slo_alert_thresholds,
    slo_status,
)
from shared.schemas import APIResponse

platform_router = APIRouter(prefix="/platform", tags=["Platform"])


@platform_router.get("/slo/budgets")
def get_slo_budgets(
    _ctx: TenantContext = Depends(require_permission("platform.slo.read")),
):
    return APIResponse(
        message="OK",
        data=[
            {
                "path_key": s.path_key,
                "description": s.description,
                "p95_latency_ms": s.p95_latency_ms,
                "error_budget_pct": s.error_budget_pct,
            }
            for s in CRITICAL_PATH_SLOS
        ],
    )


@platform_router.get("/slo/alerts")
def get_slo_alerts(
    _ctx: TenantContext = Depends(require_permission("platform.slo.read")),
):
    return APIResponse(message="OK", data=slo_alert_thresholds())


@platform_router.get("/slo/status")
def get_slo_status(
    _ctx: TenantContext = Depends(require_permission("platform.slo.read")),
):
    return APIResponse(message="OK", data=slo_status())


@platform_router.get("/metrics", response_class=PlainTextResponse)
def get_prometheus_metrics(
    _ctx: TenantContext = Depends(require_permission("platform.slo.read")),
) -> str:
    return prometheus_text()


@platform_router.get("/ops/status")
def get_ops_status(
    _ctx: TenantContext = Depends(require_permission("platform.ops.read")),
):
    return APIResponse(
        message="OK",
        data={
            "outbox_tasks": ["platform.outbox_drain", "platform.outbox_purge"],
            "connector_types": list_connector_types(),
            "workflow_backed_documents": workflow_backed_keys(),
            "approval_policy_count": len(APPROVAL_POLICIES),
            "evolution": {
                "k8s_ready": K8S_READY,
                "opensearch_ready": OPENSEARCH_READY,
                "warehouse_ready": WAREHOUSE_READY,
                "extract": {
                    key: {
                        "ready": status.ready,
                        "ports_adopted": status.ports_adopted,
                        "outbox_adopted": status.outbox_adopted,
                        "orm_debt_cleared": status.orm_debt_cleared,
                        "slo_green": status.slo_green,
                        "team_ownership": status.team_ownership,
                    }
                    for key, status in EXTRACT_STATUS.items()
                },
            },
        },
    )
