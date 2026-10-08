"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { RefreshCw } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { buildResourceColumns } from "@/components/module/resource-columns";
import { DataTable } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { WorkspacePage } from "@/components/shared/workspace-ui";
import { Button } from "@/components/ui/button";
import { isAuthenticated } from "@/lib/auth";
import { enrichRows, normalizeRows } from "@/lib/resource-display";
import { cn } from "@/lib/utils";
import { ApiClientError, resourceService } from "@/services/api-client";

interface ResourceListViewProps {
  moduleKey: string;
  moduleTitle: string;
  title: string;
  description: string;
  apiPath: string;
  /** When true, prepend a # serial column (1…n for the filtered list). */
  showRowSerial?: boolean;
}

export function ResourceListView({
  moduleKey,
  moduleTitle,
  title,
  description,
  apiPath,
  showRowSerial = false,
}: ResourceListViewProps) {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<number | null>(null);
  const authenticated = typeof window !== "undefined" ? isAuthenticated() : false;

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setStatus(null);
    try {
      const response = await resourceService.list(apiPath);
      setRows(normalizeRows(response.data));
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : "Failed to load resource";
      const code = err instanceof ApiClientError ? err.status : null;
      setError(message);
      setStatus(code);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [apiPath]);

  useEffect(() => {
    void load();
  }, [load]);

  const enrichedRows = useMemo(() => enrichRows(rows), [rows]);

  const columns = useMemo(() => buildResourceColumns(enrichedRows), [enrichedRows]);

  const errorTitle =
    status === 401
      ? "Authentication required"
      : status === 403
        ? "Permission denied"
        : "Unable to load records";

  return (
    <WorkspacePage>
      <PageHeader
        title={title}
        description={description}
        backHref={`/${moduleKey}`}
        backLabel={moduleTitle}
        actions={
          <Button
            variant="outline"
            size="sm"
            className="cursor-pointer shadow-none"
            onClick={() => void load()}
            disabled={loading}
          >
            <RefreshCw
              className={cn("size-3.5", loading && "animate-spin motion-reduce:animate-none")}
              aria-hidden
            />
            Refresh
          </Button>
        }
      />

      <DataTable
        title="Records"
        rows={enrichedRows}
        columns={columns}
        getRowId={(row, idx) => String(row.id ?? idx)}
        searchPlaceholder={`Filter ${title.toLowerCase()}…`}
        rowSerial={showRowSerial}
        loading={loading}
        error={
          error ? (
            <div className="space-y-1">
              <p className="font-medium">{errorTitle}</p>
              <p className="text-foreground/80">{error}</p>
              {status === 403 && authenticated ? (
                <p className="text-foreground/80">
                  Your role is missing this permission. Sign out and sign back in with a Microsoft
                  account that has this module assigned, or ask an administrator to grant access.
                </p>
              ) : null}
              {status === 401 || !authenticated ? (
                <Link
                  href="/login"
                  className="mt-2 inline-flex h-8 cursor-pointer items-center rounded-lg bg-primary px-3 text-sm font-medium text-primary-foreground transition-opacity duration-200 hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
                >
                  Sign in to continue
                </Link>
              ) : null}
            </div>
          ) : null
        }
        onRetry={status === 401 || status === 403 ? undefined : () => void load()}
        empty={
          <EmptyState
            compact
            preset="no-records"
            title={`No ${title.toLowerCase()} yet`}
            description="Records will appear here once they are created."
          />
        }
        aria-label={title}
      />
    </WorkspacePage>
  );
}
