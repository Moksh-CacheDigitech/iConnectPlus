"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
  type ComponentProps,
} from "react";

import { cn } from "@/lib/utils";

/** Figma motion: Expanded 260 ↔ Collapsed 72 (see design-system pages/app-shell.md). */
export const SIDEBAR_EXPANDED = 260;
export const SIDEBAR_COLLAPSED = 72;
export const SIDEBAR_WIDTH_MS = 320;
export const SIDEBAR_LABEL_MS = 160;
export const SIDEBAR_SEARCH_MS = 220;
export const SIDEBAR_EASE = "cubic-bezier(0.32, 0.72, 0, 1)";

const NARROW_VIEWPORT = "(max-width: 767px)";

function matchesMedia(query: string): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") return false;
  return window.matchMedia(query).matches;
}

export function prefersReducedMotion(): boolean {
  return matchesMedia("(prefers-reduced-motion: reduce)");
}

function subscribeNarrowViewport(onChange: () => void): () => void {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") return () => { };
  const query = window.matchMedia(NARROW_VIEWPORT);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}

/**
 * Collapse state shared by every left sidebar. The layout spacer (`layoutCollapsed`)
 * flips once at click so charts resize once; the rail animates on its own layer.
 * Follows the viewport (collapsed on phone widths) until the user toggles it.
 */
export function useSidebarCollapse() {
  const narrow = useSyncExternalStore(
    subscribeNarrowViewport,
    () => matchesMedia(NARROW_VIEWPORT),
    () => false,
  );
  const [userCollapsed, setUserCollapsed] = useState<boolean | null>(null);
  const [animating, setAnimating] = useState(false);
  const timer = useRef<number | null>(null);
  const collapsed = userCollapsed ?? narrow;

  useEffect(() => {
    document.documentElement.classList.toggle("erp-sidebar-animating", animating);
    return () => document.documentElement.classList.remove("erp-sidebar-animating");
  }, [animating]);

  useEffect(
    () => () => {
      if (timer.current !== null) window.clearTimeout(timer.current);
    },
    [],
  );

  const toggle = useCallback(() => {
    setUserCollapsed(!collapsed);
    if (prefersReducedMotion()) {
      setAnimating(false);
      return;
    }
    setAnimating(true);
    if (timer.current !== null) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setAnimating(false), SIDEBAR_WIDTH_MS + 40);
  }, [collapsed]);

  return { collapsed, layoutCollapsed: collapsed, toggle };
}

type SidebarRailProps = ComponentProps<"aside"> & {
  collapsed: boolean;
  layoutCollapsed: boolean;
};

/** Left rail: an in-flow spacer plus the fixed, width-animated `<aside>`. */
export function SidebarRail({
  collapsed,
  layoutCollapsed,
  className,
  children,
  ...rest
}: SidebarRailProps) {
  return (
    <>
      <div
        aria-hidden
        className={cn("h-dvh shrink-0", layoutCollapsed ? "w-[72px]" : "w-[260px]")}
      />
      <aside
        data-erp-primary-sidebar
        data-collapsed={collapsed ? "true" : "false"}
        className={cn(
          "fixed top-0 left-0 z-20 flex h-dvh flex-col overflow-hidden border-r border-sidebar-border bg-sidebar text-sidebar-foreground",
          "transform-gpu transition-[width] duration-[320ms] ease-[cubic-bezier(0.32,0.72,0,1)] will-change-[width] [backface-visibility:hidden] motion-reduce:transition-none",
          collapsed ? "w-[72px]" : "w-[260px]",
          className,
        )}
        {...rest}
      >
        {children}
      </aside>
    </>
  );
}
