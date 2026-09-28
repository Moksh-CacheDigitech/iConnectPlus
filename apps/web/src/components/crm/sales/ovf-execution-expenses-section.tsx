"use client";

import { useCallback, useEffect, useState } from "react";
import { Receipt, TriangleAlert } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { FinanceField, FinanceTextarea } from "@/components/finance/journals/finance-form-field";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import {
  OVF_EXPENSE_TEAMS,
  OVF_EXPENSE_TYPES,
  decideOvfExpense,
  listOvfExpenses,
  raiseOvfExpense,
  type OvfExpense,
} from "@/services/crm-deal-controls-service";
import { formatInrPrecise, type Ovf } from "@/services/sales-crm-service";

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-[13px] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

const STATUS_CLASS: Record<OvfExpense["status"], string> = {
  pending: "bg-amber-100 text-amber-900 dark:bg-amber-900/50 dark:text-amber-100",
  approved: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200",
  rejected: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
};

function label(options: readonly { value: string; label: string }[], value: string): string {
  return options.find((opt) => opt.value === value)?.label ?? value;
}

type Props = {
  ovf: Ovf;
  onChanged: () => void;
};

/**
 * Unplanned cost during execution (extra cables, MATAD, repeat visits). SCM or
 * Operations raise it; the sales owner approves and it comes off the margin.
 */
export function OvfExecutionExpensesSection({ ovf, onChanged }: Props) {
  const live = ["approved", "shared_scm", "deal_won"].includes(ovf.blueprint_state);
  const [rows, setRows] = useState<OvfExpense[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [expenseType, setExpenseType] = useState<string>("cables");
  const [team, setTeam] = useState<string>("scm");
  const [amount, setAmount] = useState("");
  const [incurredOn, setIncurredOn] = useState("");
  const [description, setDescription] = useState("");
  const [rejectRemark, setRejectRemark] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      setRows(await listOvfExpenses(ovf.id));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load expenses");
    }
  }, [ovf.id]);

  useEffect(() => {
    if (!live) return;
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [live, load]);

  if (!live) return null;

  async function run(work: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await work();
      await load();
      onChanged();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  const closed = Boolean(ovf.closed_at);

  return (
    <CrmSection title="Execution Expenses" icon={Receipt}>
      {error ? (
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
          <TriangleAlert className="size-3.5" /> {error}
        </p>
      ) : null}
      {rows.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-[13px]">
            <thead className="text-[11px] text-muted-foreground uppercase">
              <tr>
                <th className="py-1.5 pr-3 font-semibold">Type</th>
                <th className="py-1.5 pr-3 font-semibold">Raised by</th>
                <th className="py-1.5 pr-3 font-semibold">Description</th>
                <th className="py-1.5 pr-3 text-right font-semibold">Amount</th>
                <th className="py-1.5 pr-3 font-semibold">Status</th>
                <th className="py-1.5" aria-label="Decision" />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t border-border/60 align-top">
                  <td className="py-1.5 pr-3">{label(OVF_EXPENSE_TYPES, row.expense_type)}</td>
                  <td className="py-1.5 pr-3">{label(OVF_EXPENSE_TEAMS, row.raised_by_team)}</td>
                  <td className="py-1.5 pr-3">
                    <span className="whitespace-pre-wrap">{row.description}</span>
                    {row.decision_remark ? (
                      <span className="mt-0.5 block text-xs text-muted-foreground">{row.decision_remark}</span>
                    ) : null}
                  </td>
                  <td className="py-1.5 pr-3 text-right tabular-nums">{formatInrPrecise(row.amount)}</td>
                  <td className="py-1.5 pr-3">
                    <Badge className={`rounded-full border-transparent px-2.5 py-0.5 text-[11px] font-semibold capitalize ${STATUS_CLASS[row.status]}`}>
                      {row.status}
                    </Badge>
                  </td>
                  <td className="py-1.5">
                    {row.status === "pending" && !closed ? (
                      <div className="flex flex-wrap items-center justify-end gap-1.5">
                        <Input
                          aria-label="Rejection reason"
                          placeholder="Reason (to reject)"
                          value={rejectRemark[row.id] ?? ""}
                          onChange={(e) => setRejectRemark((m) => ({ ...m, [row.id]: e.target.value }))}
                          className="h-7 w-40 text-xs"
                        />
                        <Button
                          type="button"
                          size="sm"
                          disabled={busy}
                          className="h-7 cursor-pointer text-xs"
                          onClick={() => void run(() => decideOvfExpense(row.id, "approved"))}
                        >
                          Approve
                        </Button>
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          disabled={busy || !(rejectRemark[row.id] ?? "").trim()}
                          className="h-7 cursor-pointer text-xs"
                          onClick={() =>
                            void run(() => decideOvfExpense(row.id, "rejected", rejectRemark[row.id]))
                          }
                        >
                          Reject
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
        <p className="text-xs text-muted-foreground">No execution expenses raised on this deal.</p>
      )}

      {!closed ? (
        <>
          <h3 className="mt-4 border-t border-border/70 pt-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Raise an Expense
          </h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-4">
            <FinanceField label="Type">
              <select className={SELECT_CLASS} value={expenseType} onChange={(e) => setExpenseType(e.target.value)}>
                {OVF_EXPENSE_TYPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </FinanceField>
            <FinanceField label="Raised by">
              <select className={SELECT_CLASS} value={team} onChange={(e) => setTeam(e.target.value)}>
                {OVF_EXPENSE_TEAMS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </FinanceField>
            <FinanceField label="Amount (₹)">
              <Input
                type="number"
                min={0}
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="h-9 text-[13px]"
              />
            </FinanceField>
            <FinanceField label="Incurred on">
              <Input
                type="date"
                value={incurredOn}
                onChange={(e) => setIncurredOn(e.target.value)}
                className="h-9 cursor-pointer text-[13px]"
              />
            </FinanceField>
            <FinanceField label="What was it for? *" className="sm:col-span-3">
              <FinanceTextarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. 40 extra fibre patch cords short-shipped in the BOQ"
                className="min-h-[56px] text-[13px]"
              />
            </FinanceField>
            <div className="flex items-end">
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={busy || !(Number(amount) > 0) || !description.trim()}
                className="cursor-pointer transition-colors duration-200"
                onClick={() =>
                  void run(async () => {
                    await raiseOvfExpense(ovf.id, {
                      expense_type: expenseType,
                      raised_by_team: team,
                      description: description.trim(),
                      amount: Number(amount),
                      incurred_on: incurredOn || null,
                    });
                    setAmount("");
                    setDescription("");
                    setIncurredOn("");
                  })
                }
              >
                Send to owner for approval
              </Button>
            </div>
          </div>
        </>
      ) : null}
    </CrmSection>
  );
}
