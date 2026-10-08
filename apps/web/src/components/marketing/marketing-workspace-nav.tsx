"use client";

import { usePathname } from "next/navigation";
import { useMemo } from "react";
import type { LucideIcon } from "lucide-react";
import {
  BarChart3,
  Briefcase,
  CalendarDays,
  ClipboardList,
  FileText,
  FolderKanban,
  Inbox,
  LayoutDashboard,
  LineChart,
  ListTodo,
  Megaphone,
  Palette,
  Radar,
  Search,
  Share2,
  Sparkles,
  TrendingUp,
  UserCog,
  Users,
} from "lucide-react";

import { ModuleSidebar } from "@/components/layout/module-sidebar";
import { useAuthUser } from "@/hooks/use-auth-user";
import { canManageModuleUsers } from "@/lib/module-access";

type MarketingNavItem = {
  title: string;
  href: string;
  icon: LucideIcon;
};

type MarketingNavGroup = {
  label: string;
  items: readonly MarketingNavItem[];
};

/** Marketing & Social workspace panes - CRM-style left nav. */
export const MARKETING_NAV_GROUPS: readonly MarketingNavGroup[] = [
  {
    label: "Workspace",
    items: [
      { title: "Overview", href: "/marketing", icon: LayoutDashboard },
      { title: "Operations", href: "/marketing/operations", icon: Briefcase },
      { title: "My Work", href: "/marketing/my-work", icon: ListTodo },
      { title: "Campaigns", href: "/marketing/campaigns", icon: Megaphone },
      { title: "Inbox", href: "/marketing/inbox", icon: Inbox },
      { title: "Tasks", href: "/marketing/tasks", icon: ClipboardList },
      { title: "Workload", href: "/marketing/workload", icon: Users },
    ],
  },
  {
    label: "Content",
    items: [
      { title: "Content Studio", href: "/marketing/content", icon: FileText },
      { title: "Requests", href: "/marketing/content-requests", icon: FolderKanban },
      { title: "Calendar", href: "/marketing/calendar", icon: CalendarDays },
      { title: "Brand kit", href: "/marketing/brand-voices", icon: Palette },
    ],
  },
  {
    label: "Insights",
    items: [
      { title: "Research", href: "/marketing/research", icon: Search },
      { title: "Trends", href: "/marketing/trends", icon: TrendingUp },
      { title: "Competitors", href: "/marketing/competitors", icon: Radar },
      { title: "Analytics", href: "/marketing/analytics", icon: BarChart3 },
    ],
  },
  {
    label: "Channels",
    items: [
      { title: "Social", href: "/marketing/social-accounts", icon: Share2 },
      { title: "Microsoft 365", href: "/marketing/m365", icon: LineChart },
    ],
  },
] as const;

export const MARKETING_NAV: readonly MarketingNavItem[] = MARKETING_NAV_GROUPS.flatMap(
  (g) => g.items,
);

function isMarketingNavActive(pathname: string, href: string): boolean {
  if (href === "/marketing") return pathname === "/marketing";
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Left sidebar for the Marketing & Social workspace. */
export function MarketingSidebar() {
  const pathname = usePathname();
  const { user, adminModuleKeys } = useAuthUser();

  const groups = useMemo(() => {
    const base: MarketingNavGroup[] = [...MARKETING_NAV_GROUPS];
    if (canManageModuleUsers("marketing", adminModuleKeys, user?.userType)) {
      base.push({
        label: "Admin",
        items: [{ title: "Users", href: "/marketing/users", icon: UserCog }],
      });
    }
    return base;
  }, [adminModuleKeys, user?.userType]);

  const paneCount = groups.reduce((n, g) => n + g.items.length, 0);

  return (
    <ModuleSidebar
      moduleKey="marketing"
      title="Marketing & Social"
      subtitle={`${paneCount} workspace panes`}
      icon={Sparkles}
      aria-label="Marketing workspace"
      groups={groups}
      isActive={(item) => isMarketingNavActive(pathname, item.href)}
      searchPlaceholder="Search Marketing…"
    />
  );
}
