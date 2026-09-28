"use client";

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";

import { InventorySerialEditor } from "@/components/procurement/inventory-serial-editor";
import { procurementUi } from "@/components/procurement/procurement-ui";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { formatInr } from "@/services/procurement-service";
import {
  formatInventoryDateAdded,
  formatInventoryWarrantyLabel,
  inventoryAddedByLabel,
  inventoryRowAddedBy,
  inventoryRowStableKey,
  isInventoryWarrantyExpired,
  nonBilledStockQuantity,
  type GrnStockByProductRow,
} from "@/utils/procurement-inventory-report";

function displaySerial(value: string | null | undefined): string {
  const text = (value ?? "").trim();
  if (!text || text.toUpperCase() === "NA" || text === "-" || text === "-") return "-";
  return text;
}

type InventoryProductDetailDialogProps = {
  open: boolean;
  product: GrnStockByProductRow | null;
  onClose: () => void;
  onRefresh: () => void;
  onError: (message: string | null) => void;
};

export function InventoryProductDetailDialog({
  open,
  product,
  onClose,
  onRefresh,
  onError,
}: InventoryProductDetailDialogProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  const unitRows = useMemo(() => {
    if (!product) return [];
    return [...product.lines].sort((a, b) => {
      const po = (a.company_po_number ?? "").localeCompare(b.company_po_number ?? "", undefined, {
        numeric: true,
      });
      if (po !== 0) return po;
      const grn = (a.grn_number ?? "").localeCompare(b.grn_number ?? "", undefined, {
        numeric: true,
      });
      if (grn !== 0) return grn;
      return displaySerial(a.serial_number).localeCompare(displaySerial(b.serial_number));
    });
  }, [product]);

  if (!open || !mounted || !product) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-foreground/40 p-4"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="inventory-product-detail-title"
        className="flex max-h-[min(90vh,720px)] w-full max-w-5xl flex-col rounded-xl border border-border/80 bg-card shadow-lg"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex shrink-0 items-start justify-between gap-3 border-b border-border/60 px-5 py-4">
          <div className="min-w-0">
            <div className="flex min-w-0 flex-wrap items-center gap-2">
              <span
                className={cn(
                  "inline-flex shrink-0 rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                  product.addedBy === "po"
                    ? "border-sky-200 bg-sky-50 text-sky-800"
                    : product.addedBy === "manual"
                      ? "border-border/80 bg-muted/60 text-muted-foreground"
                      : "border-amber-200 bg-amber-50 text-amber-900",
                )}
              >
                {inventoryAddedByLabel(product.addedBy)}
              </span>
              <h2
                id="inventory-product-detail-title"
                className="text-base font-semibold tracking-tight"
              >
                {product.productName}
              </h2>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {product.stockQty.toLocaleString("en-IN")} unit{product.stockQty === 1 ? "" : "s"} on
              hand · avg {formatInr(product.avgUnitCost)}
            </p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="size-8 shrink-0 cursor-pointer"
            aria-label="Close"
            onClick={onClose}
          >
            <X className="size-4" />
          </Button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          <p className="mb-3 text-xs text-muted-foreground">
            Source breakdown by company PO, GRN, serial, warranty, and vendor rate.
          </p>
          <div className={procurementUi.tableShell}>
            <div className="overflow-x-auto">
              <table className={cn(procurementUi.table, "w-full min-w-[720px] table-fixed")}>
                <colgroup>
                  <col className="w-[72px]" />
                  <col className="w-[14%]" />
                  <col className="w-[12%]" />
                  <col className="w-[18%]" />
                  <col className="w-[12%]" />
                  <col className="w-[14%]" />
                  <col className="w-[56px]" />
                  <col className="w-[12%]" />
                </colgroup>
                <thead className={procurementUi.thead}>
                  <tr>
                    <th className={cn(procurementUi.th, "px-2")}>Source</th>
                    <th className={cn(procurementUi.th, "px-2")}>Company PO</th>
                    <th className={cn(procurementUi.th, "px-2")}>GRN</th>
                    <th className={cn(procurementUi.th, "px-2")}>Serial</th>
                    <th className={cn(procurementUi.th, "px-2")}>Date added</th>
                    <th className={cn(procurementUi.th, "px-2")}>Warranty until</th>
                    <th className={cn(procurementUi.th, "px-2 text-right")}>Qty</th>
                    <th className={cn(procurementUi.th, "px-2 text-right")}>Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {unitRows.map((row, index) => {
                    const addedBy = inventoryRowAddedBy(row);
                    const expired = isInventoryWarrantyExpired(row.warranty_valid_till);
                    return (
                      <tr
                        key={inventoryRowStableKey(row, index)}
                        className={cn(procurementUi.tr, expired && "bg-destructive/5")}
                      >
                        <td className={cn(procurementUi.td, "px-2")}>
                          <span
                            className={cn(
                              "inline-flex rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                              addedBy === "po"
                                ? "border-sky-200 bg-sky-50 text-sky-800"
                                : "border-border/80 bg-muted/60 text-muted-foreground",
                            )}
                          >
                            {addedBy === "po" ? "PO" : "Manual"}
                          </span>
                        </td>
                        <td
                          className={cn(
                            procurementUi.td,
                            "max-w-0 truncate px-2 font-mono text-xs tabular-nums",
                          )}
                          title={row.company_po_number?.trim() || undefined}
                        >
                          {row.company_po_number?.trim() || "-"}
                        </td>
                        <td
                          className={cn(
                            procurementUi.td,
                            "max-w-0 truncate px-2 font-mono text-xs tabular-nums",
                          )}
                          title={row.grn_number?.trim() || undefined}
                        >
                          {row.grn_number?.trim() || "-"}
                          {row.source === "grn_reversal" ? (
                            <span className="ml-1 text-[10px] font-medium uppercase text-destructive">
                              Rev
                            </span>
                          ) : null}
                        </td>
                        <td className={cn(procurementUi.td, "min-w-0 px-2")}>
                          <InventorySerialEditor
                            row={row}
                            onSaved={onRefresh}
                            onError={onError}
                          />
                        </td>
                        <td
                          className={cn(
                            procurementUi.td,
                            "px-2 text-xs text-muted-foreground",
                          )}
                        >
                          {formatInventoryDateAdded(row.receipt_at)}
                        </td>
                        <td
                          className={cn(
                            procurementUi.td,
                            "px-2 text-xs font-medium",
                            expired ? "text-destructive" : "text-muted-foreground",
                          )}
                        >
                          {formatInventoryWarrantyLabel(row.warranty_valid_till)}
                        </td>
                        <td
                          className={cn(
                            procurementUi.tdNumeric,
                            "px-2 text-right font-mono tabular-nums",
                          )}
                        >
                          {nonBilledStockQuantity(row).toLocaleString("en-IN")}
                        </td>
                        <td
                          className={cn(
                            procurementUi.tdNumeric,
                            "px-2 text-right font-mono tabular-nums",
                          )}
                        >
                          {formatInr(Number(row.unit_cost) || 0)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="flex shrink-0 justify-end border-t border-border/60 px-5 py-3">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="cursor-pointer transition-colors duration-200"
            onClick={onClose}
          >
            Close
          </Button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
