"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  Check,
  Copy,
  Download,
  Import,
  Link2,
  MapPin,
  Pencil,
  Plus,
  RefreshCw,
  RotateCcw,
  Trash2,
  TriangleAlert,
  Upload,
} from "lucide-react";

import { CrmErrorBanner, CrmListPanel, CrmPage, CrmSection, CRM_TABLE_HEAD_ROW } from "@/components/crm/crm-ui";
import { ConfirmDialog } from "@/components/finance/journals/confirm-dialog";
import { FinanceField, FinanceSelect, FinanceTextarea } from "@/components/finance/journals/finance-form-field";
import { PageHeader } from "@/components/layout/page-header";
import { ProgressBar } from "@/components/procurement/delivery-projects-page";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatApiError } from "@/services/api-client";
import { DELIVERY_MILESTONES } from "@/services/crm-deal-controls-service";
import { fileToBase64 } from "@/services/sales-crm-service";
import {
  SITE_STATUS_OPTIONS,
  addDeliverySite,
  deleteDeliverySite,
  downloadDeliveryTracker,
  getDeliveryProject,
  importSitesFromOpportunity,
  projectTrackingUrl,
  siteStatusLabel,
  updateDeliveryProject,
  updateDeliverySite,
  uploadDeliveryTracker,
  type DeliveryProjectDetail,
  type DeliverySite,
  type DeliverySiteInput,
  type TrackerImportResult,
} from "@/services/service-projects-service";

const STATUS_CLASS: Record<string, string> = {
  pending: "bg-muted text-muted-foreground",
  in_progress: "bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-200",
  delivered: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200",
  installed: "bg-emerald-200 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-100",
  on_hold: "bg-amber-100 text-amber-900 dark:bg-amber-900/50 dark:text-amber-100",
  cancelled: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-200",
};

type SiteDraft = Record<
  | "circle"
  | "site_code"
  | "site_name"
  | "address"
  | "state"
  | "gstin"
  | "customer_po_number"
  | "item_summary"
  | "quantity"
  | "milestone"
  | "status"
  | "expected_delivery_date"
  | "actual_delivery_date"
  | "awb_number"
  | "delay_reason"
  | "last_note",
  string
>;

function draftFrom(site?: DeliverySite): SiteDraft {
  return {
    circle: site?.circle ?? "",
    site_code: site?.site_code ?? "",
    site_name: site?.site_name ?? "",
    address: site?.address ?? "",
    state: site?.state ?? "",
    gstin: site?.gstin ?? "",
    customer_po_number: site?.customer_po_number ?? "",
    item_summary: site?.item_summary ?? "",
    quantity: site?.quantity != null ? String(Number(site.quantity)) : "",
    milestone: site?.milestone ?? "order_placed",
    status: site?.status ?? "pending",
    expected_delivery_date: site?.expected_delivery_date ?? "",
    actual_delivery_date: site?.actual_delivery_date ?? "",
    awb_number: site?.awb_number ?? "",
    delay_reason: site?.delay_reason ?? "",
    last_note: site?.last_note ?? "",
  };
}

function toInput(draft: SiteDraft, site?: DeliverySite): DeliverySiteInput {
  const text = (v: string) => v.trim() || null;
  const body: DeliverySiteInput = {
    circle: text(draft.circle),
    site_code: text(draft.site_code),
    site_name: draft.site_name.trim(),
    address: text(draft.address),
    state: text(draft.state),
    gstin: text(draft.gstin),
    customer_po_number: text(draft.customer_po_number),
    item_summary: text(draft.item_summary),
    quantity: draft.quantity.trim() ? Number(draft.quantity) : null,
    milestone: draft.milestone,
    expected_delivery_date: draft.expected_delivery_date || null,
    actual_delivery_date: draft.actual_delivery_date || null,
    awb_number: text(draft.awb_number),
    delay_reason: text(draft.delay_reason),
    last_note: text(draft.last_note),
  };
  // Status follows the milestone on the server unless the user changed it here.
  if (!site || draft.status !== site.status) body.status = draft.status;
  return body;
}

