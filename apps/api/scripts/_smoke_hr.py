"""Quick smoke checks for Sprint 11 HR (not full validation)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    versions = ROOT / "alembic" / "versions"
    overs = []
    for p in sorted(versions.glob("01*.py")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r'revision:\s*str\s*=\s*"([^"]+)"', text)
        if not m:
            continue
        rev = m.group(1)
        if rev.startswith(("0157", "0158", "0159")) or rev.startswith(("016", "017")):
            overs.append((rev, len(rev), len(rev) > 32))
    bad = [x for x in overs if x[2]]
    print("hr revisions:", len(overs))
    print("over_32:", bad)
    print("head candidate:", overs[-1] if overs else None)

    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from modules.hr.router import hr_router
    from shared.router import api_v1_router

    paths = [getattr(r, "path", "") for r in api_v1_router.routes]
    print("hr routes:", len(hr_router.routes))
    print("api includes /hr:", any("/hr" in str(p) for p in paths))


if __name__ == "__main__":
    main()
