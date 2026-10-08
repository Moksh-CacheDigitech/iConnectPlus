"""System job claims, SLO burn math, outbound webhook SSRF guard, approval matrix."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from modules.platform import celery_idempotent
from modules.platform.connectors.outbound_http import OutboundBlockedError, guard_outbound_url


def test_system_job_runs_once_per_window() -> None:
    calls: list[int] = []
    claims: set[tuple[str, str]] = set()

    def fake_claim(job: str, key: str) -> bool:
        if (job, key) in claims:
            return False
        claims.add((job, key))
        return True

    @celery_idempotent.system_job("test.job", window="day")
    def job() -> dict:
        calls.append(1)
        return {"ok": True}

    with patch.object(celery_idempotent, "_claim", side_effect=fake_claim), patch.object(
        celery_idempotent, "_finish"
    ):
        assert job() == {"ok": True}
        assert job()["status"] == "skipped"
    assert len(calls) == 1


def test_system_job_releases_claim_on_failure() -> None:
    @celery_idempotent.system_job("test.fail", window="day")
    def job() -> dict:
        raise RuntimeError("boom")

    finish = MagicMock()
    with patch.object(celery_idempotent, "_claim", return_value=True), patch.object(
        celery_idempotent, "_finish", finish
    ):
        with pytest.raises(RuntimeError):
            job()
    assert finish.call_args.kwargs["ok"] is False


def test_slo_status_reports_burn() -> None:
    from modules.platform import slo

    samples = [(100.0, True)] * 98 + [(100.0, False)] * 2
    with patch.object(slo, "path_samples", side_effect=lambda key: samples if key == "auth.login" else []):
        status = {row["path_key"]: row for row in slo.slo_status()}
    login = status["auth.login"]
    assert login["error_pct"] == 2.0
    assert login["budget_burn"] == 2.0
    assert login["status"] == "breached"
    assert status["payroll.run"]["status"] == "no_data"


@pytest.mark.parametrize(
    "url",
    ["http://127.0.0.1/hook", "http://10.0.0.5/hook", "http://169.254.169.254/latest", "file:///etc/passwd"],
)
def test_outbound_guard_blocks_non_public_targets(url: str) -> None:
    with pytest.raises(OutboundBlockedError):
        guard_outbound_url(url)


def test_outbound_guard_requires_allowlist_outside_development() -> None:
    settings = MagicMock(integration_outbound_allowed_hosts="", is_development=False)
    with patch("modules.platform.connectors.outbound_http.get_settings", return_value=settings):
        with pytest.raises(OutboundBlockedError):
            guard_outbound_url("https://hooks.example.com/x")


def test_policy_matrix_matches_module_workflow_codes() -> None:
    from modules.asset.domain.workflow_codes import WORKFLOW_CODES as AST
    from modules.finance.domain.enums import WORKFLOW_CODES as FIN
    from modules.master_data.domain.enums import WORKFLOW_CODES as MDM
    from modules.platform.policies import policy_for_entity
    from modules.procurement.domain.enums import WORKFLOW_CODES as PROC
    from modules.sales.domain.enums import WORKFLOW_CODES as SALES

    for codes in (AST, FIN, MDM, PROC, SALES):
        for entity, code in codes.items():
            policy = policy_for_entity(entity)
            assert policy is not None, f"{entity} missing from APPROVAL_POLICIES"
            assert policy.workflow_code == code, f"{entity}: {policy.workflow_code} != {code}"
