import type { LucideIcon } from "lucide-react";
import {
  Building2,
  ClipboardList,
  KeyRound,
  Settings2,
  Shield,
  UserRound,
  Users,
} from "lucide-react";

export type FoundationSetupStepId =
  | "access"
  | "tenant"
  | "users"
  | "rbac"
  | "engines"
  | "settings"
  | "handoff";

export type FoundationSetupCheck = {
  key: string;
  label: string;
  /** Relative API list path under /api/v1; omitted for informational-only checks. */
  apiPath?: string;
};

export type FoundationSetupStep = {
  id: FoundationSetupStepId;
  title: string;
  shortLabel: string;
  description: string;
  icon: LucideIcon;
  /** Primary admin deep-links for this step. */
  actions: { label: string; href: string }[];
  checks: FoundationSetupCheck[];
};

/** Locked Foundation sequence (FRD-01 → Organization handoff). */
export const FOUNDATION_SETUP_STEPS: readonly FoundationSetupStep[] = [
  {
    id: "access",
    title: "Access & sessions",
    shortLabel: "Access",
    description:
      "Confirm sign-in, session timeout, and who can reach the ERP. Authentication is already live; review settings and audit of logins before inviting more users.",
    icon: KeyRound,
    actions: [
      { label: "Open settings", href: "/foundation/settings" },
      { label: "View audit log", href: "/foundation/audit" },
    ],
    checks: [
      { key: "settings", label: "System settings reachable", apiPath: "/settings" },
      { key: "audit", label: "Audit log reachable", apiPath: "/audit/logs" },
    ],
  },
  {
    id: "tenant",
    title: "Tenant registry",
    shortLabel: "Tenant",
    description:
      "Every record is scoped by tenant. Ensure the active tenant exists and is correctly named before adding companies or users.",
    icon: Building2,
    actions: [{ label: "Manage tenants", href: "/foundation/tenants" }],
    checks: [{ key: "tenants", label: "At least one tenant", apiPath: "/tenants" }],
  },
  {
    id: "users",
    title: "User accounts",
    shortLabel: "Users",
    description:
      "Create ERP users (email, status, company/branch context). Users authenticate here; organization structure is assigned next in Organization.",
    icon: Users,
    actions: [{ label: "Manage users", href: "/foundation/users" }],
    checks: [{ key: "users", label: "At least one user", apiPath: "/users" }],
  },
  {
    id: "rbac",
    title: "Roles & permissions",
    shortLabel: "RBAC",
    description:
      "Define roles, attach permissions, and assign roles to users. Business modules refuse actions without the matching permission code.",
    icon: Shield,
    actions: [
      { label: "Manage roles", href: "/foundation/roles" },
      { label: "Permission catalog", href: "/foundation/permissions" },
    ],
    checks: [
      { key: "roles", label: "Roles configured", apiPath: "/roles" },
      { key: "permissions", label: "Permissions catalog", apiPath: "/permissions" },
    ],
  },
  {
    id: "engines",
    title: "Workflow, notification & audit",
    shortLabel: "Engines",
    description:
      "Platform engines every module must use — approval workflows, notification templates, and the central audit trail. Do not bypass these in business modules.",
    icon: ClipboardList,
    actions: [
      { label: "Workflow definitions", href: "/foundation/workflows" },
      { label: "Notification templates", href: "/foundation/notifications" },
      { label: "Audit logs", href: "/foundation/audit" },
    ],
    checks: [
      { key: "workflows", label: "Workflow definitions", apiPath: "/workflows/definitions" },
      { key: "notifications", label: "Notification templates", apiPath: "/notifications/templates" },
      { key: "audit", label: "Audit logs", apiPath: "/audit/logs" },
    ],
  },
  {
    id: "settings",
    title: "Global settings",
    shortLabel: "Settings",
    description:
      "Tenant-level defaults (locale, session policy, feature flags). Keep business masters out of this screen — they belong in Master Data.",
    icon: Settings2,
    actions: [{ label: "Open settings", href: "/foundation/settings" }],
    checks: [{ key: "settings", label: "Settings reachable", apiPath: "/settings" }],
  },
  {
    id: "handoff",
    title: "Next: Organization",
    shortLabel: "Next",
    description:
      "Foundation covers who can do what and how approvals/notifications/audit work. Next is Organization (company structure), then Master Data (shared business masters).",
    icon: UserRound,
    actions: [
      { label: "Go to Organization", href: "/organization" },
      { label: "Master Data", href: "/master-data" },
    ],
    checks: [],
  },
] as const;

export const FOUNDATION_SETUP_STORAGE_KEY = "erp.foundation.setup.completedSteps";

export function foundationSetupStepIndex(id: FoundationSetupStepId): number {
  return FOUNDATION_SETUP_STEPS.findIndex((s) => s.id === id);
}
