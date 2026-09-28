"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Landmark, TriangleAlert } from "lucide-react";

import { CrmDetailGrid, CrmDetailItem, CrmSection } from "@/components/crm/crm-ui";
import { FinanceField } from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatCrmCode } from "@/lib/crm/format-crm-code";
import { ApiClientError } from "@/services/api-client";
import {
  getOpportunityCustomerExpenseSummary,
  type CustomerExpenseSummary,
} from "@/services/crm-deal-controls-service";
import {
  formatInrPrecise,
  listMarketingEventOptions,
  updateOpportunity,
  type Opportunity,
  type Option,
} from "@/services/sales-crm-service";

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-[13px] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

type Props = {
  opportunity: Opportunity;
  onChanged: () => void;
};

/**
 * Single tracking number, open customer expenses to recover, marketing event
 * attribution for this deal, and CapEx / OpEx (lease) commercials.
 */
export function OpportunityDealControls({ opportunity, onChanged }: Props) {
  const [summary, setSummary] = useState<CustomerExpenseSummary | null>(null);
  const [events, setEvents] = useState<Option[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [draft, setDraft] = useState({
    marketing_event_id: opportunity.marketing_event_id ?? "",
    purchase_model: opportunity.purchase_model ?? "",
    lease_type: opportunity.lease_type ?? "",
    lease_partner: opportunity.lease_partner ?? "",
    lease_interest_rate_pct: opportunity.lease_interest_rate_pct != null ? String(opportunity.lease_interest_rate_pct) : "",
    lease_tenure_months: opportunity.lease_tenure_months != null ? String(opportunity.lease_tenure_months) : "",
    lease_monthly_rental: opportunity.lease_monthly_rental != null ? String(opportunity.lease_monthly_rental) : "",
  });

  const load = useCallback(async () => {
    const [expenseSummary, eventOptions] = await Promise.all([
      getOpportunityCustomerExpenseSummary(opportunity.id).catch(() => null),
      listMarketingEventOptions().catch(() => [] as Option[]),
    ]);
    setSummary(expenseSummary);
    setEvents(eventOptions);
  }, [opportunity.id]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const isOpex = draft.purchase_model === "opex";

  async function save() {
    setBusy(true);
    setError(null);
    try {
      await updateOpportunity(opportunity.id, {
        version: opportunity.version,
        marketing_event_id: draft.marketing_event_id || null,
        purchase_model: (draft.purchase_model || null) as "capex" | "opex" | null,
        ...(isOpex
          ? {
            lease_type: (draft.lease_type || null) as "finance" | "operating" | null,
            lease_partner: draft.lease_partner.trim() || null,
            lease_interest_rate_pct: draft.lease_interest_rate_pct ? Number(draft.lease_interest_rate_pct) : null,
            lease_tenure_months: draft.lease_tenure_months ? Number(draft.lease_tenure_months) : null,
            lease_monthly_rental: draft.lease_monthly_rental ? Number(draft.lease_monthly_rental) : null,
          }
          : {}),
      });
      onChanged();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to save");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      {summary && summary.open_count > 0 ? (
        <div className="flex flex-wrap items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm text-amber-950 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-100">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          <div className="min-w-0">
            <p className="font-semibold">
              {formatInrPrecise(summary.open_amount)} already spent on this customer ({summary.open_count}{" "}
              {summary.open_count === 1 ? "item" : "items"}) - recover it in this deal.
            </p>
            <ul className="mt-1 space-y-0.5 text-xs">
              {summary.open_items.slice(0, 5).map((item) => (
                <li key={item.id}>
                  {item.expense_date}: {item.description} - {formatInrPrecise(item.amount)} (approved by{" "}
                  {item.approved_by_name ?? "-"})
                </li>
              ))}
            </ul>
            {opportunity.company_account_id ? (
              <Link
                href={`/crm/companies/${opportunity.company_account_id}#customer-expenses`}
                className="mt-1 inline-block cursor-pointer text-xs font-medium underline underline-offset-2"
              >
                Open the customer expense ledger
              </Link>
            ) : null}
          </div>
        </div>
      ) : null}

      <CrmSection title="Deal Tracking & Commercial Model" icon={Landmark}>
        {error ? (
          <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
            <TriangleAlert className="size-3.5" /> {error}
          </p>
        ) : null}
        <CrmDetailGrid>
          <CrmDetailItem label="Opportunity / DR Number">
            <span className="font-semibold">
              {formatCrmCode(opportunity.deal_reg_number || opportunity.opportunity_code)}
            </span>
          </CrmDetailItem>
          <CrmDetailItem label="Customer PO T&C">
            {opportunity.sales_terms_accepted
              ? `Accepted by Sales${opportunity.sales_terms_accepted_at ? ` on ${opportunity.sales_terms_accepted_at.slice(0, 10)}` : ""}`
              : "Not yet accepted"}
          </CrmDetailItem>
        </CrmDetailGrid>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <FinanceField label="Marketing event (credit for this deal)">
            <select
              className={SELECT_CLASS}
              value={draft.marketing_event_id}
              onChange={(e) => setDraft((d) => ({ ...d, marketing_event_id: e.target.value }))}
            >
              <option value="">Not from an event</option>
              {events.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.label}
                </option>
              ))}
            </select>
          </FinanceField>
          <FinanceField label="Purchase model">
            <select
              className={SELECT_CLASS}
              value={draft.purchase_model}
              onChange={(e) => setDraft((d) => ({ ...d, purchase_model: e.target.value }))}
            >
              <option value="">Not set</option>
              <option value="capex">CapEx - customer buys outright</option>
              <option value="opex">OpEx - lease / rental</option>
            </select>
          </FinanceField>
          {isOpex ? (
            <FinanceField label="Lease type">
              <select
                className={SELECT_CLASS}
                value={draft.lease_type}
                onChange={(e) => setDraft((d) => ({ ...d, lease_type: e.target.value }))}
              >
                <option value="">Not set</option>
                <option value="finance">Finance lease</option>
                <option value="operating">Operating lease</option>
              </select>
            </FinanceField>
          ) : null}
          {isOpex ? (
            <>
              <FinanceField label="Lease partner (who funds it)">
                <Input
                  value={draft.lease_partner}
                  onChange={(e) => setDraft((d) => ({ ...d, lease_partner: e.target.value }))}
                  className="h-9 text-[13px]"
                />
              </FinanceField>
              <FinanceField label="Rate of interest (%)">
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  value={draft.lease_interest_rate_pct}
                  onChange={(e) => setDraft((d) => ({ ...d, lease_interest_rate_pct: e.target.value }))}
                  className="h-9 text-[13px]"
                />
              </FinanceField>
              <FinanceField label="Tenure (months)">
                <Input
                  type="number"
                  min={1}
                  value={draft.lease_tenure_months}
                  onChange={(e) => setDraft((d) => ({ ...d, lease_tenure_months: e.target.value }))}
                  className="h-9 text-[13px]"
                />
              </FinanceField>
              <FinanceField label="Monthly rental (₹)">
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  value={draft.lease_monthly_rental}
                  onChange={(e) => setDraft((d) => ({ ...d, lease_monthly_rental: e.target.value }))}
                  className="h-9 text-[13px]"
                />
              </FinanceField>
            </>
          ) : null}
        </div>
        <div className="mt-3 flex items-center gap-3">
          <Button type="button" size="sm" variant="outline" disabled={busy} className="cursor-pointer" onClick={() => void save()}>
            Save
          </Button>
          {isOpex ? (
            <span className="text-xs text-muted-foreground">
              Finance fills the lease terms - keep them here so the deal survives staff changes.
            </span>
          ) : null}
        </div>
      </CrmSection>
    </>
  );
}
