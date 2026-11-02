"use client";

/** Delivery challan queue - pending + saved DCs with generated GRN numbers. */

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FileDown, FilePlus2, FileText, RefreshCw, Truck } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { procurementUi } from "@/components/procurement/procurement-ui";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  getInvoiceGenerationTaskForBatch,
  listInvoiceGenerationTasksForOrder,
  listProcurementInventory,
  type ProcInvoiceGenerationTask,
  type ProcurementInventoryRow,
} from "@/services/procurement-service";
import {
  buildDeliveryChallanPdfInputFromRecordResolved,
  downloadDeliveryChallanPdf,
} from "@/utils/delivery-challan-pdf";
import {
  getDeliveryChallan,
  upsertDeliveryChallan,
  type DeliveryChallanRecord,
  type GrnChallanKind,
} from "@/utils/delivery-challan-storage";
import {
  listDeliveryChallanQueueByKind,
  patchPendingGrnChallan,
  pendingGrnChallanHref,
  type PendingGrnChallan,
} from "@/utils/grn-challan-pending";
import {
  formatGeneratedGrnNumbers,
  isGeneratedGrnNumber,
  resolveDisplayGrnNumbers,
  uniqueGeneratedGrnNumbers,
} from "@/utils/grn-number-display";
import { formatUniquePoLabels } from "@/utils/format-po-labels";

const LIST_RETURN_TO = encodeURIComponent("/procurement/delivery-challan");

type QueueTab = GrnChallanKind;

/** Pending billing row id -> Accounts invoice task details for the list. */
type BillingInvoiceReadyMap = Record<
  string,
  {
    ready: boolean;
    invoiceNumber?: string;
    invoiceDate?: string;
    itemsSummary?: string;
    quantity?: number;
    amount?: number;
    grnNumber?: string;
    status?: string;
  }
>;

function looksLikeUuid(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
    value.trim(),
  );
}

function formatBillingQty(value: number | undefined): string {
  if (value == null || !Number.isFinite(value) || value <= 0) return "-";
  return Number.isInteger(value) ? String(value) : String(Math.round(value * 1e4) / 1e4);
}

