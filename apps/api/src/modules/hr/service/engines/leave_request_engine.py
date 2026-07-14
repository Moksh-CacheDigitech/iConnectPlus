"""LeaveRequest lifecycle engine."""

from modules.hr.domain.enums import LeaveRequestStatus
from modules.hr.domain.exceptions import InvalidLeaveRequestState


class LeaveRequestEngine:
    def submit(self, row) -> None:
        if row.status != LeaveRequestStatus.DRAFT.value:
            raise InvalidLeaveRequestState("Only draft leave requests can be submitted")
        row.status = LeaveRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != LeaveRequestStatus.SUBMITTED.value:
            raise InvalidLeaveRequestState("Only submitted leave can be approved")
        row.status = LeaveRequestStatus.APPROVED.value

    def reject(self, row) -> None:
        if row.status != LeaveRequestStatus.SUBMITTED.value:
            raise InvalidLeaveRequestState("Only submitted leave can be rejected")
        row.status = LeaveRequestStatus.REJECTED.value

    def cancel(self, row) -> None:
        if row.status in {LeaveRequestStatus.APPROVED.value, LeaveRequestStatus.CANCELLED.value}:
            raise InvalidLeaveRequestState("Cannot cancel approved/cancelled leave")
        row.status = LeaveRequestStatus.CANCELLED.value
