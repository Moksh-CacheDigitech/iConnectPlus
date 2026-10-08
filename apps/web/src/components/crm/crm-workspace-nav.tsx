"use client";

import { usePathname } from "next/navigation";
import { useMemo } from "react";
import type { LucideIcon } from "lucide-react";
import {
  Boxes,
  BriefcaseBusiness,
  Building2,
  CalendarDays,
  ClipboardList,
  Factory,
  FileSpreadsheet,
  FileText,
  Handshake,
  Landmark,
  LayoutDashboard,
  ListTodo,
  Package,
  BarChart3,
  Receipt,
  ScrollText,
  ShieldCheck,
  ShoppingCart,
  Target,
  TrendingDown,
  Truck,
  UserCog,
  UserPlus,
  Users,
  UserRound,
} from "lucide-react";

import { ModuleSidebar, type ModuleNavItem } from "@/components/layout/module-sidebar";
import {
  getCrmSidebarFocus,
  isCompanyDealWorkspacePath,
  setCrmOpportunityContext,
  setCrmSidebarFocus,
  type CrmSidebarFocus,
} from "@/lib/crm-sidebar-focus";
import { canManageModuleUsers } from "@/lib/module-access";
import { useAuthUser } from "@/hooks/use-auth-user";

type CrmNavItem = {
  title: string;
  href: string;
  icon: LucideIcon;
};

/** Sales CRM (Zoho-replacement) teamspace navigation. */
export const CRM_NAV: readonly CrmNavItem[] = [
  { title: "Dashboard", href: "/crm", icon: LayoutDashboard },
  { title: "Reports", href: "/crm/reports", icon: BarChart3 },
  { title: "My Jobs", href: "/crm/my-jobs", icon: ListTodo },
  { title: "Company", href: "/crm/companies", icon: Building2 },
  { title: "Leads", href: "/crm/leads", icon: UserPlus },
  { title: "Opportunities", href: "/crm/opportunities", icon: Target },
  { title: "Vendor Quote", href: "/crm/oem-quotes", icon: FileSpreadsheet },
  { title: "Quotes", href: "/crm/quotes", icon: FileText },
  { title: "Purchase Order", href: "/crm/purchase-orders", icon: ShoppingCart },
  { title: "OVF", href: "/crm/ovf", icon: Receipt },
  { title: "Sales Performance", href: "/crm/sales-performance", icon: TrendingDown },
  { title: "Stock & Aging", href: "/crm/inventory-aging", icon: Boxes },
  { title: "Contacts", href: "/crm/contacts", icon: Users },
  { title: "Products", href: "/crm/products", icon: Package },
  { title: "Meetings", href: "/crm/meetings", icon: CalendarDays },
  { title: "Customer Follow Ups", href: "/crm/customer-followups", icon: BriefcaseBusiness },
  { title: "KYC - Account Mapping", href: "/crm/kyc-account-mapping", icon: ShieldCheck },
  { title: "OEM", href: "/crm/oem", icon: Factory },
  { title: "Distributor", href: "/crm/distributors", icon: Truck },
  { title: "BOQ", href: "/crm/boq", icon: ClipboardList },
  { title: "SOW", href: "/crm/sow", icon: ScrollText },
  { title: "Entity", href: "/crm/entities", icon: Landmark },
  { title: "End Customer", href: "/crm/end-customers", icon: UserRound },
];

function focusForHref(href: string): CrmSidebarFocus | null {
  if (href === "/crm") return "dashboard";
  if (href === "/crm/companies") return "company";
  if (href === "/crm/leads") return "leads";
  if (href === "/crm/opportunities") return "opportunities";
  return null;
}

function isCrmNavActive(pathname: string, href: string): boolean {
  const focus = getCrmSidebarFocus();

  // Dashboard is exact-match only - `/crm` must not light up for every CRM child route.
  if (href === "/crm") {
    return pathname === "/crm";
  }

  // Company list / overview only - not company section routes (quotes, PO, …).
  if (href === "/crm/companies") {
    if (focus === "opportunities" && isCompanyDealWorkspacePath(pathname)) {
      return false;
    }
    if (pathname === "/crm/companies" || pathname === "/crm/companies/") return true;
    // Company account overview: /crm/companies/{uuid} with no further segment.
    return /^\/crm\/companies\/[^/]+\/?$/.test(pathname) && focus !== "opportunities";
  }

  // Keep Opportunities highlighted while browsing deal docs under a company from an opportunity.
  if (href === "/crm/opportunities") {
    if (pathname === href || pathname.startsWith(`${href}/`)) {
      if (pathname.includes("/quotes") || pathname.includes("/ovf")) return false;
      return true;
    }
    if (focus === "opportunities" && isCompanyDealWorkspacePath(pathname)) {
      return true;
    }
    return false;
  }

  if (pathname === href || pathname.startsWith(`${href}/`)) {
    return true;
  }
  if (href === "/crm/quotes" && pathname.includes("/quotes")) return true;
  if (href === "/crm/ovf" && pathname.includes("/ovf")) return true;
  return false;
}

function onCrmNavigate(item: ModuleNavItem) {
  const focus = focusForHref(item.href);
  if (focus) setCrmSidebarFocus(focus);
  if (focus !== "opportunities") setCrmOpportunityContext(null);
}

/** Left sidebar for the CRM workspace. */
export function CrmSidebar() {
  const pathname = usePathname();
  const { user, adminModuleKeys } = useAuthUser();

  const navItems = useMemo(() => {
    const items: CrmNavItem[] = [...CRM_NAV];
    if (canManageModuleUsers("crm", adminModuleKeys, user?.userType)) {
      items.push({ title: "Users", href: "/crm/users", icon: UserCog });
    }
    return items;
  }, [adminModuleKeys, user?.userType]);

  return (
    <ModuleSidebar
      moduleKey="crm"
      title="Sales CRM"
      subtitle={`${navItems.length} workspace panes`}
      icon={Handshake}
      aria-label="CRM workspace"
      groups={[{ label: "Workspace", items: navItems }]}
      isActive={(item) => isCrmNavActive(pathname, item.href)}
      searchPlaceholder="Search CRM…"
      onItemNavigate={onCrmNavigate}
    />
  );
}
