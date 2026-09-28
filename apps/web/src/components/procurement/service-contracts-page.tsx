"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { FileSignature, Pencil, Plus, RefreshCw } from "lucide-react";

import { CrmErrorBanner, CrmListPanel, CrmPage, CRM_TABLE_HEAD_ROW } from "@/components/crm/crm-ui";
import { ConfirmDialog } from "@/components/finance/journals/confirm-dialog";
import { FinanceField, FinanceSelect, FinanceTextarea } from "@/components/finance/journals/finance-form-field";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatApiError } from "@/services/api-client";
import { formatInr } from "@/services/sales-crm-service";
import {
  SERVICE_TYPE_OPTIONS,
  createServiceContract,
  listServiceContracts,
  serviceTypeLabel,
  updateServiceContract,
  type ServiceRateContract,
} from "@/services/service-projects-service";

type Draft = {
  vendor_name: string;
  service_type: string;
  region: string;
  rate_per_visit: string;
  valid_from: string;
  valid_to: string;
  remarks: string;
  status: "active" | "inactive";
};

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function emptyDraft(): Draft {
  return {
    vendor_name: "",
    service_type: "site_visit",
    region: "",
    rate_per_visit: "",
    valid_from: today(),
    valid_to: "",
    remarks: "",
    status: "active",
  };
}

function draftFrom(row: ServiceRateContract): Draft {
  return {
    vendor_name: row.vendor_name,
    service_type: row.service_type,
    region: row.region ?? "",
    rate_per_visit: String(Number(row.rate_per_visit)),
    valid_from: row.valid_from,
    valid_to: row.valid_to ?? "",
    remarks: row.remarks ?? "",
    status: row.status,
  };
}

/**
 * Per-visit rate contracts with freelancers / field partners. OVFs price
 * service POs off these (visits x rate + consumables).
 */
