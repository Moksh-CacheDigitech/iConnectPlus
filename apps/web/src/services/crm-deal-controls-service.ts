/**
 * Deal controls added after the Sep-2026 review: live OVF margin, customer
 * receipts, execution expenses, vendor-line splits, delivery timeline,
 * customer GST registrations, customer PO auto-fetch, FOC ledger, quote
 * splits, BOQ/SOW SLA responses, and owner-tagged inventory.
 */
import { ApiClientError, apiClient } from "@/services/api-client";
import type { ApprovalTask, Ovf, OvfLine, Quote } from "@/services/sales-crm-service";

function asArray<T>(data: T[] | T | null | undefined): T[] {
  if (Array.isArray(data)) return data;
  if (data == null) return [];
  return [data];
}

function unwrap<T>(res: { data: T | null }): T {
  if (res.data == null) {
    throw new ApiClientError("Empty response from server", 500);
  }
  return res.data;
}

const OVF = "/crm/ovf";

// ---------------------------------------------------------------------------
// Live OVF margin, receipts, full payment
// ---------------------------------------------------------------------------

export type OvfLiveStatus = {
  ovf_id: string;
  ovf_no: string;
  as_of: string;
  margin_at_approval_amount: number | null;
  margin_at_approval_pct: number | null;
  live_margin_amount: number;
  live_margin_pct: number;
  margin_erosion: number | null;
  customer_total: number;
  customer_receivable: number;
  vendor_total: number;
  received_amount: number;
  outstanding_amount: number;
  overdue_days: number;
  overdue_finance_cost: number;
  holding_cost: number;
  execution_expense_total: number;
  early_payment_saving: number;
  planned_finance_cost: number;
  full_payment_received: boolean;
  closed_at: string | null;
  payment_due_date: string | null;
  payment_received_date: string | null;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  delivery_overdue: boolean;
};

export type OvfPayment = {
  id: string;
  ovf_id: string;
  amount: number;
  received_date: string;
  reference: string | null;
  remark: string | null;
  created_at: string | null;
};

export async function getOvfLiveStatus(ovfId: string): Promise<OvfLiveStatus> {
  return unwrap(await apiClient<OvfLiveStatus>(`${OVF}/${ovfId}/live-status`));
}

export async function listOvfPayments(ovfId: string): Promise<OvfPayment[]> {
  return asArray((await apiClient<OvfPayment[]>(`${OVF}/${ovfId}/payments`)).data);
}

export async function addOvfPayment(
  ovfId: string,
  body: { amount: number; received_date: string; reference?: string | null; remark?: string | null },
): Promise<OvfPayment> {
  return unwrap(await apiClient<OvfPayment>(`${OVF}/${ovfId}/payments`, { method: "POST", body }));
}

export async function voidOvfPayment(paymentId: string): Promise<void> {
  await apiClient(`${OVF}/payments/${paymentId}/void`, { method: "PATCH", body: {} });
}

export async function markOvfFullPayment(
  ovfId: string,
  body: { received_date: string; remark?: string | null },
): Promise<Ovf> {
  return unwrap(await apiClient<Ovf>(`${OVF}/${ovfId}/full-payment`, { method: "POST", body }));
}

// ---------------------------------------------------------------------------
// Execution expenses (cables, MATAD, visits...) approved by the sales owner
// ---------------------------------------------------------------------------

export const OVF_EXPENSE_TYPES = [
  { value: "cables", label: "Cables" },
  { value: "matad", label: "MATAD" },
  { value: "site_visit", label: "Site visit" },
  { value: "installation", label: "Installation" },
  { value: "purchase", label: "Additional purchase" },
  { value: "operations", label: "Additional operations" },
  { value: "foc", label: "Free of cost" },
  { value: "other", label: "Other" },
] as const;

export const OVF_EXPENSE_TEAMS = [
  { value: "scm", label: "Supply chain" },
  { value: "operations", label: "Operations" },
  { value: "presales", label: "Pre-sales" },
  { value: "sales", label: "Sales" },
  { value: "finance", label: "Finance" },
  { value: "other", label: "Other" },
] as const;

