# FRD-11 PROJECT MANAGEMENT DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-09 HR Domain](./FRD-09-HR-Domain.md)
- Downstream dependencies: [FRD-04 Finance & Accounting Domain](./FRD-04-Finance-Accounting-Domain.md), [FRD-06 Sales Domain](./FRD-06-Sales-Domain.md)

## 1. PURPOSE

Project Management Domain projects ko initiation se closure tak manage karega.

### Business Objectives

- Project Planning
- Task Tracking
- Resource Management
- Budget Control
- Time Tracking
- Cost Tracking
- Project Profitability

## 2. MODULES COVERED

- Project Management
- Task Management
- Milestone Management
- Resource Allocation
- Timesheets
- Project Budgeting
- Project Costing
- Project Billing
- Project Profitability
- Project Reporting

## 3. PROJECT LIFECYCLE

```
Project Request
↓
Approval
↓
Planning
↓
Execution
↓
Monitoring
↓
Completion
↓
Closure
```

## 4. PROJECT MANAGEMENT

### Purpose

Manage complete project information.

### Project Fields

| Field | Mandatory |
|---|---|
| Project Code | Yes |
| Project Name | Yes |
| Customer | No |
| Project Type | Yes |
| Project Manager | Yes |
| Start Date | Yes |
| End Date | Yes |
| Budget | Yes |
| Status | Yes |

### Project Code Format

```
PRJ-2026-000001
```

### Project Types

- Internal
- Customer Project
- R&D Project
- Implementation Project
- Support Project

### Project Status

- Draft
- Approved
- In Progress
- On Hold
- Completed
- Cancelled
- Closed

## 5. WORK BREAKDOWN STRUCTURE (WBS)

### Purpose

Break project into manageable deliverables.

### Hierarchy

```
Project
↓
Phase
↓
Milestone
↓
Task
↓
Sub Task
```

### Example

```
ERP Implementation

Phase 1
 ├─ Requirement Gathering
 ├─ BRD

Phase 2
 ├─ Development
 ├─ Testing
```

## 6. TASK MANAGEMENT

### Purpose

Track project execution.

### Task Fields

| Field |
|---|
| Task Number |
| Task Name |
| Assignee |
| Priority |
| Start Date |
| Due Date |
| Status |

### Priority

- Low
- Medium
- High
- Critical

### Task Status

- Open
- In Progress
- Blocked
- Completed
- Cancelled

## 7. MILESTONE MANAGEMENT

### Purpose

Track major project checkpoints.

### Milestone Fields

| Field |
|---|
| Milestone Name |
| Due Date |
| Owner |
| Status |

### Status

- Planned
- Achieved
- Delayed

## 8. RESOURCE ALLOCATION

### Purpose

Assign resources to projects.

### Resource Types

- Employee
- Contractor
- Consultant
- Vendor Resource

### Allocation Fields

| Field |
|---|
| Resource |
| Project |
| Allocation % |
| Start Date |
| End Date |

### Validation

Allocation Cannot Exceed 100%

## 9. TIMESHEET MANAGEMENT

### Purpose

Track employee effort.

### Timesheet Fields

| Field |
|---|
| Employee |
| Project |
| Task |
| Date |
| Hours Worked |

### Validation

Daily Hours ≤ 24

### Status

- Draft
- Submitted
- Approved
- Rejected

## 10. PROJECT BUDGETING

### Purpose

Control project spending.

### Budget Types

- Labor
- Materials
- Travel
- Software
- Hardware
- Other

### Budget Fields

| Field |
|---|
| Budget Amount |
| Cost Center |
| Fiscal Year |

## 11. PROJECT COSTING

### Purpose

Track actual project costs.

### Cost Sources

- Payroll
- Procurement
- Expenses
- Assets
- Vendor Bills

### Formula

```
Total Project Cost
=
Labor Cost
+
Material Cost
+
Other Costs
```

## 12. PROJECT BILLING

### Purpose

