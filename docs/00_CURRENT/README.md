# Current system (living)

These documents describe **iConnect Plus as implemented**, not only as planned in the baseline pack.

| Document | Purpose |
|----------|---------|
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | Stack, package layout, platform seams, request & async flows |
| [MODULE_CATALOG.md](MODULE_CATALOG.md) | Every API module, UI group, and primary business flows |
| [Module Features (as built)](../07_MASTER_ARCHITECTURE/Enterprise_ERP_Module_Features.md) | Full per-module feature inventory (API + UI), Master Architecture companion |
| [Cache Scope & Improvement Report](../07_MASTER_ARCHITECTURE/Cache_Technologies_Scope_and_Improvement_Report.md) | Cache-applicable modules (CRM, Procurement, Projects, HRMS, Assets), E2E workflows, integrations, reporting gaps · [PDF](../07_MASTER_ARCHITECTURE/Cache_Technologies_Scope_and_Improvement_Report.pdf) |

When code and baseline FRD/SDD disagree on *implementation detail*, treat **code + this folder** as current and open an ADR / FRD change if the baseline must move.
