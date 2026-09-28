"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Split, TriangleAlert } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { FinanceField } from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatCrmCode } from "@/lib/crm/format-crm-code";
import { ApiClientError } from "@/services/api-client";
import {
  getQuoteSplitBalance,
  splitQuote,
  type QuoteSplitBalanceRow,
} from "@/services/crm-deal-controls-service";
import { fullName, type Contact, type Quote } from "@/services/sales-crm-service";

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-[13px] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

type SplitDraft = {
  contact_id: string;
  entity_name: string;
  entity_gst: string;
  shipping_city: string;
  qty: Record<string, string>;
};

function emptySplit(contactId: string): SplitDraft {
  return { contact_id: contactId, entity_name: "", entity_gst: "", shipping_city: "", qty: {} };
}

type Props = {
  quote: Quote;
  contacts: Contact[];
};

/**
 * One received quote → several customer quotes (entities, locations, GSTINs).
 * Every quantity is drawn down from the source quote, so 100 licences cannot
 * be sold as 3 x 100 the way a clone would.
 */
export function QuoteSplitPanel({ quote, contacts }: Props) {
  const splittable = !quote.parent_quote_id && quote.quote_stage !== "lost";
  const [balance, setBalance] = useState<QuoteSplitBalanceRow[]>([]);
  const [count, setCount] = useState(2);
  const [sameContact, setSameContact] = useState(true);
  const [drafts, setDrafts] = useState<SplitDraft[]>([]);
  const [created, setCreated] = useState<Quote[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);

  const load = useCallback(async () => {
    try {
      setBalance(await getQuoteSplitBalance(quote.id));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load quantities");
    }
  }, [quote.id]);

  useEffect(() => {
    if (!splittable) return;
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [splittable, load]);

  const allocated = useMemo(() => {
    const totals: Record<string, number> = {};
    for (const d of drafts) {
      for (const [lineId, value] of Object.entries(d.qty)) {
        totals[lineId] = (totals[lineId] ?? 0) + (Number(value) || 0);
      }
    }
    return totals;
  }, [drafts]);

  if (!splittable) {
    return quote.parent_quote_id ? (
      <p className="text-xs text-muted-foreground">
        This quote was split from{" "}
        <Link href={`/crm/quotes/${quote.parent_quote_id}`} className="cursor-pointer font-medium text-primary underline underline-offset-2">
          the source quote
        </Link>
        ; its quantities count against that quote&apos;s balance.
      </p>
    ) : null;
  }

  function start() {
    const contactId = quote.contact_id ?? contacts[0]?.id ?? "";
    setDrafts(Array.from({ length: count }, () => emptySplit(contactId)));
    setCreated([]);
    setError(null);
    setOpen(true);
  }

  function patch(index: number, update: Partial<SplitDraft>) {
    setDrafts((rows) => rows.map((row, i) => (i === index ? { ...row, ...update } : row)));
  }

  const overAllocated = balance.some((row) => (allocated[row.line_id] ?? 0) - Number(row.balance_qty) > 1e-6);
  const everyQuoteHasLines = drafts.every((d) => Object.values(d.qty).some((v) => Number(v) > 0));

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const rows = await splitQuote(
        quote.id,
        drafts.map((d) => ({
          contact_id: (sameContact ? drafts[0]?.contact_id : d.contact_id) || null,
          entity_name: d.entity_name.trim() || null,
          entity_gst: d.entity_gst.trim().toUpperCase() || null,
          shipping_city: d.shipping_city.trim() || null,
          lines: Object.entries(d.qty)
            .filter(([, v]) => Number(v) > 0)
            .map(([lineId, v]) => ({ source_line_id: lineId, qty: Number(v) })),
        })),
      );
      setCreated(rows);
      setOpen(false);
      await load();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to split the quote");
    } finally {
      setBusy(false);
    }
  }

  return (
    <CrmSection title="Break Into Multiple Quotes" icon={Split}>
      {error ? (
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
          <TriangleAlert className="size-3.5" /> {error}
        </p>
      ) : null}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-left text-[13px]">
          <thead className="text-[11px] text-muted-foreground uppercase">
            <tr>
              <th className="py-1.5 pr-3 font-semibold">Item</th>
              <th className="py-1.5 pr-3 text-right font-semibold">Quoted</th>
              <th className="py-1.5 pr-3 text-right font-semibold">Already split</th>
              <th className="py-1.5 pr-3 text-right font-semibold">Balance</th>
            </tr>
          </thead>
          <tbody>
            {balance.map((row) => (
              <tr key={row.line_id} className="border-t border-border/60">
                <td className="py-1.5 pr-3">{row.product_name}</td>
                <td className="py-1.5 pr-3 text-right tabular-nums">{Number(row.qty)}</td>
                <td className="py-1.5 pr-3 text-right tabular-nums">{Number(row.allocated_qty)}</td>
                <td className="py-1.5 pr-3 text-right font-semibold tabular-nums">{Number(row.balance_qty)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {created.length > 0 ? (
        <p className="mt-3 text-xs text-emerald-700 dark:text-emerald-400">
          Created{" "}
          {created.map((q, i) => (
            <span key={q.id}>
              {i > 0 ? ", " : ""}
              <Link href={`/crm/quotes/${q.id}`} className="cursor-pointer font-medium underline underline-offset-2">
                {formatCrmCode(q.quote_no)}
              </Link>
            </span>
          ))}
          . Each goes through approval and gets its own customer PO and OVF.
        </p>
      ) : null}

      {!open ? (
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <FinanceField label="How many quotes from this one?">
            <Input
              type="number"
              min={2}
              max={20}
              value={count}
              onChange={(e) => setCount(Math.max(2, Math.min(20, Number(e.target.value) || 2)))}
              className="h-9 w-24 text-[13px]"
            />
          </FinanceField>
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={balance.every((row) => Number(row.balance_qty) <= 0)}
            className="h-9 cursor-pointer"
            onClick={start}
          >
            <Split className="size-3.5" /> Split quantities
          </Button>
        </div>
      ) : (
        <div className="mt-3 space-y-4">
          <label className="flex cursor-pointer items-center gap-2 text-xs">
            <input
              type="checkbox"
              className="size-4 cursor-pointer accent-primary"
              checked={sameContact}
              onChange={(e) => setSameContact(e.target.checked)}
            />
            Same contact for all quotes
          </label>
          {drafts.map((d, index) => (
            <div key={index} className="rounded-lg border border-border/70 p-3">
              <p className="mb-2 text-xs font-semibold">Quote {index + 1}</p>
              <div className="grid gap-3 sm:grid-cols-4">
                {!sameContact || index === 0 ? (
                  <FinanceField label="Contact">
                    <select
                      className={SELECT_CLASS}
                      value={d.contact_id}
                      onChange={(e) => patch(index, { contact_id: e.target.value })}
                    >
                      <option value="">Select contact</option>
                      {contacts.map((c) => (
                        <option key={c.id} value={c.id}>
                          {fullName(c)}
                        </option>
                      ))}
                    </select>
                  </FinanceField>
                ) : null}
                <FinanceField label="Entity name">
                  <Input value={d.entity_name} onChange={(e) => patch(index, { entity_name: e.target.value })} className="h-9 text-[13px]" />
                </FinanceField>
                <FinanceField label="Entity GSTIN">
                  <Input
                    value={d.entity_gst}
                    maxLength={15}
                    onChange={(e) => patch(index, { entity_gst: e.target.value.toUpperCase() })}
                    className="h-9 font-mono text-[13px]"
                  />
                </FinanceField>
                <FinanceField label="Ship-to city">
                  <Input value={d.shipping_city} onChange={(e) => patch(index, { shipping_city: e.target.value })} className="h-9 text-[13px]" />
                </FinanceField>
              </div>
              <div className="mt-2 grid gap-2 sm:grid-cols-3">
                {balance.map((row) => (
                  <FinanceField key={row.line_id} label={`${row.product_name} (left ${Number(row.balance_qty) - (allocated[row.line_id] ?? 0) + (Number(d.qty[row.line_id]) || 0)})`}>
                    <Input
                      type="number"
                      min={0}
                      value={d.qty[row.line_id] ?? ""}
                      onChange={(e) => patch(index, { qty: { ...d.qty, [row.line_id]: e.target.value } })}
                      className="h-9 text-[13px]"
                    />
                  </FinanceField>
                ))}
              </div>
            </div>
          ))}
          {overAllocated ? (
            <p className="text-xs font-medium text-red-600">
              More than the balance is allocated on at least one item - reduce the quantities.
            </p>
          ) : null}
          <div className="flex gap-2">
            <Button
              type="button"
              size="sm"
              disabled={busy || overAllocated || !everyQuoteHasLines}
              className="cursor-pointer"
              onClick={() => void submit()}
            >
              {busy ? "Creating…" : `Create ${drafts.length} quotes`}
            </Button>
            <Button type="button" size="sm" variant="outline" disabled={busy} className="cursor-pointer" onClick={() => setOpen(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}
    </CrmSection>
  );
}
