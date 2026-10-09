"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";
import { ChevronLeft, Search, X } from "lucide-react";

import { navigation } from "@/config/navigation";
import { filterNavigationGroups, hasModuleAssignments } from "@/lib/module-access";
import { AppLogo } from "@/components/brand/app-logo";
import { SidebarAccountSection } from "@/components/layout/sidebar-account-section";
import {
  SIDEBAR_EASE as EASE,
  SIDEBAR_LABEL_MS as LABEL_MS,
  SIDEBAR_SEARCH_MS as SEARCH_MS,
  SIDEBAR_WIDTH_MS as WIDTH_MS,
  SidebarRail,
  useSidebarCollapse,
} from "@/components/layout/sidebar-rail";
import { Button } from "@/components/ui/button";
import { useAuthUser } from "@/hooks/use-auth-user";
import { cn } from "@/lib/utils";
import { env } from "@/utils/env";

function isActivePath(pathname: string, href: string) {
  if (href === "/home") return pathname === "/home";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppSidebar() {
  const pathname = usePathname();
  const { collapsed, layoutCollapsed, toggle: toggleCollapsed } = useSidebarCollapse();
  const [query, setQuery] = useState("");
  const {
    user,
    loading: userLoading,
    moduleKeys,
    adminModuleKeys,
    status: authStatus,
    refresh,
  } = useAuthUser();

  const hasModules = hasModuleAssignments(moduleKeys, user?.userType, adminModuleKeys);
  const sessionReady = authStatus === "authenticated";
  const sessionPending = userLoading || authStatus === "loading";

  const navGroups = useMemo(() => {
    if (sessionPending || authStatus === "error") {
      return navigation
        .map((group) => ({
          ...group,
          items: group.items.filter(
            (item) =>
              item.href === "/" ||
              item.href === "/home" ||
              item.href === "/my-jobs",
          ),
        }))
        .filter((group) => group.items.length > 0);
    }
    return filterNavigationGroups(navigation, moduleKeys, user?.userType, adminModuleKeys);
  }, [adminModuleKeys, moduleKeys, user?.userType, sessionPending, authStatus]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return navGroups;
    return navGroups
      .map((group) => ({
        ...group,
        items: group.items.filter(
          (item) =>
            item.title.toLowerCase().includes(q) ||
            item.description?.toLowerCase().includes(q),
        ),
      }))
      .filter((group) => group.items.length > 0);
  }, [query, navGroups]);

  /** Flat list for collapsed icon rail — equal gaps, no section spacing. */
  const flatItems = useMemo(
    () => filtered.flatMap((group) => group.items),
    [filtered],
  );

  const brand = (
    <div className="flex items-center gap-2">
      <AppLogo size={28} className="shrink-0" />
      <div className="min-w-0">
        <p className="truncate text-xs font-semibold text-sidebar-foreground">{env.appName}</p>
        <p className="truncate text-[10px] text-sidebar-foreground/60">
          {sessionPending
            ? "Loading session…"
            : authStatus === "error"
              ? "Session retry needed"
              : "23 modules · live API"}
        </p>
      </div>
    </div>
  );

  return (
    <SidebarRail collapsed={collapsed} layoutCollapsed={layoutCollapsed} aria-label="ERP modules">
      {/* Fill the animated rail — icons must live in the visible width (not a clipped 260px column). */}
      <div className="flex h-full w-full flex-col">
        <SidebarAccountSection collapsed={collapsed}>{brand}</SidebarAccountSection>

        {!collapsed ? (
          <div
            className="grid overflow-hidden px-3 pb-3 opacity-100"
            style={{
              transitionProperty: "opacity",
              transitionDuration: `${SEARCH_MS}ms`,
              transitionTimingFunction: EASE,
            }}
          >
            <div className="min-h-0 overflow-hidden">
              <label className="sr-only" htmlFor="sidebar-module-search">
                Search modules
              </label>
              <div
                className={cn(
                  "group/search relative flex h-10 items-center gap-2 rounded-xl border border-sidebar-border/80",
                  "bg-white/5 px-3 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]",
                  "focus-within:border-sidebar-ring/60 focus-within:bg-white/[0.08] focus-within:ring-2 focus-within:ring-sidebar-ring/35",
                )}
              >
                <Search
                  className="size-[18px] shrink-0 text-sidebar-foreground/70"
                  strokeWidth={2}
                  aria-hidden
                />
                <input
                  id="sidebar-module-search"
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search modules…"
                  autoComplete="off"
                  tabIndex={collapsed ? -1 : 0}
                  className={cn(
                    "min-w-0 flex-1 bg-transparent text-[13px] font-medium tracking-tight text-sidebar-foreground",
                    "placeholder:font-normal placeholder:text-sidebar-foreground/45",
                    "outline-none ring-0",
                    "[&::-webkit-search-cancel-button]:hidden [&::-webkit-search-decoration]:hidden",
                  )}
                />
                {query ? (
                  <button
                    type="button"
                    onClick={() => setQuery("")}
                    className="inline-flex size-6 shrink-0 cursor-pointer items-center justify-center rounded-md text-sidebar-foreground/55 transition-colors duration-150 hover:bg-sidebar-accent hover:text-sidebar-foreground"
                    aria-label="Clear search"
                  >
                    <X className="size-3.5" strokeWidth={2} />
                  </button>
                ) : null}
              </div>
            </div>
          </div>
        ) : null}

        <nav
          className={cn(
            "min-h-0 flex-1 overflow-y-auto overflow-x-hidden py-2",
            "scrollbar-none [-ms-overflow-style:none] [scrollbar-width:none]",
            "[&::-webkit-scrollbar]:hidden",
            collapsed ? "px-0" : "px-2.5",
          )}
        >
          {authStatus === "error" ? (
            <div
              className={cn(
                "mb-4 space-y-2 rounded-lg border border-sidebar-border/80 bg-white/5 px-3 py-2.5 text-[12px] leading-relaxed text-sidebar-foreground/70",
                collapsed && "pointer-events-none opacity-0",
              )}
              style={{
                transition: `opacity ${LABEL_MS}ms ${EASE}`,
              }}
            >
              <p>Could not load modules. Retry to restore your menu.</p>
              <button
                type="button"
                className="cursor-pointer text-[12px] font-medium text-sidebar-primary underline-offset-2 hover:underline"
                onClick={() => void refresh()}
                tabIndex={collapsed ? -1 : 0}
              >
                Retry
              </button>
            </div>
          ) : null}
          {sessionReady && !hasModules ? (
            <div
              className={cn(
                "mb-4 rounded-lg border border-sidebar-border/80 bg-white/5 px-3 py-2.5 text-[12px] leading-relaxed text-sidebar-foreground/70",
                collapsed && "pointer-events-none opacity-0",
              )}
              style={{
                transition: `opacity ${LABEL_MS}ms ${EASE}`,
              }}
            >
              No modules assigned. Contact your ERP administrator to get access.
            </div>
          ) : null}

          {collapsed ? (
            <ul className="flex flex-col items-center gap-2.5 py-1">
              {flatItems.map((item) => {
                const active = isActivePath(pathname, item.href);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      {...(item.inApp
                        ? {}
                        : { target: "_blank", rel: "noopener noreferrer" })}
                      title={item.title}
                      aria-label={item.title}
                      className={cn(
                        "flex size-10 cursor-pointer items-center justify-center rounded-full transition-colors duration-200",
                        active
                          ? "bg-sidebar-accent text-sidebar-primary shadow-sm ring-1 ring-sidebar-primary/30"
                          : "bg-white/[0.08] text-sidebar-foreground/80 hover:bg-white/[0.14] hover:text-sidebar-foreground",
                      )}
                    >
                      {Icon ? (
                        <Icon className="size-[18px]" strokeWidth={1.75} />
                      ) : (
                        <span className="size-[18px]" />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          ) : (
            filtered.map((group) => (
              <div key={group.title} className="mb-5">
                <p className="mb-2 px-2.5 text-[11px] font-semibold tracking-[0.12em] text-sidebar-foreground/55 uppercase">
                  {group.title}
                </p>
                <ul className="space-y-0.5">
                  {group.items.map((item) => {
                    const active = isActivePath(pathname, item.href);
                    const Icon = item.icon;
                    const href = item.href;
                    return (
                      <li key={item.href}>
                        <Link
                          href={href}
                          {...(item.inApp
                            ? {}
                            : { target: "_blank", rel: "noopener noreferrer" })}
                          title={item.title}
                          className={cn(
                            "group relative flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[14px]",
                            "transition-colors duration-200",
                            active
                              ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm"
                              : "text-sidebar-foreground/90 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
                          )}
                        >
                          {active ? (
                            <span className="absolute inset-y-1.5 left-0 w-0.5 rounded-full bg-sidebar-primary" />
                          ) : null}
                          {Icon ? (
                            <Icon
                              className={cn(
                                "size-5 shrink-0",
                                active
                                  ? "text-sidebar-primary"
                                  : "text-sidebar-foreground/75 group-hover:text-sidebar-foreground",
                              )}
                              strokeWidth={1.75}
                            />
                          ) : (
                            <span className="size-5 shrink-0" />
                          )}
                          <span className="min-w-0 flex-1 truncate font-medium tracking-tight">
                            {item.title}
                          </span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))
          )}
        </nav>

        <div
          className={cn(
            "mt-auto border-t border-sidebar-border p-2.5",
            collapsed && "flex justify-center",
          )}
        >
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "cursor-pointer bg-transparent text-sidebar-foreground/70 shadow-none",
              "transition-colors duration-200",
              "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              "aria-expanded:bg-transparent aria-expanded:text-sidebar-foreground/70",
              "active:scale-100",
              collapsed
                ? "size-10 rounded-full bg-white/[0.08] p-0 hover:bg-white/[0.14] aria-expanded:bg-white/[0.08]"
                : "w-full justify-center",
            )}
            onClick={toggleCollapsed}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-expanded={!collapsed}
          >
            <ChevronLeft
              className="size-4 shrink-0 motion-reduce:!transition-none"
              style={{
                transform: collapsed ? "rotate(180deg)" : "rotate(0deg)",
                transition: `transform ${WIDTH_MS}ms ${EASE}`,
              }}
            />
            {!collapsed ? <span className="ml-1.5 text-xs">Collapse</span> : null}
          </Button>
        </div>
      </div>
    </SidebarRail>
  );
}
