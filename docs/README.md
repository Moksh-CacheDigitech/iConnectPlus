# iConnect Plus — Documentation Map

**Product:** iConnect Plus (enterprise ERP)  
**Architecture baseline:** v1.1 (locked) · **Implementation reality:** see `00_CURRENT/`  
**Last doc refresh:** 2026-10-08

## How to read these docs

| Order | Folder | Role |
|------:|--------|------|
| 0 | [`00_CURRENT/`](00_CURRENT/) | **Start here** — living map of modules, platform seams, and request flows as built |
| 1 | [`01_BRD/`](01_BRD/) | Business intent and scope (baseline) |
| 2 | [`02_FRD/`](02_FRD/) | Functional requirements by domain (baseline) |
| 3 | [`03_SDD/`](03_SDD/) | System design (baseline v1.1; filename still `*_v1.0.md`) |
| 4 | [`04_DBS/`](04_DBS/) | Database standards (baseline v1.1; filename still `*_v1.0.md`) |
| 5 | [`05_ARCHITECTURE_LOCK/`](05_ARCHITECTURE_LOCK/) | Locked decisions + Addendum v1.2 |
| 6 | [`06_ERD/`](06_ERD/) | Logical ERDs by domain |
| 7 | [`07_MASTER_ARCHITECTURE/`](07_MASTER_ARCHITECTURE/) | Consolidated solution architecture (current) |
| 8 | [`07_RELEASES/`](07_RELEASES/) | Latest release notes and demo guides |
| 9 | [`ADR/`](ADR/) | Architecture Decision Records (asset / domain ADRs) |
| 10 | [`09_OPS/`](09_OPS/) | Deploy contracts and operational runbooks |
| 11 | [`security/`](security/) | SAST / DAST / VAPT evidence and accepted risks |

## Source of truth

| Concern | Source |
|---------|--------|
| Locked stack & pattern | `05_ARCHITECTURE_LOCK` (Lock v1.1 + Addendum v1.2) + ADR-001 / ADR-002 |
| What is actually running | `00_CURRENT/` + code under `apps/api`, `apps/web` |
| API surface | `apps/api/src/shared/router.py` + module routers |
| UI module registry | `apps/web/src/config/modules.ts` |
| Schema | Alembic under `apps/api/alembic/versions/` |

**Filename note:** `03_SDD/ERP_SDD_v1.0.md` and `04_DBS/ERP_DBS_v1.0.md` filenames predate the lock; document **Version** headers are **v1.1** (ADR-002). Prefer content version over filename.

Historical sprint reports, phase checklists, asset CR packs, ESS phase notes, and one-off audit dumps were removed on 2026-10-08. Prefer code + this map over archived archaeology.
