"""Critical-path SLO definitions (latency budgets in ms) and live status."""

from __future__ import annotations

from dataclasses import dataclass

from modules.platform.observability import path_samples


@dataclass(frozen=True, slots=True)
class PathSLO:
    path_key: str
    description: str
    p95_latency_ms: int
    error_budget_pct: float


CRITICAL_PATH_SLOS: tuple[PathSLO, ...] = (
    PathSLO("auth.login", "User login", 800, 1.0),
    PathSLO("procurement.pr_to_po", "PR convert to PO", 2000, 1.0),
    PathSLO("procurement.grn_post", "GRN receive + stock", 2500, 1.0),
    PathSLO("finance.invoice_post", "Invoice / journal post", 2000, 0.5),
    PathSLO("payroll.run", "Payroll run calculate", 15000, 1.0),
    PathSLO("sales.invoice_post", "Sales invoice post", 2500, 0.5),
    PathSLO("inventory.transfer", "Inventory transfer post", 2500, 1.0),
    PathSLO("outbox.drain", "Platform outbox drain batch", 5000, 2.0),
)


def slo_alert_thresholds() -> list[dict]:
    """Machine-readable alert budgets for dashboards / Prometheus rules."""
    return [
        {
            "path_key": s.path_key,
            "p95_latency_ms": s.p95_latency_ms,
            "error_budget_pct": s.error_budget_pct,
            "alert_on_p95_breach": True,
            "alert_on_error_budget_burn": True,
        }
        for s in CRITICAL_PATH_SLOS
    ]


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))]


def slo_status() -> list[dict]:
    """Live p95 / error rate / budget burn per path from this process's sample window.

    ``budget_burn`` > 1.0 means errors exceed the allowed budget for the window.
    """
    out: list[dict] = []
    for slo in CRITICAL_PATH_SLOS:
        samples = path_samples(slo.path_key)
        if not samples:
            out.append({"path_key": slo.path_key, "samples": 0, "status": "no_data"})
            continue
        latencies = [lat for lat, _ in samples]
        error_pct = 100.0 * sum(1 for _, ok in samples if not ok) / len(samples)
        p95 = _p95(latencies)
        burn = error_pct / slo.error_budget_pct if slo.error_budget_pct else 0.0
        breached = p95 > slo.p95_latency_ms or burn > 1.0
        out.append(
            {
                "path_key": slo.path_key,
                "samples": len(samples),
                "p95_latency_ms": round(p95, 2),
                "p95_budget_ms": slo.p95_latency_ms,
                "error_pct": round(error_pct, 3),
                "error_budget_pct": slo.error_budget_pct,
                "budget_burn": round(burn, 3),
                "status": "breached" if breached else "ok",
            }
        )
    return out


def prometheus_text() -> str:
    lines = [
        "# HELP erp_slo_p95_latency_ms Rolling p95 latency per critical path (per process).",
        "# TYPE erp_slo_p95_latency_ms gauge",
        "# HELP erp_slo_error_budget_burn Error rate divided by error budget (per process).",
        "# TYPE erp_slo_error_budget_burn gauge",
        "# HELP erp_slo_samples Samples in the rolling window (per process).",
        "# TYPE erp_slo_samples gauge",
    ]
    for row in slo_status():
        label = f'{{path="{row["path_key"]}"}}'
        lines.append(f"erp_slo_samples{label} {row['samples']}")
        if row["samples"]:
            lines.append(f"erp_slo_p95_latency_ms{label} {row['p95_latency_ms']}")
            lines.append(f"erp_slo_error_budget_burn{label} {row['budget_burn']}")
    return "\n".join(lines) + "\n"
