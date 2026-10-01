"""Unit tests for VM → local Docker infrastructure fallback."""

from __future__ import annotations

from types import SimpleNamespace

import core.infra_resolve as infra_resolve


def _settings(**overrides: object) -> SimpleNamespace:
    base = {
        "infra_fallback_enabled": True,
        "database_url": "postgresql+psycopg://erp-postgres:erp-postgres@172.16.200.30:5433/erp",
        "database_url_fallback": "postgresql+psycopg://erp-postgres:erp-postgres@localhost:5433/erp",
        "redis_url": "redis://172.16.200.30:6379/0",
        "redis_url_fallback": "redis://localhost:6379/0",
        "celery_broker_url": "amqp://erp:erp_dev_password@172.16.200.30:5672//",
        "celery_broker_url_fallback": "amqp://erp:erp_dev_password@localhost:5672//",
        "celery_result_backend": "redis://172.16.200.30:6379/1",
        "celery_result_backend_fallback": "redis://localhost:6379/1",
        "s3_endpoint_url": "http://172.16.200.30:9000",
        "s3_endpoint_url_fallback": "http://localhost:9000",
        "opensearch_url": "http://172.16.200.30:9200",
        "opensearch_url_fallback": "http://localhost:9200",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _reset_module_state() -> None:
    infra_resolve.ACTIVE_INFRA_SOURCE = "primary"
    infra_resolve._PRIMARY_URLS.clear()


def test_keeps_vm_primary_when_reachable(monkeypatch) -> None:
    _reset_module_state()
    monkeypatch.setattr(infra_resolve, "primary_infra_reachable", lambda _s, timeout=2.0: True)
    settings = _settings()

    source = infra_resolve.apply_infra_fallback(settings)

    assert source == "primary"
    assert settings.database_url.startswith("postgresql+psycopg://erp-postgres:erp-postgres@172.16.200.30")
    assert settings.redis_url == "redis://172.16.200.30:6379/0"
    assert settings.s3_endpoint_url == "http://172.16.200.30:9000"


def test_switches_to_local_fallback_when_vm_down(monkeypatch) -> None:
    _reset_module_state()
    monkeypatch.setattr(infra_resolve, "primary_infra_reachable", lambda _s, timeout=2.0: False)
    settings = _settings()

    source = infra_resolve.apply_infra_fallback(settings)

    assert source == "fallback"
    assert settings.database_url.endswith("@localhost:5433/erp")
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.celery_broker_url.endswith("@localhost:5672//")
    assert settings.s3_endpoint_url == "http://localhost:9000"
    assert settings.opensearch_url == "http://localhost:9200"


def test_resyncs_to_vm_when_primary_returns(monkeypatch) -> None:
    _reset_module_state()
    settings = _settings()

    monkeypatch.setattr(infra_resolve, "primary_infra_reachable", lambda _s, timeout=2.0: False)
    assert infra_resolve.apply_infra_fallback(settings) == "fallback"
    assert "localhost" in settings.database_url

    monkeypatch.setattr(infra_resolve, "primary_infra_reachable", lambda _s, timeout=2.0: True)
    assert infra_resolve.apply_infra_fallback(settings) == "primary"
    assert "172.16.200.30" in settings.database_url
    assert settings.redis_url == "redis://172.16.200.30:6379/0"


def test_disabled_flag_keeps_primary(monkeypatch) -> None:
    _reset_module_state()
    monkeypatch.setattr(infra_resolve, "primary_infra_reachable", lambda _s, timeout=2.0: False)
    settings = _settings(infra_fallback_enabled=False)

    source = infra_resolve.apply_infra_fallback(settings)

    assert source == "primary"
    assert "172.16.200.30" in settings.database_url
