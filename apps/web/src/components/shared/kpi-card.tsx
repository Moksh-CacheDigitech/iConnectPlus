import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { cn } from "@/lib/utils";

export type KpiTone = "default" | "success" | "warning" | "danger";

const KPI_TONE: Record<KpiTone, { icon: string; bar: string }> = {
  default: { icon: "bg-primary/10 text-primary", bar: "bg-primary" },
  success: { icon: "bg-emerald-50 text-emerald-700", bar: "bg-emerald-500" },
  warning: { icon: "bg-amber-50 text-amber-700", bar: "bg-amber-500" },
  danger: { icon: "bg-red-50 text-red-700", bar: "bg-red-500" },
};

/** Up to four compact KPI tiles; collapses to 2 / 1 columns on narrow screens. */
export function KpiStrip({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-4", className)}>
      {children}
    </div>
  );
}

export function KpiCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = "default",
  href,
  loading,
}: {
  label: string;
  value: string;
  hint?: string;
  icon: LucideIcon;
  tone?: KpiTone;
  href?: string;
  loading?: boolean;
}) {
  const styles = KPI_TONE[tone];
  const body = (
    <div
      className={cn(
        "group relative h-full overflow-hidden rounded-xl border border-border/70 bg-card p-3 shadow-sm",
        href &&
          "transition-[box-shadow,border-color] duration-200 hover:border-border hover:shadow-md motion-reduce:transition-none",
      )}
    >
      <span className={cn("absolute inset-y-0 left-0 w-1", styles.bar)} aria-hidden />
      <div className="flex items-start justify-between gap-2 pl-1.5">
        <p className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
          {label}
        </p>
        <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-lg", styles.icon)}>
          <Icon className="size-4" aria-hidden />
        </span>
      </div>
      {loading ? (
        <div className="mt-2 ml-1.5 h-7 w-24 animate-pulse rounded bg-muted motion-reduce:animate-none" />
      ) : (
        <p className="mt-1.5 pl-1.5 text-2xl font-semibold tracking-tight text-foreground tabular-nums">
          {value}
        </p>
      )}
      {hint ? (
        <p className="mt-1 flex items-center gap-1 pl-1.5 text-[11px] text-muted-foreground">
          {hint}
        </p>
      ) : null}
      {href ? (
        <ArrowUpRight
          className="absolute right-3 bottom-3 size-4 text-muted-foreground/0 transition-colors duration-200 group-hover:text-muted-foreground"
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
