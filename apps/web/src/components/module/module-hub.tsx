"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowUpRight, Database, RefreshCw, Users } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { buildResourceColumns } from "@/components/module/resource-columns";
import { DataTable } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { KpiCard, KpiStrip } from "@/components/shared/kpi-card";
import { ViewAllLink, WorkspacePage, WorkspaceSection } from "@/components/shared/workspace-ui";
import { buttonVariants } from "@/components/ui/button";
import type { ErpModule, ModuleResource } from "@/config/modules";
import { moduleIconMap } from "@/config/navigation";
import { useAuthUser } from "@/hooks/use-auth-user";
import { canManageModuleUsers, moduleUsersHref } from "@/lib/module-access";
import { enrichRows, listTotal, normalizeRows } from "@/lib/resource-display";
import { cn } from "@/lib/utils";
import { ApiClientError, resourceService } from "@/services/api-client";

interface ModuleHubProps {
  module: ErpModule;
}

const KPI_COUNT = 4;
const RECENT_ROWS = 5;

type HubData = {
  counts: Record<string, number | null>;
  recent: Record<string, unknown>[];
};

function resourceHref(module: ErpModule, resource: ModuleResource): string {
  return `/${module.key}/${resource.key}`;
}

/**
 * Landing page for config-only modules: KPI strip, recent records from the
 * primary resource, and links into every resource (template A in MODULE_UI_PLAN).
 */
export function ModuleHub({ module }: ModuleHubProps) {
  const { user, adminModuleKeys } = useAuthUser();
  const showUsers = canManageModuleUsers(module.key, adminModuleKeys, user?.userType);
  const Icon = moduleIconMap[module.icon];

  const listable = useMemo(
    () => module.resources.filter((r) => r.listable !== false),
    [module.resources],
  );
  const kpiResources = listable.slice(0, KPI_COUNT);
  const primary = listable[0];

  const [data, setData] = useState<HubData>({ counts: {}, recent: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const targets = listable.slice(0, KPI_COUNT);
    const results = await Promise.allSettled(
      targets.map((r) => resourceService.list(r.apiPath, { page: 1, page_size: RECENT_ROWS })),
    );
    const counts: Record<string, number | null> = {};
    let recent: Record<string, unknown>[] = [];
    let firstError: string | null = null;
    results.forEach((result, i) => {
      const resource = targets[i];
      if (result.status === "fulfilled") {
        counts[resource.key] = listTotal(result.value.data);
        if (i === 0) recent = normalizeRows(result.value.data).slice(0, RECENT_ROWS);
      } else {
        counts[resource.key] = null;
        if (!firstError) {
          firstError =
            result.reason instanceof ApiClientError
              ? result.reason.message
              : "Some records could not be loaded.";
        }
      }
    });
    setData({ counts, recent: enrichRows(recent) });
    setError(results.every((r) => r.status === "rejected") ? firstError : null);
    setLoading(false);
  }, [listable]);

  useEffect(() => {
    void load();
  }, [load]);

  const recentColumns = useMemo(() => buildResourceColumns(data.recent, 4), [data.recent]);

  return (
    <WorkspacePage>
      <PageHeader
        title={module.title}
        description={module.description}
        actions={
          <>
            <button
              type="button"
              onClick={() => void load()}
              disabled={loading}
              className={cn(buttonVariants({ variant: "outline", size: "sm" }), "cursor-pointer gap-1.5 shadow-none")}
            >
              <RefreshCw
                className={cn("size-3.5", loading && "animate-spin motion-reduce:animate-none")}
                aria-hidden
              />
              Refresh
            </button>
            {showUsers ? (
              <Link
                href={moduleUsersHref(module.key)}
                className={cn(buttonVariants({ variant: "outline", size: "sm" }), "cursor-pointer gap-1.5")}
              >
                <Users className="size-3.5" aria-hidden />
                Module users
              </Link>
            ) : null}
            {primary ? (
              <Link
                href={resourceHref(module, primary)}
                className={cn(buttonVariants({ size: "sm" }), "cursor-pointer gap-1.5")}
              >
                Open {primary.title}
                <ArrowUpRight className="size-3.5" aria-hidden />
              </Link>
            ) : null}
          </>
        }
      />

      {kpiResources.length > 0 ? (
        <KpiStrip variant="hero">
          {kpiResources.map((resource) => {
            const count = data.counts[resource.key];
            return (
              <KpiCard
                key={resource.key}
                label={resource.title}
                value={count == null ? "-" : count.toLocaleString("en-IN")}
                hint={resource.description}
                icon={Icon ?? Database}
                href={resourceHref(module, resource)}
                loading={loading}
              />
            );
          })}
        </KpiStrip>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="min-w-0 xl:col-span-2">
          {primary ? (
            <DataTable
              title={`Recent ${primary.title.toLowerCase()}`}
              rows={data.recent}
              columns={recentColumns}
              getRowId={(row, i) => String(row.id ?? i)}
              pageSize={0}
              loading={loading}
              error={error}
              onRetry={() => void load()}
              actions={<ViewAllLink href={resourceHref(module, primary)} />}
              empty={
                <EmptyState
                  compact
                  preset="no-records"
                  title={`No ${primary.title.toLowerCase()} yet`}
                  description={primary.description}
                />
              }
              minWidth={480}
            />
          ) : (
            <EmptyState bordered preset="no-records" title="No listable resources" description={null} />
          )}
        </div>

        <WorkspaceSection title="Workspace" subtitle={`${module.resources.length} areas`} icon={Icon}>
          <ul className="-mx-1 space-y-0.5">
            {module.resources.map((resource) => (
              <li key={resource.key}>
                <Link
                  href={resourceHref(module, resource)}
                  className="group flex cursor-pointer items-center gap-2 rounded-lg px-2 py-1.5 transition-colors duration-150 hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
                >
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[13px] font-medium text-foreground">
                      {resource.title}
                    </span>
                    <span className="block truncate text-[11px] text-muted-foreground">
                      {resource.description}
                    </span>
                  </span>
                  <ArrowUpRight
                    className="size-3.5 shrink-0 text-muted-foreground/50 transition-colors duration-150 group-hover:text-primary"
                    aria-hidden
                  />
                </Link>
              </li>
            ))}
          </ul>
        </WorkspaceSection>
      </div>
    </WorkspacePage>
  );
}
