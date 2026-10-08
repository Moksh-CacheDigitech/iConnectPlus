"use client";

import { usePathname } from "next/navigation";
import { useMemo } from "react";
import { UserCog } from "lucide-react";

import { ModuleSidebar, type ModuleNavItem } from "@/components/layout/module-sidebar";
import {
  isWorkspaceItemActive,
  type WorkspaceSidebarConfig,
  type WorkspaceSidebarItem,
} from "@/config/workspace-sidebars";
import { useAuthUser } from "@/hooks/use-auth-user";
import { canManageModuleUsers, moduleUsersHref } from "@/lib/module-access";

/** Left sidebar for a config-only module workspace (`config/workspace-sidebars.ts`). */
export function WorkspaceModuleSidebar({ config }: { config: WorkspaceSidebarConfig }) {
  const pathname = usePathname();
  const { user, adminModuleKeys } = useAuthUser();

  const items = useMemo(() => {
    const list: WorkspaceSidebarItem[] = [...config.items];
    if (canManageModuleUsers(config.moduleKey, adminModuleKeys, user?.userType)) {
      list.push({ title: "Users", href: moduleUsersHref(config.moduleKey), icon: UserCog });
    }
    return list;
  }, [adminModuleKeys, config, user?.userType]);

  const byHref = useMemo(() => new Map(items.map((item) => [item.href, item])), [items]);

  const isActive = (item: ModuleNavItem) =>
    isWorkspaceItemActive(pathname, config.root, byHref.get(item.href) ?? item);

  return (
    <ModuleSidebar
      moduleKey={config.moduleKey}
      title={config.title}
      subtitle={config.subtitle}
      icon={config.icon}
      aria-label={`${config.title} workspace`}
      groups={[{ label: "Workspace", items }]}
      isActive={isActive}
    />
  );
}
