# FRD-17 HELPDESK & CUSTOMER SUPPORT DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Related: [FRD-12 Asset Management Domain](./FRD-12-Asset-Management-Domain.md) (OEM & Asset Linking)
- Downstream dependency: [FRD-16 Service Management Domain](./FRD-16-Service-Management-Domain.md)

## 1. PURPOSE

Helpdesk Domain users, customers, employees aur assets se related incidents, requests aur issues ko manage karega.

### Business Objectives

- Centralized Ticket Management
- SLA Compliance
- Faster Resolution
- Customer Satisfaction
- Service Visibility
- Knowledge Reuse

## 2. MODULES COVERED

- Ticket Management
- Incident Management
- Service Request Management
- Problem Management
- Change Management
- Knowledge Base
- SLA Management
- Escalation Management
- Customer Communication
- Support Analytics

## 3. HELPDESK LIFECYCLE

```
Issue Reported
↓
Ticket Created
↓
Assignment
↓
Investigation
↓
Resolution
↓
Validation
↓
Closure
```

## 4. TICKET MANAGEMENT

### Purpose

Central repository of all support requests.

### Ticket Sources

- Web Portal
- Mobile App
- Email
- Phone
- WhatsApp
- API
- Manual Entry

### Ticket Fields

| Field | Mandatory |
|---|---|
| Ticket Number | Yes |
| Requester | Yes |
| Category | Yes |
| Priority | Yes |
| Description | Yes |
| Status | Yes |

### Ticket Number Format

```
TKT-2026-000001
```

### Ticket Status

- New
- Assigned
- In Progress
- Pending
- Resolved
- Closed
- Cancelled

## 5. INCIDENT MANAGEMENT

### Purpose

Handle service interruptions.

### Incident Categories

- Hardware
- Software
- Network
- Security
- Application
- Infrastructure

### Impact Levels

- Low
- Medium
- High
- Critical

### Priority Matrix

| Impact | Urgency | Priority |
|---|---|---|
| High | High | P1 |
| High | Medium | P2 |
| Medium | Medium | P3 |
| Low | Low | P4 |

## 6. SERVICE REQUEST MANAGEMENT

### Purpose

Handle standard user requests.

### Request Types

- Password Reset
- Software Installation
- Access Request
- Hardware Request
- Asset Allocation
- Employee Onboarding

### Workflow

```
Request
↓
Approval
↓
Fulfillment
↓
Closure
```

## 7. PROBLEM MANAGEMENT

### Purpose

Identify root causes.

### Flow

```
Incident
↓
Problem Record
↓
Root Cause Analysis
↓
Known Error
↓
Permanent Fix
↓
Closure
```

### Problem Fields

| Field |
|---|
| Problem Number |
| Root Cause |
| Impact |
| Workaround |
| Resolution |

## 8. CHANGE MANAGEMENT

### Purpose

Control production changes.

### Change Types

- Standard
- Normal
- Emergency

### Change Lifecycle

```
Request
↓
Assessment
↓
Approval
↓
Implementation
↓
Validation
↓
Closure
```

### CAB Approval

Required for:

- Normal Changes
- High Risk Changes

## 9. KNOWLEDGE BASE MANAGEMENT

### Purpose

Reduce repetitive tickets.

### Article Types

- How To
- FAQ
- Troubleshooting
- Known Errors
- Best Practices

### Status

- Draft
- Review
- Published
- Archived

## 10. SLA MANAGEMENT

### Purpose

Track support commitments.

### SLA Metrics

- First Response Time
- Resolution Time
- Escalation Time
- Customer Response Time

### SLA Status

- Within SLA
- Warning
- Breached

### Example

| Priority | Response | Resolution |
|---|---|---|
| P1 | 15 Min | 4 Hours |
| P2 | 30 Min | 8 Hours |
| P3 | 4 Hours | 24 Hours |
| P4 | 1 Day | 3 Days |

## 11. ESCALATION MANAGEMENT

### Purpose

Prevent unresolved tickets.

### Escalation Levels

- L1 Support
- L2 Support
- L3 Support
- Manager
- Service Head

### Auto Escalation

Triggered by:

- SLA Breach
- No Response
- Customer Escalation

## 12. CUSTOMER COMMUNICATION

