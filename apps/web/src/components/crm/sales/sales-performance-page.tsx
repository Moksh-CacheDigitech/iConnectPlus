"use client";

import { useCallback, useEffect, useState } from "react";
import { RefreshCw, TrendingDown } from "lucide-react";

import { CrmErrorBanner, CrmListPanel, CrmPage, CRM_TABLE_HEAD_ROW } from "@/components/crm/crm-ui";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ApiClientError } from "@/services/api-client";
import { getSalesPerformance, type SalesPerformanceRow } from "@/services/crm-deal-controls-service";
import { formatInr } from "@/services/sales-crm-service";

/**
 * Per salesperson: margin Management approved vs the margin after delayed
 * payments, stock held for their deals, and execution expenses. Feeds the
 * quarterly incentive review and F&F.
 */
export function SalesPerformancePage() {
  const [rows, setRows] = useState<SalesPerformanceRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRows(await getSalesPerformance());
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load sales performance");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  return (
    <CrmPage>
      <PageHeader
        title="Sales Performance - Live OVF Margin"
        actions={
          <Button type="button" variant="outline" size="sm" className="cursor-pointer" onClick={() => void load()}>
            <RefreshCw className="size-3.5" /> Refresh
          </Button>
        }
      />
      <p className="text-xs text-muted-foreground">
        Margin erosion = approved OVF margin minus today&apos;s margin. It grows with 1% a month on unpaid
        receivables past due, 1% a month on stock bought for the deal and still unsold, and approved
        execution expenses.
      </p>
      {error ? <CrmErrorBanner>{error}</CrmErrorBanner> : null}
      <CrmListPanel>
        <div className="flex items-center gap-2.5 border-b border-border/70 px-4 py-3">
          <TrendingDown className="size-4 text-muted-foreground" />
          <h2 className="text-base font-extrabold tracking-tight">Salespeople</h2>
        </div>
        <div className="erp-scroll overflow-x-auto">
          <table className="w-full min-w-[1000px] text-left text-sm">
            <thead>
              <tr className={CRM_TABLE_HEAD_ROW}>
                <th className="px-4 py-2.5">Salesperson</th>
                <th className="px-4 py-2.5 text-right">OVFs (open)</th>
                <th className="px-4 py-2.5 text-right">Approved margin</th>
                <th className="px-4 py-2.5 text-right">Live margin</th>
                <th className="px-4 py-2.5 text-right">Erosion</th>
                <th className="px-4 py-2.5 text-right">Cost of delay</th>
                <th className="px-4 py-2.5 text-right">Stock holding</th>
                <th className="px-4 py-2.5 text-right">Extra expenses</th>
                <th className="px-4 py-2.5 text-right">Outstanding</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={9} className="px-4 py-10 text-center text-muted-foreground">Loading…</td>
                </tr>
              ) : rows.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-10 text-center text-muted-foreground">No approved OVFs yet.</td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={row.owner_employee_id ?? "none"} className="border-b border-border/50 last:border-0 hover:bg-accent/30">
                    <td className="px-4 py-2.5 font-medium">{row.owner_name ?? "-"}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">
                      {row.ovf_count} ({row.open_ovf_count})
                    </td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{formatInr(row.margin_at_approval)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{formatInr(row.live_margin)}</td>
                    <td
                      className={`px-4 py-2.5 text-right font-semibold tabular-nums ${Number(row.margin_erosion) > 0 ? "text-red-700 dark:text-red-400" : ""}`}
                    >
                      {formatInr(row.margin_erosion)}
                    </td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{formatInr(row.overdue_finance_cost)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{formatInr(row.holding_cost)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{formatInr(row.execution_expenses)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums">{formatInr(row.outstanding_receivable)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CrmListPanel>
    </CrmPage>
  );
}
