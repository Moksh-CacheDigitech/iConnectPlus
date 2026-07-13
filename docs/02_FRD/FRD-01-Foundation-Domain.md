# FRD-01 FOUNDATION DOMAIN (ARCHITECTURE FREEZE)

## Version
1.0

## Status
Architecture Approved

## Cross References
- Downstream dependency: [FRD-02 Organization Domain](./FRD-02-Organization-Domain.md)
- Referenced by all modules for Authentication, Authorization, RBAC, Workflow, Notification, and Audit services.
- Related platform backbone: [FRD-21 Integration Hub & Enterprise Platform Services](./FRD-21-Integration-Hub-Enterprise-Platform-Services.md)

## Purpose

Foundation Domain ERP ke sabhi modules ke liye centralized platform services provide karega.

Ye domain provide karega:

- Authentication
- Authorization
- User Management
- Role Management
- Permission Management
- Organization Context
- Workflow Engine
- Notification Engine
- Audit Engine
- Global Settings

## FOUNDATION MODULE BREAKDOWN

```
Foundation Domain

├── Authentication
├── Session Management
├── User Management
├── Role Management
├── Permission Management
├── RBAC Engine
├── Organization Context
├── Workflow Engine
├── Notification Engine
├── Audit Engine
└── Settings Management
```

## USER TYPES

### Super Admin

Access:

- Entire ERP
- Multi Company
- All Settings

### Company Admin

Access:

- Company Level

Cannot:

- Access Other Companies

### Branch Admin

Access:

- Branch Level

Cannot:

- Access Other Branches

### Manager

Department Specific Access

### Employee

Self Service Access

## AUTHENTICATION MODULE

### Purpose

Secure user access.

### Login Screen

#### Fields

| Field | Type | Required |
|---|---|---|
| Email | Email | Yes |
| Password | Password | Yes |

#### Actions

- Login
- Forgot Password

#### Validation Rules

Email:

- Must be valid email format

Password:

- Minimum 8 characters
- At least:
  - 1 Uppercase
  - 1 Lowercase
  - 1 Number
  - 1 Special Character

### MFA Screen

#### Fields

| Field | Type |
|---|---|
| OTP | Numeric |

Length:

- 6 Digits

Expiry:

- 5 Minutes

### Authentication Flow

```
Email
Password
↓
Validate
↓
MFA
↓
Generate Access Token
↓
Dashboard
```

## SESSION MANAGEMENT

### Requirements

Track:

- Login Time
- Logout Time
- Device
- Browser
- IP Address

### Session Timeout

30 Minutes Inactivity

### Concurrent Sessions

Configurable:

- Single Session
- OR
- Multiple Sessions

## USER MANAGEMENT MODULE

### Screen Inventory

- User List
- User Create
- User Edit
- User Details
- User Deactivate
- User Reset Password

### User Create Fields

| Field | Required |
|---|---|
| Employee | Yes |
| Email | Yes |
| Username | Yes |
| Role | Yes |
| Company | Yes |
| Branch | Yes |
| Status | Yes |

### User Status

- Active
- Inactive
- Locked
- Pending Activation

## ROLE MANAGEMENT

### Screen Inventory

- Role List
- Role Create
- Role Edit
- Role Clone
- Role Archive

### Role Fields

| Field |
|---|
| Role Name |
| Description |
| Role Type |

### Role Types

- System Role
- Business Role
- Custom Role

## PERMISSION MANAGEMENT

### Permission Levels

#### Level 1

Module

Example:

- Finance
- HR
- Sales

#### Level 2

Screen

Example:

- Sales Order
- Invoice
- Customer

#### Level 3

Action

- View
- Create
- Edit
- Delete
- Approve
- Export
- Print

#### Level 4

Data Scope

- Own Records
- Department
- Branch
- Company
- Global

## RBAC ENGINE

### Permission Formula

```
User
↓
Role
↓
Permissions
↓
Data Scope
```

### Access Evaluation

Example:

HR Manager

Can View:
- Employees

Can Edit:
- Employees

