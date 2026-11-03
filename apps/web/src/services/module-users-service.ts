import { apiClient } from "@/services/api-client";

export type ServiceJobRole = "service_engineer" | "field_engineer";

export type MarketingTeamRole =
  | "marketing_head"
  | "marketing_associate"
  | "video_editor"
  | "graphic_designer"
  | "content_creator"
  | "approval_head"
  | "supporting_member"
  | "member";

export type ModuleUserOption = {
  user_id: string;
  display_name: string;
  email: string;
  employee_code?: string | null;
  already_assigned?: boolean;
};

export type ModuleUserRecord = {
  user_id: string;
  display_name: string;
  email: string;
  role: "admin" | "member" | string;
  status: string;
  service_job_role?: ServiceJobRole | null;
};

export async function listModuleMembers(moduleKey: string): Promise<ModuleUserRecord[]> {
  const res = await apiClient<ModuleUserRecord[]>(`/modules/${moduleKey}/members`);
  return Array.isArray(res.data) ? res.data : [];
}

export async function listAssignableModuleUsers(moduleKey: string): Promise<ModuleUserOption[]> {
  const res = await apiClient<ModuleUserOption[]>(`/modules/${moduleKey}/assignable-users`);
  return Array.isArray(res.data) ? res.data : [];
}

export async function addModuleMember(
  moduleKey: string,
  userId: string,
  serviceJobRole?: ServiceJobRole,
  role?: string,
): Promise<ModuleUserRecord> {
  const res = await apiClient<ModuleUserRecord>(`/modules/${moduleKey}/members`, {
    method: "POST",
    body: {
      user_id: userId,
      ...(serviceJobRole ? { service_job_role: serviceJobRole } : {}),
      ...(role ? { role } : {}),
    },
  });
  if (!res.data) {
    throw new Error("Empty response");
  }
  return res.data;
}

export async function updateModuleMemberServiceRole(
  moduleKey: string,
  userId: string,
  serviceJobRole: ServiceJobRole,
): Promise<ModuleUserRecord> {
  const res = await apiClient<ModuleUserRecord>(
    `/modules/${moduleKey}/members/${userId}/service-role`,
    {
      method: "PATCH",
      body: { service_job_role: serviceJobRole },
    },
  );
  if (!res.data) {
    throw new Error("Empty response");
  }
  return res.data;
}

export async function updateModuleMemberRole(
  moduleKey: string,
  userId: string,
  role: string,
): Promise<ModuleUserRecord> {
  const res = await apiClient<ModuleUserRecord>(
    `/modules/${moduleKey}/members/${userId}/role`,
    {
      method: "PATCH",
      body: { role },
    },
  );
  if (!res.data) {
    throw new Error("Empty response");
  }
  return res.data;
}

export async function removeModuleMember(moduleKey: string, userId: string): Promise<void> {
  await apiClient(`/modules/${moduleKey}/members/${userId}`, { method: "DELETE" });
}

export type ModuleDemoSeedResult = {
  module_key: string;
  created: number;
  updated: number;
  password: string;
  accounts: Array<{
    email: string;
    display_name: string;
    role: string;
    role_label: string;
  }>;
};

export async function seedModuleDemoUsers(moduleKey: string): Promise<ModuleDemoSeedResult> {
  const res = await apiClient<ModuleDemoSeedResult>(`/modules/${moduleKey}/seed-demo-users`, {
    method: "POST",
  });
  if (!res.data) throw new Error("Seed demo users failed");
  return res.data;
}