function Stat({ label, value, tone }: { label: string; value: number | string; tone?: "danger" | "warn" }) {
  return (
    <div className="rounded-xl border border-border/80 bg-card px-4 py-3 shadow-sm">
      <p className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">{label}</p>
      <p
        className={`mt-1 text-xl font-bold tabular-nums ${tone === "danger" ? "text-red-700 dark:text-red-400" : tone === "warn" ? "text-amber-700 dark:text-amber-400" : ""
          }`}
      >
        {value}
      </p>
    </div>
  );
}

export function DeliveryProjectDetailPage({ projectId }: { projectId: string }) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [project, setProject] = useState<DeliveryProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [importResult, setImportResult] = useState<TrackerImportResult | null>(null);
  const [copied, setCopied] = useState(false);

  const [query, setQuery] = useState("");
  const [circle, setCircle] = useState("");
  const [status, setStatus] = useState("");
  const [milestone, setMilestone] = useState("");
  const [delayedOnly, setDelayedOnly] = useState(false);

  const [editing, setEditing] = useState<DeliverySite | "new" | null>(null);
  const [draft, setDraft] = useState<SiteDraft>(() => draftFrom());
  const [formError, setFormError] = useState<string | null>(null);
  const [removing, setRemoving] = useState<DeliverySite | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      setProject(await getDeliveryProject(projectId));
    } catch (err) {
      setError(formatApiError(err, "Failed to load the project"));
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function run(work: () => Promise<string | void>) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const message = await work();
      await load();
      if (message) setNotice(message);
    } catch (err) {
      setError(formatApiError(err, "Request failed"));
    } finally {
      setBusy(false);
    }
  }

  const sites = useMemo(() => project?.sites ?? [], [project]);
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return sites.filter(
      (s) =>
        (!circle || (s.circle ?? "") === circle) &&
        (!status || s.status === status) &&
        (!milestone || s.milestone === milestone) &&
        (!delayedOnly || s.delayed) &&
        (!q ||
          `${s.site_code ?? ""} ${s.site_name} ${s.customer_po_number ?? ""} ${s.state ?? ""} ${s.awb_number ?? ""}`
            .toLowerCase()
            .includes(q)),
    );
  }, [sites, query, circle, status, milestone, delayedOnly]);

  function openEditor(site: DeliverySite | "new") {
    setDraft(draftFrom(site === "new" ? undefined : site));
    setFormError(null);
    setEditing(site);
  }

  async function saveSite() {
    if (!draft.site_name.trim()) return setFormError("Site name is required.");
    if (draft.quantity.trim() && Number.isNaN(Number(draft.quantity))) return setFormError("Quantity must be a number.");
    setBusy(true);
    setFormError(null);
    try {
      if (editing === "new") await addDeliverySite(projectId, toInput(draft));
      else if (editing) await updateDeliverySite(editing.id, toInput(draft, editing));
      setEditing(null);
      await load();
    } catch (err) {
      setFormError(formatApiError(err, "Could not save the site"));
    } finally {
      setBusy(false);
    }
  }

  async function onUpload(file: File | undefined) {
    if (fileRef.current) fileRef.current.value = "";
    if (!file) return;
    setImportResult(null);
    await run(async () => {
      const result = await uploadDeliveryTracker(projectId, await fileToBase64(file));
      setImportResult(result);
      return `Tracker imported: ${result.updated} updated, ${result.created} added, ${result.unchanged} unchanged.`;
    });
  }

  async function copyLink() {
    if (!project) return;
    try {
      await navigator.clipboard.writeText(projectTrackingUrl(project.tracking_token));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setError("Could not copy - select the link and copy it manually.");
    }
  }

  if (loading && !project) {
    return (
      <CrmPage>
        <div className="h-24 animate-pulse rounded-xl bg-muted/60" />
      </CrmPage>
    );
  }
  if (!project) {
    return (
      <CrmPage>
        <CrmErrorBanner>{error ?? "Project not found"}</CrmErrorBanner>
      </CrmPage>
    );
  }

  const trackingUrl = projectTrackingUrl(project.tracking_token);
  const filtersOn = Boolean(query || circle || status || milestone || delayedOnly);

  return (
    <CrmPage>
      <Link
        href="/procurement/delivery-projects"
        className="inline-flex w-fit cursor-pointer items-center gap-1 rounded text-xs font-medium text-muted-foreground transition-colors duration-150 hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
      >
        <ArrowLeft className="size-3.5" aria-hidden /> Delivery projects
      </Link>
      <PageHeader
        title={project.name}
        description={`${project.project_code}${project.customer_name ? ` · ${project.customer_name}` : ""}`}
        actions={
          <div className="flex flex-wrap gap-2">
            <FinanceSelect
              aria-label="Project status"
              className="h-8 w-32 text-xs"
              value={project.status}
              disabled={busy}
              onChange={(e) =>
                void run(async () => {
                  await updateDeliveryProject(project.id, { status: e.target.value as DeliveryProjectDetail["status"] });
                })
              }
            >
              <option value="active">Active</option>
              <option value="on_hold">On hold</option>
              <option value="completed">Completed</option>
            </FinanceSelect>
            <Button type="button" variant="outline" size="sm" className="cursor-pointer" disabled={busy} onClick={() => void run(async () => { })}>
              <RefreshCw className="size-3.5" /> Refresh
            </Button>
          </div>
        }
      />
      {error ? <CrmErrorBanner>{error}</CrmErrorBanner> : null}
      {notice ? <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400">{notice}</p> : null}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Stat label="Sites" value={project.site_count} />
        <Stat label="Delivered" value={project.delivered_count} />
        <Stat label="Installed" value={project.installed_count} />
        <Stat label="Delayed" value={project.delayed_count} tone={project.delayed_count > 0 ? "danger" : undefined} />
        <Stat label="On hold" value={project.on_hold_count} tone={project.on_hold_count > 0 ? "warn" : undefined} />
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,380px)]">
        <CrmSection title="Milestones" icon={MapPin}>
          <div className="flex flex-wrap gap-1.5">
            {DELIVERY_MILESTONES.map((m) => {
              const count = project.by_milestone[m.value] ?? 0;
              const active = milestone === m.value;
              return (
                <button
                  key={m.value}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setMilestone((cur) => (cur === m.value ? "" : m.value))}
                  className={`cursor-pointer rounded-lg border px-2.5 py-1.5 text-left text-xs transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none ${active ? "border-primary bg-primary/10 text-foreground" : "border-border/70 hover:bg-accent/40"
                    }`}
                >
                  <span className="block text-[11px] text-muted-foreground">{m.label}</span>
                  <span className="text-sm font-bold tabular-nums">{count}</span>
                </button>
              );
            })}
          </div>
          <div className="mt-3">
            <ProgressBar done={project.delivered_count + project.installed_count} total={project.site_count} />
          </div>
        </CrmSection>

        <CrmSection title="Customer tracking link" icon={Link2}>
          <p className="mb-2 text-xs text-muted-foreground">
            Customers see milestones, dates and AWB per site - never prices or vendors.
          </p>
          <div className="flex gap-2">
            <Input readOnly value={trackingUrl} aria-label="Customer tracking link" className="h-8 font-mono text-[11px]" onFocus={(e) => e.target.select()} />
            <Button type="button" size="sm" variant="outline" className="h-8 shrink-0 cursor-pointer" onClick={() => void copyLink()} disabled={!project.public_tracking_enabled}>
              {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-xs">
            <label className="inline-flex cursor-pointer items-center gap-1.5">
              <input
                type="checkbox"
                className="size-4 cursor-pointer accent-primary"
                checked={project.public_tracking_enabled}
                disabled={busy}
                onChange={(e) =>
                  void run(async () => {
                    await updateDeliveryProject(project.id, { public_tracking_enabled: e.target.checked });
                    return e.target.checked ? "Tracking link turned on." : "Tracking link turned off.";
                  })
                }
              />
              Link enabled
            </label>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              className="h-7 cursor-pointer text-xs"
              disabled={busy}
              onClick={() =>
                void run(async () => {
                  await updateDeliveryProject(project.id, { rotate_tracking_token: true });
                  return "New link generated - the old one no longer works.";
                })
              }
            >
              <RotateCcw className="size-3.5" /> New link
            </Button>
          </div>
        </CrmSection>
      </div>

      <CrmListPanel>
        <div className="flex flex-wrap items-end gap-2.5 border-b border-border/70 px-4 py-3">
          <div className="mr-1 flex items-center gap-2.5">
            <h2 className="text-base font-extrabold tracking-tight">Sites</h2>
            <span className="text-xs text-muted-foreground">
              {filtered.length} of {sites.length}
            </span>
          </div>
          <Input
            aria-label="Search sites"
            placeholder="Site, code, PO, AWB"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-8 w-52 text-[13px]"
          />
          <FinanceSelect aria-label="Filter by circle" className="h-8 w-36 text-xs" value={circle} onChange={(e) => setCircle(e.target.value)}>
            <option value="">All circles</option>
            {project.circles.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </FinanceSelect>
          <FinanceSelect aria-label="Filter by status" className="h-8 w-32 text-xs" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All statuses</option>
            {SITE_STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </FinanceSelect>
          <label className="inline-flex h-8 cursor-pointer items-center gap-1.5 text-xs">
            <input type="checkbox" className="size-4 cursor-pointer accent-primary" checked={delayedOnly} onChange={(e) => setDelayedOnly(e.target.checked)} />
            Delayed only
          </label>
          {filtersOn ? (
            <Button
              type="button"
              size="sm"
              variant="ghost"
              className="h-8 cursor-pointer text-xs"
              onClick={() => {
                setQuery("");
                setCircle("");
                setStatus("");
                setMilestone("");
                setDelayedOnly(false);
              }}
            >
              Clear
            </Button>
          ) : null}
          <div className="ml-auto flex flex-wrap gap-2">
            {project.opportunity_id ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="h-8 cursor-pointer text-xs"
                disabled={busy}
                onClick={() => void run(async () => `${await importSitesFromOpportunity(project.id)} site(s) added from the deal's OVFs.`)}
              >
                <Import className="size-3.5" /> Sites from OVFs
              </Button>
            ) : null}
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="h-8 cursor-pointer text-xs"
              disabled={busy}
              onClick={() => void run(async () => downloadDeliveryTracker(project))}
            >
              <Download className="size-3.5" /> Excel
            </Button>
            <Button type="button" size="sm" variant="outline" className="h-8 cursor-pointer text-xs" disabled={busy} onClick={() => fileRef.current?.click()}>
              <Upload className="size-3.5" /> Upload tracker
            </Button>
            <input
              ref={fileRef}
              type="file"
              accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              className="hidden"
              aria-label="Upload tracker Excel"
              onChange={(e) => void onUpload(e.target.files?.[0])}
            />
            <Button type="button" size="sm" className="h-8 cursor-pointer text-xs" disabled={busy} onClick={() => openEditor("new")}>
              <Plus className="size-3.5" /> Add site
            </Button>
          </div>
        </div>

        {importResult && importResult.errors.length > 0 ? (
          <div className="border-b border-border/70 bg-amber-50 px-4 py-2.5 text-xs text-amber-900 dark:bg-amber-950/40 dark:text-amber-100">
            <p className="mb-1 flex items-center gap-1.5 font-semibold">
              <TriangleAlert className="size-3.5" aria-hidden /> {importResult.errors.length} row(s) were skipped
            </p>
            <ul className="max-h-32 space-y-0.5 overflow-y-auto">
              {importResult.errors.map((e) => (
                <li key={`${e.row}-${e.message}`}>
                  Row {e.row}: {e.message}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="erp-scroll overflow-x-auto">
          <table className="w-full min-w-[1180px] text-left text-sm">
            <thead>
              <tr className={CRM_TABLE_HEAD_ROW}>
                <th className="px-3 py-2.5">Circle</th>
                <th className="px-3 py-2.5">Site</th>
                <th className="px-3 py-2.5">Customer PO</th>
                <th className="px-3 py-2.5">Items</th>
                <th className="px-3 py-2.5">Milestone</th>
                <th className="px-3 py-2.5">Status</th>
                <th className="px-3 py-2.5">Expected</th>
                <th className="px-3 py-2.5">AWB</th>
                <th className="w-20 px-3 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-10 text-center text-muted-foreground">
                    {sites.length === 0
                      ? "No sites yet - add them, pull them from the deal's OVFs, or upload the Excel tracker."
                      : "No sites match these filters."}
                  </td>
                </tr>
              ) : (
                filtered.map((s) => (
                  <tr key={s.id} className="border-b border-border/50 align-top transition-colors duration-150 last:border-0 hover:bg-accent/30">
                    <td className="px-3 py-2 text-xs">{s.circle ?? "-"}</td>
                    <td className="px-3 py-2">
                      <span className="font-medium">{s.site_name}</span>
                      <span className="block text-[11px] text-muted-foreground">
                        {[s.site_code, s.state].filter(Boolean).join(" · ") || "\u00a0"}
                      </span>
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">{s.customer_po_number ?? "-"}</td>
                    <td className="max-w-[220px] px-3 py-2 text-xs">
                      <span className="line-clamp-2">{s.item_summary ?? "-"}</span>
                      {s.quantity != null ? <span className="text-muted-foreground">Qty {Number(s.quantity)}</span> : null}
                    </td>
                    <td className="px-3 py-2">
                      <FinanceSelect
                        aria-label={`Milestone for ${s.site_name}`}
                        className="h-7 w-44 text-xs"
                        value={s.milestone}
                        disabled={busy}
                        onChange={(e) =>
                          void run(async () => {
                            await updateDeliverySite(s.id, { milestone: e.target.value });
                          })
                        }
                      >
                        {DELIVERY_MILESTONES.map((m) => (
                          <option key={m.value} value={m.value}>
                            {m.label}
                          </option>
                        ))}
                      </FinanceSelect>
                    </td>
                    <td className="px-3 py-2">
                      <Badge className={`rounded-full border-transparent px-2.5 py-0.5 text-[11px] font-semibold ${STATUS_CLASS[s.status] ?? ""}`}>
                        {siteStatusLabel(s.status)}
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-xs tabular-nums">
                      {s.actual_delivery_date ? (
                        <span className="text-emerald-700 dark:text-emerald-400">Done {s.actual_delivery_date}</span>
                      ) : s.expected_delivery_date ? (
                        <span className={s.delayed ? "inline-flex items-center gap-1 font-semibold text-red-700 dark:text-red-400" : ""}>
                          {s.delayed ? <TriangleAlert className="size-3.5" aria-hidden /> : null}
                          {s.expected_delivery_date}
                        </span>
                      ) : (
                        "-"
                      )}
                      {s.delay_reason ? <span className="block text-[11px] text-muted-foreground">{s.delay_reason}</span> : null}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">{s.awb_number ?? "-"}</td>
                    <td className="px-3 py-2">
                      <div className="flex gap-0.5">
                        <Button type="button" size="icon-sm" variant="ghost" className="cursor-pointer" aria-label={`Edit ${s.site_name}`} onClick={() => openEditor(s)}>
                          <Pencil className="size-3.5" />
                        </Button>
                        <Button type="button" size="icon-sm" variant="ghost" className="cursor-pointer text-muted-foreground hover:text-destructive" aria-label={`Remove ${s.site_name}`} onClick={() => setRemoving(s)}>
                          <Trash2 className="size-3.5" />
                        </Button>
                      </div>
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
        title={editing === "new" ? "Add site" : `Edit ${editing?.site_name ?? "site"}`}
        confirmLabel={editing === "new" ? "Add site" : "Save"}
        busy={busy}
        contentClassName="sm:max-w-2xl"
        onCancel={() => !busy && setEditing(null)}
        onConfirm={() => void saveSite()}
      >
        <div className="grid max-h-[60vh] gap-3 overflow-y-auto pr-1 sm:grid-cols-3">
          <FinanceField label="Site name *" className="sm:col-span-2">
            <Input value={draft.site_name} onChange={(e) => setDraft((d) => ({ ...d, site_name: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Site code">
            <Input value={draft.site_code} onChange={(e) => setDraft((d) => ({ ...d, site_code: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Circle">
            <Input value={draft.circle} onChange={(e) => setDraft((d) => ({ ...d, circle: e.target.value }))} placeholder="North" className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="State">
            <Input value={draft.state} onChange={(e) => setDraft((d) => ({ ...d, state: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="GSTIN">
            <Input value={draft.gstin} maxLength={15} onChange={(e) => setDraft((d) => ({ ...d, gstin: e.target.value.toUpperCase() }))} className="h-9 font-mono text-[13px]" />
          </FinanceField>
          <FinanceField label="Address" className="sm:col-span-3">
            <Input value={draft.address} onChange={(e) => setDraft((d) => ({ ...d, address: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Customer PO">
            <Input value={draft.customer_po_number} onChange={(e) => setDraft((d) => ({ ...d, customer_po_number: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Items" className="sm:col-span-1">
            <Input value={draft.item_summary} onChange={(e) => setDraft((d) => ({ ...d, item_summary: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Qty">
            <Input type="number" min="0" inputMode="decimal" value={draft.quantity} onChange={(e) => setDraft((d) => ({ ...d, quantity: e.target.value }))} className="h-9 text-[13px] tabular-nums" />
          </FinanceField>
          <FinanceField label="Milestone">
            <FinanceSelect className="h-9 text-[13px]" value={draft.milestone} onChange={(e) => setDraft((d) => ({ ...d, milestone: e.target.value }))}>
              {DELIVERY_MILESTONES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </FinanceSelect>
          </FinanceField>
          <FinanceField label="Status" hint="Follows the milestone unless set">
            <FinanceSelect className="h-9 text-[13px]" value={draft.status} onChange={(e) => setDraft((d) => ({ ...d, status: e.target.value }))}>
              {SITE_STATUS_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </FinanceSelect>
          </FinanceField>
          <FinanceField label="AWB / docket">
            <Input value={draft.awb_number} onChange={(e) => setDraft((d) => ({ ...d, awb_number: e.target.value }))} className="h-9 font-mono text-[13px]" />
          </FinanceField>
          <FinanceField label="Expected delivery">
            <Input type="date" value={draft.expected_delivery_date} onChange={(e) => setDraft((d) => ({ ...d, expected_delivery_date: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Actual delivery">
            <Input type="date" value={draft.actual_delivery_date} onChange={(e) => setDraft((d) => ({ ...d, actual_delivery_date: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Delay reason" hint="Required when the expected date moves later">
            <Input value={draft.delay_reason} onChange={(e) => setDraft((d) => ({ ...d, delay_reason: e.target.value }))} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Note" className="sm:col-span-3">
            <FinanceTextarea value={draft.last_note} onChange={(e) => setDraft((d) => ({ ...d, last_note: e.target.value }))} className="min-h-[56px] text-[13px]" />
          </FinanceField>
          {editing !== "new" && editing && editing.history.length > 0 ? (
            <div className="sm:col-span-3">
              <p className="mb-1 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">Recent changes</p>
              <ul className="space-y-0.5 text-[11px] text-muted-foreground">
                {editing.history
                  .slice(-5)
                  .reverse()
                  .map((h) => (
                    <li key={h.at}>
                      {new Date(h.at).toLocaleString()} · {h.source.replace("_", " ")} ·{" "}
                      {Object.keys(h.changes).join(", ").replaceAll("_", " ")}
                    </li>
                  ))}
              </ul>
            </div>
          ) : null}
        </div>
        {formError ? <p className="mt-3 text-xs text-destructive">{formError}</p> : null}
      </ConfirmDialog>

      <ConfirmDialog
        open={removing !== null}
        title="Remove site?"
        description={`${removing?.site_name ?? ""} will be removed from this tracker and the customer link.`}
        confirmLabel="Remove"
        tone="destructive"
        busy={busy}
        onCancel={() => !busy && setRemoving(null)}
        onConfirm={() =>
          void run(async () => {
            if (removing) await deleteDeliverySite(removing.id);
            setRemoving(null);
            return "Site removed.";
          })
        }
      />
    </CrmPage>
  );
}