### Purpose

Maintain ticket communication history.

### Channels

- Email
- SMS
- WhatsApp
- Portal
- Mobile App

### Features

- Comments
- Internal Notes
- Attachments
- Communication History

## 13. OEM & ASSET LINKING (Enterprise Enhancement)

### Purpose

Link tickets with assets and OEMs.

### Example

```
Ticket
↓
Asset

Asset
↓
OEM

OEM
↓
Warranty

OEM
↓
Support Contract
```

### Benefits

- Warranty Validation
- AMC Validation
- OEM Performance Analysis
- MTTR Analysis

## 14. SUPPORT ANALYTICS

### KPIs

- Ticket Volume
- First Response Time
- Resolution Time
- SLA Compliance %
- Reopen Rate
- Customer Satisfaction (CSAT)
- MTTR
- MTBF

## 15. SCREEN INVENTORY

- Helpdesk Dashboard
- Ticket Dashboard
- Incident Dashboard
- Problem Dashboard
- Change Dashboard
- Knowledge Base
- SLA Dashboard
- Escalation Dashboard
- Customer Communication Dashboard
- Support Analytics Dashboard

## 16. APPROVAL WORKFLOWS

### Service Request Approval

```
Requester
↓
Manager
↓
IT Team
↓
Fulfilled
```

### Change Request Approval

```
Requester
↓
CAB Review
↓
Approval
↓
Implementation
```

### Emergency Change

```
Requester
↓
Emergency CAB
↓
Approval
```

## 17. NOTIFICATIONS

Events

- Ticket Assigned
- Ticket Escalated
- SLA Warning
- SLA Breach
- Ticket Resolved
- Change Approved

Channels

- Email
- In-App
- SMS
- WhatsApp

## 18. AUDIT REQUIREMENTS

Track:

- Ticket Changes
- Assignment Changes
- Status Changes
- SLA Changes
- Change Approvals
- Knowledge Updates

## 19. DATABASE TABLES

- tickets
- ticket_comments
- ticket_attachments
- incidents
- problems
- known_errors
- changes
- change_approvals
- knowledge_articles
- sla_policies
- sla_events
- ticket_escalations
- customer_feedback
- ticket_asset_mapping

## 20. KEY RELATIONSHIPS

```
Customer
1:N Tickets

Ticket
1:N Comments

Ticket
1:N Attachments

Incident
1:1 Problem

Problem
1:N Known Errors

Ticket
N:1 Asset

Asset
N:1 OEM
```

## 21. API SPECIFICATIONS

### Ticket APIs

```
GET /api/v1/tickets

POST /api/v1/tickets

PUT /api/v1/tickets/{id}
```

### Incident APIs

```
GET /api/v1/incidents

POST /api/v1/incidents
```

### Change APIs

```
GET /api/v1/changes

POST /api/v1/changes
```

### Knowledge APIs

```
GET /api/v1/knowledge

POST /api/v1/knowledge
```

## 22. REPORTS

### Helpdesk Reports

- Ticket Summary Report
- SLA Compliance Report
- MTTR Report
- Incident Report
- Problem Report
- Change Success Rate Report
- Knowledge Usage Report
- Customer Satisfaction Report
- OEM Performance Report

## 23. ACCEPTANCE CRITERIA

✅ Ticket lifecycle works

✅ Incident management works

✅ Problem management works

✅ Change approvals work

✅ SLA tracking works

✅ Auto escalation works

✅ Knowledge base searchable

✅ Asset/OEM linkage works

## 24. UAT SCENARIOS

### UAT-001

Create Ticket

Expected:

Ticket Created Successfully

### UAT-002

SLA Breach

Expected:

Escalation Triggered Automatically

### UAT-003

Create Problem Record

Expected:

Problem Linked To Incident

### UAT-004

Approve Change

Expected:

Change Released Successfully

### UAT-005

Search Knowledge Base

Expected:

Relevant Articles Returned

## ARCHITECT REVIEW

FRD-17 Helpdesk & Customer Support Domain is now locked.

### Important Observation

Ab tumhara ERP traditional ERP se aage nikal raha hai.

Current modules cover:

```
ERP
+
ITSM
+
Asset Lifecycle
+
OEM Intelligence Foundation
+
Service Management
```
