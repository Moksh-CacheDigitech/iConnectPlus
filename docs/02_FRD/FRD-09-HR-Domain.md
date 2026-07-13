# FRD-09 HUMAN RESOURCE (HR) DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-03 Master Data Domain](./FRD-03-Master-Data-Domain.md)
- Downstream dependency: [FRD-10 Payroll Domain](./FRD-10-Payroll-Domain.md)

## 1. PURPOSE

HR Domain employee lifecycle ko manage karega.

From:

```
Recruitment
↓
Hiring
↓
Onboarding
↓
Employment
↓
Performance
↓
Training
↓
Separation
```

### Business Objectives

- Employee Lifecycle Management
- Workforce Visibility
- Attendance Management
- Leave Management
- Shift Management
- Performance Tracking
- Training Management
- Employee Self Service

## 2. MODULES COVERED

- Recruitment
- Candidate Management
- Onboarding
- Employee Management
- Attendance Management
- Leave Management
- Shift Management
- Performance Management
- Training Management
- Employee Self Service (ESS)
- Separation Management

## 3. EMPLOYEE LIFECYCLE

```
Job Requisition
↓
Candidate
↓
Interview
↓
Offer
↓
Joining
↓
Employee
↓
Performance Reviews
↓
Exit Process
```

## 4. RECRUITMENT MANAGEMENT

### Purpose

Manage hiring process.

### Job Requisition Fields

| Field | Mandatory |
|---|---|
| Requisition Number | Yes |
| Department | Yes |
| Position | Yes |
| Openings | Yes |
| Hiring Manager | Yes |
| Status | Yes |

### Requisition Number Format

```
REQ-2026-000001
```

### Status

- Draft
- Submitted
- Approved
- Open
- Closed

## 5. CANDIDATE MANAGEMENT

### Candidate Fields

| Field |
|---|
| Candidate ID |
| Name |
| Email |
| Mobile |
| Position Applied |
| Resume |
| Experience |
| Status |

### Candidate Status

- Applied
- Screening
- Interview
- Selected
- Rejected
- On Hold

### Candidate ID

```
CAN-000001
```

## 6. INTERVIEW MANAGEMENT

### Interview Types

- HR Round
- Technical Round
- Manager Round
- Final Round

### Fields

| Field |
|---|
| Candidate |
| Interviewer |
| Date |
| Time |
| Feedback |
| Result |

### Results

- Pass
- Fail
- Hold

## 7. OFFER MANAGEMENT

### Purpose

Manage offer process.

### Offer Fields

| Field |
|---|
| Offer Number |
| Candidate |
| Position |
| Salary Offered |
| Joining Date |
| Status |

### Status

- Draft
- Sent
- Accepted
- Rejected
- Expired

## 8. ONBOARDING MANAGEMENT

### Purpose

Convert candidate into employee.

### Activities

- Document Verification
- Asset Allocation
- Account Creation
- Training Assignment
- Manager Assignment

### Onboarding Checklist

Mandatory before activation.

## 9. EMPLOYEE MANAGEMENT

### Purpose

Manage employee records.

### Employee Fields

| Field |
|---|
| Employee Code |
| Name |
| Department |
| Designation |
| Reporting Manager |
| Employment Type |
| Date Of Joining |
| Status |

### Employment Types

- Permanent
- Contract
- Intern
- Consultant

### Employee Status

- Active
- Probation
- On Leave
- Resigned
- Terminated

## 10. ATTENDANCE MANAGEMENT

### Purpose

Track working hours.

### Attendance Sources

- Manual
- Biometric
- Mobile App
- Web Portal
- Third Party Device

### Attendance Status

- Present
- Absent
- Half Day
- Work From Home
- Holiday

### Fields

| Field |
|---|
| Employee |
| Date |
| Check In |
| Check Out |
| Total Hours |

## 11. LEAVE MANAGEMENT

### Leave Types

- Casual Leave
- Sick Leave
- Earned Leave
- Maternity Leave
- Paternity Leave
- Unpaid Leave

### Leave Fields

| Field |
|---|
| Employee |
| Leave Type |
| Start Date |
| End Date |
| Reason |
| Status |

### Leave Status

- Draft
- Submitted
- Approved
- Rejected
- Cancelled

## 12. SHIFT MANAGEMENT

### Purpose

Manage work schedules.

### Shift Types

- General
- Morning
- Evening
- Night
- Rotational

### Fields

| Field |
|---|
| Shift Name |
| Start Time |
| End Time |
| Grace Period |