export type OvfExpense = {
  id: string;
  ovf_id: string;
  expense_type: string;
  raised_by_team: string;
  description: string;
  amount: number;
  incurred_on: string | null;
  status: "pending" | "approved" | "rejected";
  decided_at: string | null;
  decision_remark: string | null;
  created_at: string | null;
};

export async function listOvfExpenses(ovfId: string): Promise<OvfExpense[]> {
  return asArray((await apiClient<OvfExpense[]>(`${OVF}/${ovfId}/expenses`)).data);
}

export async function raiseOvfExpense(
  ovfId: string,
  body: {
    expense_type: string;
    raised_by_team: string;
    description: string;
    amount: number;
    incurred_on?: string | null;
  },
): Promise<OvfExpense> {
  return unwrap(await apiClient<OvfExpense>(`${OVF}/${ovfId}/expenses`, { method: "POST", body }));
}

export async function decideOvfExpense(
  expenseId: string,
  decision: "approved" | "rejected",
  remark?: string,
): Promise<OvfExpense> {
  return unwrap(
    await apiClient<OvfExpense>(`${OVF}/expenses/${expenseId}/decide`, {
      method: "POST",
      body: { decision, remark },
    }),
  );
}

// ---------------------------------------------------------------------------
// Vendor PO summary break + delivery timeline
// ---------------------------------------------------------------------------

export type OvfVendorSplit = {
  distributor_name: string;
  qty: number;
  unit_price: number;
  gst_pct?: number | null;
  contact_person?: string | null;
  contact_number?: string | null;
};

export async function splitOvfVendorLine(
  ovfId: string,
  customerLineId: string,
  splits: OvfVendorSplit[],
): Promise<OvfLine[]> {
  return asArray(
    (
      await apiClient<OvfLine[]>(`${OVF}/${ovfId}/vendor-split`, {
        method: "POST",
        body: { customer_line_id: customerLineId, splits },
      })
    ).data,
  );
}

export async function deleteOvfLine(lineId: string): Promise<void> {
  await apiClient(`${OVF}/lines/${lineId}`, { method: "DELETE" });
}

export async function updateOvfDeliveryDates(
  ovfId: string,
  body: { expected_delivery_date?: string | null; actual_delivery_date?: string | null; reason?: string | null },
): Promise<Ovf> {
  return unwrap(await apiClient<Ovf>(`${OVF}/${ovfId}/delivery-dates`, { method: "PATCH", body }));
}

export const NEGOTIATED_BY_OPTIONS = [
  { value: "sales", label: "Sales" },
  { value: "management", label: "Management" },
  { value: "scm", label: "Supply chain" },
  { value: "presales", label: "Pre-sales" },
  { value: "finance", label: "Finance" },
  { value: "other", label: "Other" },
] as const;

// ---------------------------------------------------------------------------
// Sales performance (incentive / F&F feed)
// ---------------------------------------------------------------------------

export type SalesPerformanceRow = {
  owner_employee_id: string | null;
  owner_name: string | null;
  ovf_count: number;
  open_ovf_count: number;
  margin_at_approval: number;
  live_margin: number;
  margin_erosion: number;
  overdue_finance_cost: number;
  holding_cost: number;
  execution_expenses: number;
  outstanding_receivable: number;
};

export async function getSalesPerformance(): Promise<SalesPerformanceRow[]> {
  return asArray((await apiClient<SalesPerformanceRow[]>(`${OVF}/sales-performance`)).data);
}

// ---------------------------------------------------------------------------
// Customer GST registrations + customer PO auto-fetch
// ---------------------------------------------------------------------------

export type CompanyGst = {
  id: string;
  company_account_id: string;
  gstin: string;
  state_code: string | null;
  state: string | null;
  location_label: string | null;
  billing_address: string | null;
  shipping_address: string | null;
  is_head_office: boolean;
  source: "manual" | "customer_po" | "kyc";
  status: "active" | "inactive";
  created_at: string | null;
  version: number;
};

export async function listCompanyGst(companyAccountId: string): Promise<CompanyGst[]> {
  return asArray(
    (await apiClient<CompanyGst[]>(`/crm/companies/${companyAccountId}/gst-registrations`)).data,
  );
}

