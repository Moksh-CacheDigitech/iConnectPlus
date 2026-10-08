"""Platform module — cross-domain ports, outbox, adapters, shared helpers.

Import concrete helpers from submodules to avoid circular imports with Celery:

    from modules.platform.container import get_platform_ports
"""

__all__ = ["PlatformPorts", "get_platform_ports"]


def __getattr__(name: str):
    if name in {"PlatformPorts", "get_platform_ports"}:
        from modules.platform.container import PlatformPorts, get_platform_ports

        return PlatformPorts if name == "PlatformPorts" else get_platform_ports
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
