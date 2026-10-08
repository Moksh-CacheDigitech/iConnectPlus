# ERP Architecture Addendum v1.2 — Implementation Reality

**Document type:** Addendum to Architecture Lock Report v1.1  
**Date:** 2026-10-08  
**Status:** Informative (does not unlock Tier D)  
**Parent:** `ERP_Architecture_Lock_Report_v1.1.md`

This addendum records what has been **built on top of** the locked baseline. It does **not** change ADR-001 / ADR-002 or the forbidden stack list.

## 1. Locked decisions (unchanged)

- Modular monolith · Clean Architecture · DDD  
- Python 3.13 / FastAPI / SQLAlchemy 2 / Alembic / Pydantic v2 / Celery  
- Next.js 16+ / TypeScript / Tailwind / ShadCN  
- PostgreSQL · UUID · tenant isolation · soft delete · Alembic-only schema  
- Router → Service → Repository → Database  

## 2. Platform seams now in code

| Capability | Location | Status |
|------------|----------|--------|
| Cross-module ports + adapters | `modules/platform` | In use |
| Transactional outbox + drain | `platform/outbox`, Celery | In use |
| One finance posting path | `IFinancePosting` adapter | In use |
| One inventory stock path | `IInventoryStock` adapter | In use |
| Audit / notify facades | `platform/compat` | Widely adopted |
| Document numbering SSOT | `helpers/ssot_numbering`, `numbering` | In use |
| Approval policy matrix | `policies.py` + `workflow_gate` | In use |
| Optimistic concurrency | `VersionMixin` + 409 handler | Platform-wide |
| Field encryption | `encrypted_types` + migration 0635 | Tax/KYC/bank/secrets |
| Cross-module ORM debt | Architecture CI gate | **Zero** outside adapters |
| Permission catalog sync | `permission_catalog` + 0633 | In use |
| SLO samples / Prometheus text | `/platform/slo/*`, `/platform/metrics` | Per-process |
| System job idempotency | `FndJobRun` + `system_job` | In use |
| Master-data published reads | `master_data.published` | In use |

## 3. Sprint-0 artifacts (status update)

| Artifact (v1.1 §9) | Status as of addendum |
|--------------------|------------------------|
| Monorepo scaffold | Done |
| PostgreSQL + Alembic | Done (head through encryption / job-run / permission sync) |
| FastAPI core | Done |
| Foundation + business modules | Done (see `docs/00_CURRENT/MODULE_CATALOG.md`) |
| ERD pack | Present under `docs/06_ERD/` |
| OpenAPI | Generated from app; gated by `ENABLE_API_DOCS` |
| Docker Compose / Coolify | Done |

## 4. Explicitly still gated (Tier D)

Do **not** treat these as “left to build now”:

- Microservice extraction  
- Broad event bus / CQRS rewrite  
- OpenSearch as required OLTP dependency  
- Analytical warehouse beyond current `Ana*` read models  
- Kubernetes as the only deploy target  

Flip flags in `modules/platform/evolution.py` only when ports, outbox, ORM debt, SLO-green, and ownership are all true for that context.

## 5. Living docs

Implementation truth for modules and flows:

- `docs/00_CURRENT/SYSTEM_OVERVIEW.md`  
- `docs/00_CURRENT/MODULE_CATALOG.md`  
- `docs/07_MASTER_ARCHITECTURE/Enterprise_ERP_Master_Architecture.md`  

---

**Baseline v1.1 remains LOCKED. Addendum v1.2 records adoption progress only.**
