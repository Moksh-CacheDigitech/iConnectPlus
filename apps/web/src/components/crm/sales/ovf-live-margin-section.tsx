"use client";

import { useCallback, useEffect, useState } from "react";
import { CalendarClock, CircleCheck, Lock, TrendingDown, TriangleAlert } from "lucide-react";

import { CrmDetailGrid, CrmDetailItem, CrmSection } from "@/components/crm/crm-ui";
import { FinanceField, FinanceTextarea } from "@/components/finance/journals/finance-form-field";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import {
  addOvfPayment,
  getOvfLiveStatus,
  listOvfPayments,
  markOvfFullPayment,
  updateOvfDeliveryDates,
  voidOvfPayment,
  type OvfLiveStatus,
  type OvfPayment,
} from "@/services/crm-deal-controls-service";
import { formatInrPrecise, type Ovf } from "@/services/sales-crm-service";

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function dateOrDash(value: string | null | undefined): string {
  return value ? value.slice(0, 10) : "-";
}

function erosionTone(value: number | null): string {
  if (value == null || value <= 0) return "text-emerald-700 dark:text-emerald-400";
  return "text-red-700 dark:text-red-400";
}

type Props = {
  ovf: Ovf;
  onChanged: () => void;
};

/**
 * Approved margin vs the margin after overdue receivables, stock held for the
 * deal and approved execution expenses. The OVF closes only when Finance
 * records the full payment.
 */