export async function createCompanyGst(
  companyAccountId: string,
  body: {
    gstin: string;
    location_label?: string | null;
    billing_address?: string | null;
    shipping_address?: string | null;
    is_head_office?: boolean;
  },
): Promise<CompanyGst> {
  return unwrap(
    await apiClient<CompanyGst>(`/crm/companies/${companyAccountId}/gst-registrations`, {
      method: "POST",
      body,
    }),
  );
}

export async function updateCompanyGst(
  gstId: string,
  body: Partial<Pick<CompanyGst, "location_label" | "billing_address" | "shipping_address" | "is_head_office" | "status">>,
): Promise<CompanyGst> {
  return unwrap(await apiClient<CompanyGst>(`/crm/company-gst/${gstId}`, { method: "PATCH", body }));
}

export async function deleteCompanyGst(gstId: string): Promise<void> {
  await apiClient(`/crm/company-gst/${gstId}`, { method: "DELETE" });
}

export type CustomerPoExtract = {
  po_number: string | null;
  po_date: string | null;
  billing_address: string | null;
  shipping_address: string | null;
  gst_registrations: Array<{ gstin: string; state: string | null; is_new?: boolean | null }>;
  delivery_weeks_min: number | null;
  delivery_weeks_max: number | null;
  fields_found: string[];
  text_extracted: boolean;
};

export async function extractCustomerPo(
  opportunityId: string,
  body: { file_name: string; content_base64: string; capture_gst?: boolean },
): Promise<CustomerPoExtract> {
  return unwrap(
    await apiClient<CustomerPoExtract>(`/crm/opportunities/${opportunityId}/customer-po/extract`, {
      method: "POST",
      body,
    }),
  );
}

// ---------------------------------------------------------------------------
// Customer expense (FOC) ledger
// ---------------------------------------------------------------------------

export const CUSTOMER_EXPENSE_CATEGORIES = [
  { value: "foc_material", label: "FOC material" },
  { value: "replacement", label: "Replacement" },
  { value: "cables", label: "Cables" },
  { value: "site_visit", label: "Site visit" },
  { value: "service", label: "Service" },
  { value: "other", label: "Other" },
] as const;

export type CustomerExpense = {
  id: string;
  company_account_id: string;
  opportunity_id: string | null;
  expense_date: string;
  category: string;
  description: string;
  amount: number;
  approved_by_name: string | null;
  approval_reference: string | null;
  adjust_in_future: boolean;
  status: "open" | "adjusted" | "written_off";
  adjusted_ovf_id: string | null;
  adjusted_at: string | null;
  adjustment_remark: string | null;
  created_at: string | null;
};

export type CustomerExpenseSummary = {
  company_account_id: string | null;
  open_count: number;
  open_amount: number;
  adjusted_amount: number;
  written_off_amount: number;
  open_items: CustomerExpense[];
};

export async function listCustomerExpenses(companyAccountId: string): Promise<CustomerExpense[]> {
  return asArray(
    (await apiClient<CustomerExpense[]>(`/crm/companies/${companyAccountId}/customer-expenses`)).data,
  );
}

export async function createCustomerExpense(
  companyAccountId: string,
  body: {
    expense_date: string;
    category: string;
    description: string;
    amount: number;
    approved_by_name: string;
    approval_reference?: string | null;
    opportunity_id?: string | null;
    adjust_in_future?: boolean;
  },
): Promise<CustomerExpense> {
  return unwrap(
    await apiClient<CustomerExpense>(`/crm/companies/${companyAccountId}/customer-expenses`, {
      method: "POST",
      body,
    }),
  );
}

export async function getOpportunityCustomerExpenseSummary(opportunityId: string): Promise<CustomerExpenseSummary> {
  return unwrap(
    await apiClient<CustomerExpenseSummary>(`/crm/opportunities/${opportunityId}/customer-expenses/summary`),
  );
}

