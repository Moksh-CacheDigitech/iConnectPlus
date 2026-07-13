# FRD-16 SERVICE MANAGEMENT DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependencies: [FRD-01 Foundation Domain](./FRD-01-Foundation-Domain.md), [FRD-03 Master Data Domain](./FRD-03-Master-Data-Domain.md), [FRD-12 Asset Management Domain](./FRD-12-Asset-Management-Domain.md), [FRD-17 Helpdesk & Customer Support Domain](./FRD-17-Helpdesk-Customer-Support-Domain.md)
- Downstream dependency: [FRD-04 Finance & Accounting Domain](./FRD-04-Finance-Accounting-Domain.md)

## 1. PURPOSE

Service Management Domain service delivery aur maintenance operations ko manage karega.

### Business Objectives

- Service Request Management
- SLA Compliance
- Field Service Optimization
- Maintenance Planning
- Technician Productivity
- Customer Satisfaction

## 2. MODULES COVERED

- Service Requests
- Service Contracts
- Work Orders
- Preventive Maintenance
- Corrective Maintenance
- Breakdown Maintenance
- Field Service Management
- Technician Scheduling
- Service Parts Management
- SLA Management
- Service Billing

## 3. SERVICE LIFECYCLE

```
Service Request
↓
Assignment
↓
Work Order
↓
Technician Dispatch
↓
Service Execution
↓
Validation
↓
Closure
↓
Billing
```

## 4. SERVICE REQUEST MANAGEMENT

### Purpose

Capture service needs.

### Request Sources

- Customer Portal
- Email
- Phone
- Mobile App
- Helpdesk
- Manual Entry

### Service Request Fields

| Field | Mandatory |
|---|---|
| Request Number | Yes |
| Customer | Yes |
| Asset | No |
| Service Type | Yes |
| Priority | Yes |
| Description | Yes |
| Status | Yes |

### Request Number Format

```
SR-2026-000001
```

### Priority Levels

- Low
- Medium
- High
- Critical

### Status

- New
- Assigned
- In Progress
- Resolved
- Closed
- Cancelled

## 5. SERVICE CONTRACT MANAGEMENT

### Purpose

Manage customer service agreements.

### Contract Types

- AMC
- Warranty
- Support Contract
- Managed Services

### Contract Fields

| Field |
|---|
| Contract Number |
| Customer |
| Start Date |
| End Date |
| Coverage |
| SLA |

### Contract Number

```
SC-2026-000001
```

## 6. WORK ORDER MANAGEMENT

### Purpose

Execute service activities.

### Work Order Fields

| Field |
|---|
| Work Order Number |
| Request Reference |
| Technician |
| Scheduled Date |
| Completion Date |
| Status |

### Work Order Number

```
WO-SRV-2026-000001
```

### Status

- Draft
- Assigned
- In Progress
- Completed
- Closed

## 7. PREVENTIVE MAINTENANCE

### Purpose

Avoid breakdowns.

### Scheduling Types

- Daily
- Weekly
- Monthly
- Quarterly
- Half-Yearly
- Yearly

### Trigger Sources

- Calendar Based
- Usage Based
- Meter Based

## 8. CORRECTIVE MAINTENANCE

### Purpose

Fix identified issues.

### Trigger Sources

- Inspection Failure
- Customer Complaint
- Technician Finding
- Asset Monitoring Alert

## 9. BREAKDOWN MAINTENANCE

### Purpose

Handle urgent failures.

### Characteristics

- Immediate Response
- High Priority
- SLA Driven

### Escalation

Mandatory.

## 10. FIELD SERVICE MANAGEMENT

### Purpose

Manage on-site service operations.

### Features

- Technician Assignment
- Route Planning
- Geo Tracking
- Mobile App
- Digital Service Report

### Technician Data

| Field |
|---|
| Technician |
| Skills |
| Certifications |
| Region |
| Availability |

## 11. TECHNICIAN SCHEDULING

### Purpose

Optimize workforce allocation.

### Scheduling Factors

- Skill Match
- Location
- Availability
- Priority
- SLA

### Validation

No overlapping assignments

## 12. SERVICE PARTS MANAGEMENT

