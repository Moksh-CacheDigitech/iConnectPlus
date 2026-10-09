"use client";

import {
  Archive,
  Boxes,
  MapPin,
  Package,
  Tags,
  UserCheck,
  Wrench,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { NonItDashboardSummary } from "@/services/nonit-asset-service";
import { cn } from "@/lib/utils";

function pct(count: number, total: number): number {
  if (total <= 0) return 0;
  return Math.round((count / total) * 100);
}

type StatusTone = {
  iconWrap: string;
  bar: string;
  ring: string;
};

const TONES: Record<string, StatusTone> = {
  total: {
    iconWrap: "bg-[rgba(3,105,161,0.1)] text-[#0369A1]",
    bar: "bg-[#0369A1]",
    ring: "hover:border-[#0369A1]/50",
  },
  stock: {
    iconWrap: "bg-sky-50 text-sky-700",
    bar: "bg-sky-600",
    ring: "hover:border-sky-400/60",
  },
  assigned: {
    iconWrap: "bg-emerald-50 text-emerald-700",
    bar: "bg-emerald-600",
    ring: "hover:border-emerald-400/60",
  },
  maintenance: {
    iconWrap: "bg-amber-50 text-amber-800",
    bar: "bg-amber-500",
    ring: "hover:border-amber-400/60",
  },
  disposed: {
    iconWrap: "bg-slate-100 text-slate-600",
    bar: "bg-slate-500",
    ring: "hover:border-slate-400/60",
  },
};

function KpiCard({
  title,
  value,
  share,
  icon: Icon,
  tone: _tone,
  loading,
  onClick,
}: {
  title: string;
  value: string;
  share?: number;
  icon: typeof Package;
  tone: StatusTone;
  loading?: boolean;
  onClick?: () => void;
}) {
  void _tone;
  const body = (
    <>
      <span
        className="pointer-events-none absolute -top-10 -right-8 size-28 rounded-full bg-white/10 blur-2xl"
        aria-hidden
      />
      <div className="relative flex items-start justify-between gap-2">
        <p className="text-[11px] font-semibold tracking-wide text-white/75 uppercase">{title}</p>
        <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-white/15 text-white">
          <Icon className="size-3.5" aria-hidden />
        </div>
      </div>
      <div className="relative">
        {loading ? (
          <div className="h-8 w-16 animate-pulse rounded bg-white/20 motion-reduce:animate-none" />
        ) : (
          <p className="text-2xl font-semibold tracking-tight text-white tabular-nums">{value}</p>
        )}
        {share != null && !loading ? (
          <div className="mt-2 space-y-1.5">
            <div className="h-1.5 overflow-hidden rounded-full bg-white/20">
              <div
                className="h-full rounded-full bg-white/80 transition-all duration-300"
                style={{ width: `${Math.min(100, Math.max(0, share))}%` }}
              />
            </div>
            <p className="text-[11px] text-white/65">{share}% of total</p>
          </div>
        ) : !loading ? (
          <p className="mt-2 text-[11px] text-white/65">All Non-IT assets</p>
        ) : null}
      </div>
    </>
  );

  const shell =
    "relative flex flex-col gap-3 overflow-hidden rounded-xl border border-white/10 p-4 text-white shadow-sm bg-[linear-gradient(135deg,var(--kpi-hero-from)_0%,var(--kpi-hero-via)_45%,var(--kpi-hero-to)_100%)]";

  if (onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        className={cn(
          shell,
          "cursor-pointer text-left transition-[filter,box-shadow] duration-200 hover:brightness-[1.06] hover:shadow-md",
        )}
      >
        {body}
      </button>
    );
  }

  return <div className={shell}>{body}</div>;
}

