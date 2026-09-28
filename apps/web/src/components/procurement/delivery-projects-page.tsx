"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FolderKanban, Plus, RefreshCw, TriangleAlert } from "lucide-react";

import { CrmErrorBanner, CrmListPanel, CrmPage, CRM_TABLE_HEAD_ROW } from "@/components/crm/crm-ui";
import { ConfirmDialog } from "@/components/finance/journals/confirm-dialog";
import { FinanceField, FinanceSelect, FinanceTextarea } from "@/components/finance/journals/finance-form-field";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatApiError } from "@/services/api-client";
import { listOpportunities, type Opportunity } from "@/services/sales-crm-service";
import {
  createDeliveryProject,
  listDeliveryProjects,
  type DeliveryProject,
} from "@/services/service-projects-service";

const PROJECT_STATUS_CLASS: Record<DeliveryProject["status"], string> = {
  active: "bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-200",
  on_hold: "bg-amber-100 text-amber-900 dark:bg-amber-900/50 dark:text-amber-100",
  completed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200",
};

const PROJECT_STATUS_LABEL: Record<DeliveryProject["status"], string> = {
  active: "Active",
  on_hold: "On hold",
  completed: "Completed",
};

export function ProgressBar({ done, total }: { done: number; total: number }) {
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-1.5 w-24 overflow-hidden rounded-full bg-muted"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${done} of ${total} sites delivered`}
      >
        <div className="h-full rounded-full bg-primary transition-[width] duration-300" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs tabular-nums text-muted-foreground">
        {done}/{total}
      </span>
    </div>
  );
}

