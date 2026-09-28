"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, ClipboardCheck, FileSearch, IndianRupee } from "lucide-react";

import { CrmErrorBanner, CrmPage, CrmSection } from "@/components/crm/crm-ui";
import { CrmSessionEmployeeField } from "@/components/crm/sales/crm-session-employee-field";
import {
  OvfOrderLinesSection,
  computeOvfMargins,
  customerRowsFromOvfLines,
  customerRowsFromQuoteLines,
  mergeCustomerRowsWithPoAttachments,
  mergeVendorRowsWithQuoteAttachments,
  persistOvfOrderLinesAfterCreate,
  persistOvfOrderLinesOnUpdate,
  validateChargeAttachments,
  vendorRowsFromOvfLines,
  vendorRowsFromQuoteLines,
  type CustomerChargeRow,
  type VendorChargeRow,
} from "@/components/crm/sales/ovf-order-lines-section";
import {
  RequiredFieldsDialog,
  missingRequiredMessage,
} from "@/components/crm/sales/required-fields-dialog";
import {
  FinanceField,
  FinanceTextarea,
} from "@/components/finance/journals/finance-form-field";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError } from "@/services/api-client";
import { NEGOTIATED_BY_OPTIONS, extractCustomerPo } from "@/services/crm-deal-controls-service";
import { useAuthUser } from "@/hooks/use-auth-user";
import { buildLeadDistributorDropdownOptions } from "@/lib/crm/lead-distributor-options";
import { computeFinanceCostPct } from "@/lib/crm/ovf-finance-cost";
import { resolveSessionEmployeeLabel } from "@/lib/crm/session-employee";
import {
  addOvfLine,
  createAttachment,
  createOvf,
  fileToBase64,
  fullName,
  getCompany,
  getOpportunity,
  getOpportunityBlueprint,
  getOvf,
  getQuote,
  getSalesLead,
  listAttachments,
  listContacts,
  listCrmMemberOptions,
  listMyJobs,
  listOvfLines,
  listOvfs,
  listQuoteLines,
  requestOvfFreight,
  updateOvf,
  updateOvfLine,
  type Opportunity,
  type Ovf,
  type Quote,
} from "@/services/sales-crm-service";

type OvfDraft = {
  po_number: string;
  po_date: string;
  delivery_period: string;
  customer_name: string;
  quote_name: string;
  billing_address: string;
  billing_state: string;
  billing_country: string;
  owner_name: string;
  billing_contact_person: string;
  shipping_address: string;
  shipping_state: string;
  shipping_country: string;
  shipping_contact_person: string;
  account_name: string;
  installation_details: string;
  technology_segment: string;
  sub_technology_segment: string;
  vendor_payment_days: string;
  customer_payment_days: string;
  freight: string;
  additional_charges: string;
  finance_cost_pct: string;
  approval_status: string;
  delivery_weeks_min: string;
  delivery_weeks_max: string;
  negotiated_by: string;
  negotiation_remark: string;
  early_payment_discount_pct: string;
  freight_medium: string;
  freight_weight_kg: string;
  freight_insurance: boolean;
};

const FREIGHT_MEDIUMS = [
  { value: "road", label: "Road" },
  { value: "air", label: "Air" },
  { value: "sea", label: "Sea" },
  { value: "courier", label: "Courier" },
] as const;

const SELECT_CLASS =
  "h-9 w-full cursor-pointer rounded-lg border border-input bg-background px-2.5 text-sm transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

