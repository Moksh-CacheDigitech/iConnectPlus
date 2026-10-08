import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/** Column header row for hand-built tables - high contrast, readable at a glance. */
export const TABLE_HEAD_ROW = cn(
  "border-b border-border/80 bg-muted/60 text-xs font-semibold tracking-wide text-foreground uppercase",
);

/** Plain `<th>` cells (non-sortable columns). Matches `SortableTh` padding. */
export const TABLE_HEAD_CELL = cn("px-4 py-2.5 text-xs font-semibold text-foreground");

/** Section / panel titles (forms, lists, detail cards). */
export const SECTION_TITLE = cn(
  "text-[15px] font-semibold tracking-tight text-foreground break-words",
);

/** Page vertical rhythm shared by every module. */
export function WorkspacePage({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={cn("space-y-4", className)}>{children}</div>;
}

export function InfoBanner({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-sky-200/80 bg-sky-50 px-4 py-2.5 text-xs text-sky-950">
      {children}
    </div>
  );
}

export function WarnBanner({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-amber-300/80 bg-amber-50 px-4 py-3 text-sm text-amber-950">
      {children}
    </div>
  );
}

/** Icon chip used in section / list headers. */
export function IconBadge({
  icon: Icon,
  className,
}: {
  icon: LucideIcon;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-foreground",
        className,
      )}
    >
      <Icon className="size-4" aria-hidden />
    </span>
  );
}

/** Section card with icon header. */
export function WorkspaceSection({
  title,
  subtitle,
  icon,
  badge,
  actions,
  children,
  className,
  bodyClassName,
  id,
}: {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  badge?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
  id?: string;
}) {
  return (
    <section
      id={id}
      className={cn("rounded-xl border border-border/70 bg-card p-3 shadow-sm sm:p-4", className)}
    >
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-start gap-2.5">
          {icon ? <IconBadge icon={icon} /> : null}
          <div className="min-w-0">
            <h2 className={SECTION_TITLE}>{title}</h2>
            {subtitle ? <p className="text-xs text-muted-foreground">{subtitle}</p> : null}
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {badge}
          {actions}
        </div>
      </div>
      <div className={cn("min-w-0", bodyClassName)}>{children}</div>
    </section>
  );
}

/** Card shell for list tables - border + shadow only; toolbar is separate. */
export function ListPanel({
  children,
  className,
  id,
}: {
  children: ReactNode;
  className?: string;
  id?: string;
}) {
  return (
    <div
      id={id}
      className={cn("overflow-hidden rounded-xl border border-border/70 bg-card shadow-sm", className)}
    >
      {children}
    </div>
  );
}

/** Primary-colored headline strip for key metrics (dashboard / detail pages). */
export function HeadlineBand({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        "overflow-hidden rounded-xl border border-primary/20 bg-primary text-primary-foreground shadow-sm",
        className,
      )}
    >
      {children}
    </section>
  );
}

export function HeadlineStat({
  label,
  value,
  sub,
  loading,
  className,
}: {
  label: string;
  value: string;
  sub?: string;
  loading?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("min-w-0 px-5 py-4", className)}>
      <p className="text-[11px] font-medium tracking-wide text-white/70 uppercase">{label}</p>
      {loading ? (
        <div className="mt-2 h-8 w-32 animate-pulse rounded bg-white/15 motion-reduce:animate-none" />
      ) : (
        <p className="mt-1.5 truncate text-2xl font-semibold tracking-tight text-white tabular-nums sm:text-3xl">
          {value}
        </p>
      )}
      {sub ? <p className="mt-1 text-xs text-white/70">{sub}</p> : null}
    </div>
  );
}

export function ActivityTile({
  label,
  value,
  icon: Icon,
  tint,
  href,
}: {
  label: string;
  value: string;
  icon: LucideIcon;
  tint: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="group flex cursor-pointer items-center gap-3 rounded-xl border border-border/80 bg-card px-3 py-2.5 shadow-sm transition-[box-shadow,border-color] duration-200 hover:border-border hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
    >
      <span className={cn("flex size-9 items-center justify-center rounded-lg", tint)}>
        <Icon className="size-4" aria-hidden />
      </span>
      <div className="min-w-0">
        <p className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
          {label}
        </p>
        <p className="text-lg font-semibold tabular-nums text-foreground">{value}</p>
      </div>
      <ArrowUpRight
        className="ml-auto size-4 text-muted-foreground/50 transition-colors duration-200 group-hover:text-primary"
        aria-hidden
      />
    </Link>
  );
}

export function DetailGrid({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <dl className={cn("grid grid-cols-2 gap-3 text-xs lg:grid-cols-3", className)}>{children}</dl>
  );
}

export function DetailItem({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="min-w-0">
      <dt className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
        {label}
      </dt>
      <dd className="mt-1 break-words text-sm text-foreground">{children}</dd>
    </div>
  );
}

export function MetricStrip({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        "grid gap-3 rounded-xl border border-border/80 bg-card p-3 shadow-sm sm:grid-cols-2 lg:grid-cols-4",
        className,
      )}
    >
      {children}
    </section>
  );
}

export function Metric({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
}) {
  return (
    <div className="min-w-0">
      <p className="text-[11px] font-medium tracking-wide text-muted-foreground uppercase">{label}</p>
      <p className="mt-1 text-lg font-semibold tracking-tight text-foreground tabular-nums">{value}</p>
      {hint ? <p className="mt-0.5 text-[11px] text-muted-foreground">{hint}</p> : null}
    </div>
  );
}

export function ViewAllLink({ href, label = "View all" }: { href: string; label?: string }) {
  return (
    <Link
      href={href}
      className="inline-flex cursor-pointer items-center gap-1 rounded-sm text-xs font-medium text-primary transition-opacity duration-200 hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
    >
      {label} <ArrowUpRight className="size-3.5" aria-hidden />
    </Link>
  );
}

export function CountBadge({ count, label = "shown" }: { count: number; label?: string }) {
  return (
    <Badge variant="secondary" className="shrink-0 tabular-nums">
      {count} {label}
    </Badge>
  );
}