## 13. PERFORMANCE MANAGEMENT

### Purpose

Evaluate employee performance.

### Review Cycles

- Monthly
- Quarterly
- Half-Yearly
- Yearly

### Evaluation Areas

- Goals
- KPIs
- Competencies
- Behavior
- Attendance

### Ratings

1, 2, 3, 4, 5

## 14. TRAINING MANAGEMENT

### Purpose

Track employee learning.

### Training Types

- Technical
- Compliance
- Soft Skills
- Leadership

### Fields

| Field |
|---|
| Training Name |
| Trainer |
| Date |
| Participants |
| Completion Status |

## 15. EMPLOYEE SELF SERVICE (ESS)

### Purpose

Allow employees to manage own records.

### Features

- Profile View
- Leave Requests
- Attendance View
- Payslip View
- Training View
- Performance View
- Asset Requests

## 16. SEPARATION MANAGEMENT

### Purpose

Manage employee exit.

### Types

- Resignation
- Termination
- Retirement

### Exit Checklist

- Asset Return
- Knowledge Transfer
- Clearance
- Final Settlement

## 17. SCREEN INVENTORY

- Recruitment Dashboard
- Candidate Dashboard
- Interview Dashboard
- Employee Dashboard
- Attendance Dashboard
- Leave Dashboard
- Shift Dashboard
- Performance Dashboard
- Training Dashboard
- ESS Dashboard
- Separation Dashboard

## 18. APPROVAL WORKFLOWS

### Job Requisition

```
Department Head
↓
HR Manager
↓
Approved
```

### Leave Approval

```
Employee
↓
Reporting Manager
↓
Approved
```

### Shift Change

```
Employee
↓
Manager
↓
HR Approval
```

### Separation Approval

```
Employee
↓
Manager
↓
HR
↓
Final Approval
```

## 19. NOTIFICATIONS

Events

- Interview Scheduled
- Offer Sent
- Employee Joined
- Leave Approved
- Training Assigned
- Performance Review Due

Channels

- Email
- In-App
- WhatsApp

## 20. AUDIT REQUIREMENTS

Track:

- Employee Updates
- Attendance Changes
- Leave Approvals
- Performance Reviews
- Training Records
- Exit Actions

## 21. DATABASE TABLES

- job_requisitions
- candidates
- interviews
- offers
- employees
- attendance
- leave_requests
- leave_balances
- shifts
- employee_shifts
- performance_reviews
- training_programs
- training_assignments
- employee_separations

## 22. KEY RELATIONSHIPS

```
Department
1:N Employees

Employee
1:N Attendance

Employee
1:N Leave Requests

Employee
1:N Performance Reviews

Employee
1:N Training Assignments
```

## 23. API SPECIFICATIONS

### Employee APIs

```
GET /api/v1/employees

POST /api/v1/employees

PUT /api/v1/employees/{id}
```

### Attendance APIs

```
GET /api/v1/attendance

POST /api/v1/attendance
```

### Leave APIs

```
GET /api/v1/leaves

POST /api/v1/leaves

PUT /api/v1/leaves/{id}
```

### Performance APIs

```
GET /api/v1/performance

POST /api/v1/performance
```

## 24. REPORTS

### HR Reports

- Employee Master Report
- Attendance Report
- Leave Balance Report
- Recruitment Report
- Interview Report
- Performance Report
- Training Completion Report
- Attrition Report

## 25. ACCEPTANCE CRITERIA

✅ Recruitment workflow works

✅ Candidate tracking works

✅ Onboarding checklist enforced

✅ Attendance captured correctly

✅ Leave approval workflow works

✅ Performance reviews recorded

✅ ESS portal functional

✅ Separation process completed properly

## 26. UAT SCENARIOS

### UAT-001

Create Job Requisition

Expected:

Requisition Created Successfully

### UAT-002

Schedule Interview

Expected:

Candidate Notified

### UAT-003

Approve Leave Request

Expected:

Leave Balance Updated

### UAT-004

Assign Training

Expected:

Training Assigned Successfully

### UAT-005

Employee Resignation

Expected:

Exit Workflow Triggered

## ARCHITECT REVIEW

FRD-09 HR Domain is now locked.

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
Payroll
```

### Critical Observation

HR Domain now supports:

- Recruitment-to-Hire
- Employee Lifecycle
- Attendance & Leave
- Performance Management
- Training Management
- Employee Self Service
- Separation Management