function formatBillingAmount(value: number | undefined): string {
  if (value == null || !Number.isFinite(value) || value <= 0) return "-";
  return value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function pickInvoiceTaskForRow(
  row: PendingGrnChallan,
  tasks: ProcInvoiceGenerationTask[],
): ProcInvoiceGenerationTask | null {
  if (tasks.length === 0) return null;
  const batchId = row.batchKey?.trim() || "";
  if (looksLikeUuid(batchId)) {
    const byBatch = tasks.find((t) => String(t.receipt_batch_id) === batchId);
    if (byBatch) return byBatch;
  }
  const summary = (row.itemsSummary || "").trim().toLowerCase();
  if (summary && summary !== "-") {
    const bySummary = tasks.find(
      (t) => (t.items_summary || "").trim().toLowerCase() === summary,
    );
    if (bySummary) return bySummary;
  }
  const pending = tasks.find((t) => t.status === "pending");
  if (pending) return pending;
  const completed = tasks.find((t) => t.status === "completed");
  return completed || tasks[0] || null;
}

function taskBillingMeta(task: ProcInvoiceGenerationTask | null): BillingInvoiceReadyMap[string] {
  if (!task) return { ready: false };
  const qty =
    Number(task.suggested_quantity) > 0
      ? Number(task.suggested_quantity)
      : Number(task.invoice_quantity) > 0
        ? Number(task.invoice_quantity)
        : undefined;
  const amount =
    Number(task.suggested_amount) > 0
      ? Number(task.suggested_amount)
      : Number(task.invoice_amount) > 0
        ? Number(task.invoice_amount)
        : undefined;
  const invoiceNumber = task.invoice_number?.trim() || undefined;
  const invoiceDate = task.invoice_date?.slice(0, 10) || undefined;
  const ready = task.status === "completed" && Boolean(invoiceNumber || invoiceDate);
  return {
    ready,
    invoiceNumber,
    invoiceDate,
    itemsSummary: task.items_summary?.trim() || undefined,
    quantity: qty,
    amount,
    grnNumber: task.grn_number?.trim() || undefined,
    status: task.status,
  };
}

function enrichQueueRowsWithGeneratedGrns(
  rows: PendingGrnChallan[],
  inventory: ProcurementInventoryRow[],
): PendingGrnChallan[] {
  return rows.map((row) => {
    const saved =
      row.savedRecordId ? getDeliveryChallan(row.savedRecordId) : null;
    const numbers = resolveDisplayGrnNumbers({
      stored: [row.grnNumber, ...(saved?.selectedGrnNumbers || [])],
      orderId: row.orderId || saved?.orderId,
      inventory,
    });
    const label = formatGeneratedGrnNumbers(numbers);

    if (numbers.length > 0) {
      if (!isGeneratedGrnNumber(row.grnNumber) || row.grnNumber !== label) {
        patchPendingGrnChallan(row.orderId, row.batchKey, row.kind, {
          grnNumber: label,
        });
      }
      if (
        saved &&
        uniqueGeneratedGrnNumbers(saved.selectedGrnNumbers).join("\0") !== numbers.join("\0")
      ) {
        upsertDeliveryChallan({
          ...saved,
          selectedGrnNumbers: numbers,
        });
      }
    }

    return { ...row, grnNumber: label };
  });
}

export function DeliveryChallanListPage() {
  const [tab, setTab] = useState<QueueTab>("delivery_challan");
  const [pendingBilling, setPendingBilling] = useState<PendingGrnChallan[]>([]);
  const [pendingDc, setPendingDc] = useState<PendingGrnChallan[]>([]);
  const [billingInvoiceReady, setBillingInvoiceReady] = useState<BillingInvoiceReadyMap>({});
  const [pdfBusyId, setPdfBusyId] = useState<string | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [accountsNotice, setAccountsNotice] = useState<string | null>(null);

  async function onDownloadPdf(challan: DeliveryChallanRecord) {
    setPdfBusyId(challan.id);
    setPdfError(null);
    try {
      const input = await buildDeliveryChallanPdfInputFromRecordResolved(challan);
      await downloadDeliveryChallanPdf(input);
    } catch (err) {
      setPdfError(
        err instanceof Error
          ? err.message
          : "Failed to download PDF",
      );
    } finally {
      setPdfBusyId(null);
    }
  }

  useEffect(() => {
    try {
      const msg = sessionStorage.getItem("erp.procurement.accounts-invoice-notified");
      if (msg) {
        sessionStorage.removeItem("erp.procurement.accounts-invoice-notified");
        setAccountsNotice(msg);
      }
    } catch {
      /* ignore */
    }
  }, []);

  const load = useCallback(async () => {
    const billing = listDeliveryChallanQueueByKind("billing");
    const dc = listDeliveryChallanQueueByKind("delivery_challan");
    setPendingBilling(billing);
    setPendingDc(dc);

    let nextBilling = billing;
    let nextDc = dc;
    try {
      const inventory = await listProcurementInventory();
      nextBilling = enrichQueueRowsWithGeneratedGrns(billing, inventory);
      nextDc = enrichQueueRowsWithGeneratedGrns(dc, inventory);
      setPendingBilling(nextBilling);
      setPendingDc(nextDc);
    } catch {
      /* keep local queue rows if inventory is unavailable */
    }

    const billingRowsForMeta = nextBilling.filter(
      (r) => !r.status || r.status === "pending" || r.status === "saved",
    );
    const readiness: BillingInvoiceReadyMap = {};
    const orderIds = [
      ...new Set(
        billingRowsForMeta
          .map((row) => row.orderId?.trim())
          .filter((id): id is string => Boolean(id) && looksLikeUuid(id)),
      ),
    ];
    const tasksByOrder = new Map<string, ProcInvoiceGenerationTask[]>();
    await Promise.all(
      orderIds.map(async (orderId) => {
        try {
          const tasks = await listInvoiceGenerationTasksForOrder(orderId);
          tasksByOrder.set(orderId, tasks);
        } catch {
          tasksByOrder.set(orderId, []);
        }
      }),
    );

    await Promise.all(
      billingRowsForMeta.map(async (row) => {
        const orderId = row.orderId?.trim() || "";
        let task = pickInvoiceTaskForRow(row, tasksByOrder.get(orderId) || []);
        const batchId = row.batchKey?.trim() || "";
        if (!task && looksLikeUuid(batchId)) {
          try {
            task = await getInvoiceGenerationTaskForBatch(batchId);
          } catch {
            task = null;
          }
        }
        const meta = taskBillingMeta(task);
        if (!meta.itemsSummary && row.itemsSummary?.trim()) {
          meta.itemsSummary = row.itemsSummary.trim();
        }
        if (!meta.grnNumber && row.grnNumber?.trim() && row.grnNumber !== "-") {
          meta.grnNumber = row.grnNumber.trim();
        }
        if (
          (meta.quantity == null || meta.quantity <= 0) &&
          meta.itemsSummary
        ) {
          const parsed = [...meta.itemsSummary.matchAll(/\((\d+(?:\.\d+)?)\)/g)].map(
            (m) => Number(m[1]),
          );
          const sum = parsed.reduce((a, b) => a + (Number.isFinite(b) ? b : 0), 0);
          if (sum > 0) meta.quantity = sum;
        }
        readiness[row.id] = meta;
        if (meta.ready && (meta.invoiceNumber || meta.invoiceDate)) {
          patchPendingGrnChallan(row.orderId, row.batchKey, "billing", {
            docNumber: meta.invoiceNumber || row.docNumber,
            docDate: meta.invoiceDate || row.docDate,
          });
        }
      }),
    );
    setBillingInvoiceReady(readiness);
    if (Object.values(readiness).some((r) => r.ready)) {
      setPendingBilling(listDeliveryChallanQueueByKind("billing"));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const pendingForTab = tab === "billing" ? pendingBilling : pendingDc;
  const openRows = pendingForTab
    .filter((r) => !r.status || r.status === "pending")
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  const historyRows = pendingForTab
    .filter((r) => r.status === "saved")
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  const pendingDcCount = pendingDc.filter((r) => !r.status || r.status === "pending").length;
  const pendingBillingCount = pendingBilling.filter((r) => !r.status || r.status === "pending").length;

  return (
    <div className={procurementUi.page}>
      <PageHeader
        title="Delivery"
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="cursor-pointer transition-colors duration-200"
              onClick={() => void load()}
            >
              <RefreshCw className="mr-1.5 size-3.5" />
              Refresh
            </Button>
            <Link
              href={`/procurement/delivery-challan/new?kind=${tab}&returnTo=${LIST_RETURN_TO}`}
              className={cn(
                buttonVariants({ size: "sm" }),
                "cursor-pointer transition-colors duration-200",
              )}
            >
              <FilePlus2 className="mr-1.5 size-3.5" />
              Create
            </Link>
          </div>
        }
      />

      <div
        className="flex flex-wrap gap-2"
        role="tablist"
        aria-label="Delivery challan or billing"
      >
        <Button
          type="button"
          role="tab"
          aria-selected={tab === "delivery_challan"}
          size="sm"
          variant={tab === "delivery_challan" ? "default" : "outline"}
          className="cursor-pointer transition-colors duration-200"
          onClick={() => setTab("delivery_challan")}
        >
          <Truck className="mr-1.5 size-3.5" />
          Delivery challan
          {pendingDcCount > 0 ? (
            <span className="ml-1.5 rounded-md bg-background/20 px-1.5 py-0.5 text-[10px] font-semibold tabular-nums">
              {pendingDcCount}
            </span>
          ) : null}
        </Button>
        <Button
          type="button"
          role="tab"
          aria-selected={tab === "billing"}
          size="sm"
          variant={tab === "billing" ? "default" : "outline"}
          className="cursor-pointer transition-colors duration-200"
          onClick={() => setTab("billing")}
        >
          <FileText className="mr-1.5 size-3.5" />
          Billing
          {pendingBillingCount > 0 ? (
            <span className="ml-1.5 rounded-md bg-background/20 px-1.5 py-0.5 text-[10px] font-semibold tabular-nums">
              {pendingBillingCount}
            </span>
          ) : null}
        </Button>
      </div>

      {accountsNotice ? (
        <div
          role="status"
          className="rounded-xl border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950"
        >
          {accountsNotice}
        </div>
      ) : null}

      <p className="text-sm text-muted-foreground">
        Delivery challan = item delivered without taking a bill.
        {tab === "billing" ? (
          <>
            {" "}
            Billing stays <span className="font-medium text-foreground">Pending</span> until
            Accounts completes invoice details in My Jobs.
          </>
        ) : null}
      </p>

      {pdfError ? (
        <div className="rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {pdfError}
        </div>
      ) : null}

      <PendingGrnQueueCard
        label={tab === "billing" ? "Pending billing" : "Pending delivery challans"}
        rows={openRows}
        isBilling={tab === "billing"}
        actionLabel="Open"
        billingInvoiceReady={billingInvoiceReady}
        requireInvoiceReady={tab === "billing"}
        pdfBusyId={pdfBusyId}
        onDownloadPdf={onDownloadPdf}
        emptyLabel={
          tab === "billing"
            ? "No pending billing documents."
            : "No pending delivery challans."
        }
      />

      <PendingGrnQueueCard
        label={tab === "billing" ? "Billing history" : "Delivery challan history"}
        rows={historyRows}
        isBilling={tab === "billing"}
        actionLabel="View"
        billingInvoiceReady={billingInvoiceReady}
        requireInvoiceReady={false}
        pdfBusyId={pdfBusyId}
        onDownloadPdf={onDownloadPdf}
        emptyLabel={
          tab === "billing"
            ? "No saved billing documents yet. Create or complete a billing document to see it here."
            : "No saved delivery challans yet. Create or complete a DC to see it here."
        }
      />
    </div>
  );
}

function PendingGrnQueueCard({
  label,
  rows,
  isBilling,
  actionLabel,
  emptyLabel,
  billingInvoiceReady,
  requireInvoiceReady,
  pdfBusyId,
  onDownloadPdf,
}: {
  label: string;
  rows: PendingGrnChallan[];
  isBilling: boolean;
  actionLabel: string;
  emptyLabel: string;
  billingInvoiceReady: BillingInvoiceReadyMap;
  requireInvoiceReady: boolean;
  pdfBusyId: string | null;
  onDownloadPdf: (challan: DeliveryChallanRecord) => void | Promise<void>;
}) {
  const router = useRouter();

  return (
    <div className="space-y-2">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </h2>
      <div className={procurementUi.tableShell} aria-label={label}>
        <div className={procurementUi.tableScroll}>
          <table className={cn(procurementUi.table, isBilling ? "min-w-[1100px]" : "min-w-[980px]")}>
            <thead className={procurementUi.thead}>
              <tr>
                <th className={procurementUi.th}>{isBilling ? "Invoice number" : "Challan number"}</th>
                <th className={procurementUi.th}>{isBilling ? "Invoice date" : "Challan date"}</th>
                <th className={procurementUi.th}>PO number</th>
                {isBilling ? (
                  <>
                    <th className={procurementUi.th}>Items</th>
                    <th className={procurementUi.th}>Qty</th>
                    <th className={procurementUi.th}>Amount</th>
                  </>
                ) : null}
                <th className={procurementUi.th}>Vendor name</th>
                <th className={procurementUi.th}>Customer name</th>
                <th className={procurementUi.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={isBilling ? 9 : 6} className={procurementUi.empty}>
                    {emptyLabel}
                  </td>
                </tr>
              ) : (
                rows.map((row) => {
                  const isSaved = row.status === "saved";
                  const invoiceMeta = billingInvoiceReady[row.id];
                  const canOpen =
                    !requireInvoiceReady || isSaved || Boolean(invoiceMeta?.ready);
                  const href = isSaved && row.savedRecordId
                    ? `/procurement/delivery-challan/${row.savedRecordId}`
                    : pendingGrnChallanHref(row);
                  const savedChallan =
                    isSaved && row.savedRecordId ? getDeliveryChallan(row.savedRecordId) : null;
                  const displayInvoiceNumber =
                    row.docNumber ||
                    invoiceMeta?.invoiceNumber ||
                    "-";
                  const displayInvoiceDate =
                    row.docDate ||
                    invoiceMeta?.invoiceDate ||
                    "-";
                  const rawItems =
                    invoiceMeta?.itemsSummary ||
                    row.itemsSummary?.trim() ||
                    "-";
                  const displayItems =
                    rawItems === "-"
                      ? "-"
                      : rawItems.replace(/\s*\(\d+(?:\.\d+)?\)/g, "").trim() || rawItems;
                  const pdfBusy = Boolean(savedChallan && pdfBusyId === savedChallan.id);
                  return (
                    <tr
                      key={row.id}
                      className={cn(
                        procurementUi.tr,
                        canOpen
                          ? "cursor-pointer"
                          : "cursor-default opacity-95",
                      )}
                      role={canOpen ? "link" : undefined}
                      tabIndex={canOpen ? 0 : undefined}
                      onClick={() => {
                        if (!canOpen) return;
                        router.push(href);
                      }}
                      onKeyDown={(e) => {
                        if (!canOpen) return;
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          router.push(href);
                        }
                      }}
                    >
                      <td className={cn(procurementUi.td, "font-medium tabular-nums", isSaved || canOpen ? "text-foreground" : "text-muted-foreground")}>
                        {isBilling ? displayInvoiceNumber : row.docNumber || "-"}
                      </td>
                      <td className={cn(procurementUi.tdNumeric, "text-muted-foreground")}>
                        {isBilling ? displayInvoiceDate : row.docDate || "-"}
                      </td>
                      <td className={cn(procurementUi.td, "max-w-[180px] font-medium tabular-nums")}>
                        {formatUniquePoLabels(row.purchaseOrderNumber)}
                      </td>
                      {isBilling ? (
                        <>
                          <td className={cn(procurementUi.td, "max-w-[220px]")}>
                            <span className="line-clamp-2" title={displayItems}>
                              {displayItems}
                            </span>
                          </td>
                          <td className={cn(procurementUi.tdNumeric, "tabular-nums")}>
                            {formatBillingQty(invoiceMeta?.quantity)}
                          </td>
                          <td className={cn(procurementUi.tdNumeric, "tabular-nums")}>
                            {formatBillingAmount(invoiceMeta?.amount)}
                          </td>
                        </>
                      ) : null}
                      <td className={procurementUi.tdMuted}>{row.vendorName || "-"}</td>
                      <td className={procurementUi.td}>{row.customerName?.trim() || "-"}</td>
                      <td className={procurementUi.td} onClick={(e) => e.stopPropagation()}>
                        <div className={procurementUi.rowActions}>
                          {canOpen ? (
                            <Link
                              href={href}
                              className={cn(
                                buttonVariants({ size: "sm", variant: "ghost" }),
                                procurementUi.actionBtn,
                                "text-[#0369A1] hover:text-[#0369A1]",
                              )}
                            >
                              {actionLabel}
                            </Link>
                          ) : (
                            <span
                              className="inline-flex h-8 items-center px-2 text-xs font-medium text-muted-foreground"
                              title="Waiting for Accounts to submit invoice details in My Jobs"
                            >
                              Pending
                            </span>
                          )}
                          {savedChallan ? (
                            <Button
                              type="button"
                              size="sm"
                              variant="ghost"
                              disabled={pdfBusy}
                              className={cn(
                                procurementUi.actionBtn,
                                "cursor-pointer text-[#0369A1] hover:text-[#0369A1]",
                              )}
                              title={isBilling ? "Download billing PDF" : "Download challan PDF"}
                              aria-label={
                                isBilling
                                  ? `Download billing PDF for ${displayInvoiceNumber}`
                                  : `Download challan PDF for ${row.docNumber || savedChallan.challanNumber}`
                              }
                              onClick={() => void onDownloadPdf(savedChallan)}
                            >
                              <FileDown className="mr-1 size-3.5" />
                              {pdfBusy ? "PDF…" : "PDF"}
                            </Button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