export async function adjustCustomerExpense(expenseId: string, ovfId: string, remark?: string): Promise<CustomerExpense> {
  return unwrap(
    await apiClient<CustomerExpense>(`/crm/customer-expenses/${expenseId}/adjust`, {
      method: "POST",
      body: { ovf_id: ovfId, remark },
    }),
  );
}

export async function writeOffCustomerExpense(expenseId: string, remark: string): Promise<CustomerExpense> {
  return unwrap(
    await apiClient<CustomerExpense>(`/crm/customer-expenses/${expenseId}/write-off`, {
      method: "POST",
      body: { remark },
    }),
  );
}

// ---------------------------------------------------------------------------
// Quote split (break one quote into several, quantity drawn down)
// ---------------------------------------------------------------------------

export type QuoteSplitBalanceRow = {
  line_id: string;
  line_no: number;
  product_name: string;
  qty: number;
  allocated_qty: number;
  balance_qty: number;
};

export type QuoteSplitItem = {
  contact_id?: string | null;
  entity_name?: string | null;
  entity_gst?: string | null;
  entity_address?: string | null;
  shipping_street?: string | null;
  shipping_city?: string | null;
  shipping_state?: string | null;
  shipping_zip?: string | null;
  lines: Array<{ source_line_id: string; qty: number }>;
};

export async function getQuoteSplitBalance(quoteId: string): Promise<QuoteSplitBalanceRow[]> {
  return asArray((await apiClient<QuoteSplitBalanceRow[]>(`/crm/quotes/${quoteId}/split-balance`)).data);
}

export async function splitQuote(quoteId: string, splits: QuoteSplitItem[]): Promise<Quote[]> {
  return asArray((await apiClient<Quote[]>(`/crm/quotes/${quoteId}/split`, { method: "POST", body: { splits } })).data);
}

export type VendorQuoteLine = {
  product_name: string;
  hsn_sac: string | null;
  qty: number;
  unit_cost: number;
  line_total: number;
  gst_pct: number | null;
};

export type VendorQuoteExtract = {
  lines: VendorQuoteLine[];
  text_extracted: boolean;
  ocr_available: boolean;
};

/** Read item rows (qty x rate = amount) from a vendor quote PDF / image / Excel. */
export async function extractVendorQuoteLines(fileName: string, contentBase64: string): Promise<VendorQuoteExtract> {
  return unwrap(
    await apiClient<VendorQuoteExtract>("/crm/quotes/extract-vendor-lines", {
      method: "POST",
      body: { file_name: fileName, content_base64: contentBase64 },
    }),
  );
}

export async function getDefaultQuoteTerms(): Promise<string> {
  return unwrap(await apiClient<{ terms: string }>("/crm/quotes/default-terms")).terms;
}

// ---------------------------------------------------------------------------
// BOQ / SOW SLA response
// ---------------------------------------------------------------------------

export const BOQ_SOW_SLA_ACTIONS = new Set(["provide_boq_attachment", "provide_sow_attachment"]);

export async function respondMyJob(taskId: string, canSubmit: boolean, reason?: string): Promise<ApprovalTask> {
  return unwrap(
    await apiClient<ApprovalTask>(`/crm/my-jobs/${taskId}/respond`, {
      method: "POST",
      body: { can_submit: canSubmit, reason },
    }),
  );
}

// ---------------------------------------------------------------------------
// Inventory ownership, aging, transfer requests, delivery milestones
// ---------------------------------------------------------------------------

const SCM = "/procurement/scm";

export type InventoryUnit = {
  kind: "stock_unit" | "import_line";
  id: string;
  product_name: string | null;
  serial_number: string | null;
  received_on: string | null;
  quantity: number;
  unit_cost: number;
  warranty_valid_till: string | null;
  warranty_expired: boolean;
  warranty_days_left: number | null;
  owner_employee_id: string | null;
  owner_name: string | null;
  source_ovf_id: string | null;
  open_for_sale: boolean;
  status: "owned" | "open_for_sale";
  age_days: number;
  aging_bucket: string;
  holding_cost: number;
  current_value: number;
};

export type InventoryAgingTotals = { units: number; value: number; holding_cost: number };

