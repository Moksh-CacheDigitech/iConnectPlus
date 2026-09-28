"use client";

import { useState } from "react";
import { Route } from "lucide-react";

import { DeliverySectionCard } from "@/components/procurement/delivery-section-card";
import { FinanceField } from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import { DELIVERY_MILESTONES, updateDeliveryMilestone } from "@/services/crm-deal-controls-service";

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-[13px] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

type Props = {
  orderId: string;
  initialMilestone?: string | null;
  initialAwb?: string | null;
};

/** Factory → India → warehouse → site: the shipment milestone and AWB / docket on the vendor PO. */
export function DeliveryMilestoneCard({ orderId, initialMilestone, initialAwb }: Props) {
  const [milestone, setMilestone] = useState(initialMilestone ?? "order_placed");
  const [awb, setAwb] = useState(initialAwb ?? "");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<{ tone: "ok" | "error"; text: string } | null>(null);
  const currentIndex = DELIVERY_MILESTONES.findIndex((m) => m.value === milestone);

  async function save() {
    setBusy(true);
    setMessage(null);
    try {
      await updateDeliveryMilestone(orderId, {
        milestone,
        awb_number: awb.trim() || null,
        note: note.trim() || null,
      });
      setNote("");
      setMessage({ tone: "ok", text: "Shipment milestone saved." });
    } catch (err) {
      setMessage({ tone: "error", text: err instanceof ApiClientError ? err.message : "Failed to save milestone" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <DeliverySectionCard title="Shipment milestone" icon={Route} subtitle="Customer-facing tracker for this vendor PO">
      <ol className="mb-4 flex flex-wrap gap-1.5" aria-label="Shipment progress">
        {DELIVERY_MILESTONES.map((m, idx) => (
          <li
            key={m.value}
            className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium ${idx <= currentIndex
                ? "bg-blue-600 text-white"
                : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"
              }`}
          >
            {m.label}
          </li>
        ))}
      </ol>
      <div className="grid gap-3 sm:grid-cols-4">
        <FinanceField label="Milestone">
          <select className={SELECT_CLASS} value={milestone} onChange={(e) => setMilestone(e.target.value)}>
            {DELIVERY_MILESTONES.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </FinanceField>
        <FinanceField label="AWB / docket no.">
          <Input value={awb} onChange={(e) => setAwb(e.target.value)} className="h-9 text-[13px]" />
        </FinanceField>
        <FinanceField label="Note">
          <Input value={note} onChange={(e) => setNote(e.target.value)} className="h-9 text-[13px]" />
        </FinanceField>
        <div className="flex items-end">
          <Button type="button" size="sm" variant="outline" disabled={busy} className="h-9 cursor-pointer" onClick={() => void save()}>
            Save milestone
          </Button>
        </div>
      </div>
      {message ? (
        <p className={`mt-2 text-xs ${message.tone === "ok" ? "text-emerald-700 dark:text-emerald-400" : "text-destructive"}`}>
          {message.text}
        </p>
      ) : null}
    </DeliverySectionCard>
  );
}
