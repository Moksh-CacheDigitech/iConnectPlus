"use client";

import { useCallback, useEffect, useState } from "react";
import { CalendarCheck, TriangleAlert } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatApiError } from "@/services/api-client";
import {
  formatInrPrecise,
  listMyJobs,
  requestOvfServiceVisits,
  type Ovf,
} from "@/services/sales-crm-service";
import {
  listServicePlans,
  serviceTypeLabel,
  type ServicePlan,
} from "@/services/service-projects-service";

type Props = {
  ovf: Ovf;
  onChanged: () => void;
};

/**
 * Read-only Service Visits plan summary on the OVF.
 * Plans are created by the assigned Operations owner in My Jobs;
 * planned cost → Additional Charges (not Vendor PO). No visit-log UI.
 */
export function OvfServicePlanSection({ ovf, onChanged }: Props) {
  const canAsk =
    !ovf.deal_won &&
    !ovf.locked &&
    ["draft", "approved", "shared_scm"].includes(ovf.blueprint_state);
  const [plans, setPlans] = useState<ServicePlan[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pendingAsk, setPendingAsk] = useState(false);
  const [requesting, setRequesting] = useState(false);

  const load = useCallback(async () => {
    try {
      const [rows, pendingTasks] = await Promise.all([
        listServicePlans(ovf.id),
        listMyJobs({
          entity_type: "ovf",
          entity_id: ovf.id,
          status: "pending",
        }).catch(() => []),
      ]);
      setPlans(rows);
      setPendingAsk(pendingTasks.some((task) => task.action === "provide_service_visits"));
    } catch (err) {
      setError(formatApiError(err, "Failed to load service plans"));
    }
  }, [ovf.id]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function askForServiceVisits() {
    if (!canAsk || pendingAsk || requesting || plans.length > 0) return;
    setRequesting(true);
    setError(null);
    try {
      await requestOvfServiceVisits(ovf.id);
      setPendingAsk(true);
      onChanged();
    } catch (err) {
      setError(formatApiError(err, "Failed to request service visits from Operations"));
    } finally {
      setRequesting(false);
    }
  }

  const askActions =
    canAsk && plans.length === 0 ? (
      pendingAsk ? (
        <Badge className="rounded-full border-transparent bg-amber-100 px-2.5 py-0.5 text-[11px] font-semibold text-amber-900 dark:bg-amber-900/50 dark:text-amber-100">
          Awaiting Operations
        </Badge>
      ) : (
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="h-7 cursor-pointer text-xs"
          disabled={requesting}
          onClick={() => void askForServiceVisits()}
        >
          {requesting ? "Requesting…" : "Ask Operations for service visits"}
        </Button>
      )
    ) : null;

  if (plans.length === 0) {
    return (
      <CrmSection title="Service Visits" icon={CalendarCheck} actions={askActions}>
        <p className="text-xs text-muted-foreground">
          Ask the assigned Operations owner to set up the service visit plan in My Jobs. Planned cost
          is included in Additional Charges (not Vendor PO).
        </p>
        {error ? (
          <p className="mt-2 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
            <TriangleAlert className="size-3.5" aria-hidden /> {error}
          </p>
        ) : null}
      </CrmSection>
    );
  }

  return (
    <CrmSection title="Service Visits" icon={CalendarCheck} actions={askActions}>
      {error ? (
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
          <TriangleAlert className="size-3.5" aria-hidden /> {error}
        </p>
      ) : null}

      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-[13px]">
          <thead className="text-[11px] font-semibold text-muted-foreground">
            <tr>
              <th className="py-1.5 pr-3">Vendor</th>
              <th className="py-1.5 pr-3">Service type</th>
              <th className="py-1.5 pr-3 text-right">Number of visits</th>
              <th className="py-1.5 pr-3 text-right">Rate per visit (₹)</th>
              <th className="py-1.5 pr-3 text-right">Consumables (₹)</th>
              <th className="py-1.5 text-right">Total (₹)</th>
            </tr>
          </thead>
          <tbody>
            {plans.map((p) => (
              <tr key={p.id} className="border-t border-border/60">
                <td className="py-1.5 pr-3">
                  <span className="font-medium">{p.vendor_name ?? "-"}</span>
                  <span className="block font-mono text-[11px] text-muted-foreground">
                    {p.contract_code}
                  </span>
                </td>
                <td className="py-1.5 pr-3">{serviceTypeLabel(p.service_type)}</td>
                <td className="py-1.5 pr-3 text-right tabular-nums">{p.projected_visits}</td>
                <td className="py-1.5 pr-3 text-right tabular-nums">
                  {formatInrPrecise(p.rate_per_visit)}
                </td>
                <td className="py-1.5 pr-3 text-right tabular-nums">
                  {formatInrPrecise(p.consumables_amount)}
                </td>
                <td className="py-1.5 text-right tabular-nums">
                  {formatInrPrecise(p.planned_total)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </CrmSection>
  );
}
