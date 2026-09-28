"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Plus, Split, Trash2, TriangleAlert } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { FinanceField } from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import { splitOvfVendorLine, type OvfVendorSplit } from "@/services/crm-deal-controls-service";
import { addOvfLine, formatInrPrecise, listOvfLines, type Ovf, type OvfLine } from "@/services/sales-crm-service";

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-[13px] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

type SplitDraft = { key: string; distributor_name: string; qty: string; unit_price: string };

function newDraft(price = ""): SplitDraft {
  return { key: crypto.randomUUID(), distributor_name: "", qty: "", unit_price: price };
}

type Props = {
  ovf: Ovf;
  distributorOptions: string[];
  onChanged: () => void;
};

/**
 * Break one Customer PO line across several distributors (e.g. 80 + 20), and
 * add supporting items bought outside the main PO (cables, SFPs). Totals and
 * margin recalculate on save.
 */
export function OvfVendorSplitPanel({ ovf, distributorOptions, onChanged }: Props) {
  const editable = ovf.blueprint_state === "draft" && !ovf.locked && !ovf.shared_to_scm && !ovf.deal_won;
  const [lines, setLines] = useState<OvfLine[]>([]);
  const [customerLineId, setCustomerLineId] = useState("");
  const [drafts, setDrafts] = useState<SplitDraft[]>([newDraft(), newDraft()]);
  const [extra, setExtra] = useState({ product_name: "", distributor_name: "", qty: "", unit_price: "" });
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
  const splitQty = drafts.reduce((sum, d) => sum + (Number(d.qty) || 0), 0);
  const remaining = selected ? Number(selected.qty) - splitQty : 0;
  const splitTotal = drafts.reduce((sum, d) => sum + (Number(d.qty) || 0) * (Number(d.unit_price) || 0), 0);

  if (!editable) return null;

  function patchDraft(key: string, patch: Partial<SplitDraft>) {
    setDrafts((rows) => rows.map((row) => (row.key === key ? { ...row, ...patch } : row)));
  }

  function onSelectLine(id: string) {
    setCustomerLineId(id);
    const vendorPrice = lines.find(
      (ln) => ln.side === "vendor" && ln.line_no === customerLines.find((c) => c.id === id)?.line_no,
    )?.unit_price;
    const price = vendorPrice != null ? String(vendorPrice) : "";
    setDrafts([newDraft(price), newDraft(price)]);
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
    <CrmSection title="Vendor PO Summary - Break & Supporting Items" icon={Split}>
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
              ? `${remaining} of ${Number(selected.qty)} still to place with a distributor.`
              : `Over by ${Math.abs(remaining)} - reduce a split.`}
          </p>
        ) : null}
      </div>

      {selected ? (
        <div className="mt-3 space-y-2">
          {drafts.map((d, idx) => (
            <div key={d.key} className="grid items-end gap-2 sm:grid-cols-[1fr_120px_160px_auto]">
              <FinanceField label={`Distributor ${idx + 1}`}>
                <Input
                  list="ovf-split-distributors"
                  value={d.distributor_name}
                  onChange={(e) => patchDraft(d.key, { distributor_name: e.target.value })}
                  className="h-9 text-[13px]"
                />
              </FinanceField>
              <FinanceField label="Qty">
                <Input
                  type="number"
                  min={0}
                  value={d.qty}
                  onChange={(e) => patchDraft(d.key, { qty: e.target.value })}
                  className="h-9 text-[13px]"
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
                aria-label={`Remove distributor ${idx + 1}`}
                disabled={drafts.length <= 1}
                className="size-9 cursor-pointer"
                onClick={() => setDrafts((rows) => rows.filter((row) => row.key !== d.key))}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>
          ))}
          <datalist id="ovf-split-distributors">
            {distributorOptions.map((name) => (
              <option key={name} value={name} />
            ))}
          </datalist>
          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="cursor-pointer"
              onClick={() => setDrafts((rows) => [...rows, newDraft(rows[0]?.unit_price ?? "")])}
            >
              <Plus className="size-3.5" /> Add distributor
            </Button>
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

      <h3 className="mt-4 border-t border-border/70 pt-3 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
        Add Supporting Item (outside the main PO)
      </h3>
      <div className="mt-3 grid items-end gap-2 sm:grid-cols-[1fr_1fr_100px_140px_auto]">
        <FinanceField label="Item">
          <Input
            value={extra.product_name}
            placeholder="HDMI cable, 10G SFP..."
            onChange={(e) => setExtra((x) => ({ ...x, product_name: e.target.value }))}
            className="h-9 text-[13px]"
          />
        </FinanceField>
        <FinanceField label="Supplier">
          <Input
            list="ovf-split-distributors"
            value={extra.distributor_name}
            onChange={(e) => setExtra((x) => ({ ...x, distributor_name: e.target.value }))}
            className="h-9 text-[13px]"
          />
        </FinanceField>
        <FinanceField label="Qty">
          <Input
            type="number"
            min={0}
            value={extra.qty}
            onChange={(e) => setExtra((x) => ({ ...x, qty: e.target.value }))}
            className="h-9 text-[13px]"
          />
        </FinanceField>
        <FinanceField label="Unit cost (₹)">
          <Input
            type="number"
            min={0}
            step="0.01"
            value={extra.unit_price}
            onChange={(e) => setExtra((x) => ({ ...x, unit_price: e.target.value }))}
            className="h-9 text-[13px]"
          />
        </FinanceField>
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={busy || !extra.product_name.trim() || !(Number(extra.qty) > 0)}
          className="h-9 cursor-pointer"
          onClick={() =>
            void run(async () => {
              await addOvfLine(ovf.id, {
                side: "vendor",
                product_name: extra.product_name.trim(),
                distributor_name: extra.distributor_name.trim() || null,
                qty: Number(extra.qty),
                unit_price: Number(extra.unit_price) || 0,
              });
              setExtra({ product_name: "", distributor_name: "", qty: "", unit_price: "" });
            }, "Supporting item added - it reduces the margin.")
          }
        >
          <Plus className="size-3.5" /> Add item
        </Button>
      </div>
    </CrmSection>
  );
}
