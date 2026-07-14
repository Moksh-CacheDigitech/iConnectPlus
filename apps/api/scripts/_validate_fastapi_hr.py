"""Collect FastAPI validation metrics for Sprint 11."""
from __future__ import annotations

import json
import urllib.request

BASE = "http://127.0.0.1:8010"


def get(path: str) -> tuple[int, object]:
    with urllib.request.urlopen(BASE + path, timeout=30) as resp:
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "")
        data: object
        if "json" in ctype:
            data = json.loads(body.decode())
        else:
            data = body.decode()[:200]
        return resp.status, data


def main() -> None:
    docs_status, _ = get("/docs")
    openapi_status, openapi = get("/openapi.json")
    assert isinstance(openapi, dict)
    paths = openapi.get("paths", {})
    hr_paths = [p for p in paths if "/hr" in p]

    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from main import app

    routes = [r for r in app.routes if hasattr(r, "methods") and hasattr(r, "path")]
    hr_routes = [r for r in routes if "/hr" in getattr(r, "path", "")]
    print("docs_status", docs_status)
    print("openapi_status", openapi_status)
    print("total_routes", len(routes))
    print("openapi_paths", len(paths))
    print("hr_routes", len(hr_routes))
    print("hr_openapi_paths", len(hr_paths))
    print("hr_sample", sorted(hr_paths)[:5])


if __name__ == "__main__":
    main()
