"""Alembic-only stubs for removed module (import graph).

Historical migrations still import these symbols. Tables/permissions
already exist in deployed DBs; upgrade() is not re-run for stamped revs.
"""

class IntEventDefinition:
    """Stub for alembic historical import."""

    class __table__:
        @staticmethod
        def create(bind=None, checkfirst=True):
            return None

