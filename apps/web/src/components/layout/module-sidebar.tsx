"use client";

import Link from "next/link";
import { useMemo, useState, type ComponentType, type ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { ChevronDown, ChevronLeft } from "lucide-react";

import { SidebarAccountSection } from "@/components/layout/sidebar-account-section";
import {
  SIDEBAR_EASE,
  SIDEBAR_WIDTH_MS,
  SidebarRail,
  useSidebarCollapse,
} from "@/components/layout/sidebar-rail";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ModuleNavIcon = ComponentType<{ className?: string; "aria-hidden"?: boolean }>;

export type ModuleNavItem = {
  title: string;
  href: string;
  icon?: ModuleNavIcon;
  /** Unread / pending count shown as a pill. */
  badge?: number;
  /** Nested links rendered as an expandable group under this item. */
  children?: readonly ModuleNavItem[];
  /** Extra text matched by topbar module search. */
  keywords?: string;
};

export type ModuleNavGroup = {
  label?: string;
  items: readonly ModuleNavItem[];
};

type WarmHandlers = {
  onPointerDown?: () => void;
  onMouseEnter?: () => void;
  onFocus?: () => void;
};

export type ModuleSidebarProps = {
  /** Used for landmark labels and test ids. */
  moduleKey: string;
  title: string;
  subtitle?: ReactNode;
  icon: LucideIcon;
  groups: readonly ModuleNavGroup[];
  isActive: (item: ModuleNavItem) => boolean;
  /** Renders skeleton rows instead of `groups` (e.g. while permissions load). */
  loading?: boolean;
  /** Signed-in account menu at the top of the rail. */
  showAccount?: boolean;
  onItemNavigate?: (item: ModuleNavItem) => void;
  /** Prefetch hook fired on hover, focus, and pointer down. */
  onItemWarm?: (item: ModuleNavItem) => void;
  "aria-label"?: string;
  testId?: string;
};

function initials(title: string): string {
  return title
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase() ?? "")
    .join("");
}

function NavBadge({ count, collapsed }: { count: number; collapsed?: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex min-w-5 items-center justify-center rounded-full bg-amber-400 px-1.5 py-0.5 text-[10px] leading-none font-bold text-slate-950 tabular-nums",
        collapsed && "absolute -top-0.5 -right-0.5 min-w-4 px-1",
      )}
      aria-hidden
    >
      {count > 99 ? "99+" : count}
    </span>
  );
}

function accessibleName(item: ModuleNavItem): string {
  return item.badge && item.badge > 0 ? `${item.title} (${item.badge})` : item.title;
}

/**
 * Left vertical module sidebar. Every module workspace renders this rail on the
 * left; the topbar never carries module navigation.
 */
