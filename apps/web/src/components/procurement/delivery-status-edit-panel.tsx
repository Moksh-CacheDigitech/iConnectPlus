"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, MapPinned, Package, Truck } from "lucide-react";

import { DeliveryStatusOutcomeDialog } from "@/components/procurement/delivery-status-outcome-dialog";
import { PageHeader } from "@/components/layout/page-header";
import { procurementUi } from "@/components/procurement/procurement-ui";
import {
  DeliveryStatusForm,
  deliveryStatusToFormValue,
  type AccountsInvoiceDocumentRef,
  type DeliveryStatusFormValue,
} from "@/components/procurement/delivery-status-form";
import { DeliverySectionCard } from "@/components/procurement/delivery-section-card";
import { DeliveryMilestoneCard } from "@/components/procurement/delivery-milestone-card";
import { FinanceField } from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  getInvoiceGenerationTaskForBatch,
  getPurchaseOrder,
  listOrderReceiptBatches,
  listReceiptBatchAttachments,
  openReceiptBatchAttachment,
} from "@/services/procurement-service";
import {
  deliveryStatusGrnItemRowsFromBatches,
  deliveryStatusGrnItemRowsFromChallan,
  matchChallanReceiptBatches,
  resolveChallanReceiptBatches,
  type DeliveryStatusGrnItemRow,
} from "@/utils/delivery-challan-grn";
import {
  getDeliveryChallan,
  type DeliveryChallanRecord,
} from "@/utils/delivery-challan-storage";
import { persistDeliveryStatusFromForm } from "@/utils/delivery-status-persist";
import { setDeliveryStatusFlash } from "@/utils/delivery-status-flash";
import {
  deliveryStatusUiMode,
  isFailedShipmentStatus,
  openStoredDeliveryFile,
  resolveDeliveryStatusForChallan,
  upsertDeliveryStatus,
  validateDeliveryStatusForm,
  type DeliveryStatusFormErrors,
} from "@/utils/delivery-status-storage";

type DeliveryStatusEditPanelProps = {
  challanId: string;
};

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-0.5">
      <div className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div className="text-sm font-medium tabular-nums text-foreground">
        {(value ?? "").trim() || "-"}
      </div>
    </div>
  );
}

