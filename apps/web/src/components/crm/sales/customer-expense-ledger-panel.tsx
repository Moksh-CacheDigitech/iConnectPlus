"use client";

import { useCallback, useEffect, useState } from "react";
import { HandCoins, TriangleAlert } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { FinanceField, FinanceTextarea } from "@/components/finance/journals/finance-form-field";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import {
  CUSTOMER_EXPENSE_CATEGORIES,
  adjustCustomerExpense,
  createCustomerExpense,
  listCustomerExpenses,
  writeOffCustomerExpense,
  type CustomerExpense,
} from "@/services/crm-deal-controls-service";
import { formatInrPrecise, type Ovf } from "@/services/sales-crm-service";

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-[13px] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

const STATUS_CLASS: Record<CustomerExpense["status"], string> = {
  open: "bg-amber-100 text-amber-900 dark:bg-amber-900/50 dark:text-amber-100",
  adjusted: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200",
  written_off: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
};

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

type Props = {
  companyAccountId: string;
  ovfs: Pick<Ovf, "id" | "ovf_no">[];
};

/**
 * Everything given to the customer for free - a replaced screen, urgent fibre
 * cables, extra visits - with who approved it, so the next deal recovers it.
 */
export function CustomerExpenseLedgerPanel({ companyAccountId, ovfs }: Props) {
  const [rows, setRows] = useState<CustomerExpense[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    expense_date: today(),
    category: "foc_material",
    amount: "",
    approved_by_name: "",
    description: "",
  });
  const [adjustTarget, setAdjustTarget] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      setRows(await listCustomerExpenses(companyAccountId));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load customer expenses");
    }
  }, [companyAccountId]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function run(work: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await work();
      await load();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  const openTotal = rows
    .filter((r) => r.status === "open" && r.adjust_in_future)
    .reduce((sum, r) => sum + Number(r.amount), 0);

  return (
    <div id="customer-expenses">
      <CrmSection title="Customer Expense Ledger (FOC)" icon={HandCoins}>
        {error ? (
          <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
            <TriangleAlert className="size-3.5" /> {error}
          </p>
        ) : null}
        <p className="mb-3 text-xs text-muted-foreground">
          Open to recover in future deals:{" "}
          <span className="font-semibold text-foreground tabular-nums">{formatInrPrecise(openTotal)}</span>
        </p>
        {rows.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-[13px]">
              <thead className="text-[11px] text-muted-foreground uppercase">
                <tr>
                  <th className="py-1.5 pr-3 font-semibold">Date</th>
                  <th className="py-1.5 pr-3 font-semibold">What was given</th>
                  <th className="py-1.5 pr-3 text-right font-semibold">Amount</th>
                  <th className="py-1.5 pr-3 font-semibold">Approved by</th>
                  <th className="py-1.5 pr-3 font-semibold">Status</th>
                  <th className="py-1.5" aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.id} className="border-t border-border/60 align-top">
                    <td className="py-1.5 pr-3 whitespace-nowrap">{row.expense_date}</td>
                    <td className="py-1.5 pr-3">
                      {row.description}
                      <span className="block text-[11px] text-muted-foreground">
                        {CUSTOMER_EXPENSE_CATEGORIES.find((c) => c.value === row.category)?.label ?? row.category}
                        {row.adjustment_remark ? ` · ${row.adjustment_remark}` : ""}
                      </span>
                    </td>
                    <td className="py-1.5 pr-3 text-right tabular-nums">{formatInrPrecise(row.amount)}</td>
                    <td className="py-1.5 pr-3">{row.approved_by_name ?? "-"}</td>
                    <td className="py-1.5 pr-3">
                      <Badge className={`rounded-full border-transparent px-2.5 py-0.5 text-[11px] font-semibold ${STATUS_CLASS[row.status]}`}>
                        {row.status.replace("_", " ")}
                      </Badge>
                    </td>
                    <td className="py-1.5 text-right">
                      {row.status === "open" ? (
                        <div className="flex flex-wrap justify-end gap-1.5">
                          {ovfs.length > 0 ? (
                            <>
                              <select
                                aria-label="OVF that recovered this expense"
                                className={`${SELECT_CLASS} h-7 w-36 text-xs`}
                                value={adjustTarget[row.id] ?? ""}
                                onChange={(e) => setAdjustTarget((m) => ({ ...m, [row.id]: e.target.value }))}
                              >
                                <option value="">Recovered in…</option>
                                {ovfs.map((o) => (
                                  <option key={o.id} value={o.id}>
                                    {o.ovf_no}
                                  </option>
                                ))}
                              </select>
                              <Button
                                type="button"
                                size="sm"
                                variant="outline"
                                disabled={busy || !adjustTarget[row.id]}
                                className="h-7 cursor-pointer text-xs"
                                onClick={() => void run(() => adjustCustomerExpense(row.id, adjustTarget[row.id]))}
                              >
                                Mark recovered
                              </Button>
                            </>
                          ) : null}
                          <Button
                            type="button"
                            size="sm"
                            variant="ghost"
                            disabled={busy}
                            className="h-7 cursor-pointer text-xs"
                            onClick={() => {
                              const reason = window.prompt("Why is this being written off?");
                              if (reason?.trim()) void run(() => writeOffCustomerExpense(row.id, reason.trim()));
                            }}
                          >
                            Write off
                          </Button>
                        </div>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">Nothing given free of cost to this customer yet.</p>
        )}

        <h3 className="mt-4 border-t border-border/70 pt-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
          Record an Expense
        </h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-4">
          <FinanceField label="Date">
            <Input
              type="date"
              max={today()}
              value={form.expense_date}
              onChange={(e) => setForm((f) => ({ ...f, expense_date: e.target.value }))}
              className="h-9 cursor-pointer text-[13px]"
            />
          </FinanceField>
          <FinanceField label="Category">
            <select
              className={SELECT_CLASS}
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
            >
              {CUSTOMER_EXPENSE_CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </FinanceField>
          <FinanceField label="Amount (₹)">
            <Input
              type="number"
              min={0}
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
              className="h-9 text-[13px]"
            />
          </FinanceField>
          <FinanceField label="Approved by *">
            <Input
              value={form.approved_by_name}
              onChange={(e) => setForm((f) => ({ ...f, approved_by_name: e.target.value }))}
              className="h-9 text-[13px]"
            />
          </FinanceField>
          <FinanceField label="What was given and why *" className="sm:col-span-3">
            <FinanceTextarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              placeholder="Replaced broken screen on 1 of 100 desktops, FOC - adjust in next order"
              className="min-h-[56px] text-[13px]"
            />
          </FinanceField>
          <div className="flex items-end">
            <Button
              type="button"
              size="sm"
              variant="outline"
              disabled={busy || !(Number(form.amount) > 0) || !form.description.trim() || !form.approved_by_name.trim()}
              className="cursor-pointer"
              onClick={() =>
                void run(async () => {
                  await createCustomerExpense(companyAccountId, {
                    expense_date: form.expense_date,
                    category: form.category,
                    amount: Number(form.amount),
                    approved_by_name: form.approved_by_name.trim(),
                    description: form.description.trim(),
                  });
                  setForm((f) => ({ ...f, amount: "", description: "" }));
                })
              }
            >
              Add to ledger
            </Button>
          </div>
        </div>
      </CrmSection>
    </div>
  );
}
