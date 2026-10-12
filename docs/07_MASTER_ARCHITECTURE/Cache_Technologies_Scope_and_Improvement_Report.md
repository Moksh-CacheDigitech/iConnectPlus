# Cache Technologies — Scope & Improvement Brief

**Date:** 2026-10-12  
**Audience:** Management / Service Delivery  
**Product:** iConnect Plus  

---

## Observation

After review of the shared architecture and module documents:

- Certain sections describe a **generic ERP framework**
- Some modules are **not applicable** to Cache Technologies’ business model today
- Cache’s operating model is sales → supply → site delivery → people → assets — not full plant/ecommerce ERP

---

## Cache-applicable modules (as of now)

Only these five modules are in scope for Cache Technologies:

- **CRM** — Company → Lead → Opportunity → Quote → OVF → deal won / share to SCM
- **Procurement** — SCM queue → vendor PO → GRN → delivery challan / delivery projects
- **Projects** — PO queue → site stages (survey → SCM → onsite → handover → install → acceptance)
- **HRMS** — Workforce, attendance, leave, onboarding / offboarding, ESS
- **Assets** — Incoming (from GRN) → register → assign → DC challan / Non-IT register

**Foundation (always required, not “extra modules”):**

- Auth / RBAC
- Workflow / Notification / Audit
- Organization
- Master Data (employees, products, parties as needed)

**Out of Cache day-1 focus (framework only):**

- Manufacturing, Ecommerce, Portal, full GRC / plant Quality, Marketing suite, classic Sales O2C UI, deep Finance ops UI (keep posting path when needed)

---

## End-to-end workflows

### Master chain

```text
CRM (OVF share)
  - Procurement / SCM (PO → GRN → challan)
  - Projects (PO queue → site install → acceptance)
  - Assets (incoming from GRN → assign / DC)
  - HRMS (people assigned to sites / ESS assets)
```

### Scenarios for Service Delivery (Anurag / Ashwani)

Fill / confirm each with happy path, exceptions, actors, and mandatory fields:

- **S1** — Standard HW deal: OVF → SCM → PO → GRN → site → acceptance
- **S2** — Services-heavy deal (margin / little HW)
- **S3** — Partial GRN / multi-site delivery
- **S4** — Fulfil from stock (no new vendor PO)
- **S5** — OVF hold / charge change after SCM share
- **S6** — Lost deal / My Jobs reject / quote rework
- **S7** — Asset assign + DC challan lifecycle
- **S8** — Non-IT assets
- **S9** — New joiner for project deployment
- **S10** — Separation + asset recovery
- **S11** — Customer tracker / external status
- **S12** — Multi-OEM / multi-vendor BOQ

### SD input needed per scenario

- Business trigger
- Actors / RACI
- Happy-path steps
- Exception paths
- Extra mandatory fields
- SLA / TAT
- Reports required

---

## Module integration (key handoffs)

### CRM → Procurement

- OVF status `shared_scm`
- `po_number`, delivery period
- Vendor / customer payment days → `finance_cost_pct`
- Line sides (customer vs vendor)
- Freight / additional / finance % (editable in SCM; syncs to CRM)
- Branch / company

### Procurement → Projects

- Issued PO / company PO number
- Site / circle / contact
- Rack / server flags
- Optional challan id
- CRM customer / opportunity prefill

### Procurement → Assets

- GRN / receipt line
- Serials / qty
- Branch / company

### Assets → SCM (DC challan)

- `dc_number`, asset snapshot (tag, make, model, serial, cost)
- Employee snapshot (directory vs manual + `deployed_to`)
- Status: PENDING → SENT_TO_SCM → DOCUMENT_RECEIVED → SIGNED → RECEIVED
- Note: live SCM HTTP still partial (callback contract; outbound log-only this phase)

### HRMS ↔ Projects / Assets

- Stage assignees / `owner_employee_id`
- Employee identity on DC / CRM
- ESS / workforce asset custody

---

## Reporting and dashboards

### Exists today

- **CRM** — pipeline KPIs, sales performance (OVF margin), saved reports, stock aging
- **Procurement** — SCM/PO/GRN funnel, exports, aging, timeline
- **Projects** — site KPIs / stage queues, member jobs, profitability
- **HRMS** — executive headcount / attendance / leave / hiring dashboard
- **Assets** — ops KPIs + reports workspace (IT / Non-IT)

### Gaps to close (priority)

- **R1** — One Cache Ops view: open OVFs, SCM holds, stuck sites, pending DC
- **R2** — Deal-to-acceptance cycle time by stage
- **R3** — Site SLA board (survey / install / acceptance TAT)
- **R4** — PO vs GRN vs site material readiness
- **R5** — Asset custody vs site / employee
- **R6** — Workforce on project (assignees vs attendance)
- **R7** — Weekly management export / email of the above

---

## Next actions

- Confirm Cache shortlist: CRM, Procurement, Projects, HRMS, Assets
- Service Delivery workshop (Anurag, Ashwani) on S1–S12
- Sign integration field list above (+ any SD extras)
- Build dashboards R1–R3 first
- Close live DC challan ↔ SCM loop
- Label other modules as Framework in shared decks to avoid confusion