export function DeliveryStatusEditPanel({ challanId }: DeliveryStatusEditPanelProps) {
  const router = useRouter();
  const [challan, setChallan] = useState<DeliveryChallanRecord | null>(null);
  const [form, setForm] = useState<DeliveryStatusFormValue | null>(null);
  const [grnItems, setGrnItems] = useState<DeliveryStatusGrnItemRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<DeliveryStatusFormErrors>({});
  const [saving, setSaving] = useState(false);
  const [formPhase, setFormPhase] = useState<"initial" | "tracking">("initial");
  const [outcomeOpen, setOutcomeOpen] = useState(false);
  const [billTick, setBillTick] = useState(0);
  const [orderTracking, setOrderTracking] = useState<{ milestone: string | null; awb: string | null } | null>(null);
  const [accountsInvoiceDocument, setAccountsInvoiceDocument] =
    useState<AccountsInvoiceDocumentRef | null>(null);

  useEffect(() => {
    try {
      const row = getDeliveryChallan(challanId);
      setChallan(row);
      setAccountsInvoiceDocument(null);
      if (!row) {
        setForm(null);
        setGrnItems([]);
        return;
      }
      const seeded = deliveryStatusToFormValue(resolveDeliveryStatusForChallan(row));
      setFormPhase(deliveryStatusUiMode(seeded));
      const fromChallan =
        String(row.purchaseOrderNumber ?? "").trim() &&
          String(row.purchaseOrderNumber ?? "").trim() !==
          String(row.companyPoNumber ?? "").trim()
          ? String(row.purchaseOrderNumber ?? "").trim()
          : "";
      if (!String(seeded.customerPoNumber ?? "").trim() && fromChallan) {
        seeded.customerPoNumber = fromChallan;
      }
      if (!String(seeded.customerName ?? "").trim()) {
        seeded.customerName = String(row.customerName ?? "").trim();
      }
      const challanInvoice = String(row.invoiceNumber ?? "").trim();
      if (challanInvoice && !String(seeded.cacheInvoiceNumber ?? "").trim()) {
        seeded.cacheInvoiceNumber = challanInvoice;
      }
      setForm(seeded);
      setGrnItems(deliveryStatusGrnItemRowsFromChallan(row));
      setError(null);

      const orderId = row.orderId;
      if (!orderId) return;

      let cancelled = false;
      void (async () => {
        try {
          const [order, batches] = await Promise.all([
            getPurchaseOrder(orderId),
            listOrderReceiptBatches(orderId).catch(() => []),
          ]);
          if (cancelled) return;
          setOrderTracking({ milestone: order.delivery_milestone ?? null, awb: order.awb_number ?? null });
          const resolved = resolveChallanReceiptBatches(batches, order);
          const matched = matchChallanReceiptBatches(resolved, row);
          const liveRows = deliveryStatusGrnItemRowsFromBatches(matched, order);
          if (liveRows.length > 0) setGrnItems(liveRows);
          const fromOrder = String(order.customer_po_number ?? "").trim();
          const fromOrderCustomer = String(order.customer_name ?? "").trim();

          let accountsInvoice = "";
          let accountsDoc: AccountsInvoiceDocumentRef | null = null;
          const primaryBatch = matched.find((b) => Boolean(b.id)) || matched[0] || null;
          if (primaryBatch?.id) {
            try {
              const task = await getInvoiceGenerationTaskForBatch(String(primaryBatch.id));
              if (task?.invoice_number) {
                accountsInvoice = String(task.invoice_number).trim();
              }
            } catch {
              /* optional */
            }
            if (!accountsInvoice && primaryBatch.vendor_invoice_number) {
              accountsInvoice = String(primaryBatch.vendor_invoice_number).trim();
            }
            try {
              const attachments =
                primaryBatch.attachments && primaryBatch.attachments.length > 0
                  ? primaryBatch.attachments
                  : await listReceiptBatchAttachments(String(primaryBatch.id));
              const file = attachments[0];
              if (file?.id) {
                accountsDoc = {
                  id: String(file.id),
                  fileName: file.file_name || "Invoice document",
                };
              }
            } catch {
              /* optional */
            }
          }
          if (!accountsInvoice) {
            accountsInvoice = challanInvoice;
          }
          if (!cancelled) setAccountsInvoiceDocument(accountsDoc);

          setForm((prev) => {
            if (!prev) return prev;
            let next = prev;
            if (!String(prev.customerPoNumber ?? "").trim()) {
              const seedPo = fromOrder || fromChallan;
              if (seedPo) next = { ...next, customerPoNumber: seedPo };
            }
            if (!String(prev.customerName ?? "").trim() && fromOrderCustomer) {
              next = { ...next, customerName: fromOrderCustomer };
            }
            if (accountsInvoice) {
              next = { ...next, cacheInvoiceNumber: accountsInvoice };
            }
            return next === prev ? prev : next;
          });
        } catch {
          // Keep challan line items already shown.
        }
      })();

      return () => {
        cancelled = true;
      };
    } catch {
      setChallan(null);
      setForm(null);
      setGrnItems([]);
      setAccountsInvoiceDocument(null);
      setError("Could not load this delivery status record.");
    }
  }, [challanId, billTick]);

  const isBilling = challan?.grnKind === "billing";

  async function onSave() {
    if (!challan || !form || saving) return;
    const errors = validateDeliveryStatusForm(form, {
      requireDispatch: challan.grnKind !== "billing",
    });
    setFieldErrors(errors);
    const message = Object.values(errors).find(Boolean);
    if (message) {
      setError(message);
      return;
    }

    setError(null);
    setSaving(true);
    try {
      const result = await persistDeliveryStatusFromForm(challan, form);
      if (!result.ok) {
        setFieldErrors(result.fieldErrors ?? {});
        setError(result.message);
        setSaving(false);
        return;
      }
      setDeliveryStatusFlash({
        variant: result.emailWarning ? "warning" : "success",
        message: result.emailWarning
          ? `Delivery status saved. Dispatch email failed: ${result.emailWarning}`
          : form.shipmentStatus === "Failed delivery"
            ? "Marked as failed delivery."
            : form.shipmentStatus === "Delivered" && form.requiresInstallation
              ? "Marked delivered. Open Procurement → Installation to fill site details."
              : form.shipmentStatus === "Delivered"
                ? "Marked delivered."
                : "Delivery status saved. DC stays unbilled until the customer bill is taken.",
      });
      router.replace("/procurement/delivery-status");
    } catch {
      setError("Could not save delivery status. Try again.");
      setSaving(false);
    }
  }

  if (!challan) {
    return (
      <div className={procurementUi.page}>
        <PageHeader
          title="Delivery status"
          backHref="/procurement/delivery-status"
          backLabel="Delivery status"
        />
        <p className="text-sm text-muted-foreground">
          Record not found. Return to the list and try again.
        </p>
      </div>
    );
  }

  const readOnly = formPhase === "tracking";

  return (
    <div className={procurementUi.page}>
      <PageHeader
        backHref="/procurement/delivery-status"
        backLabel="Delivery status"
        title={readOnly ? "Delivery status" : "Set dispatch"}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {readOnly ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="cursor-pointer transition-colors duration-200"
                onClick={() => setOutcomeOpen(true)}
              >
                <MapPinned className="mr-1.5 size-3.5" />
                Update status
              </Button>
            ) : null}
          </div>
        }
      />

      {error ? (
        <div className="rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      <DeliverySectionCard title="PO details" icon={FileText}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {readOnly || !form ? (
            <>
              <ReadOnlyField label="Customer name" value={form?.customerName ?? challan.customerName ?? ""} />
              <ReadOnlyField label="Customer PO number" value={form?.customerPoNumber ?? ""} />
            </>
          ) : (
            <>
              <FinanceField label="Customer name" error={fieldErrors.customerName}>
                <Input
                  value={form.customerName ?? ""}
                  onChange={(e) => {
                    const next = { ...form, customerName: e.target.value };
                    setForm(next);
                    if (Object.keys(fieldErrors).length > 0) {
                      setFieldErrors(
                        validateDeliveryStatusForm(next, {
                          requireDispatch: !isBilling,
                        }),
                      );
                    }
                  }}
                  className="h-8"
                  placeholder="Enter customer name"
                />
              </FinanceField>
              <FinanceField label="Customer PO number" error={fieldErrors.customerPoNumber}>
                <Input
                  value={form.customerPoNumber ?? ""}
                  onChange={(e) => {
                    const next = { ...form, customerPoNumber: e.target.value };
                    setForm(next);
                    if (Object.keys(fieldErrors).length > 0) {
                      setFieldErrors(
                        validateDeliveryStatusForm(next, {
                          requireDispatch: !isBilling,
                        }),
                      );
                    }
                  }}
                  className="h-8"
                  placeholder="Enter customer PO number"
                />
              </FinanceField>
            </>
          )}
        </div>
      </DeliverySectionCard>

      <DeliverySectionCard
        title="GRN items"
        icon={Package}
        subtitle="Items received on this GRN"
      >
        <GrnItemsTable rows={grnItems} />
      </DeliverySectionCard>

      {challan.orderId && orderTracking ? (
        <DeliveryMilestoneCard
          orderId={challan.orderId}
          initialMilestone={orderTracking.milestone}
          initialAwb={orderTracking.awb}
          initialCustomerEmail={form?.reminderEmail}
          challan={challan}
          deliveryStatus={form}
          onCustomerEmailChange={(email) => {
            setForm((prev) => (prev ? { ...prev, reminderEmail: email } : prev));
            const existing = resolveDeliveryStatusForChallan(challan);
            upsertDeliveryStatus({ ...existing, reminderEmail: email.trim() });
          }}
        />
      ) : null}

      {form && readOnly ? (
        <DeliverySectionCard title="Cache invoice" icon={FileText}>
          <p className="mb-3 text-xs text-muted-foreground">
            Invoice number and document are entered by Accounts and shown here read-only.
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            <ReadOnlyField label="Invoice number" value={form.cacheInvoiceNumber} />
            <div className="space-y-0.5">
              <div className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                Invoice document
              </div>
              {accountsInvoiceDocument?.id ? (
                <button
                  type="button"
                  className="cursor-pointer text-sm font-medium text-[#0369A1] underline-offset-2 transition-colors duration-150 hover:underline"
                  onClick={() => void openReceiptBatchAttachment(accountsInvoiceDocument.id)}
                >
                  {accountsInvoiceDocument.fileName}
                </button>
              ) : form.cacheInvoiceDocument?.fileName ? (
                <button
                  type="button"
                  className="cursor-pointer text-sm font-medium text-[#0369A1] underline-offset-2 transition-colors duration-150 hover:underline"
                  onClick={() => openStoredDeliveryFile(form.cacheInvoiceDocument!)}
                >
                  {form.cacheInvoiceDocument.fileName}
                </button>
              ) : (
                <div className="text-sm text-muted-foreground">Not attached by Accounts yet</div>
              )}
            </div>
          </div>
        </DeliverySectionCard>
      ) : null}

      {form && readOnly && !isBilling ? (
        <DeliverySectionCard title="Dispatch detail" icon={Truck}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <ReadOnlyField
              label="Mode"
              value={form.deliveryMode === "hand" ? "By hand" : form.deliveryMode === "courier" ? "Courier" : ""}
            />
            <ReadOnlyField label="Estimated delivery date" value={form.expectedDeliveryDate} />
            <ReadOnlyField label="Dispatch date" value={form.dispatchDate} />
            <ReadOnlyField
              label="Delivery status"
              value={
                isFailedShipmentStatus(form.shipmentStatus)
                  ? "Failed delivery"
                  : form.shipmentStatus === "Delivered" || form.actualDeliveryDate?.trim()
                    ? "Delivered"
                    : form.shipmentStatus || "In transit"
              }
            />
            <ReadOnlyField label="Delivered date" value={form.actualDeliveryDate} />
            <ReadOnlyField
              label="Requires installation"
              value={form.requiresInstallation ? "Yes" : "No"}
            />
            {form.deliveryMode === "hand" ? (
              <>
                <ReadOnlyField label="Delivery person" value={form.deliveryBoyName} />
                <ReadOnlyField label="Item" value={form.itemType} />
                <div className="space-y-0.5">
                  <div className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                    POD
                  </div>
                  {form.podDocument ? (
                    <button
                      type="button"
                      className="cursor-pointer text-sm font-medium text-[#0369A1] transition-colors duration-200 hover:underline"
                      onClick={() => openStoredDeliveryFile(form.podDocument!)}
                    >
                      {form.podDocument.fileName}
                    </button>
                  ) : (
                    <div className="text-sm font-medium text-foreground">-</div>
                  )}
                </div>
              </>
            ) : null}
            {form.deliveryMode === "courier" ? (
              <>
                <ReadOnlyField label="Courier" value={form.courierProvider} />
                <ReadOnlyField label="Docket number" value={form.docketNumber} />
              </>
            ) : null}
            <ReadOnlyField label="No. of boxes" value={form.boxCount} />
            <ReadOnlyField label="Mode of surface" value={form.surfaceMode} />
            <ReadOnlyField label="Remarks" value={form.remarks} />
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Dispatch is locked after save. Use Update status to mark Delivered or Failed.
          </p>
        </DeliverySectionCard>
      ) : null}

      {form && !readOnly ? (
        <>
          <DeliveryStatusForm
            mode="initial"
            value={form}
            showDispatchDetail={!isBilling}
            accountsInvoiceDocument={accountsInvoiceDocument}
            onOpenAccountsInvoiceDocument={(id) => {
              void openReceiptBatchAttachment(id);
            }}
            onChange={(next) => {
              setForm(next);
              if (Object.keys(fieldErrors).length > 0) {
                setFieldErrors(
                  validateDeliveryStatusForm(next, {
                    requireDispatch: !isBilling,
                  }),
                );
              }
            }}
            fieldErrors={fieldErrors}
          />
          <div className="flex justify-end">
            <Button
              type="button"
              size="sm"
              className="cursor-pointer transition-colors duration-200"
              disabled={saving}
              onClick={() => void onSave()}
            >
              {saving ? "Saving…" : "Save"}
            </Button>
          </div>
        </>
      ) : null}

      <DeliveryStatusOutcomeDialog
        open={outcomeOpen}
        challan={challan}
        onClose={() => setOutcomeOpen(false)}
        onSaved={(message) => {
          setDeliveryStatusFlash({ variant: "success", message });
          setOutcomeOpen(false);
          setBillTick((n) => n + 1);
          router.replace("/procurement/delivery-status");
        }}
      />
    </div>
  );
}

function GrnItemsTable({ rows }: { rows: DeliveryStatusGrnItemRow[] }) {
  if (rows.length === 0) {
    return <p className="text-sm text-muted-foreground">No GRN items recorded yet.</p>;
  }

  return (
    <div className={procurementUi.tableShell}>
      <div className={procurementUi.tableScroll}>
        <table className={cn(procurementUi.table, "min-w-[560px]")}>
          <thead className={procurementUi.thead}>
            <tr>
              <th className={procurementUi.th}>Product name</th>
              <th className={procurementUi.th}>Description</th>
              <th className={cn(procurementUi.th, "w-24 text-right")}>GRN qty</th>
              <th className={cn(procurementUi.th, "w-28 text-right")}>Unit rate</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className={procurementUi.tr}>
                <td className={procurementUi.td}>{row.product}</td>
                <td className={procurementUi.tdMuted}>{row.description || "-"}</td>
                <td className={cn(procurementUi.tdNumeric, "text-right font-medium")}>
                  {row.grnQty}
                </td>
                <td className={cn(procurementUi.tdNumeric, "text-right")}>{row.unitCost}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
