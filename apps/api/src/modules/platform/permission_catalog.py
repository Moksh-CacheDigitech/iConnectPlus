"""Single permission catalog assembled from every module's ``permissions.py``."""

from __future__ import annotations

import importlib
from pathlib import Path

_MODULES_ROOT = Path(__file__).resolve().parents[1]


def all_permission_entries() -> list[tuple[str, str, str, str]]:
    """(permission_code, resource, action, module) across all modules, de-duplicated."""
    seen: dict[str, tuple[str, str, str, str]] = {}
    for path in sorted(_MODULES_ROOT.glob("*/permissions.py")):
        mod = importlib.import_module(f"modules.{path.parent.name}.permissions")
        for name, value in vars(mod).items():
            if not (name.isupper() and isinstance(value, list)):
                continue
            for item in value:
                if isinstance(item, tuple) and len(item) == 4 and isinstance(item[0], str):
                    seen.setdefault(item[0], item)
    return list(seen.values())


def all_permission_codes() -> set[str]:
    return {entry[0] for entry in all_permission_entries()}
