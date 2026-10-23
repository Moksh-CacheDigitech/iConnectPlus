"""HRMS-backed login eligibility rules."""

from types import SimpleNamespace

import pytest

from modules.foundation.adapters.smtp_email_adapter import SmtpEmailAdapter
from modules.foundation.schemas import LoginRequest
from modules.foundation.service.hrms_user_directory import (
    is_onboarded_employee,
    is_valid_employee_code,
)


@pytest.mark.parametrize("code", ["CT5345", "CDPL2014", "ct5107"])
def test_real_employee_codes_are_valid(code: str) -> None:
    assert is_valid_employee_code(code)


@pytest.mark.parametrize(
    "code",
    ["", None, "EMP-000001", "CRM-15AD40C2848F", "SVC-ENG1", "EMP-ESS-001", "CT12"],
)
def test_placeholder_codes_are_rejected(code: str | None) -> None:
    assert not is_valid_employee_code(code)


def _employee(**overrides):
    base = {
        "is_deleted": False,
        "status": "active",
        "employee_code": "CT5345",
        "email": "moksh@cachedigitech.com",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_onboarded_employee_requires_active_lifecycle() -> None:
    assert is_onboarded_employee(_employee())
    assert is_onboarded_employee(_employee(status="notice_period"))
    assert not is_onboarded_employee(_employee(status="onboarding"))
    assert not is_onboarded_employee(_employee(status="resigned"))


def test_onboarded_employee_requires_email_and_code() -> None:
    assert not is_onboarded_employee(_employee(email=""))
    assert not is_onboarded_employee(_employee(employee_code="EMP-000001"))
    assert not is_onboarded_employee(_employee(is_deleted=True))


def test_smtp_adapter_reports_not_configured() -> None:
    adapter = SmtpEmailAdapter(host="", from_email="")
    result = adapter.send_mail(to_address="a@b.com", subject="x", body_html="<p>x</p>")
    assert not result.ok
    assert result.provider_response == "smtp_not_configured"


def test_login_accepts_user_id_or_email_key() -> None:
    assert LoginRequest.model_validate({"user_id": "CT5345", "password": "Cache@123"}).email == "CT5345"
    assert (
        LoginRequest.model_validate({"email": "moksh@cachedigitech.com", "password": "Cache@123"}).email
        == "moksh@cachedigitech.com"
    )
