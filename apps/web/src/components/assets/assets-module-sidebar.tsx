"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Package } from "lucide-react";

import {
  ModuleSidebar,
  type ModuleNavGroup,
  type ModuleNavItem,
} from "@/components/layout/module-sidebar";
import {
  activeAssetDomainFromPath,
  buildAssetSidebarNav,
  isAssetNavActive,
  type AssetDomainKey,
} from "@/config/assets";
import { fetchMyDomainAccess } from "@/services/asset-domain-membership-service";

type MatchMode = "exact" | "prefix";

/**
 * Docked Asset Management sidebar.
 * Top: IT / Non-IT domain switcher. Active domain expands workspace + nested Users.
 */
export function AssetsModuleSidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isModuleAdmin, setIsModuleAdmin] = useState(false);
  const [domains, setDomains] = useState<string[]>([]);
  const [adminDomains, setAdminDomains] = useState<string[]>([]);
  const [accessLoaded, setAccessLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const me = await fetchMyDomainAccess();
        if (!cancelled) {
          setIsModuleAdmin(me.is_module_admin);
          setDomains(me.domains ?? []);
          setAdminDomains(me.admin_domains ?? []);
        }
      } catch {
        if (!cancelled) {
          setIsModuleAdmin(false);
          setDomains([]);
          setAdminDomains([]);
        }
      } finally {
        if (!cancelled) setAccessLoaded(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const activeDomain: AssetDomainKey | null = useMemo(() => {
    if (pathname.startsWith("/assets/users")) {
      const q = (searchParams.get("domain") || "").toUpperCase();
      if (q === "IT" || q === "NON_IT") return q;
      return "IT";
    }
    return activeAssetDomainFromPath(pathname);
  }, [pathname, searchParams]);

  const gatedNav = useMemo(() => {
    if (!accessLoaded) {
      return buildAssetSidebarNav({
        isModuleAdmin: false,
        domains: ["IT"],
        adminDomains: [],
        activeDomain: activeDomain ?? "IT",
      });
    }
    return buildAssetSidebarNav({
      isModuleAdmin,
      domains,
      adminDomains,
      activeDomain,
    });
  }, [accessLoaded, isModuleAdmin, domains, adminDomains, activeDomain]);

  const { groups, matchModes } = useMemo(() => {
    const modes = new Map<string, MatchMode>();
    const mapped: ModuleNavGroup[] = gatedNav.map((group) => ({
      label: group.title,
      items: group.items.map((item) => {
        modes.set(`${item.href}|${item.title}`, item.match ?? "prefix");
        return { title: item.title, href: item.href, icon: item.icon };
      }),
    }));
    return { groups: mapped, matchModes: modes };
  }, [gatedNav]);

  const isActive = (item: ModuleNavItem): boolean => {
    if (item.href === "/assets" && item.title === "IT Assets") return activeDomain === "IT";
    if (item.href === "/assets/non-it" && item.title === "Non-IT Assets") {
      return activeDomain === "NON_IT";
    }
    if (item.href.startsWith("/assets/users")) {
      return (
        pathname.startsWith("/assets/users") &&
        (searchParams.get("domain") || "IT").toUpperCase() ===
          (item.href.includes("NON_IT") ? "NON_IT" : "IT")
      );
    }
    return isAssetNavActive(
      pathname,
      item.href,
      matchModes.get(`${item.href}|${item.title}`) ?? "prefix",
    );
  };

  return (
    <ModuleSidebar
      moduleKey="assets"
      title="Asset Management"
      subtitle="IT · Non-IT"
      icon={Package}
      aria-label="Asset Management"
      testId="assets-module-sidebar"
      groups={groups}
      isActive={isActive}
      searchPlaceholder="Search Assets…"
      showAccount={false}
    />
  );
}
