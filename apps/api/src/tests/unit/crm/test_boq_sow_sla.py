"""BOQ / SOW SLA: 1-hour response and 6-hour attach deadlines, escalation levels."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from modules.crm.service import boq_sow_sla_service as sla


def test_deadlines_only_for_boq_sow_tasks():
    start = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
    deadlines = sla.sla_deadlines("provide_boq_attachment", start)
    assert deadlines == {
        "response_due_at": start + timedelta(hours=1),
        "due_at": start + timedelta(hours=6),
    }
    assert sla.sla_deadlines("approve", start) == {}
    assert sla.sla_deadlines(None, start) == {}


def _task(**overrides):
    created = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
    base = dict(
        id=uuid4(),
        tenant_id=uuid4(),
        entity_type="lead",
        entity_id=uuid4(),
        action="provide_sow_attachment",
        title="Attach SOW - Acme",
        assigned_role=None,
        assigned_user_id=uuid4(),
        requested_by=uuid4(),
        responded_at=None,
        response_reason=None,
        response_due_at=created + timedelta(hours=1),
        due_at=created + timedelta(hours=6),
        escalation_level=0,
        escalated_at=None,
        priority="normal",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _run(tasks, now, monkeypatch):
    db = MagicMock()
    db.scalars.return_value.all.return_value = tasks
    sent = []
    monkeypatch.setattr(sla, "notify_crm_user", lambda *a, **kw: sent.append(kw))
    monkeypatch.setattr(sla, "resolve_user_manager_user_id", lambda *a, **kw: uuid4())
    counts = sla.BoqSowSlaService(db).escalate_breaches(now=now)
    return counts, sent


def test_missed_response_escalates_once(monkeypatch):
    task = _task()
    now = datetime(2026, 9, 28, 11, 30, tzinfo=timezone.utc)
    counts, sent = _run([task], now, monkeypatch)
    assert counts == {"response_escalations": 1, "attach_escalations": 0}
    assert task.escalation_level == 1
    assert task.priority == "high"
    # manager + requester + assignee
    assert len(sent) == 3


def test_missed_attach_escalates_to_level_two(monkeypatch):
    task = _task(escalation_level=1, responded_at=datetime(2026, 9, 28, 10, 20, tzinfo=timezone.utc))
    now = datetime(2026, 9, 28, 16, 30, tzinfo=timezone.utc)
    counts, _sent = _run([task], now, monkeypatch)
    assert counts == {"response_escalations": 0, "attach_escalations": 1}
    assert task.escalation_level == 2


def test_within_sla_does_nothing(monkeypatch):
    task = _task()
    now = datetime(2026, 9, 28, 10, 30, tzinfo=timezone.utc)
    counts, sent = _run([task], now, monkeypatch)
    assert counts == {"response_escalations": 0, "attach_escalations": 0}
    assert sent == []


def test_admin_copies_are_not_escalated(monkeypatch):
    task = _task(assigned_role="admin_copy")
    now = datetime(2026, 9, 28, 17, 0, tzinfo=timezone.utc)
    counts, sent = _run([task], now, monkeypatch)
    assert counts == {"response_escalations": 0, "attach_escalations": 0}
    assert sent == []