export function OvfLiveMarginSection({ ovf, onChanged }: Props) {
  const approved = ovf.margin_at_approval_amount != null;
  const [status, setStatus] = useState<OvfLiveStatus | null>(null);
  const [payments, setPayments] = useState<OvfPayment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [amount, setAmount] = useState("");
  const [receivedOn, setReceivedOn] = useState(today());
  const [reference, setReference] = useState("");
  const [closeDate, setCloseDate] = useState(today());
  const [closeRemark, setCloseRemark] = useState("");
  const [expectedDate, setExpectedDate] = useState(ovf.expected_delivery_date?.slice(0, 10) ?? "");
  const [actualDate, setActualDate] = useState(ovf.actual_delivery_date?.slice(0, 10) ?? "");
  const [dateReason, setDateReason] = useState("");

  const load = useCallback(async () => {
    try {
      const [live, rows] = await Promise.all([getOvfLiveStatus(ovf.id), listOvfPayments(ovf.id)]);
      setStatus(live);
      setPayments(rows);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load live margin");
    }
  }, [ovf.id]);

  useEffect(() => {
    if (!approved) return;
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [approved, load]);

  if (!approved) return null;

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
  const late = Boolean(status?.payment_due_date && closeDate > (status.payment_due_date ?? ""));
  const expectedChanged = expectedDate !== (ovf.expected_delivery_date?.slice(0, 10) ?? "");

  return (
    <CrmSection title="Live Margin & Collections" icon={TrendingDown}>
      {error ? (
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
          <TriangleAlert className="size-3.5" /> {error}
        </p>
      ) : null}

      {closed ? (
        <p className="mb-3 flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-900 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200">
          <Lock className="size-3.5" /> Full payment received on {dateOrDash(ovf.payment_received_date)} - this
          is the final OVF margin.
        </p>
      ) : null}

      {status ? (
        <CrmDetailGrid>
          <CrmDetailItem label="Margin at Approval">
            {formatInrPrecise(status.margin_at_approval_amount)} ({Number(status.margin_at_approval_pct ?? 0).toFixed(2)}%)
          </CrmDetailItem>
          <CrmDetailItem label={closed ? "Final Margin" : "Live Margin"}>
            <span className="font-semibold tabular-nums">
              {formatInrPrecise(status.live_margin_amount)} ({Number(status.live_margin_pct).toFixed(2)}%)
            </span>
          </CrmDetailItem>
          <CrmDetailItem label="Margin Erosion">
            <span className={`font-semibold tabular-nums ${erosionTone(status.margin_erosion)}`}>
              {formatInrPrecise(status.margin_erosion ?? 0)}
            </span>
          </CrmDetailItem>
          <CrmDetailItem label="Receivable (incl. GST)">{formatInrPrecise(status.customer_receivable)}</CrmDetailItem>
          <CrmDetailItem label="Received">{formatInrPrecise(status.received_amount)}</CrmDetailItem>
          <CrmDetailItem label="Outstanding">{formatInrPrecise(status.outstanding_amount)}</CrmDetailItem>
          <CrmDetailItem label="Overdue">
            {status.overdue_days > 0 ? (
              <Badge className="rounded-full border-transparent bg-red-100 px-2.5 py-0.5 text-[11px] font-semibold text-red-800 dark:bg-red-900/50 dark:text-red-200">
                {status.overdue_days} days
              </Badge>
            ) : (
              "No"
            )}
          </CrmDetailItem>
          <CrmDetailItem label="Cost of Delay (1%/month)">{formatInrPrecise(status.overdue_finance_cost)}</CrmDetailItem>
          <CrmDetailItem label="Stock Holding Cost">{formatInrPrecise(status.holding_cost)}</CrmDetailItem>
          <CrmDetailItem label="Execution Expenses">{formatInrPrecise(status.execution_expense_total)}</CrmDetailItem>
          <CrmDetailItem label="Early-payment Saving">{formatInrPrecise(status.early_payment_saving)}</CrmDetailItem>
          <CrmDetailItem label="As Of">{dateOrDash(status.as_of)}</CrmDetailItem>
        </CrmDetailGrid>
      ) : (
        <div className="h-20 animate-pulse rounded-lg bg-muted/60" />
      )}

      <h3 className="mt-4 border-t border-border/70 pt-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
        Customer Receipts
      </h3>
      {payments.length > 0 ? (
        <div className="mt-2 overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-[13px]">
            <thead className="text-[11px] text-muted-foreground uppercase">
              <tr>
                <th className="py-1.5 pr-3 font-semibold">Received on</th>
                <th className="py-1.5 pr-3 text-right font-semibold">Amount</th>
                <th className="py-1.5 pr-3 font-semibold">Reference</th>
                <th className="py-1.5 pr-3 font-semibold">Remark</th>
                <th className="py-1.5" aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {payments.map((row) => (
                <tr key={row.id} className="border-t border-border/60">
                  <td className="py-1.5 pr-3">{dateOrDash(row.received_date)}</td>
                  <td className="py-1.5 pr-3 text-right tabular-nums">{formatInrPrecise(row.amount)}</td>
                  <td className="py-1.5 pr-3">{row.reference || "-"}</td>
                  <td className="py-1.5 pr-3">{row.remark || "-"}</td>
                  <td className="py-1.5 text-right">
                    {!closed ? (
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        disabled={busy}
                        className="h-7 cursor-pointer text-xs text-red-700 transition-colors duration-200"
                        onClick={() => void run(() => voidOvfPayment(row.id))}
                      >
                        Void
                      </Button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-2 text-xs text-muted-foreground">No receipts recorded yet.</p>
      )}

      {!closed ? (
        <>
          <div className="mt-3 grid gap-3 sm:grid-cols-4">
            <FinanceField label="Amount received (₹)">
              <Input
                type="number"
                min={0}
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="h-9 text-[13px]"
              />
            </FinanceField>
            <FinanceField label="Received on">
              <Input
                type="date"
                max={today()}
                value={receivedOn}
                onChange={(e) => setReceivedOn(e.target.value)}
                className="h-9 cursor-pointer text-[13px]"
              />
            </FinanceField>
            <FinanceField label="UTR / reference">
              <Input value={reference} onChange={(e) => setReference(e.target.value)} className="h-9 text-[13px]" />
            </FinanceField>
            <div className="flex items-end">
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={busy || !(Number(amount) > 0) || !receivedOn}
                className="cursor-pointer transition-colors duration-200"
                onClick={() =>
                  void run(async () => {
                    await addOvfPayment(ovf.id, {
                      amount: Number(amount),
                      received_date: receivedOn,
                      reference: reference.trim() || null,
                    });
                    setAmount("");
                    setReference("");
                  })
                }
              >
                Record receipt
              </Button>
            </div>
          </div>

          <h3 className="mt-4 border-t border-border/70 pt-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Close OVF on Full Payment (Finance)
          </h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            <FinanceField label="Full payment received on">
              <Input
                type="date"
                max={today()}
                value={closeDate}
                onChange={(e) => setCloseDate(e.target.value)}
                className="h-9 cursor-pointer text-[13px]"
              />
            </FinanceField>
            <FinanceField label={late ? "Reason for late payment *" : "Remark"} className="sm:col-span-2">
              <FinanceTextarea
                value={closeRemark}
                onChange={(e) => setCloseRemark(e.target.value)}
                className="min-h-[56px] text-[13px]"
              />
            </FinanceField>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <Button
              type="button"
              size="sm"
              disabled={busy || !closeDate || (late && !closeRemark.trim() && !ovf.payment_delay_reason)}
              className="cursor-pointer transition-colors duration-200"
              onClick={() =>
                void run(() => markOvfFullPayment(ovf.id, { received_date: closeDate, remark: closeRemark.trim() || null }))
              }
            >
              <CircleCheck className="size-3.5" /> Mark full payment received
            </Button>
            <span className="text-xs text-muted-foreground">
              Until then the margin keeps paying 1% a month on anything unpaid past the due date.
            </span>
          </div>
        </>
      ) : null}

      <h3 className="mt-4 flex items-center gap-1.5 border-t border-border/70 pt-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
        <CalendarClock className="size-3.5" /> Delivery Timeline
      </h3>
      <CrmDetailGrid className="mt-2">
        <CrmDetailItem label="Committed Lead Time">{ovf.delivery_period || "-"}</CrmDetailItem>
        <CrmDetailItem label="Expected Delivery">
          <span className={status?.delivery_overdue ? "font-semibold text-red-700 dark:text-red-400" : undefined}>
            {dateOrDash(ovf.expected_delivery_date)}
            {status?.delivery_overdue ? " - overdue" : ""}
          </span>
        </CrmDetailItem>
        <CrmDetailItem label="Actual Delivery">{dateOrDash(ovf.actual_delivery_date)}</CrmDetailItem>
      </CrmDetailGrid>
      {ovf.delivery_date_history && ovf.delivery_date_history.length > 0 ? (
        <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
          {ovf.delivery_date_history.map((entry) => (
            <li key={`${entry.changed_at}-${entry.to}`}>
              {dateOrDash(entry.changed_at)}: moved {dateOrDash(entry.from)} → {dateOrDash(entry.to)} - {entry.reason}
            </li>
          ))}
        </ul>
      ) : null}
      {ovf.shared_to_scm ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-4">
          <FinanceField label="Revised expected date (SCM)">
            <Input
              type="date"
              value={expectedDate}
              onChange={(e) => setExpectedDate(e.target.value)}
              className="h-9 cursor-pointer text-[13px]"
            />
          </FinanceField>
          <FinanceField label={expectedChanged ? "Reason for change *" : "Reason for change"}>
            <Input value={dateReason} onChange={(e) => setDateReason(e.target.value)} className="h-9 text-[13px]" />
          </FinanceField>
          <FinanceField label="Actual delivery">
            <Input
              type="date"
              max={today()}
              value={actualDate}
              onChange={(e) => setActualDate(e.target.value)}
              className="h-9 cursor-pointer text-[13px]"
            />
          </FinanceField>
          <div className="flex items-end">
            <Button
              type="button"
              size="sm"
              variant="outline"
              disabled={busy || (expectedChanged && !dateReason.trim())}
              className="cursor-pointer transition-colors duration-200"
              onClick={() =>
                void run(async () => {
                  await updateOvfDeliveryDates(ovf.id, {
                    expected_delivery_date: expectedChanged ? expectedDate || null : null,
                    actual_delivery_date: actualDate || null,
                    reason: dateReason.trim() || null,
                  });
                  setDateReason("");
                })
              }
            >
              Save delivery dates
            </Button>
          </div>
        </div>
      ) : null}
    </CrmSection>
  );
}
