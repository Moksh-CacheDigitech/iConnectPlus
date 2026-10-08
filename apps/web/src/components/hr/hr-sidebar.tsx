"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useMemo } from "react";
import { Users } from "lucide-react";

import {
  ModuleSidebar,
  type ModuleNavGroup,
  type ModuleNavItem,
} from "@/components/layout/module-sidebar";
import { flattenHrNavHrefs, hrNavGroups, type HrNavGroup, type HrNavItem } from "@/config/hr-nav";
import { useUserPermissions } from "@/hooks/use-user-permissions";

function navHrefMatches(pathname: string, search: string, href: string): boolean {
  const [pathPart, queryPart] = href.split("?");
  if (pathPart === "/hr") return pathname === "/hr" && !queryPart;
  if (pathPart === "/hr/ess") {
    return pathname === "/hr/ess" || pathname.startsWith("/hr/ess-inbox");
  }
  const pathOk = pathname === pathPart || pathname.startsWith(`${pathPart}/`);
  if (!pathOk) return false;
  if (!queryPart) {
    // Parent /hr/setup matches any setup path; children with ?section= are more specific
    return true;
  }
  const want = new URLSearchParams(queryPart);
  const have = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  for (const [k, v] of want.entries()) {
    if (have.get(k) !== v) return false;
  }
  return true;
}

function resolveActiveHref(pathname: string, search: string, hrefs: string[]): string | null {
  const matches = hrefs.filter((href) => navHrefMatches(pathname, search, href));
  if (!matches.length) return null;
  // Prefer longer / more specific (query string counts)
  return matches.sort((a, b) => b.length - a.length)[0] ?? null;
}

function visibleNavGroups(isHrmsSuperAdmin: boolean): HrNavGroup[] {
  return hrNavGroups.map((group) => ({
    ...group,
    items: group.items.filter((item) => isHrmsSuperAdmin || !item.superAdminOnly),
  }));
}

function toModuleNavItem(item: HrNavItem): ModuleNavItem {
  return {
    title: item.title,
    href: item.href,
    icon: item.icon,
    keywords: item.description,
    children: item.children?.map(toModuleNavItem),
  };
}

/** Left sidebar for HRMS routes (`/hr`), on the shared enterprise rail. */
export function HrSidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const search = searchParams.toString();
  const { isHrmsSuperAdmin } = useUserPermissions();

  const hrGroups = useMemo(() => visibleNavGroups(isHrmsSuperAdmin), [isHrmsSuperAdmin]);
  const groups = useMemo<ModuleNavGroup[]>(
    () =>
      hrGroups.map((group) => ({
        label: group.label || undefined,
        items: group.items.map(toModuleNavItem),
      })),
    [hrGroups],
  );
  const activeHref = useMemo(
    () => resolveActiveHref(pathname, search, flattenHrNavHrefs(hrGroups)),
    [pathname, search, hrGroups],
  );

  return (
    <ModuleSidebar
      moduleKey="hr"
      title="HRMS"
      subtitle="Workforce · Leave · Pay"
      icon={Users}
      aria-label="HR workspace"
      groups={groups}
      isActive={(item) => item.href === activeHref}
      searchPlaceholder="Search HR…"
    />
  );
}
