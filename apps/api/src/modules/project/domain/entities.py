"""Project domain entity markers."""

from enum import Enum


class PrjAggregate(str, Enum):
    PROJECT = "prj_project"
    PROJECTPHASE = "prj_project_phase"
    PROJECTMILESTONE = "prj_project_milestone"
    PROJECTTASK = "prj_project_task"
    TASKDEPENDENCY = "prj_task_dependency"
    TASKASSIGNMENT = "prj_task_assignment"
    TIMESHEET = "prj_timesheet"
    TIMESHEETENTRY = "prj_timesheet_entry"
    RESOURCEPLAN = "prj_resource_plan"
    RESOURCEALLOCATION = "prj_resource_allocation"
    PROJECTBUDGET = "prj_project_budget"
    PROJECTCOST = "prj_project_cost"
    PROJECTISSUE = "prj_project_issue"
    PROJECTRISK = "prj_project_risk"
    CHANGEREQUEST = "prj_change_request"
    PROJECTDOCUMENT = "prj_project_document"
    PROJECTCOMMENT = "prj_project_comment"
    PROJECTSTATUSHISTORY = "prj_project_status_history"
    PROJECTNOTIFICATION = "prj_project_notification"
    PROJECTREPORT = "prj_project_report"
