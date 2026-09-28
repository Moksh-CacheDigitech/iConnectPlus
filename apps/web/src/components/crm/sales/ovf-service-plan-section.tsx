"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { CalendarCheck, TriangleAlert, X } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { FinanceField, FinanceSelect } from "@/components/finance/journals/finance-form-field";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatApiError } from "@/services/api-client";
import { formatInrPrecise, type Ovf } from "@/services/sales-crm-service";
import {
  cancelServiceVisit,
  closeServicePlan,
  createServicePlan,
  listServiceContracts,
  listServicePlans,
  listServiceVisits,
  logServiceVisit,
  serviceTypeLabel,
  type ServicePlan,
  type ServiceRateContract,
  type ServiceVisit,
} from "@/services/service-projects-service";

type Props = {
  ovf: Ovf;
  onChanged: () => void;
};

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Service POs priced per visit: projected visits x contract rate (+ consumables)
 * go on the OVF as vendor lines; visits past the projection become execution
 * expenses for the owner to approve.
 */
export function OvfServicePlanSection({ ovf, onChanged }: Props) {
  const editable = ovf.blueprint_state === "draft" && !ovf.locked && !ovf.shared_to_scm;
  const [plans, setPlans] = useState<ServicePlan[]>([]);
  const [contracts, setContracts] = useState<ServiceRateContract[] | null>(null);
  const [visits, setVisits] = useState<ServiceVisit[]>([]);
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [adding, setAdding] = useState(false);

  const [contractId, setContractId] = useState("");
  const [projected, setProjected] = useState("");
  const [consumables, setConsumables] = useState("");
  const [description, setDescription] = useState("");
  const [addToOvf, setAddToOvf] = useState(true);

  const [visitDate, setVisitDate] = useState(today);
  const [visitSite, setVisitSite] = useState("");
  const [engineer, setEngineer] = useState("");

  const loadVisits = useCallback(async (planId: string | null) => {
    setVisits(planId ? await listServiceVisits(planId) : []);
  }, []);

  const activePlanRef = useRef<string | null>(null);
  useEffect(() => {
    activePlanRef.current = activePlanId;
  }, [activePlanId]);

  const load = useCallback(async () => {
    try {
      const rows = await listServicePlans(ovf.id);
      setPlans(rows);
      const nextId = rows.find((p) => p.id === activePlanRef.current)?.id ?? rows[0]?.id ?? null;
      setActivePlanId(nextId);
      await loadVisits(nextId);
    } catch (err) {
      setError(formatApiError(err, "Failed to load service plans"));
    }
  }, [ovf.id, loadVisits]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function openAdd() {
    setAdding(true);
    setAddToOvf(editable);
    if (contracts === null) {
      try {
        setContracts(await listServiceContracts(true));
      } catch {
        setContracts([]);
      }
    }
  }

  async function run(work: () => Promise<unknown>, refreshOvf = false) {
    setBusy(true);
    setError(null);
    try {
      await work();
      await load();
      if (refreshOvf) onChanged();
    } catch (err) {
      setError(formatApiError(err, "Request failed"));
    } finally {
      setBusy(false);
    }
  }

  const contract = contracts?.find((c) => c.id === contractId) ?? null;
  const projectedCount = Math.floor(Number(projected) || 0);
  const preview = contract ? projectedCount * Number(contract.rate_per_visit) + (Number(consumables) || 0) : null;
  const activePlan = plans.find((p) => p.id === activePlanId) ?? null;

  if (plans.length === 0 && !adding) {
    return (
      <CrmSection
        title="Service Visits"
        icon={CalendarCheck}
        actions={
          <Button type="button" size="sm" variant="outline" className="h-7 cursor-pointer text-xs" onClick={() => void openAdd()}>
            Plan service visits
          </Button>
        }
      >
        <p className="text-xs text-muted-foreground">
          Price site visits / installation off a per-visit rate contract. Extra visits later go to the owner as expenses.
        </p>
        {error ? <p className="mt-2 text-xs text-destructive">{error}</p> : null}
      </CrmSection>
    );
  }

  return (
    <CrmSection
      title="Service Visits"
      icon={CalendarCheck}
      actions={
        !adding ? (
          <Button type="button" size="sm" variant="outline" className="h-7 cursor-pointer text-xs" onClick={() => void openAdd()}>
            Add plan
          </Button>
        ) : null
      }
    >
      {error ? (
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
          <TriangleAlert className="size-3.5" aria-hidden /> {error}
        </p>
      ) : null}

      {plans.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-[13px]">
            <thead className="text-[11px] text-muted-foreground uppercase">
              <tr>
                <th className="py-1.5 pr-3 font-semibold">Partner</th>
                <th className="py-1.5 pr-3 font-semibold">Service</th>
                <th className="py-1.5 pr-3 text-right font-semibold">Visits</th>
                <th className="py-1.5 pr-3 text-right font-semibold">Rate</th>
                <th className="py-1.5 pr-3 text-right font-semibold">Planned</th>
                <th className="py-1.5 pr-3 text-right font-semibold">Actual</th>
                <th className="py-1.5 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((p) => {
                const over = Number(p.actual_cost) > Number(p.planned_total);
                return (
                  <tr
                    key={p.id}
                    className={`cursor-pointer border-t border-border/60 transition-colors duration-150 hover:bg-accent/30 ${p.id === activePlanId ? "bg-accent/40" : ""}`}
                    onClick={() => {
                      setActivePlanId(p.id);
                      void loadVisits(p.id);
                    }}
                  >
                    <td className="py-1.5 pr-3">
                      <span className="font-medium">{p.vendor_name ?? "-"}</span>
                      <span className="block font-mono text-[11px] text-muted-foreground">{p.contract_code}</span>
                    </td>
                    <td className="py-1.5 pr-3">{serviceTypeLabel(p.service_type)}</td>
                    <td className="py-1.5 pr-3 text-right tabular-nums">
                      {p.visits_done} / {p.projected_visits}
                      {p.extra_visits > 0 ? (
                        <span className="block text-[11px] font-semibold text-red-700 dark:text-red-400">+{p.extra_visits} extra</span>
                      ) : null}
                    </td>
                    <td className="py-1.5 pr-3 text-right tabular-nums">{formatInrPrecise(p.rate_per_visit)}</td>
                    <td className="py-1.5 pr-3 text-right tabular-nums">{formatInrPrecise(p.planned_total)}</td>
                    <td className={`py-1.5 pr-3 text-right tabular-nums ${over ? "font-semibold text-red-700 dark:text-red-400" : ""}`}>
                      {formatInrPrecise(p.actual_cost)}
                    </td>
                    <td className="py-1.5">
                      <Badge
                        className={`rounded-full border-transparent px-2.5 py-0.5 text-[11px] font-semibold ${p.status === "open"
                            ? "bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-200"
                            : "bg-muted text-muted-foreground"
                          }`}
                      >
                        {p.status === "open" ? "Open" : "Closed"}
                      </Badge>
                      {!p.added_to_ovf ? <span className="block text-[11px] text-muted-foreground">Not on OVF lines</span> : null}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}

      {activePlan ? (
        <div className="mt-4 border-t border-border/70 pt-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
              Visit log · {activePlan.vendor_name}
            </h3>
            {activePlan.status === "open" ? (
              <Button
                type="button"
                size="sm"
                variant="ghost"
                className="h-7 cursor-pointer text-xs"
                disabled={busy}
                onClick={() => void run(() => closeServicePlan(activePlan.id))}
              >
                Close plan
              </Button>
            ) : null}
          </div>
          {visits.length > 0 ? (
            <ul className="mt-2 space-y-1 text-[13px]">
              {visits.map((v) => (
                <li
                  key={v.id}
                  className={`flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border/60 px-3 py-1.5 ${v.status === "cancelled" ? "opacity-60" : ""}`}
                >
                  <span>
                    <span className="tabular-nums">{v.visit_date}</span>
                    {v.site ? <span> · {v.site}</span> : null}
                    {v.engineer_name ? <span className="text-muted-foreground"> · {v.engineer_name}</span> : null}
                    {v.status === "cancelled" ? <span className="text-muted-foreground"> · cancelled</span> : null}
                  </span>
                  <span className="flex items-center gap-1.5">
                    {v.beyond_projection ? (
                      <Badge className="rounded-full border-transparent bg-amber-100 px-2 py-0.5 text-[11px] font-semibold text-amber-900 dark:bg-amber-900/50 dark:text-amber-100">
                        {v.expense_id ? "Extra - sent to owner" : "Extra - review"}
                      </Badge>
                    ) : null}
                    {v.status === "done" && !v.expense_id ? (
                      <Button
                        type="button"
                        size="icon-sm"
                        variant="ghost"
                        className="cursor-pointer text-muted-foreground hover:text-destructive"
                        aria-label={`Cancel visit on ${v.visit_date}`}
                        disabled={busy}
                        onClick={() => void run(() => cancelServiceVisit(v.id))}
                      >
                        <X className="size-3.5" />
                      </Button>
                    ) : null}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-xs text-muted-foreground">No visits logged yet.</p>
          )}
          {activePlan.status === "open" ? (
            <div className="mt-3 grid gap-3 sm:grid-cols-4">
              <FinanceField label="Visit date">
                <Input type="date" max={today()} value={visitDate} onChange={(e) => setVisitDate(e.target.value)} className="h-9 cursor-pointer text-[13px]" />
              </FinanceField>
              <FinanceField label="Site">
                <Input value={visitSite} onChange={(e) => setVisitSite(e.target.value)} className="h-9 text-[13px]" />
              </FinanceField>
              <FinanceField label="Engineer">
                <Input value={engineer} onChange={(e) => setEngineer(e.target.value)} className="h-9 text-[13px]" />
              </FinanceField>
              <div className="flex items-end">
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  className="cursor-pointer"
                  disabled={busy || !visitDate}
                  onClick={() =>
                    void run(async () => {
                      await logServiceVisit(activePlan.id, {
                        visit_date: visitDate,
                        site: visitSite.trim() || null,
                        engineer_name: engineer.trim() || null,
                      });
                      setVisitSite("");
                      setEngineer("");
                    }, activePlan.visits_done >= activePlan.projected_visits)
                  }
                >
                  Log visit
                </Button>
              </div>
            </div>
          ) : null}
          {activePlan.status === "open" && activePlan.visits_remaining === 0 ? (
            <p className="mt-2 text-[11px] text-amber-700 dark:text-amber-400">
              All projected visits are used - further visits are raised as execution expenses for the owner.
            </p>
          ) : null}
        </div>
      ) : null}

      {adding ? (
        <div className="mt-4 border-t border-border/70 pt-3">
          <h3 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">New service plan</h3>
          {contracts !== null && contracts.length === 0 ? (
            <p className="mt-2 text-xs text-muted-foreground">
              No active rate contracts. SCM adds them under Procurement → Service Contracts.
            </p>
          ) : null}
          <div className="mt-3 grid gap-3 sm:grid-cols-4">
            <FinanceField label="Rate contract *" className="sm:col-span-2">
              <FinanceSelect className="h-9 text-[13px]" value={contractId} onChange={(e) => setContractId(e.target.value)}>
                <option value="">Select…</option>
                {(contracts ?? []).map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.vendor_name} · {serviceTypeLabel(c.service_type)} · {formatInrPrecise(c.rate_per_visit)}/visit
                    {c.region ? ` · ${c.region}` : ""}
                  </option>
                ))}
              </FinanceSelect>
            </FinanceField>
            <FinanceField label="Projected visits *">
              <Input type="number" min={1} step={1} value={projected} onChange={(e) => setProjected(e.target.value)} className="h-9 text-[13px] tabular-nums" />
            </FinanceField>
            <FinanceField label="Consumables (₹)" hint="LAN cable, connectors, survey">
              <Input type="number" min={0} step="0.01" value={consumables} onChange={(e) => setConsumables(e.target.value)} className="h-9 text-[13px] tabular-nums" />
            </FinanceField>
            <FinanceField label="Scope / notes" className="sm:col-span-2">
              <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Install + 1 revisit per site, 12 sites" className="h-9 text-[13px]" />
            </FinanceField>
            <label className={`flex items-end gap-2 pb-2 text-xs ${editable ? "cursor-pointer" : "cursor-not-allowed opacity-60"}`}>
              <input
                type="checkbox"
                className="size-4 cursor-pointer accent-primary disabled:cursor-not-allowed"
                checked={addToOvf && editable}
                disabled={!editable}
                onChange={(e) => setAddToOvf(e.target.checked)}
              />
              {editable ? "Add as OVF vendor lines" : "OVF is locked - plan only"}
            </label>
            <div className="flex items-end gap-2">
              <Button
                type="button"
                size="sm"
                disabled={busy || !contractId || projectedCount < 1}
                className="cursor-pointer"
                onClick={() =>
                  void run(async () => {
                    await createServicePlan({
                      ovf_id: ovf.id,
                      rate_contract_id: contractId,
                      projected_visits: projectedCount,
                      consumables_amount: Number(consumables) || 0,
                      description: description.trim() || null,
                      add_to_ovf: addToOvf && editable,
                    });
                    setAdding(false);
                    setContractId("");
                    setProjected("");
                    setConsumables("");
                    setDescription("");
                  }, true)
                }
              >
                Create plan
              </Button>
              <Button type="button" size="sm" variant="ghost" className="cursor-pointer" disabled={busy} onClick={() => setAdding(false)}>
                Cancel
              </Button>
            </div>
          </div>
          {preview != null ? (
            <p className="mt-2 text-xs text-muted-foreground">
              Planned cost: <span className="font-semibold tabular-nums text-foreground">{formatInrPrecise(preview)}</span>
              {projectedCount > 0 && contract ? ` (${projectedCount} × ${formatInrPrecise(contract.rate_per_visit)} + consumables)` : ""}
            </p>
          ) : null}
        </div>
      ) : null}
    </CrmSection>
  );
}
