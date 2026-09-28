"use client";

import { useCallback, useEffect, useState } from "react";
import { Landmark, Plus, Star, Trash2, TriangleAlert } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { FinanceField } from "@/components/finance/journals/finance-form-field";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import {
  createCompanyGst,
  deleteCompanyGst,
  listCompanyGst,
  updateCompanyGst,
  type CompanyGst,
} from "@/services/crm-deal-controls-service";

const GSTIN_PATTERN = /^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/;

const SOURCE_LABEL: Record<CompanyGst["source"], string> = {
  manual: "Added manually",
  customer_po: "From customer PO",
  kyc: "From KYC",
};

/**
 * One customer, many GSTINs: head office at onboarding, and every branch /
 * circle GSTIN picked up automatically from the POs it sends.
 */
export function CompanyGstRegistrationsPanel({ companyAccountId }: { companyAccountId: string }) {
  const [rows, setRows] = useState<CompanyGst[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [gstin, setGstin] = useState("");
  const [location, setLocation] = useState("");
  const [address, setAddress] = useState("");

  const load = useCallback(async () => {
    try {
      setRows(await listCompanyGst(companyAccountId));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load GST registrations");
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

  const normalized = gstin.trim().toUpperCase().replaceAll(" ", "");
  const gstinValid = GSTIN_PATTERN.test(normalized);

  return (
    <CrmSection title="GST Registrations" icon={Landmark}>
      {error ? (
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-red-600" role="alert">
          <TriangleAlert className="size-3.5" /> {error}
        </p>
      ) : null}
      {rows.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-[13px]">
            <thead className="text-[11px] text-muted-foreground uppercase">
              <tr>
                <th className="py-1.5 pr-3 font-semibold">GSTIN</th>
                <th className="py-1.5 pr-3 font-semibold">State</th>
                <th className="py-1.5 pr-3 font-semibold">Location</th>
                <th className="py-1.5 pr-3 font-semibold">Source</th>
                <th className="py-1.5" aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t border-border/60">
                  <td className="py-1.5 pr-3 font-mono text-xs">
                    {row.gstin}
                    {row.is_head_office ? (
                      <Badge className="ml-2 rounded-full border-transparent bg-blue-100 px-2 py-0 text-[10px] font-semibold text-blue-800 dark:bg-blue-900/50 dark:text-blue-200">
                        Head office
                      </Badge>
                    ) : null}
                  </td>
                  <td className="py-1.5 pr-3">{row.state ?? "-"}</td>
                  <td className="py-1.5 pr-3">{row.location_label ?? "-"}</td>
                  <td className="py-1.5 pr-3 text-xs text-muted-foreground">{SOURCE_LABEL[row.source]}</td>
                  <td className="py-1.5 text-right whitespace-nowrap">
                    {!row.is_head_office ? (
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        disabled={busy}
                        aria-label={`Make ${row.gstin} the head office`}
                        className="h-7 cursor-pointer text-xs"
                        onClick={() => void run(() => updateCompanyGst(row.id, { is_head_office: true }))}
                      >
                        <Star className="size-3.5" /> Head office
                      </Button>
                    ) : null}
                    <Button
                      type="button"
                      size="icon"
                      variant="ghost"
                      disabled={busy}
                      aria-label={`Remove ${row.gstin}`}
                      className="size-7 cursor-pointer text-red-700"
                      onClick={() => void run(() => deleteCompanyGst(row.id))}
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-xs text-muted-foreground">
          No GSTIN on file. Add the head office GSTIN now - branch GSTINs are captured from customer POs.
        </p>
      )}

      <div className="mt-3 grid items-end gap-2 sm:grid-cols-[180px_1fr_1.5fr_auto]">
        <FinanceField label="GSTIN">
          <Input
            value={gstin}
            maxLength={15}
            onChange={(e) => setGstin(e.target.value.toUpperCase())}
            placeholder="27AAACB2894G1ZK"
            aria-invalid={gstin.length > 0 && !gstinValid}
            className="h-9 font-mono text-[13px]"
          />
        </FinanceField>
        <FinanceField label="Branch / location">
          <Input value={location} onChange={(e) => setLocation(e.target.value)} className="h-9 text-[13px]" />
        </FinanceField>
        <FinanceField label="Registered address">
          <Input value={address} onChange={(e) => setAddress(e.target.value)} className="h-9 text-[13px]" />
        </FinanceField>
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={busy || !gstinValid}
          className="h-9 cursor-pointer"
          onClick={() =>
            void run(async () => {
              await createCompanyGst(companyAccountId, {
                gstin: normalized,
                location_label: location.trim() || null,
                billing_address: address.trim() || null,
                is_head_office: rows.length === 0,
              });
              setGstin("");
              setLocation("");
              setAddress("");
            })
          }
        >
          <Plus className="size-3.5" /> Add GSTIN
        </Button>
      </div>
      {gstin.length > 0 && !gstinValid ? (
        <p className="mt-1 text-[11px] text-red-600">A GSTIN is 15 characters: state code, PAN, entity number, Z, check digit.</p>
      ) : null}
    </CrmSection>
  );
}
