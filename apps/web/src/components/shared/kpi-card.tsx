"use client";

import type { LucideIcon } from "lucide-react";
import {
  createContext,
  useContext,
  type ReactNode,
} from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { cn } from "@/lib/utils";

export type KpiTone = "default" | "success" | "warning" | "danger";
export type KpiVariant = "panel" | "hero";

const KPI_TONE: Record<KpiTone, { icon: string; bar: string }> = {
  default: { icon: "bg-primary/10 text-primary", bar: "bg-primary" },
  success: { icon: "bg-emerald-50 text-emerald-700", bar: "bg-emerald-500" },
  warning: { icon: "bg-amber-50 text-amber-700", bar: "bg-amber-500" },
  danger: { icon: "bg-red-50 text-red-700", bar: "bg-red-500" },
};

/** Soft status accents on the CRM-rail hero surface (not Email-Intelligence blue). */
const HERO_TONE: Record<KpiTone, string> = {
  default: "",
  success: "ring-1 ring-inset ring-emerald-300/25",
  warning: "ring-1 ring-inset ring-amber-300/30",
  danger: "ring-1 ring-inset ring-red-300/30",
};

const KpiVariantContext = createContext<KpiVariant>("hero");

/** Up to four compact KPI tiles; collapses to 2 / 1 columns on narrow screens. */
export function KpiStrip({
  children,
  className,
  variant = "hero",
}: {
  children: ReactNode;
  className?: string;
  /**
   * Surface style. Defaults to `hero` (CRM-rail teal/slate gradient) across the ERP.
   * Pass `panel` only for dense report toolbars that need a light card.
   */
  variant?: KpiVariant;
}) {
  return (
    <KpiVariantContext.Provider value={variant}>
      <div className={cn("grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-4", className)}>
        {children}
      </div>
    </KpiVariantContext.Provider>
  );
}

export function KpiCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = "default",
  variant,
  href,
  loading,
}: {
  label: string;
  value: string;
  hint?: string;
  icon?: LucideIcon;
  tone?: KpiTone;
  /** Overrides `KpiStrip` context when set. */
  variant?: KpiVariant;
  href?: string;
  loading?: boolean;
}) {
  const stripVariant = useContext(KpiVariantContext);
  const surface = variant ?? stripVariant;
  const isHero = surface === "hero";
  const styles = KPI_TONE[tone];

  const body = (
    <div
      className={cn(
        "group relative h-full overflow-hidden rounded-xl p-3 shadow-sm",
        isHero
          ? cn(
            "border border-white/10 text-white",
            "bg-[linear-gradient(135deg,var(--kpi-hero-from)_0%,var(--kpi-hero-via)_45%,var(--kpi-hero-to)_100%)]",
            HERO_TONE[tone],
            href &&
            "transition-[box-shadow,filter] duration-200 hover:brightness-[1.06] hover:shadow-md motion-reduce:transition-none",
          )
          : cn(
            "border border-border/70 bg-card",
            href &&
            "transition-[box-shadow,border-color] duration-200 hover:border-border hover:shadow-md motion-reduce:transition-none",
          ),
      )}
    >
      {!isHero ? (
        <span className={cn("absolute inset-y-0 left-0 w-1", styles.bar)} aria-hidden />
      ) : (
        <span
          className="pointer-events-none absolute -top-10 -right-8 size-28 rounded-full bg-white/10 blur-2xl"
          aria-hidden
        />
      )}
      <div className={cn("flex items-start justify-between gap-2", !isHero && "pl-1.5")}>
        <p
          className={cn(
            "text-[11px] font-medium tracking-wide uppercase",
            isHero ? "text-white/75" : "text-muted-foreground",
          )}
        >
          {label}
        </p>
        {Icon ? (
          <span
            className={cn(
              "flex size-8 shrink-0 items-center justify-center rounded-lg",
              isHero ? "bg-white/15 text-white" : styles.icon,
            )}
          >
            <Icon className="size-4" aria-hidden />
          </span>
        ) : null}
      </div>
      {loading ? (
        <div
          className={cn(
            "mt-2 h-7 w-24 animate-pulse rounded motion-reduce:animate-none",
            isHero ? "bg-white/20" : "ml-1.5 bg-muted",
          )}
        />
      ) : (
        <p
          className={cn(
            "mt-1.5 text-2xl font-semibold tracking-tight tabular-nums",
            isHero ? "text-white" : "pl-1.5 text-foreground",
          )}
        >
          {value}
        </p>
      )}
      {hint ? (
        <p
          className={cn(
            "mt-1 flex items-center gap-1 text-[11px]",
            isHero ? "text-white/65" : "pl-1.5 text-muted-foreground",
          )}
        >
          {hint}
        </p>
      ) : null}
      {href ? (
        <ArrowUpRight
          className={cn(
            "absolute right-3 bottom-3 size-4 transition-colors duration-200",
            isHero
              ? "text-white/0 group-hover:text-white/80"
              : "text-muted-foreground/0 group-hover:text-muted-foreground",
          )}
          aria-hidden
        />
      ) : null}
    </div>
  );
  if (href) {
    return (
      <Link
        href={href}
        className="block h-full cursor-pointer rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      >
        {body}
      </Link>
    );
  }
  return body;
}