export type InventoryAgingReport = {
  as_of: string;
  target_max_age_days: number;
  total: InventoryAgingTotals;
  over_target: InventoryAgingTotals;
  warranty_expired_units: number;
  buckets: Array<InventoryAgingTotals & { bucket: string }>;
  by_owner: Array<InventoryAgingTotals & { owner_employee_id: string | null; owner_name: string | null; oldest_age_days: number }>;
  by_product: Array<InventoryAgingTotals & { product_name: string | null }>;
};

export type InventoryTransfer = {
  id: string;
  requester_employee_id: string;
  owner_employee_id: string | null;
  product_name: string;
  quantity: number;
  customer_note: string | null;
  status: "pending" | "accepted" | "rejected" | "cancelled";
  decided_at: string | null;
  decision_remark: string | null;
  created_at: string | null;
};

export type InventorySelection = { stock_unit_ids: string[]; import_line_ids: string[] };

export function inventorySelection(units: InventoryUnit[]): InventorySelection {
  return {
    stock_unit_ids: units.filter((u) => u.kind === "stock_unit").map((u) => u.id),
    import_line_ids: units.filter((u) => u.kind === "import_line").map((u) => u.id),
  };
}

export async function listInventoryUnits(): Promise<InventoryUnit[]> {
  return asArray((await apiClient<InventoryUnit[]>(`${SCM}/inventory/units`)).data);
}

export async function getInventoryAging(): Promise<InventoryAgingReport> {
  return unwrap(await apiClient<InventoryAgingReport>(`${SCM}/inventory/aging`));
}

export async function suggestInventory(q: string): Promise<InventoryUnit[]> {
  return asArray((await apiClient<InventoryUnit[]>(`${SCM}/inventory/suggest`, { query: { q } })).data);
}

export async function setInventoryOpenForSale(selection: InventorySelection, openForSale: boolean): Promise<number> {
  const res = await apiClient<{ updated: number }>(`${SCM}/inventory/open-for-sale`, {
    method: "POST",
    body: { ...selection, open_for_sale: openForSale },
  });
  return unwrap(res).updated;
}

export async function assignInventoryOwner(selection: InventorySelection, ownerEmployeeId: string | null): Promise<number> {
  const res = await apiClient<{ updated: number }>(`${SCM}/inventory/assign-owner`, {
    method: "POST",
    body: { ...selection, owner_employee_id: ownerEmployeeId },
  });
  return unwrap(res).updated;
}

export async function listInventoryTransfers(): Promise<InventoryTransfer[]> {
  return asArray((await apiClient<InventoryTransfer[]>(`${SCM}/inventory/transfer-requests`)).data);
}

export async function requestInventoryTransfer(
  selection: InventorySelection,
  customerNote?: string,
): Promise<InventoryTransfer> {
  return unwrap(
    await apiClient<InventoryTransfer>(`${SCM}/inventory/transfer-requests`, {
      method: "POST",
      body: { ...selection, customer_note: customerNote },
    }),
  );
}

export async function decideInventoryTransfer(requestId: string, accept: boolean, remark?: string): Promise<InventoryTransfer> {
  return unwrap(
    await apiClient<InventoryTransfer>(`${SCM}/inventory/transfer-requests/${requestId}/decide`, {
      method: "POST",
      body: { accept, remark },
    }),
  );
}

export const DELIVERY_MILESTONES = [
  { value: "order_placed", label: "Order placed" },
  { value: "ready_at_factory", label: "Ready at factory" },
  { value: "dispatched_from_factory", label: "Dispatched from factory" },
  { value: "received_in_india", label: "Received in India" },
  { value: "received_at_warehouse", label: "Received at warehouse" },
  { value: "dispatched_to_site", label: "Dispatched to site" },
  { value: "reached_site", label: "Reached site" },
  { value: "installed", label: "Installed" },
] as const;

export async function updateDeliveryMilestone(
  orderId: string,
  body: { milestone: string; awb_number?: string | null; actual_delivery_date?: string | null; note?: string | null },
): Promise<void> {
  await apiClient(`${SCM}/orders/${orderId}/delivery-milestone`, { method: "PATCH", body });
}