export function ModuleSidebar({
  moduleKey,
  title,
  subtitle,
  icon: ModuleIcon,
  groups,
  isActive,
  loading = false,
  showAccount = true,
  onItemNavigate,
  onItemWarm,
  "aria-label": ariaLabel,
  testId,
}: ModuleSidebarProps) {
  const { collapsed, layoutCollapsed, toggle } = useSidebarCollapse();
  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({});
  const landmark = ariaLabel ?? `${title} workspace`;

  const flatItems = useMemo(() => groups.flatMap((group) => group.items), [groups]);

  const warmHandlers = (item: ModuleNavItem): WarmHandlers =>
    onItemWarm
      ? {
        onPointerDown: () => onItemWarm(item),
        onMouseEnter: () => onItemWarm(item),
        onFocus: () => onItemWarm(item),
      }
      : {};

  const brand = (
    <div className="flex items-center gap-2">
      <ModuleIcon className="size-3.5 shrink-0 text-sidebar-primary" aria-hidden />
      <div className="min-w-0">
        <p className="truncate text-xs font-semibold text-sidebar-foreground">{title}</p>
        {subtitle ? (
          <p className="truncate text-[10px] text-sidebar-foreground/60">{subtitle}</p>
        ) : null}
      </div>
    </div>
  );

  return (
    <SidebarRail
      collapsed={collapsed}
      layoutCollapsed={layoutCollapsed}
      aria-label={landmark}
      data-testid={testId}
      data-module-sidebar={moduleKey}
    >
      {showAccount ? (
        <SidebarAccountSection collapsed={collapsed}>{brand}</SidebarAccountSection>
      ) : (
        <div className={cn("flex items-center gap-3 px-4 py-5", collapsed && "justify-center px-0")}>
          <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-sidebar-primary text-sidebar-primary-foreground shadow-sm">
            <ModuleIcon className="size-4" aria-hidden />
          </div>
          {!collapsed ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-medium tracking-tight text-sidebar-foreground">
                {title}
              </p>
              {subtitle ? (
                <p className="truncate text-[11px] text-sidebar-foreground/60">{subtitle}</p>
              ) : null}
            </div>
          ) : null}
        </div>
      )}

      <nav
        aria-label={landmark}
        data-sidebar-scroll
        data-testid={testId ? `${testId}-nav` : undefined}
        className={cn(
          "erp-scroll min-h-0 flex-1 overflow-x-hidden overflow-y-auto overscroll-none py-2",
          collapsed ? "px-0" : "px-2.5",
        )}
      >
        {loading ? (
          <ul className={cn("space-y-1", collapsed && "flex flex-col items-center gap-2.5 space-y-0")}>
            {Array.from({ length: 5 }).map((_, i) => (
              <li
                key={i}
                className={cn(
                  "animate-pulse bg-sidebar-accent/40 motion-reduce:animate-none",
                  collapsed ? "size-10 rounded-full" : "h-9 rounded-lg",
                )}
              />
            ))}
          </ul>
        ) : collapsed ? (
          <ul className="flex flex-col items-center gap-2.5 py-1">
            {flatItems.map((item) => {
              const active =
                isActive(item) || (item.children ?? []).some((child) => isActive(child));
              const Icon = item.icon;
              return (
                <li key={`${item.href}-${item.title}`}>
                  <Link
                    href={item.href}
                    title={item.title}
                    aria-label={accessibleName(item)}
                    aria-current={active ? "page" : undefined}
                    onClick={onItemNavigate ? () => onItemNavigate(item) : undefined}
                    {...warmHandlers(item)}
                    className={cn(
                      "relative flex size-10 cursor-pointer items-center justify-center rounded-full transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring motion-reduce:transition-none",
                      active
                        ? "bg-sidebar-accent text-sidebar-primary shadow-sm ring-1 ring-sidebar-primary/30"
                        : "bg-white/[0.08] text-sidebar-foreground/80 hover:bg-white/[0.14] hover:text-sidebar-foreground",
                    )}
                  >
                    {Icon ? (
                      <Icon className="size-[18px]" aria-hidden />
                    ) : (
                      <span className="text-[11px] font-semibold tracking-wide" aria-hidden>
                        {initials(item.title)}
                      </span>
                    )}
                    {item.badge && item.badge > 0 ? <NavBadge count={item.badge} collapsed /> : null}
                  </Link>
                </li>
              );
            })}
          </ul>
        ) : (
          groups.map((group, gi) => (
            <div key={group.label ?? gi} className="mb-4 last:mb-0">
              {group.label ? (
                <p className="mb-1.5 px-2.5 text-[10px] font-semibold tracking-[0.14em] text-sidebar-foreground/55 uppercase">
                  {group.label}
                </p>
              ) : null}
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const kids = item.children ?? [];
                  const childActive = kids.some((child) => isActive(child));
                  const selfActive = isActive(item) && !childActive;
                  const override = openMenus[item.href];
                  const expanded =
                    kids.length > 0 &&
                    (override ?? (childActive || isActive(item)));
                  return (
                    <li key={`${item.href}-${item.title}`}>
                      <div className="relative flex items-center">
                        <ModuleNavLink
                          item={item}
                          active={selfActive || (childActive && !expanded)}
                          onNavigate={onItemNavigate}
                          warm={warmHandlers(item)}
                        />
                        {kids.length > 0 ? (
                          <button
                            type="button"
                            aria-label={expanded ? `Collapse ${item.title}` : `Expand ${item.title}`}
                            aria-expanded={expanded}
                            className="absolute right-1 flex size-7 cursor-pointer items-center justify-center rounded-md text-sidebar-foreground/60 transition-colors duration-150 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring"
                            onClick={() =>
                              setOpenMenus((prev) => ({ ...prev, [item.href]: !expanded }))
                            }
                          >
                            <ChevronDown
                              className={cn(
                                "size-3.5 transition-transform duration-200 motion-reduce:transition-none",
                                expanded && "rotate-180",
                              )}
                              aria-hidden
                            />
                          </button>
                        ) : null}
                      </div>
                      {expanded ? (
                        <ul className="mt-0.5 ml-4 space-y-0.5 border-l border-sidebar-border/70 pl-2">
                          {kids.map((child) => (
                            <li key={`${child.href}-${child.title}`}>
                              <ModuleNavLink
                                item={child}
                                active={isActive(child)}
                                nested
                                onNavigate={onItemNavigate}
                                warm={warmHandlers(child)}
                              />
                            </li>
                          ))}
                        </ul>
                      ) : null}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))
        )}
      </nav>

      <div className={cn("border-t border-sidebar-border p-2.5", collapsed && "flex justify-center")}>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className={cn(
            "cursor-pointer bg-transparent text-sidebar-foreground/70 shadow-none transition-colors duration-200 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground active:scale-100",
            collapsed
              ? "size-10 rounded-full bg-white/[0.08] p-0 hover:bg-white/[0.14]"
              : "w-full justify-center",
          )}
          onClick={toggle}
          aria-label={collapsed ? `Expand ${title} sidebar` : `Collapse ${title} sidebar`}
          aria-expanded={!collapsed}
          data-testid={testId ? `${testId}-collapse` : undefined}
        >
          <ChevronLeft
            className="size-4 shrink-0 motion-reduce:!transition-none"
            style={{
              transform: collapsed ? "rotate(180deg)" : "rotate(0deg)",
              transition: `transform ${SIDEBAR_WIDTH_MS}ms ${SIDEBAR_EASE}`,
            }}
            aria-hidden
          />
          {!collapsed ? <span className="ml-1.5 text-xs">Collapse</span> : null}
        </Button>
      </div>
    </SidebarRail>
  );
}

