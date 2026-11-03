"use client";

import { useCallback, useEffect, useState } from "react";
import { Gauge, RefreshCw, Users } from "lucide-react";

import { FinanceKpiCard } from "@/components/finance/finance-kpi-card";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { loadWorkloadOverview, type WorkloadOverview } from "@/services/marketing-service";

const EMPTY: WorkloadOverview = {
  company: {
    active_tasks: 0,
    pending_reviews: 0,
    delayed_tasks: 0,
    workload_score: 0,
    utilization_pct: 0,
  },
  me: {
    active_tasks: 0,
    pending_reviews: 0,
    delayed_tasks: 0,
    workload_score: 0,
    utilization_pct: 0,
    completed_tasks: 0,
    actual_hours: 0,
    checklist_pct: 0,
    duration_hours: 0,
  },
  people: [],
  overloaded: [],
  underutilized: [],
  campaign_health: [],
  team_checklist: [],
};

export function MarketingWorkloadBoard() {
  const [data, setData] = useState<WorkloadOverview>(EMPTY);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await loadWorkloadOverview());
    } catch {
      setData(EMPTY);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Workload & resources"
        description="Capacity, utilization, overload, and reassignment signals across the marketing team."
        actions={
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="cursor-pointer transition-colors duration-200"
            onClick={() => void load()}
          >
            <RefreshCw className="size-3.5" aria-hidden />
            Refresh
          </Button>
        }
      />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <FinanceKpiCard
          label="Overloaded"
          value={loading ? "-" : String(data.overloaded.length)}
          tone={data.overloaded.length ? "warning" : "success"}
          icon={Users}
        />
        <FinanceKpiCard
          label="Underutilized"
          value={loading ? "-" : String(data.underutilized.length)}
          icon={Gauge}
        />
        <FinanceKpiCard
          label="My utilization"
          value={loading ? "-" : `${data.me.utilization_pct}%`}
          hint={`${data.me.active_tasks} active tasks`}
          icon={Gauge}
        />
      </div>
      <section className="space-y-2">
        <h2 className="text-sm font-semibold tracking-tight">Team checklist (head view)</h2>
        <p className="text-[11px] text-muted-foreground">
          Vishakha view — Ansh / Piyush / Harshita progress, duration logged, and delayed work.
        </p>
        <div className="overflow-x-auto rounded-md border border-border/70">
          <table className="w-full min-w-[720px] text-left text-xs">
            <thead className="border-b border-border/60 bg-muted/40 text-[11px] uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Person</th>
                <th className="px-3 py-2 font-medium">Checklist %</th>
                <th className="px-3 py-2 font-medium">Done / Active</th>
                <th className="px-3 py-2 font-medium">Duration (hrs)</th>
                <th className="px-3 py-2 font-medium">Delayed</th>
                <th className="px-3 py-2 font-medium">Balance</th>
              </tr>
            </thead>
            <tbody>
              {(data.team_checklist?.length ? data.team_checklist : data.people).length === 0 ? (
                <tr>
                  <td className="px-3 py-4 text-muted-foreground" colSpan={6}>
                    No assigned work yet.
                  </td>
                </tr>
              ) : (
                (data.team_checklist?.length
                  ? data.team_checklist.map((row) => ({
                      user_id: row.user_id,
                      display_name: row.display_name,
                      checklist_pct: row.checklist_pct,
                      completed: row.completed,
                      active: row.active,
                      duration_hours: row.duration_hours,
                      delayed: row.delayed,
                      reassignment:
                        data.people.find((p) => p.user_id === row.user_id)?.reassignment ||
                        "balanced",
                    }))
                  : data.people.map((row) => ({
                      user_id: row.user_id,
                      display_name: row.display_name || row.user_id.slice(0, 8),
                      checklist_pct: row.checklist_pct || 0,
                      completed: row.completed_tasks || 0,
                      active: row.active_tasks,
                      duration_hours: row.duration_hours || 0,
                      delayed: row.delayed_tasks || 0,
                      reassignment: row.reassignment,
                    }))
                ).map((row) => (
                  <tr key={row.user_id} className="border-b border-border/40 last:border-0">
                    <td className="px-3 py-2 font-medium text-foreground">{row.display_name}</td>
                    <td className="px-3 py-2 font-mono tabular-nums">{row.checklist_pct}%</td>
                    <td className="px-3 py-2 font-mono tabular-nums">
                      {row.completed} / {row.active}
                    </td>
                    <td className="px-3 py-2 font-mono tabular-nums">{row.duration_hours}</td>
                    <td className="px-3 py-2 font-mono tabular-nums">{row.delayed}</td>
                    <td className="px-3 py-2">
                      <Badge variant="secondary" className="text-[10px] uppercase">
                        {row.reassignment}
                      </Badge>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