function RankList({
  loading,
  emptyLabel,
  items,
  maxCount,
  barClass,
}: {
  loading: boolean;
  emptyLabel: string;
  items: { id: string; label: string; meta?: string; count: number }[];
  maxCount: number;
  barClass: string;
}) {
  if (loading) {
    return (
      <div className="space-y-3 py-1">
        {[0, 1, 2].map((i) => (
          <div key={i} className="space-y-1.5">
            <div className="h-3 w-2/3 animate-pulse rounded bg-muted/50" />
            <div className="h-1.5 animate-pulse rounded-full bg-muted/40" />
          </div>
        ))}
      </div>
    );
  }
  if (items.length === 0) {
    return <p className="py-6 text-center text-sm text-muted-foreground">{emptyLabel}</p>;
  }
  return (
    <ul className="space-y-3">
      {items.map((row) => {
        const width = maxCount > 0 ? Math.round((row.count / maxCount) * 100) : 0;
        return (
          <li key={row.id} className="space-y-1.5">
            <div className="flex items-center justify-between gap-3 text-sm">
              <div className="min-w-0">
                <p className="truncate font-medium text-foreground">{row.label}</p>
                {row.meta ? (
                  <p className="font-mono text-[11px] text-muted-foreground">{row.meta}</p>
                ) : null}
              </div>
              <span className="shrink-0 tabular-nums text-sm font-semibold text-foreground">
                {row.count}
              </span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-muted/50">
              <div
                className={cn("h-full rounded-full transition-all duration-300", barClass)}
                style={{ width: `${Math.min(100, Math.max(width, row.count > 0 ? 6 : 0))}%` }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export type NonItDashboardSummaryProps = {
  summary: NonItDashboardSummary | null;
  loading?: boolean;
  onStatusClick?: (status: string) => void;
  className?: string;
};

export function NonItDashboardSummarySection({
  summary,
  loading = false,
  onStatusClick,
  className,
}: NonItDashboardSummaryProps) {
  const total = summary?.total_assets ?? 0;
  const inStock = summary?.in_stock ?? 0;
  const assigned = summary?.assigned ?? 0;
  const maintenance = summary?.in_maintenance ?? 0;
  const disposed = summary?.disposed ?? 0;
  const byType = summary?.by_type ?? [];
  const byLocation = summary?.by_location ?? [];

  const typeMax = Math.max(0, ...byType.map((r) => r.count));
  const locMax = Math.max(0, ...byLocation.map((r) => r.count));

  return (
    <div className={cn("space-y-5", className)} data-testid="nonit-dashboard-summary">
      <section aria-labelledby="nonit-kpi-heading" className="space-y-2.5">
        <div className="flex items-end justify-between gap-2">
          <div>
            <h2
              id="nonit-kpi-heading"
              className="text-xs font-semibold uppercase tracking-wide text-muted-foreground"
            >
              Counts by status
            </h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Click a card to open filtered inventory
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 xl:grid-cols-5">
          <KpiCard
            title="Total assets"
            icon={Boxes}
            tone={TONES.total!}
            loading={loading}
            value={summary ? String(total) : "—"}
            onClick={onStatusClick ? () => onStatusClick("") : undefined}
          />
          <KpiCard
            title="In stock"
            icon={Package}
            tone={TONES.stock!}
            loading={loading}
            value={summary ? String(inStock) : "—"}
            share={pct(inStock, total)}
            onClick={onStatusClick ? () => onStatusClick("IN_STOCK") : undefined}
          />
          <KpiCard
            title="Assigned"
            icon={UserCheck}
            tone={TONES.assigned!}
            loading={loading}
            value={summary ? String(assigned) : "—"}
            share={pct(assigned, total)}
            onClick={onStatusClick ? () => onStatusClick("ASSIGNED") : undefined}
          />
          <KpiCard
            title="In maintenance"
            icon={Wrench}
            tone={TONES.maintenance!}
            loading={loading}
            value={summary ? String(maintenance) : "—"}
            share={pct(maintenance, total)}
            onClick={onStatusClick ? () => onStatusClick("MAINTENANCE") : undefined}
          />
          <KpiCard
            title="Disposed"
            icon={Archive}
            tone={TONES.disposed!}
            loading={loading}
            value={summary ? String(disposed) : "—"}
            share={pct(disposed, total)}
            onClick={onStatusClick ? () => onStatusClick("DISPOSED") : undefined}
          />
        </div>
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card
          className="overflow-hidden border-border/70 bg-background/95 shadow-md"
          data-testid="nonit-by-type"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 border-b border-border/50 pb-3 pt-4">
            <CardTitle className="flex items-center gap-2 text-sm font-semibold tracking-tight">
              <span className="flex size-7 items-center justify-center rounded-lg bg-[rgba(3,105,161,0.1)] text-[#0369A1]">
                <Tags className="size-3.5" aria-hidden />
              </span>
              By type
            </CardTitle>
            <span className="rounded-md border border-border/70 bg-muted/30 px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
              {loading ? "…" : `${byType.length} active`}
            </span>
          </CardHeader>
          <CardContent className="p-4">
            <RankList
              loading={loading}
              emptyLabel="No active asset types yet"
              maxCount={typeMax}
              barClass="bg-[#0369A1]"
              items={byType.map((row) => ({
                id: row.asset_type_id,
                label: row.name,
                meta: row.prefix,
                count: row.count,
              }))}
            />
          </CardContent>
        </Card>

        <Card
          className="overflow-hidden border-border/70 bg-background/95 shadow-md"
          data-testid="nonit-by-location"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 border-b border-border/50 pb-3 pt-4">
            <CardTitle className="flex items-center gap-2 text-sm font-semibold tracking-tight">
              <span className="flex size-7 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                <MapPin className="size-3.5" aria-hidden />
              </span>
              Top locations
            </CardTitle>
            <span className="rounded-md border border-border/70 bg-muted/30 px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
              Assigned assets
            </span>
          </CardHeader>
          <CardContent className="p-4">
            <RankList
              loading={loading}
              emptyLabel="No location assignments yet"
              maxCount={locMax}
              barClass="bg-emerald-600"
              items={byLocation.map((row) => ({
                id: row.location_id,
                label: row.name,
                count: row.count,
              }))}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
