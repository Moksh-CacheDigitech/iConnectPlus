"""Unit tests for recruitment engines."""

from types import SimpleNamespace

from modules.recruitment.service.engines import (
    JobPostingEngine,
    JobRequisitionEngine,
    OfferEngine,
    OnboardingEngine,
)


def test_job_requisition_lifecycle():
    engine = JobRequisitionEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"
    engine.open(row)
    assert row.status == "open"


def test_job_posting_publish():
    engine = JobPostingEngine()
    row = SimpleNamespace(status="draft")
    engine.publish(row)
    assert row.status == "published"


def test_offer_submit_approve_send():
    engine = OfferEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.send(row)
    assert row.status == "sent"


def test_onboarding_submit_approve():
    engine = OnboardingEngine()
    row = SimpleNamespace(status="draft", employee_id=None)
    engine.submit(row)
    engine.approve(row)
    assert row.status == "in_progress"