function ModuleNavLink({
  item,
  active,
  nested = false,
  onNavigate,
  warm,
}: {
  item: ModuleNavItem;
  active: boolean;
  nested?: boolean;
  onNavigate?: (item: ModuleNavItem) => void;
  warm: WarmHandlers;
}) {
  const Icon = item.icon;
  const hasKids = (item.children?.length ?? 0) > 0;
  return (
    <Link
      href={item.href}
      title={item.title}
      aria-label={accessibleName(item)}
      aria-current={active ? "page" : undefined}
      onClick={onNavigate ? () => onNavigate(item) : undefined}
      {...warm}
      className={cn(
        "group relative flex min-w-0 flex-1 cursor-pointer items-center gap-2.5 rounded-lg font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring motion-reduce:transition-none",
        nested ? "px-2.5 py-1.5 text-[12px]" : "px-2.5 py-2 text-[13px]",
        hasKids && "pr-9",
        active
          ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm"
          : "text-sidebar-foreground/75 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
      )}
    >
      {active && !nested ? (
        <span className="absolute inset-y-1.5 left-0 w-0.5 rounded-full bg-sidebar-primary" aria-hidden />
      ) : null}
      {Icon ? (
        <Icon
          className={cn(
            "shrink-0",
            nested ? "size-3.5" : "size-4",
            active
              ? "text-sidebar-primary"
              : "text-sidebar-foreground/55 group-hover:text-sidebar-foreground/85",
          )}
          aria-hidden
        />
      ) : null}
      <span className="min-w-0 flex-1 truncate">{item.title}</span>
      {item.badge && item.badge > 0 ? <NavBadge count={item.badge} /> : null}
    </Link>
  );
}
