"""Unit tests for project engines."""

from types import SimpleNamespace

from modules.project.service.engines import (
    ChangeRequestEngine,
    ProjectBudgetEngine,
    ProjectCostEngine,
    ProjectEngine,
    ProjectTaskEngine,
    TimesheetEngine,
)


def test_project_lifecycle():
    engine = ProjectEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"
    engine.start(row)
    assert row.status == "in_progress"
    engine.complete(row)
    assert row.status == "completed"
    engine.close(row)
    assert row.status == "closed"


def test_task_submit_approve():
    engine = ProjectTaskEngine()
    row = SimpleNamespace(status="open")
    engine.submit(row)
    engine.approve(row)
    assert row.status == "approved"


def test_timesheet_submit_approve():
    engine = TimesheetEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    assert row.status == "approved"


def test_budget_and_change_and_cost():
    budget = ProjectBudgetEngine()
    brow = SimpleNamespace(status="draft")
    budget.submit(brow)
    budget.approve(brow)
    assert brow.status == "approved"

    change = ChangeRequestEngine()
    crow = SimpleNamespace(status="draft")
    change.submit(crow)
    change.approve(crow)
    assert crow.status == "approved"

    cost = ProjectCostEngine()
    cost_row = SimpleNamespace(status="draft")
    cost.post(cost_row)
    assert cost_row.status == "posted"