export function ServiceContractsPage() {
  const [rows, setRows] = useState<ServiceRateContract[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [editing, setEditing] = useState<ServiceRateContract | "new" | null>(null);
  const [draft, setDraft] = useState<Draft>(emptyDraft);
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRows(await listServiceContracts());
    } catch (err) {
      setError(formatApiError(err, "Failed to load rate contracts"));
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
    return rows.filter(
      (r) =>
        (!typeFilter || r.service_type === typeFilter) &&
        (!q || `${r.contract_code} ${r.vendor_name} ${r.region ?? ""}`.toLowerCase().includes(q)),
    );
  }, [rows, query, typeFilter]);

  function openEditor(row: ServiceRateContract | "new") {
    setDraft(row === "new" ? emptyDraft() : draftFrom(row));
    setFormError(null);
    setEditing(row);
  }

  async function save() {
    const rate = Number(draft.rate_per_visit);
    if (!draft.vendor_name.trim()) return setFormError("Vendor / freelancer name is required.");
    if (!(rate > 0)) return setFormError("Rate per visit must be more than zero.");
    if (draft.valid_to && draft.valid_to < draft.valid_from) return setFormError("Valid-to cannot be before valid-from.");
    setBusy(true);
    setFormError(null);
    const body = {
      vendor_name: draft.vendor_name.trim(),
      service_type: draft.service_type,
      region: draft.region.trim() || null,
      rate_per_visit: rate,
      valid_from: draft.valid_from,
      valid_to: draft.valid_to || null,
      remarks: draft.remarks.trim() || null,
    };
    try {
      if (editing === "new") await createServiceContract(body);
      else if (editing) await updateServiceContract(editing.id, { ...body, status: draft.status });
      setEditing(null);
      await load();
    } catch (err) {
      setFormError(formatApiError(err, "Could not save the rate contract"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <CrmPage>
      <PageHeader
        title="Service Rate Contracts"
        description="Per-visit rates agreed with field partners. OVF service plans are priced off these."
        actions={
          <div className="flex gap-2">
            <Button type="button" variant="outline" size="sm" className="cursor-pointer" onClick={() => void load()}>
              <RefreshCw className="size-3.5" /> Refresh
            </Button>
            <Button type="button" size="sm" className="cursor-pointer" onClick={() => openEditor("new")}>
              <Plus className="size-3.5" /> New rate contract
            </Button>
          </div>
        }
      />
      {error ? <CrmErrorBanner>{error}</CrmErrorBanner> : null}

      <CrmListPanel>
        <div className="flex flex-wrap items-end gap-3 border-b border-border/70 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <FileSignature className="size-4 text-muted-foreground" aria-hidden />
            <h2 className="text-base font-extrabold tracking-tight">Contracts</h2>
            <span className="text-xs text-muted-foreground">{filtered.length} shown</span>
          </div>
          <Input
            aria-label="Search rate contracts"
            placeholder="Search code, partner, region"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-9 w-64 text-[13px]"
          />
          <FinanceSelect
            aria-label="Filter by service type"
            className="h-9 w-44 text-[13px]"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="">All service types</option>
            {SERVICE_TYPE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </FinanceSelect>
        </div>
        <div className="erp-scroll overflow-x-auto">
          <table className="w-full min-w-[860px] text-left text-sm">
            <thead>
              <tr className={CRM_TABLE_HEAD_ROW}>
                <th className="px-3 py-2.5">Code</th>
                <th className="px-3 py-2.5">Partner</th>
                <th className="px-3 py-2.5">Service</th>
                <th className="px-3 py-2.5">Region</th>
                <th className="px-3 py-2.5 text-right">Rate / visit</th>
                <th className="px-3 py-2.5">Valid</th>
                <th className="px-3 py-2.5">Status</th>
                <th className="w-12 px-3 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-10 text-center text-muted-foreground">Loading rate contracts…</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-10 text-center text-muted-foreground">
                    {rows.length === 0 ? "No rate contracts yet - add the first one." : "No contracts match these filters."}
                  </td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id} className="border-b border-border/50 transition-colors duration-150 last:border-0 hover:bg-accent/30">
                    <td className="px-3 py-2 font-mono text-xs">{r.contract_code}</td>
                    <td className="px-3 py-2 font-medium">{r.vendor_name}</td>
                    <td className="px-3 py-2">{serviceTypeLabel(r.service_type)}</td>
                    <td className="px-3 py-2">{r.region ?? "-"}</td>
                    <td className="px-3 py-2 text-right tabular-nums">{formatInr(r.rate_per_visit)}</td>
                    <td className="px-3 py-2 text-xs tabular-nums">
                      {r.valid_from} → {r.valid_to ?? "open"}
                    </td>
                    <td className="px-3 py-2">
                      <Badge
                        className={`rounded-full border-transparent px-2.5 py-0.5 text-[11px] font-semibold ${r.status === "active"
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200"
                            : "bg-muted text-muted-foreground"
                          }`}
                      >
                        {r.status === "active" ? "Active" : "Inactive"}
                      </Badge>
                    </td>
                    <td className="px-3 py-2">
                      <Button
                        type="button"
                        size="icon-sm"
                        variant="ghost"
                        className="cursor-pointer"
                        aria-label={`Edit ${r.contract_code}`}
                        onClick={() => openEditor(r)}
                      >
                        <Pencil className="size-3.5" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CrmListPanel>

      <ConfirmDialog
        open={editing !== null}
        title={editing === "new" ? "New rate contract" : `Edit ${editing?.contract_code ?? ""}`}
        confirmLabel={editing === "new" ? "Create" : "Save"}
        busy={busy}
        contentClassName="sm:max-w-lg"
        onCancel={() => !busy && setEditing(null)}
        onConfirm={() => void save()}
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <FinanceField label="Partner / freelancer *" className="sm:col-span-2">
            <Input
              value={draft.vendor_name}
              onChange={(e) => setDraft((d) => ({ ...d, vendor_name: e.target.value }))}
              placeholder="Ravi Field Services"
              className="h-9 text-[13px]"
            />
          </FinanceField>
          <FinanceField label="Service type *">
            <FinanceSelect
              className="h-9 text-[13px]"
              value={draft.service_type}
              onChange={(e) => setDraft((d) => ({ ...d, service_type: e.target.value }))}
            >
              {SERVICE_TYPE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </FinanceSelect>
          </FinanceField>
          <FinanceField label="Rate per visit (₹) *">
            <Input
              type="number"
              min="0"
              step="0.01"
              inputMode="decimal"
              value={draft.rate_per_visit}
              onChange={(e) => setDraft((d) => ({ ...d, rate_per_visit: e.target.value }))}
              className="h-9 text-[13px] tabular-nums"
            />
          </FinanceField>
          <FinanceField label="Region / circle">
            <Input
              value={draft.region}
              onChange={(e) => setDraft((d) => ({ ...d, region: e.target.value }))}
              placeholder="North, Mumbai…"
              className="h-9 text-[13px]"
            />
          </FinanceField>
          {editing !== "new" ? (
            <FinanceField label="Status">
              <FinanceSelect
                className="h-9 text-[13px]"
                value={draft.status}
                onChange={(e) => setDraft((d) => ({ ...d, status: e.target.value as Draft["status"] }))}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </FinanceSelect>
            </FinanceField>
          ) : (
            <div className="hidden sm:block" />
          )}
          <FinanceField label="Valid from *">
            <Input
              type="date"
              value={draft.valid_from}
              onChange={(e) => setDraft((d) => ({ ...d, valid_from: e.target.value }))}
              className="h-9 text-[13px]"
            />
          </FinanceField>
          <FinanceField label="Valid to" hint="Leave empty for open-ended">
            <Input
              type="date"
              value={draft.valid_to}
              onChange={(e) => setDraft((d) => ({ ...d, valid_to: e.target.value }))}
              className="h-9 text-[13px]"
            />
          </FinanceField>
          <FinanceField label="Remarks" className="sm:col-span-2">
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
