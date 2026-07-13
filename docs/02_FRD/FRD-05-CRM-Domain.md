# FRD-05 CRM DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-03 Master Data Domain](./FRD-03-Master-Data-Domain.md)
- Downstream dependency: [FRD-06 Sales Domain](./FRD-06-Sales-Domain.md)

## 1. PURPOSE

CRM domain prospects, leads, opportunities aur customer interactions manage karega.

### Business Objectives

- Centralized Lead Management
- Opportunity Tracking
- Pipeline Visibility
- Sales Forecasting
- Customer Interaction Tracking
- Conversion Optimization

## 2. MODULES COVERED

- Lead Management
- Lead Assignment
- Lead Qualification
- Opportunity Management
- Activity Management
- Meeting Management
- Task Management
- Pipeline Management
- Sales Forecasting
- Customer Communication

## 3. CRM LIFECYCLE

```
Lead
↓
Qualified
↓
Opportunity
↓
Quotation
↓
Negotiation
↓
Won
↓
Sales Order

OR

Lost
```

## 4. LEAD MANAGEMENT

### Purpose

Potential customer information capture karna.

### Lead Sources

- Website
- Referral
- Cold Call
- Email Campaign
- Social Media
- Events
- Manual Entry

### Lead Fields

| Field | Mandatory |
|---|---|
| Lead Code | Yes |
| First Name | Yes |
| Last Name | No |
| Company Name | No |
| Email | No |
| Mobile | Yes |
| Lead Source | Yes |
| Lead Owner | Yes |
| Status | Yes |

### Lead Code Format

```
LEAD-000001
```

Auto Generated.

## 5. LEAD STATUS

- New
- Assigned
- Contacted
- Qualified
- Unqualified
- Converted
- Lost

### Validation Rules

Lead cannot be converted unless:

Mandatory Contact Information Exists

## 6. LEAD ASSIGNMENT

### Assignment Types

#### Manual

Sales Manager assigns lead.

#### Automatic

Based on:

- Territory
- Industry
- Region
- Workload

## 7. LEAD QUALIFICATION

### Qualification Parameters

| Parameter |
|---|
| Budget |
| Authority |
| Need |
| Timeline |

### Outcome

- Qualified
- Unqualified

## 8. OPPORTUNITY MANAGEMENT

### Purpose

Qualified sales opportunity track karna.

### Opportunity Fields

| Field |
|---|
| Opportunity Code |
| Opportunity Name |
| Customer |
| Expected Revenue |
| Expected Close Date |
| Sales Owner |
| Stage |

### Opportunity Code

```
OPP-000001
```

## 9. OPPORTUNITY STAGES

- Qualification
- Discovery
- Proposal
- Negotiation
- Won
- Lost

### Business Rule

Won Opportunity:

Can Generate Quotation

## 10. ACTIVITY MANAGEMENT

### Activity Types

- Call
- Meeting
- Email
- Task
- Follow-up

### Activity Fields

| Field |
|---|
| Activity Type |
| Date |
| Owner |
| Notes |
| Outcome |

## 11. MEETING MANAGEMENT

### Fields

| Field |
|---|
| Meeting Title |
| Date |
| Time |
| Participants |
| Notes |

### Outcomes

- Interested
- Need Follow-up
- Closed

## 12. TASK MANAGEMENT

### Purpose

Track sales activities.

### Task Status

- Pending
- In Progress
- Completed
- Cancelled

## 13. PIPELINE MANAGEMENT

### Purpose

Visual sales funnel.

### Pipeline Stages

- Lead
- Qualified
- Opportunity
- Proposal
- Negotiation
- Won
- Lost

### Metrics

Track:

- Conversion Rate
- Pipeline Value
- Average Deal Size
- Sales Cycle Length

## 14. CUSTOMER COMMUNICATION

### Communication Channels

- Email
- Phone
- WhatsApp
- SMS

### Communication Log

Every interaction stored.

## 15. SALES FORECASTING

### Forecast Types

- Monthly
- Quarterly
- Yearly

### Inputs

- Pipeline Value
- Probability %
- Expected Close Date

### Formula

```
Forecast Revenue
=
Expected Revenue
×
Probability %
```

## 16. SCREEN INVENTORY

- Lead Dashboard
- Lead List
- Lead Details
- Lead Create
- Opportunity Dashboard
- Opportunity List
- Opportunity Details
- Activity Calendar
- Meeting Scheduler
- Task Board
- Pipeline Dashboard
- Forecast Dashboard

## 17. APPROVAL WORKFLOWS

### Lead Conversion

```
Lead
↓
Qualification
↓
Manager Approval
↓
Opportunity
```

### Opportunity Closure

```
Won/Lost
↓
Manager Validation
```

## 18. NOTIFICATIONS

Events:

- Lead Assigned
- Lead Qualified
- Opportunity Created
- Meeting Reminder
- Task Due
- Opportunity Won

Channels

- Email
- In-App
- WhatsApp

## 19. AUDIT REQUIREMENTS

Track:

- Lead Creation
- Lead Update
- Lead Assignment
- Opportunity Changes
- Activity Updates
- Status Changes

## 20. DATABASE TABLES

- leads
- lead_sources
- lead_assignments
- lead_notes
- opportunities
- opportunity_stages
- activities
- meetings
- tasks
- communication_logs
- sales_forecasts

## 21. KEY RELATIONSHIPS

```
Lead
1:N Activities

Lead
1:1 Opportunity

Opportunity
1:N Meetings

Opportunity
1:N Tasks

Customer
1:N Opportunities
```

## 22. API SPECIFICATIONS

### Lead APIs

```
GET /api/v1/leads

POST /api/v1/leads

PUT /api/v1/leads/{id}

DELETE /api/v1/leads/{id}
```

### Opportunity APIs

```
GET /api/v1/opportunities

POST /api/v1/opportunities

PUT /api/v1/opportunities/{id}
```

### Activity APIs

```
GET /api/v1/activities

POST /api/v1/activities
```

## 23. REPORTS

### CRM Reports

- Lead Source Report
- Lead Conversion Report
- Opportunity Report
- Sales Funnel Report
- Sales Forecast Report
- Activity Report

## 24. ACCEPTANCE CRITERIA

✅ Leads created successfully

✅ Lead assignment works

✅ Opportunity conversion works

✅ Pipeline visible

✅ Forecast generated

✅ Activities tracked

✅ Reports generated

## 25. UAT SCENARIOS

### UAT-001

Create Lead

Expected:

Lead Created Successfully

### UAT-002

Assign Lead

Expected:

Lead Assigned To Sales User

### UAT-003

Convert Lead To Opportunity

Expected:

Opportunity Created

### UAT-004

Create Activity

Expected:

Activity Logged

### UAT-005

Forecast Revenue

Expected:

Forecast Calculated Correctly

## ARCHITECT REVIEW

FRD-05 CRM Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
CRM
↓
Sales
```