### Purpose

Track spare part usage.

### Sources

- Inventory
- Warehouse
- Vendor

### Fields

| Field |
|---|
| Part |
| Quantity |
| Cost |
| Work Order |

### Inventory Impact

```
Parts Consumption
↓
Inventory Reduction
```

## 13. SLA MANAGEMENT

### Purpose

Track contractual commitments.

### SLA Metrics

- Response Time
- Resolution Time
- First Time Fix Rate
- Availability

### SLA Status

- Within SLA
- At Risk
- Breached

## 14. SERVICE BILLING

### Purpose

Generate invoices for service activities.

### Billing Types

- Time Based
- Fixed Price
- Contract Based
- Material Based

### Finance Impact

- Accounts Receivable Dr
- Service Revenue Cr

## 15. SCREEN INVENTORY

- Service Dashboard
- Service Request Dashboard
- Service Contract Dashboard
- Work Order Dashboard
- Maintenance Dashboard
- Field Service Dashboard
- Technician Dashboard
- SLA Dashboard
- Service Billing Dashboard

## 16. APPROVAL WORKFLOWS

### Service Request Escalation

```
Agent
↓
Supervisor
↓
Manager
```

### Work Order Approval

```
Coordinator
↓
Service Manager
↓
Approved
```

### Service Billing Approval

```
Service Manager
↓
Finance
↓
Approved
```

## 17. NOTIFICATIONS

Events

- Request Assigned
- Technician Assigned
- SLA Breach Risk
- Maintenance Due
- Work Order Completed
- Invoice Generated

Channels

- Email
- In-App
- SMS
- WhatsApp

## 18. AUDIT REQUIREMENTS

Track:

- Request Updates
- Work Order Changes
- Technician Assignment
- SLA Changes
- Maintenance Records
- Billing Activities

## 19. DATABASE TABLES

- service_requests
- service_contracts
- service_work_orders
- preventive_maintenance
- corrective_maintenance
- breakdown_maintenance
- technician_profiles
- technician_schedules
- service_parts
- sla_policies
- sla_events
- service_billings

## 20. KEY RELATIONSHIPS

```
Customer
1:N Service Requests

Contract
1:N Service Requests

Request
1:N Work Orders

Technician
1:N Work Orders

Work Order
1:N Service Parts

Contract
1:N SLA Policies
```

## 21. API SPECIFICATIONS

### Service Request APIs

```
GET /api/v1/service-requests

POST /api/v1/service-requests

PUT /api/v1/service-requests/{id}
```

### Work Order APIs

```
GET /api/v1/service-work-orders

POST /api/v1/service-work-orders

PUT /api/v1/service-work-orders/{id}
```

### SLA APIs

```
GET /api/v1/sla

POST /api/v1/sla
```

## 22. REPORTS

### Service Reports

- Service Request Report
- SLA Compliance Report
- Technician Productivity Report
- Preventive Maintenance Report
- Breakdown Analysis Report
- Service Revenue Report
- Work Order Report
- Customer Service Performance Report

## 23. ACCEPTANCE CRITERIA

✅ Service requests created successfully

✅ Work orders generated

✅ Technician scheduling works

✅ Preventive maintenance schedules generated

✅ SLA tracking accurate

✅ Service billing generated

✅ Inventory updates for spare parts

✅ Reports generated correctly

## 24. UAT SCENARIOS

### UAT-001

Create Service Request

Expected:

Request Created Successfully

### UAT-002

Assign Technician

Expected:

Technician Assigned

### UAT-003

Complete Work Order

Expected:

Service Closure Recorded

### UAT-004

SLA Breach

Expected:

Escalation Triggered

### UAT-005

Generate Service Invoice

Expected:

Invoice Created Successfully

## ARCHITECT REVIEW

FRD-16 Service Management Domain is now locked.

### Dependency Chain

```
Foundation
↓
Master Data
↓
Assets
↓
Helpdesk
↓
Service Management
↓
Finance
```

### Critical Observation

Service Management now supports:

- End-to-End Service Lifecycle
- Preventive & Corrective Maintenance
- Field Service Operations
- SLA Governance
- Technician Scheduling
- Service Billing