Cannot Delete:
- Employees

## ORGANIZATION CONTEXT

### Context Levels

- Tenant
- Company
- Branch
- Department

### Mandatory Filters

Every Business Record Must Contain:

- tenant_id
- company_id
- branch_id
- created_by
- created_at

## WORKFLOW ENGINE

### Purpose

Dynamic Approval Management

### Workflow Builder

Admin can create:

- Approval Levels
- Conditions
- Escalations
- Notifications

Without coding.

### Workflow States

- Draft
- Submitted
- Under Review
- Approved
- Rejected
- Cancelled

### Example Workflow

Purchase Request

```
Employee
↓
Manager
↓
Finance
↓
Procurement
↓
Approved
```

### Escalation

Rule:

If no action within 48 hours

Escalate

## NOTIFICATION ENGINE

### Channels

- Email
- SMS
- WhatsApp
- In-App

### Notification Types

- Approval Request
- Approval Granted
- Approval Rejected
- Password Reset
- Inventory Alert
- Payroll Generated

### Template Management

Templates support:

- Variables
- Conditions
- Localization

Example:

Hello {{EmployeeName}}

Your Leave Request has been approved.

## AUDIT ENGINE

### Purpose

Track all critical changes.

### Audit Events

- Create
- Update
- Delete
- Approve
- Reject
- Login
- Logout

### Audit Fields

| Field |
|---|
| User |
| Module |
| Record ID |
| Action |
| Old Value |
| New Value |
| IP Address |
| Timestamp |

### Retention

7 Years

Minimum.

## SETTINGS MANAGEMENT

### Categories

#### Company Settings
- Company Name
- Branding
- Logo

#### Localization
- Language
- Currency
- Timezone

#### Security
- Password Policy
- MFA Policy

#### Email
- SMTP Configuration

#### Notifications
- SMS Providers
- WhatsApp Providers

## FOUNDATION DATABASE TABLES

### Core Tables

- users
- roles
- permissions
- role_permissions
- user_roles
- sessions
- mfa_codes
- workflows
- workflow_steps
- workflow_conditions
- notifications
- notification_templates
- audit_logs
- settings
- companies
- branches
- departments

## API MODULES

### Authentication APIs

```
POST /api/v1/auth/login

POST /api/v1/auth/logout

POST /api/v1/auth/mfa

POST /api/v1/auth/forgot-password

POST /api/v1/auth/reset-password
```

### User APIs

```
GET /api/v1/users

POST /api/v1/users

PUT /api/v1/users/{id}

DELETE /api/v1/users/{id}
```

### Role APIs

```
GET /api/v1/roles

POST /api/v1/roles

PUT /api/v1/roles/{id}
```

### Workflow APIs

```
GET /api/v1/workflows

POST /api/v1/workflows

PUT /api/v1/workflows/{id}
```

## SECURITY REQUIREMENTS

Mandatory:

- JWT Access Token
- Refresh Token
- MFA
- Password Hashing
- Rate Limiting
- CSRF Protection
- XSS Protection
- SQL Injection Protection

## ACCEPTANCE CRITERIA

Foundation Module shall be accepted when:

✅ Users can authenticate securely

✅ MFA works successfully

✅ Roles and permissions are enforced

✅ Workflow engine supports dynamic approvals

✅ Notifications are delivered

✅ Audit logs are generated

✅ Organization isolation is enforced

✅ Security testing is passed

✅ UAT sign-off is completed

## UAT TEST SCENARIOS

### UAT-001

Login with valid credentials

Expected:

User logged in successfully

### UAT-002

Login with invalid password

Expected:

Authentication failed

### UAT-003

Role without permission accesses module

Expected:

Access denied

### UAT-004

Approval workflow escalation

Expected:

Escalation triggered after configured duration

### UAT-005

Audit log generation

Expected:

Action recorded in audit log

## Architect Review

FRD-01 is now sufficient to begin:

- Authentication Development
- RBAC Development
- Workflow Engine Development
- Notification Engine Development
- Audit Engine Development
