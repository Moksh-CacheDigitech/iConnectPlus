/**
 * Service POs on per-visit rate contracts, and multi-site delivery project
 * trackers (circles / sites, Excel round-trip, customer tracking link).
 */
import { ApiClientError, apiClient, downloadApiFile } from "@/services/api-client";
import { env } from "@/utils/env";

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

const SCM = "/procurement/scm";

// ---------------------------------------------------------------------------
// Rate contracts
// ---------------------------------------------------------------------------

export const SERVICE_TYPE_OPTIONS = [
  { value: "site_visit", label: "Site visit" },
  { value: "installation", label: "Installation" },
  { value: "survey", label: "Site survey" },
  { value: "maintenance", label: "Maintenance" },
  { value: "manpower", label: "Manpower" },
  { value: "other", label: "Other" },
] as const;

export function serviceTypeLabel(value: string | null | undefined): string {
  return SERVICE_TYPE_OPTIONS.find((o) => o.value === value)?.label ?? value ?? "-";
}

export type ServiceRateContract = {
  id: string;
  contract_code: string;
  vendor_id: string | null;
  vendor_name: string;
  service_type: string;
  region: string | null;
  rate_per_visit: number;
  valid_from: string;
  valid_to: string | null;
  status: "active" | "inactive";
  remarks: string | null;
  created_at: string | null;
};

export type ServiceRateContractInput = {
  vendor_name: string;
  service_type: string;
  region?: string | null;
  rate_per_visit: number;
  valid_from: string;
  valid_to?: string | null;
  remarks?: string | null;
};

export async function listServiceContracts(activeOnly = false): Promise<ServiceRateContract[]> {
  return asArray(
    (await apiClient<ServiceRateContract[]>(`${SCM}/service-contracts`, { query: { active_only: activeOnly } })).data,
  );
}

export async function createServiceContract(body: ServiceRateContractInput): Promise<ServiceRateContract> {
  return unwrap(await apiClient<ServiceRateContract>(`${SCM}/service-contracts`, { method: "POST", body }));
}

export async function updateServiceContract(
  id: string,
  body: Partial<ServiceRateContractInput> & { status?: "active" | "inactive" },
): Promise<ServiceRateContract> {
  return unwrap(await apiClient<ServiceRateContract>(`${SCM}/service-contracts/${id}`, { method: "PATCH", body }));
}

// ---------------------------------------------------------------------------
// Service plans (projected visits on an OVF) and visit log
// ---------------------------------------------------------------------------

export type ServicePlan = {
  id: string;
  ovf_id: string;
  rate_contract_id: string;
  contract_code: string | null;
  vendor_name: string | null;
  service_type: string | null;
  description: string | null;
  projected_visits: number;
  visits_done: number;
  visits_remaining: number;
  extra_visits: number;
  rate_per_visit: number;
  consumables_amount: number;
  planned_total: number;
  actual_cost: number;
  added_to_ovf: boolean;
  status: "open" | "closed";
};

export type ServiceVisit = {
  id: string;
  plan_id: string;
  visit_date: string;
  site: string | null;
  engineer_name: string | null;
  remarks: string | null;
  status: "done" | "cancelled";
  beyond_projection: boolean;
  expense_id: string | null;
  created_at: string | null;
};

export async function listServicePlans(ovfId: string): Promise<ServicePlan[]> {
  return asArray((await apiClient<ServicePlan[]>(`${SCM}/service-plans`, { query: { ovf_id: ovfId } })).data);
}

export async function createServicePlan(body: {
  ovf_id: string;
  rate_contract_id: string;
  projected_visits: number;
  consumables_amount?: number;
  description?: string | null;
  add_to_ovf?: boolean;
}): Promise<ServicePlan> {
  return unwrap(await apiClient<ServicePlan>(`${SCM}/service-plans`, { method: "POST", body }));
}

export async function closeServicePlan(planId: string): Promise<ServicePlan> {
  return unwrap(await apiClient<ServicePlan>(`${SCM}/service-plans/${planId}/close`, { method: "POST", body: {} }));
}

export async function listServiceVisits(planId: string): Promise<ServiceVisit[]> {
  return asArray((await apiClient<ServiceVisit[]>(`${SCM}/service-plans/${planId}/visits`)).data);
}

export async function logServiceVisit(
  planId: string,
  body: { visit_date: string; site?: string | null; engineer_name?: string | null; remarks?: string | null },
): Promise<ServiceVisit> {
  return unwrap(await apiClient<ServiceVisit>(`${SCM}/service-plans/${planId}/visits`, { method: "POST", body }));
}

export async function cancelServiceVisit(visitId: string): Promise<ServiceVisit> {
  return unwrap(await apiClient<ServiceVisit>(`${SCM}/service-visits/${visitId}/cancel`, { method: "POST", body: {} }));
}

// ---------------------------------------------------------------------------
// Delivery projects (multi-site tracker)
// ---------------------------------------------------------------------------

export const SITE_STATUS_OPTIONS = [
  { value: "pending", label: "Pending" },
  { value: "in_progress", label: "In progress" },
  { value: "delivered", label: "Delivered" },
  { value: "installed", label: "Installed" },
  { value: "on_hold", label: "On hold" },
  { value: "cancelled", label: "Cancelled" },
] as const;

export function siteStatusLabel(value: string): string {
  return SITE_STATUS_OPTIONS.find((o) => o.value === value)?.label ?? value;
}