Customer invoicing.

### Billing Types

- Fixed Price
- Time & Material
- Milestone Based
- Retainer Based

### Invoice Triggers

- Milestone Completion
- Monthly Billing
- Manual Billing

## 13. PROJECT PROFITABILITY

### Purpose

Evaluate project performance.

### Formula

```
Project Profit
=
Project Revenue
-
Project Cost
```

### KPIs

- Budget Variance
- Cost Variance
- Margin %
- Revenue
- Profit

## 14. PROJECT RISKS

### Purpose

Manage project risks.

### Risk Fields

| Field |
|---|
| Risk Name |
| Impact |
| Probability |
| Owner |
| Mitigation Plan |

### Risk Levels

- Low
- Medium
- High
- Critical

## 15. SCREEN INVENTORY

- Project Dashboard
- Project List
- Project Details
- WBS View
- Task Board
- Milestone Dashboard
- Resource Allocation Dashboard
- Timesheet Dashboard
- Budget Dashboard
- Cost Dashboard
- Profitability Dashboard
- Risk Register

## 16. APPROVAL WORKFLOWS

### Project Approval

```
Project Manager
↓
Department Head
↓
Finance
↓
Approved
```

### Timesheet Approval

```
Employee
↓
Manager
↓
Approved
```

### Budget Approval

```
Project Manager
↓
Finance
↓
Approved
```

## 17. NOTIFICATIONS

Events

- Project Created
- Task Assigned
- Task Due
- Milestone Achieved
- Timesheet Submitted
- Budget Exceeded

Channels

- Email
- In-App
- WhatsApp

## 18. AUDIT REQUIREMENTS

Track:

- Project Changes
- Task Updates
- Budget Changes
- Timesheet Approvals
- Billing Changes

## 19. DATABASE TABLES

- projects
- project_phases
- project_milestones
- project_tasks
- task_dependencies
- resource_allocations
- timesheets
- timesheet_entries
- project_budgets
- project_costs
- project_billings
- project_risks

## 20. KEY RELATIONSHIPS

```
Project
1:N Phases

Project
1:N Milestones

Project
1:N Tasks

Project
1:N Resources

Project
1:N Timesheets

Project
1:N Costs

Project
1:N Billings
```

## 21. API SPECIFICATIONS

### Project APIs

```
GET /api/v1/projects

POST /api/v1/projects

PUT /api/v1/projects/{id}
```

### Task APIs

```
GET /api/v1/tasks

POST /api/v1/tasks

PUT /api/v1/tasks/{id}
```

### Timesheet APIs

```
GET /api/v1/timesheets

POST /api/v1/timesheets

PUT /api/v1/timesheets/{id}
```

## 22. REPORTS

### Project Reports

- Project Status Report
- Resource Utilization Report
- Timesheet Report
- Budget vs Actual Report
- Project Cost Report
- Project Revenue Report
- Project Profitability Report
- Risk Report

## 23. ACCEPTANCE CRITERIA

✅ Project lifecycle works

✅ Task management works

✅ Resource allocation validated

✅ Timesheets submitted and approved

✅ Project costing calculated

✅ Project billing generated

✅ Profitability calculated

✅ Reports generated

## 24. UAT SCENARIOS

### UAT-001

Create Project

Expected:

Project Created Successfully

### UAT-002

Assign Resource

Expected:

Allocation Created

### UAT-003

Submit Timesheet

Expected:

Timesheet Sent For Approval

### UAT-004

Generate Project Invoice

Expected:

Invoice Created Successfully

### UAT-005

View Profitability Report

Expected:

Profit Calculated Correctly

## ARCHITECT REVIEW

FRD-11 Project Management Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
HR
↓
Projects
↓
Finance
↓
Sales
```

### Critical Observation

Project Domain now supports:

- End-to-End Project Lifecycle
- WBS & Task Management
- Resource Planning
- Timesheets
- Budgeting & Costing
- Customer Billing
- Project Profitability
