"use client";

import { usePathname } from "next/navigation";
import { useMemo } from "react";
import type { LucideIcon } from "lucide-react";
import {
  CheckCircle2,
  Clock3,
  Headphones,
  Inbox,
  LayoutDashboard,
  Ticket,
  UserCog,
  Wrench,
} from "lucide-react";

import { ModuleSidebar } from "@/components/layout/module-sidebar";
import { useAuthUser } from "@/hooks/use-auth-user";
import { useUserPermissions } from "@/hooks/use-user-permissions";
import { canManageModuleUsers } from "@/lib/module-access";
import {
  hasServiceFieldEngineerRole,
  isServiceFieldEngineerOnly,
} from "@/lib/service-field-engineer-access";

export type ServiceNavItem = {
  title: string;
  href: string;
  icon: LucideIcon;
  mailboxAccess?: boolean;
  fieldEngineerOnly?: boolean;
};

/** SOP service request ticket workflow - CRM-style workspace panes. */
export const SERVICE_NAV: readonly ServiceNavItem[] = [
  { title: "Dashboard", href: "/service", icon: LayoutDashboard },
  { title: "Request Tickets", href: "/service/service-request-tickets", icon: Ticket },
  { title: "Mailbox", href: "/service/mailbox", icon: Inbox, mailboxAccess: true },
  {
    title: "Field Engineer",
    href: "/service/field-engineer",
    icon: Wrench,
    fieldEngineerOnly: true,
  },
  { title: "SLAs", href: "/service/service-slas", icon: Clock3 },
  { title: "Resolved", href: "/service/resolved-tickets", icon: CheckCircle2 },
];

function canViewServiceMailbox(permissions: string[] | undefined | null): boolean {
  const perms = permissions ?? [];
  return perms.includes("service.request:update") || perms.includes("service.request:approve");
}

function filterServiceNav(
  items: readonly ServiceNavItem[],
  opts: {
    permissions?: string[] | null;
    roleCodes?: string[] | null;
    roleNames?: string[] | null;
  },
): ServiceNavItem[] {
  const isFe = hasServiceFieldEngineerRole(opts.roleCodes, opts.roleNames);
  const feOnly = isServiceFieldEngineerOnly(opts.roleCodes, opts.permissions, opts.roleNames);

  return items.filter((item) => {
    if (item.fieldEngineerOnly) return isFe;
    if (item.mailboxAccess) return canViewServiceMailbox(opts.permissions) && !feOnly;
    if (feOnly) return false;
    return true;
  });
}

function isServiceNavActive(pathname: string, href: string): boolean {
  if (href === "/service") return pathname === "/service";
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Left sidebar for the Service workspace. */
export function ServiceSidebar() {
  const pathname = usePathname();
  const { user, adminModuleKeys } = useAuthUser();
  const { profile, loading } = useUserPermissions();

  const navItems = useMemo(() => {
    const items = filterServiceNav(SERVICE_NAV, {
      permissions: profile?.permissions,
      roleCodes: profile?.roleCodes,
      roleNames: profile?.roleNames,
    });
    const feOnly = isServiceFieldEngineerOnly(
      profile?.roleCodes,
      profile?.permissions,
      profile?.roleNames,
    );
    if (!feOnly && canManageModuleUsers("service", adminModuleKeys, user?.userType)) {
      items.push({ title: "Users", href: "/service/users", icon: UserCog });
    }
    return items;
  }, [
    adminModuleKeys,
    profile?.permissions,
    profile?.roleCodes,
    profile?.roleNames,
    user?.userType,
  ]);

  return (
    <ModuleSidebar
      moduleKey="service"
      title="Service"
      subtitle={loading ? "…" : `${navItems.length} workspace panes`}
      icon={Headphones}
      aria-label="Service workspace"
      groups={[{ label: "Workspace", items: navItems }]}
      isActive={(item) => isServiceNavActive(pathname, item.href)}
      loading={loading}
    />
  );
}
