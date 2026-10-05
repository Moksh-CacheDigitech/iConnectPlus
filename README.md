# iConnect Plus

Multi-Industry, Multi-Company, Enterprise-Grade ERP Platform.

**Architecture Baseline:** v1.1 — LOCKED  
**Product:** iConnect Plus / Connect Plus (B2B SaaS admin)

## Architecture

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+, TypeScript, Tailwind CSS, ShadCN UI |
| Backend | Python 3.13+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Celery |
| Database | PostgreSQL (AWS RDS in production) |
| Search | OpenSearch |
| Object storage | MinIO (local / on-prem, S3 API) · AWS S3 (cloud) |
| Antivirus | ClamAV (upload scanning) |
| Cache / Queue | Redis, RabbitMQ |
| Auth | Microsoft Entra ID SSO · JWT in **HttpOnly cookies** (not localStorage) |
| Deploy | Docker Compose · Coolify on EC2 (`docker-compose.coolify.yml`) |

**Pattern:** Clean Architecture · DDD · Modular Monolith  
**Backend flow:** Router → Service → Repository → Database

## Documentation

| Document | Path |
|----------|------|
| BRD | `docs/01_BRD/` |
| FRD | `docs/02_FRD/` |
| SDD v1.1 | `docs/03_SDD/` |
| DBS v1.1 | `docs/04_DBS/` |
| Architecture Lock | `docs/05_ARCHITECTURE_LOCK/` |
| Coolify deploy | `docs/coolify-deploy.md` |

## Repository Structure

```text
enterprise-erp/
├── apps/
│   ├── api/                 # FastAPI backend
│   ├── web/                 # Next.js frontend
│   └── employee-app/        # Employee PWA (optional)
├── docker/
│   ├── minio/               # MinIO server image (build from source)
│   └── minio-mc/            # MinIO client image (build from source)
├── docs/
├── docker-compose.local.yml # All-in-one local stack (recommended)
├── docker-compose.infra.yml # Infra only (VM / shared host)
├── docker-compose.app.yml   # App services against external infra
├── docker-compose.coolify.yml
└── .env.example
```

## Quick Start (local Docker — recommended)

### 1. Environment

```bash
cp .env.example .env
```

Point infra at local services (see comments in `.env`). Important knobs:

| Variable | Local typical value | Notes |
|----------|---------------------|--------|
| `OBJECT_STORAGE_BACKEND` | `s3` or `minio` | S3-compatible API via MinIO |
| `S3_ENDPOINT_URL` | `http://localhost:9000` | Compose overrides to `http://minio:9000` inside containers |
| `S3_BUCKET` | `cache-erp-bucket` | Created by `minio-init` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | MinIO root user/password | Match `MINIO_ROOT_*` |
| `CLAMAV_ENABLED` | `true` | Upload AV scan |
| `CLAMAV_HOST` | `clamav` (in Docker) / `localhost` (host tools) | Port `3310` |
| `API_RATE_LIMIT` | `600`+ for local | Home dashboard fans out many GETs; `120` causes mass 429s |
| `AUTH_COOKIE_*` | HttpOnly cookie settings | Sessions use cookies; UI keeps a non-secret session hint after `/auth/me` |

### 2. Start the stack

```bash
docker compose -f docker-compose.local.yml up -d --build
```

This starts Postgres, Redis, RabbitMQ, OpenSearch, **ClamAV**, **MinIO** (+ bucket init), API, Celery worker, and Web.

| Service | Host URL / port |
|---------|-----------------|
| Web | http://localhost:3000 |
| API | http://localhost:8000 · health `/api/v1/health` |
| Postgres | `localhost:5433` |
| Redis | `localhost:6379` |
| RabbitMQ | `localhost:5672` · UI `:15672` |
| OpenSearch | http://localhost:9200 |
| MinIO API | http://localhost:9000 |
| MinIO Console | http://localhost:9001 |
| ClamAV | `localhost:3310` |

Default MinIO login (override via `.env`): `erp_minio` / `erp_minio_password`.

### 3. Sign-in

Use Microsoft Entra SSO from http://localhost:3000/login (or the landing access gate → live ERP).

Auth tokens are set as **HttpOnly cookies**. After a reload the UI probes `/auth/me` with credentials; do not expect tokens in `localStorage`.

---

## Compose files

| File | Use |
|------|-----|
| `docker-compose.local.yml` | Full local stack (infra + API + Celery + Web). No VM IPs. |
| `docker-compose.infra.yml` | Infra only on a LAN VM / shared host (Postgres, Redis, RabbitMQ, OpenSearch, MinIO, ClamAV). |
| `docker-compose.app.yml` | App containers against external infra. |
| `docker-compose.coolify.yml` | Production-style Coolify deploy (RDS + S3; see `docs/coolify-deploy.md`). |

### MinIO images (important)

Public Docker Hub / Quay MinIO images were removed (Sep 2026). Local and infra compose **build MinIO and `mc` from source**:

- `docker/minio/Dockerfile` → `enterprise-erp-minio:local`
- `docker/minio-mc/Dockerfile` → `enterprise-erp-minio-mc:local`

First build can take several minutes (Go compile). Images are cached afterward.

### Optional: sync DB from VM

```powershell
powershell -File scripts/sync-from-vm.ps1 -SkipMinio
```

---

## Host-based API / Web (optional)

Use when infra is already running (local compose or VM).

### Backend

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn main:app --reload --reload-dir src --host 0.0.0.0 --port 8000 --app-dir src
```

API: http://localhost:8000/api/v1/health  

OpenAPI/Swagger may be disabled when `ENABLE_API_DOCS=false` (VAPT / shared hosts).

### Frontend

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
```

App: http://localhost:3000

---

## Quality Checks

### Backend

```bash
cd apps/api
ruff check src
ruff format --check src
mypy src
pytest
```

### Frontend

```bash
cd apps/web
npm run lint
npm run typecheck
npm run build
```

## Development Rules

- **Backend flow:** Router → Service → Repository → Database
- **No business logic in routers**
- **No direct database access from UI**
- **Alembic migrations only** for schema changes
- **Follow DBS standards:** UUID PK, audit columns, tenant isolation, soft delete
- **Do not bypass** Workflow, Notification, or Audit engines

## Remotes

| Remote | Role |
|--------|------|
| `origin` (GitHub) | Primary — default push target |
| `gitlab` | Mirror — sync only when explicitly requested |

## License

Proprietary — Internal Use Only