export type DeliverySite = {
  id: string;
  project_id: string;
  circle: string | null;
  site_code: string | null;
  site_name: string;
  address: string | null;
  state: string | null;
  gstin: string | null;
  customer_po_number: string | null;
  ovf_id: string | null;
  order_header_id: string | null;
  item_summary: string | null;
  quantity: number | null;
  milestone: string;
  milestone_label: string;
  status: string;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  awb_number: string | null;
  delay_reason: string | null;
  last_note: string | null;
  delayed: boolean;
  history: { at: string; by: string | null; source: string; changes: Record<string, unknown> }[];
  updated_at: string | null;
};

export type DeliverySiteInput = Partial<
  Pick<
    DeliverySite,
    | "circle"
    | "site_code"
    | "site_name"
    | "address"
    | "state"
    | "gstin"
    | "customer_po_number"
    | "item_summary"
    | "quantity"
    | "milestone"
    | "status"
    | "expected_delivery_date"
    | "actual_delivery_date"
    | "awb_number"
    | "delay_reason"
    | "last_note"
  >
>;

export type DeliveryProjectSummary = {
  site_count: number;
  delivered_count: number;
  installed_count: number;
  delayed_count: number;
  on_hold_count: number;
  by_milestone: Record<string, number>;
  circles: string[];
};

export type DeliveryProject = DeliveryProjectSummary & {
  id: string;
  project_code: string;
  name: string;
  company_account_id: string | null;
  customer_name: string | null;
  opportunity_id: string | null;
  tracking_token: string;
  public_tracking_enabled: boolean;
  status: "active" | "on_hold" | "completed";
  remarks: string | null;
  created_at: string | null;
};

export type DeliveryProjectDetail = DeliveryProject & { sites: DeliverySite[] };

export type TrackerImportResult = {
  updated: number;
  created: number;
  unchanged: number;
  errors: { row: number; message: string }[];
};

const DP = `${SCM}/delivery-projects`;

export async function listDeliveryProjects(): Promise<DeliveryProject[]> {
  return asArray((await apiClient<DeliveryProject[]>(DP)).data);
}

export async function getDeliveryProject(id: string): Promise<DeliveryProjectDetail> {
  return unwrap(await apiClient<DeliveryProjectDetail>(`${DP}/${id}`));
}

export async function createDeliveryProject(body: {
  name: string;
  opportunity_id?: string | null;
  company_account_id?: string | null;
  customer_name?: string | null;
  remarks?: string | null;
}): Promise<DeliveryProjectDetail> {
  return unwrap(await apiClient<DeliveryProjectDetail>(DP, { method: "POST", body }));
}

export async function updateDeliveryProject(
  id: string,
  body: {
    name?: string;
    customer_name?: string | null;
    remarks?: string | null;
    status?: DeliveryProject["status"];
    public_tracking_enabled?: boolean;
    rotate_tracking_token?: boolean;
  },
): Promise<DeliveryProjectDetail> {
  return unwrap(await apiClient<DeliveryProjectDetail>(`${DP}/${id}`, { method: "PATCH", body }));
}

export async function addDeliverySite(projectId: string, body: DeliverySiteInput): Promise<DeliverySite> {
  return unwrap(await apiClient<DeliverySite>(`${DP}/${projectId}/sites`, { method: "POST", body }));
}

export async function updateDeliverySite(siteId: string, body: DeliverySiteInput): Promise<DeliverySite> {
  return unwrap(await apiClient<DeliverySite>(`${SCM}/delivery-sites/${siteId}`, { method: "PATCH", body }));
}

export async function deleteDeliverySite(siteId: string): Promise<void> {
  await apiClient(`${SCM}/delivery-sites/${siteId}`, { method: "DELETE" });
}

export async function importSitesFromOpportunity(projectId: string): Promise<number> {
  return unwrap(
    await apiClient<{ created: number }>(`${DP}/${projectId}/import-from-opportunity`, { method: "POST", body: {} }),
  ).created;
}

export async function downloadDeliveryTracker(project: Pick<DeliveryProject, "id" | "project_code">): Promise<void> {
  await downloadApiFile(`${DP}/${project.id}/excel`, undefined, `${project.project_code}-tracker.xlsx`);
}

export async function uploadDeliveryTracker(projectId: string, contentBase64: string): Promise<TrackerImportResult> {
  return unwrap(
    await apiClient<TrackerImportResult>(`${DP}/${projectId}/excel`, {
      method: "POST",
      body: { content_base64: contentBase64 },
    }),
  );
}

export function projectTrackingUrl(token: string): string {
  const origin = typeof window !== "undefined" ? window.location.origin : "";
  return `${origin}/track/project/${encodeURIComponent(token)}`;
}

// ---------------------------------------------------------------------------
// Public (customer) view - no auth
// ---------------------------------------------------------------------------

export type PublicTrackerSite = {
  circle: string | null;
  site_code: string | null;
  site_name: string;
  customer_po_number: string | null;
  milestone: string;
  milestone_label: string;
  milestone_step: number;
  milestone_steps: number;
  status: string;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  awb_number: string | null;
  delayed: boolean;
  updated_at: string | null;
};

export type PublicTracker = DeliveryProjectSummary & {
  project_code: string;
  name: string;
  customer_name: string | null;
  status: string;
  sites: PublicTrackerSite[];
};

export async function getPublicTracker(token: string): Promise<PublicTracker> {
  const res = await fetch(`${env.apiUrl}/public/project-tracking/${encodeURIComponent(token)}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  const payload = (await res.json().catch(() => null)) as { data?: PublicTracker; message?: string } | null;
  if (!res.ok || !payload?.data) {
    throw new ApiClientError(payload?.message ?? "Tracker not found", res.status);
  }
  return payload.data;
}