/** Multi-site rollouts: one project per customer deal, one row per site / circle. */
export function DeliveryProjectsPage() {
  const router = useRouter();
  const [rows, setRows] = useState<DeliveryProject[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [creating, setCreating] = useState(false);
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [draft, setDraft] = useState({ name: "", opportunity_id: "", customer_name: "", remarks: "" });

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRows(await listDeliveryProjects());
    } catch (err) {
      setError(formatApiError(err, "Failed to load delivery projects"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) =>
      `${r.project_code} ${r.name} ${r.customer_name ?? ""} ${r.circles.join(" ")}`.toLowerCase().includes(q),
    );
  }, [rows, query]);

  function openCreate() {
    setDraft({ name: "", opportunity_id: "", customer_name: "", remarks: "" });
    setFormError(null);
    setCreating(true);
    if (opportunities.length === 0) {
      void listOpportunities()
        .then(setOpportunities)
        .catch(() => setOpportunities([]));
    }
  }

  async function create() {
    if (!draft.name.trim()) return setFormError("Give the project a name.");
    setBusy(true);
    setFormError(null);
    try {
      const project = await createDeliveryProject({
        name: draft.name.trim(),
        opportunity_id: draft.opportunity_id || null,
        customer_name: draft.customer_name.trim() || null,
        remarks: draft.remarks.trim() || null,
      });
      setCreating(false);
      router.push(`/procurement/delivery-projects/${project.id}`);
    } catch (err) {
      setFormError(formatApiError(err, "Could not create the project"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <CrmPage>
      <PageHeader
        title="Delivery Projects"
        description="Multi-site rollouts tracked per circle and site, with an Excel tracker and a customer link."
        actions={
          <div className="flex gap-2">
            <Button type="button" variant="outline" size="sm" className="cursor-pointer" onClick={() => void load()}>
              <RefreshCw className="size-3.5" /> Refresh
            </Button>
            <Button type="button" size="sm" className="cursor-pointer" onClick={openCreate}>
              <Plus className="size-3.5" /> New project
            </Button>
          </div>
        }
      />
      {error ? <CrmErrorBanner>{error}</CrmErrorBanner> : null}

      <CrmListPanel>
        <div className="flex flex-wrap items-end gap-3 border-b border-border/70 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <FolderKanban className="size-4 text-muted-foreground" aria-hidden />
            <h2 className="text-base font-extrabold tracking-tight">Projects</h2>
            <span className="text-xs text-muted-foreground">{filtered.length} shown</span>
          </div>
          <Input
            aria-label="Search projects"
            placeholder="Search project, customer, circle"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-9 w-72 text-[13px]"
          />
        </div>
        <div className="erp-scroll overflow-x-auto">
          <table className="w-full min-w-[880px] text-left text-sm">
            <thead>
              <tr className={CRM_TABLE_HEAD_ROW}>
                <th className="px-3 py-2.5">Project</th>
                <th className="px-3 py-2.5">Customer</th>
                <th className="px-3 py-2.5">Circles</th>
                <th className="px-3 py-2.5">Delivered</th>
                <th className="px-3 py-2.5 text-right">Delayed</th>
                <th className="px-3 py-2.5 text-right">On hold</th>
                <th className="px-3 py-2.5">Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-muted-foreground">Loading projects…</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-muted-foreground">
                    {rows.length === 0 ? "No delivery projects yet." : "No projects match your search."}
                  </td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id} className="border-b border-border/50 transition-colors duration-150 last:border-0 hover:bg-accent/30">
                    <td className="px-3 py-2">
                      <Link
                        href={`/procurement/delivery-projects/${r.id}`}
                        className="cursor-pointer rounded font-medium text-primary underline-offset-2 hover:underline focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
                      >
                        {r.name}
                      </Link>
                      <span className="block font-mono text-[11px] text-muted-foreground">{r.project_code}</span>
                    </td>
                    <td className="px-3 py-2">{r.customer_name ?? "-"}</td>
                    <td className="px-3 py-2 text-xs">
                      {r.circles.length ? r.circles.slice(0, 4).join(", ") + (r.circles.length > 4 ? ` +${r.circles.length - 4}` : "") : "-"}
                    </td>
                    <td className="px-3 py-2">
                      <ProgressBar done={r.delivered_count + r.installed_count} total={r.site_count} />
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {r.delayed_count > 0 ? (
                        <span className="inline-flex items-center gap-1 font-semibold text-red-700 dark:text-red-400">
                          <TriangleAlert className="size-3.5" aria-hidden /> {r.delayed_count}
                        </span>
                      ) : (
                        0
                      )}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums">{r.on_hold_count}</td>
                    <td className="px-3 py-2">
                      <Badge className={`rounded-full border-transparent px-2.5 py-0.5 text-[11px] font-semibold ${PROJECT_STATUS_CLASS[r.status]}`}>
                        {PROJECT_STATUS_LABEL[r.status]}
                      </Badge>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CrmListPanel>

      <ConfirmDialog
        open={creating}
        title="New delivery project"
        description="Link the deal to pull one site per OVF automatically. You can also add sites or upload the Excel tracker later."
        confirmLabel="Create project"
        busy={busy}
        contentClassName="sm:max-w-lg"
        onCancel={() => !busy && setCreating(false)}
        onConfirm={() => void create()}
      >
        <div className="grid gap-3">
          <FinanceField label="Project name *">
            <Input
              value={draft.name}
              onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))}
              placeholder="Airtel - 120 site router rollout"
              className="h-9 text-[13px]"
            />
          </FinanceField>
          <FinanceField label="Deal (opportunity)" hint="Optional - the customer name is taken from the deal">
            <FinanceSelect
              className="h-9 text-[13px]"
              value={draft.opportunity_id}
              onChange={(e) => setDraft((d) => ({ ...d, opportunity_id: e.target.value }))}
            >
              <option value="">No linked deal</option>
              {opportunities.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.opportunity_code} · {o.opportunity_name}
                </option>
              ))}
            </FinanceSelect>
          </FinanceField>
          {!draft.opportunity_id ? (
            <FinanceField label="Customer name">
              <Input
                value={draft.customer_name}
                onChange={(e) => setDraft((d) => ({ ...d, customer_name: e.target.value }))}
                className="h-9 text-[13px]"
              />
            </FinanceField>
          ) : null}
          <FinanceField label="Remarks">
            <FinanceTextarea
              value={draft.remarks}
              onChange={(e) => setDraft((d) => ({ ...d, remarks: e.target.value }))}
              className="min-h-[64px] text-[13px]"
            />
          </FinanceField>
        </div>
        {formError ? <p className="mt-3 text-xs text-destructive">{formError}</p> : null}
      </ConfirmDialog>
    </CrmPage>
  );
}