/** Last day of the final committed week, counted from the PO date (or today). */
function expectedDeliveryFromWeeks(poDate: string, weeksMax: string): string {
  const weeks = Number(weeksMax);
  if (!Number.isFinite(weeks) || weeks <= 0) return "";
  const start = poDate ? new Date(`${poDate}T00:00:00`) : new Date();
  start.setDate(start.getDate() + weeks * 7);
  const y = start.getFullYear();
  const m = String(start.getMonth() + 1).padStart(2, "0");
  const d = String(start.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function weeksFromDeliveryPeriod(value: string | null | undefined): [string, string] {
  const match = /(\d{1,3})\s*(?:(?:-|–|to)\s*(\d{1,3}))?\s*(?:weeks?|wks?|w)\b/i.exec(value ?? "");
  if (!match) return ["", ""];
  return [match[1], match[2] ?? match[1]];
}

const NUMBER_NO_SPIN =
  "[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none";

async function distributorOptionsForOpportunity(opportunityRow: Opportunity): Promise<string[]> {
  if (!opportunityRow.lead_id) return buildLeadDistributorDropdownOptions(null);
  try {
    const lead = await getSalesLead(opportunityRow.lead_id);
    return buildLeadDistributorDropdownOptions(lead.distributor_name);
  } catch {
    return buildLeadDistributorDropdownOptions(null);
  }
}

export function OvfFormPage({ quoteId, ovfId }: { quoteId?: string; ovfId?: string }) {
  const router = useRouter();
  const { user } = useAuthUser();
  const isEdit = Boolean(ovfId);
  const [ovf, setOvf] = useState<Ovf | null>(null);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [vendorNameOptions, setVendorNameOptions] = useState<string[]>([]);
  const [form, setForm] = useState<OvfDraft>({
    po_number: "",
    po_date: "",
    delivery_period: "",
    customer_name: "",
    quote_name: "",
    billing_address: "",
    billing_state: "",
    billing_country: "",
    owner_name: "",
    billing_contact_person: "",
    shipping_address: "",
    shipping_state: "",
    shipping_country: "",
    shipping_contact_person: "",
    account_name: "",
    installation_details: "",
    technology_segment: "",
    sub_technology_segment: "",
    vendor_payment_days: "",
    customer_payment_days: "",
    freight: "",
    additional_charges: "",
    finance_cost_pct: "",
    approval_status: "not_required",
    delivery_weeks_min: "",
    delivery_weeks_max: "",
    negotiated_by: "",
    negotiation_remark: "",
    early_payment_discount_pct: "",
    freight_medium: "road",
    freight_weight_kg: "",
    freight_insurance: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [requestingFreight, setRequestingFreight] = useState(false);
  const [readingPo, setReadingPo] = useState(false);
  const [poReadNote, setPoReadNote] = useState<string | null>(null);
  const [freightPending, setFreightPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mandateOpen, setMandateOpen] = useState(false);
  const [mandateMessage, setMandateMessage] = useState("");
  const [customerRows, setCustomerRows] = useState<CustomerChargeRow[]>([]);
  const [vendorRows, setVendorRows] = useState<VendorChargeRow[]>([]);
  const [marginInputsDirty, setMarginInputsDirty] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setMarginInputsDirty(false);
    try {
      if (isEdit && ovfId) {
        const ovfRow = await getOvf(ovfId);
        if (ovfRow.locked) {
          throw new ApiClientError("This OVF is locked and cannot be edited.", 409);
        }
        if (ovfRow.deal_won || ovfRow.shared_to_scm) {
          throw new ApiClientError(
            "OVF cannot be edited after it is shared to SCM or marked Deal Won.",
            409,
          );
        }
        const [quoteRow, opportunityRow, ovfLines, quoteLines, attachments] = await Promise.all([
          getQuote(ovfRow.quote_id),
          getOpportunity(ovfRow.opportunity_id),
          listOvfLines(ovfId).catch(() => []),
          listQuoteLines(ovfRow.quote_id).catch(() => []),
          listAttachments("ovf", ovfId).catch(() => []),
        ]);
        const poAttachments = attachments.filter((row) => row.category === "customer_po");
        const quoteAttachments = attachments.filter((row) => row.category === "vendor_quote");
        setOvf(ovfRow);
        setQuote(quoteRow);
        setOpportunity(opportunityRow);
        const freightTasks = await listMyJobs({
          entity_type: "ovf",
          entity_id: ovfId,
          status: "pending",
        }).catch(() => []);
        setFreightPending(freightTasks.some((task) => task.action === "provide_freight"));
        setVendorNameOptions(await distributorOptionsForOpportunity(opportunityRow));
        setCustomerRows(
          mergeCustomerRowsWithPoAttachments(
            customerRowsFromOvfLines(ovfLines, quoteLines),
            poAttachments,
          ),
        );
        setVendorRows(
          mergeVendorRowsWithQuoteAttachments(
            vendorRowsFromOvfLines(ovfLines, quoteLines),
            quoteAttachments,
          ),
        );
        setForm({
          po_number: ovfRow.po_number ?? "",
          po_date: ovfRow.po_date ? String(ovfRow.po_date).slice(0, 10) : "",
          delivery_period: ovfRow.delivery_period ?? "",
          customer_name: ovfRow.customer_name ?? "",
          quote_name: ovfRow.quote_name ?? "",
          billing_address: ovfRow.billing_address ?? "",
          billing_state: ovfRow.billing_state ?? "",
          billing_country: ovfRow.billing_country ?? "",
          owner_name: ovfRow.owner_name ?? "",
          billing_contact_person: ovfRow.billing_contact_person ?? "",
          shipping_address: ovfRow.shipping_address ?? "",
          shipping_state: ovfRow.shipping_state ?? "",
          shipping_country: ovfRow.shipping_country ?? "",
          shipping_contact_person: ovfRow.shipping_contact_person ?? "",
          account_name: ovfRow.account_name ?? "",
          installation_details: ovfRow.installation_details ?? "",
          technology_segment: ovfRow.technology_segment ?? "",
          sub_technology_segment: ovfRow.sub_technology_segment ?? "",
          vendor_payment_days: String(ovfRow.vendor_payment_days ?? ""),
          customer_payment_days: String(ovfRow.customer_payment_days ?? ""),
          freight: String(ovfRow.freight ?? ""),
          additional_charges: String(ovfRow.additional_charges ?? ""),
          finance_cost_pct: String(ovfRow.finance_cost_pct ?? ""),
          approval_status: ovfRow.approval_status || "not_required",
          delivery_weeks_min:
            ovfRow.delivery_weeks_min != null
              ? String(ovfRow.delivery_weeks_min)
              : weeksFromDeliveryPeriod(ovfRow.delivery_period)[0],
          delivery_weeks_max:
            ovfRow.delivery_weeks_max != null
              ? String(ovfRow.delivery_weeks_max)
              : weeksFromDeliveryPeriod(ovfRow.delivery_period)[1],
          negotiated_by: ovfRow.negotiated_by ?? "",
          negotiation_remark: ovfRow.negotiation_remark ?? "",
          early_payment_discount_pct:
            ovfRow.early_payment_discount_pct ? String(ovfRow.early_payment_discount_pct) : "",
          freight_medium: ovfRow.freight_medium ?? "road",
          freight_weight_kg: ovfRow.freight_weight_kg != null ? String(ovfRow.freight_weight_kg) : "",
          freight_insurance: Boolean(ovfRow.freight_insurance),
        });
        return;
      }

      if (!quoteId) {
        throw new ApiClientError("Quote is required to create an OVF.", 400);
      }

      const quoteRow = await getQuote(quoteId);
      const opportunityRow = await getOpportunity(quoteRow.opportunity_id);
      const [companyRow, contactRows, memberRows, blueprint, existingOvfs, quoteLines] =
        await Promise.all([
          opportunityRow.company_account_id
            ? getCompany(opportunityRow.company_account_id).catch(() => null)
            : Promise.resolve(null),
          opportunityRow.company_account_id
            ? listContacts(opportunityRow.company_account_id).catch(() => [])
            : Promise.resolve([]),
          listCrmMemberOptions().catch(() => []),
          getOpportunityBlueprint(quoteRow.opportunity_id).catch(() => null),
          listOvfs({ opportunity_id: quoteRow.opportunity_id }).catch(() => []),
          listQuoteLines(quoteId).catch(() => []),
        ]);
      if (quoteRow.quote_stage !== "accepted") {
        throw new ApiClientError("OVF can only be created from an accepted quote.", 409);
      }
      if (!blueprint || blueprint.state !== "ovf_ready" || blueprint.locked) {
        throw new ApiClientError(
          `OVF can only be created when the opportunity is at OVF Ready (current: ${blueprint?.state ?? "unknown"}).`,
          409,
        );
      }
      const splitQuoteWithoutOvf =
        Boolean(quoteRow.parent_quote_id) && existingOvfs.every((row) => row.quote_id !== quoteRow.id);
      if (existingOvfs.length > 0 && !splitQuoteWithoutOvf) {
        throw new ApiClientError(
          "An OVF already exists for this opportunity. Open the existing OVF to continue.",
          409,
        );
      }
      const selectedContact =
        contactRows.find((row) => row.id === quoteRow.contact_id) ??
        contactRows.find((row) => row.is_primary) ??
        contactRows[0] ??
        null;
      const ownerName =
        resolveSessionEmployeeLabel(memberRows, user) ||
        quoteRow.owner_name?.trim() ||
        memberRows.find((member) => member.id === opportunityRow.owner_employee_id)?.label ||
        "";
      const contactName = selectedContact ? fullName(selectedContact) : "";
      const billingAddress = companyRow
        ? [
          companyRow.billing_street,
          companyRow.billing_city,
          companyRow.billing_code,
        ]
          .filter(Boolean)
          .join(", ")
        : "";
      const shippingAddress = companyRow
        ? [
          companyRow.shipping_street,
          companyRow.shipping_city,
          companyRow.shipping_code,
        ]
          .filter(Boolean)
          .join(", ")
        : "";
      setQuote(quoteRow);
      setOpportunity(opportunityRow);
      setVendorNameOptions(await distributorOptionsForOpportunity(opportunityRow));
      setCustomerRows(customerRowsFromQuoteLines(quoteLines));
      setVendorRows(vendorRowsFromQuoteLines(quoteLines));
      setForm((current) => ({
        ...current,
        customer_name: companyRow?.customer_name ?? quoteRow.entity_name ?? "",
        quote_name: quoteRow.subject ?? "",
        billing_address: quoteRow.entity_address ?? billingAddress,
        billing_state: companyRow?.billing_state ?? "",
        billing_country:
          quoteRow.billing_country ?? companyRow?.billing_country ?? "",
        owner_name: ownerName,
        billing_contact_person: contactName || quoteRow.entity_contact || "",
        shipping_address: shippingAddress,
        shipping_state: companyRow?.shipping_state ?? "",
        shipping_country:
          quoteRow.shipping_country ?? companyRow?.shipping_country ?? "",
        shipping_contact_person: contactName || quoteRow.entity_contact || "",
        account_name: companyRow?.customer_name ?? quoteRow.entity_name ?? "",
      }));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to load OVF details");
    } finally {
      setLoading(false);
    }
  }, [isEdit, ovfId, quoteId, user]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  function setField<K extends keyof OvfDraft>(key: K, value: OvfDraft[K]) {
    if (
      key === "vendor_payment_days" ||
      key === "customer_payment_days" ||
      key === "early_payment_discount_pct" ||
      key === "additional_charges"
    ) {
      setMarginInputsDirty(true);
    }
    setForm((current) => ({ ...current, [key]: value }));
  }

  function onCustomerRowsChange(rows: CustomerChargeRow[]) {
    setMarginInputsDirty(true);
    setCustomerRows(rows);
  }

  function onVendorRowsChange(rows: VendorChargeRow[]) {
    setMarginInputsDirty(true);
    setVendorRows(rows);
  }

  const financeCostPct = useMemo(
    () =>
      computeFinanceCostPct(
        Number(form.vendor_payment_days) || 0,
        Number(form.customer_payment_days) || 0,
      ),
    [form.vendor_payment_days, form.customer_payment_days],
  );

  const margins = computeOvfMargins({
    customerRows,
    vendorRows,
    freight: form.freight,
    financeCostPct,
  });
  // Early-payment discount from the distributor is credited back to the margin.
  const earlyPaymentSaving =
    (margins.totalPurchaseValue * (Number(form.early_payment_discount_pct) || 0)) / 100;
  const totalMarginAmount =
    margins.totalMarginAmount - (Number(form.additional_charges) || 0) + earlyPaymentSaving;
  const totalMarginPct = margins.totalSaleValue
    ? (totalMarginAmount / margins.totalSaleValue) * 100
    : 0;
  const expectedDelivery = expectedDeliveryFromWeeks(form.po_date, form.delivery_weeks_max);
  const freightAmount = Number(form.freight) || 0;
  const marginAmountDisplay =
    marginInputsDirty && Number.isFinite(totalMarginAmount) ? totalMarginAmount.toFixed(2) : "";
  const marginPctDisplay =
    marginInputsDirty && Number.isFinite(totalMarginPct) ? totalMarginPct.toFixed(2) : "";

  function ovfPayload() {
    const weeksMin = Number(form.delivery_weeks_min) || Number(form.delivery_weeks_max) || null;
    const weeksMax = Number(form.delivery_weeks_max) || Number(form.delivery_weeks_min) || null;
    return {
      po_number: form.po_number.trim(),
      po_date: form.po_date || null,
      delivery_period:
        weeksMax != null
          ? weeksMin === weeksMax
            ? `${weeksMax} weeks`
            : `${weeksMin}-${weeksMax} weeks`
          : null,
      delivery_weeks_min: weeksMin,
      delivery_weeks_max: weeksMax,
      negotiated_by: form.negotiated_by || null,
      negotiation_remark: form.negotiation_remark.trim() || null,
      early_payment_discount_pct: Number(form.early_payment_discount_pct) || 0,
      customer_name: form.customer_name.trim() || null,
      quote_name: form.quote_name.trim() || null,
      billing_address: form.billing_address.trim() || null,
      billing_state: form.billing_state.trim() || null,
      billing_country: form.billing_country.trim() || null,
      owner_name: form.owner_name.trim() || null,
      billing_contact_person: form.billing_contact_person.trim() || null,
      shipping_address: form.shipping_address.trim() || null,
      shipping_state: form.shipping_state.trim() || null,
      shipping_country: form.shipping_country.trim() || null,
      shipping_contact_person: form.shipping_contact_person.trim() || null,
      account_name: form.account_name.trim() || null,
      technology_segment: form.technology_segment.trim() || null,
      sub_technology_segment: form.sub_technology_segment.trim() || null,
      installation_details: form.installation_details.trim() || null,
      vendor_payment_days: Number(form.vendor_payment_days) || 0,
      customer_payment_days: Number(form.customer_payment_days) || 0,
      additional_charges: Number(Number(form.additional_charges || 0).toFixed(2)),
      total_margin_amount: Number(totalMarginAmount.toFixed(2)),
      total_margin_pct: Number(totalMarginPct.toFixed(2)),
      finance_cost_pct: Number(financeCostPct.toFixed(2)),
    };
  }

  async function onReadPo(upload: File | undefined) {
    if (!upload || !opportunity) return;
    setReadingPo(true);
    setPoReadNote(null);
    try {
      const found = await extractCustomerPo(opportunity.id, {
        file_name: upload.name,
        content_base64: await fileToBase64(upload),
      });
      if (!found.fields_found.length) {
        setPoReadNote(
          found.text_extracted
            ? "No PO number or date found in this file - enter them manually."
            : "This file has no readable text (scanned image?) - enter the PO details manually.",
        );
        return;
      }
      setForm((f) => ({
        ...f,
        po_number: found.po_number ?? f.po_number,
        po_date: found.po_date ?? f.po_date,
        delivery_weeks_min: found.delivery_weeks_min != null ? String(found.delivery_weeks_min) : f.delivery_weeks_min,
        delivery_weeks_max: found.delivery_weeks_max != null ? String(found.delivery_weeks_max) : f.delivery_weeks_max,
        billing_address: f.billing_address.trim() ? f.billing_address : found.billing_address ?? f.billing_address,
        shipping_address: f.shipping_address.trim() ? f.shipping_address : found.shipping_address ?? f.shipping_address,
      }));
      const newGst = found.gst_registrations.filter((g) => g.is_new).map((g) => g.gstin);
      setPoReadNote(
        `Filled from ${upload.name}: ${found.fields_found.join(", ").replaceAll("_", " ")}. Check before saving.` +
          (newGst.length ? ` New GSTIN saved to the account: ${newGst.join(", ")}.` : ""),
      );
    } catch (err) {
      setPoReadNote(err instanceof ApiClientError ? err.message : "Could not read the PO file.");
    } finally {
      setReadingPo(false);
    }
  }

  async function onAskScmFreight() {
    if (!quote || !opportunity || freightPending || requestingFreight || saving) return;
    setRequestingFreight(true);
    setError(null);
    try {
      let targetId = ovfId ?? ovf?.id ?? null;
      if (!targetId) {
        try {
          const created = await createOvf({
            quote_id: quote.id,
            branch_id: opportunity.branch_id,
            ...ovfPayload(),
          });
          await persistOvfOrderLinesAfterCreate(
            created.id,
            created.branch_id,
            created.company_id ?? opportunity.company_account_id,
            customerRows,
            vendorRows,
            { listOvfLines, addOvfLine, updateOvfLine, createAttachment, fileToBase64 },
          ).catch(() => undefined);
          targetId = created.id;
          setOvf(created);
        } catch (createErr) {
          const existing = await listOvfs({ opportunity_id: opportunity.id }).catch(() => []);
          const found = existing[0];
          if (!found) throw createErr;
          targetId = found.id;
          setOvf(found);
        }
      }

      const updated = await requestOvfFreight(targetId, {
        medium: (form.freight_medium || null) as "air" | "road" | "sea" | "courier" | null,
        weight_kg: form.freight_weight_kg.trim() ? Number(form.freight_weight_kg) : null,
        insurance: form.freight_insurance,
      });
      setOvf(updated);
      setFreightPending(true);
      setForm((f) => ({
        ...f,
        freight: updated.freight != null ? String(updated.freight) : f.freight,
        approval_status: updated.approval_status ?? f.approval_status,
      }));

      if (!ovfId) {
        router.replace(`/crm/ovf/${targetId}/edit`);
      }
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "Failed to request freight from SCM");
    } finally {
      setRequestingFreight(false);
    }
  }

  async function onSave() {
    if (!quote || !opportunity) return;
    const missing: string[] = [];
    if (!form.po_number.trim()) missing.push("PO Number");
    if (!(Number(form.delivery_weeks_max) > 0 || Number(form.delivery_weeks_min) > 0)) {
      missing.push("Delivery Timeline (weeks)");
    }
    if (
      Number(form.delivery_weeks_min) > 0 &&
      Number(form.delivery_weeks_max) > 0 &&
      Number(form.delivery_weeks_min) > Number(form.delivery_weeks_max)
    ) {
      setError("Delivery 'from' weeks cannot be more than 'to' weeks.");
      return;
    }
    if (form.negotiated_by === "other" && !form.negotiation_remark.trim()) {
      missing.push("Negotiation remark (who negotiated)");
    }
    if (!form.shipping_address.trim()) missing.push("Shipping Address");
    if (missing.length > 0) {
      setMandateMessage(missingRequiredMessage(missing));
      setMandateOpen(true);
      return;
    }
    const chargeError = validateChargeAttachments(customerRows, vendorRows);
    if (chargeError) {
      setError(chargeError);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (isEdit && ovfId) {
        const payload = ovfPayload();
        const saved = await updateOvf(ovfId, payload);
        await persistOvfOrderLinesOnUpdate(
          saved.id,
          saved.branch_id,
          saved.company_id ?? opportunity.company_account_id,
          customerRows,
          vendorRows,
          { addOvfLine, updateOvfLine, createAttachment, fileToBase64 },
        );
        await updateOvf(saved.id, {
          additional_charges: payload.additional_charges,
          total_margin_amount: payload.total_margin_amount,
          total_margin_pct: payload.total_margin_pct,
          finance_cost_pct: payload.finance_cost_pct,
        });
        router.push(`/crm/ovf/${saved.id}`);
        return;
      }

      const created = await createOvf({
        quote_id: quote.id,
        branch_id: opportunity.branch_id,
        ...ovfPayload(),
      });
      await persistOvfOrderLinesAfterCreate(
        created.id,
        created.branch_id,
        created.company_id ?? opportunity.company_account_id,
        customerRows,
        vendorRows,
        { listOvfLines, addOvfLine, updateOvfLine, createAttachment, fileToBase64 },
      );
      router.push(`/crm/ovf/${created.id}`);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : isEdit ? "Failed to update OVF" : "Failed to create OVF");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className="h-96 animate-pulse rounded-xl bg-muted/60" />;
  }

  const backHref = isEdit && ovfId
    ? `/crm/ovf/${ovfId}`
    : `/crm/opportunities/${opportunity?.id ?? ""}`;
  const backLabel = isEdit ? ovf?.ovf_no ?? "OVF" : "Opportunity";

  return (
    <CrmPage>
      <Link
        href={backHref}
        className="inline-flex cursor-pointer items-center gap-1 text-xs font-medium text-primary transition-opacity duration-200 hover:opacity-80"
      >
        <ArrowLeft className="size-3.5" /> {backLabel}
      </Link>
      <PageHeader
        title={isEdit ? `Edit ${ovf?.ovf_no ?? "OVF"}` : "Create OVF Module"}
        actions={
          <div className="flex items-center gap-2">
            <Link
              href={backHref}
              className="inline-flex h-8 cursor-pointer items-center rounded-lg border border-border px-3 text-sm font-medium transition-colors duration-200 hover:bg-muted"
            >
              Cancel
            </Link>
            <Button type="button" className="cursor-pointer" disabled={saving} onClick={() => void onSave()}>
              {saving ? "Saving…" : isEdit ? "Save changes" : "Save"}
            </Button>
          </div>
        }
      />
      {error ? <CrmErrorBanner>{error}</CrmErrorBanner> : null}

      <CrmSection title="OVF Module Information" icon={ClipboardCheck}>
        <div className="grid gap-x-10 gap-y-3 md:grid-cols-2">
          <FinanceField label="Customer Name"><Input value={form.customer_name} onChange={(event) => setField("customer_name", event.target.value)} /></FinanceField>
          <FinanceField label="Quote Name"><Input value={form.quote_name} onChange={(event) => setField("quote_name", event.target.value)} /></FinanceField>
          <FinanceField label="Billing Address"><Input value={form.billing_address} onChange={(event) => setField("billing_address", event.target.value)} /></FinanceField>
          <FinanceField label="Quote No"><Input value={quote?.quote_no ?? "-"} disabled /></FinanceField>
          <FinanceField label="Billing State"><Input value={form.billing_state} onChange={(event) => setField("billing_state", event.target.value)} /></FinanceField>
          <CrmSessionEmployeeField label="OVF Module Owner" value={form.owner_name} />
          <FinanceField label="Billing Contact Person"><Input value={form.billing_contact_person} onChange={(event) => setField("billing_contact_person", event.target.value)} /></FinanceField>
          <FinanceField label="Shipping Address *"><Input value={form.shipping_address} onChange={(event) => setField("shipping_address", event.target.value)} /></FinanceField>
          <FinanceField label="Billing Country"><Input value={form.billing_country} onChange={(event) => setField("billing_country", event.target.value)} /></FinanceField>
          <FinanceField label="Shipping State"><Input value={form.shipping_state} onChange={(event) => setField("shipping_state", event.target.value)} /></FinanceField>
          <FinanceField label="PO Number *">
            <div className="flex min-w-0 flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <Input value={form.po_number} onChange={(event) => setField("po_number", event.target.value)} />
                <label
                  className={`inline-flex h-9 shrink-0 cursor-pointer items-center gap-1.5 rounded-lg border border-border px-2.5 text-xs font-medium transition-colors duration-200 hover:bg-muted ${readingPo || !opportunity ? "pointer-events-none opacity-60" : ""}`}
                >
                  <FileSearch className="size-3.5" />
                  {readingPo ? "Reading…" : "Read from PO"}
                  <input
                    type="file"
                    accept=".pdf,.xlsx,.xls,.png,.jpg,.jpeg,.txt"
                    className="sr-only"
                    onChange={(event) => {
                      void onReadPo(event.target.files?.[0]);
                      event.target.value = "";
                    }}
                  />
                </label>
              </div>
              {poReadNote ? <p className="text-[11px] text-muted-foreground">{poReadNote}</p> : null}
            </div>
          </FinanceField>
          <FinanceField label="Customer PO Date"><Input type="date" value={form.po_date} onChange={(event) => setField("po_date", event.target.value)} /></FinanceField>
          <FinanceField label="Shipping Contact Person"><Input value={form.shipping_contact_person} onChange={(event) => setField("shipping_contact_person", event.target.value)} /></FinanceField>
          <FinanceField label="Delivery Timeline (weeks) *">
            <div className="flex min-w-0 flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  min={1}
                  inputMode="numeric"
                  aria-label="Delivery from weeks"
                  placeholder="16"
                  className={`${NUMBER_NO_SPIN} w-24`}
                  value={form.delivery_weeks_min}
                  onChange={(event) => setField("delivery_weeks_min", event.target.value)}
                />
                <span className="text-xs text-muted-foreground">to</span>
                <Input
                  type="number"
                  min={1}
                  inputMode="numeric"
                  aria-label="Delivery to weeks"
                  placeholder="18"
                  className={`${NUMBER_NO_SPIN} w-24`}
                  value={form.delivery_weeks_max}
                  onChange={(event) => setField("delivery_weeks_max", event.target.value)}
                />
                <span className="text-xs text-muted-foreground">weeks</span>
              </div>
              <p className="text-[11px] text-muted-foreground">
                {expectedDelivery
                  ? `Deliver by ${expectedDelivery} (last day of week ${form.delivery_weeks_max || form.delivery_weeks_min} from ${form.po_date ? "the PO date" : "today"}).`
                  : "Enter the committed lead time; the delivery date is calculated from the PO date."}
              </p>
            </div>
          </FinanceField>
          <FinanceField label="Shipping Country"><Input value={form.shipping_country} onChange={(event) => setField("shipping_country", event.target.value)} /></FinanceField>
          <FinanceField label="OVF sent to SCM team">
            <Input value={ovf?.shared_to_scm ? "Yes" : "No"} disabled />
          </FinanceField>
          <FinanceField label="Installation/Service Details"><FinanceTextarea value={form.installation_details} onChange={(event) => setField("installation_details", event.target.value)} /></FinanceField>
        </div>
      </CrmSection>

      <CrmSection title="Charges and Details" icon={IndianRupee}>
        <div className="grid gap-x-10 gap-y-3 md:grid-cols-2">
          <FinanceField label="Total Margin in Amount">
            <Input
              type="text"
              readOnly
              className={`${NUMBER_NO_SPIN} cursor-default bg-muted/50`}
              value={marginAmountDisplay}
              placeholder="-"
              title="Customer - Vendor - Freight - Additional charges - Finance cost + Early-payment saving"
            />
          </FinanceField>
          <FinanceField label="Vendor Payments Terms">
            <Input
              type="number"
              min={0}
              className={NUMBER_NO_SPIN}
              value={form.vendor_payment_days}
              onChange={(event) => setField("vendor_payment_days", event.target.value)}
            />
          </FinanceField>
          <FinanceField label="Total Margin in Percentage">
            <Input
              type="text"
              readOnly
              className={`${NUMBER_NO_SPIN} cursor-default bg-muted/50`}
              value={marginPctDisplay}
              placeholder="-"
              title="Total Margin Amount ÷ Customer Total × 100"
            />
          </FinanceField>
          <FinanceField label="Customer Payment Term">
            <Input
              type="number"
              min={0}
              className={NUMBER_NO_SPIN}
              value={form.customer_payment_days}
              onChange={(event) => setField("customer_payment_days", event.target.value)}
            />
          </FinanceField>
          <FinanceField label="Opportunity">
            <Input value={opportunity?.opportunity_name ?? "-"} disabled />
          </FinanceField>
          <FinanceField label="Freight Charges (₹)">
            <div className="flex min-w-0 flex-col gap-2">
              <Input
                type="text"
                readOnly
                aria-readonly="true"
                className="cursor-default bg-muted/50"
                value={
                  form.freight.trim()
                    ? Number(form.freight).toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })
                    : "—"
                }
              />
              {freightPending ? (
                <p className="text-xs text-muted-foreground">
                  Draft — waiting on SCM to enter freight in My Jobs. You will get a notification when
                  it is ready.
                </p>
              ) : (
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                  <select
                    aria-label="Freight medium"
                    className={SELECT_CLASS}
                    value={form.freight_medium}
                    onChange={(event) => setField("freight_medium", event.target.value)}
                  >
                    {FREIGHT_MEDIUMS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                  <Input
                    type="number"
                    min={0}
                    step="0.1"
                    aria-label="Expected weight (kg)"
                    placeholder="Weight (kg)"
                    className={NUMBER_NO_SPIN}
                    value={form.freight_weight_kg}
                    onChange={(event) => setField("freight_weight_kg", event.target.value)}
                  />
                  <label className="col-span-2 flex cursor-pointer items-center gap-2 text-xs sm:col-span-1">
                    <input
                      type="checkbox"
                      className="size-4 cursor-pointer accent-primary"
                      checked={form.freight_insurance}
                      onChange={(event) => setField("freight_insurance", event.target.checked)}
                    />
                    Insure shipment
                  </label>
                </div>
              )}
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="w-fit cursor-pointer"
                disabled={freightPending || requestingFreight || saving || !quote || !opportunity}
                onClick={() => void onAskScmFreight()}
              >
                {requestingFreight
                  ? "Requesting…"
                  : freightPending
                    ? "Freight requested"
                    : "Ask SCM for freight"}
              </Button>
              {!freightPending ? (
                <p className="text-[11px] text-muted-foreground">
                  SCM receives the ship-to address, items, quantities, medium, weight and insurance
                  choice in My Jobs.
                </p>
              ) : null}
            </div>
          </FinanceField>
          <FinanceField label="Approval Status">
            <Input
              value={
                (
                  {
                    not_required: "None",
                    pending: "Pending",
                    approved: "Approved",
                    rejected: "Rejected",
                  } as Record<string, string>
                )[form.approval_status] ?? form.approval_status.replaceAll("_", " ")
              }
              disabled
              aria-readonly="true"
              className="cursor-default bg-muted/50 capitalize"
            />
          </FinanceField>
          <FinanceField label="Finance Cost (%)">
            <Input
              type="text"
              readOnly
              className={`${NUMBER_NO_SPIN} cursor-default bg-muted/50`}
              value={financeCostPct.toFixed(2)}
              title="max(0, customer days − vendor days − 5) / 15 × 0.5 (2 d.p.)"
            />
          </FinanceField>
          <FinanceField label="Additional Charges (₹)">
            <Input
              type="number"
              min={0}
              step="0.01"
              className={NUMBER_NO_SPIN}
              value={form.additional_charges}
              onChange={(event) => setField("additional_charges", event.target.value)}
            />
          </FinanceField>
          <FinanceField label="Early-payment Discount from Vendor (%)">
            <div className="flex min-w-0 flex-col gap-1">
              <Input
                type="number"
                min={0}
                max={100}
                step="0.01"
                className={NUMBER_NO_SPIN}
                placeholder="0.5"
                value={form.early_payment_discount_pct}
                onChange={(event) => setField("early_payment_discount_pct", event.target.value)}
              />
              <p className="text-[11px] text-muted-foreground">
                {earlyPaymentSaving > 0
                  ? `Adds ₹${earlyPaymentSaving.toLocaleString("en-IN", { maximumFractionDigits: 2 })} back to the margin. Compare it with the finance cost of paying earlier (1% a month).`
                  : "Discount the distributor gives for paying within its payment terms."}
              </p>
            </div>
          </FinanceField>
          <FinanceField label="Negotiated By">
            <select
              className={SELECT_CLASS}
              value={form.negotiated_by}
              onChange={(event) => setField("negotiated_by", event.target.value)}
            >
              <option value="">Not negotiated</option>
              {NEGOTIATED_BY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </FinanceField>
          <FinanceField label={form.negotiated_by === "other" ? "Negotiation Remark *" : "Negotiation Remark"}>
            <FinanceTextarea
              value={form.negotiation_remark}
              placeholder={
                ovf?.original_vendor_total != null
                  ? `Original vendor price ₹${Number(ovf.original_vendor_total).toLocaleString("en-IN")} - what changed and why?`
                  : "Original vs negotiated price, and why"
              }
              onChange={(event) => setField("negotiation_remark", event.target.value)}
            />
          </FinanceField>
        </div>
      </CrmSection>

      <OvfOrderLinesSection
        customerRows={customerRows}
        vendorRows={vendorRows}
        onCustomerRowsChange={onCustomerRowsChange}
        onVendorRowsChange={onVendorRowsChange}
        vendorNameOptions={vendorNameOptions}
        readOnlyLines
        disabled={saving}
      />

      <RequiredFieldsDialog
        open={mandateOpen}
        message={mandateMessage}
        onClose={() => setMandateOpen(false)}
      />
    </CrmPage>
  );
}
