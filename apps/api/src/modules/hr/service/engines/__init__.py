"""HR business engines."""

from modules.hr.service.engines.appraisal_engine import AppraisalEngine
from modules.hr.service.engines.attendance_engine import AttendanceEngine
from modules.hr.service.engines.department_assignment_engine import DepartmentAssignmentEngine
from modules.hr.service.engines.designation_assignment_engine import DesignationAssignmentEngine
from modules.hr.service.engines.designation_engine import DesignationEngine
from modules.hr.service.engines.employee_document_engine import EmployeeDocumentEngine
from modules.hr.service.engines.employee_profile_engine import EmployeeProfileEngine
from modules.hr.service.engines.employment_engine import EmploymentEngine
from modules.hr.service.engines.goal_engine import GoalEngine
from modules.hr.service.engines.holiday_calendar_engine import HolidayCalendarEngine
from modules.hr.service.engines.leave_balance_engine import LeaveBalanceEngine
from modules.hr.service.engines.leave_request_engine import LeaveRequestEngine
from modules.hr.service.engines.leave_type_engine import LeaveTypeEngine
from modules.hr.service.engines.performance_review_engine import PerformanceReviewEngine
from modules.hr.service.engines.separation_engine import SeparationEngine
from modules.hr.service.engines.shift_assignment_engine import ShiftAssignmentEngine
from modules.hr.service.engines.shift_engine import ShiftEngine
from modules.hr.service.engines.training_attendance_engine import TrainingAttendanceEngine
from modules.hr.service.engines.training_engine import TrainingEngine

__all__ = [
    "DesignationEngine",
    "EmployeeProfileEngine",
    "EmploymentEngine",
    "DepartmentAssignmentEngine",
    "DesignationAssignmentEngine",
    "ShiftEngine",
    "ShiftAssignmentEngine",
    "HolidayCalendarEngine",
    "LeaveTypeEngine",
    "LeaveBalanceEngine",
    "LeaveRequestEngine",
    "AttendanceEngine",
    "EmployeeDocumentEngine",
    "PerformanceReviewEngine",
    "GoalEngine",
    "AppraisalEngine",
    "TrainingEngine",
    "TrainingAttendanceEngine",
    "SeparationEngine",
]
