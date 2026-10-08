"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, type ComponentType } from "react";
import {
  BadgeCheck,
  BarChart3,
  Boxes,
  Building2,
  ClipboardList,
  FileBarChart,
  FileSignature,
  FileSpreadsheet,
  FolderKanban,
  History,
  Hourglass,
  LayoutDashboard,
  MapPinned,
  Mail,
  Package,
  PackageCheck,
  ShoppingCart,
  Truck,
  UserCog,
  Wrench,
} from "lucide-react";

import { ModuleSidebar, type ModuleNavItem } from "@/components/layout/module-sidebar";
import { canManageModuleUsers } from "@/lib/module-access";
import { useAuthUser } from "@/hooks/use-auth-user";
import { useProcurementApprovals } from "@/hooks/use-procurement-approvals";
import { useProcurementRole } from "@/hooks/use-procurement-role";
import { useScmQueueUnreadCount } from "@/hooks/use-scm-queue-unread-count";
import { prefetchProcurementTab } from "@/services/procurement-service";
import { useDeliveryReminderSweep } from "@/hooks/use-delivery-reminder-sweep";

type NavIcon = ComponentType<{ className?: string; "aria-hidden"?: boolean }>;

type ProcurementNavItem = {
  title: string;
  href: string;
  icon: NavIcon;
};

export const PROCUREMENT_NAV = [
  { title: "Dashboard", href: "/procurement", icon: LayoutDashboard },
  { title: "SCM Queue", href: "/procurement/scm", icon: ClipboardList },
  { title: "Purchase Orders", href: "/procurement/orders", icon: ShoppingCart },
  { title: "GRNs", href: "/procurement/grns", icon: PackageCheck },
  { title: "Billing/DC", href: "/procurement/delivery-challan", icon: Truck },
  { title: "Delivery Status", href: "/procurement/delivery-status", icon: MapPinned },
  { title: "Delivery Projects", href: "/procurement/delivery-projects", icon: FolderKanban },
  { title: "Tracker Upload", href: "/procurement/tracker", icon: FileSpreadsheet },
  { title: "Installation", href: "/procurement/installation", icon: Wrench },
  { title: "Service Contracts", href: "/procurement/service-contracts", icon: FileSignature },
  { title: "Vendors", href: "/procurement/vendors", icon: Building2 },
  { title: "Inventory", href: "/procurement/inventory", icon: Boxes },
  { title: "Stock Aging", href: "/procurement/inventory-aging", icon: Hourglass },
  { title: "Approval", href: "/procurement/approval", icon: BadgeCheck },
] as const satisfies ReadonlyArray<ProcurementNavItem>;

export const PROCUREMENT_INSIGHT_NAV = [
  { title: "Mails", href: "/procurement/correspondence", icon: Mail },
  { title: "Reports", href: "/procurement/reports", icon: FileBarChart },
  { title: "Analytics", href: "/procurement/analytics", icon: BarChart3 },
  { title: "Timeline", href: "/procurement/timeline", icon: History },
] as const satisfies ReadonlyArray<ProcurementNavItem>;

export const ALL_PROCUREMENT_NAV = [
  ...PROCUREMENT_NAV,
  ...PROCUREMENT_INSIGHT_NAV,
] as const;

export function warmProcurementNavTarget(
  router: ReturnType<typeof useRouter>,
  href: string,
): void {
  router.prefetch(href);
  prefetchProcurementTab(href);
}

export function warmAllProcurementNavTargets(router: ReturnType<typeof useRouter>): void {
  for (const item of ALL_PROCUREMENT_NAV) {
    warmProcurementNavTarget(router, item.href);
  }
  warmProcurementNavTarget(router, "/procurement/users");
}

function isProcurementNavActive(pathname: string, href: string): boolean {
  if (href === "/procurement") {
    return pathname === "/procurement";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Left sidebar for the Procurement workspace. */
export function ProcurementSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, adminModuleKeys } = useAuthUser();
  const { isAdmin } = useProcurementRole();
  const { pendingCount } = useProcurementApprovals();
  const scmUnreadCount = useScmQueueUnreadCount();
  useDeliveryReminderSweep();

  const workspaceItems = useMemo(() => {
    const items: ModuleNavItem[] = PROCUREMENT_NAV.map((item) => ({
      ...item,
      badge:
        item.href === "/procurement/approval" && isAdmin
          ? pendingCount
          : item.href === "/procurement/scm"
            ? scmUnreadCount
            : undefined,
    }));
    if (canManageModuleUsers("procurement", adminModuleKeys, user?.userType)) {
      items.push({ title: "Users", href: "/procurement/users", icon: UserCog });
    }
    return items;
  }, [adminModuleKeys, isAdmin, pendingCount, scmUnreadCount, user?.userType]);

  useEffect(() => {
    if (typeof requestIdleCallback !== "undefined") {
      const id = requestIdleCallback(() => warmAllProcurementNavTargets(router), {
        timeout: 2000,
      });
      return () => cancelIdleCallback(id);
    }
    const timer = window.setTimeout(() => warmAllProcurementNavTargets(router), 100);
    return () => window.clearTimeout(timer);
  }, [router]);

  useEffect(() => {
    const active =
      workspaceItems.find((item) => isProcurementNavActive(pathname, item.href)) ??
      ALL_PROCUREMENT_NAV.find((item) => isProcurementNavActive(pathname, item.href)) ??
      PROCUREMENT_NAV[0];
    warmProcurementNavTarget(router, active.href);
  }, [workspaceItems, pathname, router]);

  return (
    <ModuleSidebar
      moduleKey="procurement"
      title="Procurement"
      subtitle={isAdmin ? "Admin workspace" : "SCM workspace"}
      icon={Package}
      aria-label="Procurement workspace"
      groups={[
        { label: "Workspace", items: workspaceItems },
        { label: "Insight", items: PROCUREMENT_INSIGHT_NAV },
      ]}
      isActive={(item) => isProcurementNavActive(pathname, item.href)}
      onItemWarm={(item) => warmProcurementNavTarget(router, item.href)}
    />
  );
}
