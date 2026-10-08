"""Backup → restore drill: proves the current database can be restored, and measures RPO/RTO.

Dumps the live database (custom format), restores it into a scratch database on the
same server, verifies the alembic head and every table's row count match, then drops
the scratch database. Exits non-zero on any mismatch.

    python scripts/restore_drill.py --container erp-postgres
    python scripts/restore_drill.py                      # local pg_dump/pg_restore on PATH
    python scripts/restore_drill.py --backup-dir ../../backups   # also report backup age (RPO)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import create_engine, text  # noqa: E402

from core.config import settings  # noqa: E402

_DUMP_PATH = "/tmp/erp_restore_drill.dump"


def _pg_cmd(args: argparse.Namespace, password: str, *cmd: str) -> list[str]:
    if args.container:
        return ["docker", "exec", "-e", f"PGPASSWORD={password}", args.container, *cmd]
    return list(cmd)


def _run(command: list[str], *, env_password: str | None = None) -> None:
    env = None
    if env_password is not None:
        import os

        env = {**os.environ, "PGPASSWORD": env_password}
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(command[:4])}... failed: {result.stderr.strip()[:500]}")


def _table_counts(url: str) -> dict[str, int]:
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            tables = conn.execute(
                text(
                    "SELECT table_schema, table_name FROM information_schema.tables "
                    "WHERE table_type = 'BASE TABLE' "
                    "AND table_schema NOT IN ('pg_catalog', 'information_schema')"
                )
            ).all()
            return {
                f"{schema}.{name}": int(conn.execute(text(f'SELECT count(*) FROM "{schema}"."{name}"')).scalar())
                for schema, name in tables
            }
    finally:
        engine.dispose()


def _alembic_head(url: str) -> str | None:
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    finally:
        engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--container", help="Docker container running Postgres (uses docker exec)")
    parser.add_argument("--scratch-db", default="erp_restore_drill")
    parser.add_argument("--backup-dir", help="Directory of scheduled backups, to report RPO")
    parser.add_argument("--keep", action="store_true", help="Keep the scratch database afterwards")
    args = parser.parse_args()

    source_url = settings.database_url
    parsed = urlparse(source_url.replace("+psycopg", "").replace("+psycopg2", ""))
    source_db = parsed.path.lstrip("/")
    user, password = parsed.username or "postgres", parsed.password or ""
    host = "localhost" if args.container else (parsed.hostname or "localhost")
    port = str(5432 if args.container else (parsed.port or 5432))
    if "drill" not in args.scratch_db or args.scratch_db == source_db:
        print("Refusing: scratch database name must contain 'drill' and differ from the source", file=sys.stderr)
        return 2

    conn_args = ["-h", host, "-p", port, "-U", user]
    local_pw = None if args.container else password
    report: dict = {"source_db": source_db, "scratch_db": args.scratch_db, "started_at": datetime.now(timezone.utc).isoformat()}

    t0 = time.perf_counter()
    _run(_pg_cmd(args, password, "pg_dump", *conn_args, "-d", source_db, "-Fc", "-f", _DUMP_PATH), env_password=local_pw)
    report["dump_seconds"] = round(time.perf_counter() - t0, 2)

    admin = [*conn_args, "-d", "postgres"]
    _run(_pg_cmd(args, password, "psql", *admin, "-c", f'DROP DATABASE IF EXISTS "{args.scratch_db}"'), env_password=local_pw)
    _run(_pg_cmd(args, password, "psql", *admin, "-c", f'CREATE DATABASE "{args.scratch_db}"'), env_password=local_pw)

    t1 = time.perf_counter()
    _run(
        _pg_cmd(args, password, "pg_restore", *conn_args, "-d", args.scratch_db, "--no-owner", "--jobs", "4", _DUMP_PATH),
        env_password=local_pw,
    )
    report["restore_seconds_rto"] = round(time.perf_counter() - t1, 2)

    scratch_url = source_url.rsplit("/", 1)[0] + f"/{args.scratch_db}"
    try:
        source_head, restored_head = _alembic_head(source_url), _alembic_head(scratch_url)
        source_counts, restored_counts = _table_counts(source_url), _table_counts(scratch_url)
    finally:
        if not args.keep:
            _run(_pg_cmd(args, password, "psql", *admin, "-c", f'DROP DATABASE IF EXISTS "{args.scratch_db}"'), env_password=local_pw)

    mismatches = {
        table: {"source": n, "restored": restored_counts.get(table)}
        for table, n in source_counts.items()
        if restored_counts.get(table) != n
    }
    report.update(
        alembic_head={"source": source_head, "restored": restored_head},
        tables_checked=len(source_counts),
        rows_checked=sum(source_counts.values()),
        mismatches=mismatches,
    )
    if args.backup_dir:
        backups = sorted(Path(args.backup_dir).glob("*"), key=lambda p: p.stat().st_mtime)
        if backups:
            newest = backups[-1]
            age_h = (time.time() - newest.stat().st_mtime) / 3600
            report["latest_backup"] = {"file": newest.name, "age_hours_rpo": round(age_h, 1)}

    ok = source_head == restored_head and not mismatches
    report["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(report, indent=2, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
