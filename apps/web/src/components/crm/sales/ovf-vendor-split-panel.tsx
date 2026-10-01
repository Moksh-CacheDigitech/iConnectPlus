"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Split, Trash2, TriangleAlert } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { FinanceField } from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import { splitOvfVendorLine, type OvfVendorSplit } from "@/services/crm-deal-controls-service";
import { formatInrPrecise, listOvfLines, type Ovf, type OvfLine } from "@/services/sales-crm-service";

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-[13px] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

type SplitDraft = { key: string; distributor_name: string; qty: string; unit_price: string };

type Props = {
  ovf: Ovf;
  /** Kept for API compatibility with the detail page; distributors come from Vendor PO rows. */
  distributorOptions?: string[];
  onChanged: () => void;
};

/**
 * Break one Customer PO line across distributors already named on Vendor PO Summary.
 * Qty / unit purchase only — distributor names are not re-entered here.
 */
export function OvfVendorSplitPanel({ ovf, onChanged }: Props) {
  const editable = ovf.blueprint_state === "draft" && !ovf.locked && !ovf.shared_to_scm && !ovf.deal_won;
  const [lines, setLines] = useState<OvfLine[]>([]);
  const [customerLineId, setCustomerLineId] = useState("");
  const [drafts, setDrafts] = useState<SplitDraft[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setLines(await listOvfLines(ovf.id));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load OVF lines");
    }
  }, [ovf.id]);

  useEffect(() => {
    if (!editable) return;
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [editable, load]);

  const customerLines = useMemo(() => lines.filter((ln) => ln.side === "customer_po"), [lines]);
  const selected = customerLines.find((ln) => ln.id === customerLineId) ?? null;
  const lineQty = selected ? Math.max(0, Number(selected.qty) || 0) : 0;
  const splitQty = drafts.reduce((sum, d) => sum + (Number(d.qty) || 0), 0);
  const remaining = lineQty - splitQty;
  const splitTotal = drafts.reduce((sum, d) => sum + (Number(d.qty) || 0) * (Number(d.unit_price) || 0), 0);

  if (!editable) return null;

  function patchDraft(key: string, patch: Partial<SplitDraft>) {
    setDrafts((rows) => rows.map((row) => (row.key === key ? { ...row, ...patch } : row)));
  }

  function patchDraftQty(key: string, raw: string) {
    if (raw.trim() === "") {
      patchDraft(key, { qty: "" });
      return;
    }
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed < 0) {
      patchDraft(key, { qty: "0" });
      return;
    }
    const others = drafts
      .filter((row) => row.key !== key)
      .reduce((sum, row) => sum + (Number(row.qty) || 0), 0);
    const maxAllowed = Math.max(0, lineQty - others);
    const capped = Math.min(parsed, maxAllowed);
    const next = Number.isInteger(lineQty) ? String(Math.floor(capped)) : String(capped);
    patchDraft(key, { qty: next });
  }

  function maxQtyForDraft(key: string): number {
    const others = drafts
      .filter((row) => row.key !== key)
      .reduce((sum, row) => sum + (Number(row.qty) || 0), 0);
    return Math.max(0, lineQty - others);
  }

  function vendorRowsForCustomerLine(customer: OvfLine): OvfLine[] {
    const product = (customer.product_name || "").trim().toLowerCase();
    return lines.filter((ln) => {
      if (ln.side !== "vendor") return false;
      if (ln.source_line_id === customer.id) return true;
      if (ln.line_no === customer.line_no) return true;
      return product.length > 0 && (ln.product_name || "").trim().toLowerCase() === product;
    });
  }

  function onSelectLine(id: string) {
    setCustomerLineId(id);
    const customer = customerLines.find((c) => c.id === id);
    if (!customer) {
      setDrafts([]);
      return;
    }
    const vendors = vendorRowsForCustomerLine(customer).filter((ln) =>
      (ln.distributor_name || "").trim(),
    );
    setDrafts(
      vendors.map((ln) => ({
        key: ln.id,
        distributor_name: (ln.distributor_name || "").trim(),
        qty: String(Number(ln.qty) || ""),
        unit_price: String(Number(ln.unit_price) || ""),
      })),
    );
  }

  async function run(work: () => Promise<unknown>, message: string) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await work();
      await load();
      onChanged();
      setNotice(message);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  const splitsValid =
    selected != null &&
    drafts.length > 0 &&
    drafts.every((d) => d.distributor_name.trim() && Number(d.qty) > 0 && Number(d.unit_price) >= 0) &&
    remaining >= -1e-6;

  return (
    <CrmSection title="Vendor PO Summary - Break by Distributor" icon={Split}>
      {error ? (
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
          <TriangleAlert className="size-3.5" /> {error}
        </p>
      ) : null}
      {notice ? <p className="mb-3 text-xs font-medium text-emerald-700 dark:text-emerald-400">{notice}</p> : null}

      <div className="grid gap-3 sm:grid-cols-2">
        <FinanceField label="Customer PO line to break">
          <select className={SELECT_CLASS} value={customerLineId} onChange={(e) => onSelectLine(e.target.value)}>
            <option value="">Select a line</option>
            {customerLines.map((ln) => (
              <option key={ln.id} value={ln.id}>
                {ln.line_no}. {ln.product_name} - qty {Number(ln.qty)}
              </option>
            ))}
          </select>
        </FinanceField>
        {selected ? (
          <p className="self-end text-xs text-muted-foreground">
            {remaining >= 0
              ? `${remaining} of ${lineQty} still to place with a distributor.`
              : `Over by ${Math.abs(remaining)} - reduce a split.`}
          </p>
        ) : null}
      </div>

      {selected ? (
        <div className="mt-3 space-y-2">
          {drafts.length === 0 ? (
            <p className="rounded-lg border border-dashed border-border/80 bg-muted/30 px-3 py-3 text-xs text-muted-foreground">
              Set <span className="font-medium text-foreground">Distributor Name</span> on the Vendor PO
              Summary rows for this product first. Those distributors appear here so you only adjust qty and
              unit purchase.
            </p>
          ) : (
            drafts.map((d) => (
              <div key={d.key} className="grid items-end gap-2 sm:grid-cols-[1fr_120px_160px_auto]">
                <FinanceField label="Distributor">
                  <Input value={d.distributor_name} readOnly className="h-9 cursor-default bg-muted/40 text-[13px]" />
                </FinanceField>
                <FinanceField label="Qty">
                  <Input
                    type="number"
                    min={0}
                    max={maxQtyForDraft(d.key)}
                    step={Number.isInteger(lineQty) ? 1 : "any"}
                    value={d.qty}
                    onChange={(e) => patchDraftQty(d.key, e.target.value)}
                    className="h-9 text-[13px]"
                    aria-describedby="ovf-split-qty-hint"
                  />
                </FinanceField>
                <FinanceField label="Unit purchase (₹)">
                  <Input
                    type="number"
                    min={0}
                    step="0.01"
                    value={d.unit_price}
                    onChange={(e) => patchDraft(d.key, { unit_price: e.target.value })}
                    className="h-9 text-[13px]"
                  />
                </FinanceField>
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  aria-label={`Remove ${d.distributor_name}`}
                  disabled={drafts.length <= 1}
                  className="size-9 cursor-pointer"
                  onClick={() => setDrafts((rows) => rows.filter((row) => row.key !== d.key))}
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>
            ))
          )}
          <p id="ovf-split-qty-hint" className="text-[11px] text-muted-foreground">
            Split quantities cannot exceed Customer PO Quantity ({lineQty}). Distributor names come from Vendor
            PO Summary.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="button"
              size="sm"
              disabled={busy || !splitsValid}
              className="cursor-pointer"
              onClick={() =>
                void run(
                  () =>
                    splitOvfVendorLine(
                      ovf.id,
                      selected.id,
                      drafts.map<OvfVendorSplit>((d) => ({
                        distributor_name: d.distributor_name.trim(),
                        qty: Number(d.qty),
                        unit_price: Number(d.unit_price),
                      })),
                    ),
                  `${selected.product_name} split across ${drafts.length} distributors.`,
                )
              }
            >
              Save split
            </Button>
            <span className="text-xs text-muted-foreground tabular-nums">
              Purchase total for this line: {formatInrPrecise(splitTotal)}
            </span>
          </div>
        </div>
      ) : null}
    </CrmSection>
  );
}
