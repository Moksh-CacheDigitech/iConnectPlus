"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";

import { CrmGlobalSearch } from "@/components/crm/crm-global-search";
import { ModulePaneSearch } from "@/components/layout/module-pane-search";
import { ProjectsGlobalSearch } from "@/components/projects/projects-global-search";
import { navigation } from "@/config/navigation";
import { useAuthUser } from "@/hooks/use-auth-user";
import { filterNavigationGroups, hasModuleAssignments } from "@/lib/module-access";
import {
  homeModuleHits,
  resolveShellSearchScope,
} from "@/lib/shell-search";

/** Topbar search: CRM/Projects entity search, or module/pane finder everywhere else. */
export function ShellGlobalSearch({ className }: { className?: string }) {
  const pathname = usePathname();
  const scope = resolveShellSearchScope(pathname);
  const {
    user,
    loading: userLoading,
    moduleKeys,
    adminModuleKeys,
    status: authStatus,
  } = useAuthUser();

  const homePanes = useMemo(() => {
    if (scope.mode !== "home") return [];
    const sessionPending = userLoading || authStatus === "loading";
    if (sessionPending || authStatus === "error") {
      const limited = navigation
        .flatMap((group) => group.items)
        .filter(
          (item) =>
            item.href === "/" || item.href === "/home" || item.href === "/my-jobs",
        );
      return homeModuleHits(limited);
    }
    const groups = filterNavigationGroups(
      navigation,
      moduleKeys,
      user?.userType,
      adminModuleKeys,
    );
    if (!hasModuleAssignments(moduleKeys, user?.userType, adminModuleKeys)) {
      return homeModuleHits(
        groups.flatMap((g) => g.items).filter((item) => item.href === "/home" || item.href === "/my-jobs"),
      );
    }
    return homeModuleHits(groups.flatMap((g) => g.items));
  }, [scope.mode, userLoading, authStatus, moduleKeys, adminModuleKeys, user?.userType]);

  if (scope.mode === "crm") {
    return <CrmGlobalSearch className={className} />;
  }
  if (scope.mode === "projects") {
    return <ProjectsGlobalSearch className={className} />;
  }
  if (scope.mode === "panes") {
    return (
      <ModulePaneSearch
        className={className}
        placeholder={scope.placeholder}
        panes={scope.panes}
      />
    );
  }

  return (
    <ModulePaneSearch
      className={className}
      placeholder={scope.placeholder}
      panes={homePanes}
    />
  );
}
