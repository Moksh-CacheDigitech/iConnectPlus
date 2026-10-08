"""Workflow port — thin start / approve / reject / cancel API."""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from modules.platform.dto import WorkflowActionRequest, WorkflowStartRequest


class IWorkflow(Protocol):
    def start(self, request: WorkflowStartRequest) -> Any:
        ...

    def approve(self, request: WorkflowActionRequest) -> Any:
        ...

    def reject(self, request: WorkflowActionRequest) -> Any:
        ...

    def cancel(self, request: WorkflowActionRequest) -> Any:
        ...

    def get_definition_id(self, tenant_id: UUID, workflow_code: str) -> UUID | None:
        ...
